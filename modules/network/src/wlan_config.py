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
from dtk.ui.button import CheckButton
from dtk.ui.new_entry import InputEntry, PasswordEntry
from dtk.ui.label import Label
from dtk.ui.spin import SpinBox
from dtk.ui.utils import container_remove_all
from dtk.ui.combo import ComboBox
from nm_modules import nm_module
from nmlib.nmcache import cache
import gtk

#from nmlib.nm_utils import TypeConvert
from shared_widget import IPV4Conf, IPV6Conf
from nmlib.nm_remote_connection import NMRemoteConnection
import style
from nls import _
from shared_methods import Settings
from helper import Dispatcher

def check_settings(connection, fn):
    if connection.check_setting_finish():
        fn('save', True)
        print "pass"
    else:
        fn("save", False)
        print "not pass"

class WirelessSetting(Settings):

    def __init__(self, ap):
        Settings.__init__(self,[Security,
                                Wireless,
                                IPV4Conf,
                                IPV6Conf],)

        self.crumb_name = _("Wireless Setting")
        self.ap = ap

    def get_ssid(self):
        return self.connections.get_setting("802-11-wireless").ssid

    def get_connections(self):
        self.connections = nm_module.nm_remote_settings.get_ssid_associate_connections(self.ap.get_ssid())
        if self.connections == []:
            self.connections = [nm_module.nm_remote_settings.new_wireless_connection(self.ap.get_ssid())]

        return self.connections
    
    def add_new_connection(self):
        return (nm_module.nm_remote_settings.new_wireless_connection(self.ap.get_ssid()), -1)

    def save_changes(self, connection):
        if connection.check_setting_finish():
            if isinstance(connection, NMRemoteConnection):
                connection.update()
            else:
                connection = nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')
                Dispatcher.emit("connection-replace", connection)
                # reset index
            Dispatcher.set_button("apply", True)
        else:
            print "not complete"

    def apply_changes(self, connection):
        wireless_device = nm_module.nmclient.get_wireless_devices()[0]
        device_wifi = cache.get_spec_object(wireless_device.object_path)
        ssid = connection.get_setting("802-11-wireless").ssid
        ap = device_wifi.get_ap_by_ssid(ssid)

        if ap == None:
            device_wifi.emit("try-ssid-begin", ssid)
            nm_module.nmclient.activate_connection_async(connection.object_path,
                                       wireless_device.object_path,
                                       "/")

        else:
            device_wifi.emit("try-ssid-begin", ssid)
            # Activate
            nm_module.nmclient.activate_connection_async(connection.object_path,
                                       wireless_device.object_path,
                                       ap.object_path)
        Dispatcher.to_main_page()

class NoSetting(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)

        label_align = gtk.Alignment(0.5,0.5,0,0)

        label = Label("No active connection")
        label_align.add(label)
        self.add(label_align)


class Security(gtk.VBox):
    ENTRY_WIDTH = 222

    def __init__(self, connection, set_button_cb):
        gtk.VBox.__init__(self)
        self.tab_name = _("Security")
        self.connection = connection
        self.set_button = set_button_cb
        
        if self.connection.get_setting("802-11-wireless").security == "802-11-wireless-security":
            self.has_security = True
            self.setting = self.connection.get_setting("802-11-wireless-security")
        else:
            self.has_security = False
        self.security_label = Label(_("Security:"),
                                    enable_select=False,
                                    enable_double_click=False)
        self.key_label = Label(_("Key:"),
                               enable_select=False,
                               enable_double_click=False)
        self.wep_index_label = Label(_("Wep index:"),
                                     enable_select=False,
                                     enable_double_click=False)

        self.auth_label = Label(_("Authentication:"),
                                enable_select=False,
                                enable_double_click=False)
        self.password_label = Label(_("Password:"),
                                    enable_select=False,
                                    enable_double_click=False)

        self.encry_list = [(_("None"), None),
                      (_("WEP (Hex or ASCII)"), "none"),
                      (_("WEP 104/128-bit Passphrase"), "none"),
                      (_("WPA WPA2 Personal"), "wpa-psk")]
        #entry_item = map(lambda l: (l[1],l[0]), enumerate(self.encry_list))
        self.security_combo = ComboBox(self.encry_list, max_width=self.ENTRY_WIDTH)
        self.security_combo.set_size_request(self.ENTRY_WIDTH, 22)

        self.key_entry = PasswordEntry()
        self.password_entry = PasswordEntry()
        self.show_key_check = CheckButton(_("Show key"), padding_x=0)
        self.show_key_check.connect("toggled", self.show_key_check_button_cb)
        self.wep_index_spin = SpinBox(0, 0, 3, 1, self.ENTRY_WIDTH)
        self.auth_combo = ComboBox([(_("Open System"), "open"),
                                    (_("Shared Key"), "shared")], max_width=self.ENTRY_WIDTH)

        ## Create table
        self.table = gtk.Table(5, 4, True)
        #TODO UI change
        label_list = ["security_label", "key_label", "wep_index_label", "auth_label", "password_label", "password_entry", "key_entry", "wep_index_spin", "auth_combo", "security_combo"]
        for label in label_list:
            l = getattr(self, label)
            align = style.wrap_with_align(l)
            setattr(self, label+"_align", align)

        self.show_key_check_align = style.wrap_with_align(self.show_key_check, align="left")

        self.reset(self.has_security)
        self.security_combo.connect("item-selected", self.change_encry_type)
        self.key_entry.entry.connect("changed", self.save_wep_pwd)
        self.password_entry.entry.connect("changed", self.save_wpa_pwd)
        self.wep_index_spin.connect("value-changed", self.wep_index_spin_cb)
        self.auth_combo.connect("item-selected", self.save_auth_cb)
        
        style.set_table(self.table)
        style.draw_background_color(self)
        align = style.set_box_with_align(self.table, "text")
        width, height = self.ENTRY_WIDTH, 22
        self.key_entry.set_size(width, height)
        self.password_entry.set_size(width, height)
        self.wep_index_spin.set_size_request(width, height)
        self.auth_combo.set_size_request(width, height)
        self.security_combo.set_size_request(width, height)

        self.add(align)

    def reset(self, security=True):
        ## Add security
        container_remove_all(self.table)

        self.table.attach(self.security_label_align, 0, 1, 0, 1)
        self.table.attach(self.security_combo_align, 1, 4, 0, 1)

        if not security:
            return 
        
        keys = [None, "none", "none","wpa-psk"]
        
        self.key_mgmt = self.setting.key_mgmt
        if self.key_mgmt == "none":
            key_type = self.setting.wep_key_type
            self.security_combo.set_select_index(key_type)
        else:
            self.security_combo.set_select_index(keys.index(self.key_mgmt))
        
        if not self.security_combo.get_current_item()[1] == None: 
            try:
                (setting_name, method) = self.connection.guess_secret_info() 
                secret = nm_module.secret_agent.agent_get_secrets(self.connection.object_path,
                                                        setting_name,
                                                        method)
            except:
                secret = ""

            if self.security_combo.get_current_item()[1] == "wpa-psk":
                self.table.attach(self.password_label_align, 0, 1, 1, 2)
                self.table.attach(self.password_entry_align, 1, 4, 1, 2)
                self.table.attach(self.show_key_check_align, 1, 4, 2, 3)
                
                self.password_entry.entry.set_text(secret)
                if secret:
                    Dispatcher.set_button("save", True)
                self.setting.psk = secret

            elif self.security_combo.get_current_item()[1] == "none":
                # Add Key
                self.table.attach(self.key_label_align, 0, 1, 1, 2)
                self.table.attach(self.key_entry_align, 1, 4, 1, 2)
                self.table.attach(self.show_key_check_align, 1, 4, 2, 3)
                # Add wep index
                self.table.attach(self.wep_index_label_align, 0, 1, 3, 4)
                self.table.attach(self.wep_index_spin_align, 1, 4, 3, 4)
                # Add Auth
                self.table.attach(self.auth_label_align, 0, 1, 4, 5)
                self.table.attach(self.auth_combo_align, 1, 4, 4, 5)

                # Retrieve wep properties
                try:
                    index = self.setting.wep_tx_keyidx
                    auth = self.setting.auth_alg
                    self.auth_combo.set_select_index(["open", "shared"].index(auth))
                except:
                    index = 0
                    auth = "open"
                # must convert long int to int 
                index = int(index)
                
                #init_key = True
                #if isinstance(self.connection, NMRemoteConnection):
                    #init_setting = self.connection.get_setting("802-11-wireless-security")
                    #if init_setting.wep_key_type != self.setting.wep_key_type:
                        #init_key = False

                #if init_key:
                self.key_entry.entry.set_text(secret)
                self.setting.set_wep_key(index, secret)
                self.wep_index_spin.set_value(index)
                self.auth_combo.set_select_index(["open", "shared"].index(auth))
        self.queue_draw()

    def change_encry_type(self, widget, content, value, index):
        print content, value, index
        if value == None:
            self.connection.del_setting("802-11-wireless-security")
            del self.connection.get_setting("802-11-wireless").security
            self.has_security = False
            self.reset(self.has_security)
            Dispatcher.set_button("save", True)
        else:
            if self.has_security == False:
                self.connection.get_setting("802-11-wireless").security = "802-11-wireless-security"
                self.connection.reinit_setting("802-11-wireless-security")
                self.setting = self.connection.get_setting("802-11-wireless-security")
            self.has_security = True
            self.setting.key_mgmt = value
            if value == "none":
                del self.setting.psk
                self.setting.wep_key_type = index
                for key in range(0, 4):
                    delattr(self.setting, "wep_key%d"%key)
            Dispatcher.set_button("save", False)
            self.reset()

    def save_wpa_pwd(self, widget, content):
        if self.setting.verify_wpa_psk(content):
            self.setting.psk = content
            check_settings(self.connection, self.set_button)
        else:
            Dispatcher.set_button("save", False)
            print "invalid"

    def save_wep_pwd(self, widget, content):
        active = self.setting.wep_tx_keyidx
        wep_type = self.setting.wep_key_type
        if self.setting.verify_wep_key(content, wep_type):
            self.setting.set_wep_key(active, content)
            check_settings(self.connection, self.set_button)
            print "wep_valid"
        else:
            Dispatcher.set_button("save", False)
            print "invalid"

    
    def show_key_check_button_cb(self, widget):
        name = self.security_combo.get_current_item()[1]
        entry = [self.password_entry, self.key_entry][name=="none"]
        if widget.get_active():
            entry.show_password(True)
        else:
            entry.show_password(False)
    
    def save_auth_cb(self, widget, content, value, index):
        self.setting.auth_alg = value
        self.reset()

    def wep_index_spin_cb(self, widget, value):
        if isinstance(self.connection, NMRemoteConnection):
            key = nm_module.secret_agent.agent_get_secrets(self.connection.object_path,
                                                       "802-11-wireless-security",
                                                       "wep-key%d"%value)
        else:
            key = self.setting.get_wep_key(value)

        if not key:
            key = ''
        self.key_entry.entry.set_text(key)
        self.setting.wep_tx_keyidx = value
        #self.key_entry.queue_draw()

    def save_setting(self):
        # Save wpa settings
        active = self.security_combo.get_current_item()[1]
        if active == 0:
            pass
        elif active == 3:
            passwd = self.password_entry.entry.get_text()
            key_mgmt = "wpa-psk"
            self.setting.key_mgmt = key_mgmt

            self.setting.psk = passwd
        else:
            passwd = self.key_entry.entry.get_text()
            index = self.wep_index_spin.get_value()
            key_mgmt = "none"
            auth_active = self.auth_combo.get_current_item()[0]

            self.setting.key_mgmt = key_mgmt
            self.setting.wep_key_type = active
            self.setting.set_wep_key(index, passwd)
            self.setting.wep_tx_keyidx = index
            if auth_active == 0:
                self.setting.auth_alg = "open"
            else:
                self.setting.auth_alg = "shared"
            del self.setting.psk

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
    ENTRY_WIDTH = 222

    def __init__(self, connection, set_button_cb):
        gtk.VBox.__init__(self)
        self.tab_name = _("Wireless")
        self.connection = connection 
        self.set_button = set_button_cb
        self.wireless = self.connection.get_setting("802-11-wireless")
        ### UI
        self.ssid_label = Label(_("SSID:"),
                                enable_select=False,
                                enable_double_click=False)
        self.ssid_entry = InputEntry()

        self.mode_label = Label(_("Mode:"),
                               enable_select=False,
                               enable_double_click=False)
        self.mode_combo = ComboBox([(_("Infrastructure"),"infrastructure"),(_("Ad-hoc"), "adhoc")], max_width=self.ENTRY_WIDTH)
        
        # TODO need to put this section to personal wifi
        self.band_label = Label(_("Band:"),
                               enable_select=False,
                               enable_double_click=False)
                                
        self.band_combo = ComboBox([(_("Automatic"), None),
                                    ("a (5 GHZ)", "a"),
                                    ("b/g (2.4)", "bg")],
                                    max_width=self.ENTRY_WIDTH)
        self.channel_label = Label(_("Channel:"),
                                   enable_select=False,
                                   enable_double_click=False)
        self.channel_spin = SpinBox(0, 0, 1500, 1, self.ENTRY_WIDTH)
        # BSSID
        self.bssid_label = Label(_("BSSID:"),
                                 enable_select=False,
                                 enable_double_click=False)
        self.bssid_entry = InputEntry()
        self.mac_address = Label(_("Device Mac Address:"),
                                 enable_select=False,
                                 enable_double_click=False)
        self.mac_entry = InputEntry()
        self.clone_addr = Label(_("Cloned Mac Address:"),
                                 enable_select=False,
                                 enable_double_click=False)
        self.clone_entry = InputEntry()

        self.mtu = Label(_("MTU:"),
                           enable_select=False,
                           enable_double_click=False)
        self.mtu_spin = SpinBox(0, 0, 1500, 1, self.ENTRY_WIDTH)

        self.table = gtk.Table(8, 2, False)

        """
        wrap with alignment
        """
        widget_list = ["ssid_label", "ssid_entry", "mode_label", "mode_combo",
                       "band_label", "band_combo", "channel_label", "channel_spin",
                       "bssid_label", "bssid_entry", "mac_address", "mac_entry",
                       "clone_addr", "clone_entry", "mtu", "mtu_spin"]

        for widget in widget_list:
            item = getattr(self, widget)
            align = style.wrap_with_align(item)
            setattr(self, widget + "_align", align)

        #TODO UI change
        style.draw_background_color(self)
        align = style.set_box_with_align(self.table, 'text')
        style.set_table(self.table)
        self.add(align)
        #self.table.set_size_request(340, 227)

        self.ssid_entry.set_size(self.ENTRY_WIDTH, 22)
        self.bssid_entry.set_size(self.ENTRY_WIDTH, 22)
        self.mac_entry.set_size(self.ENTRY_WIDTH, 22)
        self.clone_entry.set_size(self.ENTRY_WIDTH, 22)

        self.reset()
        #self.mode_combo.connect("item-selected", self.mode_combo_selected)
        self.band_combo.connect("item-selected", self.band_combo_selected)
        self.mtu_spin.connect("value-changed", self.spin_value_changed, "mtu")
        self.channel_spin.connect("value-changed", self.spin_value_changed, "channel")
        self.ssid_entry.entry.connect("changed", self.entry_changed, "ssid")
        self.bssid_entry.entry.connect("changed", self.entry_changed, "bssid")
        self.mac_entry.entry.connect("changed", self.entry_changed, "mac_address")
        self.clone_entry.entry.connect("changed", self.entry_changed, "cloned_mac_address")


    def spin_value_changed(self, widget, value, types):
        setattr(self.wireless, types, value)

    def entry_changed(self, widget, content, types):
        if types.endswith("ssid"):
            setattr(self.wireless, types, content)
        else:
            from nmlib.nm_utils import TypeConvert
            if TypeConvert.is_valid_mac_address(content):
                setattr(self.ethernet, types, content)
                check_settings(self.connection, self.set_button)
            else:
                Dispatcher.set_button("save", False)

    def band_combo_selected(self, widget, content, value, index):
        self.wirless.band = value


    def mode_combo_selected(self, widget, content, value, index):
        self.wireless.mode = value
        self.wireless.adapt_wireless_commit()
        self.reset_table()

    def reset_table(self):
        container_remove_all(self.table)
        mode = self.mode_combo.get_current_item()[1]

        self.table.attach(self.ssid_label_align, 0, 1, 0, 1)
        self.table.attach(self.ssid_entry_align, 1, 2, 0, 1)
        # Mode
        self.table.attach(self.mode_label_align, 0, 1, 1, 2)
        self.table.attach(self.mode_combo_align, 1, 2, 1, 2)
        if mode == "adhoc":
            self.table.attach(self.band_label_align, 0, 1, 2, 3)
            self.table.attach(self.band_combo_align, 1, 2, 2, 3)
            self.table.attach(self.channel_label_align, 0, 1, 3, 4)
            self.table.attach(self.channel_spin_align, 1, 2, 3, 4)

        # Bssid
        self.table.attach(self.bssid_label_align, 0, 1, 4, 5)
        self.table.attach(self.bssid_entry_align, 1, 2, 4, 5)

        # MAC
        self.table.attach(self.mac_address_align, 0, 1, 5, 6)
        self.table.attach(self.mac_entry_align, 1, 2, 5, 6)
        # MAC_CLONE
        self.table.attach(self.clone_addr_align, 0, 1, 6, 7)
        self.table.attach(self.clone_entry_align, 1,2, 6, 7)
        # MTU
        self.table.attach(self.mtu_spin_align, 1, 2, 7, 8)
        self.table.attach(self.mtu_align, 0, 1, 7, 8)

    def reset(self):
        wireless = self.wireless
        ## retrieve wireless info
        if wireless.ssid != None:
            self.ssid_entry.set_text(wireless.ssid)

        if wireless.bssid != None:
            self.bssid_entry.set_text(wireless.bssid)

        if wireless.mode == 'infrastructure':
            #self.mode_combo.set_select_index(0)
            self.mode_combo.set_select_index(0)
        else:
            #self.mode_combo.set_select_index(1)
            self.mode_combo.set_select_index(1)

        if wireless.mac_address != None:
            self.mac_entry.set_text(wireless.mac_address)

        if wireless.cloned_mac_address !=None:
            self.clone_entry.set_text(wireless.cloned_mac_address)

        if wireless.mtu != None:
            self.mtu_spin.set_value(int(wireless.mtu))
        
        self.reset_table()

    
    def save_change(self):
        
        self.wireless.ssid = self.ssid_entry.get_text()
        self.wireless.mode = self.mode_combo.get_current_item()[0]

        if self.bssid_entry.get_text() != "":
            self.wireless.bssid = self.bssid_entry.get_text()
        if self.mac_entry.get_text() != "":
            self.wireless.mac_address = self.mac_entry.get_text()
        if self.clone_entry.get_text() != "":
            self.wireless.cloned_mac_address = self.clone_entry.get_text()

        self.wireless.mtu = self.mtu_spin.get_value()
        self.wireless.adapt_wireless_commit()

