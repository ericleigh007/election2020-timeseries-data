import requests
import time
import pandas as pd


src_dir = ''

def get_archived_county_results(race):
    assert race['race_id'][2:6] == '-G-P'
    
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
    
    return race['state_id'], state_records

def extract_country_wide_county_data(csv_file_name):
    print('Searching for archived copies of the national U.S. presidential election results')

    archive_api_url = 'http://web.archive.org/cdx/search/cdx?url='
    archive_output_qualifier = '&output=json&from=20201104&to=20201107'   #limit search to election day +4
    state_str = state.lower().replace(' ','-')
    nyt_url = 'https://static01.nyt.com/elections-assets/2020/data/api/2020-11-03/national-map-page/national/president.json'
    search_hits = requests.get(archive_api_url + nyt_url + archive_output_qualifier).json()[1:]
    
    urls_searched = []
    for i, url_group in enumerate(search_hits):
        archived_url = 'http://web.archive.org/web/' + url_group[1] + 'if_/' + url_group[2]
        good_url_status = int(url_group[4]) < 400
        correct_data_type = url_group[3] == 'application/json'
        url_is_new = not archived_url in urls_searched
        
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
                    vote_records += get_archived_county_results(race)[1]
                results_df = pd.DataFrame.from_records(vote_records)
                results_df.to_csv(csv_file_name, mode='a', header=(i==0))
                
                print('Data extraction successful, took {:.1f} seconds'.format(time.time() - download_finish))
                print('Waiting 5x length of previous download as courtesy before continuing...')
                time.sleep(5 * (download_finish - download_start))
                
            except Exception as e:
                print('Failed to extract data from {} with error: {}'.format(archived_url, str(e)))

extract_country_wide_county_data(src_dir + '/' + 'county_presidential.csv')


