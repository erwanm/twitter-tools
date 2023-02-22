# twitter-tools
A few scripts to collect/process Twitter data through the official API

## Requirements

### Valid Twitter developer account

Most of these scripts require a Twitter developer account, some more precisely [an academic account](https://developer.twitter.com/en/products/twitter-api/academic-research).  A valid Twitter API account must be provided by setting an environment var as follows:

```
export BEARER_TOKEN='<your_bearer_token>'
```

### Twarc2 

Most of these scripts require the [twarc2](https://twarc-project.readthedocs.io/en/latest/twarc2_en_us/) python library.


## Snowballing "grandparents"

Idea: from an initial set of "seed users", collect all the following/followers of these users. Filter users who have specific words in their description, here words which are likely markers for older adults:

```
 grandchild grandfather grandmother granddad granny grandparent retired retirement
```

Then filter the location of the remanining users based on their location field (free text, so people can say anything). A list of Irish towns is used to capture locations in Ireland.

Finally restart this process from the beginning, using the new users as "seed users".

- Main script: `snowball-grandparents.sh`


### Example



```
cat retirement-users-details.tsv | cut -f 1 > grandparents-snowballing.full/retirement-users-ids.list
./snowball-grandparents.sh grandparents-snowballing.full/retirement-users-ids.list 1 10
```

The following output is indicative only:

```
###LOOP nextIndex=1 ###
 Collecting fron Twitter step 1 ...
  grandparents-snowballing.full/iter.1: filtering ...
 New grandparents IRL step 1 = 1480
###LOOP nextIndex=2 ###
 Collecting fron Twitter step 2 ...
  grandparents-snowballing.full/iter.2: filtering ...
 New grandparents IRL step 2 = 266
###LOOP nextIndex=3 ###
  Collecting fron Twitter step 3 ...
  grandparents-snowballing.full/iter.3: filtering ...
 New grandparents IRL step 3 = 273
###LOOP nextIndex=4 ###
  Collecting fron Twitter step 4 ...
  grandparents-snowballing.full/iter.4: filtering ...
 New grandparents IRL step 4 = 118
###LOOP nextIndex=5 ###
  Collecting fron Twitter step 5 ...
  grandparents-snowballing.full/iter.5: filtering ...
 New grandparents IRL step 5 = 46
###LOOP nextIndex=6 ###
  Collecting fron Twitter step 6 ...
  grandparents-snowballing.full/iter.6: filtering ...
 New grandparents IRL step 6 = 25
###LOOP nextIndex=7 ###
  Collecting fron Twitter step 7 ...
  grandparents-snowballing.full/iter.7: filtering ...
 New grandparents IRL step 7 = 6
###LOOP nextIndex=8 ###
  Collecting fron Twitter step 8 ...
  grandparents-snowballing.full/iter.8: filtering ...
 New grandparents IRL step 8 = 4
###LOOP nextIndex=9 ###
  Collecting fron Twitter step 9 ...
  grandparents-snowballing.full/iter.9: filtering ...
 New grandparents IRL step 9 = 5
###LOOP nextIndex=10 ###
  Collecting fron Twitter step 10 ...
  grandparents-snowballing.full/iter.10: filtering ...
 New grandparents IRL step 10 = 4
```

One can see that in this case the filtering causes less and less users to be retrieved, as we reach close to the full set of target users satisfying the constraints. The collected users are obtained as follows:

```
cat grandparents-snowballing.full/iter.?.grandparents.IRL > grandparents-snowballing.full.tsv
```

The output file contains the following tab-separated columns:     

```
user_id username full_name user_description user_location country_ids
```

Note: `country_ids` are heuristically predicted from the user location with `filter-user-location.py` and the list of cities `places-iso3.tsv` obtained from https://simplemaps.com/data/world-cities (licence CC BY 4.0).

## Collecting tweets authored by a set of users



```
cut -f 1 grandparents-snowballing.full.tsv > grandparents-snowballing.full.list
```

`timeline.py` collects the timeline of a (set of) user(s) as follows:

```
python3 timeline.py grandparents-snowballing.full.list grandparents-snowballing.full.timeline.tsv
```

The output file (2nd arg) contains the following tab-separated columns:     

```
user_id id text conversation_id created_at lang retweet_count reply_count like_count quote_count geo
```

