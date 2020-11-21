# 2020 election: state-general

Unofficial 2020 U.S. general election timeseries data for congressional, senatorial, and presidential races, for individual states and congressional districts.

## Data

The `general_election2020_races_timeseries.csv` dataset expands on one that was uploaded by an anonymous data scientist and is currently circulating.  That dataset scraped the NY Times general election race page directly, whereas this data has been gleaned from archived copies of the NY Times state pages (archived at the [Internet Archive](https://web.archive/org)).  The dataset provided here additionally includes timeseries data for the other general election races (i.e., U.S. Congressional and Senate races).  The timeseries data for these other races is often thinner than for the presidential race, so I have added a date column linking the nearest presidential timeseries date/timestamp to every data row in all the races within a given state (the original timestamps for these other races are preserved in a separate column).  This should facilitate a rough side-by-side comparison of vote counting patterns for, e.g., presidential and congressional races in a particular state.  This approach adds a lot of duplicate entries for the non-presidential races, so if you're interested in just the original timeseries data for a particular congressional or senate race, be sure to drop duplicate rows.

You may download the [general_election2020_races_timeseries.csv](./general_election2020_races_timeseries.csv) or compile it yourself by running the Python script provided.  The dataset includes the following variables:

* `state`             -- The usual uppercase, two-letter state abbreviation (includes all 50 states)
* `race_id`           -- A string indicating the kind of election: `G-P`, `G-S`, and `G-H-##` refer to the Presidential, Senatorial, and Congressional races in a particular state, with `##` representing the congressional district number.  There should also be an `S-S` code in Georgia for the Special Senatorial election.
* `date`              -- A datetime column used as an index for every race within a given state.  See above for more details.
* `timestamp`         -- The (UTC) date/time when the vote information source file was created (*assumed* to correspond to when the vote counts were tallied)
* `votes2020`         -- The total number of votes tallied for all candidates at prior to the time in the `timestamp`
* `vf_dem`            -- Fraction of the `votes` tallied for Joe Biden 
* `vf_rep`            -- Fraction of the `votes` tallied for Donald Trump
* `vf_extra`          -- Fraction of the `votes` tallied for a third candidate, if one is tracked (otherwise it equals 0)
* `votes2016`         -- Total number of votes tallied for the given `state` in 2016
* `margin2016`        -- Percentage points margin of Trump's 2016 victory (or loss where negative)
* `votes2012`         -- Total number of votes tallied for the given `state` in 2012
* `margin2012`        -- Percentage points margin of Romney's 2012 victory (or loss where negative)

## Examples

My goal with the following examples is to give a flavor of the data and provide you with some code to get you started right away.  While these examples deserve some discussion, I strive to be as apolitical as possible with my interpretation.

