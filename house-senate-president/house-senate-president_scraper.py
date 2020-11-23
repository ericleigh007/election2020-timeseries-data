import requests
import time
import pandas as pd


states_list = ['Alaska', 'Alabama', 'Arkansas', 'Arizona', 'California', 
 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia',
 'Hawaii', 'Iowa', 'Idaho', 'Illinois', 'Indiana', 'Kansas', 'Kentucky',
 'Louisiana', 'Massachusetts', 'Maryland', 'Maine', 'Michigan',
 'Minnesota', 'Missouri', 'Mississippi', 'Montana', 'North Carolina',
 'North Dakota', 'Nebraska', 'New Hampshire', 'New Jersey', 'New Mexico',
 'Nevada', 'New York', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas',
 'Utah', 'Virginia', 'Vermont', 'Washington', 'Wisconsin',
 'West Virginia', 'Wyoming']

def eval_candidates(clist, cnames):
    out = {}
    curr_rep_order = 1000
    curr_dem_order = 1000
    curr_extra_order = 1000
    
    for candidate_dict in clist:
        candidate = candidate_dict['candidate_key']
        if candidate in cnames:
            party_id = candidate_dict['party_id']
            order = candidate_dict['order']

            if (party_id == 'democrat') and (order < curr_dem_order):
                out['dem'] = candidate
            elif (party_id == 'republican') and (order < curr_rep_order):
                out['rep'] = candidate
            elif order < curr_extra_order:
                out['extra'] = candidate
    return out

def build_state_dataframe(state_data):
    vote_dfs = {}

    #first loop gathers presidential race timestamps (and other data).  Timestamps
    #are needed before running through loops for other races.
    for race in state_data:
        race_records = []
        state = race['race_id'][:2]
        race_type = race['race_id'][3:7]
        race_id = race['race_id'][:-11]

        
        if race_type in ('G-P-', 'G-S-', 'S-S-', 'G-H-'):
            print(race_id)
            
            past_elections_data = {}
            if race_type == 'G-P-':
                past_elections_data['votes2016']   = race['votes2016']
                past_elections_data['margin2016']  = race['margin2016']
                past_elections_data['votes2012']   = race['votes2012']
                past_elections_data['margin2012']  = race['margin2012']

            candidates = {}
            N = len(race['timeseries'])
            for i, vote_dict in enumerate(race['timeseries']):
                if i == 0:   #the first timestamp always seems to be out of order and have zero votes
                    candidate_names = [*vote_dict['vote_shares'].keys()]
                    candidates = eval_candidates(race['candidates'], candidate_names)
                
                #get the timestamp and check that it is lower than the next value in the timeseries
                curr_timestamp = vote_dict['timestamp']
                if i < N - 1:
                    next_timestamp = race['timeseries'][i + 1]['timestamp']
                    if pd.Timestamp(curr_timestamp) > pd.Timestamp(next_timestamp):
                        continue
                
                vote_record = {}
                vote_record['timestamp']     = curr_timestamp
                vote_record['votes2020']     = vote_dict['votes']
                vote_record['vf_dem']        = vote_dict['vote_shares'].get(candidates.get('dem'), 0)
                vote_record['vf_rep']        = vote_dict['vote_shares'].get(candidates.get('rep'), 0)
                vote_record['vf_extra']      = vote_dict['vote_shares'].get(candidates.get('extra'), 0)
                vote_record.update(past_elections_data)
                race_records.append(vote_record)
            
            if len(race_records) == 0:
                continue
            race_df = pd.DataFrame.from_records(race_records)
            race_df.set_index(pd.to_datetime(race_df['timestamp']), drop=False, inplace=True)
            race_df.index.rename('date', inplace=True)
            
            if race_type == 'G-P-':
                vote_dfs[race_id[3:]] = race_df
                synced_dates = race_df.index.to_frame(index=False, name='date')
            else:
                race_df = pd.merge_asof(synced_dates, race_df, left_on='date', 
                                        right_index=True, direction='backward')
                vote_dfs[race_id[3:]] = race_df.set_index('date')#.drop_duplicates(subset=['timestamp']))
    
    full_df = pd.concat(vote_dfs.values(), keys=vote_dfs.keys())
    return state, full_df

def load_state_data(state):
    State_Str = ' '.join([s[0].upper() + s[1:] for s in state.split('-')])
    print('Searching for the latest archived copy of the {} state page data'.format(State_Str))

    archive_api_url = 'http://web.archive.org/cdx/search/cdx?url='
    archive_output_qualifier = '&output=json'
    nyt_url = 'https://static01.nyt.com/elections-assets/2020/data/api/2020-11-03/state-page/{}.json'.format(state)
    search_hits = requests.get(archive_api_url + nyt_url + archive_output_qualifier).json()

    #loops through `search_hits` checking for the first hit with a good url status code
    for url_group in reversed(search_hits):
        if int(url_group[4]) < 400:
            archived_urlA = 'http://web.archive.org/web/' + url_group[1] + 'if_/' + url_group[2]
            archived_urlB = 'http://web.archive.org/web/' + url_group[1] + '/' + url_group[2]
            
            download_start = time.time()
            try:
                state_data = requests.get(archived_urlA).json()
                print('Downloading {} data from {}'.format(State_Str, archived_urlA))
            except:
                state_data = requests.get(archived_urlB).json()
                print('Downloading {} data from {}'.format(State_Str, archived_urlB))
            download_finish = time.time()
            print('Download successful, took {:.1f} seconds'.format(download_finish - download_start))
            
            state_abbrv, vote_df = build_state_dataframe(state_data['data']['races'])
            
            print('Waiting 5x length of previous download as courtesy before continuing...')
            time.sleep(5 * (download_finish - download_start))
            break
    
    return state_abbrv, vote_df

if __name__=='__main__':
    df_dict = {}
    for state in states_list:
        state_abbrv, vote_df = load_state_data(state.lower().replace(' ','-'))
        df_dict[state_abbrv] = vote_df

    full_df = pd.concat(df_dict.values(), keys=df_dict.keys())
    full_df.index.rename(['state', 'race_id', 'date'], inplace=True)
    src_dir = '.'
    full_df.to_csv(src_dir + '/' + 'election2020_house-senate-president.csv')


