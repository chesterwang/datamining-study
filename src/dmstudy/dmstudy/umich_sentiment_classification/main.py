#coding:utf8

import pandas as pd
import numpy as np 
import re,nltk
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.porter import PorterStemmer
from sklearn.cross_validation import train_test_split    
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

#import urllib

#test_file = "/home/chester/Downloads/testdata.txt"
#train_file = "/home/chester/Downloads/training.txt"

test_file = "/home/data/testdata.txt"
train_file = "/home/data/training.txt"

#由于需要登陆账号,此处代码作废
#train_df = urllib.urlretrieve("https://inclass.kaggle.com/c/si650winter11/download/training.txt","/tmp/training")
#test_df = urllib.urlretrieve("https://inclass.kaggle.com/c/si650winter11/download/testdata.txt","/tmp/test")


test_data_df = pd.read_csv(test_file,header=None,delimiter="\t",quoting=3)
test_data_df.columns = ["text"]
train_data_df = pd.read_csv(train_file,header=None,delimiter="\t",quoting=3)
train_data_df.columns = ["sentiment","text"]
train_data_df.sentiment.value_counts()
np.mean([len(s.split(" ")) for s in train_data_df.text])


stemmer = PorterStemmer()
def stem_tokens(tokens,stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def tokenize(text):
    text = re.sub("[^a-zA-Z]"," ",text)
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens,stemmer)
    return stems

vectorizer = CountVectorizer(
    analyzer = 'word',
    tokenizer = tokenize,
    lowercase = True,
    max_features = 85)

    #stop_words = 'english',


corpus_data_features = vectorizer.fit_transform(
    train_data_df.text.tolist() + test_data_df.text.tolist())

corpus_data_features_nd = corpus_data_features.toarray()
print corpus_data_features_nd.shape
vocab = vectorizer.get_feature_names()
print vocab

dist = np.sum(corpus_data_features_nd, axis=0)
print dist

for tag, count in zip(vocab, dist):
    print count, tag

X_train, X_test, y_train, y_test  = train_test_split(
        corpus_data_features_nd[0:len(train_data_df)], 
        train_data_df.Sentiment,
        train_size=0.85, 
        random_state=1234)

log_model = LogisticRegression()
log_model = log_model.fit(X=X_train, y=y_train)
y_pred = log_model.predict(X_test)

print(classification_report(y_test, y_pred))
