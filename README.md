## openplotter-network

OpenPlotter app to manage network connections in Raspberry Pi

### Installing

#### For production

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) and just install this app from *OpenPlotter Apps* tab.

#### For development

Install dependencies:

`sudo apt install openplotter-settings hostapd dnsmasq bridge-utils dialog usbmuxd libnss-mdns avahi-utils libavahi-compat-libdnssd-dev`

Clone the repository:

`git clone https://github.com/openplotter/openplotter-network.git`

Make your changes and test them:

`sudo python3 setup.py install`

Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://launchpad.net/~openplotter/+archive/ubuntu/openplotter/).

### Documentation

https://openplotter.readthedocs.io

### Support

http://forum.openmarine.net/forumdisplay.php?fid=1