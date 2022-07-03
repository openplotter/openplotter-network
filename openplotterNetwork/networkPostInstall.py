#!/usr/bin/env python3

# This file is part of OpenPlotter.
# Copyright (C) 2022 by e-sailing <https://github.com/e-sailing/openplotter-network>
# Copyright (C) 2022 by Sailoog <https://github.com/openplotter/openplotter-network>
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

import subprocess, os
from openplotterSettings import conf
from openplotterSettings import language
from .version import version

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-network',currentLanguage)

	print(_('Installing python packages...'))
	try:
		subprocess.call(['pip3', 'install', 'pyric'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	try:
		print(_('Editing config files...'))

		fo = open('/etc/default/hostapd', "w")
		fo.write( 'DAEMON_CONF="/etc/hostapd/hostapd.conf"')
		fo.close()

		fo = open('/etc/systemd/system/openplotter-network.service', "w")
		data = '[Unit]\n'
		data += 'After=local-fs.target network-pre.target apparmor.service systemd-sysctl.service systemd-modules-load.service ifupdown-pre.service network.target\n'
		data += '\n'
		data += '[Service]\n'
		data += 'ExecStart='+conf2.home+'/.openplotter/start-ap-managed-wifi.sh\n'
		data += 'StandardOutput=syslog\n'
		data += 'StandardError=syslog\n'
		data += 'WorkingDirectory='+conf2.home+'/.openplotter\nUser=root\n'
		data += '\n'
		data += '[Install]\n'
		data += 'WantedBy=multi-user.target\n'

		fo.write(data)
		fo.close()

		fo = open(currentdir+'/Network/udev/rules.d/11-openplotter-usb0.rules', "w")
		fo.write( 'KERNEL=="usb0", SUBSYSTEMS=="net", RUN+="/bin/bash '+conf2.home+'/.openplotter/Network/11-openplotter-usb0.sh"\n')
		fo.close()

		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	try:
		print(_('Enabling services...'))

		subprocess.call(['systemctl', 'daemon-reload'])
		subprocess.call(['systemctl', 'unmask', 'hostapd.service'])
		subprocess.call(['systemctl', 'enable', 'openplotter-network'])
		subprocess.call(['systemctl', 'enable', 'nftables.service'])
		if not os.path.exists('/etc/hostapd/hostapd.conf'):
			subprocess.call(['systemctl', 'disable', 'hostapd'])
		
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Setting version...'))
	try:
		conf2.set('APPS', 'network', version)
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))
	
if __name__ == '__main__':
	main()
