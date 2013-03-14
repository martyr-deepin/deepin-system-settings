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
from dss import app_theme
#from dtk.ui.new_entry import InputEntry
from elements import MyInputEntry as InputEntry
from dtk.ui.label import Label
from dtk.ui.spin import SpinBox
from dtk.ui.button import Button
#from dtk.ui.droplist import Droplist
from nm_modules import nm_module
#from widgets import SettingButton
from nmlib.nm_utils import TypeConvert
from nmlib.nmcache import cache
from nmlib.nm_remote_connection import NMRemoteConnection
from ipsettings import IPV4Conf, IPV6Conf
from elements import SettingSection
import gtk
wired_device = []

from constants import  CONTENT_FONT_SIZE, WIDGET_HEIGHT
from shared_methods import Settings
import style
from helper import Dispatcher
from nls import _
from device_manager import device_manager

class WiredSetting(Settings):
    def __init__(self, device, spec_connection=None):
        Settings.__init__(self,[Wired, Sections, IPV6Conf])
        self.crumb_name = _("Wired")
        self.device = device
        self.spec_connection = spec_connection

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
        else:
            print "not complete"

    def apply_changes(self, connection):
        wired_device = device_manager.get_wired_devices()[0]
        if wired_device.get_state() != 20:
            nm_module.nmclient.activate_connection_async(connection.object_path,
                                               wired_device.object_path,
                                               "/")
            self.device_ethernet = cache.get_spec_object(wired_device.object_path)
            self.device_ethernet.emit("try-activate-begin")
        Dispatcher.to_main_page()

class Sections(gtk.Alignment):

    def __init__(self, connection, set_button):
        gtk.Alignment.__init__(self, 0, 0 ,0, 0)
        self.set_padding(35, 0, 50, 0)

        self.main_box = gtk.VBox()
        self.tab_name = "sfds"
        basic = SettingSection(_("Basic") +"(IPV4)")

        self.wired = SettingSection(_("Wired"), always_show=True)
        self.ipv6 = SettingSection(_("Ipv6 setting"), always_show=True)
        align = gtk.Alignment(0, 0, 0, 0)
        align.set_padding(0, 0, 225, 0)
        # align.add(self.button)
        
        basic.load([IPV4Conf(connection, set_button), align])
        self.wired.load([Wired(connection, set_button)])
        self.ipv6.load([IPV6Conf(connection, set_button)])

        self.space = gtk.HBox()
        self.space.set_size_request(-1 ,30)

        self.main_box.pack_start(self.wired, False, False, 15)
        self.main_box.pack_start(basic, False, False)
        self.main_box.pack_start(self.ipv6, False, False)
        
        self.add(self.main_box)

class Wired(gtk.VBox):
    ENTRY_WIDTH = 222

    def __init__(self, connection, set_button_callback=None):
        gtk.VBox.__init__(self)
        self.tab_name = _("Wired")
        
        self.ethernet = connection.get_setting("802-3-ethernet")
        self.connection = connection
        self.set_button = set_button_callback
        table = gtk.Table(3, 2, False)
        
        mac_address = Label(_("Device Mac Address:"),
                            text_size=CONTENT_FONT_SIZE,
                            enable_select=False,
                            enable_double_click=False)
        table.attach(style.wrap_with_align(mac_address, width=210), 0, 1, 0, 1)

        self.mac_entry = InputEntry()
        table.attach(style.wrap_with_align(self.mac_entry), 1, 2, 0, 1)

        clone_addr = Label(_("Cloned Mac Address:"),
                           text_size=CONTENT_FONT_SIZE,
                           enable_select=False,
                           enable_double_click=False)
        table.attach(style.wrap_with_align(clone_addr), 0, 1, 1, 2)
        self.clone_entry = InputEntry()
        table.attach(style.wrap_with_align(self.clone_entry), 1,2, 1, 2)

        mtu = Label(_("MTU:"),
                    enable_select=False,
                    enable_double_click=False)
        table.attach(style.wrap_with_align(mtu), 0,1,2,3)
        self.mtu_spin = SpinBox(0,0, 1500, 1, self.ENTRY_WIDTH)
        table.attach(style.wrap_with_align(self.mtu_spin), 1,2,2,3)
        
        # TODO UI change
        #self.connect("expose-event", expose_background)
        #style.draw_background_color(self)
        style.set_table(table)
        #align = style.set_box_with_align(table, "text")
        align = gtk.Alignment(0,0,0,0)
        #align.set_padding(0, 0, 210, 0)
        align.add(table)
        self.add(align)
        self.mac_entry.set_size(self.ENTRY_WIDTH, WIDGET_HEIGHT)
        self.clone_entry.set_size(self.ENTRY_WIDTH, WIDGET_HEIGHT)
    
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
                print "valid mac"
                widget.ancestor.set_normal()
                self.queue_draw()
                setattr(self.ethernet, types, value)
                if self.connection.check_setting_finish():
                    self.set_button("save", True)
            else:
                print "invalid mac"
                widget.ancestor.set_warning()
                self.queue_draw()
                self.set_button("save", False)
                if value is "":
                    #delattr(self.ethernet, types)
                    self.set_button("save", True)
        else:
            setattr(self.ethernet, types, value)
            if self.connection.check_setting_finish():
                self.set_button("save", True)

