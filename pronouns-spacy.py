import os
import sys, getopt
from collections import defaultdict
import spacy


PROG_NAME = "pronouns-spacy.py"

nlp = spacy.load("en_core_web_sm")

possesssive_included = True


def usage(out):
    print("Usage: cat <sentences> | "+PROG_NAME+" [options] <output file>",file=out)
    print("",file=out)
    print("  Parses sentences read from STDIN, one per line, and for every sentence analyzes the pronouns and ",file=out)
    print("  prints their attribute/number. The output contains: a header line, followed by one line for  ",file=out)
    print("  every input sentence, followed by one SPECIAL line at the end with the totals for all the sentences. ",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -p: only personal pronouns (default) and NOT possessive pronouns.",file=out)
    print("",file=out)



def main():
    global possesssive_included
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hp")
    except getopt.GetoptError:
        usage(sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage(sys.stdout)
            sys.exit()
        elif opt == "-p":
            possesssive_included = False
#        elif opt == "-p":
#            keep_pos = arg.split(",")
    if len(args) != 1:
        usage(sys.stderr)
        sys.exit(2)

    output_file = args[0]
      
    global_lemmas = defaultdict(int)
    global_sentMorph = defaultdict(int)
    morph_pairs = set()
    data = []
    for line in sys.stdin:
        sentence = line.rstrip()
        doc = nlp(sentence)
        #print(sentence)
        sentMorph = defaultdict(int)
        lemmas = defaultdict(int)
        for token in doc:
            if token.pos_ == 'PRON' and 'PronType=Prs' in token.morph and (possesssive_included or not 'Poss=Yes' in token.morph):
                lemmas[token.lemma_] += 1
                global_lemmas[token.lemma_] += 1
                for keyValuePair in token.morph:
                    sentMorph[keyValuePair] += 1
                    global_sentMorph[keyValuePair] += 1
                    morph_pairs.add(keyValuePair)
        data.append( (lemmas, sentMorph) )
    
    sorted_morph = sorted(morph_pairs)
    with open(output_file,"w") as outfile:
        # header
        outfile.write('lemmas')
        for pair in sorted_morph:
            outfile.write("\t"+pair)
        outfile.write('\n')
        # data
        for lemmas, sentMorph in data:
            outfile.write(' '.join([ token+':'+str(n) for token, n in lemmas.items() ]))
            for pair in sorted_morph:
                n = sentMorph.get(pair)
                if n is None:
                    outfile.write("\t0")
                else:
                    outfile.write("\t"+str(n))
            outfile.write('\n')
        # SPECIAL LAST LINE: total number of everything
        outfile.write(' '.join([ token+':'+str(n) for token, n in global_lemmas.items() ]))
        for pair in sorted_morph:
            n = global_sentMorph.get(pair)
            if n is None:
                outfile.write("\t0")
            else:
                outfile.write("\t"+str(n))
        outfile.write('\n')

if __name__ == "__main__":
    main()
