import os
import sys, getopt
from collections import defaultdict
from pathlib import Path
from pprint import pprint
import random


from tweetopic import TopicPipeline, DMM
from sklearn.feature_extraction.text import CountVectorizer



PROG_NAME = "test-tweetopic.py"
n_topics = 30

min_freq = 12
max_prop = .3

min_words = 1

pmi= False

def usage(out):
    print("Usage: "+PROG_NAME+" [options] <input data dir> <output prefix>",file=out)
    print("",file=out)
    print("  <input data dir> contains subdirectories, one per document.",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -m <min freq>. default: "+str(min_freq),file=out)
    print("    -M <max prop>. default: "+str(max_prop),file=out)
    print("    -w <min words in tweet>. default: "+str(min_words),file=out)
    print("    -p use PMI for top words and write PMI values.",file=out)
#    print("    -a: no filtering on location at all.",file=out)

    print("",file=out)



# returns tuple (doc_probs_by_topic, sorted_doc_probs_by_doc, top_docs_by_topic, topic_probs)
def topic_per_doc(doc_probs, top_n = None):
    doc_probs_by_topic = defaultdict(list)
    sorted_doc_probs_by_doc = []
    for doc_no, row in enumerate(doc_probs):
        print(f"\r{doc_no}",end='', file=sys.stderr)
        for topic_no, prob in enumerate(row):
            doc_probs_by_topic[topic_no].append((doc_no, prob))
        # sort by descending prob
        s_doc_probs = sorted(doc_probs_by_topic[topic_no], key=lambda x: x[1], reverse=True)
        sorted_doc_probs_by_doc.append(s_doc_probs)
    top_docs_by_topic = []
    topic_probs = []
    #    for topic_no, doc_prob_pairs in enumerate(doc_probs_by_topic):
    for topic_no, doc_prob_pairs in doc_probs_by_topic.items():
        top = sorted(doc_prob_pairs, key=lambda x: x[1], reverse=True)
        if top_n is not None:
            top = top[0:top_n]
        top_docs_by_topic.append(top)
        marginal = sum([ p for doc,p in doc_prob_pairs]) / len(doc_probs)
        topic_probs.append(marginal)
    return doc_probs_by_topic, sorted_doc_probs_by_doc, top_docs_by_topic, topic_probs


def write_doc_probs(doc_probs_by_topic, output_file):
    with open(output_file, 'w') as out:
        for topic_no,  doc_prob_pairs in doc_probs_by_topic.items():
            for doc_no, prob in doc_prob_pairs:
                out.write("{}\t{}\t{}\n".format(doc_no,topic_no, prob))
                      
def write_topic_probs(topic_probs, output_file):
    with open(output_file, 'w') as out:
        for topic_no, prob in enumerate(topic_probs):
            out.write("{}\t{}\n".format(topic_no, prob))
    

def compute_pmi(corpus, word_given_topic_probs):
    
    word_freq = defaultdict(int)
    n_word = 0
    for doc in corpus:
        for w in doc:
            word_freq[w] += 1
            n_word += 1
    pmi_by_topic = []
    for topic_no, wgt in enumerate(word_given_topic_probs):
        pmi_by_topic.append({ w : p * n_word / word_freq[w] for w,p in wgt.items() })
    return pmi_by_topic
            

#
# word_given_topic_probs = as dict (w, p(w|t))
#
def display_topics(corpus, doc_probs, word_given_topic_probs, output_prefix, with_probs=False, top_n_words = 15, top_n_docs = 5, doc_random_n = 12):

    doc_probs_by_topic, sorted_doc_probs_by_doc, top_docs_by_topic, topic_probs = topic_per_doc(doc_probs, top_n_docs)
    top_pmi_by_topic = []
    if pmi:
        pmi_by_topic = compute_pmi(corpus, word_given_topic_probs)
        with open(output_prefix+".pmi", 'w') as pmi_output:
            for topic_no,pmi_values in enumerate(pmi_by_topic):
                sorted_pmi = sorted(pmi_values.items(), key = lambda pair: pair[1], reverse = True)
                top_pmi_by_topic.append(sorted_pmi[0:top_n_words])
                for rank, (w, pmi_value) in enumerate(sorted_pmi):
                    pmi_output.write("{}\t{}\t{}\t{}\n".format(topic_no, rank, w, pmi_value))

    write_doc_probs(doc_probs_by_topic, output_prefix+".doc-probs")
    write_topic_probs(topic_probs, output_prefix+".topics")

    with open(output_prefix+".out", 'w') as output_stream:
        with open(output_prefix+".word-probs", 'w') as full_output:
            for topic_no,l in enumerate(word_given_topic_probs):
                top_indexes = sorted(l.items(), key=lambda pair: pair[1], reverse=True)
#                print('  DEBUG top topic {} :'.format(topic_no), top_indexes[0],top_indexes[1], top_indexes[2])
                for rank, pair in enumerate(l.items()):
                    full_output.write("{}\t{}\t{}\t{}\n".format(topic_no, rank, pair[0], pair[1]))
                top_indexes = top_indexes[0:top_n_words]
                if pmi:
                    values = top_pmi_by_topic[topic_no]
                else:
                    values = top_indexes
                if with_probs:
                    print(topic_no, ':', "{:.2f}".format(topic_probs[topic_no]), ':' , ", ".join([ w+"["+"{:.3f}".format(p)+"]" for w,p in values ]), file=output_stream)
                else:
                    print(topic_no, ':', "{:.2f}".format(topic_probs[topic_no]), ':' , ", ".join([ w for w,p in values ]), file=output_stream)
                for top_doc, prob in top_docs_by_topic[topic_no]:
                    doc_sample = corpus[top_doc]
                    if len(doc_sample)>doc_random_n:
                        doc_sample = random.sample(doc_sample, doc_random_n)
                    print('   ',"{:.2f}".format(prob),  doc_sample, file=output_stream)
                print(file=output_stream)
                        


def read_tweets(input_dir):
    no = 0
    docs = []
    for subdir_no,subdir in enumerate(Path(input_dir).iterdir()):
        print(f"\r{subdir_no}", end='')
        if subdir.is_dir():
            for filename in Path(os.path.join(input_dir, subdir.name)).iterdir():
                #print(f"   {filename}")
                with open(filename, newline="\n") as infile:
                    for line in infile:
                        fields = line.rstrip().replace("\r", " ").split("\t")
                        if (len(fields)==2):
                            user,tweet = fields
                            tokens = tweet.split(' ')
                            if len(tokens) >= min_words:
                                #print('doc: ',tokens)
                                docs.append(tokens)
                        else:
                            if len(fields)!=1:
                                raise Exception(f"Error, too many fields: {' ; '.join(fields)}")
    return docs


# see https://stackoverflow.com/questions/35867484/pass-tokens-to-countvectorizer
def dummy_tokenizer(doc):
    return doc


def main():
    global min_freq
    global max_prop
    global min_words
    global pmi
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hm:M:w:p")
    except getopt.GetoptError:
        usage(sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage(sys.stdout)
            sys.exit()
        elif opt == "-m":
            min_freq = int(arg)
        elif opt == "-M":
            max_prop = float(arg)
        elif opt == "-w":
            min_words = float(arg)
        elif opt == "-p":
            pmi = True

    if len(args) != 2:
        usage(sys.stderr)
        sys.exit(2)

    input_dir = args[0]
    output_prefix = args[1]

    docs = read_tweets(input_dir)

    dico = defaultdict(int)
    with open(output_prefix+".conv-map", "w") as outfile:
        print("Writing "+output_prefix+".conv-map")
        for no, doc in enumerate(docs):
            #for no, doc in enumerate(raw_corpus):
            #print("\r"+str(no), end='')
            for w in set(doc):
                dico[w] += 1
            outfile.write(str(no)+"\t"+" ".join(doc)+"\n")

#    max_df = int(len(docs) * max_prop)
    print('Number of unique tokens before filtering: %d' % len(dico))
#    dico = {  word: freq for (word,freq) in dico if freq >= min_freq and freq <= max_df }
#    new_docs = []
#    for no, doc in enmerate(docs):
#        new_docs.append([ w in doc if dico.get(w) is not None ])
#    print('Number of unique tokens after filtering: %d' % len(dico))

    # Creating a vectorizer for extracting document-term matrix from the
    # text corpus.
    # see https://stackoverflow.com/questions/35867484/pass-tokens-to-countvectorizer
    vectorizer = CountVectorizer(tokenizer=dummy_tokenizer,
                                 preprocessor=dummy_tokenizer,
                                 min_df=min_freq, 
                                 max_df=max_prop)
    #vectorizer = CountVectorizer(min_df=15, max_df=0.1)

    # Creating a Dirichlet Multinomial Mixture Model with 30 components
    dmm = DMM(n_components=n_topics, n_iterations=100, alpha=0.1, beta=0.1)

    # Creating topic pipeline
    pipeline = TopicPipeline(vectorizer, dmm)

    # for each doc, an array of probs which sum to 1 = p(t|d)
    doc_probs = pipeline.fit_transform(docs)
            
    print('Number of unique tokens after filtering: %d' % len(vectorizer.vocabulary_))

    # docu = https://centre-for-humanities-computing.github.io/tweetopic/tweetopic.pipeline.html#tweetopic.pipeline.TopicPipeline.top_words
    # list[dict[str, int]]: for every word, number of occurences with this topic
    words_by_topic = pipeline.top_words(top_n=None)
    word_freq = defaultdict(int)
    total_by_topic = []
    corpus_total = 0
    word_given_topic = []
    for topic_no,topic in enumerate(words_by_topic):
#        print("  Computing word given topic, topic: ", topic_no)
        w_g_t = {}
        total = 0
        for word_no, (word, freq) in enumerate(topic.items()):
#            print(f"\r  pass 1/ word {word_no}",end='', file=sys.stderr)
            total += freq
            word_freq[word] += freq
#        print()
        total_by_topic.append(total)
        corpus_total += total
        for word_no,(word, freq) in enumerate(topic.items()):
#            print(f"\r  pass 2 / word {word_no}",end='', file=sys.stderr)
            w_g_t[word] = freq / total
#        print()
        word_given_topic.append(w_g_t)
    topic_probs = []
    for count in total_by_topic:
        topic_probs.append(count / corpus_total)
    display_topics(docs, doc_probs, word_given_topic, output_prefix)
    

    

if __name__ == "__main__":
    main()




