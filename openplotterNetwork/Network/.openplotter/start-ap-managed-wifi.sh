#!/bin/sh
internet=wlan0
router=
sysctl -w net.ipv4.ip_forward=1
/bin/bash start1.sh
/bin/bash iptables.sh "$internet" "$router"
