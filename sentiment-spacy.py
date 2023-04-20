import os
import sys, getopt
from collections import defaultdict
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob


PROG_NAME = "sentiment-spacy.py"

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('spacytextblob')


def usage(out):
    print("Usage: cat <sentences> | "+PROG_NAME+" [options] <output file>",file=out)
    print("",file=out)
    print("  Apply sentiment analysis to the input sentences/tweets. ",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("",file=out)



def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"h")
    except getopt.GetoptError:
        usage(sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage(sys.stdout)
            sys.exit()
#        elif opt == "-l":
#            use_lemma = True
#        elif opt == "-p":
#            keep_pos = arg.split(",")
    if len(args) != 1:
        usage(sys.stderr)
        sys.exit(2)

    output_file = args[0]
      
    with open(output_file,"w") as outfile:
        for line in sys.stdin:
            sentence = line.rstrip()
            doc = nlp(sentence)
            outfile.write(str(doc._.blob.polarity)+"\t"+str(doc._.blob.subjectivity)+"\t"+str(doc._.blob.sentiment_assessments.assessments)+"\n")


if __name__ == "__main__":
    main()
