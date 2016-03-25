import tweepy
from settings import settings

consumer_key = "Xr6KWgR7T7gk2wgKLSaU0w"

consumer_secret = "dZoz2jB7oMGtdcP6GBVWR22vf7UxM9RU7sYbeZq0M"

access_token = "2324996719-Rl9E5JIJ13gdwYMTtDWJwZGJLzcE5EM5hSjbN6O"

access_token_secret = "KR1oFZFidusr9O1FqTovZjfzPnzCJJLgnZ7w8ZAHbm1rk"
try:
	auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	#Creating api object
	api = tweepy.API(auth)
	user = api.me()
except:
	pass

def filter_tweets(tweets):
	tweets = tweets.replace('"',"'")
	tweets = tweets.replace('\n',"")
	tweets = tweets.replace('[',"")
	tweets = tweets.replace(']',"")
	tweets = tweets.replace('<p/>',"")
	tweets = tweets.replace('<p>',"")
	tweets = tweets.replace('</p>',"")
	tweets = tweets.replace('<br>',"")
	tweets = tweets.replace('<br/>',"")
	tweets = tweets.replace('<br />',"")
	return tweets


def tweets(handle,count):
	rep = []
	page_list = []
	try:
		for page in tweepy.Cursor(api.user_timeline, count=count,id=handle).pages(1):
			page_list.append(page)
		for page in page_list:
			for status in page:
				# rep = rep + str(status.created_at) + status.author.name + status.text + "\n\n"
				txt = status.text.strip()
				txt = txt.split('http')[0]
				rep.append(filter_tweets(txt))
			return rep
	except:
		return rep

if settings['show_twitter_on'] != 'N':
	new_tweets =  tweets(settings['twitter_handle'],int(settings['no_of_tweets']))
	
	FILE = '/home/pi/rids_files/tweets.txt'
	try:
		with file(FILE) as f: 
			tweets = eval(f.read())
	except:
		tweets = []

	if tweets != new_tweets and new_tweets != []:
		if new_tweets == None and tweets == []:
			print "Handle %s has no tweets" % settings['twitter_handle']
		else :
			f = open(FILE,'w')
			f.write(str(new_tweets))
			f.close()
			print "New tweets fetched"

	elif new_tweets == tweets and tweets == None:
		f = open(FILE,'w')
		f.write('[]')
		f.close()
		
	else:
		print "No new tweets"
		