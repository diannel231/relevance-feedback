import re
import os
import collections
import time
import lucene
import time
import numpy as np
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
    stop_list = []
    
    
    def filter_words_with_stoplist(self, text):
        with open(self.path + "./stop-list.txt") as file:
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
    
    def buildDocumentVector(self, rawDoc, query_terms):
        words = self.filter_words_with_stoplist(rawDoc)
        vector = []
        for term in query_terms:
            i = 0
            for word in words:
                if word == term:
                    i += 1
            vector.append(i)
        return vector
            
    def __init__(self):
        #lucene.initVM()
        #print("Building Documents Dictionary")        
        #self.build_doc_dict()
        #print("Building Index")
        #self.buildIndex()
        self.query(["asd"], 5)
        
    
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
		#function to read documents from collection, tokenize and build the index with tokens
		# implement additional functionality to support relevance feedback
		#use unique document integer IDs

    def rocchio(self, query_text, pos_feedback, neg_feedback, alpha, beta, gamma):
        docVectors = self.query(query_text, 10)
        q1Vector = np.array(docVectors["q1"])
        num_of_pos_feedback = len(pos_feedback)
        num_of_neg_feedback = len(neg_feedback)
        sum_of_pos_docs = []
        sum_of_neg_docs = []
        for i in len(q1Vector):
            sum_of_pos_docs.append(0)
            sum_of_neg_docs.append(0)
        sum_of_pos_docs = np.array(sum_of_pos_docs)
        sum_of_neg_docs = np.array(sum_of_neg_docs)
        for doc in pos_feedback:
            docNp = np.array(docVectors[doc])
            sum_of_pos_docs = sum_of_pos_docs + docNp
        for doc in neg_feedback:
            docNp = np.array(docVectors[doc])
            sum_of_neg_docs = sum_of_neg_docs + docNp
        queryExp = (alpha * q1Vector) + \
        ((beta / num_of_pos_feedback) * sum_of_pos_docs) - \
        ((gamma / num_of_neg_feedback) * sum_of_neg_docs)
        print("Expanded query vector", queryExp)
        return queryExp
        
    	#function to implement rocchio algorithm
    	#pos_feedback - documents deemed to be relevant by the user
    	#neg_feedback - documents deemed to be non-relevant by the user
    	#Return the new query  terms and their weights
	
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
        qvector = []
        for qterm in query_terms:
            qf = idxReader.totalTermFreq(Term("text",qterm))
            qvector.append(qf)
        docVectors = {"q1":qvector}
        #print("DFFF", df)
        for result in scoreDocs:
            print("RESULT!", result)
            rawDoc = searcher.doc(result.doc)
            docVector = self.buildDocumentVector(rawDoc, query_terms)
            docVectors[result.doc] = docVector
            #terms = idxReader.getTermVector(result.doc, "text")
            #termEnum = terms.iterator()
            # print("dir termENUM", dir(termEnum))
            # print("dir TERMS", dir(terms))
            # print("term", termEnum.term())
            # print("terms members", dir(terms))
            # print("freq",termEnum[1].docFreq(), termEnum[1].totalTermFreq())
            # bref = BytesRef("nassau")
            # bytesRef = termEnum.seekExact(bref)
            # print("bytesre", bytesRef)
            # #while bytesRef != None:
            # if termEnum.seekExact(bref):                    
            #     term = bref.utf8ToString(); 
            #     print("TERM!!", term)
            #     bytesRef = termEnum.next()
                #idf = tfidfSIM.idf( termEnum.docFreq(), reader.numDocs() );
                    #docFrequencies.put(term, idf);
            #print("STATS!!!", terms.getStats())
            #print("TERM VECTORS!!",terms)
        #print(scoreDocs)
        return docVectors
	
    def print_dict(self):
        print("hlle")
    #function to print the terms and posting list in the index

    def print_doc_list(self):
        print("hlle")
	# function to print the documents and their document id
    
c = index()