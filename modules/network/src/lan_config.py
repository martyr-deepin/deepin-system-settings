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
from nm_modules import nm_module
#from widgets import SettingButton
from settings_widget import EntryTreeView, SettingItem
from nmlib.nm_utils import TypeConvert
from nmlib.nmcache import cache
from nmlib.nm_remote_connection import NMRemoteConnection
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
        self.tab_window.set_size_request(674, 408)
        self.items = [("有线", NoSetting()),
                      ("IPv4设置", NoSetting()),
                      ("IPv6设置", NoSetting())]
        self.tab_window.add_items(self.items)
        self.sidebar = SideBar( None, self.init, self.check_click)
        # Build ui
        self.pack_start(self.sidebar, False , False)
        vbox = gtk.VBox()
        vbox.connect("expose-event", self.expose_event)
        vbox.pack_start(self.tab_window ,True, True)
        self.pack_start(vbox, True, True)
        #hbox = gtk.HBox()

        save_button = Button("Save")
        apply_button = Button("Connect")
        #apply_button.set_sensitive(False)
        button_box = gtk.HBox()
        button_box.add(save_button)
        button_box.add(apply_button)
        apply_button.connect("clicked", self.apply_changes)
        save_button.connect("clicked", self.save_changes)

        #hbox.pack_start(apply_button, False, False, 0)
        buttons_aligns = gtk.Alignment(0.5 , 1, 0, 0)
        buttons_aligns.add(button_box)
        vbox.pack_start(buttons_aligns, False , False)
        #hbox.connect("expose-event", self.expose_event)

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb( 1, 1, 1) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

    def init(self, device=None, new_connection=None, init_connection=False):
        # Get all connections
        #print "*in lan_config* ", nm_module.nmclient
        if device is not None:
            wired_device = device
            global wired_device


        self.connections = nm_module.nm_remote_settings.get_wired_connections()
        if init_connection:
            for connection in self.connections:
                connection.init_settings_prop_dict()
        # Check connections
        if self.connections == []:
            self.connections = [].append(nm_module.nm_remote_settings.new_wired_connection())
            #connections = nm_module.nm_remote_settings.get_wired_connections()

        if new_connection:
            self.connections += new_connection
        else:
            self.sidebar.new_connection_list = []
            
        self.wired_setting = [Wired(con) for con in self.connections]
        self.ipv4_setting = [IPV4Conf(con) for con in self.connections]
        self.ipv6_setting = [IPV6Conf(con) for con in self.connections]

        self.sidebar.init(self.connections, self.ipv4_setting)
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

        connection = self.ipv4.connection
        if connection.check_setting_finish():
            this_index = self.connections.index(connection)
            if isinstance(connection, NMRemoteConnection):
                connection.update()
            else:
                nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')
                index = self.sidebar.new_connection_list.index(connection)
                self.sidebar.new_connection_list.pop(index)
                self.init(None, self.sidebar.new_connection_list)

                # reset index
                con = self.sidebar.connection_tree.visible_items[this_index]
                self.sidebar.connection_tree.select_items([con])
        else:
            print "not complete"

    def apply_changes(self, widget):
        connection = self.ipv4.connection
        nm_module.nmclient.activate_connection_async(connection.object_path,
                                           wired_device.object_path,
                                           "/")
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

        self.new_connection_list =[]

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
        cons = []
        self.connection_tree = EntryTreeView(cons)
        for index, connection in enumerate(self.connections):
            cons.append(SettingItem(connection, self.setting[index], self.check_click_cb, self.delete_item_cb))
        self.connection_tree.add_items(cons)

        self.connection_tree.show_all()

        self.buttonbox.pack_start(self.connection_tree, False, False, 6)

        try:
            index = self.connections.index(active)
            this_connection = self.connection_tree.visible_items[index]
            this_connection.set_active(True)
            self.connection_tree.select_items([this_connection])
        except ValueError:
            self.connection_tree.select_first_item()
        if self.new_connection_list:
            connect = self.connection_tree.visible_items[-1]
            self.connection_tree.select_items([connect])

    def delete_item_cb(self, connection):
        from nmlib.nm_remote_connection import NMRemoteConnection
        self.connection_tree.delete_select_items()
        if isinstance(connection, NMRemoteConnection):
            connection.delete()
        else:
            index = self.new_connection_list.index(connection)
            self.new_connection_list.pop(index)
        self.connection_tree.set_size_request(-1,len(self.connection_tree.visible_items) * self.connection_tree.visible_items[0].get_height())

    def get_active(self):
        return self.connection_tree.select_rows[0]

    def set_active(self):
        index = self.get_active()
        this_connection = self.connection_tree.visible_items[index]
        this_connection.set_active(True)

    def clear_active(self):
        items = self.connection_tree.visible_items
        for item in items:
            item.set_active(False)

    def add_new_setting(self, widget):
        connection = nm_module.nm_remote_settings.new_wired_connection()
        self.new_connection_list.append(connection)
        self.main_init_cb(new_connection=self.new_connection_list)

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

        self.addr_label = Label("IP地址:")
        table.attach(self.addr_label, 0,1,2,3)
        self.addr_entry = InputEntry()
        self.addr_entry.set_sensitive(False)
        table.attach(self.addr_entry, 1,2,2,3)

        self.mask_label = Label("子网掩码:")
        table.attach(self.mask_label, 0,1,3,4)
        self.mask_entry = InputEntry()
        table.attach(self.mask_entry, 1,2,3,4)
        
        self.gate_label = Label("默认网关")
        table.attach(self.gate_label, 0,1,4,5)
        self.gate_entry = InputEntry()
        table.attach(self.gate_entry, 1,2,4,5)
        
        #DNS configuration
        self.auto_dns = gtk.RadioButton(None, "自动获得DNS服务器地址")
        self.manual_dns = gtk.RadioButton(self.auto_dns,"使用下面的dns服务器:")
        table.attach(self.auto_dns, 0, 1, 5, 6) 
        table.attach(self.manual_dns, 0, 1, 6, 7)

        self.master_dns = Label("首选DNS服务器地址:")
        self.slave_dns = Label("使用下面的DNS服务器地址:")
        self.master_entry = InputEntry()
        self.slave_entry = InputEntry()
        
        table.attach(self.master_dns, 0, 1, 7, 8)
        table.attach(self.master_entry, 1, 2, 7, 8)
        table.attach(self.slave_dns, 0, 1, 8, 9)
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
        self.show_all()
        
        self.ip = ["","",""]
        self.dns = ["",""]
        self.reset(connection)
        self.addr_entry.entry.connect("changed", self.set_ip_address, 0)
        self.mask_entry.entry.connect("changed", self.set_ip_address, 1)
        self.gate_entry.entry.connect("changed", self.set_ip_address, 2)
        self.master_entry.entry.connect("changed", self.set_dns_address, 0)
        self.slave_entry.entry.connect("changed", self.set_dns_address, 1)
        
        self.manual_ip.connect("toggled", self.manual_ip_entry)
        self.auto_ip.connect("toggled", self.auto_get_ip_addr)
        self.auto_dns.connect("toggled", self.auto_dns_set)
        self.manual_dns.connect("toggled", self.manual_dns_set)

    def reset(self, connection):
        self.setting = connection.get_setting("ipv4")       

        if self.setting.method == "auto":
            self.auto_ip.set_active(True)
            self.set_group_sensitive("ip", False)
            
        else:
            self.manual_ip.set_active(True)
            self.set_group_sensitive("ip", True)
            if not self.setting.addresses == []:
                self.addr_entry.set_text(self.setting.addresses[0][0])
                self.mask_entry.set_text(self.setting.addresses[0][1])
                self.gate_entry.set_text(self.setting.addresses[0][2])
                self.ip = self.setting.addresses[0]

        if self.setting.dns == []:
            self.auto_dns.set_active(True)
            self.set_group_sensitive("dns", False)
        else:
            self.manual_dns.set_active(True)
            self.set_group_sensitive("dns", True)
            self.master_entry.set_text(self.setting.dns[0])
            self.dns = self.setting.dns + [""]
            if len(self.setting.dns) > 1:
                self.slave_entry.set_text(self.setting.dns[1])
                self.dns = self.setting.dns


    def set_group_sensitive(self, group_name, sensitive):
        if group_name is "ip":
            self.addr_label.set_sensitive(sensitive)
            self.mask_label.set_sensitive(sensitive)
            self.gate_label.set_sensitive(sensitive)
            self.addr_entry.set_sensitive(sensitive)
            self.mask_entry.set_sensitive(sensitive)
            self.gate_entry.set_sensitive(sensitive)
            if not sensitive:
                self.addr_entry.set_text("")
                self.mask_entry.set_text("")
                self.gate_entry.set_text("")
        elif group_name is "dns":
            self.master_dns.set_sensitive(sensitive)
            self.slave_dns.set_sensitive(sensitive)
            self.master_entry.set_sensitive(sensitive)
            self.slave_entry.set_sensitive(sensitive)
            if not sensitive:
                self.master_entry.set_text("")
                self.slave_entry.set_text("")

    def set_ip_address(self, widget, content, index):
        names = ["ip4", "netmask", "gw"]
        self.ip[index] = content
        if self.check_valid(names[index]):
            setattr(self, names[index] + "_flag", True)
            #print "valid"+ names[index]
        else:
            setattr(self, names[index] + "_flag", False)

        if self.check_valid("gw"):
            #print "update ip4"
            if self.setting.addresses:
                self.setting.clear_addresses()
            self.setting.add_address(self.ip)
        else:
            self.setting.clear_addresses()

    def set_dns_address(self, widget, content, index):
        self.dns[index] = content
        names = ["master", "slaver"]
        if TypeConvert.is_valid_ip4(content):
            setattr(self, names[index] + "_flag", True)
            print "valid"+ names[index]
        else:
            setattr(self, names[index] + "_flag", False)

        dns = self.check_complete_dns()
        if dns:
            self.setting.clear_dns()
            for d in dns:
                self.setting.add_dns(d)
        else:
            self.setting.clear_dns()
            
    def check_complete_dns(self):
        dns = []
        for address in self.dns:
            if TypeConvert.is_valid_ip4(address):
                dns.append(address)
            else:
                return dns
        return dns

    def check_valid(self, name):
        if name == "ip4":
            return TypeConvert.is_valid_ip4(self.ip[0])
        elif name == "netmask":
            return TypeConvert.is_valid_netmask(self.ip[1])
        elif name == "gw":
            return TypeConvert.is_valid_gw(self.ip[0], self.ip[1], self.ip[2])

    def auto_dns_set(self, widget):
        if widget.get_active():
            self.setting.clear_dns()
            self.dns = ["",""]
            self.set_group_sensitive("dns", False)

    def manual_dns_set(self, widget):
        if widget.get_active():
            self.set_group_sensitive("dns", True)

    def auto_get_ip_addr(self, widget):
        if widget.get_active():
            self.setting.clear_addresses()
            self.ip = ["","",""]
            self.setting.method = 'auto'
            self.set_group_sensitive("ip", False)

    def manual_ip_entry(self,widget):
        if widget.get_active():
            self.setting.method = 'manual'
            self.set_group_sensitive("ip", True)
    
    def save_changes(self):
        pass
        #connection = self.setting
        #if connection.method =="manual": 
            #connection.clear_addresses()
            #connection.add_address([self.addr_entry.get_text(),
                                     #self.mask_entry.get_text(),
                                     #self.gate_entry.get_text()])
            #connection.clear_ns()
            #if not self.master_entry.get_text() == "":
                #connection.add_dns(self.master_entry.get_text())
            #if not self.slave_entry.get_text() == "":
                #connection.add_dns(self.slave_entry.get_text())
        
        #connection.adapt_ip4config_commit()

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

        self.addr_label = Label("IP地址:")
        table.attach(self.addr_label, 0,1,2,3)
        self.addr_entry = InputEntry()
        self.addr_entry.set_sensitive(False)
        table.attach(self.addr_entry, 1,2,2,3)

        self.mask_label = Label("前缀:")
        table.attach(self.mask_label, 0,1,3,4)
        self.mask_entry = InputEntry()
        table.attach(self.mask_entry, 1,2,3,4)
        
        self.gate_label = Label("默认网关")
        table.attach(self.gate_label, 0,1,4,5)
        self.gate_entry = InputEntry()
        table.attach(self.gate_entry, 1,2,4,5)
        
        #DNS configuration
        self.auto_dns = gtk.RadioButton(None, "自动获得DNS服务器地址")
        self.manual_dns = gtk.RadioButton(self.auto_dns,"使用下面的dns服务器:")
        table.attach(self.auto_dns, 0, 1, 5, 6) 
        table.attach(self.manual_dns, 0, 1, 6, 7)

        self.master_dns = Label("首选DNS服务器地址:")
        self.slave_dns = Label("使用下面的DNS服务器地址:")
        self.master_entry = InputEntry()
        self.slave_entry = InputEntry()
        
        table.attach(self.master_dns, 0, 1, 7, 8)
        table.attach(self.master_entry, 1, 2, 7, 8)
        table.attach(self.slave_dns, 0, 1, 8, 9)
        table.attach(self.slave_entry, 1, 2, 8, 9)

        # TODO UI change 
        table.set_size_request(340, 227)
        align = gtk.Alignment( 0, 0, 0, 0)
        align.set_padding( 35, 0, 120, 0)
        align.add(table)
        self.add(align)
        
        self.addr_entry.set_size(222, 22)
        self.gate_entry.set_size(222, 22)
        self.mask_entry.set_size(222, 22)
        self.master_entry.set_size(222, 22)
        self.slave_entry.set_size(222, 22)
        
        
        self.ip = ["","",""]
        self.dns = ["",""]
        self.setting =None
        self.reset(connection)
        self.addr_entry.entry.connect("changed", self.set_ip_address, 0)
        self.mask_entry.entry.connect("changed", self.set_ip_address, 1)
        self.gate_entry.entry.connect("changed", self.set_ip_address, 2)
        self.master_entry.entry.connect("changed", self.set_dns_address, 0)
        self.slave_entry.entry.connect("changed", self.set_dns_address, 1)

        self.manual_ip.connect("toggled", self.manual_ip_entry)
        self.auto_ip.connect("toggled", self.auto_get_ip_addr)
        self.auto_dns.connect("toggled", self.auto_dns_set)
        self.manual_dns.connect("toggled", self.manual_dns_set)



    def reset(self, connection):
        self.setting = connection.get_setting("ipv6")       

        if self.setting.method == "auto":
            self.auto_ip.set_active(True)
            self.set_group_sensitive("ip", False)
            
        else:
            self.manual_ip.set_active(True)
            self.set_group_sensitive("ip", True)
            if not self.setting.addresses == []:
                self.addr_entry.set_text(self.setting.addresses[0][0])
                self.mask_entry.set_text(self.setting.addresses[0][1])
                self.gate_entry.set_text(self.setting.addresses[0][2])
                self.ip = self.setting.addresses

        if self.setting.dns == []:
            self.auto_dns.set_active(True)
            self.set_group_sensitive("dns", False)
        else:
            self.manual_dns.set_active(True)
            self.set_group_sensitive("dns", True)
            self.master_entry.set_text(self.setting.dns[0])
            self.dns = self.setting_dns +[""]
            if len(self.setting.dns) > 1:
                self.slave_entry.set_text(self.setting.dns[1])
                self.dns = self.setting.dns

    def set_group_sensitive(self, group_name, sensitive):
        if group_name is "ip":
            self.addr_label.set_sensitive(sensitive)
            self.mask_label.set_sensitive(sensitive)
            self.gate_label.set_sensitive(sensitive)
            self.addr_entry.set_sensitive(sensitive)
            self.mask_entry.set_sensitive(sensitive)
            self.gate_entry.set_sensitive(sensitive)
            if not sensitive:
                self.addr_entry.set_text("")
                self.mask_entry.set_text("")
                self.gate_entry.set_text("")
        elif group_name is "dns":
            self.master_dns.set_sensitive(sensitive)
            self.slave_dns.set_sensitive(sensitive)
            self.master_entry.set_sensitive(sensitive)
            self.slave_entry.set_sensitive(sensitive)
            if not sensitive:
                self.master_entry.set_text("")
                self.slave_entry.set_text("")

    def set_ip_address(self, widget, content, index):
        names = ["ip6", "netmask", "gw"]
        self.ip[index] = content
        if self.check_valid(names[index]):
            setattr(self, names[index] + "_flag", True)
            #print "valid"+ names[index]
        else:
            setattr(self, names[index] + "_flag", False)

        if self.check_valid("gw"):
            #print "update ip4"
            if self.setting.addresses:
                self.setting.clear_addresses()
            self.setting.add_address(self.ip)
        else:
            self.setting.clear_addresses()

    def set_dns_address(self, widget, content, index):
        self.dns[index] = content
        names = ["master", "slaver"]
        if TypeConvert.is_valid_ip6(content):
            setattr(self, names[index] + "_flag", True)
            print "valid"+ names[index]
        else:
            setattr(self, names[index] + "_flag", False)

        dns = self.check_complete_dns()
        if dns:
            self.setting.clear_dns()
            for d in dns:
                self.setting.add_dns(d)
        else:
            self.setting.clear_dns()
            
    def check_complete_dns(self):
        dns = []
        for address in self.dns:
            if TypeConvert.is_valid_ip6(address):
                dns.append(address)
            else:
                return dns
        return dns

    def check_valid(self, name):
        if name == "ip6":
            return TypeConvert.is_valid_ip6(self.ip[0])
        elif name == "netmask":
            return TypeConvert.is_valid_netmask(self.ip[1])
        elif name == "gw":
            return TypeConvert.is_valid_gw(self.ip[0], self.ip[1], self.ip[2])

    def auto_dns_set(self, widget):
        if widget.get_active():
            self.setting.clear_dns()
            self.dns = ["",""]
            self.set_group_sensitive("dns", False)

    def manual_dns_set(self, widget):
        if widget.get_active():
            self.set_group_sensitive("dns", True)

    def auto_get_ip_addr(self, widget):
        if widget.get_active():
            self.setting.clear_addresses()
            self.ip = ["","",""]
            self.setting.method = 'auto'
            self.set_group_sensitive("ip", False)

    def manual_ip_entry(self,widget):
        if widget.get_active():
            self.setting.method = 'manual'
            self.set_group_sensitive("ip", True)
    
    def save_changes(self):
        pass
    #def set_addresses(self, widget, content, index):
        #self.ip_address[index] = content
        #if self.check_complete():
            #self.setting.addresses = self.ip_address
            #print "address>>>>",self.setting.addresses
        #else:
            #self.setting.clear_addresses()
            #self.ip_address = ["","",""]

        
    #def check_complete(self):
        #names = ["ip6", "netmask", "gw"]
        #for index, content in enumerate(self.ip_address):
            #if self.check_valid(names[index], content):
                #pass
            #else:
                #return False
        #return True


    #def check_valid(self, name, content):
        ## Name: ip6, netmask, gw
        #if getattr(TypeConvert, "is_valid_%s"%name)(content):
            #return True
        #else:
            #return False


    #def check_ip_valid(self, widget):
        #text = widget.get_text()
        #if TypeConvert.is_valid_ip6(text):
            #print "valid"
        #else:
            #print "invalid"

    #def check_mask_valid(self, widget):
        #text = widget.get_text()
        #if TypeConvert.is_valid_netmask(text):
            #print "valid"
        #else:
            #print "invalid"


    #def check_gate_valid(self, widget):
        #text = widget.get_text()
        #if TypeConvert.is_valid_gw(text):
            #print "valid"
        #else:
            #print "invalid"
        

    #def check_dns_valid(self, widget):
        #text = widget.get_text()
        #if TypeConvert.is_valid_ip4(text):
            #print "valid"
        #else:
            #print "invalid"


    #def reset(self, connection):
        #self.connection = connection
        #self.setting = connection.get_setting("ipv6")       
        #self.clear_entry()
        #if self.setting.method == "auto":
            #self.auto_ip.set_active(True)
            #self.set_group_sensitive("ip", False)
            
        #else:
            #self.manual_ip.set_active(True)
            #self.set_group_sensitive("ip", True)

            #if not self.setting.addresses == []:
                #self.addr_entry.set_text(self.setting.addresses[0][0])
                #self.mask_entry.set_text(self.setting.addresses[0][1])
                #self.gate_entry.set_text(self.setting.addresses[0][2])

        #if self.setting.dns == []:
            #self.auto_dns.set_active(True)
            #self.set_group_sensitive("dns", False)
        #else:
            #self.manual_dns.set_active(True)
            #self.set_group_sensitive("dns", True)
            #if len(self.setting.dns) > 1:
                #self.slave_entry.set_text(self.setting.dns[1])
            #self.master_entry.set_text(self.setting.dns[0])
    
    #def set_group_sensitive(self, group_name, sensitive):
        #if group_name is "ip":
            #self.addr_label.set_sensitive(sensitive)
            #self.mask_label.set_sensitive(sensitive)
            #self.gate_label.set_sensitive(sensitive)
            #self.addr_entry.set_sensitive(sensitive)
            #self.mask_entry.set_sensitive(sensitive)
            #self.gate_entry.set_sensitive(sensitive)
            #if not sensitive:
                #self.addr_entry.set_text("")
                #self.mask_entry.set_text("")
                #self.gate_entry.set_text("")
        #elif group_name is "dns":
            #self.master_dns.set_sensitive(sensitive)
            #self.slave_dns.set_sensitive(sensitive)
            #self.master_entry.set_sensitive(sensitive)
            #self.slave_entry.set_sensitive(sensitive)
            #if not sensitive:
                #self.master_entry.set_text("")
                #self.slave_entry.set_text("")

    #def auto_dns_set(self, widget, connection):
        #if widget.get_active():
            #print "asfsd"
            #connection.clear_dns()
            #self.set_group_sensitive('dns', False)
            ##self.master_entry.set_sensitive(False)
            ##self.slave_entry.set_sensitive(False)

    #def manual_dns_set(self, widget, connection):
        #if widget.get_active():
            #self.set_group_sensitive('dns', True)
            #if len(connection.dns) == 1:
                #self.master_entry.set_text(connection.dns[0])
            #elif len(connection.dns) > 1:
                #self.slave_entry.set_text(connection.dns[1])

    #def clear_entry(self):
        #self.addr_entry.set_text("")
        #self.mask_entry.set_text("")
        #self.gate_entry.set_text("")
        #self.master_entry.set_text("")
        #self.slave_entry.set_text("")

    #def auto_get_ip_addr(self, widget, connection):
        #if widget.get_active():
            #self.connection.method = 'auto'
            #self.set_group_sensitive('ip', False)
    #def manual_ip_entry(self,widget, connection):
        #if widget.get_active():
            #self.connection.method = 'manual'
            #self.set_group_sensitive('ip', True)
            #if not connection.addresses == []:
                #self.addr_entry.set_text(connection.addresses[0][0])
                #self.mask_entry.set_text(connection.addresses[0][1])
                #self.gate_entry.set_text(connection.addresses[0][2])
    
    #def save_changes(self):
        #connection = self.setting
        #if connection.method =="manual": 
            #connection.clear_addresses()

            #print self.addr_entry.get_text()

            #connection.add_address([self.addr_entry.get_text(),
                                     #self.mask_entry.get_text(),
                                     #self.gate_entry.get_text()])
            #connection.clear_dns()
            #if not self.master_entry.get_text() == "":
                #connection.add_dns(self.master_entry.get_text())
            #if not self.slave_entry.get_text() == "":
                #connection.add_dns(self.slave_entry.get_text())

        #connection.adapt_ip6config_commit()
        #print self.connection.get_setting("connection").id
        #self.connection.update()

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

        self.mac_entry = InputEntry()
        table.attach(self.mac_entry, 1, 2, 0, 1)

        clone_addr = Label("Cloned Mac Adrress:")
        table.attach(clone_addr, 0, 1, 1, 2)
        self.clone_entry = InputEntry()
        table.attach(self.clone_entry, 1,2, 1, 2)

        mtu = Label("MTU:")
        table.attach(mtu, 0,1,2,3)
        self.mtu_spin = SpinBox(0,0, 1500, 1, 55)
        table.attach(self.mtu_spin, 1,2,2,3)
        
        # TODO UI change
        align = gtk.Alignment( 0, 0, 0, 0)
        align.set_padding(35, 0, 120, 0)
        align.add(table)
        self.add(align)

        self.mac_entry.set_size(222, 22)
        self.clone_entry.set_size(222, 22)

        self.mac_entry.entry.connect("changed", self.save_settings, "mac_address")
        self.clone_entry.entry.connect("changed", self.save_settings, "cloned_mac_address")
        self.mtu_spin.connect("value_changed", self.save_settings, "mtu")


        ## retrieve wired info
        (mac, clone_mac, mtu) = self.ethernet.mac_address, self.ethernet.cloned_mac_address, self.ethernet.mtu
        #print mac, clone_mac, mtu
        if mac != None:
            self.mac_entry.set_text(mac)
        if clone_mac !=None:
            self.clone_entry.set_text(clone_mac)
        if mtu != None:
            self.mtu_spin.set_value(int(mtu))

    def save_settings(self, widget, value, types):
        if type(value) is str:
            if TypeConvert.is_valid_mac_address(value):
                setattr(self.ethernet, types, value)
            elif value is "":
                delattr(self.ethernet, types)
        else:
            setattr(self.ethernet, types, value)

    #def check_mac(self, widget):
        #mac_string = widget.get_text()
        #from nmlib.nm_utils import TypeConvert
        #if TypeConvert.is_valid_mac_address(mac_string):
            #print "valid"
        #else:
            #print "invalid"

    def save_setting(self):
        pass
        #mac_entry = self.mac_entry.get_text()
        #clone_entry = self.clone_entry.get_text()
        #mtu = self.mtu_spin.get_value()
        #if mac_entry != "": 
            #self.ethernet.mac_address = mac_entry
        #if clone_entry != "":
            #self.ethernet.cloned_mac_address = clone_entry
        #self.ethernet.mtu = mtu

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
