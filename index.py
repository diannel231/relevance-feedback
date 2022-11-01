import re
import os
import collections
import time
import lucene
import time
import json
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
        
    def filter_query_text_return_text(self, query_text):
        query_array_cleaned = self.filter_words_with_stoplist(query_text)
        return query_array_cleaned#self.join_txt_array_to_string(query_array_cleaned)
    
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
    def rocchio(self, query_text, k, alpha, beta, gamma):
        docVectors = self.query(query_text, k)
        pos_feedback = []
        neg_feedback = []
        for doc in docVectors:
            if doc == "q1":
                continue
            #get feedback from user
            feedback_input = input(f"Enter feedback for the search result with doc id {doc} and score: {docVectors[doc][0]}. Y for positive, N for negative: ")
            if feedback_input.lower() == "y":
                pos_feedback.append(doc)
            else:
                neg_feedback.append(doc)
        q1Vector = np.array(docVectors["q1"][1])
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
            docNp = np.array(docVectors[doc][1])
            sum_of_pos_docs = sum_of_pos_docs + docNp
        for doc in neg_feedback:
            docNp = np.array(docVectors[doc][1])
            sum_of_neg_docs = sum_of_neg_docs + docNp
        print("num_of_pos_feedback",num_of_pos_feedback)
        print("num_of_neg_feedback",num_of_neg_feedback)
        queryExp = (alpha * q1Vector) + \
        ((beta / num_of_pos_feedback) * sum_of_pos_docs) - \
        ((gamma / num_of_neg_feedback) * sum_of_neg_docs)
        return queryExp
        
    	
	
    def query(self, query_text, k):
        query_terms = self.filter_query_text_return_text(query_text)
        #function for exact top K retrieval using cosine similarity
        #Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
        query = QueryParser("text", StandardAnalyzer()).parse(query_text)
        # retrieving top 50 results for each query
        directory = FSDirectory.open(Paths.get(index.corpus_index_folder))
        searcher = IndexSearcher(DirectoryReader.open(directory))
        searcher.similarity = ClassicSimilarity() #vector space
        results = searcher.search(query, 50)
        scoreDocs = results.scoreDocs
        idxReader = searcher.getIndexReader()
        qvector = self.buildDocumentVector(query_terms)
        result_vector = {}
        result_vector["q1"] = (1,qvector)
        #print("QVECTOR!", qvector, "query_terms", query_terms)
        # for qterm in query_terms:
        #     qf = idxReader.totalTermFreq(Term("text",qterm))
        #     qvector.append(qf)
        for result in scoreDocs:
            luc_doc = searcher.doc(result.doc)
            docId = int(luc_doc.get("id"))
            if docId in list(self.docVectors.keys()):
                result_vector[docId] = (result.score,self.docVectors[docId])
            else:
                print("docId that not in docVectors", docId)
            #rawDoc = searcher.doc(result.doc)
            #terms = idxReader.getTermVector(result.doc, "text")
            #termEnum = terms.iterator()
            #bytesRef = termEnum.next() --> No Next() !! ERROR !
        return result_vector
	
    def print_dict(self):
        print("hello")
    #function to print the terms and posting list in the index

    def print_doc_list(self):
        print("hello")
	# function to print the documents and their document id
    
c = index()
#docVectors = c.query("nassau", 10)
alpha = 1
beta = 0.75
gamma = 0.15
expanded_query = c.rocchio("nassau", 10, alpha, beta, gamma)
print("EXPANDED QUERY", expanded_query)