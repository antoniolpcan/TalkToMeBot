from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
from deep_translator import GoogleTranslator
import matplotlib.pyplot as plt
import spacy
import pt_core_news_sm
import pandas as pd
import seaborn as sns
import numpy as np
import re
import random

class Chat():

  def __init__(self, type: str):
    self.type_bot = type
    train_data = pd.read_csv('data/tw_pt.csv',
                         header=None, names=['id', 'message','sentiment'], encoding='latin1')
    train_data=train_data.drop(['id'], axis=1)
    train_data = train_data.drop(0)
    train_data['sentiment'] = train_data['sentiment'].replace({'Positivo': 2, 'Negativo': 0, 'Neutro': 1})
    print(train_data)
    x = train_data.iloc[:,0].values
    y = train_data.iloc[:,1].values
    x,_, y,_ = train_test_split(x,y,test_size=0.97)
    x_treino, x_teste, y_treino, y_teste = train_test_split(x,y,test_size=0.2)
    self.nlp = spacy.load('pt_core_news_sm')
    x_train_cleaned=[self.preprocessing(tweet) for tweet in x_treino]
    self.x_test_cleaned=[self.preprocessing(tweet) for tweet in x_teste]
    self.vectorizer = TfidfVectorizer()
    x_train_tfidf = self.vectorizer.fit_transform(x_train_cleaned)
    x_train_cleaned_lemma = [self.preprocessing_lemma(tweet) for tweet in x_train_cleaned]
    x_train_tfidf = self.vectorizer.fit_transform(x_train_cleaned_lemma)
    x_test_cleanned_lemma = [self.preprocessing_lemma(tweet) for tweet in self.x_test_cleaned]
    x_test_tfidf = self.vectorizer.transform(x_test_cleanned_lemma)
    self.model = tree.DecisionTreeClassifier(criterion='entropy')
    self.model.fit(x_train_tfidf, y_treino)
    self.predictions = self.model.predict(x_test_tfidf)
    accuracy_score(y_teste,self.predictions)
    self.welcome_words_input = ['olá', 'oi', 'eae', "bom dia", "boa tarde", "boa noite"] 
    self.welcome_words_output = self.wellcome_words()

  def get_cleaned_text(self):
    return self.preprocessing(self.article.cleaned_text)

  def preprocessing_lemma(self, sentence):
    tokens=[]
    tokens = [token.lemma_ for token in self.nlp(sentence)]
    tokens = ' '.join(element for element in tokens)
    return tokens

  def translated_phrase(self, phrase):
    try:
        translation = GoogleTranslator(source='auto', target='en').translate(phrase)
        return translation
    except Exception as e:
        print('Erro ao converter frase')
      
  def sentiment_scores(self, sentence):  
    sid_obj = SentimentIntensityAnalyzer() 
    sentiment_dict = sid_obj.polarity_scores(sentence)
    
    if sentiment_dict['compound'] >= 0.05 : 
        #Positivo
        return 2
  
    elif sentiment_dict['compound'] <= - 0.05 : 
        #Negative
        return 0
  
    else : 
        #Neutro
        return 1

  def avaliate(self, sentence):
    self.x_test_cleaned.append(sentence)
    x_test_cleanned_lemma = [self.preprocessing_lemma(tweet) for tweet in self.x_test_cleaned]
    x_test_tfidf = self.vectorizer.transform(x_test_cleanned_lemma)
    predictions = self.model.predict(x_test_tfidf)
    print( 'Valor da matriz ',predictions[-1])
    new_sentence = self.translated_phrase(sentence)
    score = self.sentiment_scores(new_sentence)
    print( 'Valor de score ',score)
    return score
  
  def welcome_message(self, text):
    for word in text.split():
      if word.lower() in self.welcome_words_input: 
        return random.choice(self.welcome_words_output) 

  def preprocessing(self, sentence):
    sentence = re.sub(r'@[A-Za-z0-9]+',' ', sentence)
    sentence = re.sub(r'https?://[A-Za-z0-9./]+',' ',sentence)

    sentence = sentence.replace('.','')
    sentence = sentence.lower()
    tokens = []
    tokens = [token.text for token in self.nlp(sentence) if not (token.is_stop
                                                            or token.like_num
                                                            or token.is_punct
                                                            or token.is_space
                                                            or len(token)==1)]

    tokens = ' '.join([element for element in tokens])

    return tokens

  def answer(self, user_text):
      sentence_humor = self.avaliate(user_text)
      chatbot_answer = self.bot_response(sentence_humor)
      return chatbot_answer

  def wellcome_words(self):
    if self.type_bot == "Felicidade":
      return ["Ótimo dia!", "Olá amigo!", "Que bom te ver!! ops... ler! hehe", "Boas vindas!!"]
    elif self.type_bot == "Ódio":
      return ["Péssimo dia", "...", "#@%@&*$", "Fala logo", "Aff", "Odeio você"]
    else:
      return ["👋🤖", "🤖🤝🙂", "🥰🥰🥰", "🤖👍"]
    
  def bot_response(self, sentence_humor):
    if self.type_bot == "Felicidade":
      if sentence_humor == 0:
        return "Você parece negativo... posso fazer algo pra te ajudar?"
      elif sentence_humor == 1:
        return "Que interessante, mas você parece neutro em sua fala!"
      else:
        return "Vamos lá amigo, quero que mantenha essa positividade!"
    elif self.type_bot == "Ódio":
      if sentence_humor == 0:
        return "ESTÁ TENTANDO DESCONTAR ALGO EM MIM?"
      elif sentence_humor == 1:
        return "FALE ALGO ÚTIL, NÃO QUERO MENSAGENS NEUTRAS"
      else:
        return "SUA FELICIDADE ME IRRITA!"
    else:
      if sentence_humor == 0:
        return "😟😟😟😟"
      elif sentence_humor == 1:
        return "👍👍👍👍👍"
      else:
        return "😀😀😀😀"
