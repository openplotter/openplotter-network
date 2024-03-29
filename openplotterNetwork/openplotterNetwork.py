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

import wx, os, webbrowser, subprocess, time, sys
import wx.richtext as rt
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import ports
from openplotterSettings import platform
from .version import version

class MyFrame(wx.Frame):
	def __init__(self):
		import pyric.pyw as pyw
		
		self.conf = conf.Conf()
		self.conf_folder = self.conf.conf_folder
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-network',currentLanguage)

		wx.Frame.__init__(self, None, title=_('Network')+' '+version, size=(800,444))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		icon = wx.Icon(self.currentdir+"/data/openplotter-network.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)
		self.CreateStatusBar()
		font_statusBar = self.GetStatusBar().GetFont()
		font_statusBar.SetWeight(wx.BOLD)
		self.GetStatusBar().SetFont(font_statusBar)

		self.toolbar1 = wx.ToolBar(self, style=wx.TB_TEXT)
		toolHelp = self.toolbar1.AddTool(101, _('Help'), wx.Bitmap(self.currentdir+"/data/help.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolHelp, toolHelp)
		if not self.platform.isInstalled('openplotter-doc'): self.toolbar1.EnableTool(101,False)
		toolSettings = self.toolbar1.AddTool(102, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSettings, toolSettings)
		self.toolbar1.AddSeparator()
		toolAddresses = self.toolbar1.AddTool(103, _('Addresses and Ports'), wx.Bitmap(self.currentdir+"/data/ports.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolAddresses, toolAddresses)
		toolCheck = self.toolbar1.AddTool(104, _('Check Network'), wx.Bitmap(self.currentdir+"/data/check.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolCheck, toolCheck)
		self.toolbar1.AddSeparator()
		toolTime = self.toolbar1.AddCheckTool(105, _('NTP server'), wx.Bitmap(self.currentdir+"/data/time.png"))
		self.Bind(wx.EVT_TOOL, self.onToolTime, toolTime)
		if os.path.exists('/etc/chrony/conf.d/openplotter.conf'): self.toolbar1.ToggleTool(105,True)
		else: self.toolbar1.ToggleTool(105,False)

		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.ap = wx.Panel(self.notebook)
		self.client = wx.Panel(self.notebook)
		self.output = wx.Panel(self.notebook)
		self.notebook.AddPage(self.ap, ' '+_('Access Point'))
		self.notebook.AddPage(self.client, ' '+_('Wlan Client'))
		self.notebook.AddPage(self.output, '')
		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/ap.png", wx.BITMAP_TYPE_PNG))
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/wifi.png", wx.BITMAP_TYPE_PNG))
		img2 = self.il.Add(wx.Bitmap(self.currentdir+"/data/output.png", wx.BITMAP_TYPE_PNG))
		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)
		self.notebook.SetPageImage(1, img1)
		self.notebook.SetPageImage(2, img2)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)

		self.pageAp()
		self.pageClient()
		self.pageOutput()
		self.read_wifi_conf()

		maxi = self.conf.get('GENERAL', 'maximize')
		if maxi == '1': self.Maximize()
		
		self.Centre() 

	def ShowStatusBar(self, w_msg, colour):
		self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText(w_msg)

	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, (130,0,0))

	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, (0,130,0))

	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK) 

	def ShowStatusBarYELLOW(self, w_msg):
		self.ShowStatusBar(w_msg,(255,140,0))

	def onTabChange(self, event):
		try:
			self.SetStatusText('')
		except:pass

	def OnToolHelp(self, event): 
		url = "/usr/share/openplotter-doc/network/network_app.html"
		webbrowser.open(url, new=2)

	def OnToolSettings(self, event): 
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	def onToolTime(self,e):
		if self.toolbar1.GetToolState(105):
			try: 
				subprocess.call([self.platform.admin, 'python3', self.currentdir+'/service.py', 'ntp', 'enable'])
				self.ShowStatusBarGREEN(_('NTP server enabled'))
			except Exception as e: ShowStatusBarRED('Error enabling NTP server: '+str(e))
		else:
			try:
				subprocess.call([self.platform.admin, 'python3', self.currentdir+'/service.py', 'ntp', 'disable'])
				self.ShowStatusBarGREEN(_('NTP server disabled'))
			except Exception as e: ShowStatusBarRED('Error disabling NTP server: '+str(e))

	def pageOutput(self):
		self.logger = rt.RichTextCtrl(self.output, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
		self.logger.SetMargins((10,10))

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.logger, 1, wx.EXPAND, 0)
		self.output.SetSizer(sizer)

	def pageAp(self):

		self.rpimodel = 'no raspberry'
		if self.platform.isRPI:
			modelfile = open('/sys/firmware/devicetree/base/model', 'r', 2000)
			self.rpimodel = modelfile.read()
			modelfile.close()
			
		leftbox = wx.StaticBox(self.ap, label=_('Network Mode')+'  '+self.rpimodel)
	
		self.available_ap_device2 = []

		self.wlan_security = wx.CheckBox(self.ap, label=_('activate wlan security (nft filter)'))
		self.wlan_security.Bind(wx.EVT_CHECKBOX, self.on_wlan_security)

		self.ap_device_label = wx.StaticText(self.ap, label=_('AP'))
		self.ap_device = wx.ComboBox(self.ap, choices=self.available_ap_device2, style=wx.CB_READONLY, size=(265, -1))
		self.ap_device.Bind(wx.EVT_COMBOBOX, self.on_ap_device)

		h_ap = wx.BoxSizer(wx.HORIZONTAL)
		h_ap.Add(self.ap_device_label, 0, wx.TOP | wx.BOTTOM, 6)
		h_ap.Add(self.ap_device, 0, wx.LEFT, 5) 
		#h_ap.Add(self.ap_device_label, 0, wx.RIGHT | wx.UP |wx.EXPAND, 10)
		#h_ap.Add(self.ap_device, 0, wx.RIGHT | wx.EXPAND, 10)  
		
		self.ap_5 = wx.CheckBox(self.ap, label=_('5 GHz'))
		self.ap_5.Bind(wx.EVT_CHECKBOX, self.on_ap_5)
		self.bridge = wx.CheckBox(self.ap, label=_('Add Ethernet port to the AP'))
		self.bridge.Bind(wx.EVT_CHECKBOX, self.on_bridge)
		
		h_set = wx.BoxSizer(wx.HORIZONTAL)
		h_set.Add(self.ap_5, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 6)
		h_set.AddSpacer(10)
		h_set.Add(self.bridge, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 6)

		nextButton = wx.Bitmap(self.currentdir+"/data/edit.png", wx.BITMAP_TYPE_ANY)
		self.wifi_button_apply1 = wx.BitmapButton(self.ap, bitmap=nextButton, size=(nextButton.GetWidth()+40, nextButton.GetHeight()+10))
		self.wifi_button_apply1.Bind(wx.EVT_BUTTON, self.on_wifi_apply1)

		h_button0 = wx.BoxSizer(wx.HORIZONTAL)
		h_button0.AddStretchSpacer(1)
		h_button0.Add(self.wifi_button_apply1, 0, wx.ALL | wx.EXPAND, 5)

		v_leftbox = wx.StaticBoxSizer(leftbox, wx.VERTICAL)
		v_leftbox.AddSpacer(10)
		v_leftbox.Add(self.wlan_security, 0, wx.LEFT, 8)	
		v_leftbox.AddSpacer(15)
		v_leftbox.Add(h_ap, 0, wx.LEFT, 10)
		v_leftbox.Add(h_set, 0, wx.LEFT | wx.EXPAND, 8)
		v_leftbox.AddStretchSpacer(1)
		v_leftbox.Add(h_button0, 0, wx.ALL | wx.EXPAND, 5)

		separator_label = wx.StaticText(self.ap, label='->')
		
		leftbox2 = wx.StaticBox(self.ap, label=_('Access Point Settings'))
	
		self.share = wx.CheckBox(self.ap, label=_('share internet'))

		self.ssid = wx.TextCtrl(self.ap, -1, size=(120, -1))
		self.ssid_label = wx.StaticText(self.ap, label=_('SSID \nmaximum 32 characters'))

		h_ssid = wx.BoxSizer(wx.HORIZONTAL)
		h_ssid.Add(self.ssid, 0)
		h_ssid.AddSpacer(5)
		h_ssid.Add(self.ssid_label, 0)

		self.passw = wx.TextCtrl(self.ap, -1, style=wx.TE_PASSWORD, size=(120, -1))
		self.passw_label = wx.StaticText(self.ap, label=_('Password \nminimum 8 characters required'))
		
		h_passw = wx.BoxSizer(wx.HORIZONTAL)
		h_passw.Add(self.passw, 0)
		h_passw.AddSpacer(5)
		h_passw.Add(self.passw_label, 0)
		
		self.wifi_channel_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13','36','40','44','48','149','153','157','161','165']
		self.wifi_channel = wx.ComboBox(self.ap, choices=self.wifi_channel_list, style=wx.CB_READONLY, size=(120, -1))
		self.wifi_channel_label = wx.StaticText(self.ap, label=_('Channel'))

		h_wifi_channel = wx.BoxSizer(wx.HORIZONTAL)
		h_wifi_channel.Add(self.wifi_channel, 0)
		h_wifi_channel.AddSpacer(5)
		h_wifi_channel.Add(self.wifi_channel_label, 0, wx.TOP | wx.BOTTOM, 6)

		okButton = wx.Bitmap(self.currentdir+"/data/ok.png", wx.BITMAP_TYPE_ANY)
		self.wifi_button_apply = wx.BitmapButton(self.ap, bitmap=okButton, size=(okButton.GetWidth()+40, okButton.GetHeight()+10))
		self.wifi_button_apply.Bind(wx.EVT_BUTTON, self.on_wifi_apply2)

		h_button = wx.BoxSizer(wx.HORIZONTAL)
		h_button.AddStretchSpacer(1)
		h_button.Add(self.wifi_button_apply, 0, wx.ALL | wx.EXPAND, 5)

		v_leftbox2 = wx.StaticBoxSizer(leftbox2, wx.VERTICAL)
		v_leftbox2.AddSpacer(10)
		v_leftbox2.Add(self.share, 0, wx.LEFT | wx.EXPAND, 6)
		v_leftbox2.AddSpacer(9)
		v_leftbox2.Add(h_ssid, 0, wx.LEFT | wx.EXPAND, 10)
		v_leftbox2.AddSpacer(5)
		v_leftbox2.Add(h_passw, 0, wx.LEFT | wx.EXPAND, 10)
		v_leftbox2.AddSpacer(5)
		v_leftbox2.Add(h_wifi_channel, 0, wx.LEFT | wx.EXPAND, 10)
		v_leftbox2.AddStretchSpacer(1)
		v_leftbox2.Add(h_button, 0, wx.ALL | wx.EXPAND, 5)
		
		middle = wx.BoxSizer(wx.VERTICAL)
		middle.AddStretchSpacer(1)
		middle.Add(separator_label, 0, wx.EXPAND, 0)
		middle.AddStretchSpacer(1)

		main = wx.BoxSizer(wx.HORIZONTAL)
		main.Add(v_leftbox, 1, wx.ALL | wx.EXPAND, 10)
		main.Add(middle, 0, wx.EXPAND, 0)
		main.Add(v_leftbox2, 1, wx.ALL | wx.EXPAND, 10)
		
		self.ap.SetSizer(main)

	def read_wifi_conf(self):
		self.conf_network = self.conf_folder + '/Network'
		self.AP_aktiv = False
		self.hostapd_interface = ''
		self.hostapd_bridge = ''

		#security/share device ipforward
		i=' '
		try:
			wififile = open(self.conf_network+'/.openplotter/start-ap-managed-wifi.sh', 'r', 2000)
			bak = wififile.read()
			wififile.close()
		except:
			bak=''
		i=self.find_line_split(bak,"share_internet=",1)
		self.share.SetValue(i=="True")
		
		i=self.find_line_split(bak,"nft_public_security=",1)
		self.wlan_security.SetValue(i=="True")

		#read settings from hostapd.conf  GHz, bridge, ssid, password, channel and check if AP is activ
		try:
			wififile = open(self.conf_network+'/hostapd/hostapd.conf', 'r', 2000)
			bak = wififile.read()
			wififile.close()
			self.AP_aktiv = True
		except:
			bak=''
		
		#on AP
		if self.AP_aktiv:
			if len(bak)>0:
				self.find_line_split_set(bak,"wpa_passphrase",self.passw,1)
				self.find_line_split_set(bak,"ssid",self.ssid,1)
				self.hostapd_interface = self.find_line_split(bak,"interface",1)
				if (self.find_line_split(bak,"hw_mode",1))[0:1] == "a":
					self.ap_5.SetValue(True)
					self.wifi_channel_list = ['36','40','44','48','149','153','157','161','165']
				else:
					self.ap_5.SetValue(False)
					self.wifi_channel_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']
				
				self.wifi_channel.Clear()
				for i in self.wifi_channel_list:
					self.wifi_channel.Append(i)
				self.find_line_split_set(bak,"channel",self.wifi_channel,1)
				
				i=bak.find("bridge=br0")
				if i>=0:
					i=bak.find("#bridge=br0")
					if i>=0:
						self.bridge.SetValue(False)
					else:
						self.bridge.SetValue(True)
			self.read_network_interfaces()

			try:
				wififile = open(self.conf_network+'/udev/rules.d/72-wireless.rules', 'r', 2000)
				bak = wififile.read()
				wififile.close()
			except:
				bak=''
			found = False
			if 'brcmfmac' in bak:
				for i in self.available_ap_device:
					if 'on board' == i[2]:
						self.ap_device.SetStringSelection(i[0])
						self.ap_5.Disable()
						if i[3]>=1: self.ap_5.Enable()
						found = True;
			if not found:
				for i in self.available_ap_device:
					if i[1] in bak and len(i[1])>10:
						self.ap_device.SetStringSelection(i[0])
						self.ap_5.Disable()
						if i[3]>=1: self.ap_5.Enable()
						found = True;
			if not found:
				try:
					wififile = open(self.conf_network+'/.openplotter/start1.sh', 'r', 2000)
					bak2 = wififile.read()
					wififile.close()
				except:
					bak2 = ''
				if '__ap' in bak2:
					for i in self.available_ap_device:
						if 'AP and Station' == i[2]:
							self.ap_device.SetStringSelection(i[0])
							self.on_ap_device(0)
							found = True;
			if not found:
				self.ap_device.SetStringSelection(_('none'))
			
			self.on_ap_device()
		
		#on client only
		else:
			self.read_network_interfaces()
			self.ap_device.SetStringSelection(_('none'))
			self.on_ap_device()

	def find_line_split_set(self,data,search,_setvalue,pos):
		_setvalue.SetValue(self.find_line_split_set2(data,search,"=",pos))

	def find_line_split_set2(self,data,search,splitstr,pos):
		i=data.find(search)
		if i>=0:
			j=data[i:].find("\n")
			if j==0:j=data[i:].length
			line = data[i:i+j]
			sline = line.split(splitstr)
			if len(sline)>1:
				return sline[pos]

	def find_line_split(self,data,search,pos):
		i=data.find(search)
		if i>=0:
			j=data[i:].find("\n")
			if j==0:j=data[i:].length
			line = data[i:i+j]
			sline = line.split('=')
			if len(sline)>1:
				return sline[pos]
			else:
				return ""

	def ap_disable1(self):
		self.ap_5.Disable()
		self.bridge.Disable()

	def ap_enable1(self):
		self.ap_5.Enable()
		self.bridge.Enable()

	def ap_disable(self):
		self.share.Disable()
		self.ssid.Disable()
		self.passw.Disable()
		self.wifi_channel.Disable()

	def ap_enable(self):
		self.share.Enable()
		self.ssid.Enable()
		self.passw.Enable()
		self.wifi_channel.Enable()

	def on_wlan_security(self, e=0):
		pass

	def on_ap_device(self, e=0):
		j = self.ap_device.GetValue()
		self.wifi_button_apply1.Enable()
		self.wifi_button_apply.Disable()
		self.ap_disable()
		if _('none') == j: 
			self.ap_disable1()
		else: 
			self.ap_enable1()
		self.ap_5.Disable()
		for i in self.available_ap_device:
			if _('none') == j:
				self.ap_disable()
			if i[0] == j:
				if i[3] >0:
					self.ap_5.Enable()		

	def on_ap_5(self,e):
		self.on_ap_device()

	def on_bridge(self,e):
		self.on_ap_device()

	def on_wifi_apply1(self, e):
		self.ShowStatusBarYELLOW(_('Wait please... '))
		j = self.ap_device.GetValue()
		for i in self.available_ap_device:
			if i[0] == j:
				if self.bridge.GetValue():
					text = 'br0'
				else:
					text = 'no'
				if not i[1]: mac = '0'
				else: mac = i[1]
				text += ' '+i[4]+' '+mac+' '
				if self.ap_5.GetValue():
					text += '5'
				else:
					text += '2.4'
				if i[2] == 'usb':
					text += ' e'
				else:
					text += ' i'
				text += ' '+self.currentdir

				text += ' '
				text2 = text.split()
				if text2[1] ==  "none":
					subprocess.call((self.platform.admin+' bash '+self.currentdir+'/Network/hostname_dot_local.sh n').split())
				else:
					subprocess.call((self.platform.admin+' bash '+self.currentdir+'/Network/hostname_dot_local.sh y').split())
				process = subprocess.call(('bash '+self.currentdir+'/Network/copy_main.sh '+text).split())
				time.sleep(2)
				self.wifi_button_apply1.Disable()
				self.wifi_button_apply.Enable()
				if _('none') == j: self.ap_disable()
				else: self.ap_enable()

		self.AP_aktiv = False
		try:
			wififile = open(self.conf_network+'/hostapd/hostapd.conf', 'r', 2000)
			bak = wififile.read()
			wififile.close()
			self.AP_aktiv = True
		except: bak=''
		if bak:
			if (self.find_line_split(bak,"hw_mode",1))[0:1] == "a":
				self.wifi_channel_list = ['36','40','44','48','149','153','157','161','165']
			else:
				self.wifi_channel_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']
			
			if self.wifi_channel.GetValue() not in self.wifi_channel_list:
				self.wifi_channel.Clear()
				self.wifi_channel.AppendItems(self.wifi_channel_list)
				if '6' in self.wifi_channel_list: self.wifi_channel.SetStringSelection('6')
				if '48' in self.wifi_channel_list: self.wifi_channel.SetStringSelection('48')

		self.ShowStatusBarYELLOW('Edit settings and validate')

	def read_network_interfaces(self):
		import pyric.pyw as pyw
		
		network_info = ''
		try:
			network_info = pyw.interfaces()
		except:
			pass

		type=''
		phy=''
		AP=-1
		GHz=-1
		
		self.available_ap_device = []
		self.available_ap_device.append([_('none'),'',-1,-1,'none'])
		
		for i in pyw.winterfaces():
			if 'wlan' in i:
				try:
					wlan = 'wlan9'  #AP allways on wlan9
					w0 = pyw.getcard(i)
					mac = subprocess.check_output(('cat /sys/class/net/'+i+'/address').split()).decode()[:-1]

					AP = -1
					if 'AP' in pyw.phyinfo(w0)['modes']:AP = 0

					GHz = -1
					if 'a' in pyw.devstds(w0): GHz = 1

					if b'usb' in subprocess.check_output(('ls -l /sys/class/net/'+i).split()):
						type  = 'usb'
						if AP > -1:
								self.available_ap_device.append([mac+' '+type, mac, type, GHz, wlan])
					else:
						type = 'on board'
						do_exist = False
						for j in self.available_ap_device:
							if j[1] == mac: do_exist = True
						if not do_exist:
							self.available_ap_device.append([mac+' '+type, mac, type, GHz, wlan])
				except: pass

		if not ('Raspberry Pi 2' in self.rpimodel) and len(self.available_ap_device) == 2:
			for i in self.available_ap_device:
				if 'on board' == i[2]:
					type = 'AP and Station'
					wlan = 'uap'
					self.available_ap_device.append([i[1]+' '+type, i[1], type, i[3], wlan])

		self.available_ap_device2 = []
		for i in self.available_ap_device:
			self.available_ap_device2.append(i[0])
			
		self.ap_device.Clear()
		for i in self.available_ap_device2:
			self.ap_device.Append(i)
		
	def on_wifi_apply2(self, e):
		share = str(self.share.GetValue())
		security = str(self.wlan_security.GetValue())

		if not self.AP_aktiv:
			share = "False"
		#set start script
		script_file = self.conf_network+'/.openplotter/start-ap-managed-wifi.sh'
		if os.path.isfile(script_file):
			wififile = open(script_file, 'r', 2000)
			lines = wififile.readlines()
			wififile.close()

			wififile = open(script_file, 'w')
			for line in lines:
				if 0<=line.find("share_internet="): line = "share_internet="+share+"\n"
				if 0<=line.find("nft_public_security="): line = "nft_public_security="+security+"\n"
				wififile.write(line)
			wififile.close()


		if self.AP_aktiv:
			
			passw = self.passw.GetValue()
			ssid = self.ssid.GetValue()
			channel = self.wifi_channel.GetValue()
			
			#check length
			if self.AP_aktiv:
				if (len(ssid) > 32 or len(passw) < 8):
					self.ShowStatusBarRED(_('Your SSID must have a maximum of 32 characters and your password a minimum of 8.'))
					return

			#everything checked give warning
			if not self.wifi_apply2_Message(): return

			#set hostapd
			hostapd_file = self.conf_network+'/hostapd/hostapd.conf'
			if os.path.isfile(hostapd_file):
				wififile = open(hostapd_file, 'r', 2000)
				lines = wififile.readlines()
				wififile.close()
				
				wififile = open(hostapd_file, 'w')
				for line in lines:
					if 0<=line.find("wpa_passphrase"): line = "wpa_passphrase="+passw+'\n'
					if 0<=line.find("channel"): line = "channel="+channel+'\n'
					if 0<=line.find("ssid"): 
						sline = line.split('=')
						if sline[0][:4]== "ssid":
							line = "ssid="+ssid+'\n'
					wififile.write(line)
				wififile.close()
			
			#install files
			process = subprocess.call([self.platform.admin, 'bash', self.currentdir+'/Network/install.sh','install', self.currentdir, self.conf.home], cwd = self.conf_network)
			os.system('shutdown -r now')
			
		#on no AP
		else:
			if not self.wifi_apply2_Message(): return
			#set back to default
			process = subprocess.call([self.platform.admin, 'bash', self.currentdir+'/Network/install.sh','uninstall', self.currentdir, self.conf.home], cwd = self.conf_network)
			os.system('shutdown -r now')

	def wifi_apply2_Message(self):
		dlg = wx.MessageDialog(None, _(
			'OpenPlotter will reboot. If something goes wrong and you are on a headless system, you may not be able to reconnect again.\n\nAre you sure?'),
			_('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		if dlg.ShowModal() == wx.ID_YES:
			dlg.Destroy()
			return True
		else:
			dlg.Destroy()
			return False

	def OnToolCheck(self, e):
		self.logger.Clear()
		self.notebook.ChangeSelection(2)

		msg = ''
		msg1 = ''

		wlan_interfaces=['wlan0','wlan1','wlan2','wlan9']
		
		for i in wlan_interfaces:
			network_info = ''
			try:
				network_info = subprocess.check_output(('iw '+i+' info').split()).decode(sys.stdin.encoding)
			except:
				pass
			if 'AP' in network_info: msg1 += _('wifi access point: ')+i
		if msg1 == '': msg1 += _('wifi access point: ')+_('none')
		msg += msg1 + '\n'

		msg1 = ''
		network_info = ''
		try:
			network_info = subprocess.check_output('ifconfig'.split()).decode(sys.stdin.encoding)
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
				network_info = subprocess.check_output(('service '+service[j]+' status').split()).decode(sys.stdin.encoding)
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
				network_info = subprocess.check_output(('ip addr show '+net[j]).split()).decode(sys.stdin.encoding)
				for i in network_info.split('\n'):
					if 'inet ' in i:
						if not '169.254' in i.split(' ')[5]: 
							msg1 += net[j] + '\t' + i.split(' ')[5][0:-3] + '\n'
				network_info = ''
		msg += _('IP address\n') + msg1 + '\n'

		self.logger.WriteText(msg)
		self.logger.ShowPosition(self.logger.GetLastPosition())

	#def OnToolDrivers(self, e):
	#	self.logger.Clear()
	#	self.notebook.ChangeSelection(1)
	#	command = self.platform.admin+' install-wifi'
	#	popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
	#	for line in popen.stdout:
	#		if not 'Warning' in line and not 'WARNING' in line:
	#			self.logger.WriteText(line)
	#			self.ShowStatusBarYELLOW(_('Installing Wifi modules... ')+line)
	#			self.logger.ShowPosition(self.logger.GetLastPosition())
	#	self.ShowStatusBarGREEN(_('Done.'))

	def OnToolAddresses(self, e):
		allPorts = ports.Ports()
		usedPorts = allPorts.getUsedPorts()
		ip_hostname = subprocess.check_output(['hostname']).decode(sys.stdin.encoding)[:-1]
		ip_info = subprocess.check_output(['hostname', '-I']).decode(sys.stdin.encoding)
		ips = ip_info.split()
		self.logger.Clear()
		self.notebook.ChangeSelection(2)
		self.logger.BeginTextColour((55, 55, 55))
		for i in usedPorts:
			self.logger.BeginBold()
			self.logger.WriteText(i['description']+' ('+i['mode']+')')
			self.logger.EndBold()
			self.logger.Newline()
			if i['address'] == 'localhost' or i['address'] == '127.0.0.1':
				self.logger.WriteText(i['type']+' '+str(ip_hostname)+'.local:'+str(i['port']))
				self.logger.Newline()
				for ip in ips:
					if ip[0:7]=='169.254': pass
					elif ':' in ip: pass
					else: 
						self.logger.WriteText(i['type']+' '+str(ip)+':'+str(i['port']))
						self.logger.Newline()
			else: 
				self.logger.WriteText(i['type']+' '+i['address']+':'+str(i['port']))
				self.logger.Newline()
		self.logger.EndTextColour()
		
		conflicts = allPorts.conflicts()
		if conflicts:
			red = ''
			self.logger.BeginTextColour((130, 0, 0))
			for i in conflicts:
				self.logger.Newline()
				self.logger.WriteText(i['description']+' ('+i['mode']+'): '+i['type']+' '+i['address']+':'+i['port'])
			self.logger.EndTextColour()
			self.ShowStatusBarRED(_('There are conflicts between server connections'))
		else: self.ShowStatusBarGREEN(_('No conflicts between server connections'))
		self.logger.ShowPosition(self.logger.GetLastPosition())

	def pageClient(self):
		self.conf_private_ssid_txt = self.conf_folder + '/private_ssid.conf'
		try:
			private_ssid = open(self.conf_private_ssid_txt, 'r', 2000)
			bak = private_ssid.read()
			private_ssid.close()
		except:
			bak = ''
			
		self.private_ssid_list = bak.split('\n')
		self.private_ssid_list.remove('')

		leftbox = wx.StaticBox(self.client, label=_('wlan0 Client'))
	
		self.client_ssid_label = wx.StaticText(self.client, label=_('SSID (Net Name)'))
		self.client_ssid = wx.TextCtrl(self.client, -1, style=wx.TE_READONLY, size=(120, -1))

		self.add_ssid_label = "+"
		self.add_ssid = wx.Button(self.client, -1, "+", size=(120, -1))
		self.add_ssid.Bind(wx.EVT_BUTTON, self.on_add_ssid)

		self.client_bitRate_label = wx.StaticText(self.client, label=_('Bit Rate'))
		self.client_bitRate = wx.TextCtrl(self.client, -1, style=wx.TE_READONLY, size=(120, -1))

		self.client_linkQuality_label = wx.StaticText(self.client, label=_('Link Quality'))
		self.client_linkQuality = wx.TextCtrl(self.client, -1, style=wx.TE_READONLY, size=(120, -1))

		self.client_signalLevel_label = wx.StaticText(self.client, label=_('Signal Level'))
		self.client_signalLevel = wx.TextCtrl(self.client, -1, style=wx.TE_READONLY, size=(120, -1))

		h_ssid = wx.BoxSizer(wx.HORIZONTAL)
		h_ssid.Add(self.client_ssid, 0, wx.LEFT, 5) 
		h_ssid.Add(self.client_ssid_label, 0, wx.ALL, 6)

		h_button = wx.BoxSizer(wx.HORIZONTAL)
		h_button.Add(self.add_ssid, 0, wx.LEFT, 5)
		
		h_bitRate = wx.BoxSizer(wx.HORIZONTAL)
		h_bitRate.Add(self.client_bitRate, 0, wx.LEFT, 5) 
		h_bitRate.Add(self.client_bitRate_label, 0, wx.ALL, 6)
		
		h_linkQuality = wx.BoxSizer(wx.HORIZONTAL)
		h_linkQuality.Add(self.client_linkQuality, 0, wx.LEFT, 5) 
		h_linkQuality.Add(self.client_linkQuality_label, 0, wx.ALL, 6)
		
		h_signalLevel = wx.BoxSizer(wx.HORIZONTAL)
		h_signalLevel.Add(self.client_signalLevel, 0, wx.LEFT, 5) 
		h_signalLevel.Add(self.client_signalLevel_label, 0, wx.ALL, 6)

		v_leftbox = wx.StaticBoxSizer(leftbox, wx.VERTICAL)
		v_leftbox.AddSpacer(10)
		v_leftbox.Add(h_ssid, 0, wx.LEFT, 10)
		v_leftbox.Add(h_button, 0, wx.LEFT, 10)
		v_leftbox.AddSpacer(10)
		v_leftbox.Add(h_bitRate, 0, wx.LEFT, 10)
		v_leftbox.AddSpacer(10)
		v_leftbox.Add(h_linkQuality, 0, wx.LEFT, 10)
		v_leftbox.AddSpacer(10)
		v_leftbox.Add(h_signalLevel, 0, wx.LEFT, 10)
		v_leftbox.AddStretchSpacer(1)

		midbox = wx.StaticBox(self.client, label=_('wlan1 Client'))
	
		self.client_ssid1_label = wx.StaticText(self.client, label=_('SSID (Net Name)'))
		self.client_ssid1 = wx.TextCtrl(self.client, -1, style=wx.TE_READONLY, size=(120, -1))

		self.add_ssid1 = wx.Button(self.client, -1, "+", size=(120, -1))
		self.add_ssid1.Bind(wx.EVT_BUTTON, self.on_add_ssid1)

		self.client_bitRate1_label = wx.StaticText(self.client, label=_('Bit Rate'))
		self.client_bitRate1 = wx.TextCtrl(self.client, -1, style=wx.TE_READONLY, size=(120, -1))

		self.client_linkQuality1_label = wx.StaticText(self.client, label=_('Link Quality'))
		self.client_linkQuality1 = wx.TextCtrl(self.client, -1, style=wx.TE_READONLY, size=(120, -1))

		self.client_signalLevel1_label = wx.StaticText(self.client, label=_('Signal Level'))
		self.client_signalLevel1 = wx.TextCtrl(self.client, -1, style=wx.TE_READONLY, size=(120, -1))

		h_ssid1 = wx.BoxSizer(wx.HORIZONTAL)
		h_ssid1.Add(self.client_ssid1, 0, wx.LEFT, 5) 
		h_ssid1.Add(self.client_ssid1_label, 0, wx.ALL, 6)

		h_button1 = wx.BoxSizer(wx.HORIZONTAL)
		h_button1.Add(self.add_ssid1, 0, wx.LEFT, 5)

		h_bitRate1 = wx.BoxSizer(wx.HORIZONTAL)
		h_bitRate1.Add(self.client_bitRate1, 0, wx.LEFT, 5) 
		h_bitRate1.Add(self.client_bitRate1_label, 0, wx.ALL, 6)
		
		h_linkQuality1 = wx.BoxSizer(wx.HORIZONTAL)
		h_linkQuality1.Add(self.client_linkQuality1, 0, wx.LEFT, 5) 
		h_linkQuality1.Add(self.client_linkQuality1_label, 0, wx.ALL, 6)
		
		h_signalLevel1 = wx.BoxSizer(wx.HORIZONTAL)
		h_signalLevel1.Add(self.client_signalLevel1, 0, wx.LEFT, 5) 
		h_signalLevel1.Add(self.client_signalLevel1_label, 0, wx.ALL, 6)
		
		v_midbox = wx.StaticBoxSizer(midbox, wx.VERTICAL)
		v_midbox.AddSpacer(10)
		v_midbox.Add(h_ssid1, 0, wx.LEFT, 10)
		v_midbox.Add(h_button1, 0, wx.LEFT, 10)
		v_midbox.AddSpacer(10)
		v_midbox.Add(h_bitRate1, 0, wx.LEFT, 10)
		v_midbox.AddSpacer(10)
		v_midbox.Add(h_linkQuality1, 0, wx.LEFT, 10)
		v_midbox.AddSpacer(10)
		v_midbox.Add(h_signalLevel1, 0, wx.LEFT, 10)
		v_midbox.AddStretchSpacer(1)

		rightbox = wx.StaticBox(self.client, label=_('Private Network'))

		self.privateList = wx.ListBox(self.client,-1, choices = self.private_ssid_list, size =(-1,180), style=wx.LB_SINGLE)
		self.Bind(wx.EVT_LISTBOX, self.OnCLICK)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnDCLICK)
	
		self.remove_ssid_label = "-"
		self.remove_ssid = wx.Button(self.client, -1, self.remove_ssid_label)
		self.remove_ssid.Bind(wx.EVT_BUTTON, self.on_remove_ssid)

		self.remove_ssid.Disable()

		h_button2 = wx.BoxSizer(wx.HORIZONTAL)
		h_button2.AddStretchSpacer(1)
		h_button2.Add(self.remove_ssid, 0, wx.ALL | wx.EXPAND, 5)

		v_rightbox = wx.StaticBoxSizer(rightbox, wx.VERTICAL)
		v_rightbox.AddSpacer(10)
		v_rightbox.Add(self.privateList, 0, wx.ALL | wx.EXPAND, 5)
		v_rightbox.AddStretchSpacer(1)
		v_rightbox.Add(h_button2, 0, wx.ALL | wx.EXPAND, 5)
		
		main = wx.BoxSizer(wx.HORIZONTAL)
		main.Add(v_leftbox, 1, wx.ALL | wx.EXPAND, 10)
		main.Add(v_midbox, 1, wx.ALL | wx.EXPAND, 10)
		main.Add(v_rightbox, 1, wx.ALL | wx.EXPAND, 10)
		
		self.client.SetSizer(main)
		self.read_wlan()
		#self.privateList.SetSelection(0)

	def read_wlan(self):
		try:
			network_info = subprocess.check_output('ip addr'.split()).decode(sys.stdin.encoding)
		except:
			pass
		net=['wlan0','wlan1']

		self.client_ssid.SetValue('----')
		self.client_bitRate.SetValue('----')
		self.client_linkQuality.SetValue('----')
		self.client_signalLevel.SetValue('----')
		self.add_ssid.Disable()

		self.client_ssid1.SetValue('----')
		self.client_bitRate1.SetValue('----')
		self.client_linkQuality1.SetValue('----')
		self.client_signalLevel1.SetValue('----')
		self.add_ssid1.Disable()
		
		for i in network_info.split('\n'):
			if net[0] in i:
				wlan_info = subprocess.check_output('iwconfig wlan0'.split()).decode(sys.stdin.encoding)
				try:
					if len(self.find_line_split_set2(wlan_info,"ESSID",":",1).split('"'))>1: 
						self.client_ssid.SetValue(self.find_line_split_set2(wlan_info,"ESSID",":",1).split('"')[1])
						try: self.client_bitRate.SetValue(self.find_line_split_set2(wlan_info,"Rate","=",1).split("   ")[0])
						except: pass
						try: self.client_linkQuality.SetValue(self.find_line_split_set2(wlan_info,"Quality","=",1).split(" ")[0])
						except: pass
						try: self.client_signalLevel.SetValue(self.find_line_split_set2(wlan_info,"level","=",1))
						except: pass
						self.add_ssid.Enable()
				except: pass

			if net[1] in i: 
				wlan_info = subprocess.check_output('iwconfig wlan1'.split()).decode(sys.stdin.encoding)
				try:
					if len(self.find_line_split_set2(wlan_info,"ESSID",":",1).split('"'))>1: 
						self.client_ssid1.SetValue(self.find_line_split_set2(wlan_info,"ESSID",":",1).split('"')[1])
						try: self.client_bitRate1.SetValue(self.find_line_split_set2(wlan_info,"Rate","=",1).split("   ")[0])
						except: pass
						try: self.client_linkQuality1.SetValue(self.find_line_split_set2(wlan_info,"Quality","=",1).split(" ")[0])
						except: pass
						try: self.client_signalLevel1.SetValue(self.find_line_split_set2(wlan_info,"level","=",1))
						except: pass
						self.add_ssid1.SetLabel = "Hallo"
						self.add_ssid1.Enable()
				except: pass

		self.conf_private_ssid_txt = self.conf_folder + '/private_ssid.conf'
		try:
			private_ssid = open(self.conf_private_ssid_txt, 'r', 2000)
			bak = private_ssid.read()
			private_ssid.close()
		except:
			bak = ''
			
		self.private_ssid_list = bak.split('\n')
		self.private_ssid_list.remove('')

		self.privateList.Set(self.private_ssid_list)
		
	def set_nft(self):
		cwd1 = os.getcwd()
		os.chdir(self.conf.home+'/.openplotter')
		process = subprocess.call([self.platform.admin, 'bash', self.conf.home+'/.openplotter/wpa_cli_script.sh','none','CONNECTED'],cwd = self.conf.home+'/.openplotter')
		os.chdir(cwd1)		
		
	def on_add_ssid(self, event):
		self.appendName(self.client_ssid.GetValue())
		self.set_nft()

	def on_add_ssid1(self, event):
		self.appendName(self.client_ssid1.GetValue())
		self.set_nft()

	def on_remove_ssid(self, event):
		if self.privateList.GetSelection() == -1:
			return
		self.private_ssid_list.remove(self.private_ssid_list[self.privateList.GetSelection()])
		try:
			private_ssid = open(self.conf_private_ssid_txt, 'w')
			for i in self.private_ssid_list:
				if i != '':
					private_ssid.write(i + '\n')
			private_ssid.close()
		except:
			pass
		self.read_wlan()
		self.remove_ssid.Disable()
		self.set_nft()

	def OnCLICK(self, event):
		if self.privateList.GetSelection() != -1:
			self.remove_ssid.Enable()

	def OnDCLICK(self, event):
		if self.privateList.GetSelection() != -1:
			self.privateList.Deselect(self.privateList.GetSelection())
			self.remove_ssid.Disable()			
		
	def appendName(self,name):
		try:
			private_ssid = open(self.conf_private_ssid_txt, 'a')
			private_ssid.write(name + '\n')
			private_ssid.close()
		except:
			pass
		self.read_wlan()

def main():
	try:
		platform2 = platform.Platform()
		if not platform2.postInstall(version,'network'):
			subprocess.Popen(['openplotterPostInstall', platform2.admin+' networkPostInstall'])
			return
	except: pass

	app = wx.App()
	MyFrame().Show()
	time.sleep(1)
	app.MainLoop()

if __name__ == '__main__':
	main()
