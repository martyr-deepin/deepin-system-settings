#!/usr/bin/env python
#-*- coding:utf-8 -*-
# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Zeng Zhi
# 
# Author:     Zeng Zhi <zengzhilg@gmail.com>
# Maintainer: Zeng Zhi <zengzhilg@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from theme import app_theme
from dtk.ui.tab_window import TabBox
from dtk.ui.label import Label

import gtk

class Tabs(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)

        tab_window = TabBox()
        items = [("IPv4设置", WirelessConf()), ("IPv6设置", gtk.Button("asfsd")), ("802.1x安全性", gtk.Button("sad")), ("MAC地址克隆", gtk.Button("asdsadsa"))]
        tab_window.add_items(items)

        self.add(tab_window)

class WirelessConf(gtk.Table):

    def __init__(self):
        
        gtk.Table.__init__(self, 9, 2 , False)
        # Ip configuration
        auto_ip = gtk.RadioButton(None, "自动获得IP地址")
        self.attach(auto_ip, 0,1,0,1,)
        
        manual_ip = gtk.RadioButton(auto_ip, "手动添加IP地址")
        self.attach(manual_ip, 0,1,1,2)

        addr_label = Label("IP地址:")
        self.attach(addr_label, 0,1,2,3)
        addr_entry = gtk.Entry()
        self.attach(addr_entry, 1,2,2,3)

        mask_label = Label("子网掩码:")
        self.attach(mask_label, 0,1,3,4)
        mask_entry = gtk.Entry()
        self.attach(mask_entry, 1,2,3,4)
        
        gate_label = Label("默认网关")
        self.attach(gate_label, 0,1,4,5)
        gate_entry = gtk.Entry()
        self.attach(gate_entry, 1,2,4,5)
        
        #DNS configuration
        auto_dns = gtk.RadioButton(None, "自动获得DNS服务器地址")
        manual_dns = gtk.RadioButton(auto_dns,"使用下面的dns服务器")
        self.attach(auto_dns, 0, 1, 5, 6) 


if __name__=="__main__":
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_title("sadfsdf")
    win.set_size_request(770,500)
    #win.border_width(2)
    win.connect("destroy", lambda w: gtk.main_quit())
    tab = Tabs() 

    win.add(tab)
    win.show_all()

    gtk.main()


