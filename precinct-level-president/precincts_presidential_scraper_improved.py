import requests
import itertools
from pathlib import Path
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def extract_vote_record(state, timestamp, data_dict):
    vote_info = {}
    
    vote_info['state'] = state
    county = data_dict['locality_name'].lower().replace(' ','-')
    vote_info['county'] = county.replace('-county','')
    precinct = data_dict['precinct_id']
    if precinct == 'COUNTY':
        vote_info['precinct'] = precinct
        vote_info['fips'] = -9999
    else:
        vote_info['precinct'] = precinct.lower().replace(' ','-')
        vote_info['fips'] = data_dict['locality_fips']

    vote_info['timestamp'] = timestamp

    results = {k: v if not v in (None, 'null') else np.nan for k, v in data_dict['results'].items()}
    vote_info['vote_type'] = data_dict.get('vote_type', 'null')
    vote_info['votes'] = data_dict.get('votes', np.nan)
    vote_info['votes_biden'] = results.pop('bidenj', np.nan)
    vote_info['votes_trump'] = results.pop('trumpd', np.nan)
    vote_info['votes_jorgensen'] = results.pop('jorgensenj', np.nan)
    vote_info['votes_other'] = sum(results.values()) if results else np.nan

    return vote_info

def load_precinct_data(nyt_url, csv_path, state, extra_only=False, extra_urls=[]):
    print('Searching for archived copies of the U.S. presidential election results')

    uniq_nyt_urls = []
    urls_to_search = []
    failed_urls = []
    
    if not extra_only:
        archive_api_url = 'http://web.archive.org/cdx/search/cdx?url='
        archive_output_qualifier = '&output=json&from=20201104&to=20201111'   #limit search to election day +4
        search_hits = requests.get(archive_api_url + nyt_url + archive_output_qualifier).json()[1:]

        for url_group in search_hits:
            archived_url = 'https://web.archive.org/web/' + url_group[1] + 'if_/' + url_group[2]
            try:
                good_url_status = int(url_group[4]) < 400
                correct_data_type = url_group[3] == 'application/json'
                url_is_new = not url_group[2] in uniq_nyt_urls
                if good_url_status and correct_data_type and url_is_new:
                    uniq_nyt_urls.append(url_group[2])
                    if not extra_only:
                        urls_to_search.append(archived_url)
            except:
                continue
    
    for i, url in enumerate(extra_urls):
        url_pieces = url.split('/')
        url_pieces[4] = url_pieces[4][:14] + 'if_'
        url = '/'.join(url_pieces)
        orig_src_url = '/'.join(url_pieces[5:])
        if (state in url) and (not orig_src_url in uniq_nyt_urls):
            uniq_nyt_urls.append(orig_src_url)
            urls_to_search.append(url)
            print(i, url)
    
    for archived_url in urls_to_search:
        try:
            print('\nDownloading data from {}'.format(archived_url))
            download_start = time.time()
            race_data = requests.get(archived_url)
            download_finish = time.time()
            print('Download successful, took {:.1f} seconds'.format(download_finish - download_start))

            precinct_records = []
            for record_type, record in race_data.json().items():
                if record_type == 'meta':
                    continue
                print('Extracting {} data...'.format(record_type))
                for row in record:
                    precinct_records.append( extract_vote_record(state, archived_url[-29:-5], row) )
            results_df = pd.DataFrame.from_records(precinct_records)
            results_df.to_csv(csv_path, mode='a', header=not csv_path.is_file())

            print('Data extraction successful, took {:.1f} seconds'.format(time.time() - download_finish))
            print('Waiting 3x length of previous download as courtesy before continuing...')
            time.sleep(3 * (download_finish - download_start))

        except Exception as e:
            print('Failed to extract data from {} with error: {}'.format(archived_url, str(e)))
            failed_urls.append(archived_url)
                
    return failed_urls

def fill_missing_totals(inputfile, outputfile):
    df = pd.read_csv(inputfile, index_col=0)
    df.dropna(subset=['votes_biden', 'votes_trump'], how='all', inplace=True)
    df['vote_type'].fillna(value='null', inplace=True)

    df['vtype_bool'] = (df['vote_type'] == 'total') | (df['vote_type'] == 'null')
    df['has_total_vtype'] = df.groupby(['county','precinct','timestamp'])['vtype_bool'].transform(sum)
    grouped_totals = df[df['has_total_vtype'] == 0].groupby(['county','precinct','timestamp'])

    totals_df = grouped_totals.first()
    vote_vars = ['votes', 'votes_biden', 'votes_trump', 'votes_jorgensen', 'votes_other']
    totals_df[vote_vars] = grouped_totals[vote_vars].sum()
    totals_df['vote_type'] = 'total'
    totals_df.reset_index(inplace=True)

    totals_df.drop(columns=['vtype_bool','has_total_vtype'], inplace=True)
    df.drop(columns=['vtype_bool','has_total_vtype'], inplace=True)
    ordered_cols = df.columns.tolist()
    full_df = pd.concat([df, totals_df[ordered_cols]], axis=0)

    full_df.sort_values(by=['county', 'precinct', 'timestamp', 'vote_type'], inplace=True)
    full_df['votes_other'].fillna(value=0, inplace=True)
    full_df.reset_index(drop=True, inplace=True)

    full_df.to_csv(outputfile)


if __name__=='__main__':
    src_dir = Path('.')
    stored_url_file = src_dir / Path('archived_nyt_timestamped_precinct_urls.txt')
    pre_collected_urls = stored_url_file.read_text().split()

    for state in ('PA','MI','FL','GA','NC'):
        state_str = state + ('General' if state in ('GA', 'NC') else 'GeneralConcatenator')
        nyt_url = 'https://static01.nyt.com/elections-assets/2020/data/api/2020-11-03/precincts/{}-2020-11*'.format(state_str)
        csv_path = src_dir / Path('{}_precincts_timeseries_2020_unprocessed.csv'.format(state))
        
        failed_urls = load_precinct_data(nyt_url, csv_path, state, extra_urls=pre_collected_urls)
        num_failed = len(failed_urls) + 1
        while len(failed_urls) < num_failed:
            num_failed = len(failed_urls)
            failed_urls = load_precinct_data(nyt_url, csv_path, state, extra_urls=failed_urls, extra_only=True)

        outputfile = src_dir / Path('{}_precincts_timeseries_2020_processed.csv'.format(state))
        fill_missing_totals(csv_path, outputfile)
        
