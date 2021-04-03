import tweepy
import json
from pymongo import MongoClient
from datetime import datetime
import time
import sys
import numpy
import emoji
import re

df_stream = pd.read_json (r'C:\Users\hp\Google Drive\University of Glasgow\Level 3\Web Science\Coursework\tweetNew.json')
df_rest = pd.read_json (r'C:\Users\hp\Google Drive\University of Glasgow\Level 3\Web Science\Coursework\tweetNew.json')

images = 0
videos = 0
gifs = 0
retweets = 0
quotes = 0
geoenabled = 0
coords = 0
twitter_place = 0
generic_location = 0
redundant = 0
verified = 0

for x in df_stream.index:
    images += df["photoCount"][x]
    videos += df["videoCount"][x]
    gifs += df["gifCount"][x]
    
    if df["retweet"][x] == True:
        retweets += 1

    if df["quoteTweet"][x] == True:
        quotes += 1

    if df["redundant"][x] == True:
        redundant += 1

    if df["geoenabled"][x] == True:
        geoenabled += 1

    if df["verified"][x] == True:
        verified += 1

    if df["coordinates"][x] != None:
        coords += 1
        
    elif df["place_name"][x] != None:
        twitter_place += 1
        
    elif df["location"][x] != None:
        generic_location += 1
        
print("Analysis result from Stream Crawler")
print("images - " + str(images))
print("videos - " + str(videos))
print("gifs - " + str(gifs))
print("verified - " + str(verified))
print("retweets - " + str(retweets))
print("quotes - " + str(quotes))
print("redundant - " + str(redundant))
print("geoenabled - " + str(geoenabled))
print("coordinates - " + str(coords))
print("place objects - " + str(twitter_place))
print("Generic - " + str(generic_location))

images = 0
videos = 0
gifs = 0
retweets = 0
quotes = 0
geoenabled = 0
coords = 0
twitter_place = 0
generic_location = 0
redundant = 0
verified = 0

for x in df_rest.index:
    images += df["photoCount"][x]
    videos += df["videoCount"][x]
    gifs += df["gifCount"][x]
    
    if df["retweet"][x] == True:
        retweets += 1

    if df["quoteTweet"][x] == True:
        quotes += 1

    if df["redundant"][x] == True:
        redundant += 1

    if df["geoenabled"][x] == True:
        geoenabled += 1

    if df["verified"][x] == True:
        verified += 1

    if df["coordinates"][x] != None:
        coords += 1
        
    elif df["place_name"][x] != None:
        twitter_place += 1
        
    elif df["location"][x] != None:
        generic_location += 1

print("Analysis result from REST API Crawler")
print("images - " + str(images))
print("videos - " + str(videos))
print("gifs - " + str(gifs))
print("verified - " + str(verified))
print("retweets - " + str(retweets))
print("quotes - " + str(quotes))
print("redundant - " + str(redundant))
print("geoenabled - " + str(geoenabled))
print("coordinates - " + str(coords))
print("place objects - " + str(twitter_place))
print("Generic - " + str(generic_location))