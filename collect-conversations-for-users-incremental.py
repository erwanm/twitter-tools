from twarc.client2 import Twarc2
import os
import json
import sys, getopt
from collections import defaultdict

import datetime


PROG_NAME = "collect-conversations-for-users-incremental.py"


only_print_conv_ids = False
load_conv_ids = False
filter_lang = True
max_tweets = None
datetime_format = "%Y-%m-%d"
utc_start_time_timeline = datetime.datetime.strptime("2010-12-01", datetime_format)
#utc_start_time_timeline = datetime.datetime(2010, 12, 1, 0, 0, 0, 0, datetime.timezone.utc)
#print("Datetime: ", utc_start_time_timeline)

# Your bearer token here
bearer_token = os.environ.get("BEARER_TOKEN")
t = Twarc2(bearer_token=bearer_token)




def usage(out):
    print("Usage: "+PROG_NAME+" [options] <file OR user> <output prefix>",file=out)
    print("",file=out)
    print("  Given a list of users (first arg), collects the timeline of every user and then",file=out)
    print("  the full conversations (threads) in which the user's tweets took place.",file=out)
    print("",file=out)
    print("  A valid Twitter API account must be provided by setting an env var as follows:",file=out)
    print("    export BEARER_TOKEN='<your_bearer_token>'",file=out)
    print("  If a file is provided, it should contain a user on each line.",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -s <N>: start at user N (default 0)",file=out)
    print("    -t <start date>: start date with format 2022-12-31, year>2010",file=out)
    print("    -c only collect conversation ids and write them",file=out)
    print("    -C conversation ids as input, write the tweets as output WITHOUT header.",file=out)
    print("    -l accept all languages (default: filter English only).",file=out)
    print("    -m <N> stop colelctiing conversation after N tweets",file=out)

    print("",file=out)


def collect(users, output_prefix, utc_start_time_timeline, start_at_user=0):

    count_conv = 0
    conv_by_nb_tweets = defaultdict(int)
    conv_by_nb_users = defaultdict(int)

    # Iterate over our target users
    for user_no,user_id in enumerate(users):
        if user_no >= start_at_user:
            with open(output_prefix+'.'+str(user_id),"w") as outfile:
                if not only_print_conv_ids:
                    outfile.write("conversation_id\tuser_id\ttweet_id\tcreated_at\ttext\tlang\tretweet_count\treply_count\tlike_count\tquote_count\tgeo\n")
                conversations = defaultdict(dict)
                try:
                    for i, tweets in enumerate(t.timeline(user_id,exclude_retweets=True,start_time=utc_start_time_timeline)): 
                        print(f"Fetched a page of {len(tweets['data'])} tweets for user {user_no}/{len(users)} {user_id} ({len(conversations)} conversations so far for this user), oldest:{tweets['data'][-1]['created_at']}", flush=True)
                        for datum in tweets['data']:
                            conv_id = datum["conversation_id"]
                            conversations[conv_id][datum['id']] = datum
                            count_conv += 1

                    conv_no = 0
                    for conv_id, conv_dict in conversations.items():
                        conv_no += 1
                        if only_print_conv_ids:
                            outfile.write(conv_id+"\n")
                        else:
                            users_this_conv = set()
                            q="conversation_id:{}".format(conv_id)
                            if filter_lang:
                                q =  q+" lang:en"
                            nb_collected = 0
                            for i, tweets in enumerate(t.search_all(q)): 
                                print(f"   Fetched a page of {len(tweets['data'])} tweets for conversation {conv_id} ({conv_no}/{len(conversations)}, user {user_no}/{len(users)}), oldest:{tweets['data'][-1]['created_at']}", flush=True)
                                nb_collected += len(tweets['data'])
                                for datum in tweets['data']:
                                    #print(datum.keys())
                                    conv_dict[datum['id']] = datum
                                    users_this_conv.add(datum.get("author_id"))
                                    conv_by_nb_users[len(users_this_conv)] += 1
                                    conv_by_nb_tweets[len(conv_dict)] += 1
                                    for tweet_id, datum in sorted(conv_dict.items(), key=lambda item: item[1]['created_at'], reverse = True):
                                        outfile.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(datum.get("conversation_id"),
                                                                                                        datum.get("author_id"),
                                                                                                        tweet_id,
                                                                                                        datum.get("created_at"),
                                                                                                        datum['text'].replace('\n',' '),
                                                                                                        datum.get("lang"),
                                                                                                        datum['public_metrics']["retweet_count"],
                                                                                                        datum['public_metrics']["reply_count"],
                                                                                                        datum['public_metrics']["like_count"],
                                                                                                        datum['public_metrics']["quote_count"],
                                                                                                        datum.get("geo")))
                                if max_tweets is not None and nb_collected >= max_tweets:
                                    break
                                        #                print("Stats so far: number conversations (second value) by number of tweets (first value):")
                                        #                for nb_tweets, freq in conv_by_nb_tweets.items():
                                        #                    print(nb_tweets, " : ", freq)
                                        #                print("Stats so far: number conversations (second value) by number of users (first value):")
                                        #                for nb_users, freq in conv_by_nb_users.items():
                                        #                    print(nb_users, " : ", freq)
                except Exception:
                    print(f"An error happened with user '{user_id}', skipping.", file=sys.stderr)


def collect_tweets_from_conv_ids(conversations, output_prefix):

    for conv_no, conv_id in enumerate(conversations):
        with open(output_prefix+'.'+str(conv_id),"w") as outfile:
            q="conversation_id:{}".format(conv_id)
            if filter_lang:
                q =  q+" lang:en"
            nb_collected = 0
            for i, tweets in enumerate(t.search_all(q)): 
                print(f"   Fetched a page of {len(tweets['data'])} tweets for conversation {conv_id} ({conv_no}/{len(conversations)}, oldest:{tweets['data'][-1]['created_at']}", flush=True)
                nb_collected += len(tweets['data'])
                for datum in tweets['data']:
                    #print(datum.keys())
                    outfile.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(datum.get("conversation_id"),
                                                                                                        datum.get("author_id"),
                                                                                                        datum.get("id"),
                                                                                                        datum.get("created_at"),
                                                                                                        datum['text'].replace('\n',' '),
                                                                                                        datum.get("lang"),
                                                                                                        datum['public_metrics']["retweet_count"],
                                                                                                        datum['public_metrics']["reply_count"],
                                                                                                        datum['public_metrics']["like_count"],
                                                                                                        datum['public_metrics']["quote_count"],
                                                                                                        datum.get("geo")))
                if max_tweets is not None and nb_collected >= max_tweets:
                    break
#                except Exception:
#                    print(f"An error happened with user '{user_id}', skipping.", file=sys.stderr)



def main():
    #    global overlap_min 
    global utc_start_time_timeline
    global only_print_conv_ids
    global load_conv_ids
    global filter_lang
    global max_tweets

    start_at = 0
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hs:t:cClm:")
    except getopt.GetoptError:
        usage(sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage(sys.stdout)
            sys.exit()
        elif opt == "-s":
            start_at = int(arg)
        elif opt == "-t":
            utc_start_time_timeline = utc_start_time_timeline = datetime.datetime.strptime(arg, datetime_format)
        elif opt == "-c":
            only_print_conv_ids = True
        elif opt == "-C":
            load_conv_ids = True
        elif opt == "-l":
            filter_lang = False
        elif opt == "-m":
            max_tweets = int(arg)

    if len(args) != 2:
        usage(sys.stderr)
        sys.exit(2)

    users_file = args[0]
    output_file = args[1]
    
    if os.path.exists(users_file):
        with open(users_file) as infile:
            users = [ line.rstrip() for line in infile ]
    else:
        users = [ users_file ]

    if load_conv_ids:
        collect_tweets_from_conv_ids(users,output_file)
    else:
        collect(users, output_file, utc_start_time_timeline, start_at)


if __name__ == "__main__":
    main()
