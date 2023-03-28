from twarc.client2 import Twarc2
import os
import json
import sys, getopt
from collections import defaultdict
from os.path import exists


PROG_NAME = "collect-following.py"

skip_existing_output = True

follower = False
detail_input_user = False
overlap_min = 1
print_only_if_location = True

# Your bearer token here
bearer_token = os.environ.get("BEARER_TOKEN")
t = Twarc2(bearer_token=bearer_token)


def usage(out):
    print("Usage: "+PROG_NAME+" [options] <file OR user> <output file>",file=out)
    print("",file=out)
    print("  Given a list of users (usernames or user ids), retrieves the full list of the accounts that ",file=out)
    print("  each user follows (or the list of their followers of -r is used).",file=out)
    print("  Details about the users collected include description and location.",file=out)
    print("  ",file=out)
    print("  A valid Twitter API account must be provided by setting an env var as follows:",file=out)
    print("    export BEARER_TOKEN='<your_bearer_token>'",file=out)
    print("  If a file is provided, it should contain a user on each line.",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -o <min overlap>: include user if at least this number of initial users follow them",file=out)
    print("    -r: collect followers instead of following",file=out)
    print("    -d: delete any existing output (default: skip if existing).",file=out)
    print("    -s: collect detailed profile for the input users themselves (instead of following/followers).",file=out)
    print("    -e: print all users even if they don't have a location defined (default: only if location).",file=out)

    print("",file=out)


def collect_following(users, output_file):

    followed = defaultdict(list)

    if not skip_existing_output or not exists(output_file):

        if detail_input_user:
            content = t.user_lookup(users)
            for i, users_page in enumerate(content):
                
                if 'data' in users_page:
                    print(f"Fetched a page of {len(users_page['data'])} users ", flush=True)
                    for datum in users_page['data']:
                        followed[datum['id']].append(datum)
                else:
                    print(f"Warning: No 'data' field found:", users_page, file=sys.stderr, flush=True)
        else:

            # Iterate over our target users
            for user_id in users:
            
                if follower:
                    content = t.followers(user_id)
                else:
                    content = t.following(user_id)
                
                # apparently users can be provided either as ids or usernames
                for i, following_page in enumerate(content):
                
                    if 'data' in following_page:
                        print(f"Fetched a page of {len(following_page['data'])} following for user {user_id}", flush=True)
                        for datum in following_page['data']:
                            followed[datum['id']].append(datum)
                        else:
                            print(f"Warning: No 'data' field found:", following_page, file=sys.stderr, flush=True)

        with open(output_file,"w") as outfile:
            outfile.write("user_id\tusername\tname\tdescription\tlocation\n")
            for (id, l) in followed.items():
                if len(l) >= overlap_min:
                    datum = l[0]
                    if not print_only_if_location or "location" in datum:
                        outfile.write("{}\t{}\t{}\t{}\t{}\n".format(datum.get("id"),
                                                                datum.get("username"),
                                                                fix_string(datum.get("name")),
                                                                fix_string(datum.get("description")),
                                                                fix_string(datum.get("location"))
                                                                ))

    else:
        print(f"Skipping because {output_file} exists.", file=sys.stderr, flush=True)

 
def fix_string(s):
    if s is None:
        return "NA"
    else:
        return ' '.join(s.splitlines())


def main():
    global overlap_min 
    global follower
    global skip_existing_output
    global detail_input_user
    global print_only_if_location
    try:
        opts, args = getopt.getopt(sys.argv[1:],"ho:rdse")
    except getopt.GetoptError:
        usage(sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage(sys.stdout)
            sys.exit()
        elif opt == "-o":
            overlap_min = int(arg)
        elif opt == "-r":
            follower = True
        elif opt == "-s":
            detail_input_user = True
        elif opt == "-d":
            skip_existing_output = False
        elif opt == "-e":
            print_only_if_location = False
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
    if follower and detail_input_user:
        raise Exception("-r and -s are not compatible.")

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
