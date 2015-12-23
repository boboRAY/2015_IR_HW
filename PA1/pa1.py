from lib.porterStemmer import PorterStemmer


# read raw data 
f = open('28.txt')
raw_str = f.read()

# remove special character
raw_str = raw_str.replace("'",'').replace('.','').replace(',','')

# read stop word
f_stopwords = open('stop_words.txt')
raw_stopwords = f_stopwords.read()
stopwords = raw_stopwords.lower().splitlines()


# lowercase
raw_str = raw_str.lower()

#tokenize
tokens = raw_str.split()

#stemming
stemmer = PorterStemmer()
for n,token in enumerate(tokens):
    new_token = stemmer.stem(token,0,len(token)-1)
    tokens[n] = new_token    
    
# stemming for stop word
# remove stop word from tokens
for n,stopword in enumerate(stopwords):
    new_stopword = stemmer.stem(stopword,0,len(stopword)-1)
    while new_stopword in tokens:
        tokens.remove(new_stopword)
'''
#save result as txt file
result = open('result.txt','w')
for  token in tokens:
    result.write(token+'\n')
result.close()
'''
