#!/bin/sh
echo install.sh start
function disable_dhcp_server_and_ap {
	erg=$(systemctl status dnsmasq | grep 'enabled;')
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		systemctl disable dnsmasq
	fi
	
	erg=$(systemctl status hostapd | grep 'enabled;')
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		systemctl disable hostapd
	fi	
}

function enable_dhcp_server_and_ap {
	erg=$(systemctl status dnsmasq | grep disabled)
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		systemctl enable dnsmasq
	fi

	erg=$(systemctl status hostapd | grep disabled)
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		systemctl enable hostapd
	fi	
}

function disable_bridge {
	erg=$(systemctl status systemd-networkd | grep 'enabled;')
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		systemctl disable systemd-networkd
	fi
}

function enable_bridge {
	erg=$(systemctl status systemd-networkd | grep 'disabled;')
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		systemctl enable systemd-networkd
	fi
}

function delete_file {
	if [ -e $1 ]
	then
		rm $1
	fi
}

function copy_file {
	if [ -e $1 ]
	then
		cp $1 $2
	fi
}

#main
response=$1
currentdir=$2
home=$3

#set back to default debian
if [[ "$response" = "uninstall" ]]; then
	#no AP (set back to original setting)
	disable_dhcp_server_and_ap

	cp dhcpcd.conf /etc
	cp nftables/nftables.conf /etc
	echo '#!/bin/sh' > $home/.openplotter/start-ap-managed-wifi.sh
	#sudo cp network/interfaces /etc/network

	delete_file /etc/network/interfaces.d/ap
	delete_file /etc/udev/rules.d/72-wireless.rules
	delete_file /etc/udev/rules.d/11-openplotter-usb0.rules
	
	if [ -e /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant_wlan9 ]
	then
		rm /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant_wlan9
		cp $currentdir/Network/dhcpcd-hooks/10-wpa_supplicant /lib/dhcpcd/dhcpcd-hooks
	fi

	#uninstall bridge
	disable_bridge
	delete_file /etc/systemd/network/bridge-br0.network
	delete_file /etc/systemd/network/bridge-br0-slave.network
	delete_file /etc/systemd/network/bridge-br0.netdev
	
#set to access point
else
	cp dhcpcd.conf /etc
	cp dnsmasq.conf /etc
	cp nftables/nftables.conf /etc
	cp .openplotter/start-ap-managed-wifi.sh $home/.openplotter
	cp .openplotter/wpa_cli_script.sh $home/.openplotter
	cp .openplotter/start1.sh $home/.openplotter
	chmod +x $home/.openplotter/start-ap-managed-wifi.sh
	chmod +x $home/.openplotter/wpa_cli_script.sh
	chmod +x $home/.openplotter/start1.sh
	
	if [ ! -f $home/.openplotter/private_ssid.conf ]; then
		touch $home/.openplotter/private_ssid.conf
		chmod 666 $home/.openplotter/private_ssid.conf
	fi
	
	cp hostapd/hostapd.conf /etc/hostapd
#	sudo cp network/interfaces /etc/network
#	sudo cp network/interfaces.d/ap /etc/network/interfaces.d

	if [ -e /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant ]
	then
		rm /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant
		cp $currentdir/Network/dhcpcd-hooks/10-wpa_supplicant_wlan9 /lib/dhcpcd/dhcpcd-hooks
	fi

	copy_file udev/rules.d/11-openplotter-usb0.rules /etc/udev/rules.d

	enable_dhcp_server_and_ap
	
	#bridge yes/no
	if [ -e systemd/network/bridge-br0.network ]
	then
		#enable bridge
		copy_file systemd/network/bridge-br0.network /etc/systemd/network
		copy_file systemd/network/bridge-br0-slave.network /etc/systemd/network
		copy_file systemd/network/bridge-br0.netdev /etc/systemd/network
		enable_bridge
	else
		disable_bridge
		delete_file /etc/systemd/network/bridge-br0.network
		delete_file /etc/systemd/network/bridge-br0-slave.network
		delete_file /etc/systemd/network/bridge-br0.netdev
	fi
	
	#station and ap yes/no
	if [ -e $home/.openplotter/Network/.openplotter/start1.sh ]
	then
		result=$(cat $home/.openplotter/Network/.openplotter/start1.sh | grep __ap)
		#result2=$(expr length $result)
		#echo $result2
		if [ -z "$result" ]
		then
			cp udev/rules.d/72-wireless.rules /etc/udev/rules.d
		else
			delete_file /etc/udev/rules.d/72-wireless.rules
		fi
	fi

fi
echo install.sh end

