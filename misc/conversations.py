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
    print("Usage: "+PROG_NAME+" [options] <file OR conversation id> <output file>",file=out)
    print("",file=out)
    print("  Reads a list of conversations ids and collects their content through the Twitter API.",file=out)
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


def collect_conversations(conv_ids, output_file):

    with open(output_file,"w") as outfile:
        outfile.write("user_id\tid\ttext\tconversation_id\tcreated_at\tlang\tretweet_count\treply_count\tlike_count\tquote_count\tgeo\n")
        # Iterate over our target users
        for conv_id in conv_ids:

            # Iterate over pages of tweets
            q="conversation_id:{}".format(conv_id)
            print(q)
            for i, tweets in enumerate(t.search_all(q)): 

                print(f"Fetched a page of {len(tweets['data'])} tweets for {conv_id}")
                for datum in tweets['data']:
                    #print(datum.keys())
                    outfile.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(datum.get("author_id"),
                                                                                           datum.get("id"),
                                                                                           datum['text'].replace('\n',' '),
                                                                                           datum.get("conversation_id"),
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

    convs_file = args[0]
    output_file = args[1]
    
    if os.path.exists(convs_file):
        with open(convs_file) as infile:
            conv_ids = [ line.rstrip() for line in infile ]
    else:
        conv_ids = [convs_file]
    collect_conversations(conv_ids, output_file)


if __name__ == "__main__":
    main()
