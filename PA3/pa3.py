from lib.porterStemmer import PorterStemmer
import re
import collections
import math
from tabulate import tabulate
from sets import Set
import operator

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

#read training data doc_id to dictionary
f_training = open('training.txt')
train = f_training.read().splitlines()
trainid_dict = {}

for tclass in train:
    clist = tclass.split()
    cid = clist[0]
    clist.pop(0)#remove class id 
    trainid_dict[cid] =  clist

    
#stemming for stopword
for n,stopword in enumerate(raw_stopwords):
    new_stopword = stemmer.stem(stopword,0,len(stopword)-1)
    stopwords.append(new_stopword)

trainv_dict = {}

def get_stem_voc(doc_id):
    f = open('data/'+str(doc_id)+'.txt')
    raw_str = f.read()

    # lowercase
    raw_str = raw_str.lower()

    # delete non-letters
    regex = re.compile('[^a-zA-Z]')
    raw_str = regex.sub(' ',raw_str)
	
    #tokenize
    tokens = raw_str.split()

    #stemming
    stemmer = PorterStemmer()
    vdict = {} 
    for token in list(tokens):
        #stemming for token
        stemmed_token = stemmer.stem(token,0,len(token)-1)
        if stemmed_token not in stopwords and len(stemmed_token)>1:
            if stemmed_token in vdict:
                vdict[stemmed_token]+=1
            else: 
                vdict[stemmed_token]=1
    return vdict


doc_term_dict = {}

print "pre processing"
#read vocbabulary from training data
def read_voc(doc_id,class_id):
    vdict = get_stem_voc(doc_id) 
    doc_term_dict[doc_id] = vdict
    for v in vdict:
        if v in trainv_dict:
            vlist = trainv_dict[v]
            vlist[class_id] += 1
        else:
            vlist = [0]*14
            vlist[class_id]=1
        trainv_dict[v] = vlist

   
#training
#1.set up vocabulary and tf in class
l_ratio_dict = {} #{ class_id : { term : l_ration}}
for class_id in range(1,14): 
    l_ratio_dict[class_id] = {}
    class_list = trainid_dict[str(class_id)]
    for tid in class_list:
        read_voc(tid,int(class_id))

#feature selection : LLR
for term in trainv_dict:
    
    tf_list = trainv_dict[term]
    for cid in range(1,14):
        n11 = float(tf_list[cid])
        n01 = float(15-n11)
        n10 = float(sum(tf_list)-n11)
        n00 = float(195-15-n10)
        N = 195
        h11 = math.log(((n11+n01)/N)**n11)
        h12 = math.log((1-(n11+n01)/N)**n10)
        h13 = math.log(((n11+n01)/N)**n01)
        h14 = math.log((1-(n11+n01)/N)**n00)
        h21 = math.log((n11/(n11+n10))**n11)
        h22 = math.log((1-n11/(n11+n10))**n10)
        h23 = math.log((n01/(n01+n00))**n01)
        h24 = math.log((1-(n01/(n01+n00)))**n00)
        h1 = h11+h12+h13+h14
        h2 = h21+h22+h23+h24
        l_ratio = -2*(h1-h2)
        l_ratio_dict[cid][term] = l_ratio
        
        
fscount = 0
cround = 0
chances = [39]*13
feature_set = Set([])
print "selecting features"
while fscount < 500:
    if sum(chances) == 0:
        chances = [5]*13
    cround = (cround + 1) %13 +1
    feature = max(l_ratio_dict[cround].iteritems(), key=operator.itemgetter(1))[0]
    l_ratio_dict[cround][feature] = -100000 #set it to an min value
    while feature in feature_set and chances[cround] != 0:
        chances[cround-1] = chances[cround-1] -1
        feature = max(l_ratio_dict[cround].iteritems(), key=operator.itemgetter(1))[0]
        l_ratio_dict[cround][feature] = -100000 #set it to an min value
    if chances[cround-1] != 0:
        feature_set.add(feature)
        fscount += 1


print "training"
#training
trainid_list = []
for key,value in trainid_dict.iteritems():
    trainid_list += value



score_dict = {}
for feature in feature_set:
    score_dict[feature]={}
for cid in trainid_dict:
    for tid in trainid_dict[cid]:
        vdict = doc_term_dict[tid]
        total_tf = 0
        for feature in feature_set:
            if feature in vdict:
                total_tf += vdict[feature]
        total_tf += 500
        for feature in feature_set:
            value = 1.0
            if feature in vdict:
                value = value+vdict[feature]
            score = float(value)/float(total_tf)
            score_dict[feature][int(cid)] = score 

print "testing"
#testing
table = []
for doc_id in range(1,1096):
    if str(doc_id) not in trainid_list:
        vdict = get_stem_voc(doc_id)
        score_list = [0]*14
        score_list[0] = -100000
        for cid in range(1,14):
            score = 0.0
            for feature in feature_set:
                if feature in vdict:
                    for i in range(0,vdict[feature]):
                        score += math.log(score_dict[feature][cid])
            score_list[cid] = score
        result = score_list.index(max(score_list))
        table.append([doc_id , result])

print "saving output.txt"
output_f = open('output.txt','w')
output_f.write(tabulate(table,headers = ['doc_id','class_id']))
output_f.close()

