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
from dtk.ui.button import CheckButton, Button
from dtk.ui.entry import InputEntry, PasswordEntry
from dtk.ui.net import MACEntry
from dtk.ui.label import Label
from dtk.ui.spin import SpinBox
from dtk.ui.utils import container_remove_all
from dtk.ui.combo import ComboBox
from nm_modules import nm_module
import gtk

#from nmlib.nm_utils import TypeConvert
from ipsettings import IPV4Conf, IPV6Conf
from elements import SettingSection
from nmlib.nm_remote_connection import NMRemoteConnection
import style
from nls import _
from shared_methods import Settings, net_manager
from helper import Dispatcher, event_manager

def check_settings(connection, fn):
    if connection.check_setting_finish():
        Dispatcher.set_button('save', True)
        print "pass"
        #print connection.get_setting("802-11-wireless-security").prop_dict
    else:
        Dispatcher.set_button("save", False)
        print "not pass, ==================>"
        #print connection.get_setting("802-11-wireless-security").prop_dict

class WirelessSetting(Settings):
    def __init__(self, ap, spec_connection=None):
        Settings.__init__(self,[Security,
                                Sections,
                                IPV4Conf,
                                IPV6Conf],)
        if ap:
            self.crumb_name = ap.get_ssid()
        else:
            self.crumb_name = ""
        self.spec_connection = spec_connection
        event_manager.emit("update-delete-button", False)

    def get_ssid(self):
        return self.connections.get_setting("802-11-wireless").ssid

    def get_connections(self):
        self.connections = nm_module.nm_remote_settings.get_ssid_associate_connections(self.crumb_name)
        if self.connections == []:
            self.connections = [nm_module.nm_remote_settings.new_wireless_connection(self.crumb_name, None)]

        return self.connections
    
    def add_new_connection(self):
        return (nm_module.nm_remote_settings.new_wireless_connection(self.crumb_name, None), -1)
    
    def save_changes(self, connection):
        print "save changes"
        if connection.check_setting_finish():
            if isinstance(connection, NMRemoteConnection):
                connection.update()
            else:
                connection = nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')
                Dispatcher.emit("connection-replace", connection)
                #Dispatcher.emit("wireless-redraw")
                # reset index
            #self.apply_changes(connection)
            #Dispatcher.set_button("apply", True)
            Dispatcher.to_main_page()
        else:
            print "not complete"
        #self.setting_group.set_button(connection)
    def apply_changes(self, connection):
        print "apply changes"
        wireless_device = net_manager.device_manager.get_wireless_devices()[0]
        if wireless_device.get_state() == 100:
            return
        device_wifi = nm_module.cache.get_spec_object(wireless_device.object_path)
        ssid = connection.get_setting("802-11-wireless").ssid
        ap = device_wifi.get_ap_by_ssid(ssid)

        if ap == None:
            #device_wifi.emit("try-ssid-begin", ssid)
            nm_module.nmclient.activate_connection_async(connection.object_path,
                                       wireless_device.object_path,
                                       "/")

        else:
            #device_wifi.emit("try-ssid-begin", ssid)
            # Activate
            nm_module.nmclient.activate_connection_async(connection.object_path,
                                       wireless_device.object_path,
                                       ap.object_path)

class HiddenSetting(Settings):
    
    def __init__(self, connection, spec_connection=None):
        Settings.__init__(self, [Sections])
        #self.settings_dict = Sections
        self.connection = connection
        self.spec_connection = spec_connection
        self.crumb_name = _("Hidden network")

    def init_items(self, connection):
        self.connection = connection
        if connection not in self.settings:
            self.setting_lock[connection] = True
            #self.init_button_state(connection)
            setting_list = []
            for setting in self.setting_list:
                s = setting(connection, self.set_button, True)
                setting_list.append((s.tab_name, s))
            self.settings[connection] = setting_list
        return self.settings[connection][0][1]

    def get_connections(self):
        if self.connection:
            return [self.connection]
        else:
            return [nm_module.nm_remote_settings.new_wireless_connection("", None)]

    def delete_request_redraw(self):
        net_manager.remove_hidden(self.connection)
        Dispatcher.emit("wireless-redraw")

    def add_new_connection(self):
        pass

    def save_changes(self, connection):
        if isinstance(connection, NMRemoteConnection):
            connection.update()
        else:
            connection = nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')
            #Dispatcher.emit("connection-replace", connection)
            net_manager.add_hidden(connection)
        Dispatcher.to_main_page()
        Dispatcher.emit("wireless-redraw")

class NoSetting(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)

        label_align = gtk.Alignment(0.5,0.5,0,0)

        label = Label("No active connection")
        label_align.add(label)
        self.add(label_align)

class Sections(gtk.Alignment):

    def __init__(self, connection, set_button, need_ssid=False, settings_obj=None):
        gtk.Alignment.__init__(self, 0, 0 ,0, 0)
        self.set_padding(35, 0, 20, 0)
        self.connection = connection
        self.set_button = set_button
        # 新增settings_obj变量，用于访问shared_methods.Settings对象
        self.settings_obj = settings_obj

        self.main_box = gtk.VBox()
        self.tab_name = "sfds"
        basic = SettingSection(_("Basic"))

        if need_ssid:
            security = Security(connection, set_button, need_ssid, settings_obj=settings_obj)
        else:
            security = Security(connection, set_button, settings_obj=settings_obj)
        security.button.connect("clicked", self.show_more_options)
        basic.load([security])


        self.main_box.pack_start(basic, False, False)

        self.add(self.main_box)

    def show_more_options(self, widget):
        widget.parent.destroy()
        self.wireless = SettingSection(_("Wireless"), always_show=True)
        self.ipv4 = SettingSection(_("Ipv4 setting"), always_show=True)
        self.ipv6 = SettingSection(_("Ipv6 setting"), always_show=True)
        self.wireless.load([Wireless(self.connection, self.set_button, settings_obj=self.settings_obj)])
        self.ipv4.load([IPV4Conf(self.connection, self.set_button, settings_obj=self.settings_obj)])
        self.ipv6.load([IPV6Conf(self.connection, self.set_button, settings_obj=self.settings_obj)])
        self.main_box.pack_start(self.wireless, False, False, 15)
        self.main_box.pack_start(self.ipv4, False, False)
        self.main_box.pack_start(self.ipv6, False, False, 15)

class Security(gtk.VBox):
    ENTRY_WIDTH = 222

    def __init__(self, connection, set_button_cb, need_ssid=False, settings_obj=None):
        gtk.VBox.__init__(self)
        self.tab_name = _("Security")
        self.connection = connection
        self.set_button = set_button_cb
        # 新增settings_obj变量，用于访问shared_methods.Settings对象
        self.settings_obj = settings_obj

        self.need_ssid = need_ssid

        self.add_ssid_entry()
        
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
        self.security_combo = ComboBox(self.encry_list, fixed_width=self.ENTRY_WIDTH)
        #self.security_combo.set_size_request(self.ENTRY_WIDTH, 22)

        self.key_entry = PasswordEntry()
        self.password_entry = PasswordEntry()
        self.show_key_check = CheckButton(_("Show key"), padding_x=0)
        self.show_key_check.connect("toggled", self.show_key_check_button_cb)
        self.wep_index_spin = SpinBox(0, 0, 3, 1, self.ENTRY_WIDTH)
        self.auth_combo = ComboBox([
                                    (_("Shared Key"), "shared"),
                                    (_("Open System"), "open")],fixed_width=self.ENTRY_WIDTH)

        ## advance button
        self.align = gtk.Alignment(0, 1.0, 0, 0)
        self.align.set_padding(0, 0, 376, 0)
        self.align.set_size_request(-1 ,30)
        self.button = Button(_("Advanced"))
        self.align.add(self.button)

        ## Create table
        self.table = gtk.Table(5, 4)
        #TODO UI change
        label_list = ["security_label", "key_label", "wep_index_label", "auth_label", "password_label"]
        widget_list = ["password_entry", "key_entry", "wep_index_spin", "auth_combo", "security_combo"]
        for label in label_list:
            l = getattr(self, label)
            l.set_can_focus(False)
            align = style.wrap_with_align(l, width=210)
            setattr(self, label+"_align", align)

        for w in widget_list:
            l = getattr(self, w)
            align = style.wrap_with_align(l, align="left")
            setattr(self, w+"_align", align)

        self.show_key_check_align = style.wrap_with_align(self.show_key_check, align="left")

        self.reset(self.has_security)
        self.security_combo.connect("item-selected", self.change_encry_type)
        self.key_entry.entry.connect("changed", self.save_wep_pwd)
        self.password_entry.entry.connect("changed", self.save_wpa_pwd)
        self.wep_index_spin.connect("value-changed", self.wep_index_spin_cb)
        self.auth_combo.connect("item-selected", self.save_auth_cb)
        
        style.set_table(self.table)
        table_align = gtk.Alignment(0, 0, 0, 0)
        table_align.add(self.table)
        style.draw_background_color(self)
        width, height = self.ENTRY_WIDTH, 22
        self.key_entry.set_size(width, height)
        self.password_entry.set_size(width, height)
        self.wep_index_spin.set_size_request(width, height)
        self.auth_combo.set_size_request(width, height)
        self.security_combo.set_size_request(width, height)
        self.pack_start(table_align, False, False)
        self.pack_start(self.align, False, False, 0)

    def add_ssid_entry(self):
        self.wireless = self.connection.get_setting("802-11-wireless")
        self.ssid_label = Label(_("SSID:"),
                                enable_select=False,
                                enable_double_click=False)
        self.ssid_label_align = style.wrap_with_align(self.ssid_label, width=210)
        self.ssid_entry = MACEntry()
        self.ssid_entry.set_size_request(130, 22)
        self.ssid_entry_align = style.wrap_with_align(self.ssid_entry, align="left")
        self.ssid_entry.connect("changed", self.set_ssid)
        self.ssid_entry.set_address(self.wireless.ssid)

        #self.add(align)

    def set_ssid(self, widget, content):
        self.wireless.ssid = content
        check_settings(self.connection, None)

    def advand_cb(self, widget):
        pass

    def reset(self, security=True):
        ## Add security
        container_remove_all(self.table)
        if self.need_ssid:
            self.table.attach(self.ssid_label_align, 0, 1, 0, 1)
            self.table.attach(self.ssid_entry_align, 1, 4, 0, 1)
        
        self.table.resize(2, 4)
        self.table.attach(self.security_label_align, 0, 1, 1, 2)
        self.table.attach(self.security_combo_align, 1, 4, 1, 2)

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
                self.setting.psk = secret
            except:
                secret = ""

            if self.security_combo.get_current_item()[1] == "wpa-psk":
                self.table.resize(4, 4)
                self.table.attach(self.password_label_align, 0, 1, 2, 3)
                self.table.attach(self.password_entry_align, 1, 4, 2, 3)
                self.table.attach(self.show_key_check_align, 1, 4, 3, 4)
                
                self.password_entry.entry.set_text(secret)
                if secret:
                    #Dispatcher.set_button("save", True)
                    ###########
                    self.settings_obj.wlan_encry_is_valid = True
                    self.settings_obj.set_button("save", True)
                self.setting.psk = secret

            elif self.security_combo.get_current_item()[1] == "none":
                self.table.resize(6, 4)
                # Add Key
                self.table.attach(self.key_label_align, 0, 1, 2, 3)
                self.table.attach(self.key_entry_align, 1, 4, 2, 3)
                self.table.attach(self.show_key_check_align, 1, 4, 3, 4)
                # Add wep index
                self.table.attach(self.wep_index_label_align, 0, 1, 4, 5)
                self.table.attach(self.wep_index_spin_align, 1, 4, 4, 5)
                # Add Auth
                self.table.attach(self.auth_label_align, 0, 1, 5, 6)
                self.table.attach(self.auth_combo_align, 1, 4, 5, 6)

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

        Dispatcher.request_redraw()

    def change_encry_type(self, widget, content, value, index):
        print content, value, index
        if value == None:
            self.connection.del_setting("802-11-wireless-security")
            del self.connection.get_setting("802-11-wireless").security
            self.has_security = False
            self.reset(self.has_security)
            #Dispatcher.set_button("save", True)
            self.settings_obj.wlan_encry_is_valid = True
            self.settings_obj.set_button("save", True)
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
            #Dispatcher.set_button("save", False)
            self.reset()
            self.settings_obj.wlan_encry_is_valid = False
            self.settings_obj.set_button("save", False)

    def save_wpa_pwd(self, widget, content):
        is_valid = False
        if self.setting.verify_wpa_psk(content):
            self.setting.psk = content
            #print "in save wpa pwd", self.connection.settings_dict
            #check_settings(self.connection, self.set_button)
        #else:
            #Dispatcher.set_button("save", False)
            #print "invalid"
            #######
            is_valid = self.connection.check_setting_finish()
        self.settings_obj.wlan_encry_is_valid = is_valid
        self.settings_obj.set_button("save", is_valid)

    def save_wep_pwd(self, widget, content):
        active = self.setting.wep_tx_keyidx
        wep_type = self.setting.wep_key_type
        is_valid = False
        if self.setting.verify_wep_key(content, wep_type):
            self.setting.set_wep_key(active, content)
            #check_settings(self.connection, self.set_button)
        #else:
            #Dispatcher.set_button("save", False)
            #print "invalid"
            is_valid = self.connection.check_setting_finish()
        self.settings_obj.wlan_encry_is_valid = is_valid
        self.settings_obj.set_button("save", is_valid)
    
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
            try:
                key = self.setting.get_wep_key(value)
            except:
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
        wireless_device = net_manager.device_manager.get_wireless_devices()[0]
        device_wifi = nm_module.cache.get_spec_object(wireless_device.object_path)
        setting = self.connection.get_setting("802-11-wireless")
        ssid = setting.ssid
        ap = device_wifi.get_ap_by_ssid(ssid)
        # Activate
        nm_module.nmclient.activate_connection_async(self.connection.object_path,
                                   wireless_device.object_path,
                                   ap.object_path)

class Wireless(gtk.VBox):
    ENTRY_WIDTH = 222

    def __init__(self, connection, set_button_cb, settings_obj=None):
        gtk.VBox.__init__(self)
        self.tab_name = _("Wireless")
        self.connection = connection 
        self.set_button = set_button_cb
        # 新增settings_obj变量，用于访问shared_methods.Settings对象
        self.settings_obj = settings_obj

        self.wireless = self.connection.get_setting("802-11-wireless")
        ### UI
        self.ssid_label = Label(_("SSID:"),
                                enable_select=False,
                                enable_double_click=False)
        self.ssid_entry = MACEntry()

        self.mode_label = Label(_("Mode:"),
                               enable_select=False,
                               enable_double_click=False)
        self.mode_combo = ComboBox([(_("Infrastructure"),"infrastructure"),(_("Ad-hoc"), "adhoc")], fixed_width=130)
        
        # TODO need to put this section to personal wifi
        self.band_label = Label(_("Band:"),
                               enable_select=False,
                               enable_double_click=False)
                                
        self.band_combo = ComboBox([(_("Automatic"), None),
                                    ("a (5 GHZ)", "a"),
                                    ("b/g (2.4)", "bg")],
                                    fixed_width=self.ENTRY_WIDTH)
        self.channel_label = Label(_("Channel:"),
                                   enable_select=False,
                                   enable_double_click=False)
        self.channel_spin = SpinBox(0, 0, 1500, 1, self.ENTRY_WIDTH)
        # BSSID
        self.bssid_label = Label(_("BSSID:"),
                                 enable_select=False,
                                 enable_double_click=False)
        self.bssid_entry = MACEntry()
        self.mac_address_label = Label(_("Device Mac Address:"),
                                 enable_select=False,
                                 enable_double_click=False)
        self.mac_entry = MACEntry()
        self.clone_addr_label = Label(_("Cloned Mac Address:"),
                                 enable_select=False,
                                 enable_double_click=False)
        self.clone_entry = MACEntry()

        self.mtu_label = Label(_("MTU:"),
                           enable_select=False,
                           enable_double_click=False)
        self.mtu_spin = SpinBox(0, 0, 1500, 1, 130)

        self.table = gtk.Table(8, 2, False)

        """
        wrap with alignment
        """
        widget_list = ["ssid_label", "ssid_entry", "mode_label", "mode_combo",
                       "band_label", "band_combo", "channel_label", "channel_spin",
                       "bssid_label", "bssid_entry", "mac_address_label", "mac_entry",
                       "clone_addr_label", "clone_entry", "mtu_label", "mtu_spin"]

        for widget in widget_list:
            item = getattr(self, widget)
            if widget.endswith("label"):
                item.set_can_focus(False)
                align = style.wrap_with_align(item, width=210)
            else:
                align = style.wrap_with_align(item, align="left")
            setattr(self, widget + "_align", align)

        #TODO UI change
        style.draw_background_color(self)
        #align = style.set_box_with_align(self.table, 'text')
        style.set_table(self.table)

        section = SettingSection(_("Default Settings"), always_show= False, revert=True, label_right=True, has_seperator=False)
        section.load([self.table])
        self.pack_start(section, False, False)
        #self.pack_start(self.table, False, False)
        #self.table.set_size_request(340, 227)

        self.ssid_entry.set_size_request(130, 22)
        self.bssid_entry.set_size_request(130, 22)
        self.mac_entry.set_size_request(130, 22)
        self.clone_entry.set_size_request(130, 22)

        self.reset()
        #self.mode_combo.connect("item-selected", self.mode_combo_selected)
        self.band_combo.connect("item-selected", self.band_combo_selected)
        self.mtu_spin.connect("value-changed", self.spin_value_changed, "mtu")
        self.channel_spin.connect("value-changed", self.spin_value_changed, "channel")
        self.ssid_entry.connect("changed", self.entry_changed, "ssid")
        self.bssid_entry.connect("changed", self.entry_changed, "bssid")
        self.mac_entry.connect("changed", self.entry_changed, "mac_address")
        self.clone_entry.connect("changed", self.entry_changed, "cloned_mac_address")

    def spin_value_changed(self, widget, value, types):
        setattr(self.wireless, types, value)

    def entry_changed(self, widget, content, types):
        is_valid = True
        if types.endswith("ssid"):
            setattr(self.wireless, types, content)
        else:
            from nmlib.nm_utils import TypeConvert
            if TypeConvert.is_valid_mac_address(content):
                setattr(self.wireless, types, content)
                #check_settings(self.connection, self.set_button)
                is_valid = self.connection.check_setting_finish()
            else:
                is_valid = False
                #Dispatcher.set_button("save", False)
        self.settings_obj.mac_is_valid = is_valid
        self.settings_obj.set_button("save", is_valid)

    def band_combo_selected(self, widget, content, value, index):
        self.wirless.band = value

    def mode_combo_selected(self, widget, content, value, index):
        self.wireless.mode = value
        self.wireless.adapt_wireless_commit()
        self.reset_table()

    def reset_table(self):
        container_remove_all(self.table)
        mode = self.mode_combo.get_current_item()[1]

        #self.table.attach(self.ssid_label_align, 0, 1, 0, 1)
        #self.table.attach(self.ssid_entry_align, 1, 2, 0, 1)
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
        self.table.attach(self.mac_address_label_align, 0, 1, 5, 6)
        self.table.attach(self.mac_entry_align, 1, 2, 5, 6)
        # MAC_CLONE
        self.table.attach(self.clone_addr_label_align, 0, 1, 6, 7)
        self.table.attach(self.clone_entry_align, 1,2, 6, 7)
        # MTU
        self.table.attach(self.mtu_spin_align, 1, 2, 7, 8)
        self.table.attach(self.mtu_label_align, 0, 1, 7, 8)

    def reset(self):
        wireless = self.wireless
        ## retrieve wireless info
        if wireless.ssid != None:
            self.ssid_entry.set_address(wireless.ssid)

        if wireless.bssid != None:
            self.bssid_entry.set_address(wireless.bssid)

        if wireless.mode == 'infrastructure':
            #self.mode_combo.set_select_index(0)
            self.mode_combo.set_select_index(0)
        else:
            #self.mode_combo.set_select_index(1)
            self.mode_combo.set_select_index(1)

        if wireless.mac_address != None:
            self.mac_entry.set_address(wireless.mac_address)

        if wireless.cloned_mac_address !=None:
            self.clone_entry.set_address(wireless.cloned_mac_address)

        if wireless.mtu != None:
            self.mtu_spin.set_value(int(wireless.mtu))
        
        self.reset_table()

    
    def save_change(self):
        
        self.wireless.ssid = self.ssid_entry.get_address()
        self.wireless.mode = self.mode_combo.get_current_item()[0]

        if self.bssid_entry.get_address() != "":
            self.wireless.bssid = self.bssid_entry.get_address()
        if self.mac_entry.get_address() != "":
            self.wireless.mac_address = self.mac_entry.get_address()
        if self.clone_entry.get_address() != "":
            self.wireless.cloned_mac_address = self.clone_entry.get_address()

        self.wireless.mtu = self.mtu_spin.get_value()
        self.wireless.adapt_wireless_commit()

