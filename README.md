# relevance-feedback

## How to execute code
  - Install python
  - Copy the index.py, stoplist.txt, and collections files
  - run "python index.py"

### build_doc_dict()
Randomly assigns a number of documents as leaders according to the square root of the total number of documents. The document list is then processed , ignoring the leader documents, to calculate the similarity between remaining documents and assign each document as a follower to the most relevant leader.

### filter_words_with_stoplist()
Calculates the cosine of two documents for later use in the inexact retrieval methods

### filter_query_text_return_text()
returns the list of words as a vector

### getFreqOfTermInWords()
Does the post processing of the results from each search to display relevant information like the number of documents searched and the search results

### buildDocumentVector()
Takes in a list of tuples as a query and returns the list of tuples relevant to the inverted document frequency

### buildDictionary()

### __init__()
Returns the Id dictionary

### buildIndex()
Returns the term frequency for a specific term in a specific document

### rocchio_docVectors()
Gets the term idf for cosing scoring

### rocchio_queryText()
gets the file name from the document Id dictionary

### query()
Creates the term frequenxy-inverse document frequency list

### getExpandedQueryText()
Uses both the invesrted index list and tfidf list to creade a weighted inverted index that contains the tfidf information for the champions lst.

### parseTimeQueryFile()
Takes in a list of tuples as a query and returns a list of the most relevant tuples in the list for inexact search methods

### parseTimeRel()
Takes in a list of words in a document as a query and returns a list with information on how frequent each term in the list is compared to every other term as a percentage

### getAvgPrecision()
Normalizes the documents term frequency by taking the square root of the frequencies log + 1 squared

### do_query_study()
returns the cosine similarty by comparing the term frequency lists to see how much terms have similar frequency within their respective documents

### print_dict()
Returns the Id dictionary

### print_doc_list()
returns the text of a document by inputting a file name
