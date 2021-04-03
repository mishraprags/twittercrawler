#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pymongo
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.snowball import SnowballStemmer
from sklearn.metrics import jaccard_score
from bson import json_util
import numpy as np
import pandas as pd
import requests
import string
import tweepy
import emoji
import nltk
import json
import time
import sys
import re

consumer_key = ""
consumer_secret =""
access_token =""
access_token_secret =""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

if (not api):
    print('Can\'t authenticate')
    print('failed cosumeer id ----------: ', consumer_key )
else:
    print('Sucessfully authenticated the keys') #remove before submitting
    
client = pymongo.MongoClient("mongodb://localhost:27017/")
dbName = "TwitterCrawlerAE"
db = client[dbName]
collName = 'tweetNew'
collection = db[collName]

def qualityCheck(tweet):
    user = tweet['user']
    if user['verified']:
        weight = 1.5
    else:
        weight = 1.0
    
    verifiedWeight = weight/1.5

    followersCount = user['followers_count']

    if followersCount < 50:
        weight = 0.5
    elif followersCount < 5000:
        weight = 1.0
    elif followersCount < 10000:
        weight = 1.5
    elif followersCount < 100000:
        weight = 2.0
    elif followersCount < 200000:
        weight = 2.5
    elif followersCount > 200000:
        weight = 3.0

    followersWeight= weight/3


    weight =1
    if(user['default_profile_image']):
        weight =0.5
    profileWeight = weight
    today = datetime.now()
    s = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    daysSince = (today - s).total_seconds()/60/60/24

    if daysSince < 1:
        weight = 0.05
    elif daysSince < 30:
        weight = 0.10
    elif daysSince < 90:
        weight = 0.25
    elif daysSince > 90:
        weight = 1.0
    accountAgeWeight = weight
    
    
    qualityScore = (profileWeight + verifiedWeight + followersWeight + accountAgeWeight)/4
    return qualityScore


def cleanTweets(tweet_message):
    tweet_message = re.sub(emoji.get_emoji_regexp(), r"", tweet_message)
    tweet_message = re.sub(r'\&\w*;', '', tweet_message)
    tweet_message = re.sub('@[^\s]+','',tweet_message)
    tweet_message = re.sub(r'\$\w*', '', tweet_message)
    tweet_message = tweet_message.lower()
    tweet_message = re.sub(r'https?:\/\/.*\/\w*', '', tweet_message)
    tweet_message = re.sub(r'#\w*', '', tweet_message)
    tweet_message = re.sub(r'\b\w{1,2}\b', '', tweet_message)
    tweet_message = re.sub(r'\s\s+', ' ', tweet_message)
    tweet_message = tweet_message.lstrip(' ') 
    tweet_message = ''.join(c for c in tweet_message if c <= '\uFFFF') 
    tweet_message.encode("ascii", errors="ignore").decode()

    return tweet_message

def processTweets(tweet):
    placeName = None
    placeCountry = None
    placeCountrycode = None
    placeCoordinates = None
    geoEnabled = None
    coordinates = None
    location = None
    hashtagsList = None
    mentionsList = None
    source = None
    quoted = None
    mediaList = None
    try:
        created = tweet['created_at']
        tweet_id = tweet['id_str']
        username = tweet['user']['screen_name']
        message = tweet['text']
        entities = tweet['entities']
        mentions = entities['user_mentions']
        mentionsList = []
        
        for m in mentions:
            mentionsList.append(m['screen_name'])
            
        hashtags = entities['hashtags']
        hashtagsList = []
        
        for h in hashtags:
            hashtagsList.append(h['text'])
            
        source = tweet['source']
        exactCoordinates = tweet['coordinates']
        
        if(exactCoordinates):
            coordinates = exactCoordinates['coordinates']
            
        geoEnabled = tweet['user']['geo_enabled']
        location = tweet['user']['location']
            
        quoted = tweet['is_quote_status']
        retweeted = tweet['retweeted']
        
        media = tweet['extended_entities']['media']
        mediaList = []
        
        for m in media:
            mediaList.append(m['media_url'])
            
        
    except Exception as e:
        print(e)
       
    try:
        if(tweet['truncated'] == True):
            message = tweet['extended_tweet']['full_text']
            
        elif(message.startswith('RT') == True):
            if(tweet['retweeted_status']['truncated'] == True):
                message = tweet['retweeted_status']['extended_tweet']['full_text']
            else:
                message = tweet['retweeted_status']['full_text']
                
    except Exception as e:
        pass
            
    if((geoEnabled) and (message.startswith('RT') == False)):
        try:
            if(tweet['place']):
                placeName = tweet['place']['full_name']
                placeCountry = tweet['place']['country']
                placeCountryCode = tweet['place']['country_code']
                placeCoordinates = tweet['place']['bounding_box']['coordinates']
                
        except Exception as e:
            print(e)
            
    mediaList = False
    photoCount = 0
    videoCount = 0
    gifCount = 0
    if 'extended_entities' in tweet:
        extendedEntities = tweet['extended_entities']
        if ('media' in extendedEntities):
            mediaList = []
            for x in extendedEntities['media']:
                mediaList.append(x['media_url'])
                if x['type'] == 'video':
                    videoCount += 1
                elif x['type'] == 'photo':
                    photoCount += 1
                elif x['type'] == 'animated_gif':
                    gifCount += 1
                    
    score = qualityCheck(tweet)
    
    redundant = False
    
    if score < 0.5:
        redundant = True
        
    tweet_message = cleanTweets(message)
    
    tweet_json = {'_id' : tweet_id, 'date': created, 'username': username,  'text' : tweet_message,  'geoenabled' : geoEnabled,  'coordinates' : coordinates,  'location' : location,  'place_name' : placeName, 'place_country' : placeCountry, 'country_code': placeCountrycode,  'place_coordinates' : placeCoordinates, 'hashtags' : hashtagsList, 'mentions' : mentionsList, 'source' : source, 'retweet' : retweeted, 'quoteTweet' : quoted, 'media' : mediaList, 'photoCount': photoCount, 'videoCount': videoCount, 'gifCount': gifCount, 'redundant': redundant}    
    
    return tweet_json
    
class streamListener(tweepy.StreamListener):
    
    global geoEnabled
    global geoDisabled
    
    def on_connect(self):
        print("You are connected to the API")
        
    def on_error(self, status_code):
        print('An Error has occured: ' + repr(status_code))
        return False

    def on_data(self, data):
        t = json.loads(data)
        tweet = processTweets(t)
        try:
            collection.insert_one(tweet)
        except Exception as e:
            print(e)
                
Loc_UK = [-10.392627, 49.681847, 1.055039, 61.122019] # UK and Ireland

places = api.geo_search(query="UK", granularity="country")

place_id = places[0].id

Words_UK =["Boris", "Prime Minister", "Tories", "UK", "London", "England", "Manchester", "Sheffield", "York", "Southampton",  "Wales", "Cardiff", "Swansea" ,"Banff", "Bristol", "Oxford", "Birmingham" ,"Scotland", "Glasgow", "Edinburgh", "Dundee", "Aberdeen", "Highlands" "Inverness", "Perth", "St Andrews", "Dumfries", "Ayr" "Ireland", "Dublin", "Cork", "Limerick", "Galway", "Belfast"," Derry", "Armagh" "BoJo", "Labour", "Liberal Democrats", "SNP", "Conservatives", "First Minister", "Surgeon", "Chancelor" "Boris Johnson", "BoJo", "Keith Stramer"]

listener = streamListener(api=tweepy.API(wait_on_rate_limit=True))
streamer = tweepy.Stream(auth=auth, listener=listener)
streamer.filter(locations= Loc_UK, track = Words_UK, languages = ['en'], is_async=True)

Place =  'London'
Lat   =  '51.450798'
Long  =  '-0.137842'
geoTerm = Lat+','+Long+','+'10km'

last_id =  None
counter =0
sinceID = None
results = True

while results:
    if (counter < 360 ):
        try:
            
            results = api.search(q = "place:%s" % place_id, count=100, lang="en", tweet_mode='extended', max_id=last_id)
            
        except Exception as e:
            print(e)
            
        counter += 1
        
    else:
        
        time.sleep(15*60)


# In[ ]:




