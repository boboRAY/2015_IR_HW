import math
#get value from docID.txt and calculate its unit vector
def get_value(doc_id):
    dict = {}
    with open('result/'+str(doc_id)+'.txt') as f:
        #read line begin from line3 (because first 3 lines are headers)
        for i in xrange(3):
            f.next()
        for line in f:
            list = line.split()
            dict[list[0]] = float(list[1]) #dict of {index : vector value}
    return dict


def cosine(docid_x , docid_y):
    inner_product_sum = 0
    dict_x = get_value(docid_x)
    dict_y = get_value(docid_y)
    for index,vector in dict_x.iteritems():
        #if doc_y also has term with index, than multiple them
        if index in dict_y:
            inner_product_sum += vector * dict_y[index]
    print 'cosine value is :',inner_product_sum

            
docid_x = raw_input('please input doc id of x : ')
docid_y = raw_input('please input doc id of y : ')
cosine(docid_x,docid_y)
