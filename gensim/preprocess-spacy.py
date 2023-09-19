import os
import sys, getopt
from collections import defaultdict
#from gensim import corpora
import spacy

PROG_NAME = "preprocess-gensim.py"

nlp = spacy.load("en_core_web_sm")

keep_pos = None
content_pos = [ "NOUN", "VERB", "PROPN", "ADJ", "ADV", "INTJ" ]
use_lemma = False
remove_stop_words = False
remove_at_user = False

provided_col_nos = None

lowercase = True

def usage(out):
    print("Usage: ls <files> | "+PROG_NAME+" [options] <output dir>",file=out)
    print("",file=out)
    print("  Reads input tweet files as tsv, applies Spacy and writes the resulting text ",file=out)
    print("  to a file named like the first input file in a subdir <output dir>/<conv id>.",file=out)
    print("  <output dir> must exist.",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -l: use lemma instead of token",file=out)
    print("    -p <pos list>: list of retained POS tags, others discarded. Default: all accepted.",file=out)
    print("                   (POS tags separated by comma)", file=out)
    print("                   See list at https://universaldependencies.org/u/pos/", file=out)
    print("    -P shortcut for '-p "+",".join(content_pos)+"' (content words)", file=out)
    print("    -s: remove stop words.",file=out)
    print("    -a: remove every '@user' ",file=out)
    print("    -c <conv_id>,<user_id>,<text>: the input files don't have a header. The col no to use ",file=out)
    print("                                 for columns 'conversation_id', 'user_id' and 'text' is given as argument.",file=out)
    print("    -m keep mixed case (default: transform to lowercase).",file=out)
    print("",file=out)



def read_input_files(filenames):
    data = {}
    for file_no, filename in enumerate(filenames):
        with open(filename, newline="\n") as infile:
            header = False
            data_this_user = defaultdict(list)
            if provided_col_nos is not None:
                conv_col = provided_col_nos[0]
                user_col = provided_col_nos[1]
                text_col = provided_col_nos[2]
            else:
                text_col = None
                conv_col = None
                user_col = None
            for line in infile:
                fields = line.rstrip().replace("\r", " ").split('\t')
                if len(fields) > 1:
                    if header or provided_col_nos is not None:
                        try:
                            data_this_user[fields[conv_col]].append((fields[user_col], fields[text_col]))
                        except IndexError:
                            print(conv_col)
                            print(user_col)
                            print(text_col)
                    else:
                        if "conversation_id" in fields and "text" in fields and "user_id" in fields:
                            conv_col = fields.index("conversation_id")
                            user_col = fields.index("user_id")
                            text_col = fields.index("text")
                        header = True
                        if text_col is None or conv_col is None or user_col is None:
                            raise Exception(f"Col name 'text' and/or 'conversation_id' and/or 'user_id' not found in supposed header [{','.join(fields)}] in file '{filename}'")
                else:
                    print('Weird line??', fields,file=sys.stderr)
            for conv_id, text_list in data_this_user.items():
                if data.get(conv_id) is None:
                    data[conv_id] = text_list
#                    print(conv_id, text_list)
                else:
                    if len(data[conv_id]) != len(text_list):
                        raise Exception(f"Unexpected: same conversation id {conv_id} but different content.")
    return data


def preprocess(data, input_file, output_dir):

    no = 0
    for conv_id,user_tweet_pairs in data.items():
        no += 1
        print(f"preprocessing conv {no}/{len(data)} ({len(user_tweet_pairs)} tweets)", flush= True, file=sys.stderr)
        target_dir = os.path.join(output_dir, conv_id)
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
        output_file = os.path.join(target_dir, input_file)
        with open(output_file,"w") as outfile:
            for user, tweet in user_tweet_pairs:
                new_doc = []
                spacy_doc = nlp(tweet)
                for token in spacy_doc:
                    #                print(token.text, token.lemma_, token.pos_, token.shape_, token.is_alpha, token.is_stop)
                    if not remove_stop_words or not token.is_stop:
                        if keep_pos is None or token.pos_ in keep_pos:
                            val = token.text
                            if not remove_at_user or val[0] != '@':
                                if use_lemma:
                                    val = token.lemma_
                                if lowercase:
                                    val = val.lower()
                                new_doc.append(val)
                outfile.write(user+"\t"+" ".join(new_doc)+"\n")
                


def main():
    global keep_pos
    global content_pos
    global use_lemma 
    global remove_stop_words 
    global remove_at_user
    global provided_col_nos
    global lowercase 
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hlsp:Pac:m")
    except getopt.GetoptError:
        usage(sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage(sys.stdout)
            sys.exit()
        elif opt == "-l":
            use_lemma = True
        elif opt == "-p":
            keep_pos = arg.split(",")
        elif opt == "-P":
            keep_pos = content_pos
        elif opt == '-s':
            remove_stop_words = True
        elif opt == '-a':
            remove_at_user = True
        elif opt == '-c':
            provided_col_nos =  [ int(x) for x in arg.split(",") ] 
        elif opt == '-m':
            lowercase = False
    if len(args) != 1:
        usage(sys.stderr)
        sys.exit(2)

    output_dir = args[0]
      
    filenames = []
    for line in sys.stdin:
        filename = line.rstrip()
        if os.path.exists(filename):
            filenames.append(filename)
        else:
            raise Exception(f"File not found: {filename}")
#    if not os.path.exists(output_dir):
#        os.mkdir(output_dir)

    print("Reading...", flush=True)
    conversations = read_input_files(filenames)
    print("Processing...", flush=True)
    preprocess(conversations, os.path.basename(filenames[0]), output_dir)

if __name__ == "__main__":
    main()
