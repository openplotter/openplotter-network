#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2019 by e-sailing <https://github.com/e-sailing/openplotter-network>
# Copyright (C) 2019 by Sailoog <https://github.com/openplotter/openplotter-network>
#
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.
import os, subprocess
from openplotterSettings import conf
from openplotterSettings import language

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(__file__)
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-network',currentLanguage)

	try:	
		print(_('Restoring network Debian defaults...'))
		subprocess.call(['cp', currentdir+'/Network/dhcpcd_default.conf', '/etc/dhcpcd.conf'])
		subprocess.call(['rm', '-f', '/etc/network/interfaces.d/ap'])
		subprocess.call(['rm', '-f', '/etc/udev/rules.d/72-wireless.rules'])
		subprocess.call(['rm', '-f', '/etc/udev/rules.d/11-openplotter-usb0.rules'])
		subprocess.call(['rm', '-f', '/lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant_wlan9'])
		subprocess.call(['cp', currentdir+'/Network/dhcpcd-hooks/10-wpa_supplicant', '/lib/dhcpcd/dhcpcd-hooks'])
		subprocess.call(['rm', '-f', '/etc/systemd/network/bridge-br0.network'])
		subprocess.call(['rm', '-f', '/etc/systemd/network/bridge-br0-slave.network'])
		subprocess.call(['rm', '-f', '/etc/systemd/network/bridge-br0.netdev'])

		print(_('Removing openplotter-network service...'))
		subprocess.call(['systemctl', 'disable', 'dnsmasq'])
		subprocess.call(['systemctl', 'disable', 'hostapd'])
		subprocess.call(['systemctl', 'disable', 'systemd-networkd'])
		subprocess.call(['systemctl', 'disable', 'openplotter-network'])
		subprocess.call(['systemctl', 'stop', 'openplotter-network'])
		subprocess.call(['rm', '-f', '/etc/systemd/system/openplotter-network.service'])
		subprocess.call(['systemctl', 'daemon-reload'])
		print(_('DONE. PLEASE REBOOT TO RESTORE NETWORK SETTINGS'))
	except Exception as e: print(_('FAILED: ')+str(e))


if __name__ == '__main__':
	main()