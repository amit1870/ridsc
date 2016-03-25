import urllib2
from bs4 import BeautifulSoup
import re
from settings import settings

def filter_feeds(description):
	description = description.strip()

	description = description.replace('"',"'")
	description = description.replace('\n',"")
	description = description.replace('[',"")
	description = description.replace(']',"")
	description = description.replace('<p/>',"")
	description = description.replace('<p>',"")
	description = description.replace('</p>',"")
	description = description.replace('<br>',"")
	description = description.replace('<br/>',"")
	description = description.replace('<br />',"")
	link_pattern = "http://"
	if description.lower().find(link_pattern.lower()) != -1:
		description = description.split("<a")[0]
	link_pattern = "<img"
	if description.lower().find(link_pattern.lower()) != -1:
		try:
			description = description.split("/>")[1]
		except:
			description = description.split(">")[1]
	div_pattern = "<div"
	if description.lower().find(div_pattern.lower()) != -1:
		description = description.split("<div")[0]

	return description

def get_rssfeed(url,count):
	feeds = []
	try:
		usock = urllib2.urlopen(url)
		xml = usock.read()
		soup = BeautifulSoup(xml,"xml")
		items = soup.findAll('item')
			
		for item in items:
			title = item.findAll('title')[0].contents
			title = "".join(title)

			title = "<b>"+ title + ":</b>"
			description = item.findAll('description')[0].contents
			description = "".join(description)
			feeds.append(title + filter_feeds(description))
		return feeds[:min(count,len(feeds))]

	except:
		return feeds

if settings['show_rss_on'] != 'N':
	new_feeds = get_rssfeed(settings['rss_url'],int(settings['no_of_feeds']))
	
	FILE = '/home/pi/rids_files/feeds.txt'
	try:
		with file(FILE) as f: 
			feeds = eval(f.read())
	except:
		feeds = []

	if feeds != new_feeds and new_feeds != []:
		f = open(FILE,'w')
		f.write(str(new_feeds))
		f.close()
		print "New feeds fetched"

	elif new_feeds == feeds and feeds == None:
		f = open(FILE,'w')
		f.write('[]')
		f.close()
		
	else:
		print "No new feeds"