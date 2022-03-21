OpenPlotter does use standard raspbian network!

The additional packets needed for AP are:
sudo apt-get install hostapd dnsmasq
The additional packets to use eth0 in the same net as the AP are:
sudo apt-get install bridge-utils

When activating a network profile with "Apply 1" OpenPlotter: copies the selected setting from here to the directory /home/pi/.openplotter/Network
OpenPlotter edit the individual settings as ssid password ... there.
Manual settings should be done here also.

The "Apply 2" button copies some files into the system.

(wlan9 is used for the AP. You can use more wifi adapter but remember the internet connection would work with the first gateway (use: "ip route" to see it)
The network is shared to the clients (get internet access for the clients).
wlan0 and wlan1 are blocked by nft to disallow others to get access to the raspberry (public marina wifi).
If the ssid is declared private (file /home/pi/.openplotter/private_ssid.txt) it won't be blocked.

Headless mode with android device as display (android will be on usb0)
Use android device to connect to the rpi with usb cable.
Activate tethering usb in android.
Now you have a network connection between rpi and android.
Install realvnc.
Start realvnc with ip address 192.168.42.10, openplotter or openplotter.local.

Headless mode with iphone/ipad device as display (iphone will be on eth1)
Use iphone/ipad device to connect to the rpi with usb cable.
Install realvnc.
Start realvnc with ip address 172.20.10.3, openplotter.local.

The raspbian standard wifi settings (in the upper right corner) often don't want to change from one marina to the next one.
If you don't get the connection symbol you can "Turn Off Wifi" and "Turn On Wifi". To get it to work. (Wait an instant until the wlan list updates.)
If you are connected over the AP use the
bash file /home/pi/.openplotter/Network/restart_wlan0.sh

Add ethernet port to the AP (bridge) is only needed when you want to connect a ethernet mfd (plotter), a ethernet radar or a pc.

For rpi 3b 3b+ 4b you can use the internal wifi to act as AP and Station. This is good to save energy. But it isn't so realiable and it reduces speed.
(see https://github.com/peebles/rpi3-wifi-station-ap-stretch)

To have a good internet connection we recommend to use a usb wifi stick with antenna connected by a long usb cable (with active usb hub at the end to have good 5V supply)
to get the best connection to the marina wifi.
