# 2020 election: counties-presidential

Timeseries data for the U.S. 2020 presidential election race by county.  The dataset also includes a breakdown of absentee vote counts, where available.

## Data

The `county_presidential.csv` dataset should include data for all the counties and cities in the United States (except the District of Columbia, and I haven't actually verified that all the other counties *are* included).  You may download the dataset from here or scrape it yourself using the `county_presidential_scraper.py` script.  The dataset includes the following variables:

 * `state`              -- The usual uppercase, two-letter state abbreviation (includes all 50 states)
 * `county`             -- The name of the election district (includes, e.g., counties and cities) in lower case and with spaces replaced by hyphens
 * `fips`               -- The geographical FIPS tag associated with each `county`
 * `timestamp`          -- The (UTC) date/time when the vote information source file was created (*assumed* to correspond to when the vote counts were tallied)
 * `last_updated`       -- The (UTC) date/time when the vote information was updated (i.e., this would be earlier than timestamp if the county totals haven't changed since the last time the results file was updated)
 * `absentee_dem`       -- Number of absentee votes tallied for the Democrat party candidate (Joe Biden) 
 * `absentee_rep`       -- Number of absentee votes tallied for the Democrat party candidate (Donald Trump) 
 * `absentee_jorgensen` -- Number of absentee votes tallied for the Libertarian party candidate (Jo Jorgensen) 
 * `votes_dem`          -- Number of total votes tallied for the Democrat party candidate (Joe Biden) 
 * `votes_rep`          -- Number of total votes tallied for the Democrat party candidate (Donald Trump) 
 * `votes_jorgensen`    -- Number of total votes tallied for the Libertarian party candidate (Jo Jorgensen) 
 * `absentee2020`       -- Number of absentee votes tallied for all presidential candidates in the 2020 general election
 * `votes2020`          -- Number of total votes tallied for all presidential candidates in the 2020 general election
 * `margin2020`         -- Percentage point difference between the Republican candidate and the Democrat candidate...this should equal `(votes_rep - votes_dem) / votes2020`
 * `votes2016`          -- Number of total votes tallied for all presidential candidates in the 2016 general election 
 * `margin2016`         -- Percentage point difference between the Republican candidate and the Democrat presidential candidates in the 2016 general election
 * `votes2012`          -- Number of total votes tallied for all presidential candidates in the 2012 general election 
 * `margin2012`         -- Percentage point difference between the Republican candidate and the Democrat presidential candidates in the 2012 general election

## Examples

Let's look at the state of Virginia as an example.  First we'll load and prep the data...

```Python
#load the data and select just vote counts for Virginia
csv_file = '/Users/kaiser/pythonapps/county_level_president.csv'
va_df = pd.read_csv(csv_file).set_index(['state']).loc['VA']
va_df['date'] = pd.to_datetime(va_df['timestamp'])

#extract votes just for Fairfax County
fairfax_df = va_df.set_index(['county']).loc['fairfax']
fairfax_df['date_updated'] = pd.to_datetime(fairfax_df['last_updated'])
#sum votes for all of Virginia except Fairfax County
va_sans_fairfax_df = va_df[ va_df['county'] != 'fairfax' ].groupby(['date']).sum().reset_index()
#sum votes for all of Virginia
va_df = va_df.groupby(['date']).sum().reset_index()
```

Now let's plot how the vote counts for Biden and Trump across the whole state updated over a six hour window on election night (note the time on the horizontal axis is UTC).

```Python
#plot Biden and Trump vote timeseries in VA with vs. without Fairfax County
ax = va_df.plot('date', 'votes_dem', marker='o', color='b')
va_df.plot('date', 'votes_rep', marker='D', color='r', ax=ax)
va_sans_fairfax_df.plot('date', 'votes_dem', linestyle='--', marker='o', color='b', alpha=0.2, ax=ax)
va_sans_fairfax_df.plot('date', 'votes_rep', linestyle='--', marker='D', color='r', alpha=0.2, ax=ax)
ax.legend(['Biden', 'Trump', 'Biden (sans Fairfax County)', 'Trump (sans Fairfax County)'])
ax.set_ylabel('Virginia Vote Counts')
ax.set_xlabel("Date/time ('mm-dd hh' format)")
ax.set_xlim([pd.Timestamp('2020-11-04T03'), pd.Timestamp('2020-11-04T09')])
ax.set_ylim([11e5, 22e5])
```
[](./example_fig3.png)

Actually, I plotted the vote counts across the whole state *and* the vote counts across all the VA counties and cities except for Fairfax County.  The reason should be evident in the plot.  Some really strange vote counting behaviour shows up in the full state counts and disappears without Fairfax.  Now that we've fingered Fairfax County as the culprit, let's take a closer look...

```Python
#plot Biden and Trump total and absentee vote timeseries for Fairfax County
ax = fairfax_df.plot('date_updated', 'votes_dem', marker='o', color='b')
fairfax_df.plot('date_updated', 'votes_rep', marker='D', color='r', ax=ax)
fairfax_df.plot('date_updated', 'absentee_dem', linestyle='--', marker='o', color='b', alpha=0.35, ax=ax)
fairfax_df.plot('date_updated', 'absentee_rep', linestyle='--', marker='D', color='r', alpha=0.35, ax=ax)
ax.legend(['Biden total votes', 'Trump total votes', 
           'Biden absentee votes', 'Trump absentee votes'])
ax.set_ylabel('Fairfax County Vote Counts')
ax.set_xlabel("Date/time ('mm-dd hh' format)")
ax.set_xlim([pd.Timestamp('2020-11-04T01'), pd.Timestamp('2020-11-04T09')])
ax.set_ylim([-10000, 55e4])
```
[](./example_fig4.png)

The window on this second figure starts two hours earlier than the previous figure, and you can see how to vote count seems to plateau around ~100k votes for each candidate with some strange spikes occuring in the middle.  I checked Fairfax County's election results webpage and found that the plateau agrees pretty well with the official election day vote tallies, while the second spike and subsequent plateau on the right side of the plot are consistent with the absentee ballots being counted as well.

A couple things are evident.  One, except for the first spike, it appears that the NY Times never found out that the absentee ballots had been counted as absentee ballots.  Two, it seems evident that the county was having some problems loading their absentee counts such that they had to take them offline and put them back up again twice!  What is more, the peak of the first spike is higher for Biden and lower for Trump than the second spike and final plateau... I wonder what went on in the counting room that required this adjustment?

Finally, for those who question whether the strange spikes are simply artifacts of corrupted data, I looked up an archived CBS election night broadcast [video feed](https://archive.org/details/KPIX_20201104_000000_CBS_News_2020_Election_Night_--_America_Decides/start/17460/end/17520) (check out 8:51pm, 9:17pm, 9:23pm, and 9:39pm all PST, and also 11:41pm at this [continuation](https://archive.org/details/KPIX_20201104_073500_CBS_News_2020_Election_Night_--_America_Decides/start/360/end/420) of the same broadcast) and was able to find inconsistencies that agree with what we see in the plots here.  Since both CBS and the NY Times were probably using the same Edison Research data, I conclude that any data corruption issues would enter the pipeline at or before Edison Research.  

Regardless of where they entered the pipeline, however, it only seems logical that these spikes would occur through human intervention of some sort, because the data before and after make sense, and the other counties make sense (including their absentee ballot counts).  Certainly, this example shows that there is a lot one can glean from county level timeseries!
