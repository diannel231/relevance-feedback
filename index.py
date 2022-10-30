import re
import os
import collections
import time
import lucene
import time
#from java.io import File
from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.util import Version
from org.apache.lucene.store import FSDirectory
from java.nio.file import Paths

# Indexer imports:
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
# from org.apache.lucene.store import SimpleFSDirectory

from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search.similarities import ClassicSimilarity
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser

class index:
    corpus_path = "./time/time.all"
    corpus_index_folder = "./index1"
    
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
                    #print(current_file_id+":::"+str(len(doctext)))
                current_file_id = list(filter(None, line.split()))[1]
                doctext = ""
            else:
                doctext += line
        file.close() # close the file pointer
    
    def __init__(self):
        print("Building Documents Dictionary")        
        self.build_doc_dict()
        print("Building Index")
        self.buildIndex()
        #lucene.initVM()
        
        
    def buildIndex(self):
        directory = FSDirectory.open(Paths.get(index.corpus_index_folder))
        analyzer = StandardAnalyzer()
        config = IndexWriterConfig(analyzer)
        self.writer = IndexWriter(directory, config)
        i = 0
        for docid, text in self.doc_files.items():
            doc = Document() # create a new document
            doc.add(TextField("id", docid, Field.Store.YES))
            doc.add(TextField("text", text, Field.Store.YES))
            self.writer.addDocument(doc)
            i+=1
        print(f"{i} files indexed")
        self.writer.close()
		#function to read documents from collection, tokenize and build the index with tokens
		# implement additional functionality to support relevance feedback
		#use unique document integer IDs

    def rocchio(self, query_terms, pos_feedback, neg_feedback, alpha, beta, gamma):
        print("hlle")
	#function to implement rocchio algorithm
	#pos_feedback - documents deemed to be relevant by the user
	#neg_feedback - documents deemed to be non-relevant by the user
	#Return the new query  terms and their weights
	
    def query(self, query_terms, k):
	#function for exact top K retrieval using cosine similarity
	#Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
        query = QueryParser("text", StandardAnalyzer()).parse("NASSAU")
        # retrieving top 50 results for each query
        directory = FSDirectory.open(Paths.get(index.corpus_index_folder))
        searcher = IndexSearcher(DirectoryReader.open(directory))
        searcher.similarity = ClassicSimilarity() #vector space
        scoreDocs = searcher.search(query, 50).scoreDocs
        for result in scoreDocs:
            d = searcher.doc(result.doc)
            print(d["id"], result.score)
        #print(scoreDocs)
	
    def print_dict(self):
        print("hlle")
    #function to print the terms and posting list in the index

    def print_doc_list(self):
        print("hlle")
	# function to print the documents and their document id
    
c = index()