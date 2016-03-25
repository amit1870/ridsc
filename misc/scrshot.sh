#!/bin/bash
# This script will generate the screenshot of running pi
PATH=/bin/sh.distrib /bin/sh /usr/share/man/man1/sh.1.gz

while true ; do
	sleep 120
	dir=/home/pi/rids_files
	if [ -d "$dir" ]; then
		cd $dir
	else
		mkdir $dir && cd $dir
	fi
	
	export DISPLAY=:0 
	str=`cat /home/pi/ridsc/install_id.py`
	arrIN=(${str//=/ })
	ID=${arrIN[1]}
	len=${#ID}
	ID=${ID:1:$len-2}
	sudo rm -r screenshot*
	scrot -z "screenshot$ID.png"
	
done

