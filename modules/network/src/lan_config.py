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
from nm_modules import nm_module
from widgets import SettingButton
from nmlib.nm_utils import TypeConvert
from nmlib.nmcache import cache
import gtk
wired_device = []

class WiredSetting(gtk.HBox):

    def __init__(self, slide_back_cb, change_crumb_cb):
        gtk.HBox.__init__(self)
        self.slide_back = slide_back_cb
        self.change_crumb = change_crumb_cb

        self.wired = None
        self.ipv4 = None
        self.ipv6 = None

        self.tab_window = TabBox(dockfill = True)
        self.items = [("有线", NoSetting()),
                      ("IPv4设置", NoSetting()),
                      ("IPv6设置", NoSetting())]
        self.tab_window.add_items(self.items)
        self.sidebar = SideBar( None, self.init, self.check_click)

        # Build ui
        self.pack_start(self.sidebar, False , False)
        vbox = gtk.VBox()
        #vbox.connect("expose-event", self.expose_event)
        vbox.pack_start(self.tab_window ,True, True)
        self.pack_start(vbox, True, True)
        #hbox = gtk.HBox()
        apply_button = gtk.Button("Apply")
        apply_button.connect("clicked", self.save_changes)
        #hbox.pack_start(apply_button, False, False, 0)
        buttons_aligns = gtk.Alignment(0.5 , 1, 0, 0)
        buttons_aligns.add(apply_button)
        vbox.pack_start(buttons_aligns, False , False)
        #hbox.connect("expose-event", self.expose_event)

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb( 1, 1, 1) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

    def init(self, device = None):
        # Get all connections
        #print "*in lan_config* ", nm_module.nmclient
        if device != None:
            wired_device = device
            global wired_device
        connections = nm_module.nm_remote_settings.get_wired_connections()
        # Check connections
        if connections == []:
            nm_module.nm_remote_settings.new_wired_connection()
            connections = nm_module.nm_remote_settings.get_wired_connections()

        self.wired_setting = [Wired(con) for con in connections]
        self.ipv4_setting = [IPV4Conf(con) for con in connections]
        self.ipv6_setting = [IPV6Conf(con) for con in connections]

        self.sidebar.init(connections, self.ipv4_setting)
        index = self.sidebar.get_active()
        self.wired = self.wired_setting[index]
        self.ipv4 = self.ipv4_setting[index]
        self.ipv6 = self.ipv6_setting[index]

        self.init_tab_box()

    def init_tab_box(self):
        self.tab_window.tab_items[0] = ("有线", self.wired)
        self.tab_window.tab_items[1] = ("IPV4设置",self.ipv4)
        self.tab_window.tab_items[2] = ("IPV6设置",self.ipv6)
        tab_index = self.tab_window.tab_index
        self.tab_window.tab_index = -1
        self.tab_window.switch_content(tab_index)
        self.queue_draw()

    def check_click(self, connection):
        index = self.sidebar.get_active()
        self.wired = self.wired_setting[index]
        self.ipv4 = self.ipv4_setting[index]
        self.ipv6 = self.ipv6_setting[index]

        self.init_tab_box()

    def save_changes(self, widget):
        self.wired.save_setting()
        self.ipv4.save_changes()
        self.ipv6.save_changes()
        self.device_ethernet = cache.get_spec_object(wired_device.object_path)
        self.device_ethernet.emit("try-activate-begin")
        self.change_crumb()
        self.slide_back()
        
class SideBar(gtk.VBox):
    def __init__(self, connections, main_init_cb, check_click_cb):
        gtk.VBox.__init__(self, False, 5)
        self.connections = connections
        self.main_init_cb = main_init_cb
        self.check_click_cb = check_click_cb

        # determin the active one
        self.buttonbox = gtk.VBox(False, 6)
        self.pack_start(self.buttonbox, False, False)
        add_button = Button("Add setting")
        add_button.connect("clicked", self.add_new_setting)
        self.pack_start(add_button, False, False, 6)
        self.set_size_request(160, -1)

    def init(self, connection_list, ipv4setting):

        # check active
        active_connection = wired_device.get_active_connection()
        if active_connection:
            active = active_connection.get_connection()
        else:
            active = None

        self.connections = connection_list
        self.setting = ipv4setting
        
        # Add connection buttons
        container_remove_all(self.buttonbox)
        btn = SettingButton(None, 
                            self.connections[0],
                            self.setting[0],
                            self.check_click_cb)
        self.buttonbox.pack_start(btn, False, False, 6)
        for index, connection in enumerate(self.connections[1:]):
            button = SettingButton(btn,
                                   connection,
                                   self.setting[index + 1],
                                   self.check_click_cb)
            self.buttonbox.pack_start(button, False, False, 6)

        try:
            index = self.connections.index(active)
            self.buttonbox.get_children()[index].check.set_active(True)
        except ValueError:
            self.buttonbox.get_children()[0].check.set_active(True)

    def get_active(self):
        checks = self.buttonbox.get_children()
        for index,c in enumerate(checks):
            if c.check.get_active():
                return index

    def add_new_setting(self, widget):
        nm_module.nm_remote_settings.new_wired_connection()
        self.main_init_cb()

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

        nm_module.nmclient.activate_connection_async(self.connection.object_path,
                                           wired_device.object_path,
                                           "/")

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
        
        self.ethernet = connection.get_setting("802-3-ethernet")

        table = gtk.Table(3, 2, False)
        
        mac_address = Label("Device Mac address:")
        table.attach(mac_address, 0, 1, 0, 1)

        self.mac_entry = gtk.Entry()
        self.mac_entry.connect("activate", self.check_mac)
        table.attach(self.mac_entry, 1, 2, 0, 1)

        clone_addr = Label("Cloned Mac Adrress:")
        table.attach(clone_addr, 0, 1, 1, 2)
        self.clone_entry = gtk.Entry()
        self.clone_entry.connect("activate", self.check_mac)
        table.attach(self.clone_entry, 1,2, 1, 2)

        mtu = Label("MTU:")
        table.attach(mtu, 0,1,2,3)
        self.mtu_spin = SpinBox(0,0, 1500, 1, 55)
        table.attach(self.mtu_spin, 1,2,2,3)
        
        align = gtk.Alignment(0.5, 0.5, 0, 0)
        align.add(table)
        self.add(align)

        ## retrieve wired info
        (mac, clone_mac, mtu) = self.ethernet.mac_address, self.ethernet.cloned_mac_address, self.ethernet.mtu
        #print mac, clone_mac, mtu
        if mac != None:
            self.mac_entry.set_text(mac)
        if clone_mac !=None:
            self.clone_entry.set_text(clone_mac)
        if mtu != None:
            self.mtu_spin.set_value(int(mtu))

    def check_mac(self, widget):
        mac_string = widget.get_text()
        from nmlib.nm_utils import TypeConvert
        if TypeConvert.is_valid_mac_address(mac_string):
            print "valid"
        else:
            print "invalid"

    def save_setting(self):
        mac_entry = self.mac_entry.get_text()
        clone_entry = self.clone_entry.get_text()
        mtu = self.mtu_spin.get_value()
        if mac_entry != "": 
            self.ethernet.mac_address = mac_entry
        if clone_entry != "":
            self.ethernet.cloned_mac_address = clone_entry
        self.ethernet.mtu = mtu





    
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
