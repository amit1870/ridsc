import urllib
import ast
import urllib2
from install_id import INSTALLATION_ID
from api_url import API_URL
from version import VERSION
import re
from subprocess import check_output


# to get used space on card
cmd = "df -h | grep 'rootfs'"
size = check_output([cmd],shell=True).split("  ")[5]
Used = check_output([cmd],shell=True).split("  ")[6]
Avail = check_output([cmd],shell=True).split("  ")[7]
used_per = check_output([cmd],shell=True).split("  ")[8]
USED_PER = re.findall(r'\d+', used_per)[0]


def validIP(address):
    parts = address.split(".")
    if len(parts) != 4:
        return False
    for item in parts:
        if not 0 <= int(item) <= 255:
            return False
    return True

def generate_rsync_file(resolution):

	PRE_STR = """#!/bin/bash
	#'eval `keychain --noask --eval /var/www/client/sshkey` || exit 1

	LOG=/tmp/rids_monitor.log

	python ~/ridsc/monitor.py >> $LOG 2>&1
	
	if pidof "rsync"; then
		echo "RSYNC already running"
	else
		rsync -avz --delete-after -e 'ssh -o StrictHostKeyChecking=no -i /home/pi/ridsc/misc/sshkey' """


	POST_STR = """:scheduler/""" + INSTALLATION_ID +"""/ /home/pi/rids_assets

	"""

	SCREENSHOT = """	rsync -avz -e 'ssh -o StrictHostKeyChecking=no -i /home/pi/ridsc/misc/sshkey' """

	SCREENSRC = """/home/pi/rids_files/screenshot"""+INSTALLATION_ID + ".png  /home/pi/rids_files/feeds.txt /home/pi/rids_files/tweets.txt " 
	SCREENDES = """:screenshot/""" + INSTALLATION_ID + """/
	
	"""

	LAST_STR = "fi"

	url = API_URL + INSTALLATION_ID + "/init/?resolution=" + resolution + "&version=" + VERSION  +"&size=" + size + "&Used=" + Used
	RSINK = '/home/pi/ridsc/misc/rsink'

	try:
	    r = urllib.urlopen(url)
	    if r.code == 200 :
	    	server = ast.literal_eval(r.read())['server']
	    	if validIP(server.split('@')[1]):
	    		with open(RSINK,'w') as f:
	    			f.write(PRE_STR + server.strip() + POST_STR + SCREENSHOT + SCREENSRC + server.strip() + SCREENDES + LAST_STR)

	except:
	    print "Error in Internet Connection"

