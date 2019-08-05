#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
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

import wx, os, webbrowser, subprocess
import wx.richtext as rt

from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import ports

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.currentdir = os.path.dirname(__file__)
		currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-network',currentLanguage)

		wx.Frame.__init__(self, None, title=_('OpenCPN Network'), size=(800,444))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		icon = wx.Icon(self.currentdir+"/data/openplotter-network.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)

		self.toolbar1 = wx.ToolBar(self, style=wx.TB_TEXT)
		toolHelp = self.toolbar1.AddTool(101, _('Help'), wx.Bitmap(self.currentdir+"/data/help.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolHelp, toolHelp)
		toolSettings = self.toolbar1.AddTool(102, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSettings, toolSettings)
		self.toolbar1.AddSeparator()
		toolAddresses = self.toolbar1.AddTool(103, _('Ports'), wx.Bitmap(self.currentdir+"/data/ports.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolAddresses, toolAddresses)
		toolCheck = self.toolbar1.AddTool(104, _('Check Network'), wx.Bitmap(self.currentdir+"/data/check.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolCheck, toolCheck)
		self.toolbar1.AddSeparator()
		toolDrivers = self.toolbar1.AddTool(105, _('Install Wifi Drivers'), wx.Bitmap(self.currentdir+"/data/package.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolDrivers, toolDrivers)

		self.notebook = wx.Notebook(self)
		self.ap = wx.Panel(self.notebook)
		self.output = wx.Panel(self.notebook)
		self.notebook.AddPage(self.ap, _('Access Point'))
		self.notebook.AddPage(self.output, _('Output'))
		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/ap.png", wx.BITMAP_TYPE_PNG))
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/output.png", wx.BITMAP_TYPE_PNG))
		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)
		self.notebook.SetPageImage(1, img1)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)

		self.CreateStatusBar()
		font_statusBar = self.GetStatusBar().GetFont()
		font_statusBar.SetWeight(wx.BOLD)
		self.GetStatusBar().SetFont(font_statusBar)
		self.Centre(True) 
		self.Show(True)

		self.pageAp()
		self.pageOutput()

	def ShowStatusBar(self, w_msg, colour):
		self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText(w_msg)

	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, wx.RED)

	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, wx.GREEN)

	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK) 

	def ShowStatusBarYELLOW(self, w_msg):
		self.ShowStatusBar(w_msg,(255,140,0)) 

	def OnToolHelp(self, event): 
		url = "/usr/share/openplotter-doc/xxx/xxx.html"
		webbrowser.open(url, new=2)

	def OnToolSettings(self, event): 
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	def pageOutput(self):
		self.logger = rt.RichTextCtrl(self.output, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
		self.logger.SetMargins((10,10))

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.logger, 1, wx.EXPAND, 0)
		self.output.SetSizer(sizer)

	def pageAp(self):
		pass

	def OnToolCheck(self, e):
		msg = ''
		msg1 = ''

		wlan_interfaces=['wlan0','wlan1','wlan2','wlan9']
		
		for i in wlan_interfaces:
			network_info = ''
			try:
				network_info = subprocess.check_output(('iw '+i+' info').split()).decode('utf-8')
			except:
				pass
			if 'AP' in network_info: msg1 += _('wifi access point: ')+i
		if msg1 == '': msg1 += _('wifi access point: ')+_('none')
		msg += msg1 + '\n'

		msg1 = ''
		network_info = ''
		try:
			network_info = subprocess.check_output('ifconfig'.split()).decode('utf-8')
		except:
			pass
		net=['wlan0','wlan1','wlan2','wlan9','usb0','br0','eth0','eth1']
		netactiv = [False,False,False,False,False,False,False]

		for i in network_info.split('\n'):
			for j in range(7):
				if net[j] in i: 
					netactiv[j]=True
					if j<3: msg1 += net[j]+' '
		msg += _('wifi client: ') + msg1 + '\n'

		service=['dnsmasq','hostapd','dhcpcd','avahi-daemon']
		servicetxt=['dnsmasq (dhcp-server):\t','hostapd (AP):\t\t\t','dhcpcd:\t\t\t\t\t','avahi-daemon:\t\t\t']

		for j in range(len(service)):
			msg1 = ''
			network_info = ''
			try:
				network_info = subprocess.check_output(('service '+service[j]+' status').split()).decode('utf-8')
			except:
				pass
			for i in network_info.split('\n'):
				if '(running)' in i: msg1 += _('running')
			if msg1 == '': msg1 += _('stopped')
			msg += servicetxt[j] + msg1 + '\n'

		msg1 = ''
		network_info = ''

		for j in range(7):
			if netactiv[j]:
				network_info = subprocess.check_output(('ip addr show '+net[j]).split()).decode('utf-8')
				for i in network_info.split('\n'):
					if 'inet ' in i:
						if not '169.254' in i.split(' ')[5]: 
							msg1 += net[j] + '\t' + i.split(' ')[5][0:-3] + '\n'
				network_info = ''
		msg += _('IP address\n') + msg1 + '\n'

		self.logger.Clear()
		self.logger.WriteText(msg)
		self.notebook.ChangeSelection(1)
		self.logger.ShowPosition(self.logger.GetLastPosition())

	def OnToolDrivers(self, e):
		self.logger.Clear()
		command = ' sudo install-wifi'
		popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
		for line in popen.stdout:
			self.logger.WriteText(line)
			self.ShowStatusBarYELLOW(_('Installing Wifi modules... ')+line)
		self.notebook.ChangeSelection(1)
		self.logger.ShowPosition(self.logger.GetLastPosition())
		self.ShowStatusBarGREEN(_('Done.'))


	def OnToolAddresses(self, e):
		allPorts = ports.Ports()
		usedPorts = allPorts.getUsedPorts()
		ip_hostname = subprocess.check_output(['hostname']).decode('utf-8')[:-1]
		ip_info = subprocess.check_output(['hostname', '-I']).decode('utf-8')
		ips = ip_info.split()
		self.logger.Clear()
		self.logger.BeginTextColour((55, 55, 55))
		for i in usedPorts:
			self.logger.BeginBold()
			self.logger.WriteText(i['description'])
			self.logger.EndBold()
			self.logger.Newline()
			if i['address'] == 'localhost' or i['address'] == '127.0.0.1':
				self.logger.WriteText(i['type']+' '+str(ip_hostname)+'.local:'+i['port'])
				self.logger.Newline()
				for ip in ips:
					if ip[0:7]=='169.254': pass
					elif ':' in ip: pass
					else:
						self.logger.WriteText(i['type']+' '+str(ip)+':'+i['port'])
						self.logger.Newline()
			else: self.logger.WriteText(i['type']+' '+i['address']+':'+i['port'])
		self.logger.EndTextColour()
		self.notebook.ChangeSelection(1)

def main():
	app = wx.App()
	MyFrame().Show()
	app.MainLoop()

if __name__ == '__main__':
	main()
