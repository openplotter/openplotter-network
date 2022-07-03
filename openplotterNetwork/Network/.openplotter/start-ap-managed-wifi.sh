#!/bin/sh
share_internet=True
nft_public_security=True
cd /home/pi/.openplotter
sleep 1
echo "start" >> /home/pi/log.txt
rfkill unblock all
if [ "$share_internet" = True ] ; then
	sysctl -w net.ipv4.ip_forward=1
	echo "ip forward started" >> /home/pi/log.txt
else
	sysctl -w net.ipv4.ip_forward=0
fi
/bin/bash start1.sh

if [ "$nft_public_security" = True ] ; then
	echo "nft public security started" >> /home/pi/log.txt
	/home/pi/.openplotter/wpa_cli_script.sh none CONNECTED
	/usr/sbin/wpa_cli -a /home/pi/.openplotter/wpa_cli_script.sh
fi
