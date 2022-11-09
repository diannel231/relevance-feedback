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
Removes common words to improve results by eliminating generic values


