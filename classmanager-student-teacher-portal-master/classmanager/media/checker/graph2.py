import spacy
nlp = spacy.load('en_core_web_sm')
from spacy.matcher import Matcher 
from media.checker.sentencesplitting import *

def graph(list1, list2):
  entities_student = sentmaker(list1)
  # relations_student = relmaker(list1)
  entities_teacher = sentmaker(list2)
  # relations_teacher = relmaker(list2)
  print(entities_student)
  print(entities_teacher)
  return len(list(set(entities_student) & set(entities_teacher)))/len(entities_teacher) #+ len(list(set(relations_student) & set(relations_teacher)))

def get_entities(sent):
  ent1 = ""
  ent2 = ""
  
  prv_tok_dep = ""    # dependency tag of previous token in the sentence
  prv_tok_text = ""   # previous token in the sentence

  prefix = ""
  modifier = ""
  for tok in nlp(sent):
    if tok.dep_ != "punct": # if token is a punctuation mark then move on to the next token
      if tok.dep_ == "compound":  # check: token is a compound word or not
        prefix = tok.text
        if prv_tok_dep == "compound": # if the previous word was also a 'compound' then add the current word to it
          prefix = prv_tok_text + " "+ tok.text
      
      if tok.dep_.endswith("mod") == True:  # check: token is a modifier or not
        modifier = tok.text
        if prv_tok_dep == "compound": # if the previous word was also a 'compound' then add the current word to it
          modifier = prv_tok_text + " "+ tok.text
      
      if tok.dep_.find("subj") == True:
        ent1 = modifier +" "+ prefix + " "+ tok.text
        prefix = ""
        modifier = ""
        prv_tok_dep = ""
        prv_tok_text = ""      

      if tok.dep_.find("obj") == True:
        ent2 = modifier +" "+ prefix +" "+ tok.text
     
      prv_tok_dep = tok.dep_
      prv_tok_text = tok.text
  
  return [ent1.strip(), ent2.strip()]
  
def get_relation(sent):
  doc = nlp(sent)
  matcher = Matcher(nlp.vocab)
  pattern = [{'DEP':'ROOT'}, 
            {'DEP':'prep','OP':"?"},
            {'DEP':'agent','OP':"?"},  
            {'POS':'ADJ','OP':"?"}] 

  matcher.add("matching_1", [pattern]) 
  matches = matcher(doc)
  k = len(matches) - 1
  span = doc[matches[k][0]:matches[k][1]] 
  return(span.text)

def sentmaker(list):
  text = sensplit(list)
  entities_arr=[]
  for sent in text:
    for ent in get_entities(sent):
      entities_arr.append(ent)
  return entities_arr    

def relmaker(list): 
  relations_arr=[]
  for sent in list:
    relations_arr.append(get_relation(sent)) 
  return relations_arr    

