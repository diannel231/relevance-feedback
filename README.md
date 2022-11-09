# relevance-feedback

## How to execute code
  - Install python
  - Copy the index.py, stoplist.txt, and collections files
  - run "python index.py"

### build_doc_dict()
Read in files, filters out stopwords and saves the generated document vectors to a json file

### getFreqOfTermInWords()
Counts the number of instances of a term inside a list of words

### buildDocumentVector()
Takes in a list of tuples as a query and returns the list of tuples relevant to the inverted document frequency

### buildDictionary()
Adds new words from the document list to the dictionary

### buildIndex()
Builds the file index using the standard analyzer and necessary feild type data

### query()
Uses cosine simiarity to take an exact top k measurement of the query and return the result vector

### rocchio_docVectors()
Uses the rocchio algorithm to claculate the positive, negative and query aspects of the calculation which are later used in the query study function

### do_query_study()
gets query feedback by using the rocchio values to get better and better queries through multiple iterations

### getExpandedQueryText()
Generates the query and weight values for the new expanded queries

### getAvgPrecision()
Calculates mean average percision of the results by caculating when relevant results occur in the query and taking the average value

### filter_words_with_stoplist()
Calculates the cosine of two documents for later use in the inexact retrieval methods

### filter_query_text_return_text()
returns the list of words as a vector

### __init__()
Returns the Id dictionary

### rocchio_queryText()
gets the file name from the document Id dictionary

### parseTimeQueryFile()
Takes in a list of tuples as a query and returns a list of the most relevant tuples in the list for inexact search methods

### parseTimeRel()
Takes in a list of words in a document as a query and returns a list with information on how frequent each term in the list is compared to every other term as a percentage

### print_dict()
Returns the Id dictionary

### print_doc_list()
returns the text of a document by inputting a file name
