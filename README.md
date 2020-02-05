## openplotter-network

OpenPlotter app to manage network connections in Raspberry Pi

### Installing

#### For production

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **production** and just install this app from *OpenPlotter Apps* tab.

#### For development

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **development**.

Install dependencies:

```
sudo apt install hostapd dnsmasq bridge-utils dialog usbmuxd libnss-mdns avahi-utils libavahi-compat-libdnssd-dev
sudo pip3 install pyric
```

Clone the repository:

`git clone https://github.com/openplotter/openplotter-network.git`

Install:

```
cd openplotter-network
sudo python3 setup.py install
```
Run post-installation script:

`sudo networkPostInstall`

Run:

`openplotter-network`

Make your changes and repeat installation and post-installation steps to test. Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://launchpad.net/~openplotter/+archive/ubuntu/openplotter/).

### Documentation

https://openplotter.readthedocs.io

### Support

http://forum.openmarine.net/forumdisplay.php?fid=1