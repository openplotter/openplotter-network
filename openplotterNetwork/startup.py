#!/usr/bin/env python3

# This file is part of OpenPlotter.
# Copyright (C) 2022 by e-sailing <https://github.com/e-sailing/openplotter-network>
# Copyright (C) 2023 by Sailoog <https://github.com/openplotter/openplotter-network>
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

import time, subprocess, os
from openplotterSettings import language

class Start():
	def __init__(self, conf, currentLanguage):
		self.conf = conf
		self.initialMessage = ''
		
	def start(self):
		green = ''
		black = ''
		red = ''

		return {'green': green,'black': black,'red': red}

class Check():
	def __init__(self, conf, currentLanguage):
		self.conf = conf
		self.conf_folder = self.conf.conf_folder
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-network',currentLanguage)
		self.initialMessage = _('Checking Network...')

	def check(self):
		green = ''
		black = ''
		red = ''

		#access point
		wifi = self.conf_folder+'/Network/hostapd/hostapd.conf'
		if os.path.isfile(wifi):
			wifi_pass = ''
			try:
				hostapd = open('/etc/hostapd/hostapd.conf', 'r')
				data = hostapd.read()
				hostapd.close()
				i=data.find("wpa_passphrase")
				if i>=0:
					j=data[i:].find("\n")
					if j==0:j=data[i:].length
					line = data[i:i+j]
					sline = line.split('=')
					if len(sline)>1:
						wifi_pass=sline[1]
			except: pass
			if wifi_pass == '12345678':
				msg = _('Security warning: You are using the default WIFI Access Point password.\nPlease change password in OpenPlotter Network.')
				if red: red += '\n   '+msg
				else: red = msg
			else:
				msg = _('correct access point password')
				if not black: black = msg
				else: black+= ' | '+msg
		else:
			msg = _('access point disabled')
			if not black: black = msg
			else: black+= ' | '+msg

		#NTP server
		if os.path.exists('/etc/chrony/conf.d/openplotter.conf'):
			msg = _('NTP server running')
			if not green: green = msg
			else: green+= ' | '+msg
		else:
			msg = _('NTP server not running')
			if not black: black = msg
			else: black+= ' | '+msg

		return {'green': green,'black': black,'red': red}

