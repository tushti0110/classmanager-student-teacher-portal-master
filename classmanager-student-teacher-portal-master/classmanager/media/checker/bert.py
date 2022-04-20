from numpy import vectorize
from scipy import spatial
from sent2vec.vectorizer import Vectorizer

def callbert(list):
    vectorizer = Vectorizer()
    vectorizer.bert(list)
    vectors_bert = vectorizer.vectors
    
    dist_1 = spatial.distance.cosine(vectors_bert[0], vectors_bert[1])
    return 1 - dist_1