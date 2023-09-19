#import logging
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from pprint import pprint
from gensim import corpora, models

import os
import sys, getopt
import random
from collections import defaultdict



PROG_NAME = "write-gensim-corpus.py"

nwords=0

def usage(out):
    print("Usage: "+PROG_NAME+" [options] <corpus prefix> <output>",file=out)
    print("",file=out)
#    print("  <input data dir> contains subdirectories, one per document.",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -n <n words /doc> (default=0 for full doc)",file=out)

    print("",file=out)






def main():
    global nwords
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hn:")
    except getopt.GetoptError:
        usage(sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage(sys.stdout)
            sys.exit()
        elif opt == "-n":
            nwords = int(arg)

    if len(args) != 2:
        usage(sys.stderr)
        sys.exit(2)

    corpus_prefix = args[0]
    output_file = args[1]



    corpus = corpora.MmCorpus(corpus_prefix)
    dictionary = corpora.Dictionary.load(corpus_prefix+'.dict')
    #    print(len(corpus))
    #    print(len(dictionary))

    temp = dictionary[0]  # This is only to "load" the dictionary.
    id2word = dictionary.id2token

    with open(output_file, 'w') as output:
        for doc_no,doc in enumerate(corpus):
            doc_sample = [ dictionary[w] for w,f in doc ]
            if nwords>0 and len(doc_sample)>nwords:
                doc_sample = random.sample(doc_sample, nwords)
            output.write(f"{doc_no}\t"+" ".join(doc_sample)+"\n")


    

if __name__ == "__main__":
    main()
