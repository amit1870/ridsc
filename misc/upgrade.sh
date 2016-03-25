#!/bin/bash

RIDS="/home/pi/ridsc"

echo "Upgrading RIDS ..."

echo "Ensuring proper permission is set..."
sudo chown -R pi:pi $RIDS
sudo chown -R pi:pi /home/pi/rids_assets
# sudo chown -R pi:pi /home/pi/.ridsc

echo "Installing new dependencies..."
sudo apt-get -y -qq install $(cat ~/ridsc/packages.txt) > /dev/null

echo "Ensuring all Python modules are installed..."
sudo pip install -r $RIDS/requirements.txt -q

echo "Changing BOOT Splash Screen with RIDS..."
sudo cp ~/ridsc/static/img/rids_boot.png ~/rids_assets/
sudo mv /etc/rids_boot.png /etc/rids_boot.bak.png
sudo ln -s ~/rids_assets/rids_boot.png /etc/rids_boot.png

sudo chmod 600 ~/ridsc/misc/sshkey 

echo "Restarting viewer module..."
pkill -f "viewer.py"

echo "Done! Please reboot."
