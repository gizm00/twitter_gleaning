from twython import Twython, TwythonError
from unidecode import unidecode
import psycopg2
import time
import re
import urllib2
from bs4 import BeautifulSoup
import datetime
from dateutil import tz

#######
#
# Script mines twitter query API, starting with the most recent results and walking back in time
# using max_id to find earlier posts. 
# Built in rate limiting via sleep to stay under the 180 requests/ 15min window
# Current rate is 10 queries / min = 150 queries / 15min
# Tweets stored in a postgres db
# Uses 1.1 API version
#
########

def GetTwitterImage(tweet) :
	try :
		url = tweet['entities']['media'][0]['media_url']
		return url
	except :
		return

def GetInstagramImage(tweet) :
	try:
		url = search_results['entities']['urls'][0]['expanded_url']
		page = urllib2.urlopen(url).read()
	except:
		return

	soup = BeautifulSoup(page)
	imageUrl = soup.find('meta', attrs={'property': 'og:image', 'content': True})
	if (imageUrl != None) :
		return imageUrl['content']

def GetResults(search_results) :
	tweetCount = 0;
	try:
		length = len(search_results['statuses'])
	except Exception, e:
		print search_results
	
	print "search results: " + str(length)
	lastId = 0
	for tweet in search_results['statuses']:
		#print tweet

		ts = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))

		#print 'Tweet %s from @%s Date: %s Location: %s Coords: %s Geo: %s Id: %s Lang: %s' % (tweetCount, tweet['user']['screen_name'].encode('utf-8'), ts, tweet['user']['location'].encode('utf-8'), tweet['coordinates'], tweet['geo'], tweet['id'], tweet['lang'])
		#print tweet['text'].encode('utf-8'), '\n'

		queryStr = "INSERT INTO cxnats (id, name, text, loc, image_url, num_retweets, timestamp, coordinates, geo) VALUES("
		#queryVals = "'" + unidecode(tweet['user']['screen_name']) + "','" + ts + "','" + unidecode(tweet['user']['location']) + "','" + unidecode(tweet['coordinates']) + "','" + tweet['geo'] + "'," + tweet['id'] + ",'" + tweet['lang'] + "')"
		if (tweet['user']['location'] == None ): 
			location = "NULL" 
		else : 
			location = tweet['user']['location']
			#print "location: " + location
		if (tweet['coordinates'] == None):
			coords = "NULL"
		else :
			coords = str(tweet['coordinates']['coordinates'][0]) + " " + str(tweet['coordinates']['coordinates'][1])
			#print "coords: " + coords
		if (tweet['geo'] == None) :
			geo = "NULL"
		else :
			geo = str(tweet['geo']['coordinates'][0]) + " " + str(tweet['geo']['coordinates'][1]) 
			#print "geo: " + geo

		image_url = GetTwitterImage(tweet)
		if (image_url == None) :
			#check for instagram image
			image_url = GetInstagramImage(tweet)
		if (image_url == None) :
			image_url = "NULL"

		queryVals = str(tweet['id']) + ",'" + re.sub(r"[',]", "", tweet['user']['screen_name']) + "','" + re.sub(r"[',\n]", "", tweet['text']) + "','" + re.sub(r"[',]", "", location)+ "','" + image_url + "'," + str(tweet['retweet_count']) + ",'" + ts + "','" + coords + "','" + geo + "')"
	
		#print tweet['text']
		try :
			dbCursor.execute(queryStr + queryVals)
			conn.commit()
			a = 1
		except Exception as e :
			print "Unable to insert: " + e[0] + " " + queryStr + queryVals
			conn.rollback()
		
		lastId = tweet['id']

	return lastId


######
#
# Need to define your twitter keys to connect
#
######

twitter = Twython(consumer_key,
              consumer_secret,
              access_token,
              access_token_secret)

try:
    search_results = twitter.search(q='#cxnats OR @AustinCityParks OR @usacycling', result_type='recent', include_entities=True, count=100)
except TwythonError as e:
    print e
    exit

# connect to db
try:
	 conn = psycopg2.connect("dbname='tweets' user='postgres' host='localhost' password=''")
except:
	print "unable to connect to the database"
else:		
	if (conn != None):
   	 	dbCursor = conn.cursor();

#while (len(search_results) > 0) :
#for sl in range (0, 10):
a=1
while(True) :
	# add a delay to avoid rate limiting - search limited to 180 requests per 15min
	#wait 1 minute
	print "start sleep: " + time.strftime("%I:%M:%S")
	time.sleep(60)	
	print "end sleep: " + time.strftime("%I:%M:%S")

	#send 10 queries / minute
	for i in range (0, 9) :
		newIndex = GetResults(search_results)
		print "new index:  " + str(newIndex)
		try:
			search_results = twitter.search(q='#cxnats OR @AustinCityParks OR @usacycling', result_type='recent', include_entities=True, count=100, max_id=newIndex)
		except TwythonError as e:
			print e
			exit
	a=2
dbCursor.close()
conn.close()