import yake

def keywordextract(doctext1,doctext2):
    language = "en"
    max_ngram_size = 10
    numOfKeywords = 20
    custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, top=numOfKeywords, features=None)
    keywords1 = custom_kw_extractor.extract_keywords(doctext1)
    keywords2 = custom_kw_extractor.extract_keywords(doctext2)
    
    return len(keywords1)/len(keywords2)