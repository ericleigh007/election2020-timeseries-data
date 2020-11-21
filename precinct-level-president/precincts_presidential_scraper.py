import requests
import itertools
from pathlib import Path
import time
import pandas as pd
import numpy as np


##########################################################################################
#The src folder needs to be set here before the file i/o will work properly
src_dir = ''
##########################################################################################

def extract_vote_record(state, timestamp, data_dict):
    vote_info = {}
    
    vote_info['state'] = state
    county = data_dict['locality_name'].lower().replace(' ','-')
    vote_info['county'] = county.replace('-county','')
    vote_info['precinct'] = data_dict['precinct_id'].lower().replace(' ','-')
    vote_info['fips'] = data_dict['locality_fips']

    vote_info['timestamp'] = timestamp

    results = {k: v if not v in (None, 'null') else np.nan for k, v in data_dict['results'].items()}
    vote_type = data_dict.get('vote_type', 'null')
    vote_info['vote_type'] = vote_type if vote_type != 'null' else None
    vote_info['votes'] = data_dict.get('votes', np.nan)
    vote_info['votes_biden'] = results.pop('bidenj')
    vote_info['votes_trump'] = results.pop('trumpd')
    vote_info['votes_jorgensen'] = results.pop('jorgensenj')
    vote_info['votes_other'] = sum(results.values())
    
    return vote_info

def load_data(url, state, out=None):
    return_data = True if out is None else False
    if return_data:
        out = []
    
    try:
        print('Attempting to download: {}'.format(url))
        json_data = requests.get(url).json()
    except:
        raise IOError

    for record in itertools.chain(json_data.get('precincts', []),
                                  json_data.get('precinct_by_vote_type', [])):
        out.append( extract_vote_record(state, url[-29:-6], record) )
    
    if return_data:
        return out

def fill_missing_timestamps(df, uniq_size, template_df):
    if df.shape[0] < uniq_size:
        first_row = df.iloc[0]
        df = df.merge(template_df, how='outer')
        df['state']    = first_row['state']
        df['county']   = first_row['county']
        df['precinct'] = first_row['precinct']
        df['fips']     = first_row['fips']
    return df
    
def correct_for_missing_data(df):
    #ensures timestamps and vote_types are complete for each precinct and county pair
    uniq_tstamps = np.unique(df['timestamp'].dropna().values)
    uniq_vtypes = np.unique(df['vote_type'].dropna().values)
    uniq_size = uniq_tstamps.size * uniq_vtypes.size
    template_df = pd.DataFrame({'vote_type':[uniq_vtypes], 
                                'timestamp':[uniq_tstamps]}).explode('vote_type').explode('timestamp')
    
    out = df.groupby(['state', 'county', 'precinct', 'fips'], as_index=False).apply(fill_missing_timestamps, 
                                                                                    uniq_size=uniq_size,
                                                                                    template_df=template_df)
    return out.reset_index(drop=True)

def compute_margins(df):
    return (df['votes_trump'] - df['votes_biden']).divide(df['votes'], fill_value=1) * 100

def fill_margins(df):
    df['margin'] = df.iloc[df['date'].argmax()]['margin']
    return df

def add_categories(df, vars_to_fill={}, ordered_cols=None, mask=slice(None)):
    grouping_vars = [v for v in ['state', 'county', 'precinct', 'fips', 
                                 'timestamp', 'vote_type'] if not v in vars_to_fill]
    new_df = df[mask].groupby(grouping_vars, as_index=False).sum()
    
    if vars_to_fill:
        new_df[[*vars_to_fill.keys()]] = pd.DataFrame(vars_to_fill, index=new_df.index)
    if ordered_cols is not None:
        new_df = new_df[ordered_cols]
    
    return new_df

def streamline_data(precinct_records, sum_counties=True):
    #votes categorized by precinct and vote type...might include some of the other categories
    #for certain states (i.e., Florida, Michigan, Pennsylvania)
    precincts_df = pd.DataFrame.from_records(precinct_records)
    ordered_cols = precincts_df.columns.tolist()

    #total votes per precinct (i.e., not separated by vote type)
    mask_p = precincts_df['vote_type'] != 'total'   #this line is needed for MI
    precinct_totals_df = add_categories(precincts_df, {'vote_type':'total'}, ordered_cols, mask_p)

    #all precinct votes summed within each county (keeping each vote type in a separate bin) 
    county_df = add_categories(precincts_df, {'precinct':'COUNTY', 'fips':-9999}, ordered_cols)

    #total votes (all types) summed within each county
    mask_c = county_df['vote_type'] != 'total'
    county_totals_df = add_categories(county_df, {'precinct':'COUNTY', 'fips':-9999, 
                                                     'vote_type':'total'}, ordered_cols, mask_c)

    if sum_counties:
        #all precinct votes summed within each state (keeping each vote type in a separate bin) 
        states_df = add_categories(county_df, {'county':'STATE', 'precinct':'STATE', 
                                               'fips':-9999}, ordered_cols)

        #total votes (all types) summed within each state 
        state_totals_df = add_categories(states_df, {'county':'STATE', 'precinct':'STATE', 
                                                     'fips':-9999, 'vote_type':'total', }, ordered_cols)

        df_list_to_concat = [precincts_df, precinct_totals_df, county_df, county_totals_df, 
                             states_df, state_totals_df]
    else:
        df_list_to_concat = [precincts_df, precinct_totals_df, county_df, county_totals_df]

    #concatenate all the results and add a column containing Trump's winning/losing margins 
    #as of the most recent timestamp
    results_df = pd.concat(df_list_to_concat, axis=0, sort=False, ignore_index=True)
    results_df['margin'] = compute_margins(results_df)
    results_df['date'] = pd.to_datetime(results_df['timestamp'], format="%Y-%m-%dT%H:%M:%S")
    results_df.groupby(['state', 'county', 'precinct', 'fips', 'vote_type'])[['margin','date']].apply(fill_margins)
    results_df = results_df.drop(columns=['date'])

    #fill holes and then sort the dataset
    results_df = correct_for_missing_data(results_df)
    sort_by_vars = ['state','county','precinct','fips','vote_type','timestamp']
    results_df.sort_values(by=sort_by_vars, ascending=True, inplace=True)
    
    return results_df


if __name__=='__main__':
    json_urls_file = src_dir + '/' + 'archived_nyt_timestamped_precinct_urls.txt'
    json_urls_all = Path(json_urls_file).read_text().split()

    for state in ('GA','NC','FL','MI','PA'):
        json_urls = [u for u in json_urls_all if state in u]

        precinct_records = []
        unique_src_urls = []

        num_urls = len(json_urls) + 1
        while len(json_urls) < num_urls:
            num_urls = len(json_urls)

            for line in json_urls:
                #this should download from the Internet Archive <web.archive.org>, not the NY Times
                #the `nyt_src_url` is only used here for bookkeeping to weed out redundant archived copies
                url = line.strip()
                nyt_src_url = url[43:]
                if nyt_src_url in unique_src_urls:
                    json_urls.remove(url)
                    continue

                try:
                    start_time = time.time()
                    load_data(url, state, out=precinct_records)
                    print('Download successful.  Time elapsed was {:.1f} seconds.'.format(time.time() - start_time))
                    unique_src_urls.append(nyt_src_url)
                    json_urls.remove(url)
                except IOError:
                    print('!!! Download failed for {}'.format(url))

        if state in ('GA', 'NC'):
            results_df = streamline_data(precinct_records)
        else:
            results_df = streamline_data(precinct_records, sum_counties=False)

        results_df.to_csv(src_dir + '/' + '{}_precincts_timeseries_2020.csv'.format(state), index=False, encoding='utf-8')

