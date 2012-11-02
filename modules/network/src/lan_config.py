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
from dtk.ui.button import Button,ToggleButton, RadioButton, CheckButton
from dtk.ui.entry import InputEntry, TextEntry
from dtk.ui.label import Label
from dtk.ui.spin import SpinBox
from dtk.ui.utils import container_remove_all
#from dtk.ui.droplist import Droplist
from dtk.ui.combo import ComboBox
from wired import *
from widgets import SettingButton
from nmlib.nm_utils import TypeConvert
import gtk

from nmutils.nmsetting_802_1x import NMSetting8021x
active_connection = wired_device.get_active_connection()
if active_connection:
    active = active_connection.get_connection()
else: 
    active =None

class WiredSetting(gtk.HBox):

    def __init__(self, slide_back_cb, change_crumb_cb):
        gtk.HBox.__init__(self)
        self.slide_back_cb = slide_back_cb
        self.change_crumb = change_crumb_cb
        #self.tab_window.set_size_request(585,-1)

        self.tab_window = TabBox()
        if active == None:
            self.ipv4 = NoSetting()
            self.ipv6 = NoSetting()
            #self.security = NoSetting()
            self.wired = NoSetting()
        else:
            self.ipv4 = IPV4Conf(active)
            self.ipv6 = IPV6Conf(active)
            #self.security = Security(active)
            self.wired = Wired(active)

        self.items = [("有线", self.wired),
                      ("IPv4设置", self.ipv4),
                      ("IPv6设置", self.ipv6),
                      ("802.1x安全性", NoSetting())]
        self.tab_window.add_items(self.items)
        self.sidebar = None

        self.init_connection()
        self.sidebar = Sidebar(self.cons, 
                               self.ipv4_setting,
                               self.ipv6_setting,
                               self.wired_setting ,
                               self.init_connection,
                               self.global_setting_callback)
        self.pack_start(self.sidebar, False ,False)

        vbox = gtk.VBox()
        vbox.connect("expose-event", self.expose_event)
        vbox.pack_start(self.tab_window ,True, True)
        self.pack_start(vbox, True, True)

        ## reformate apply and cancel
        aligns = gtk.Alignment(0.5,1,0,0)
        hbox = gtk.HBox()
        self.apply_button = gtk.Button("Apply")
        self.cancel_button = gtk.Button("Cancel")
        self.cancel_button.connect("clicked", self.cancel_changes)
        self.apply_button.connect("clicked", self.save_changes)
        #hbox.pack_start(self.cancel_button, False, False, 0)
        hbox.pack_start(self.apply_button, False, False, 0)
        aligns.add(hbox)
        vbox.pack_start(aligns, False , False)
        hbox.connect("expose-event", self.expose_event)

    def init_connection(self):
        self.cons = nm_remote_settings.get_wired_connections()
        if not self.cons:
            nm_remote_settings.new_wired_connection()
            self.cons = nm_remote_settings.get_wired_connections()
        self.ipv4_setting = [IPV4Conf(conn) for conn in self.cons]
        self.ipv6_setting = [IPV6Conf(conn) for conn in self.cons]
        #self.security_setting = [Security(conn) for conn in self.cons]
        self.wired_setting = [Wired(conn) for conn in self.cons]

        if not self.sidebar == None:
            self.sidebar.cons = self.cons
            self.sidebar.ipv4_setting = self.ipv4_setting
            self.sidebar.ipv6_setting = self.ipv6_setting
            self.sidebar.wired_setting = self.wired_setting

    def cancel_changes(self, widget):
        self.slide_back_cb()
        
    def save_changes(self, widget):
        self.ipv4.save_changes()
        self.ipv6.save_changes()

        #self.slide.slide_to_page(self.slide.layout.get_children()[0], "left")
        self.change_crumb()
        self.slide_back_cb()
        

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb( 1, 1, 1) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

    def global_setting_callback(self, connection):
        index = self.cons.index(connection)
        self.ipv4 = self.ipv4_setting[index]
        self.tab_window.tab_items[1] = ("IPv4设置",self.ipv4)

        self.ipv6 = self.ipv6_setting[index]
        self.tab_window.tab_items[2] = ("IPv6设置",self.ipv6)

        #self.security = self.sidebar.security_setting[index]
        #self.tab_window.tab_items[2] = ("802.1x安全性", self.security)

        self.wired = self.wired_setting[index]
        self.tab_window.tab_items[0] = ("有线", self.wired)

        tab_index = self.tab_window.tab_index
        self.tab_window.tab_index = -1
        self.tab_window.switch_content(tab_index)
        self.queue_draw()


class Sidebar(gtk.VBox):

    def __init__(self, cons, ipv4, ipv6, wired, init_cb, sidebar_callback):
        gtk.VBox.__init__(self, False, 5)
        self.cons = cons
        self.ipv4_setting = ipv4
        self.ipv6_setting = ipv6
        self.wired_setting = wired
        self.init_cb = init_cb
        self.sidebar_callback = sidebar_callback
        self.set_size_request(160, -1)

        # determin the active one
        self.buttonbox = gtk.VBox(False, 6)
        self.pack_start(self.buttonbox, False, False)
        self.refresh()
        add_button = Button("Add setting")
        add_button.connect("clicked", self.add_new_setting)
        self.pack_start(add_button, False, False, 6)

    def refresh(self):
        
        btn = SettingButton(None, self.cons[0], self.ipv4_setting[0], self.sidebar_callback)
        #btn.set_size(160)
        self.buttonbox.pack_start(btn, False, False,6)

        active_connection = wired_device.get_active_connection()
        if active_connection:
            active = active_connection.get_connection()
        for index,c in enumerate(self.cons[1:]):
            button = SettingButton(btn, c, self.ipv4_setting[index + 1], self.sidebar_callback)
            #button.set_size(160)
            self.buttonbox.pack_start(button, False ,False, 6)

        for index, c in enumerate(self.cons):
            if active !=None and c.get_setting("connection").id == active.get_setting("connection").id:
                self.buttonbox.get_children()[index].check.set_active(True)


    def add_new_setting(self, widget):
        nm_remote_settings.new_wired_connection()
        container_remove_all(self.buttonbox)
        self.init_cb()
        self.refresh()

        
class NoSetting(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)

        label_align = gtk.Alignment(0.5,0.5,0,0)

        label = Label("No active connection")
        label_align.add(label)
        self.add(label_align)


class IPV4Conf(gtk.VBox):

    def __init__(self, connection = None):
        
        gtk.VBox.__init__(self)
        self.connection = connection 
        table = gtk.Table(9, 2 , False)
        # Ip configuration
        self.auto_ip = gtk.RadioButton(None, "自动获得IP地址")
        table.attach(self.auto_ip, 0,1,0,1,)
        self.manual_ip = gtk.RadioButton(self.auto_ip, "手动添加IP地址")
        table.attach(self.manual_ip, 0,1,1,2)

        addr_label = Label("IP地址:")
        table.attach(addr_label, 0,1,2,3)
        self.addr_entry = gtk.Entry()
        #self.addr_entry.set_size(30, 25)
        self.addr_entry.connect("activate", self.check_ip_valid)
        self.addr_entry.set_sensitive(False)
        table.attach(self.addr_entry, 1,2,2,3)

        mask_label = Label("子网掩码:")
        table.attach(mask_label, 0,1,3,4)
        self.mask_entry = gtk.Entry()
        #self.mask_entry.set_size(30, 25)
        self.mask_entry.connect("activate", self.check_mask_valid)
        table.attach(self.mask_entry, 1,2,3,4)
        
        gate_label = Label("默认网关")
        table.attach(gate_label, 0,1,4,5)
        self.gate_entry = gtk.Entry()
        #self.gate_entry.set_size(30, 25)
        self.gate_entry.connect("activate", self.check_gate_valid)
        table.attach(self.gate_entry, 1,2,4,5)
        
        #DNS configuration
        self.auto_dns = gtk.RadioButton(None, "自动获得DNS服务器地址")
        self.manual_dns = gtk.RadioButton(self.auto_dns,"使用下面的dns服务器:")
        table.attach(self.auto_dns, 0, 1, 5, 6) 
        table.attach(self.manual_dns, 0, 1, 6, 7)

        master_dns = Label("首选DNS服务器地址:")
        slave_dns = Label("使用下面的DNS服务器地址:")
        self.master_entry = gtk.Entry()
        self.slave_entry = gtk.Entry()
        #self.master_entry.set_size(30, 25)
        #self.slave_entry.set_size(30, 25)
        self.master_entry.connect("activate", self.check_dns_valid)
        self.slave_entry.connect("activate", self.check_dns_valid)
        
        table.attach(master_dns, 0, 1, 7, 8)
        table.attach(self.master_entry, 1, 2, 7, 8)
        table.attach(slave_dns, 0, 1, 8, 9)
        table.attach(self.slave_entry, 1, 2, 8, 9)

        align = gtk.Alignment(0.5,0.5,0.5,0.5)
        align.add(table)
        self.add(align)
        
        #aligns = gtk.Alignment(0.5,0.5,0,0)
        #hbox = gtk.HBox()
        #self.apply_button = gtk.Button("Apply")
        self.show_all()
        #self.cancel_button = gtk.Button("Cancel")
        #hbox.pack_start(self.cancel_button, False, False, 0)
        #hbox.pack_start(self.apply_button, False, False, 0)
        #aligns.add(hbox)
        #self.add(aligns)
        
        
        self.cs =None
        self.reset(connection)
        self.manual_ip.connect("toggled", self.manual_ip_entry, self.cs)
        self.auto_ip.connect("toggled", self.auto_get_ip_addr, self.cs)
        self.auto_dns.connect("toggled", self.auto_dns_set, self.cs)
        self.manual_dns.connect("toggled", self.manual_dns_set, self.cs)
        #self.apply_button.connect("clicked", self.save_changes, self.cs)
        #self.cancel_button.connect("clicked", self.cancel_changes)

    def check_ip_valid(self, widget ):
        text = widget.get_text()
        if TypeConvert.is_valid_ip4(text):
            print "valid"
        else:
            print "invalid"

    def check_mask_valid(self, widget):
        text = widget.get_text()
        if TypeConvert.is_valid_netmask(text):
            print "valid"
        else:
            print "invalid"


    def check_gate_valid(self, widget):
        text = widget.get_text()
        if TypeConvert.is_valid_gw(self.addr_entry.get_text(),
                                   self.mask_entry.get_text(),
                                   text):
            print "valid"
        else:
            print "invalid"
        

    def check_dns_valid(self, widget):
        text = widget.get_text()
        if TypeConvert.is_valid_ip4(text):
            print "valid"
        else:
            print "invalid"


    def reset(self, connection):
        self.cs = connection.get_setting("ipv4")       
        self.clear_entry()
        #print self.cs.dns
        #print self.cs.method, connection.get_setting("connection").id
        if self.cs.method == "auto":
            self.auto_ip.set_active(True)
            self.addr_entry.set_sensitive(False)
            self.mask_entry.set_sensitive(False)
            self.gate_entry.set_sensitive(False)
            
        else:
            self.manual_ip.set_active(True)
            self.addr_entry.set_sensitive(True)
            self.mask_entry.set_sensitive(True)
            self.gate_entry.set_sensitive(True)
            if not self.cs.addresses == []:
                self.addr_entry.set_text(self.cs.addresses[0][0])
                self.mask_entry.set_text(self.cs.addresses[0][1])
                self.gate_entry.set_text(self.cs.addresses[0][2])

        if self.cs.dns == []:
            self.auto_dns.set_active(True)
            self.master_entry.set_sensitive(False)
            self.slave_entry.set_sensitive(False)
        else:
            self.manual_dns.set_active(True)
            self.master_entry.set_sensitive(True)
            self.slave_entry.set_sensitive(True)
            if len(self.cs.dns) > 1:
                self.slave_entry.set_text(self.cs.dns[1])
            self.master_entry.set_text(self.cs.dns[0])


    def auto_dns_set(self, widget, connection):
        if widget.get_active():
            connection.clear_dns()
            self.master_entry.set_sensitive(False)
            self.slave_entry.set_sensitive(False)

    def manual_dns_set(self, widget, connection):
        if widget.get_active():
            self.master_entry.set_sensitive(True)
            self.slave_entry.set_sensitive(True)
            if len(connection.dns) == 1:
                self.master_entry.set_text(connection.dns[0])
            elif len(connection.dns) > 1:
                self.slave_entry.set_text(connection.dns[1])

    def clear_entry(self):
        self.addr_entry.set_text("")
        self.mask_entry.set_text("")
        self.gate_entry.set_text("")
        self.master_entry.set_text("")
        self.slave_entry.set_text("")

    def auto_get_ip_addr(self, widget, connection):
        if widget.get_active():
            connection.method = 'auto'
            self.addr_entry.set_sensitive(False)
            self.mask_entry.set_sensitive(False)
            self.gate_entry.set_sensitive(False)
    def manual_ip_entry(self,widget, connection):
        if widget.get_active():
            connection.method = 'manual'
            self.addr_entry.set_sensitive(True)
            self.mask_entry.set_sensitive(True)
            self.gate_entry.set_sensitive(True)
            if not connection.addresses == []:
                self.addr_entry.set_text(connection.addresses[0][0])
                self.mask_entry.set_text(connection.addresses[0][1])
                self.gate_entry.set_text(connection.addresses[0][2])
    
    def save_changes(self):
        connection = self.cs
        if connection.method =="manual": 
            connection.clear_addresses()
            connection.add_address([self.addr_entry.get_text(),
                                     self.mask_entry.get_text(),
                                     self.gate_entry.get_text()])
            connection.clear_dns()
            if not self.master_entry.get_text() == "":
                connection.add_dns(self.master_entry.get_text())
            if not self.slave_entry.get_text() == "":
                connection.add_dns(self.slave_entry.get_text())
        connection.adapt_ip4config_commit()
        self.connection.update()

class IPV6Conf(gtk.VBox):

    def __init__(self, connection = None):
        
        gtk.VBox.__init__(self)
        self.connection = connection 
        table = gtk.Table(9, 2 , False)
        # Ip configuration
        self.auto_ip = gtk.RadioButton(None, "自动获得IP地址")
        table.attach(self.auto_ip, 0,1,0,1,)
        self.manual_ip = gtk.RadioButton(self.auto_ip, "手动添加IP地址")
        table.attach(self.manual_ip, 0,1,1,2)

        addr_label = Label("IP地址:")
        table.attach(addr_label, 0,1,2,3)
        self.addr_entry = gtk.Entry()
        #self.addr_entry.set_size(30, 25)
        self.addr_entry.connect("activate", self.check_ip_valid)
        self.addr_entry.set_sensitive(False)
        table.attach(self.addr_entry, 1,2,2,3)

        mask_label = Label("前缀:")
        table.attach(mask_label, 0,1,3,4)
        self.mask_entry = gtk.Entry()
        #self.mask_entry.set_size(30, 25)
        self.mask_entry.connect("activate", self.check_mask_valid)
        table.attach(self.mask_entry, 1,2,3,4)
        
        gate_label = Label("默认网关")
        table.attach(gate_label, 0,1,4,5)
        self.gate_entry = gtk.Entry()
        #self.gate_entry.set_size(30, 25)
        self.gate_entry.connect("activate", self.check_gate_valid)
        table.attach(self.gate_entry, 1,2,4,5)
        
        #DNS configuration
        self.auto_dns = gtk.RadioButton(None, "自动获得DNS服务器地址")
        self.manual_dns = gtk.RadioButton(self.auto_dns,"使用下面的dns服务器:")
        table.attach(self.auto_dns, 0, 1, 5, 6) 
        table.attach(self.manual_dns, 0, 1, 6, 7)

        master_dns = Label("首选DNS服务器地址:")
        slave_dns = Label("使用下面的DNS服务器地址:")
        self.master_entry = gtk.Entry()
        self.slave_entry = gtk.Entry()
        #self.master_entry.set_size(30, 25)
        #self.slave_entry.set_size(30, 25)
        self.master_entry.connect("activate", self.check_dns_valid)
        self.slave_entry.connect("activate", self.check_dns_valid)
        
        table.attach(master_dns, 0, 1, 7, 8)
        table.attach(self.master_entry, 1, 2, 7, 8)
        table.attach(slave_dns, 0, 1, 8, 9)
        table.attach(self.slave_entry, 1, 2, 8, 9)

        align = gtk.Alignment(0.5,0.5,0.5,0.5)
        align.add(table)
        self.add(align)
        
        #aligns = gtk.Alignment(0.5,0.5,0,0)
        #hbox = gtk.HBox()
        #self.apply_button = gtk.Button("Apply")
        #self.cancel_button = gtk.Button("Cancel")
        #hbox.pack_start(self.cancel_button, False, False, 0)
        #hbox.pack_start(self.apply_button, False, False, 0)
        #aligns.add(hbox)
        #self.add(aligns)
        
        
        self.cs =None
        self.reset(connection)
        self.manual_ip.connect("toggled", self.manual_ip_entry, self.cs)
        self.auto_ip.connect("toggled", self.auto_get_ip_addr, self.cs)
        self.auto_dns.connect("toggled", self.auto_dns_set, self.cs)
        self.manual_dns.connect("toggled", self.manual_dns_set, self.cs)
        #self.apply_button.connect("clicked", self.save_changes, self.cs)
        #self.cancel_button.connect("clicked", self.cancel_changes)

    def check_ip_valid(self, widget):
        text = widget.get_text()
        if TypeConvert.is_valid_ip6(text):
            print "valid"
        else:
            print "invalid"

    def check_mask_valid(self, widget):
        text = widget.get_text()
        if TypeConvert.is_valid_netmask(text):
            print "valid"
        else:
            print "invalid"


    def check_gate_valid(self, widget):
        text = widget.get_text()
        if TypeConvert.is_valid_gw(text):
            print "valid"
        else:
            print "invalid"
        

    def check_dns_valid(self, widget):
        text = widget.get_text()
        if TypeConvert.is_valid_ip4(text):
            print "valid"
        else:
            print "invalid"


    def reset(self, connection):
        self.cs = connection.get_setting("ipv6")       
        self.clear_entry()
        #print connection.get_setting("connection").id,self.cs.method
        #print self.cs.method, connection.get_setting("connection").ssid
        #print "###########" + connection.get_setting("connection").id
        #print connection.settings_dict
        if self.cs.method == "auto":
            self.auto_ip.set_active(True)
            self.addr_entry.set_sensitive(False)
            self.mask_entry.set_sensitive(False)
            self.gate_entry.set_sensitive(False)
            
        else:
            self.manual_ip.set_active(True)
            self.addr_entry.set_sensitive(True)
            self.mask_entry.set_sensitive(True)
            self.gate_entry.set_sensitive(True)
            if not self.cs.addresses == []:
                self.addr_entry.set_text(self.cs.addresses[0][0])
                self.mask_entry.set_text(self.cs.addresses[0][1])
                self.gate_entry.set_text(self.cs.addresses[0][2])

        if self.cs.dns == []:
            self.auto_dns.set_active(True)
            self.master_entry.set_sensitive(False)
            self.slave_entry.set_sensitive(False)
        else:
            self.manual_dns.set_active(True)
            self.master_entry.set_sensitive(True)
            self.slave_entry.set_sensitive(True)
            if len(self.cs.dns) > 1:
                self.slave_entry.set_text(self.cs.dns[1])
            self.master_entry.set_text(self.cs.dns[0])


    def auto_dns_set(self, widget, connection):
        if widget.get_active():
            connection.clear_dns()
            self.master_entry.set_sensitive(False)
            self.slave_entry.set_sensitive(False)

    def manual_dns_set(self, widget, connection):
        if widget.get_active():
            self.master_entry.set_sensitive(True)
            self.slave_entry.set_sensitive(True)
            if len(connection.dns) == 1:
                self.master_entry.set_text(connection.dns[0])
            elif len(connection.dns) > 1:
                self.slave_entry.set_text(connection.dns[1])

    def clear_entry(self):
        self.addr_entry.set_text("")
        self.mask_entry.set_text("")
        self.gate_entry.set_text("")
        self.master_entry.set_text("")
        self.slave_entry.set_text("")

    def auto_get_ip_addr(self, widget, connection):
        if widget.get_active():
            connection.method = 'auto'
            self.addr_entry.set_sensitive(False)
            self.mask_entry.set_sensitive(False)
            self.gate_entry.set_sensitive(False)
    def manual_ip_entry(self,widget, connection):
        if widget.get_active():
            connection.method = 'manual'
            self.addr_entry.set_sensitive(True)
            self.mask_entry.set_sensitive(True)
            self.gate_entry.set_sensitive(True)
            if not connection.addresses == []:
                self.addr_entry.set_text(connection.addresses[0][0])
                self.mask_entry.set_text(connection.addresses[0][1])
                self.gate_entry.set_text(connection.addresses[0][2])
    
    def save_changes(self):
        connection = self.cs
        if connection.method =="manual": 
            connection.clear_addresses()

            print self.addr_entry.get_text()

            connection.add_address([self.addr_entry.get_text(),
                                     self.mask_entry.get_text(),
                                     self.gate_entry.get_text()])
            connection.clear_dns()
            if not self.master_entry.get_text() == "":
                connection.add_dns(self.master_entry.get_text())
            if not self.slave_entry.get_text() == "":
                connection.add_dns(self.slave_entry.get_text())

        print "connection address:"        
        print connection.addresses
        connection.adapt_ip6config_commit()
        #print self.connection.get_setting("connection").id
        self.connection.update()

#class Security(gtk.VBox):

    #def __init__(self, connection):
        #gtk.VBox.__init__(self)
        ##xs = NMSetting8021x(connection)
        #check_button = CheckButton("Use 802.1x security for this connection")
        #check_align = gtk.Alignment(0, 0.1, 0, 0)
        #auth_align = gtk.Alignment(0, 0.1, 0, 0)
        #check_align.add(check_button)
        
        ##auth = ComboBox([("MD5", None),
                         ##("TLS", None),
                         ##("Fast", None),
                         ##("Tunneled TLS", None),
                         ##("PEAP", None)])

        ##TODO need change it to deepin-ui ComboBox, the menu in ComboBox doesnt looks correct

        #auth = gtk.combo_box_new_text()
        #s_list = ["MD5", "TLS", "FAST", "Tunneled TLS", "PEAP"]
        #for l in s_list:
            #auth.append_text(l)

        #auth_align.add(auth)
        #auth_align.set_padding(0,0,10,0)

        #self.pack_start(check_align, False, False)
        #self.pack_start(auth_align, False, False)

class Wired(gtk.VBox):

    def __init__(self, connection):
        gtk.VBox.__init__(self)
        
        ethernet = connection.get_setting("802-3-ethernet")

        table = gtk.Table(3, 2, False)
        
        mac_address = Label("Device Mac address:")
        table.attach(mac_address, 0, 1, 0, 1)

        mac_entry = gtk.Entry()
        table.attach(mac_entry, 1, 2, 0, 1)

        clone_addr = Label("Cloned Mac Adrress:")
        table.attach(clone_addr, 0, 1, 1, 2)
        clone_entry = gtk.Entry()
        table.attach(clone_entry, 1,2, 1, 2)

        mtu = Label("MTU:")
        table.attach(mtu, 0,1,2,3)
        mtu_spin = SpinBox(0,0, 1500, 1, 55)
        table.attach(mtu_spin, 1,2,2,3)
        
        align = gtk.Alignment(0.5, 0.5, 0, 0)
        align.add(table)
        self.add(align)

        ## retrieve wired info
        (mac, clone_mac, mtu) = ethernet.mac_address, ethernet.cloned_mac_address, ethernet.mtu
        #print mac, clone_mac, mtu
        if mac != None:
            mac_entry.set_text(mac)
        if clone_mac !=None:
            clone_entry.set_text(clone_mac)
        if mtu != None:
            mtu_spin.set_value(int(mtu))

    
#if __name__=="__main__":
    #win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    #win.set_title("sadfsdf")
    #win.set_size_request(770,500)
    #win.border_width(2)
    #win.connect("destroy", lambda w: gtk.main_quit())
    #tab = WiredSetting(slide) 
    
    #win.add(tab)
    #win.show_all()

    #gtk.main()
