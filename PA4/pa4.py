from lib.porterStemmer import PorterStemmer
import re
import collections
import math
import heapq
from pqdict import pqdict

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
            if stemmed_token not in stopwords and len(stemmed_token)>2:
                #save it to tf_dict 
                tf_dict[stemmed_token] = 1
                if stemmed_token in raw_term_dict:
                    #if it existed in raw_term_dict, increase it's df 
                    raw_term_dict[stemmed_token]+=1
                else:
                    raw_term_dict[stemmed_token]=1
    all_tf_dict[file_name] = tf_dict #save tf_dict to all_tf_dict
                
#read all 1095 source file
print 'read file....\n'
for i in range(1,doc_number+1):
    make_dictionary(str(i)+'.txt')

#sort dictionary
print 'making dictionary '
for term in raw_term_dict:
    df = raw_term_dict[term]
    term_idf = math.log10(float(doc_number)/float(df))
    term_dict[term] = {'df' : df , 'idf' : term_idf}

doc_tfidf_dict = {}
#cosine similarity
def cosine(docid_x , docid_y):
    inner_product_sum = 0
    dict_x = doc_tfidf_dict[docid_x]
    dict_y = doc_tfidf_dict[docid_y]

    for index,vector in dict_x.iteritems():
        #if doc_y also has term with index, than multiple them
        if index in dict_y:
            inner_product_sum += vector * dict_y[index]
    return inner_product_sum

print 'count tfidf'
#for each doc do tf-idf
print 'do tf-idf'
for i in range(1,doc_number+1):
    tf_dict = all_tf_dict[str(i)+'.txt']
    #normalize vector
    vector_length = 0
    for term in tf_dict:
        tf_idf = tf_dict[term]*term_dict[term]['idf']
        tf_idf = tf_idf ** 2
        vector_length += tf_idf
    vector_length = math.sqrt(vector_length) 
    tfidf_dict = {}
    for term in tf_dict:
        tf_idf = tf_dict[term]*term_dict[term]['idf']/vector_length
        tfidf_dict[term] = tf_idf
    doc_tfidf_dict[i] = tfidf_dict

P = {}
print 'save similarity'
for i in range(1,1096):
    pq = pqdict({},reverse = True) 
    for j in range(1,1096):
        if i != j:
            pq[j]=cosine(i,j)
    P[i] = pq 

I = [1]*1096
A = [[]]
for i in range(1,1096):
    A.append([i])
#print result
def print_result(k):
    k = 1095-k
    f = open(str(k)+".txt","w")
    for vlist in A:
        if len(vlist) > 0:
            for t in sorted(vlist):
                f.write(str(t))
                f.write("\n")
            f.write("\n")
    f.close()
    print str(k)+".txt has saved"
            

print "clustering"
for k in range(1,1095):
    k2 = 0
    k1 = 0
    maxm = 0
    for m in range(1,1096):
        if I[m] != 0 and maxm < P[m].values()[0]:
            maxm = P[m].values()[0]
            k1 = m 
            k2 =  P[m].keys()[0]
    A[k1] = A[k1]+A[k2]
    A[k2] = []
    print k1,k2
    P[k1].pop(k2)
    I[k2] = 0
    for i in range(1,1096):
        if I[i] == 1 and i != k1:
            pq = P[i]
            newscore = min(pq.pop(k1),pq.pop(k2))
            pq[k1] = newscore
            P[i] = pq
    if k == 1095-8 or k == 1095-13 or k == 1095-20:
        print_result(k)
