import re
import os
import collections
import time
import lucene
import time
import json
import random
import numpy as np
from os.path import exists
#from java.io import File
from org.apache.lucene.document import Document, Field, FieldType, StringField, TextField
from org.apache.lucene.util import Version
from org.apache.lucene.store import FSDirectory
from java.nio.file import Paths

# Indexer imports:
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
# from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import *
from org.apache.lucene.search import *
from org.apache.lucene.search.similarities import *
from org.apache.lucene.index import *
from org.apache.lucene.queryparser.classic import *
    

class index:
    corpus_path = "./time/time.all"
    corpus_index_folder = "./index7"
    dictionary = []
    stop_list = []
    docVectors = {}
    doc_files = []
    def build_doc_dict(self):
        file = open(index.corpus_path) # open in read mode
        lines = file.readlines()
        self.doc_files = {}
        current_file_id = 0
        doctext = ""
        for line in lines:
            if line.startswith("*TEXT"):
                #beginning of next text file. save what we have so far as a document
                if doctext != "":
                    self.doc_files[current_file_id] = doctext
                    docWords = self.filter_words_with_stoplist(doctext)
                    self.buildDictionary(docWords)
                    #print(current_file_id+":::"+str(len(doctext)))
                current_file_id = list(filter(None, line.split()))[1]
                doctext = ""
            else:
                doctext += line
        
        #build docVector dictionary
        file_exists = exists("./docVectors.json")
        if file_exists:
            #deserialize vectors
            f = open("./docVectors.json", "r")
            jsonText = f.read()
            self.docVectors = json.loads(jsonText)
            self.docVectors = {int(k):v for k,v in self.docVectors.items()}
            print(f"read {len(self.docVectors)} doc vectors")
        else:
            for d in self.doc_files:
                #todo: this is called twice, once above. optimize it later!
                docWords = self.filter_words_with_stoplist(self.doc_files[d])
                print(f"Building document vector for docId {d}")
                self.docVectors[d] = self.buildDocumentVector(docWords)
            jsText = json.dumps(self.docVectors)
            f = open("./docVectors.json","w")
            f.write(jsText)
            f.close()
            file.close() # close the file pointer
    
    
    
    def filter_words_with_stoplist(self, text):
        with open("./stop-list.txt") as file:
            self.stop_list = file.read().split('\n')
        text = text.replace('\n',' ')
        words = re.sub('[^a-zA-Z \n]', '', text).lower().split()
        word_array_cleaned = []
        for word in words:
            if word not in self.stop_list:
                word_array_cleaned.append(word)
        return word_array_cleaned
        
    def filter_query_text_return_text(self, query_text, return_text):
        query_array_cleaned = self.filter_words_with_stoplist(query_text)
        if return_text:
            return ' '.join(word for word in query_array_cleaned)
        return query_array_cleaned
    
    def getFreqOfTermInWords(self, term, words):
        i = 0
        for word in words:
            if term == word:
                i+=1
        return i
    
    def buildDocumentVector(self, docWords):
        #print("docWords", docWords)
        vector = {}
        for dictWord in self.dictionary:
            vector[dictWord] = self.getFreqOfTermInWords(dictWord, docWords)
        return list(vector.values())
            
    def buildDictionary(self, docWords):
        for word in docWords:
            if word not in self.dictionary:
                self.dictionary.append(word)
    
    def __init__(self):
        #lucene.initVM()
        print("Building Documents List")        
        self.build_doc_dict()
        #print("Building Index")
        #self.buildIndex()
        
		#function to read documents from collection, tokenize and build the index with tokens
		# implement additional functionality to support relevance feedback
		#use unique document integer IDs    
    def buildIndex(self):
        directory = FSDirectory.open(Paths.get(index.corpus_index_folder))
        analyzer = StandardAnalyzer()
        config = IndexWriterConfig(analyzer)
        self.writer = IndexWriter(directory, config)
        i = 0
        for docid, text in self.doc_files.items():
            doc = Document() # create a new document
            doc.add(TextField("id", docid, Field.Store.YES))
            f = FieldType()
            f.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS_AND_OFFSETS);
            f.setStored(True);
            f.setStoreTermVectors(True);
            field = Field("text", text, f)
            doc.add(field)
            self.writer.addDocument(doc)
            i+=1
        print(f"{i} files indexed")
        self.writer.close()

        #function to implement rocchio algorithm
        #s_feedback - documents deemed to be relevant by the user
        #g_feedback - documents deemed to be non-relevant by the user
        #turn the new query  terms and their weights
    def rocchio_docVectors(self, docVectors, alpha, beta, gamma):
        pos_feedback = []
        neg_feedback = []
        for doc in docVectors:
            if doc == "q1":
                continue
            #print("doc[2]", docVectors[doc][2])
            if docVectors[doc][2] == 1:
                pos_feedback.append(doc)
            else:
                neg_feedback.append(doc)
        q1Vector = np.array(docVectors["q1"][3])
        num_of_pos_feedback = len(pos_feedback)
        num_of_neg_feedback = len(neg_feedback)
        sum_of_pos_docs = []
        sum_of_neg_docs = []
        for i in range(len(q1Vector)):
            sum_of_pos_docs.append(0)
            sum_of_neg_docs.append(0)
        sum_of_pos_docs = np.array(sum_of_pos_docs)
        sum_of_neg_docs = np.array(sum_of_neg_docs)
        for doc in pos_feedback:
            docNp = np.array(docVectors[doc][3])
            sum_of_pos_docs = sum_of_pos_docs + docNp
        for doc in neg_feedback:
            docNp = np.array(docVectors[doc][3])
            sum_of_neg_docs = sum_of_neg_docs + docNp
        #print(f"({alpha} * q1Vector) + (({beta} / {num_of_pos_feedback}) * sum_of_pos_docs) - (({gamma} / {num_of_neg_feedback}) * sum_of_neg_docs)")
        queryExp = (alpha * q1Vector) + ((beta / num_of_pos_feedback) * sum_of_pos_docs) - ((gamma / num_of_neg_feedback) * sum_of_neg_docs)
        return queryExp
    
    def rocchio_queryText(self, query_text, k, alpha, beta, gamma):
        docVectors = self.query(query_text, k)
        self.rocchio_docVectors(docVectors, alpha, beta, gamma)
    	
	
    def query(self, query_text, k):
        query_terms = self.filter_query_text_return_text(query_text, False)
        #function for exact top K retrieval using cosine similarity
        #Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
        query = QueryParser("text", StandardAnalyzer()).parse(query_text)
        # retrieving top 50 results for each query
        directory = FSDirectory.open(Paths.get(index.corpus_index_folder))
        searcher = IndexSearcher(DirectoryReader.open(directory))
        searcher.similarity = ClassicSimilarity() #vector space
        results = searcher.search(query, k)
        scoreDocs = results.scoreDocs
        #idxReader = searcher.getIndexReader()
        qvector = self.buildDocumentVector(query_terms)
        result_vector = {}
        result_vector["q1"] = (1, 0, 0, qvector)
        for result in scoreDocs:
            luc_doc = searcher.doc(result.doc)
            docId = int(luc_doc.get("id"))
            if docId in list(self.docVectors.keys()):
                result_vector[docId] = (result.score, docId, random.randint(0, 1), self.docVectors[docId])
            else:
                print("docId that not in docVectors", docId)
            #print(searcher.explain(query, result.doc))
            #rawDoc = searcher.doc(result.doc)
            #terms = idxReader.getTermVector(result.doc, "text")
            #termEnum = terms.iterator()
            #bytesRef = termEnum.next() --> No Next() !! ERROR !
        return result_vector
    
    def getExpandedQueryText(self, exQuery, threshold_value):
        q = ""
        for i in range(len(exQuery)):
            if exQuery[i] >= threshold_value:
                #print("exQuery[i]", exQuery[i])
                q += (self.dictionary[i] + " ")
        #print("Expanded query: ", q)
        return q
	
    def parseTimeQueryFile(self):
        file = open("./time/time.que","r") # open in read mode
        lines = file.readlines()
        self.query_map = {}
        current_query_id = 0
        querytext = ""
        for line in lines:
            if line.startswith("*FIND"):
                #beginning of next query text. save what we have so far in a dict
                if querytext != "":
                    self.query_map[current_query_id] = querytext
                current_query_id = list(filter(None, line.split()))[1]
                querytext = ""
            else:
                querytext += line
    
    def parseTimeRel(self):
        file = open("./time/time.rel","r") # open in read mode
        lines = file.readlines()
        self.relevance_map = {}
        for line in lines:
            p = list(filter(None, line.split()))
            if len(p) > 6: # pick only 5 or more relevant docs, 5 + 1
                self.relevance_map[p[0]] = p[1:]

    
    def print_dict(self):
        print("hello")
    #function to print the terms and posting list in the index

    def print_doc_list(self):
        print("hello")
	# function to print the documents and their document id
    
    def getAvgPrecision(self, results):
        i = 0
        avg_numerator = 0
        relevant_count = 0
        for doc in results: # doc= (score, docid, relevance, vector)
            result = results[doc]
            i += 1
            if result[2] == 1:
                relevant_count += 1
                p = relevant_count / i
                avg_numerator += p
        return avg_numerator / relevant_count
            
    def do_query_study(self, query):
        alpha = 1
        beta = 0.75
        gamma = 0.15
        threshold_value = 1.5
        k = 10
        num_of_rocchio_iterations = 5
        mapval = 0
        for iteration in range(num_of_rocchio_iterations):
            results = self.query(query, k)
            print("\n\n-----------iteration#", str(iteration+1)+"-------------")
            print("query:",query)
            print("-----------------------------------------------------")
            num_of_relevant_docs = 0
            num_of_nonrelevant_docs = 0
            total_num_relevant_docs = random.randint(k, len(list(self.doc_files.keys())))
            for result in results:# doc= (score, docid, relevance, vector)
                if results[result][0] == 1:
                    continue
                if results[result][2] == 1:
                    num_of_relevant_docs += 1
                else:
                    num_of_nonrelevant_docs += 1
                #print("result:",results[result][0], "docId:",results[result][1])
            precision = num_of_relevant_docs / k
            recall = num_of_relevant_docs / total_num_relevant_docs
            f_measure = (2 * precision * recall)/ (precision + recall)
            average_precision = self.getAvgPrecision(results)
            mapval += average_precision
            print("precision:", precision, "\nrecall: ", recall, "\nf_measure:", f_measure, "\naverage_precision:", average_precision)
            exp_query_vector = self.rocchio_docVectors(results, alpha, beta, gamma)
            query = self.getExpandedQueryText(exp_query_vector, threshold_value)
        print("\nM.A.P:",mapval/num_of_rocchio_iterations)
        #pseudo relevance feedback - r =  # 0 = NR, 1 = R
        #
c = index()

#docVectors = c.query("nassau", 10)
#expanded_query = c.rocchio("nassau british government", 10, alpha, beta, gamma)
#print("EXPANDED QUERY VECTOR", expanded_query)
#text = c.getExpandedQueryText(expanded_query, threshold_value)
c.parseTimeQueryFile()
c.parseTimeRel()

# part 3 -- begin study
# query_for_test = {key:c.query_map[key] for key in list(c.relevance_map.keys())[5:10]}
# for i, query in query_for_test.items():
#     c.relevance_map[i] = [int(d) for d in c.relevance_map[i]]
#     total_relevant_for_query = len(c.relevance_map[i])
#     k = int(total_relevant_for_query*2)#np.ceil(total_relevant_for_query/2)
#     query = c.filter_query_text_return_text(query, True)
#     print("--------------------------------------------------")
#     print(f"query# {i} k = {k}: ", query)
#     result_vector = c.query(query, k)
#     result_doc_ids = list(result_vector.keys())[1:]
#     result_doc_ids.sort()
#     print("Result doc ids", result_doc_ids)
#     print("Relevant doc ids", c.relevance_map[i])
#     common = len(set(result_doc_ids) & set(c.relevance_map[i]))
#     print("Common elements", common)

#part 3 - study while ignoring relevant documents in TIME.REL

    
    
query_ids_to_test = {key:c.query_map[key] for key in list(c.query_map.keys())[:5]}
for qid in query_ids_to_test:
    query = query_ids_to_test[qid]
    c.do_query_study(query)
    #exp_q_text = c.getExpandedQueryText(expanded_query, threshold_value)
    print("\n\n=========================================================")
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        