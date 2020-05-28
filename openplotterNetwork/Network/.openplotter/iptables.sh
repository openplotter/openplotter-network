#!/bin/sh
internet=$1
router=$2

base=auto
baserouter=br0

#delete old filter
    sudo iptables -t nat -F
    sudo iptables -t mangle -F
    sudo iptables -F
    sudo iptables -X

if [ $internet = $base ];
then
	internet=wlan0
	iptables -t nat -A POSTROUTING -o "${internet}" -j MASQUERADE
	iptables -A FORWARD -i "${internet}" -o "${router}" -m state --state RELATED,ESTABLISHED -j ACCEPT
	iptables -A FORWARD -i "${router}" -o "${internet}" -j ACCEPT
	internet=wlan1
	iptables -t nat -A POSTROUTING -o "${internet}" -j MASQUERADE
	iptables -A FORWARD -i "${internet}" -o "${router}" -m state --state RELATED,ESTABLISHED -j ACCEPT
	iptables -A FORWARD -i "${router}" -o "${internet}" -j ACCEPT
	internet=eth1
	iptables -t nat -A POSTROUTING -o "${internet}" -j MASQUERADE
	iptables -A FORWARD -i "${internet}" -o "${router}" -m state --state RELATED,ESTABLISHED -j ACCEPT
	iptables -A FORWARD -i "${router}" -o "${internet}" -j ACCEPT
	internet=usb0
	iptables -t nat -A POSTROUTING -o "${internet}" -j MASQUERADE
	iptables -A FORWARD -i "${internet}" -o "${router}" -m state --state RELATED,ESTABLISHED -j ACCEPT
	iptables -A FORWARD -i "${router}" -o "${internet}" -j ACCEPT

	if [ $router != $baserouter ];
    then
		internet=eth0
		iptables -t nat -A POSTROUTING -o "${internet}" -j MASQUERADE
		iptables -A FORWARD -i "${internet}" -o "${router}" -m state --state RELATED,ESTABLISHED -j ACCEPT
		iptables -A FORWARD -i "${router}" -o "${internet}" -j ACCEPT
	fi
	
else
	iptables -t nat -A POSTROUTING -o "${internet}" -j MASQUERADE
	iptables -A FORWARD -i "${internet}" -o "${router}" -m state --state RELATED,ESTABLISHED -j ACCEPT
	iptables -A FORWARD -i "${router}" -o "${internet}" -j ACCEPT
fi
