#!/bin/bash
wlan0=""
ssid0=""
wlan1=""
ssid1=""
arg2=$2

function work () {
	wlan=$1
	wlanExists="$(ls /sys/class/net/ | grep "$wlan")"

	if [ "$wlanExists" ]; then
		echo $wlan exists

		wlanHandle="$(sudo nft --handle --numeric list chain inet filter INPUT | grep usb0 | cut -d'#' -f 2 | cut -d' ' -f 3)"
		wlan9="$(sudo nft list ruleset | grep wlan9)"
		br0="$(sudo nft list ruleset | grep br0)"
		ssid="$(sudo wpa_cli status -i "$wlan" | grep "\bssid" | cut -d'=' -f 2)"
		echo $wlan" handle:" $wlanHandle
		echo "ssid:" $ssid
		
		if [ "$ssid" ]
		then
			if grep -Fxq "$ssid" private_ssid.conf
			then	
				echo "found private network ssid"
				if [ "$wlanHandle" ]
				then
					# text length > 0 -> blocked must be deleted
					#sudo nft delete rule inet filter INPUT handle "$wlanHandle"
					#echo delete rule $wlan
					sudo nft delete chain inet filter INPUT
					sudo nft add 'chain inet filter INPUT {type filter hook input priority filter; policy accept;}'
					echo open input filter
				else
					echo no rule to delete					
				fi
			# public network
			else
				echo "found public network ssid"
				if [ -z "$wlanHandle" ]
				then
					echo "public network not blocked must be added"
					#sudo nft add rule inet filter INPUT iifname $wlan drop
					#echo add rule $wlan
					sudo nft delete chain inet filter INPUT
					sudo nft add 'chain inet filter INPUT {type filter hook input priority filter; policy drop;}'
					sudo nft add rule inet filter INPUT iifname "lo" accept
					sudo nft add rule inet filter INPUT iifname "eth1" accept
					sudo nft add rule inet filter INPUT iifname "usb0" accept
					if [ "$wlan9" ]; then
						sudo nft add rule inet filter INPUT iifname "wlan9" accept
					else
						sudo nft add rule inet filter INPUT iifname "br0" accept
					fi
					if [ -z "$br0" ]; then
						sudo nft add rule inet filter INPUT iifname "eth0" accept
					fi
					sudo nft add rule inet filter INPUT ct state { established, related } accept
					sudo nft add rule inet filter INPUT ct state invalid drop
					sudo nft add rule inet filter INPUT ip protocol icmp accept
					echo block wlan0 and wlan1 for outside
				else
					echo rule already exists					
				fi
			fi
		fi
	else
		echo $wlan does not exist
	fi

}
# text length 0 (wlan0 not connected or too early)
echo "arg2 " $2
case "$2" in
    CONNECTED)
        echo "WPA supplicant: connection established";
		work wlan0
		work wlan1
        ;;
    DISCONNECTED)
        echo "WPA supplicant: connection lost";
        ;;
esac
