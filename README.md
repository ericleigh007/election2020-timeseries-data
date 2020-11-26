# 2020 election: timeseries data
Unofficial United States general election (2020) timeseries data scraped from archived copies of the NY Times election results webpages.

## Data

**UPDATE:** The original precinct-level datasets were full of numerous missing data entries, due to a deficient scraper script.  These datasets have been replaced by more complete ones.  If you are using a prior version, the important point is that the prior datasets were *not* inaccurate, just incomplete.

The data is described in depth by the README files in each of the individual folders linked to below.  Collectively, these datasets include various election race vote count details that I have not found elsewhere.  The excellent [nyt-2020-election-scraper](https://github.com/alex/nyt-2020-election-scraper) project, for example, periodically scrapes the NY Times "votes remaining" page, but leaves untouched (to the best of my knowledge) the county-level data available in that page.  Additionally, there are several other NY Times `.json` files for national and state elections worth exploring, as well as numerous copies of all these files archived by the [Internet Archive](https://web.archive.org/).

Here are links to the various data folders:
  1. [County-level presidential vote counting timeseries](/county-level-president/)
  2. [State-level house, senate, and presidential timeseries](/house-senate-president/)
  3. [Precinct-level presidential timeseries by vote type](/precinct-level-president/) (only for GA, FL, MI, NC, and PA)

## Context

<!--- On election night (11/03/2020), most Americans went to sleep anticipating a surprising electoral victory for the Republican Party candidate, Donald Trump.  Less than four days later, however, Trump's lead in several key states had evaporated and the news media had crowned his main opponent, the Democrat Party candidate, Joe Biden, the winner.  Not one to give up without a fight, however, Trump and his campaign immediately cried foul, claiming that the late turn in the vote count toward Biden was the result of voter fraud, particularly in the handling of an unprecedented number (owing to the COVID-19 pandemic) of mail-in ballots.  While most Americans probably expect that some small degree of voter fraud occurs in every election, the large-scale and coordinated operation insinuated by the Trump campaign has never been documented.  Nevertheless, many on the right of the political spectrum, convinced that such fraud did occur, are searching for evidence to convince the courts and the public.  Meanwhile, others on the left are working to affirm the legitimacy of the election. --->

Regardless of one's political leaning, perhaps we can all agree that allegations of voter fraud destroy confidence in our government and that they must be responded to promptly and seriously.  Arguments grounded in hard data, not speculation or prejudice, are needed to determine the facts and fiction regarding voter fraud in the 2020 General Election.  To remedy the paucity of detailed, accessible election results timeseries data (aside from the [nyt-2020-election-scraper](https://github.com/alex/nyt-2020-election-scraper) project), I have collected detailed vote counts timestamped at numerous intervals on election night and the subsequent days.  The data in these unofficial election results "updates" were originally disseminated by the National Election Pool/Edison Research, databased by the NY Times (among other news agencies), and archived by the [Internet Archive](https://web.archive.org/).  I did not change or add any data, however, I cannot guarantee that the data I extracted is complete.  So, be warned that you are responsible for verifying that any conclusions you draw from them make sense.
