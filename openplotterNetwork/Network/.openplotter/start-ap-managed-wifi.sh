#!/bin/sh
share_internet=True
cd /home/pi/.openplotter
sleep 1
echo "start" >> /home/pi/log.txt
echo "wpa started" >> /home/pi/log.txt
rfkill unblock all
if [ "$share_internet" = True ] ; then
	sysctl -w net.ipv4.ip_forward=1
else
	sysctl -w net.ipv4.ip_forward=0
fi
echo "ip forward started" >> /home/pi/log.txt
/bin/bash start1.sh
/usr/sbin/wpa_cli -a /home/pi/.openplotter/wpa_cli_script.sh
