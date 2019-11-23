#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2019 by e-sailing <https://github.com/e-sailing/openplotter-network>
# Copyright (C) 2019 by Sailoog <https://github.com/openplotter/openplotter-network>

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

from setuptools import setup
from openplotterNetwork import version

setup (
	name = 'openplotterNetwork',
	version = version.version,
	description = 'OpenPlotter app to manage network connections in Raspberry Pi',
	license = 'GPLv3',
	author="Sailoog",
	author_email='info@sailoog.com',
	url='https://github.com/openplotter/openplotter-network',
	packages=['openplotterNetwork'],
	classifiers = ['Natural Language :: English',
	'Operating System :: POSIX :: Linux',
	'Programming Language :: Python :: 3'],
	include_package_data=True,
	entry_points={'console_scripts': ['openplotter-network=openplotterNetwork.openplotterNetwork:main','networkPreUninstall=openplotterNetwork.networkPreUninstall:main','networkPostInstall=openplotterNetwork.networkPostInstall:main']},
	scripts=['bin/install-wifi'],
	data_files=[('share/applications', ['openplotterNetwork/data/openplotter-network.desktop']),('share/pixmaps', ['openplotterNetwork/data/openplotter-network.png']),],
	)
