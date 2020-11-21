# Election 2020 Precincts Time Series Data
Timestamped 2020 presidential (general) election results for categorized by vote type (i.e., absentee, early, electionday, or provisional) for individual precincts and counties in the battleground states of FL, GA, MI, NC, and PA.

## Context

On election night (11/03/2020), most Americans went to sleep anticipating a surprising electoral victory for the Republican Party candidate, Donald Trump.  Less than four days later, however, Trump's lead in several key states had evaporated and the news media had crowned his main opponent, the Democrat Party candidate, Joe Biden, the winner.  Not one to give up without a fight, however, Trump and his campaign immediately cried foul, claiming that the late turn in the vote count toward Biden was the result of voter fraud, particularly in the handling of an unprecedented number (owing to the COVID-19 pandemic) of mail-in ballots.  While most Americans probably expect that some small degree of voter fraud occurs in every election, the large-scale and coordinated operation insinuated by the Trump campaign has never been documented.  Nevertheless, many on the right of the political spectrum, convinced that such fraud did occur, are searching for evidence to convince the courts and the public.  Meanwhile, others on the left are working to affirm the legitimacy of the election.

Regardless of one's political leaning, perhaps we can all agree that allegations of voter fraud destroy confidence in our government and that they must be responded to promptly and seriously.  Arguments grounded in hard data, not speculation or prejudice, are needed to determine the facts and fiction regarding voter fraud in the 2020 General Election.  To remedy the paucity of readily accessible election results timeseries data, I have compiled a dataset of detailed vote counts as they rolled in from some of the most hotly contested states on election night and over the following week.  Additionally, as an aspiring data scientist on the brink of completing my PhD, this project has afforded me a chance to practice data collection and data mining techniques on a meaningful, real-life problem.  Please share widely!

## Data

The (unofficial) election results data presented here is sourced from archived copies ([Internet Archive](https://web.archive.org)) of the NY Times Presidential Election Results [webpage](https://www.nytimes.com/interactive/2020/11/03/us/elections/results-president.html), which in turn obtained these data from the National Election Pool/Edison Research.  You may access this data by either downloading the gzipped `.csv` files in this repository, or by running the `election_results_extractor.py` Python script to scrape them from the Internet Archive yourself.  If you choose to collect the results yourself, be warned that it may take a few hours.

   *Note 0: The `.csv.gz` data files under the data/ directory are gzipped in order to stay under github.com's file size limits.  These are >90% compressed, so keep in mind that you will need ~1 GB of space to unzip them.*

   *Note 1: One major caveat of this dataset is that the timestamps were originally produced for internal use by the NY Times.  Logically, these should correspond to roughly when the vote numbers reported were tallied, however, there is no guarantee that this is true.*

   *Note 2: A second caveat is that only GA and NC appear to be complete datasets.  I.e., every county and (almost?) every precinct in these two states is represented in these two states by all five vote types and all the available timestamps.  For whatever reason, the NY Times did not collect data for every county (or even every precinct within some counties) for 'FL', 'MI', and 'PA', so the datasets for these states are not geographically complete.*

The `{*insert_state_abbrv*}_precincts_timeseries_2020.csv` datasets contain the following variables:

* `state`             -- The usual uppercase, two-letter state abbreviation (only includes `'FL'`, `'GA'`, `'MI'`, `'NC'`, and `'PA'`)
* `county`            -- The county names with spaces replaced by '-' (and the word 'County' removed)
* `precinct`          -- The precinct names with spaces replaced by '-'.  Rows with precincts labeled 'COUNTY' tally total vote counts for all precincts in the county specified by the 'county' variable and similarly the precinct label 'STATE' tallies votes across the whole state (only included for GA and NC).
* `fips`              -- A numerical geographic id (not unique between states) that is helpful for distinguishing between precincts with the same name.  `fips` is set to -9999 when `precinct == 'COUNTY'` or `precinct == 'STATE'`
* `timestamp`         -- The (UTC) date/time when the vote information source file was created (*assumed* to correspond to when the vote counts were tallied)
* `vote_type`         -- `'absentee'`, `'early'`, `'electionday'`, `'provisional'`, or `'total'`.  Total vote counts are the sum of all other kinds.  Some vote types are not recorded in the source data for some states (e.g., Chester County, PA).  The vote counts for these missing data points are recorded as `NaN` values in the dataset.
* `votes`             -- The total number of votes tallied for all candidates at *some point* prior to the time in the `timestamp`
* `votes_biden`       -- The number of votes tallied for Joe Biden
* `votes_trump`       -- The number of votes tallied for Donald Trump
* `votes_jorgensen`   -- The number of votes tallied for Jo Jorgensen
* `votes_other`       -- The number of votes tallied for other candidates (if any)
* `margin`            -- The number of percentage points, i.e., `(votes_trump - votes_biden) / votes * 100`, by which Trump is leading Biden (negative if trailing).  This is computed at the last timestamp for the specified region (where "region" refers to a unique State-County-Precinct-Fips combination) and the preceeding timestamps are backfilled with this value.

## Examples

My goal with the following examples is to give a flavor of the data and provide you with some code to get you started right away.  While these examples deserve some discussion, I strive to be as apolitical as possible with my interpretation.  

First, let's import the Pandas and Matplotlib packages for our data analysis and plotting, respectively.  Then, read in the data from the `.csv` file.
```python
import pandas as pd
import matplotlib.pyplot as plt

results_df = pd.read_csv('GA_precincts_timeseries_test.csv')
#convert the timestamps to Pandas' datetime type to help with plotting
results_df['date'] = pd.to_datetime(results_df['timestamp'], format="%Y-%m-%dT%H:%M:%S")
```

Now, let's compare votes counted from absentee ballots in all the precincts where Biden won to those where Trump won.  This next block of code isolates the data cells we want to use and bins them into the two categories of precincts.
```python
#we want to split the results based on which candidate won the counties (or precincts depending
#on how `geo_index` was defined).  This makes a boolean array that is `True` where Biden won
margin_mask   = results_df['margin'] < 0
#select the results on the precinct level
geo_mask      = (results_df['precinct']!='STATE') & (results_df['precinct']!='COUNTY')
#or could instead choose county level results with this line...
#geo_mask      = results_df['precinct']=='COUNTY'
#not every precinct/county has an entry at the earliest dates, so this cutoff keeps the comparisons uniform
date_mask     = results_df['date'] > pd.Timestamp('2020-11-04T01')
#combine for neater code
mask_absentee = geo_mask & date_mask & (results_df['vote_type']=='absentee')

#use the logic above to filter the dataset, then sum all the votes counted under each timestamp/datetime
cols_to_sum = ['votes_biden', 'votes_trump', 'votes']
biden_precincts_df = results_df[mask_absentee & margin_mask].groupby(['date'])[cols_to_sum].sum()
trump_precincts_df = results_df[mask_absentee & ~margin_mask].groupby(['date'])[cols_to_sum].sum()
```

Let's plot how Biden and Trump fared in each of the two categories of precincts.
```python
#plot an interesting view of the data...mixes matplotlib and built-in pandas plotting support
ax = biden_precincts_df.plot(y=['votes_biden', 'votes_trump'], color=['b','orange'], ylim=(0, 850000))
ax = trump_precincts_df.plot(y=['votes_biden', 'votes_trump'], color=['c','r'], ylim=(0, 850000), ax=ax)
ax.set_xlim([pd.Timestamp('2020-11-04T01'), pd.Timestamp('2020-11-04T19')])

#enhance the plot
markers = ['<', 'D', '>', 's']
for i, line in enumerate(ax.get_lines()):
    line.set_marker(markers[i])
ax.set_ylabel('Absentee votes')
ax.set_xlabel("Date/time (in 'mm-dd hh' format, UTC)")
ax.legend(['Biden votes (in GA precincts Biden won)', 'Trump votes (in GA precincts Biden won)',
           'Biden votes (in GA precincts Biden lost)', 'Trump votes (in GA precincts Biden lost)'])
```
![](images/example_fig1.png)

I've truncated the horizontal axis of this plot in order to highlight a particularly interesting region.  Notice how slightly after 6am UTC (i.e., after 1am EST) in the precincts where Biden won (which I will reference as "blue" precincts), both candidates observed an uptick in votes.  This suggests that the rate of reporting absentee ballots increased briefly (e.g., for <30 minutes).  Compare this to the sharp jump in votes for Biden from blue precincts at around 4am UTC.  Oddly, this sharp jump is not accompanied by a proportional jump for Trump (in the same precincts).  

This jump surprised me, since mail-in (i.e., absentee) ballots are pretty well shuffled by the US Postal Service, so the ratio of Biden to Trump should be more or less constant throughout the night.  Perhaps this is a hint of some mail-in ballot tampering, or perhaps it is driven by a largely populated and strongly pro-Biden county that is just beginning to report results.  This plot alone won't tell you the answer, but if you're interested, you can use the same dataset to check the vote counting pattern in the most heavily populated and pro-Biden precincts.  That's the beauty of having timestamped data on the precinct level.

Let's look at another slice of the dataset, this time focusing on election day votes.  Again, let's first set up the necessary masks and variables...
```python
#change the masks and data variables to explore election day data now
mask_eday = geo_mask & date_mask & (results_df['vote_type']=='electionday')
biden_precincts_df = results_df[mask_eday & margin_mask].groupby(['date'])[cols_to_sum].sum()
trump_precincts_df = results_df[mask_eday & ~margin_mask].groupby(['date'])[cols_to_sum].sum()

#the total election day votes accumulated for any candidate at each timestamp
total_votes = trump_precincts_df['votes'] + biden_precincts_df['votes']
```

...and now we're ready to plot the data.  This time we'll look at the evolution of the winning margin in the two precinct categories that we defined above (i.e., pro-Biden vs. pro-Trump precincts).  Instead of using the datetime as the variable on the independent variable, however, let's replace it with the total number of election day votes accrued.
```python
def compute_margins(df):
    """Computes the percentage point difference between the top two candidates.""" 
    return (df['votes_trump'] - df['votes_biden']).divide(df['votes'], fill_value=1) * 100

#we need to recompute the candidate margins because the original `margin` column in 
#`results_df` has been mangled by the df.groupby().sum() operation above.
plt.figure()
labels = ("Biden's winning margin in GA precincts he won", "Trump's winning margin in GA precincts he won")
plt.plot(total_votes, -compute_margins(biden_precincts_df), '>b', label=labels[0])
plt.plot(total_votes, compute_margins(trump_precincts_df), 'Dr', label=labels[1])

plt.xlabel('Total absentee votes counted')
plt.ylabel("Win(/loss) margin (for absentee ballots)")
plt.legend()
```
![](images/example_fig2.png)

Well, that's interesting!  Two things stand out to me.  First, the red diamonds show a steady downward trend in Trump's election day margin in the precincts he won.  The most innocuous reason for this that I could think of is that perhaps election day voters initially skew Republican and Democrat voters come out later in the day.  This assumes, of course, that most votes are counted in the order they were collected.  Even if this were true, however, the margin still declines at a noticeably steeper rate than it does in the equivalent plot for North Carolina (...try plotting NC yourself!).  A good way to get started playing with the data yourself would be to remake this plot with different vote types (e.g., absentee or early) to get started.

The second oddity is the huge 10 percentage point jump in Biden's margin that occurs around the 450,000 vote mark.  Before that point, Biden's margin in precincts he won is steadily rising, but after the dramatically steep rise, it flattens out for the remaining half of the vote counting.  I really have no idea what to make of this.  Perhaps you can think of some way to explore this more?

