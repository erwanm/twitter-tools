import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from pprint import pprint
from gensim import corpora, models

import os
import sys, getopt
import random
from collections import defaultdict



PROG_NAME = "gensim-topics.py"

model_type = "lda"
ncores=1
ntopics=10
nworkers=64

pmi= False

def usage(out):
    print("Usage: "+PROG_NAME+" [options] <corpus prefix> <output>",file=out)
    print("",file=out)
#    print("  <input data dir> contains subdirectories, one per document.",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -m <model type>. Possible values: lda, ens, lsi. Default: "+model_type,file=out)
    print("    -c <cores>. Default: "+str(ncores),file=out)
    print("    -t <N>. Number of topics. Default: "+str(ntopics),file=out)
    print("    -w <N>. Number of LDA models for ensemble. Default: "+str(nworkers),file=out)
    print("    -p use PMI for top words and write PMI values.",file=out)
#    print("    -c <cities file>: list of accepted place names.",file=out)
#    print("    -a: no filtering on location at all.",file=out)

    print("",file=out)


def compute_pmi(corpus, word_given_topic_probs, dico):
    
    word_freq = defaultdict(int)
    n_word = 0
    for doc in corpus:
        for (i,freq) in doc:
            word_freq[dico[i]] += freq
            n_word += freq
    pmi_by_topic = []
    for topic_no, wgt in enumerate(word_given_topic_probs):
        pmi_by_topic.append({ w : p * n_word / word_freq[w] for w,p in wgt.items() })
    return pmi_by_topic


# returns tuple (doc_probs_by_topic, sorted_doc_probs_by_doc, top_docs_by_topic, topic_probs)
def topic_per_doc(model, corpus, top_n = None):
    doc_probs_by_topic = defaultdict(list)
    sorted_doc_probs_by_doc = []
    for doc_no, row in enumerate(model[corpus]):
        print(f"\r{doc_no}",end='', file=sys.stderr)
        #        print(row,file=sys.stderr)
        # below because the result format appears to differ between lda and ensemble lda:
        if type(row[0]) == tuple:
            doc_info = row
        else:
            doc_info = row[0]
        for topic_no, prob in doc_info:
            doc_probs_by_topic[topic_no].append((doc_no, prob))
        # sort by descending prob
        doc_probs = sorted(doc_info, key=lambda x: x[1], reverse=True)
        sorted_doc_probs_by_doc.append(doc_probs)
    top_docs_by_topic = []
    topic_probs = []
    #    for topic_no, doc_prob_pairs in enumerate(doc_probs_by_topic):
    for topic_no, doc_prob_pairs in doc_probs_by_topic.items():
        top = sorted(doc_prob_pairs, key=lambda x: x[1], reverse=True)
        if top_n is not None:
            top = top[0:top_n]
        top_docs_by_topic.append(top)
        marginal = sum([ p for doc,p in doc_prob_pairs]) / len(corpus)
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
    


def display_topics(model, corpus, dictionary, output_prefix, with_probs=False, top_n_words = 15, top_n_docs = 5, doc_random_n = 12):
    doc_probs_by_topic, sorted_doc_probs_by_doc, top_docs_by_topic, topic_probs = topic_per_doc(model, corpus, top_n_docs)
    word_given_topic_probs = model.get_topics()
    wgt_by_topic_as_dict = [ { dictionary[i] : p for i,p in enumerate(wgt) } for wgt in word_given_topic_probs ]
    top_pmi_by_topic = []
    if pmi:
        pmi_by_topic = compute_pmi(corpus, wgt_by_topic_as_dict, dictionary)
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
            for topic_no,l in enumerate(wgt_by_topic_as_dict):
                top_indexes = sorted(l.items(), key = lambda pair: pair[1], reverse = True)
                for rank, (w, v) in enumerate(top_indexes):
                    full_output.write("{}\t{}\t{}\t{}\n".format(topic_no, rank, w, v))
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
                    doc_sample = [ dictionary[w] for w,f in corpus[top_doc] ]
                    if len(doc_sample)>doc_random_n:
                        doc_sample = random.sample(doc_sample, doc_random_n)
                    print('   ',"{:.2f}".format(prob),  doc_sample, file=output_stream)
                print(file=output_stream)




def main():
    global model_type
    global ncores
    global ntopics
    global nworkers
    global pmi
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hm:t:c:w:p")
    except getopt.GetoptError:
        usage(sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage(sys.stdout)
            sys.exit()
        elif opt == "-m":
            model_type = arg
        elif opt == "-c":
            ncores = int(arg)
        elif opt == "-t":
            ntopics = int(arg)
        elif opt == "-w":
            nworkers = int(arg)
        elif opt == "-p":
            pmi = True
#        elif opt == "-M":
#            max_prop = float(arg)

    if len(args) != 2:
        usage(sys.stderr)
        sys.exit(2)

    corpus_prefix = args[0]
    output_prefix = args[1]



    corpus = corpora.MmCorpus(corpus_prefix)
    dictionary = corpora.Dictionary.load(corpus_prefix+'.dict')
    #    print(len(corpus))
    #    print(len(dictionary))

    temp = dictionary[0]  # This is only to "load" the dictionary.
    id2word = dictionary.id2token

    for i,w in dictionary.items():
        if w == '':
            raise Exception('Error: empty word at index ',i,', there was a problem at corpus creation.')

    model = None
    if model_type == "lda":
        model = models.LdaMulticore(corpus, 
                                    id2word=id2word, 
                                    num_topics=ntopics,
                                    workers=ncores,
                                    per_word_topics=True )
        display_topics(model,corpus, dictionary, output_prefix)
    elif model_type == "ens":
        model = models.EnsembleLda(corpus=corpus,
                                   id2word=id2word,
                                   num_topics=ntopics,
#                                   passes=2,
#                                   iterations = 200,
                                   num_models=ncores,
                                   topic_model_class=models.LdaModel,
                                   ensemble_workers=nworkers,
                                   distance_workers=ncores)
        display_topics(model,corpus, dictionary, output_prefix)
    elif model_type == "lsi":
        model = models.LsiModel(corpus=corpus,
                                id2word=id2word,
                                num_topics=ntopics,
                                onepass=False)
        display_topics(model,corpus, dictionary, output_prefix)
    else:
        raise Exception(f"Invalid model id '{model_type}'")



    

if __name__ == "__main__":
    main()




