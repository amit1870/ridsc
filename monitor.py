from install_id import INSTALLATION_ID
from api_url import API_URL,RCA
import urllib
import ast
import os
from subprocess import check_output, Popen
from ipaddr import IP


scr = check_output(['tvservice', '-s']).split(" ")[2]

if (scr != "[NTSC") or RCA:
	print 'Screen On'
else:
	os.system("sudo reboot")

url = API_URL + INSTALLATION_ID + "/log/?ipaddr=" + IP

r = urllib.urlopen(url)
if r.code == 200:
	commands = ast.literal_eval(r.read())['commands']
	print commands
	for command in commands:
		if(command=='R'):
			url = API_URL + INSTALLATION_ID + "/ack/R/"
			r = urllib.urlopen(url)			
			print "Rebooting Now"
			os.system("sudo reboot")

		if(command=='K'):
			url = API_URL + INSTALLATION_ID + "/ack/K/"
			r = urllib.urlopen(url)			
			print "Restarting RIDS"
			os.system("killall python")

		if(command=='U'):
			url = API_URL + INSTALLATION_ID + "/ack/U/"
			# Pulling the latest code
			cmd = "ssh-agent bash -c 'ssh-add /home/pi/ridsc/misc/sshkey; cd ~/ridsc; git pull'"
			print check_output([cmd],shell=True)
			# Run upgrade.sh after pull
			cmd = "/home/pi/ridsc/misc/upgrade.sh"
			print Popen([cmd],shell=True)
			r = urllib.urlopen(url)

