import os
import sys, getopt
from collections import defaultdict
from gensim import corpora
import spacy

PROG_NAME = "conv-to-doc.py"

nlp = spacy.load("en_core_web_sm")


def usage(out):
    print("Usage: "+PROG_NAME+" [options] <tsv conv file> <output dir>",file=out)
    print("",file=out)
    print("  TODO",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
#    print("    -o <min overlap>: include user if at least this number of initial users follow them",file=out)
#    print("    -b: do not add default query filter: '"+default_filters+"'",file=out)
#    print("    -c <cities file>: list of accepted place names.",file=out)
#    print("    -a: no filtering on location at all.",file=out)

    print("",file=out)



def read_input_files(filenames):
    data = {}
    for file_no, filename in enumerate(filenames):
        with open(filename, newline="\n") as infile:
            data_this_user = defaultdict(list)
            text_col = None
            conv_col = None
            for line in infile:
                fields = line.rstrip().replace("\r", " ").split('\t')
                if len(fields) > 1:
                    if text_col is None:
                        for col_no,col_name in enumerate(fields):
                            if col_name == 'text':
                                text_col = col_no
                            if col_name == 'conversation_id':
                                conv_col = col_no
                        if text_col is None or conv_col is None:
                            raise Exception(f"Col name 'text' not found in supposed header [{','.join(fields)}] in file '{filename}'")
                    else:
                        try:
                            data_this_user[fields[conv_col]].append(fields[text_col])
                        except IndexError:
                            print(conv_col)
                            print(text_col)
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


def preprocess(data, remove_stop=True, keep_pos=["NOUN", "VERB", "PROPN", "ADJ", "ADV", "INTJ" ], use_lemma=True, min_freq=3):

    frequency = defaultdict(int)
    processed = []
    no = 0
    for conv,tweets in data.items():
        no += 1
        print(f"preprocessing conv {no}/{len(data)}")
        new_doc = []
        for tweet in tweets:
            spacy_doc = nlp(tweet)
            for token in spacy_doc:
                #                print(token.text, token.lemma_, token.pos_, token.shape_, token.is_alpha, token.is_stop)
                if not remove_stop or not token.is_stop:
                    if keep_pos is None or token.pos_ in keep_pos:
                        val = token.text
                        if use_lemma:
                            val = token.lemma_
                        frequency[val] += 1
                        new_doc.append(val)
        processed.append(new_doc)
    texts = []
    for doc in processed:
        texts.append([ token for token in doc if frequency[token] >= min_freq ])
    return texts


def save_data(corpus, fname):
    #dictionary.filter_extremes(no_below=20, no_above=0.5)
    dictionary = corpora.Dictionary(corpus)
    bow = [ dictionary.doc2bow(doc) for doc in corpus ]
    corpora.MmCorpus.serialize(fname, bow, dictionary)  # store to disk, for later use
    dictionary.save(fname+".dict")

def process(input_file, output_dir):
    header = False
    with open(input_file, newline="\n") as f:
        for line in f:
            fields = line.rstrip().replace("\r", " ").split("\t")
            if not header:
                col_conv_id = fields.index("conversation_id")
                col_text = fields.index("text")
                header = True
            else:
                conv_id = fields[col_conv_id]
                text = fields[col_text]
                target_file = os.path.join(output_dir, conv_id)
                with open(target_file, "a") as output:
                    output.write(text+"\n")

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"ho:")
    except getopt.GetoptError:
        usage(sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage(sys.stdout)
            sys.exit()
#        elif opt == "-o":
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

    input_file = args[0]
    output_dir = args[1]
    
    if os.path.exists(input_file):
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        process(input_file, output_dir)
    else:
        print('Error input file not found')

if __name__ == "__main__":
    main()
