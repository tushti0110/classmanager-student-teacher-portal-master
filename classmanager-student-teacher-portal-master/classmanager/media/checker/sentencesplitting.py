from nltk import tokenize
from nltk.tokenize import sent_tokenize
import nltk

nltk.download('punkt')

def sensplit(doctext):
    return tokenize.sent_tokenize(doctext)
