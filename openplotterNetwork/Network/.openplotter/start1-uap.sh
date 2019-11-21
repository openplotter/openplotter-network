#!/bin/sh
#sleep 30
seconds=5
systemctl stop hostapd.service
systemctl stop dnsmasq.service
systemctl stop dhcpcd.service

#when wlan9 exist it must be deleted first
if [ -e /sys/class/net/wlan9 ]
then
    iw dev wlan9 del
fi

#before adding an access point to the same device it must be turned off
ifconfig wlan0 down
#adding wlan9 as access point to wlan0"
iw dev wlan0 interface add wlan9 type __ap
#enable turned off wlan9
ifconfig wlan9 up

#start services, mitigating race conditions
#start access point
systemctl start hostapd.service
sleep "${seconds}"
#restart dhcpcd
systemctl restart dhcpcd.service
sleep "${seconds}"
#start dhcp server
systemctl start dnsmasq.service
