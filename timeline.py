from twarc.client2 import Twarc2
import os
import json
import sys, getopt
from collections import defaultdict

PROG_NAME = "timeline.py"

overlap_min = 1

# Your bearer token here
bearer_token = os.environ.get("BEARER_TOKEN")
t = Twarc2(bearer_token=bearer_token)


def usage(out):
    print("Usage: "+PROG_NAME+" [options] <file OR user> <output file>",file=out)
    print("",file=out)
    print("  Reads a list of users and collects their timelinem i.e. every tweet they authored.",file=out)
    print("  Note: conversation id included with the tweet, can be used to retrieve full conversations.",file=out)
    print("",file=out)
    print("  A valid Twitter API account must be provided by setting an env var as follows:",file=out)
    print("    export BEARER_TOKEN='<your_bearer_token>'",file=out)
    print("  If a file is provided, it should contain a user on each line.",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
#    print("    -o <min overlap>: include user if at least this number of initial users follow them",file=out)
#    print("    -b: do not add default query filter: '"+default_filters+"'",file=out)
#    print("    -c <cities file>: list of accepted place names.",file=out)
#    print("    -a: no filtering on location at all.",file=out)

    print("",file=out)


def collect_following(users, output_file):

    with open(output_file,"w") as outfile:
        outfile.write("user_id\tid\ttext\tconversation_id\tcreated_at\tlang\tretweet_count\treply_count\tlike_count\tquote_count\tgeo\n")
        # Iterate over our target users
        for user_id in users:

            # Iterate over pages of tweets
            # apparently users can be provided either as ids or usernames
            for i, tweets in enumerate(t.timeline(user_id,exclude_retweets=True)): 

                print(f"Fetched a page of {len(tweets['data'])} tweets for {user_id}")
                for datum in tweets['data']:
                    outfile.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(user_id,
                                                                                           datum.get("id"),
                                                                                           datum['text'].replace('\n',' '),
                                                                                           datum.get("conversation_id"),
#                                                                                           datum.get("source"),
                                                                                           datum.get("created_at"),
                                                                                           datum.get("lang"),
                                                                                           datum['public_metrics']["retweet_count"],
                                                                                           datum['public_metrics']["reply_count"],
                                                                                           datum['public_metrics']["like_count"],
                                                                                           datum['public_metrics']["quote_count"],
                                                                                           datum.get("geo")
                                                                ))



 


def main():
    #    global overlap_min 
    try:
        opts, args = getopt.getopt(sys.argv[1:],"ho:")
    except getopt.GetoptError:
        usage(sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage(sys.stdout)
            sys.exit()
            #       elif opt == "-o":
            #            overlap_min = int(arg)
        #        elif opt == "-b":
        #            basic = True
    #        elif opt == "-c":
    #            with open(arg) as infile:
    #                accepted_places = [ line.rstrip() for line in infile ]
    #        elif opt == '-a':
    #            filter_loc = False
    #           with open(arg) as infile:
    #                accepted_places = [ line.rstrip() for line in infile ]

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
    collect_following(users, output_file)


if __name__ == "__main__":
    main()
