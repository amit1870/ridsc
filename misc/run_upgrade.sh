#!/bin/bash
LOG=/tmp/rids_monitor.log

function update_rids {
	output=`ssh-agent bash -c 'ssh-add /home/pi/ridsc/misc/sshkey; cd ~/ridsc; git pull'`
	
	if [[ $output != 'Already up-to-date.' ]]; then
		/bin/bash ~/ridsc/misc/upgrade.sh >> $LOG	
	fi
}
update_rids
