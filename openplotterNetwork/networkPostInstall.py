#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2015 by Sailoog <https://github.com/openplotter/openplotter-network>
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

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(__file__)
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-network',currentLanguage)

	try:
		print(_('Editing config files...'))

		fo = open('/etc/default/hostapd', "w")
		fo.write( 'DAEMON_CONF="/etc/hostapd/hostapd.conf"')
		fo.close()

		fo = open('/etc/systemd/system/openplotter-network.service', "w")
		fo.write( '[Service]\nExecStart='+conf2.home+'/.openplotter/start-ap-managed-wifi.sh\nStandardOutput=syslog\nStandardError=syslog\nUser='+conf2.user+'\n\n[Install]\nWantedBy=multi-user.target\n')
		fo.close()

		subprocess.call(['systemctl', 'daemon-reload'])
		subprocess.call(['systemctl', 'unmask', 'hostapd.service'])
		subprocess.call(['systemctl', 'enable', 'openplotter-network'])

		print(' ')
		print(_('DONE'))

	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()
