import os
import json
import sys, getopt
import time
import re
from collections import defaultdict

excluded_places = ['northern ireland' ]

PROG_NAME = "filter-user-location.py"

def usage(out):
    print("Usage: cat <input locations> | "+PROG_NAME+" [options] <cities-iso3.tsv resource>",file=out)
    print("",file=out)
    print("  Reads location descriptions from Twitter users on STDIN, one by line (only location),",file=out)
    print("  then serches for known places within each using the <cities-iso3.tsv resource>",file=out)
    print("    and prints a new column of countries codes corresponding to each location.",file=out)
    print("  <cities-iso3.tsv resource> contains several colums, last one is country code.",file=out)
    print("  Any match from any field in the other columns maps to this country.",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -i: prints the input line and adds the country code as a new column.",file=out)
#    print("    -c <cities file>: list of accepted place names.",file=out)
#    print("    -a: no filtering on location at all.",file=out)

    print("",file=out)




def main():

    print_input = False
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi")
    except getopt.GetoptError:
        usage(sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage(sys.stdout)
            sys.exit()
        elif opt == "-i":
            print_input = True

    #print("debug args after options: ",args)

    if len(args) != 1:
        usage(sys.stderr)
        sys.exit(2)

    cities_file = args[0]

    cocode_by_place = defaultdict(set)

    with open(cities_file) as infile:
        for line in infile:
            fields = line.rstrip().split("\t")
            cocode = fields.pop()
            for f in fields:
                if len(f) > 3:
                    cocode_by_place[f].add(cocode)
                else:
                    print(f"Warning: ignoring short place  string '{f}'", file=sys.stderr)

    for line in sys.stdin:
        location = line.rstrip()
        collected = set()
        for place, cocodes in cocode_by_place.items():
            if re.search(place, location, re.IGNORECASE):
                collected = collected.union(cocodes)
        if 'IRL' in collected:
            for place in excluded_places:
                if re.search(place, location, re.IGNORECASE):
                    collected.remove('IRL')

        if print_input:
            print(line.rstrip()+"\t", end='')
        print(" ".join(collected))
        sys.stdout.flush()


if __name__ == "__main__":
    main()

