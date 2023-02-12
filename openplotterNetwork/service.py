#!/usr/bin/env python3

# This file is part of OpenPlotter.
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

import sys, subprocess

if sys.argv[1] == 'ntp':
	if sys.argv[2] == 'enable':
		fo = open('/etc/chrony/conf.d/openplotter.conf', "w")
		fo.write( 'allow 192.168.0.0/24\nallow 10.10.0.0/24')
		fo.close()
		subprocess.call(['systemctl', 'restart', 'chronyd'])
	else:
		subprocess.call(['rm', '-f', '/etc/chrony/conf.d/openplotter.conf'])
		subprocess.call(['systemctl', 'restart', 'chronyd'])
