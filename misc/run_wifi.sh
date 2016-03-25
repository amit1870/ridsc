#!/bin/bash
# This script starts networking if connection breaks

LOG=/tmp/rids_wifi.log
PATH=/bin/sh.distrib /bin/sh /usr/share/man/man1/sh.1.gz
IP=/home/pi/ridsc/ipaddr.py    # File holds IP address
TXTIP=/home/pi/rids_files/ipaddr.txt   # File holds IP address

while true ; do
    sleep 100
    # getting old ip from ipaddr.txt
    old_ip=`cat /home/pi/rids_files/ipaddr.txt`
    if ifconfig eth0 | grep -q "inet addr:" ; then
        ifconfig=`ifconfig eth0 | grep "inet addr:"`
        arrIN=(${ifconfig//addr:/ })
        new_ip=${arrIN[1]}
        echo "Internet ON (eth0)" >> $LOG
        sudo killall wvdial

    elif ifconfig eth1 | grep -q "inet addr:" ; then
        ifconfig=`ifconfig eth1 | grep "inet addr:"`
        arrIN=(${ifconfig//addr:/ })
        new_ip=${arrIN[1]}
        echo "Internet ON (eth1)" >> $LOG
        sudo killall wvdial

    elif ifconfig wlan0 | grep -q "inet addr:" ; then
        ifconfig=`ifconfig wlan0 | grep "inet addr:"`
        arrIN=(${ifconfig//addr:/ })
        new_ip=${arrIN[1]}
        echo "Internet ON (wlan0)" >> $LOG
        sudo killall wvdial

    elif ifconfig wlan1 | grep -q "inet addr:" ; then
        ifconfig=`ifconfig wlan1 | grep "inet addr:"`
        arrIN=(${ifconfig//addr:/ })
        new_ip=${arrIN[1]}
        echo "Internet ON (wlan1)" >> $LOG
        sudo killall wvdial

    elif ifconfig ppp0 | grep -q "inet addr:" ; then
        ifconfig=`ifconfig ppp0 | grep "inet addr:"`
        arrIN=(${ifconfig//addr:/ })
        new_ip=${arrIN[1]}
        echo "Internet ON (ppp0)" >> $LOG

    else
        echo "Network connection down! Restarting network" >> $LOG
        sudo /etc/init.d/networking restart
        sudo /etc/init.d/autoconnect stop
        sudo /etc/init.d/autoconnect start
        new_ip="0.0.0.0"
        sleep 40
    fi
    # Writing new_ip to file if old_ip is not equal to new_ip
    if [[ $old_ip != $new_ip ]]; then
        sed '' $IP > $IP
        echo "IP = '$new_ip'" >> $IP
        sed '' $TXTIP > $TXTIP
        echo "$new_ip" >> $TXTIP
    fi
done

