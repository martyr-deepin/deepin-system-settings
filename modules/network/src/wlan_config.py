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
from dtk.ui.new_entry import InputEntry
from dtk.ui.label import Label
from dtk.ui.spin import SpinBox
from dtk.ui.utils import container_remove_all
#from dtk.ui.droplist import Droplist
from dtk.ui.combo import ComboBox
from nm_modules import nm_module
from nmlib.nmcache import cache
from widgets import SettingButton
import gtk

# NM lib import 
from nmlib.nm_utils import TypeConvert
#from nmlib.nmclient import nmclient
#from nmlib.nm_remote_settings import nm_remote_settings

class WirelessSetting(gtk.HBox):

    def __init__(self, access_point, slide_back_cb, change_crumb_cb):

        gtk.HBox.__init__(self)
        self.access_point = access_point
        self.slide_back = slide_back_cb
        self.change_crumb = change_crumb_cb

        self.wireless = None
        self.ipv4 = None
        self.ipv6 = None
        self.security = None

        self.tab_window = TabBox(dockfill = True)
        self.tab_window.set_size_request(674, 408)
        self.items = [("Wireless", NoSetting()),
                      ("IPV4", NoSetting()),
                      ("IPv6", NoSetting()),
                      ("Security", NoSetting())]
        self.tab_window.add_items(self.items)

        self.sidebar = SideBar( None,self.init, self.check_click)

        # Build ui
        self.pack_start(self.sidebar, False , False)
        vbox = gtk.VBox()
        #vbox.connect("expose-event", self.expose_event)
        vbox.pack_start(self.tab_window ,True, True)
        self.pack_start(vbox, True, True)
        apply_button = gtk.Button("Apply")
        apply_button.connect("clicked", self.save_changes)
        #hbox.pack_start(apply_button, False, False, 0)
        buttons_aligns = gtk.Alignment(0.5 , 1, 0, 0)
        buttons_aligns.add(apply_button)
        vbox.pack_start(buttons_aligns, False , False)
        #hbox.connect("expose-event", self.hbox_expose_event)


        # FIXME cairo bug need to be fixed
    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb( 1, 1, 1) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

    #def hbox_expose_event(self, widget, event):
        #cr = widget.window.cairo_create()
        #rect = widget.allocation
        #cr.set_source_rgb( 1, 1, 1) 
        #cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        #cr.fill()

    def init(self, access_point):
        self.access_point = access_point
        # Get all connections  
        connection_associate = nm_module.nm_remote_settings.get_ssid_associate_connections(self.access_point.get_ssid())
        connect_not_assocaite = nm_module.nm_remote_settings.get_ssid_not_associate_connections(self.access_point.get_ssid())

        connections = connection_associate + connect_not_assocaite
        # Check connections
        if connection_associate == []:
            nm_module.nm_remote_settings.new_wireless_connection(self.access_point.get_ssid())
            connection_associate = nm_module.nm_remote_settings.get_ssid_associate_connections(self.access_point.get_ssid())
            connect_not_assocaite = nm_module.nm_remote_settings.get_ssid_not_associate_connections(self.access_point.get_ssid())
            connections = connection_associate + connect_not_assocaite

        self.wireless_setting = [Wireless(con) for con in connections]
        self.ipv4_setting = [IPV4Conf(con) for con in connections]
        self.ipv6_setting = [IPV6Conf(con) for con in connections]
        self.security_setting = [Security(con) for con in connections]

        self.sidebar.init(connections,
                          self.ipv4_setting,
                          len(connection_associate),
                          self.access_point)
        index = self.sidebar.get_active()
        self.wireless = self.wireless_setting[index]
        self.ipv4 = self.ipv4_setting[index]
        self.ipv6 = self.ipv6_setting[index]
        self.security = self.security_setting[index]

        self.init_tab_box()

    def init_tab_box(self):
        self.tab_window.tab_items[0] = ("Wireless", self.wireless)
        self.tab_window.tab_items[1] = ("IPV4",self.ipv4)
        self.tab_window.tab_items[2] = ("IPV6",self.ipv6)
        self.tab_window.tab_items[3] = ("Security", self.security)
        tab_index = self.tab_window.tab_index
        self.tab_window.tab_index = -1
        self.tab_window.switch_content(tab_index)
        self.queue_draw()

    def check_click(self, connection):
        index = self.sidebar.get_active()
        self.wireless = self.wireless_setting[index]
        self.ipv4 = self.ipv4_setting[index]
        self.ipv6 = self.ipv6_setting[index]
        self.security = self.security_setting[index]

        self.init_tab_box()

    def save_changes(self, widget):
        self.wireless.save_change()
        self.ipv4.save_changes()
        self.ipv6.save_changes()
        self.security.save_setting()
        #wireless_device = nmclient.get_wireless_devices()[0]
        self.change_crumb()
        self.slide_back() 
        

class SideBar(gtk.VBox):

    def __init__(self, connections, main_init_cb, check_click_cb):
        gtk.VBox.__init__(self, False, 5)
        self.connections = connections
        self.main_init_cb = main_init_cb
        self.check_click_cb = check_click_cb

        # Build ui
        self.associate_buttonbox = gtk.VBox(False, 6)
        self.pack_start(self.associate_buttonbox, False, False)
        
        self.spacer = Label("-------------")
        self.pack_start(self.spacer, False, False, 6)
        self.unassociate_buttonbox = gtk.VBox(False, 6)
        self.pack_start(self.unassociate_buttonbox, False, False)

        add_button = Button("Add setting")
        add_button.connect("clicked", self.add_new_connection)
        self.pack_start(add_button, False, False, 6)
        self.set_size_request(160, -1)

    def init(self, connection_list, ipv4setting, associate_len, access_point):
        wireless_device = nm_module.nmclient.get_wireless_devices()[0]
        #print "in wlan_config get device"
        active_connection = wireless_device.get_active_connection()
        if active_connection:
            active = active_connection.get_connection()
        else: 
            active =None

        self.connections = connection_list
        self.setting = ipv4setting
        self.split = associate_len
        self.access_point = access_point
        self.ssid = self.access_point.get_ssid()

        container_remove_all(self.associate_buttonbox)
        container_remove_all(self.unassociate_buttonbox)
        btn = SettingButton(None,
                            self.connections[0],
                            self.setting[0],
                            self.check_click_cb)
        self.associate_buttonbox.pack_start(btn, False, False,6)

        for index, connection in enumerate(self.connections[1:self.split]):
            button = SettingButton(btn,
                                   connection,
                                   self.setting[index + 1],
                                   self.check_click_cb)
            self.associate_buttonbox.pack_start(button, False ,False, 6)

        if self.connections[self.split:] !=[]:
            for index, connection in enumerate(self.connections[self.split:]):
                button = SettingButton(btn,
                                       connection,
                                       self.setting[index + 1],
                                       self.check_click_cb)
                self.unassociate_buttonbox.pack_start(button, False ,False, 6)

        self.buttonbox = self.associate_buttonbox.get_children() + self.unassociate_buttonbox.get_children()
        try:
            index = self.connections.index(active)
            if index < self.split:
                self.buttonbox[index].check.set_active(True)
            else:
                self.buttonbox[0].check.set_active(True)

        except ValueError:
            self.buttonbox[0].check.set_active(True)

    def get_active(self):
        for index,c in enumerate(self.buttonbox):
            if c.check.get_active():
                return index

    def add_new_connection(self, widget):
        nm_module.nm_remote_settings.new_wireless_connection(self.ssid)
        self.main_init_cb(self.access_point)

        
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
        self.addr_entry = InputEntry()
        #self.addr_entry.set_size(30, 25)
        self.addr_entry.entry.connect("press-return", self.check_ip_valid)
        self.addr_entry.set_sensitive(False)
        table.attach(self.addr_entry, 1,2,2,3)

        mask_label = Label("子网掩码:")
        table.attach(mask_label, 0,1,3,4)
        self.mask_entry = InputEntry()
        #self.mask_entry.set_size(30, 25)
        self.mask_entry.entry.connect("press-return", self.check_mask_valid)
        table.attach(self.mask_entry, 1,2,3,4)
        
        gate_label = Label("默认网关")
        table.attach(gate_label, 0,1,4,5)
        self.gate_entry = InputEntry()
        #self.gate_entry.set_size(30, 25)
        self.gate_entry.entry.connect("press-return", self.check_gate_valid)
        table.attach(self.gate_entry, 1,2,4,5)
        
        #DNS configuration
        self.auto_dns = gtk.RadioButton(None, "自动获得DNS服务器地址")
        self.manual_dns = gtk.RadioButton(self.auto_dns,"使用下面的dns服务器:")
        table.attach(self.auto_dns, 0, 1, 5, 6) 
        table.attach(self.manual_dns, 0, 1, 6, 7)

        master_dns = Label("首选DNS服务器地址:")
        slave_dns = Label("使用下面的DNS服务器地址:")
        self.master_entry = InputEntry()
        self.slave_entry = InputEntry()
        #self.master_entry.set_size(30, 25)
        #self.slave_entry.set_size(30, 25)
        self.master_entry.entry.connect("press-return", self.check_dns_valid)
        self.slave_entry.entry.connect("press-return", self.check_dns_valid)
        
        table.attach(master_dns, 0, 1, 7, 8)
        table.attach(self.master_entry, 1, 2, 7, 8)
        table.attach(slave_dns, 0, 1, 8, 9)
        table.attach(self.slave_entry, 1, 2, 8, 9)

        # TODO UI change 
        table.set_size_request(340, 227)
        align = gtk.Alignment(0, 0, 0, 0)
        align.set_padding(35, 0, 120, 0)
        align.add(table)
        self.add(align)
        
        self.addr_entry.set_size(222, 22)
        self.gate_entry.set_size(222, 22)
        self.mask_entry.set_size(222, 22)
        self.master_entry.set_size(222, 22)
        self.slave_entry.set_size(222, 22)
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

    def get_this_connection(self):
        return self.connection

    def check_ip_valid(self, widget ):
        text = widget.get_text()
        if TypeConvert.is_valid_ip4(text):
            print "valid"
        else:
            print "invalid"

    def check_mask_valid(self, widget):
        text = widget.get_text()
        if TypeConvert.is_valid_netmask(text):
            pass
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
        self.addr_entry = InputEntry()
        #self.addr_entry.set_size(30, 25)
        self.addr_entry.entry.connect("press-return", self.check_ip_valid)
        self.addr_entry.set_sensitive(False)
        table.attach(self.addr_entry, 1,2,2,3)

        mask_label = Label("前缀:")
        table.attach(mask_label, 0,1,3,4)
        self.mask_entry = InputEntry()
        #self.mask_entry.set_size(30, 25)
        self.mask_entry.entry.connect("press-return", self.check_mask_valid)
        table.attach(self.mask_entry, 1,2,3,4)
        
        gate_label = Label("默认网关")
        table.attach(gate_label, 0,1,4,5)
        self.gate_entry = InputEntry()
        #self.gate_entry.set_size(30, 25)
        self.gate_entry.entry.connect("press-return", self.check_gate_valid)
        table.attach(self.gate_entry, 1,2,4,5)
        
        #DNS configuration
        self.auto_dns = gtk.RadioButton(None, "自动获得DNS服务器地址")
        self.manual_dns = gtk.RadioButton(self.auto_dns,"使用下面的dns服务器:")
        table.attach(self.auto_dns, 0, 1, 5, 6) 
        table.attach(self.manual_dns, 0, 1, 6, 7)

        master_dns = Label("首选DNS服务器地址:")
        slave_dns = Label("使用下面的DNS服务器地址:")
        self.master_entry = InputEntry()
        self.slave_entry = InputEntry()
        #self.master_entry.set_size(30, 25)
        #self.slave_entry.set_size(30, 25)
        self.master_entry.entry.connect("press-return", self.check_dns_valid)
        self.slave_entry.entry.connect("press-return", self.check_dns_valid)
        
        table.attach(master_dns, 0, 1, 7, 8)
        table.attach(self.master_entry, 1, 2, 7, 8)
        table.attach(slave_dns, 0, 1, 8, 9)
        table.attach(self.slave_entry, 1, 2, 8, 9)

        # TODO UI change 
        table.set_size_request(340, 227)
        align = gtk.Alignment(0, 0, 0, 0)
        align.set_padding(35, 0, 120, 0)
        align.add(table)
        self.add(align)
        
        self.addr_entry.set_size(222, 22)
        self.gate_entry.set_size(222, 22)
        self.mask_entry.set_size(222, 22)
        self.master_entry.set_size(222, 22)
        self.slave_entry.set_size(222, 22)
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
            connection.add_address([self.addr_entry.get_text(),
                                     self.mask_entry.get_text(),
                                     self.gate_entry.get_text()])
            connection.clear_dns()
            if not self.master_entry.get_text() == "":
                connection.add_dns(self.master_entry.get_text())
            if not self.slave_entry.get_text() == "":
                connection.add_dns(self.slave_entry.get_text())
        #connection.adapt_ip6config_commit()
        #print self.connection.get_setting("connection").id

class Security(gtk.VBox):

    def __init__(self, connection):
        gtk.VBox.__init__(self)
        self.connection = connection

        self.setting = self.connection.get_setting("802-11-wireless-security")
        self.security_label = Label("Security:")
        self.key_label = Label("Key:")
        self.wep_index_label = Label("Wep index:")
        self.auth_label = Label("Authentication:")
        self.password_label = Label("Password:")

        self.security_combo = gtk.combo_box_new_text()
        self.model = self.security_combo.get_model()

        self.encry_list = ["None", 
                      "WEP (Hex or ASCII)",
                      "WEP 104/128-bit Passphrase",
                      "WPA & WPA2 Personal"]
        map(lambda s: self.security_combo.append_text(s), self.encry_list)
        self.security_combo.connect("changed", self.changed_cb)
        self.key_entry = InputEntry()
        self.key_entry.entry.connect("press-return", self.check_wep_validation)
        #self.key_entry.set_size(200, 50)
        self.password_entry = InputEntry()
        #self.password_entry.set_size(200, 50)
        self.password_entry.entry.connect("press-return", self.check_wpa_validate)
        self.show_key_check = CheckButton("Show key")
        self.show_key_check.connect("toggled", self.show_key_check_button_cb)
        self.wep_index_spin = SpinBox(0, 0,3,1 ,55 )
        self.wep_index_spin.connect("value-changed", self.wep_index_spin_cb)
        self.auth_combo = gtk.combo_box_new_text()
        map(lambda s: self.auth_combo.append_text(s), ["Open System", "Shared Key"])

        ## Create table
        self.table = gtk.Table(5, 4, True)
        keys = [None, "none", "none","wpa-psk"]
        
        self.key_mgmt = self.setting.key_mgmt
        if self.key_mgmt == "none":
            key_type = self.setting.wep_key_type
            self.security_combo.set_active(key_type)
        else:
            self.security_combo.set_active(keys.index(self.key_mgmt))
            
        #self.reset(True)

        #table_wpa = gtk.Table(3, 4, True)
        #table_wpa.attach(security_label, 0, 1, 0, 1)
        #table_wpa.attach(self.security_combo, 1 ,4, 0 ,1)
        #TODO UI change
        align = gtk.Alignment(0, 0, 0, 0)
        align.set_padding(35, 0, 120, 0)

        align.add(self.table)

        self.add(align)

    def check_wpa_validate(self, widget):
        text = widget.get_text()
        if self.setting.verify_wpa_psk(text):
            print "valid"
        else:
            print "invalid"

    def check_wep_validation(self, widget):
        key = widget.get_text()
        print key, self.setting.wep_key_type
        active = self.security_combo.get_active()
        if self.setting.verify_wep_key(key, 1):
            print "valid"
        else:
            print "invalid"

    def reset(self, secret = False):
        ## Add security
        container_remove_all(self.table)
        self.table.attach(self.security_label, 0, 1, 0, 1)
        self.table.attach(self.security_combo, 1, 4, 0, 1)

        (setting_name, method) = self.connection.guess_secret_info() 
        if not self.security_combo.get_active() == 0: 
            try:
                secret = nm_module.secret_agent.agent_get_secrets(self.connection.object_path,
                                                        setting_name,
                                                        method)
            except:
                secret = ""


        if self.security_combo.get_active() == 3:
            self.table.attach(self.password_label, 0, 1, 1, 2)
            self.table.attach(self.password_entry, 1, 4, 1, 2)
            
            try:
                self.password_entry.set_text(secret)
            except:
                self.password_entry.set_text("")

        elif self.security_combo.get_active() >=1:
            # Add Key
            self.table.attach(self.key_label, 0, 1, 1, 2)
            self.table.attach(self.key_entry, 1, 4, 1, 2)
            self.table.attach(self.show_key_check, 1, 3, 2, 3)
            # Add wep index
            self.table.attach(self.wep_index_label, 0, 1, 3, 4)
            self.table.attach(self.wep_index_spin, 1, 4, 3, 4)
            # Add Auth
            self.table.attach(self.auth_label, 0, 1, 4, 5)
            self.table.attach(self.auth_combo, 1, 4, 4, 5)
            #table_wpa.attach(show_key_check, 1, 4, 2, 3 )

            # Retrieve wep properties
            #try:
            try:
                key = secret
                index = self.setting.wep_tx_keyidx
                auth = self.setting.auth_alg
                self.auth_combo.set_active(["open", "shared"].index(auth))
            except:
                key = ""
                index = 0
                auth = "open"
            # must convert long int to int 
            index = int(index)
            self.key_entry.set_text(key)
            self.wep_index_spin.set_value(index)
            self.auth_combo.set_active(["open", "shared"].index(auth))

        self.table.show_all()
        #if secret:
            ## TODO need to add entry show password 
    
    def show_key_check_button_cb(self, widget):
        if widget.get_active():
            pass
    
    def changed_cb(self, widget):
        self.reset(True)

    def wep_index_spin_cb(self, widget, value):
        key = nm_module.secret_agent.agent_get_secrets(self.connection.object_path,
                                                   "802-11-wireless-security",
                                                   "wep-key%d"%value)

        if key == None:
            key = ''
        self.key_entry.set_text(key)
        #self.key_entry.queue_draw()

    def save_setting(self):
        # Save wpa settings
        active = self.security_combo.get_active()
        if active == 0:
            pass
        elif active == 3:
            passwd = self.password_entry.get_text()
            key_mgmt = "wpa-psk"
            self.setting.key_mgmt = key_mgmt

            self.setting.psk = passwd
        else:
            passwd = self.key_entry.get_text()
            index = self.wep_index_spin.get_value()
            key_mgmt = "none"
            auth_active = self.auth_combo.get_active()

            self.setting.key_mgmt = key_mgmt
            self.setting.wep_key_type = active
            self.setting.set_wep_key(index, passwd)
            self.setting.wep_tx_keyidx = index
            if auth_active == 0:
                self.setting.auth_alg = "open"
            else:
                self.setting.auth_alg = "shared"

        # Update
        
        self.setting.adapt_wireless_security_commit()
        self.connection.update()
        wireless_device = nm_module.nmclient.get_wireless_devices()[0]
        device_wifi = cache.get_spec_object(wireless_device.object_path)
        setting = self.connection.get_setting("802-11-wireless")
        ssid = setting.ssid
        ap = device_wifi.get_ap_by_ssid(ssid)
        #print ap
        device_wifi.emit("try-ssid-begin", ssid)
        # Activate
        nm_module.nmclient.activate_connection_async(self.connection.object_path,
                                   wireless_device.object_path,
                                   ap.object_path)

class Wireless(gtk.VBox):

    def __init__(self, connection):
        gtk.VBox.__init__(self)
        self.connection = connection 
        self.wireless = self.connection.get_setting("802-11-wireless")
        ### UI
        self.ssid_label = Label("SSID:")
        self.ssid_entry = InputEntry()

        self.mode_label = Label("Mode:")
        self.mode_combo = gtk.combo_box_new_text()
        map(lambda s: self.mode_combo.append_text(s), ["Infrastructure", "Ad-hoc"])
        
        # TODO need to put this section to personal wifi
        #self.band_label = Label("Band:")
        #self.band_combo = gtk.combo_box_new_text()
        #map(lambda s: self.band_combo.append_text(s), ["Automatic", "a (5 GHZ)", "b/g (2.4)"])

        #self.channel_label = Label("Channel:")
        #self.channel_spin = SpinBox(0, 0, 1500, 1, 55)
        # BSSID
        self.bssid_label = Label("BSSID:")
        self.bssid_entry = InputEntry()
        self.mac_address = Label("Device Mac address:")
        self.mac_entry = InputEntry()
        self.clone_addr = Label("Cloned Mac Adrress:")
        self.clone_entry = InputEntry()
        self.mtu = Label("MTU:")
        self.mtu_spin = SpinBox(0, 0, 1500, 1, 55)
        #self.mode_combo.connect("item-selected", self.mode_combo_select)

        self.reset()
        #self.init_table(self.mode_combo.get_current_item()[1]) 

        table = gtk.Table(8, 2, True)
        # SSID
        table.attach(self.ssid_label, 0, 1, 0, 1)
        table.attach(self.ssid_entry, 1, 2, 0, 1)
        # Mode
        table.attach(self.mode_label, 0, 1, 1, 2)
        table.attach(self.mode_combo, 1, 2, 1, 2)
        #Band
        #table.attach(self.band_label, 0, 1, 2, 3)
        #table.attach(self.band_combo, 1, 2, 2, 3)

        #self.band_label.set_no_show_all(True)
        #self.band_combo.set_no_show_all(True)
        #self.band_label.hide()
        #self.band_combo.hide()
        # Channel
        #table.attach(self.channel_label, 0, 1, 3, 4)
        #table.attach(self.channel_spin, 1, 2, 3, 4)
        #self.channel_label.set_no_show_all(True)
        #self.channel_spin.set_no_show_all(True)

        #self.channel_label.hide()
        #self.channel_spin.hide()
        # Bssid
        table.attach(self.bssid_label, 0, 1, 4, 5)
        table.attach(self.bssid_entry, 1, 2, 4, 5)

        # MAC
        table.attach(self.mac_address, 0, 1, 5, 6)
        table.attach(self.mac_entry, 1, 2, 5, 6)
        # MAC_CLONE
        table.attach(self.clone_addr, 0, 1, 6, 7)
        table.attach(self.clone_entry, 1,2, 6, 7)
        # MTU
        table.attach(self.mtu_spin, 1, 2, 7, 8)
        table.attach(self.mtu, 0, 1, 7, 8)

        #TODO UI change
        align = gtk.Alignment(0, 0, 0, 0)
        align.set_padding(35, 0, 120, 0)
        align.add(table)
        self.add(align)
        table.set_size_request(340, 227)

        self.ssid_entry.set_size(222, 22)
        self.bssid_entry.set_size(222, 22)
        self.mac_entry.set_size(222, 22)
        self.clone_entry.set_size(222, 22)


    def reset(self):
        wireless = self.wireless
        ## retrieve wireless info
        if wireless.ssid != None:
            self.ssid_entry.set_text(wireless.ssid)

        if wireless.bssid != None:
            self.bssid_entry.set_text(wireless.bssid)

        if wireless.mode == 'infrastructure':
            #self.mode_combo.set_select_index(0)
            self.mode_combo.set_active(0)
        else:
            #self.mode_combo.set_select_index(1)
            self.mode_combo.set_active(1)

        if wireless.mac_address != None:
            self.mac_entry.set_text(wireless.mac_address)

        if wireless.cloned_mac_address !=None:
            self.clone_entry.set_text(wireless.cloned_mac_address)

        if wireless.mtu != None:
            self.mtu_spin.set_value(int(wireless.mtu))

    
    def save_change(self):
        
        self.wireless.ssid = self.ssid_entry.get_text()
        model = self.mode_combo.get_model()
        active = self.mode_combo.get_active()
        self.wireless.mode = model[active][0]

        if self.bssid_entry.get_text() != "":
            self.wireless.bssid = self.bssid_entry.get_text()
        if self.mac_entry.get_text() != "":
            self.wireless.mac_address = self.mac_entry.get_text()
        if self.clone_entry.get_text() != "":
            self.wireless.cloned_mac_address = self.clone_entry.get_text()

        self.wireless.mtu = self.mtu_spin.get_value()
        self.wireless.adapt_wireless_commit()
        # TODO add update functions
        #connection.adapt_ip4config_commit()
        #self.connection.update()
        
