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

   *Note 0: The `county_presidential.csv.gz` data file is gzipped in order to stay under github.com's file size limits. The uncompressed file takes about 5 MB of storage space.*

## Examples

Examples forthcoming...
