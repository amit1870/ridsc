#!/bin/bash

echo "Installing RIDS (beta)"

## Simple disk storage check. Naively assumes root partition holds all system data.
ROOT_AVAIL=$(df -k / | tail -n 1 | awk {'print $4'})
MIN_REQ="512000"

if [ $ROOT_AVAIL -lt $MIN_REQ ]; then
  echo "Insufficient disk space. Make sure you have at least 500MB available on the root partition."
  exit 1
fi

echo "Updating system package database..."
sudo apt-get -qq update > /dev/null

echo "Upgrading the system..."
echo "(This might take a while.)"
sudo apt-get -y -qq upgrade > /dev/null

echo "Installing dependencies..."
sudo apt-get -y -qq install $(cat ~/ridsc/packages.txt) > /dev/null

echo "Downloading RIDS..."
# git clone git://bitbucket.com/rigvee/ridsc.git ~/rids > /dev/null

echo "Installing more dependencies..."
sudo pip install -r ~/ridsc/requirements.txt -q > /dev/null

echo "Adding RIDS to X auto start..."
mkdir -p ~/.config/lxsession/LXDE/
echo "@~/ridsc/misc/xloader.sh" > ~/.config/lxsession/LXDE/autostart

echo "Increasing swap space to 500MB..."
echo "CONF_SWAPSIZE=500" > ~/dphys-swapfile
sudo cp /etc/dphys-swapfile /etc/dphys-swapfile.bak
sudo mv ~/dphys-swapfile /etc/dphys-swapfile

echo "Adding RIDS's config-file"
mkdir -p ~/rids_assets
cp ~/ridsc/misc/rids.conf ~/rids_assets/
mkdir -p ~/rids_files

echo "Enabling Watchdog..."
sudo modprobe bcm2708_wdog > /dev/null
sudo cp /etc/modules /etc/modules.bak
sudo sed '$ i\bcm2708_wdog' -i /etc/modules
sudo chkconfig watchdog on
sudo cp /etc/watchdog.conf /etc/watchdog.conf.bak
sudo sed -e 's/#watchdog-device/watchdog-device/g' -i /etc/watchdog.conf
sudo /etc/init.d/watchdog start

echo "Adding RIDS to autostart (via Supervisord)"
sudo ln -s ~/ridsc/misc/supervisor_rids.conf /etc/supervisor/conf.d/rids.conf
sudo /etc/init.d/supervisor stop > /dev/null
sudo /etc/init.d/supervisor start > /dev/null

echo "Making modifications to X..."
[ -f ~/.gtkrc-2.0 ] && rm -f ~/.gtkrc-2.0
ln -s ~/ridsc/misc/gtkrc-2.0 ~/.gtkrc-2.0
[ -f ~/.config/openbox/lxde-rc.xml ] && mv ~/.config/openbox/lxde-rc.xml ~/.config/openbox/lxde-rc.xml.bak
[ -d ~/.config/openbox ] || mkdir -p ~/.config/openbox
ln -s ~/ridsc/misc/lxde-rc.xml ~/.config/openbox/lxde-rc.xml
[ -f ~/.config/lxpanel/LXDE/panels/panel ] && mv ~/.config/lxpanel/LXDE/panels/panel ~/.config/lxpanel/LXDE/panels/panel.bak
[ -f /etc/xdg/lxsession/LXDE/autostart ] && sudo mv /etc/xdg/lxsession/LXDE/autostart /etc/xdg/lxsession/LXDE/autostart.bak
sudo sed -e 's/^#xserver-command=X$/xserver-command=X -nocursor/g' -i /etc/lightdm/lightdm.conf

# Make sure we have proper framebuffer depth.
if grep -q framebuffer_depth /boot/config.txt; then
  sudo sed 's/^framebuffer_depth.*/framebuffer_depth=32/' -i /boot/config.txt
else
  echo 'framebuffer_depth=32' | sudo tee -a /boot/config.txt > /dev/null
fi

# Fix frame buffer bug
if grep -q framebuffer_ignore_alpha /boot/config.txt; then
  sudo sed 's/^framebuffer_ignore_alpha.*/framebuffer_ignore_alpha=1/' -i /boot/config.txt
else
  echo 'framebuffer_ignore_alpha=1' | sudo tee -a /boot/config.txt > /dev/null
fi

# Fix hdmi blinking bug
if grep -q config_hdmi_boost /boot/config.txt; then
  sudo sed 's/^config_hdmi_boost.*/config_hdmi_boost=4/' -i /boot/config.txt
else
  echo 'config_hdmi_boost=4' | sudo tee -a /boot/config.txt > /dev/null
fi

# added for display rotation
if grep -q display_rotate /boot/config.txt; then
  sudo sed 's/^display_rotate.*/display_rotate=0/' -i /boot/config.txt
else
  echo 'display_rotate=0' | sudo tee -a /boot/config.txt > /dev/null
fi

echo "Quiet the boot process..."
sudo cp /boot/cmdline.txt /boot/cmdline.txt.bak
sudo sed 's/$/ loglevel=3/' -i /boot/cmdline.txt
sudo sed 's/$/ logo.nologo/' -i /boot/cmdline.txt
sudo sed 's/$/ quiet/' -i /boot/cmdline.txt
sudo sed 's/console=tty1/console=tty9/' -i /boot/cmdline.txt

echo "Changing BOOT Splash Screen with RIDS..."
sudo cp ~/ridsc/static/img/rids_boot.png ~/rids_assets/
sudo mv /etc/rids_boot.png /etc/rids_boot.bak.png
sudo ln -s ~/rids_assets/rids_boot.png /etc/rids_boot.png
sudo cp ~/ridsc/misc/aarids_boot.sh /etc/init.d/aarids_boot
sudo chmod a+x /etc/init.d/aarids_boot
sudo insserv /etc/init.d/aarids_boot

echo "Adding autoconnect to /etc/init.d"
sudo cp ~/ridsc/misc/autoconnect /etc/init.d/autoconnect 
sudo chmod a+x /etc/init.d/autoconnect

echo "Adding wvdial.conf and usb_modeswitch.conf to /etc/ "
sudo cp ~/ridsc/misc/wvdial.conf /etc/wvdial.conf
sudo cp ~/ridsc/misc/usb_modeswitch.conf /etc/usb_modeswitch.conf

echo "Adding scripts to crontab..."
tmp=${TMPDIR:-/tmp}/xyz.$$
trap "rm -f $tmp; exit 1" 0 1 2 3 13 15
crontab -l > $tmp
echo "SHELL=/bin/bash" >> $tmp
echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> $tmp
echo "* * * * * $HOME/ridsc/misc/rsink 2>&1 >> /tmp/rsink_cron.log" >> $tmp
echo "@reboot /home/pi/ridsc/misc/run_wifi.sh 2>&1 >> /tmp/rids_wifi.log" >> $tmp
echo "@reboot /home/pi/ridsc/misc/get_frame.sh 2>&1 >> /tmp/rids_wifi.log" >> $tmp
echo "@reboot /home/pi/ridsc/misc/scrshot.sh 2>&1 >> /dev/null " >> $tmp
crontab < $tmp
rm -f $tmp

tmp=${TMPDIR:-/tmp}/xyz.$$
trap "rm -f $tmp; exit 1" 0 1 2 3 13 15
crontab -l > $tmp
echo "@reboot sleep 180 && python /home/pi/ridsc/twitter.py 2>&1 >> /tmp/rids_wifi.log" >> $tmp
echo "@reboot sleep 180 && python /home/pi/ridsc/rssfeed.py 2>&1 >> /tmp/rids_wifi.log" >> $tmp
echo "*/30 * * * * python /home/pi/ridsc/twitter.py 2>&1 >> /tmp/rids_wifi.log" >> $tmp
echo "*/30 * * * * python /home/pi/ridsc/rssfeed.py 2>&1 >> /tmp/rids_wifi.log" >> $tmp
echo "*/10 * * * * /home/pi/ridsc/misc/get_frame.sh 2>&1 >> /tmp/rids_wifi.log" >> $tmp
crontab < $tmp
rm -f $tmp

echo "Setting Up Wifi"
[ -f /etc/network/interfaces ] && sudo mv /etc/network/interfaces /etc/network/interfaces.bak
sudo cp ~/ridsc/misc/interfaces ~/rids_assets/interfaces
sudo ln -s ~/rids_assets/interfaces /etc/network/interfaces
[ -f /etc/wpa_supplicant/wpa_supplicant.conf ] && sudo mv /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.bak
sudo cp ~/ridsc/misc/wpa_supplicant.conf ~/rids_assets/wpa_supplicant.conf
sudo ln -s ~/rids_assets/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf

echo "Changing Keyboard Layout to US"
sudo sed 's/gb/us/' -i /etc/default/keyboard

echo "Changing Installation Id"
sudo sed "s/inst_id_chg/$1/" -i ~/ridsc/install_id.py

echo "Installing tweepy for twitter..."
cd ~
git clone -qq git://github.com/joshthecoder/tweepy.git 
cd tweepy
sudo python setup.py -qq install 
sudo rm -r ~/tweepy
cd ~

echo "Creating feeds.txt, tweets.txt, ipaddr.txt in ~/rids_files dir ..."
echo "[]" > /home/pi/rids_files/feeds.txt 
echo "[]" > /home/pi/rids_files/tweets.txt 
echo "0.0.0.0" > /home/pi/rids_files/ipaddr.txt
echo "" > /home/pi/rids_files/latest_rids_sha

# updating youtube-dl to remove signature problem
sudo youtube-dl -U >> /dev/null
sudo youtube-dl

# creating udev rule for 3G doungle automatic switch
sudo echo "ATTRS{idVendor}==\"12d1\", ATTRS{idProduct}==\"1446\", RUN+=\"usb_modeswitch '%b/%k'\"" >> /home/pi/41-usb_modeswitch.rules
sudo mv /home/pi/41-usb_modeswitch.rules /etc/udev/rules.d/41-usb_modeswitch.rules

sudo chmod 600 ~/ridsc/misc/sshkey 
echo "Assuming no errors were encountered, go ahead and restart your computer."