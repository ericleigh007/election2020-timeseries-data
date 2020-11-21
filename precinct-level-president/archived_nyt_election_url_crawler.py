from bs4 import BeautifulSoup
import requests
import itertools

##########################################################################################
#The src folder needs to be set here before the file i/o will work properly
src_dir = ''
##########################################################################################


data_urls = []
visited_urls = []

with open(src_dir + '/' + 'archived_nyt_election2020_urls.txt', 'r') as file_handle:
    for archived_url in file_handle:
        if archived_url in visited_urls:
            continue
        else:
            visited_urls.append(archived_url)
        
        soup = BeautifulSoup(requests.get(archived_url).content, 'html.parser')
        
        #This line is the key to grabbing the timestamped url.  I found the "e-map-data"
        #<div> class by searching for 'static01.nyt.com/elections-assets/2020/data/api/*' 
        #at https://www.nytimes.com/interactive/2020/11/03/us/election/results-president.html
        script_text = soup.find("script", class_="e-map-data").string
        
        #a hackish and opaque, but fast way to extract the timestamped urls
        for url_str in script_text.split('"timestamped_url":"')[1:]:
            nyt_url = url_str[:171].split('"')[0]
            if not nyt_url in data_urls:
                data_urls.append(nyt_url)
        print('extracted urls for archived NY Times source files from %s' %archived_url)

with open(src_dir + '/' + 'archived_nyt_timestamped_data_urls.txt', 'w') as data_dump_file:
    for url in data_urls:
        data_dump_file.write(url + '\n')


