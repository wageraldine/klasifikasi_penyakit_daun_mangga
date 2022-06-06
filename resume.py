# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 09:19:53 2021

@author: W A Geraldine
"""
#Import library
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from pdf2image import convert_from_path    

from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from sklearn.preprocessing import LabelEncoder

import re
import nltk 

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from string import punctuation

import spacy
nlp = spacy.load('en_core_web_sm')

    
#we are loading the model using pickle
def convert_pdf_to_text(path):
    pages = convert_from_path(pdf_path=path, dpi=200)
    num_pages = 0
    extractedInformation = ''
    #Saving pages in jpeg format
    for page in pages:
        page.save('static/files/resume_'+str(num_pages)+'.jpg', 'JPEG')
        
        image_path = ('static/files/resume_'+str(num_pages)+'.jpg')
        text = pytesseract.image_to_string(Image.open(image_path))
        extractedInformation += text
        num_pages += 1

    return extractedInformation

def resume_classification(path):
    tfidfconverter = TfidfVectorizer(max_features=20000, min_df=5, max_df=0.7, stop_words=stopwords.words('english'),ngram_range=(1,3))
    le = LabelEncoder()
    
    filename = 'resume_classification_model.sav'
    loaded_model = loaded_model = pickle.load(open(filename, 'rb'))
    
    text = convert_pdf_to_text(path)
    
    vec_path = 'vectorizer.pickle'
    tfidf_file = open(vec_path, 'rb')
    tfidfconverter = pickle.load(tfidf_file)
    tfidf_file.close()
    
    text_vector = tfidfconverter.transform([text]).toarray()
    pred_text = loaded_model.predict(text_vector)
    
    
    pkl_file = open('encoder.pkl', 'rb')
    le = pickle.load(pkl_file) 
    pkl_file.close()
    
    pred_text = le.inverse_transform(pred_text)
    score = round(max(loaded_model.predict_proba(text_vector)[0])*100,2)
    result = str(pred_text[0].capitalize())
    
    return text, result, score

def similar_check(vacancy, doc2):
    image_path = (vacancy)
    doc1 = pytesseract.image_to_string(Image.open(image_path))
    
    stop_words = set(stopwords.words("english"))
    
    doc1 = nlp(doc1)
    tokens = [token.text for token in doc1]
    word_frequencies = {}
 
    for word in doc1:
        if word.text.lower() not in stop_words:
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1

    lemmatizer = WordNetLemmatizer()

    doc1 = list(word_frequencies.keys())
    doc1 = [lemmatizer.lemmatize(word, pos='a') for word in doc1]
    doc1 = [lemmatizer.lemmatize(word, pos='v') for word in doc1]
    doc1 = [lemmatizer.lemmatize(word, pos='n') for word in doc1]
    
    def listToString(s): 
        # initialize an empty string
        str1 = "" 
        # traverse in the string  
        for ele in s: 
            str1 += " "+ele  
        # return string  
        return str1

    doc1 = listToString(doc1)
    
    processed_tweet = re.sub(r'\W', ' ', doc1)
    # Hapus semua single characters
    processed_tweet = re.sub(r'\s+[a-zA-Z]\s+', ' ', processed_tweet)
    # Hapus single characters dari awal
    processed_tweet = re.sub(r'\^[a-zA-Z]\s+', ' ', processed_tweet) 
    # Substitusi multiple spaces dengan single space
    processed_tweet= re.sub(r'\s+', ' ', processed_tweet, flags=re.I)
    # Hapus prefixed 'b'
    processed_tweet = re.sub(r'^b\s+', '', processed_tweet)
    
    processed_tweet = re.sub(r'\d', '', processed_tweet)
    # Ubah menjadi Lowercase
    processed_tweet1 = processed_tweet.lower()
    
    doc2 = nlp(doc2)
    tokens = [token.text for token in doc2]
    print(tokens)
    
    word_frequencies2 = {}

    # Mengisi word_frequencies tanpa stopword dan karakter khusus
    for word in doc2:
        if word.text.lower() not in stop_words:
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies2.keys():
                    word_frequencies2[word.text] = 1
                else:
                    word_frequencies2[word.text] += 1
                    
    doc2 = list(word_frequencies2.keys())
    doc2 = [lemmatizer.lemmatize(word, pos='a') for word in doc2]
    doc2 = [lemmatizer.lemmatize(word, pos='v') for word in doc2]
    doc2 = [lemmatizer.lemmatize(word, pos='n') for word in doc2]

    doc2 = listToString(doc2) 
    
    processed_tweet = re.sub(r'\W', ' ', doc2)
    # Hapus semua single characters
    processed_tweet = re.sub(r'\s+[a-zA-Z]\s+', ' ', processed_tweet)
    # Hapus single characters dari awal
    processed_tweet = re.sub(r'\^[a-zA-Z]\s+', ' ', processed_tweet) 
    # Substitusi multiple spaces dengan single space
    processed_tweet= re.sub(r'\s+', ' ', processed_tweet, flags=re.I)
    # Hapus prefixed 'b'
    processed_tweet = re.sub(r'^b\s+', '', processed_tweet)
    
    processed_tweet = re.sub(r'\d', '', processed_tweet)
    
    # Ubah menjadi Lowercase
    processed_tweet2 = processed_tweet.lower()
    
    # tokenization
    X_list = word_tokenize(processed_tweet1) 
    Y_list = word_tokenize(processed_tweet2)
      
    # sw contains the list of stopwords
    sw = stopwords.words('english') 
    l1 =[];l2 =[]
      
    # remove stop words from the string
    X_set = {w for w in X_list if not w in sw} 
    Y_set = {w for w in Y_list if not w in sw}
      
    # form a set containing keywords of both strings 
    rvector = X_set.union(Y_set) 
    for w in rvector:
        if w in X_set: l1.append(1) # create a vector
        else: l1.append(0)
        if w in Y_set: l2.append(1)
        else: l2.append(0)
    c = 0
      
    # cosine formula 
    for i in range(len(rvector)):
            c+= l1[i]*l2[i]
    score = round(c / float((sum(l1)*sum(l2))**0.5)*100, 2)
    
    return score
