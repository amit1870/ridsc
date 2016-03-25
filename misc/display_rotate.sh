#!/bin/bash

# getting display_rotate value
display_rotate=`grep display_rotate /boot/config.txt`

# matching config value and current value of display_rotate
# if they don't match it will change that value with config
# value and will reboot the pi to make changes visible.

if [ "$display_rotate" != "display_rotate=$1" ];then
	if [ $1 -eq 0 ];then
		sudo sed 's/^display_rotate.*/display_rotate=0/' -i /boot/config.txt
		sudo reboot
	elif [ $1 -eq 1 ];then
        sudo sed 's/^display_rotate.*/display_rotate=1/' -i /boot/config.txt
        sudo reboot
    fi
fi