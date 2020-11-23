import requests
import time
import tempfile
from pathlib import Path

import pandas as pd


def get_archived_county_results(race):
    if race['race_id'][2:6] != '-G-P':
        return []
    print(race['race_id'])
    
    state_records = []
    for county in race['counties']:
        vote_record = {}
        vote_record['state']              = race['state_id']
        vote_record['county']             = county['name'].lower().replace(' ', '-')
        vote_record['fips']               = county['fips']
        vote_record['timestamp']          = race['last_updated']
        vote_record['last_updated']       = county['last_updated']
        vote_record['absentee_dem']       = county['results_absentee'].pop('bidenj', np.nan)
        vote_record['absentee_rep']       = county['results_absentee'].pop('trumpd', np.nan)
        vote_record['absentee_jorgensen'] = county['results_absentee'].pop('jorgensenj', np.nan)
        vote_record['votes_dem']          = county['results'].pop('bidenj', np.nan)
        vote_record['votes_rep']          = county['results'].pop('trumpd', np.nan)
        vote_record['votes_jorgensen']    = county['results'].pop('jorgensenj', np.nan)
        vote_record['absentee2020']       = county.get('absentee_votes', np.nan)
        vote_record['votes2020']          = county.get('votes', np.nan)
        vote_record['margin2020']         = county.get('margin2020', np.nan)
        vote_record['votes2016']          = county.get('votes2016', np.nan)
        vote_record['margin2016']         = county.get('margin2016', np.nan)
        vote_record['votes2012']          = county.get('votes2012', np.nan)
        vote_record['margin2012']         = county.get('margin2012', np.nan)
        state_records.append(vote_record)
    
    return state_records

def load_county_presidential(nyt_url, csv_path):
    print('Searching for archived copies of the U.S. presidential election results')

    archive_api_url = 'http://web.archive.org/cdx/search/cdx?url='
    archive_output_qualifier = '&output=json&from=20201104&to=20201107'   #limit search to election day +4
    search_hits = requests.get(archive_api_url + nyt_url + archive_output_qualifier).json()[1:]
    
    urls_searched = []
    for i, url_group in enumerate(search_hits):
        try:
            archived_url = 'http://web.archive.org/web/' + url_group[1] + 'if_/' + url_group[2]
            good_url_status = int(url_group[4]) < 400
            correct_data_type = url_group[3] == 'application/json'
            url_is_new = not archived_url in urls_searched
        except:
            continue
        
        if good_url_status and correct_data_type and url_is_new:
            urls_searched.append(archived_url)
            try:
                print('Downloading national data from {}'.format(archived_url))
                download_start = time.time()
                race_data = requests.get(archived_url)
                download_finish = time.time()
                print('Download successful, took {:.1f} seconds'.format(download_finish - download_start))
                
                vote_records = []
                for race in race_data.json()['data']['races']:
                    vote_records += get_archived_county_results(race)
                results_df = pd.DataFrame.from_records(vote_records)
                results_df.to_csv(csv_path, mode='a', header=~csv_path.is_file())
                
                print('Data extraction successful, took {:.1f} seconds'.format(time.time() - download_finish))
                print('Waiting 5x length of previous download as courtesy before continuing...')
                time.sleep(5 * (download_finish - download_start))
                
            except Exception as e:
                print('Failed to extract data from {} with error: {}'.format(archived_url, str(e)))

def scrape_state_pages(csv_path):
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

    for state in states_list:
        state_str = state.lower().replace(' ','-')
        nyt_urlC = 'https://static01.nyt.com/elections-assets/2020/data/api/2020-11-03/state-page/{}.json'.format(state_str)
        load_county_presidential(nyt_urlC, csv_path)
        nyt_urlD = 'https://static01.nyt.com/elections-assets/2020/data/api/2020-11-03/race-page/{}/president.json'.format(state_str)
        load_county_presidential(nyt_urlD, csv_path)
    
def scrape_national_pages(csv_path, all_pages=False):
    nyt_urlA = 'https://static01.nyt.com/elections-assets/2020/data/api/2020-11-03/national-map-page/national/president.json'
    nyt_urlB = 'https://static01.nyt.com/elections-assets/2020/data/api/2020-11-03/votes-remaining-page/national/president.json'
    load_county_presidential(nyt_urlA, csv_path)
    if all_pages:
        load_county_presidential(nyt_urlB, csv_path)

def remove_duplicates(csv_path):
    cols_to_keep = ['state', 'county', 'fips', 'timestamp', 'last_updated', 
                    'absentee_dem', 'absentee_rep', 'absentee_jorgensen', 'votes_dem', 
                    'votes_rep', 'votes_jorgensen', 'absentee2020', 'votes2020', 
                    'margin2020', 'votes2016', 'margin2016', 'votes2012', 'margin2012']

    temp = tempfile.NamedTemporaryFile(prefix=csv_path.name, dir=csv_path.parent, delete=False)
    df = pd.read_csv(csv_path)[cols_to_keep].drop_duplicates(['state', 'timestamp', 'county'], keep='last')
    df.to_csv(temp.name)
    Path(temp.name).replace(csv_path)

if __name__=='__main__':
    src_dir = ''   #you'll need to put the path to your data directory here
    csv_path = Path(src_dir + '/' + 'county_presidential.csv')
    scrape_national_pages(csv_path, all_pages=False)
    scrape_state_pages(csv_path)   #<-- !!!Warning this will take ~24 hours and only net ~12k original rows!!!
    remove_duplicates(csv_path)
