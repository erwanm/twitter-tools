from twarc.client2 import Twarc2
import os
import json
import sys, getopt
from collections import defaultdict
import datetime


PROG_NAME = "search-multiple-requests.py"

extra_string = ""
max_tweets = None


# Your bearer token here
bearer_token = os.environ.get("BEARER_TOKEN")
t = Twarc2(bearer_token=bearer_token)

datetime_format = "%Y-%m-%d"
utc_start_time_timeline = datetime.datetime.strptime("2010-12-01", datetime_format)


def usage(out):
    print("Usage: "+PROG_NAME+" [options] <input requests file> <output file>",file=out)
    print("",file=out)
    print("  Reads a list of requests line by line, queries Twitter for each of them and writes the results.",file=out)
    print("  If the input file doesn't exist, first arg interpreted as single query.",file=out)
    print("  Note: conversation id included with the tweet, can be used to retrieve full conversations.",file=out)
    print("",file=out)
    print("  A valid Twitter API account must be provided by setting an env var as follows:",file=out)
    print("    export BEARER_TOKEN='<your_bearer_token>'",file=out)
    print("  If a file is provided, it should contain a user on each line.",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -a <extra string>: add this string to every request",file=out)
    print("    -m <N> stop collecting for query after N tweets",file=out)
    print("    -t <start date>: start date with format 2022-12-31, year>2010",file=out)
    print("",file=out)


def run_queries(requests, output_file):

    with open(output_file,"w") as outfile:
        outfile.write("query\tid\tuser_id\ttext\tconversation_id\tcreated_at\tlang\tretweet_count\treply_count\tlike_count\tquote_count\tgeo\n")
        for request in requests:

            r =request
            if len(extra_string) > 0:
                r += " " + extra_string
            # Iterate over pages of tweets
            nb_collected = 0
            try:
                for i, tweets in enumerate(t.search_all(r, start_time=utc_start_time_timeline)): 

                    print(f"Fetched a page of {len(tweets['data'])} tweets for query {r}")
                    nb_collected += len(tweets['data'])
                    for datum in tweets['data']:
                        outfile.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(r,
                                                                                           datum.get("id"),
                                                                                           datum.get("author_id"),
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
                    if max_tweets is not None and nb_collected >= max_tweets:
                        print(nb_collected, max_tweets)
                        break
            except:
                print("Warning: an error occcured with the query '"+r+"'", file=sys.stderr)




 


def main():
    global extra_string
    global max_tweets
    global utc_start_time_timeline
    try:
        opts, args = getopt.getopt(sys.argv[1:],"ha:m:t:")
    except getopt.GetoptError:
        usage(sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage(sys.stdout)
            sys.exit()
        elif opt == "-a":
            extra_string = arg
        elif opt == "-m":
            max_tweets = int(arg)
        elif opt == "-t":
            utc_start_time_timeline = utc_start_time_timeline = datetime.datetime.strptime(arg, datetime_format)

    if len(args) != 2:
        usage(sys.stderr)
        sys.exit(2)

    req_file = args[0]
    output_file = args[1]
    
    if os.path.exists(req_file):
        with open(req_file) as infile:
            requests = [ line.rstrip() for line in infile ]
    else:
        requests = [ req_file ]
    run_queries(requests, output_file)


if __name__ == "__main__":
    main()







