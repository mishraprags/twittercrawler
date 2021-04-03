#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.snowball import SnowballStemmer
from sklearn.metrics import jaccard_score
from sklearn.cluster import KMeans
from textblob import TextBlob
import nltk
import string
import numpy as np

df = pd.read_json (r'C:\Users\hp\Google Drive\University of Glasgow\Level 3\Web Science\Coursework\tweet.json')

df_quoted = (df.groupby("quoted"))

print("Total number of Tweets : ")

print(len(df))

print("Number of Quoted Tweets : ")

print(df_quoted.size())

df_retweeted = df.groupby("retweeted")

print("Number of Retweeted Tweets : ")

print(df_retweeted.size())


# In[2]:


tweetText = np.array(df['text'])
stopWords = nltk.corpus.stopwords.words('english')


# In[3]:


def tokenize(tweet):
    tweetTokenized = [char for char in list(tweet) if char not in string.punctuation]
    tweetTokenized = ''.join(tweetTokenized)
    tweetFinal = [word for word in tweetTokenized.lower().split() if word.lower() not in stopWords]
    stemmer = SnowballStemmer("english")
    tweetFinal = ([stemmer.stem(t) for t in tweetFinal])
    tweetFinal = ' '.join(tweetFinal)
    return tweetFinal

for i in tweetText:
    tokenize(i)
    
tfidf_vectorizer = TfidfVectorizer()
tfidf_vectorizer.fit(tweetText)
tfidf_matrix = tfidf_vectorizer.fit_transform(tweetText)


# In[4]:


distortion = []
K = range(1, 10)

for k in K:
    kmeans = KMeans(n_clusters=k, max_iter=200, n_init=10)
    kmeans = kmeans.fit(tfidf_matrix)
    distortion.append(kmeans.inertia_)


# In[5]:


plt.plot(K, distortion, 'bx-')
plt.xlabel('k')
plt.ylabel('Distortion')
plt.title('Elbow Method For Optimal k')
plt.show()


# In[6]:


finalK = 8
model = KMeans(n_clusters=finalK, init='k-means++', max_iter=200, n_init=10)
model.fit(tfidf_matrix)
labels=model.labels_
tweetClusters=pd.DataFrame(list(zip(df['text'],labels)),columns=['title','cluster'])
print(tweetClusters.sort_values(by=['cluster']))


# In[7]:


from wordcloud import WordCloud
result={'cluster':labels,'tweets':df['text']}
result=pd.DataFrame(result)
for k in range(0,finalK):
    s=result[result.cluster==k]
    text=s['tweets'].str.cat(sep=' ')
    text=text.lower()
    text=' '.join([word for word in text.split()])
    wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(text)
    titles=tweetClusters[tweetClusters.cluster==k]['title']         
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()


# In[9]:


f = open("keywords.txt", "w")
f.write(" ".join(list(wordcloud.words_.keys())))
f.close()


# In[ ]:




