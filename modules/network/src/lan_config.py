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
#from dss import app_theme
from nm_modules import nm_module
from dtk.ui.button import Button
from nmlib.nm_utils import TypeConvert
from nmlib.nm_remote_connection import NMRemoteConnection
from ipsettings import IPV4Conf, IPV6Conf
from elements import SettingSection, TableAsm
import gtk
wired_device = []

from shared_methods import Settings, net_manager
from helper import Dispatcher, event_manager
from nls import _

class WiredSetting(Settings):
    def __init__(self, device, spec_connection=None):
        Settings.__init__(self,[Wired, Sections, IPV6Conf])
        self.crumb_name = _("Wired")
        self.device = device
        self.spec_connection = spec_connection
        event_manager.emit("update-delete-button", False)

    def get_connections(self):
        self.connections = nm_module.nm_remote_settings.get_wired_connections()

        if self.connections == []:
            self.connections = [nm_module.nm_remote_settings.new_wired_connection()]
        return self.connections
    
    def add_new_connection(self):
        return (nm_module.nm_remote_settings.new_wired_connection(), -1)
    
    def save_changes(self, connection):
        if connection.check_setting_finish():
            if isinstance(connection, NMRemoteConnection):
                connection.update()
            else:
                connection = nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')
                Dispatcher.emit("connection-replace", connection)
                # reset index
            self.set_button("apply", True)
            Dispatcher.to_main_page()
        else:
            print "not complete"

    def apply_changes(self, connection):
        wired_device = net_manager.device_manager.get_wired_devices()[0]
        if wired_device.get_state() != 20:
            nm_module.nmclient.activate_connection_async(connection.object_path,
                                               wired_device.object_path,
                                               "/")
            self.device_ethernet = nm_module.cache.get_spec_object(wired_device.object_path)
            self.device_ethernet.emit("try-activate-begin")
        Dispatcher.to_main_page()

class Sections(gtk.Alignment):

    def __init__(self, connection, set_button, settings_obj=None):
        gtk.Alignment.__init__(self, 0, 0 ,0, 0)
        self.set_padding(35, 0, 20, 0)
        self.connection = connection
        self.set_button = set_button
        # 新增settings_obj变量，用于访问shared_methods.Settings对象
        self.settings_obj = settings_obj

        self.main_box = gtk.VBox()
        self.tab_name = "sfds"

        basic = SettingSection(_("Wired"), always_show=True)
        button = Button(_("Advanced"))
        button.connect("clicked", self.show_more_options)

        align = gtk.Alignment(0, 0, 0, 0)
        align.set_padding(0, 0, 285, 0)
        align.add(button)

        basic.load([Wired(self.connection, self.set_button, settings_obj), align])
        self.main_box.pack_start(basic, False, False)
        self.add(self.main_box)
        # align.add(self.button)
        
    def show_more_options(self, widget):
        widget.destroy()
        ipv4 = SettingSection(_("Ipv4 setting"), always_show=True)
        ipv6 = SettingSection(_("Ipv6 setting"), always_show=True)
        ipv4.load([IPV4Conf(self.connection, self.set_button, settings_obj=self.settings_obj)])
        ipv6.load([IPV6Conf(self.connection, self.set_button, settings_obj=self.settings_obj)])

        self.main_box.pack_start(ipv4, False, False, 15)
        self.main_box.pack_start(ipv6, False, False)
        

class Wired(gtk.VBox):
    ENTRY_WIDTH = 222

    def __init__(self, connection, set_button_callback=None, settings_obj=None):
        gtk.VBox.__init__(self)
        self.tab_name = _("Wired")
        
        self.ethernet = connection.get_setting("802-3-ethernet")
        self.connection = connection
        self.set_button = set_button_callback
        # 新增settings_obj变量，用于访问shared_methods.Settings对象
        self.settings_obj = settings_obj

        self.__init_table()
        self.__init_signals()

        (mac, clone_mac, mtu) = self.ethernet.mac_address, self.ethernet.cloned_mac_address, self.ethernet.mtu
        if mac != None:
            self.mac_entry.set_address(mac)
        if clone_mac !=None:
            self.clone_entry.set_address(clone_mac)
        if mtu != None:
            self.mtu_spin.set_value(int(mtu))

    def __init_table(self):
        self.table = TableAsm()
        self.mac_entry = self.table.row_mac_entry(_("Device Mac Address:"))
        self.clone_entry = self.table.row_mac_entry(_("Cloned Mac Address:"))
        self.mtu_spin = self.table.row_spin(_("MTU:"), 0, 1500)
        self.table.table_build()
        # TODO UI change
        align = gtk.Alignment(0,0,0,0)
        align.add(self.table)
        self.pack_start(align)
   
    def __init_signals(self):
        self.mac_entry.connect("changed", self.save_settings, "mac_address")
        self.clone_entry.connect("changed", self.save_settings, "cloned_mac_address")
        self.mtu_spin.connect("value_changed", self.save_settings, "mtu")

        ## retrieve wired info
    def save_settings(self, widget, event, types):
        value = None
        # if widget is SpinBox
        if hasattr(widget, "get_value"):
            value = widget.get_value()
        elif hasattr(widget, "get_text"):
            value = widget.get_text()
        else:
            value = widget.get_address()
        setattr(self.ethernet, types, value)
        # check mac address whether is valid
        if self.settings_obj is None:
            return
        mac_address = event
        cloned_mac_address = event
        if (mac_address == "") or (TypeConvert.is_valid_mac_address(mac_address)):
            mac_address_is_valid = True
        else:
            mac_address_is_valid = False
        if (cloned_mac_address == "") or (TypeConvert.is_valid_mac_address(cloned_mac_address)):
            cloned_mac_address_is_valid = True
        else:
            cloned_mac_address_is_valid = False
        if mac_address_is_valid and cloned_mac_address_is_valid:
            self.settings_obj.mac_is_valid = True
        else:
            self.settings_obj.mac_is_valid = False

        # 统一调用shared_methods.Settings的set_button
        self.settings_obj.set_button("save", True)
        """
        if type(value) is str and value:
            if TypeConvert.is_valid_mac_address(value):
                #widget.set_normal()
                #self.queue_draw()
                setattr(self.ethernet, types, value)
                if self.connection.check_setting_finish():
                    self.set_button("save", True)
            else:
                Dispatcher.set_tip("invalid mac address, please check your settings") 
                #widget.set_warning()
                #self.queue_draw()
                self.set_button("save", False)
                if value is "":
                    #delattr(self.ethernet, types)
                    self.set_button("save", True)
        else:
            setattr(self.ethernet, types, value)
            if self.connection.check_setting_finish():
                self.set_button("save", True)
        """
