# twitter-tools
A few scripts to collect/process Twitter data through the official API

## Twarc2 and Twitter developer account

- Most of these scripts require a Twitter developer account, some more precisely an academic account.
- Most of these scripts require the [twarc2](https://twarc-project.readthedocs.io/en/latest/twarc2_en_us/) python library.


## Snowballing "grandparents"

Idea: from an initial set of "seed users", collect all the following/followers of these users. Filter users who have specific words in their description, here words which are likely markers for older adults:

```
 grandchild grandfather grandmother granddad granny grandparent retired retirement
```

Then filter the location of the remanining users based on their location field (free text, so people can say anything). A list of Irish towns is used to capture locations in Ireland.

Finally restart this process from the beginning using the new users as "seed users".

- Main script: `snowball-grandparents.sh`
