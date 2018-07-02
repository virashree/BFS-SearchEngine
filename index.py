# Created By: Virashree Patel

from collections import Counter
from math import log2, pow, sqrt

class Index:

    # returns words and their occurrences in form of dictionary for the  given file
    @staticmethod
    def term_frequency(tokens):
        if type(tokens) is list:
            termFreqTable = dict(Counter(tokens))
            return termFreqTable
        else:
            return None

    @staticmethod
    def build_inverted_index(doc, inverted_index):
        if type(doc) is dict and type(inverted_index) is dict:
            docUrl = doc['url']
            tokens = doc['tokens']
            for key, value in tokens.items():
                if key not in inverted_index:
                    inverted_index[key] = {}
                    inverted_index[key][docUrl] = value
                else:
                    inverted_index[key][docUrl] = value
            return inverted_index
        else:
            return None

    def tf_idf(self, inverted_index, no_doc):
        if type(inverted_index) is dict:
            tf_idf = {}
            # idf = {}
            for key, value in inverted_index.items():
                term = key  # term
                diD_tf = value  # document Id as key , term freq as value
                df = len(diD_tf)  # document freq
                idf = log2(no_doc/df)  # idf for the term
                # idf[term] = idf

                for d_id, tf in diD_tf.items():
                    if d_id in tf_idf:
                        tf_idf[d_id][term] = round(tf*idf, 3)
                    else:
                        tf_idf[d_id] = {}
                        tf_idf[d_id][term] = round(tf*idf, 3)
            return tf_idf
        else:
            return None

    @staticmethod
    def get_document_frequency(term, inverted_index):
        if term in inverted_index:
            return len(inverted_index[term])
        else:
            return 0

    def tf_idf_query(self, term_freq, inverted_index, no_doc):
        if type(term_freq) is dict:
            tf_idf = {}
            for term, freq in term_freq.items():
                df = self.get_document_frequency(term, inverted_index)
                if df != 0:
                    idf = log2(no_doc / df)
                    tf_idf[term] = round(freq*idf, 3)
                else:
                    tf_idf[term] = 0
            return tf_idf
        else:
            return None

    def cos_similarity(self, doc, query):
        if type(doc) is dict and type(query) is dict:
            dot_product = round(sum(query[key]*doc.get(key, 0) for key, value in query.items()), 3)
            document_vector_length = self.vector_length(doc)
            query_vector_length = self.vector_length(query)
            cos_sim = round(dot_product / (document_vector_length * query_vector_length), 3)
            return cos_sim

    @staticmethod
    def vector_length(vector):
        return round(sqrt(sum(pow(vector[key], 2) for key, value in vector.items())), 3)

    @staticmethod
    def rank_list(list, threshold):
        return list[:threshold]

    @staticmethod
    def recall(relevant_docs, retrieved_docs):
        if type(retrieved_docs) is list and type(relevant_docs) is list:
            retrieved_relevant_docs = [x for x in relevant_docs for y in retrieved_docs if x == y[0]]
            no_retrieved_relevant_docs = len(retrieved_relevant_docs)
            no_relevant_docs = len(relevant_docs)
            recall = no_retrieved_relevant_docs / no_relevant_docs
            return recall

    @staticmethod
    def precision(relevant_docs, retrieved_docs):
        if type(retrieved_docs) is list and type(relevant_docs) is list:
            retrieved_relevant_docs = [x for x in relevant_docs for y in retrieved_docs if x == y[0]]
            no_retrieved_relevant_docs = len(retrieved_relevant_docs)
            no_retrieved_docs = len(retrieved_docs)
            precision = no_retrieved_relevant_docs / no_retrieved_docs
            return precision

















