from lib.porterStemmer import PorterStemmer
import re
import collections
import math
from tabulate import tabulate
from decimal import *

doc_number = 1095
# read stop word
f_stopwords = open('stop_words.txt')

#retrieve stopwords
raw_stopwords = f_stopwords.read().lower().splitlines()
stopwords = []

stemmer = PorterStemmer()
raw_term_dict = {}
term_dict = {} #{term : {'index' : index, 'df' : df , 'idf' : idf }}
all_tf_dict = {} #{doc_name : { term : tf }}

#stemming for stopword
for n,stopword in enumerate(raw_stopwords):
    new_stopword = stemmer.stem(stopword,0,len(stopword)-1)
    stopwords.append(new_stopword)

def make_dictionary(file_name):
    f = open('data/'+file_name)
    raw_str = f.read()
	
    # lowercase
    raw_str = raw_str.lower()

    # delete non-letters
    regex = re.compile('[^a-zA-Z]')
    raw_str = regex.sub(' ',raw_str)
	
    #tokenize
    tokens = raw_str.split()	
    
    tf_dict = {}  #temr dict {term : tf} for current doc
    #stemming
    stemmer = PorterStemmer()
    for token in list(tokens):
        #stemming for token
        stemmed_token = stemmer.stem(token,0,len(token)-1)
        if stemmed_token in tf_dict:
            #if in tf_dict, just increase it's tf-value in tf_dict ( do nothing to df cause it has been added)
            tf_dict[stemmed_token] += 1
        else:
            #first, check if it's a stopword
            if stemmed_token not in stopwords:
                #save it to tf_dict 
                tf_dict[stemmed_token] = 1
                if stemmed_token in raw_term_dict:
                    #if it existed in raw_term_dict, increase it's df 
                    raw_term_dict[stemmed_token]+=1
                else:
                    raw_term_dict[stemmed_token]=1
    all_tf_dict[file_name] = tf_dict #save tf_dict to all_tf_dict
    print file_name+'....done'
                
#read all 1095 source file
print 'read file....\n'
for i in range(1,doc_number+1):
    make_dictionary(str(i)+'.txt')

#sort dictionary
index = 1 
sorted_dict = {} 
print '\nsaving dicionary.txt...'
dictionary = open('dictionary.txt','w')
table = []
for term in sorted(raw_term_dict):
    df = raw_term_dict[term]
    term_idf = math.log10(Decimal(doc_number)/df)
    term_dict[term] = {'index' : index , 'df' : df , 'idf' : term_idf}
    table.append([index,term,df]) 
    index += 1 

dictionary.write(tabulate(table,headers = ['index','term','df']))
dictionary.close()
print 'dictionary.txt has saved....\n'


#for each doc do tf-idf
for i in range(1,doc_number+1):
    tf_dict = all_tf_dict[str(i)+'.txt']
    #normalize vector
    vector_length = 0
    for term in tf_dict:
        tf_idf = tf_dict[term]*term_dict[term]['idf']
        tf_idf = tf_idf ** 2
        vector_length += tf_idf
    vector_length = math.sqrt(vector_length) 
    file_name = str(i)+'.txt'
    term_count = 0
    table = []
    for term in tf_dict:
        term_count += 1
        tf_idf = tf_dict[term]*term_dict[term]['idf']/vector_length
        table.append([term_dict[term]['index'],tf_idf])
    tf_file = open('result/'+file_name,'w')
    tf_file.write(str(term_count)+'\n')
    tf_file.write(tabulate(table,headers = ['index','tf-idf']))
    tf_file.close() 
    print i,'.txt has saved.....'


