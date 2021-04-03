#!/usr/bin/env python
# coding: utf-8

# In[14]:


from imports import *

import tweepy

import pymongo

import json

import datetime

consumer_key = "ChyGP4dic6FAfH9upbzqLKSW2"
consumer_secret ="nrmTO1tjLsGqwW5PpMwib4Ow35VV5XZJQ0CoKr90ioX9hT4K0M"
access_token ="1350297625388490758-dzWxd9Ee48B9NwoNfeicqA0lpJ4btk"
access_token_secret ="56r4UfE5yWieTylTCfFqVCqO7zOySjDVuBzuxftTPYtrl"
 
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

client = pymongo.MongoClient('mongodb://localhost:27017/')
dbName = "TwitterCrawlerAE"
db = client[dbName]
collName = 'tweetNew'
collection = db[collName]

def getMostRetweetedNames(collectionName): #Returns 15 most retweeted users
    
    """Returns most retweeted tweets"""
    
    cursor = db[collectionName+"_filtered"].find({"user.verified":True, "retweet_count":{"$gt":1000}}).sort([('retweet_count',-1)]).limit(15)
    
    cursor = [items["user"]["screen_name"] for items in cursor]

    return cursor



def getMostLiked(collectionName): #Returns most liked tweet
    """ Returns most liked tweets """
    
    cursor = db[collectionName].find().sort([('favorite_count',-1)]).limit(1)

    cursor = list(cursor)
    
    return cursor[0]



def REST_keyword_search(keywords,buf,api):

    until = datetime.date.today()

    since = until - datetime.timedelta(days=7)

    print("Searching for tweets with the given keywords...")

    for i in range(len(keywords)):

        count = 0

        for status in tweepy.Cursor(api.search,q=keywords[i], lang="en",since=since.strftime("%Y-%m-%d"), until=until.strftime("%Y-%m-%d")).items(200):

            buffer.append(status._json)

            count+=1

        buf+=buffer

        print("Finished searching for: "+keywords[i]+".")



    print("Search complete.")


def REST_users_search(top_users,buf,api):

    print("Searching for tweets from the given usernames...")

    for i in range(len(top_users)):

        buffer = []

        for status in Cursor(api.user_timeline, screen_name=top_users[i], count="200").items(200):

            buffer.append(status._json)

        buf+=buffer

        print("Tweets from @"+top_users[i]+" is complete.")



    print("Search complete.")



#From the filtered tweets, it would seem that the topics are mainly:
 
f = open("keywords.txt", "r")

keywords = (f.read().split(" "))


#As for the power users, it can be obtained by:

topUsers = getMostRetweetedNames("tweets")

buffer = []

REST_keyword_search(keywords,buffer,api)



REST_users_search(topUsers,buffer,api)



print("Saving to file: rest_api.json...")

with open("rest_api.json","w", encoding="utf-8") as f:

    json.dump(buffer,f,indent=4)

    print("Save complete.")



def getCollection(collectionName): #Returns collection

    try:

        collection = db[collectionName]

    except Exception as e:

        print(e)

    return collection


# In[ ]:




