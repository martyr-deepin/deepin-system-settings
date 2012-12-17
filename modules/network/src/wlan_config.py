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
from dtk.ui.button import Button,CheckButton
from dtk.ui.new_entry import InputEntry, PasswordEntry
from dtk.ui.label import Label
from dtk.ui.spin import SpinBox
from dtk.ui.utils import container_remove_all
from dtk.ui.combo import ComboBox
from nm_modules import nm_module
from nmlib.nmcache import cache
#from widgets import SettingButton
from settings_widget import EntryTreeView, SettingItem, ShowOthers
import gtk

#from nmlib.nm_utils import TypeConvert
from shared_widget import IPV4Conf, IPV6Conf
from nmlib.nm_remote_connection import NMRemoteConnection

def check_settings(connection, fn):
    if connection.check_setting_finish():
        fn('save', True)
        print "pass"
    else:
        fn("save", False)
        print "not pass"

class WirelessSetting(gtk.HBox):

    def __init__(self, slide_back_cb, change_crumb_cb):

        gtk.HBox.__init__(self)
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

        self.sidebar = SideBar( None,self.init, self.check_click, self.set_button)

        # Build ui
        self.pack_start(self.sidebar, False , False)
        vbox = gtk.VBox()
        vbox.connect("expose-event", self.expose_event)
        vbox.pack_start(self.tab_window ,True, True)
        self.pack_start(vbox, True, True)
        self.save_button = Button("Apply")
        self.save_button.connect("clicked", self.save_changes)
        #hbox.pack_start(apply_button, False, False, 0)
        buttons_aligns = gtk.Alignment(0.5 , 1, 0, 0)
        buttons_aligns.add(self.save_button)
        vbox.pack_start(buttons_aligns, False , False)
        #hbox.connect("expose-event", self.hbox_expose_event)

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb( 1, 1, 1) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

    def init(self, access_point, new_connection_list=None, init_connections=False):
        self.ssid = access_point
        if init_connections:
            self.sidebar.new_connection_list = []
        # Get all connections  
        connection_associate = nm_module.nm_remote_settings.get_ssid_associate_connections(self.ssid)
        connect_not_assocaite = nm_module.nm_remote_settings.get_ssid_not_associate_connections(self.ssid)

        # Check connections
        if connection_associate == []:
            connection = nm_module.nm_remote_settings.new_wireless_connection(self.ssid)
            connection_associate.append(connection)
            connections = connection_associate + connect_not_assocaite

        if new_connection_list:
            connection_associate += new_connection_list
        connections = connection_associate + connect_not_assocaite

        self.connections = connections

        self.wireless_setting = [Wireless(con, self.set_button) for con in connections]
        self.ipv4_setting = [IPV4Conf(con, self.set_button) for con in connections]
        self.ipv6_setting = [IPV6Conf(con, self.set_button) for con in connections]
        self.security_setting = [Security(con, self.set_button) for con in connections]

        self.sidebar.init(connections,
                          self.ipv4_setting,
                          len(connection_associate),
                          self.ssid)
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
        connection = self.ipv4.connection
        #self.wireless.save_change()
        #self.ipv4.save_changes()
        #self.ipv6.save_changes()
        #self.security.save_setting()
        #wireless_device = nmclient.get_wireless_devices()[0]
        if widget.label == "save":
            self.wireless.wireless.adapt_wireless_commit()
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
                self.set_button("apply", True)
            else:
                print "not complete"

        else:
            wireless_device = nm_module.nmclient.get_wireless_devices()[0]
            device_wifi = cache.get_spec_object(wireless_device.object_path)
            ap = device_wifi.get_ap_by_ssid(self.ssid)

            device_wifi.emit("try-ssid-begin", self.ssid)
            # Activate
            nm_module.nmclient.activate_connection_async(connection.object_path,
                                       wireless_device.object_path,
                                       ap.object_path)
            self.change_crumb()
            self.slide_back() 
        
    def set_button(self, name, state):
        if name == "save":
            self.save_button.set_label(name)
            self.save_button.set_sensitive(state)
        else:
            self.save_button.set_label("connect")
            self.save_button.set_sensitive(state)

class SideBar(gtk.VBox):

    def __init__(self, connections, main_init_cb, check_click_cb, set_button_cb):
        gtk.VBox.__init__(self, False, 5)
        self.connections = connections
        self.main_init_cb = main_init_cb
        self.check_click_cb = check_click_cb
        self.set_button = set_button_cb

        # Build ui
        self.buttonbox = gtk.VBox(False, 6)
        self.pack_start(self.buttonbox, False, False)
        
        add_button = Button("Add setting")
        add_button.connect("clicked", self.add_new_connection)
        self.pack_start(add_button, False, False, 6)
        self.set_size_request(160, -1)
        self.new_connection_list = []

    def init(self, connection_list, ipv4setting, associate_len, access_point):
        wireless_device = nm_module.nmclient.get_wireless_devices()[0]
        active_connection = wireless_device.get_active_connection()
        if active_connection:
            active = active_connection.get_connection()
        else: 
            active =None

        self.connections = connection_list
        self.setting = ipv4setting
        self.split = associate_len
        self.ssid = access_point

        container_remove_all(self.buttonbox)
        cons = []
        self.connection_tree = EntryTreeView(cons)
        for index, connection in enumerate(self.connections[:self.split]):
            cons.append(SettingItem(connection,
                                    self.setting[index],
                                    self.check_click_cb, 
                                    self.delete_item_cb,
                                    self.set_button))
        if self.split is not len(self.connections):
            other_connections = map(lambda c: SettingItem(c[1],
                                self.setting[c[0]],
                                self.check_click_cb,
                                self.delete_item_cb,
                                self.set_button),
                                enumerate(self.connections[self.split:]))

            def resize_tree_cb():
                self.connection_tree.set_size_request(-1,len(self.connection_tree.visible_items) * self.connection_tree.visible_items[0].get_height())

                
            cons.append(ShowOthers(other_connections, resize_tree_cb))

        self.connection_tree.add_items(cons)


        self.connection_tree.show_all()

        self.buttonbox.pack_start(self.connection_tree, False, False, 6)

        try:
            index = self.connections.index(active)
            this_connection = self.connection_tree.visible_items[index]
            this_connection.set_active(True)
            self.connection_tree.select_items([this_connection])
        except:
            self.connection_tree.select_first_item()
        
        if self.new_connection_list:
            connect = self.connection_tree.visible_items[self.split -1]
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
        row = self.connection_tree.select_rows[0]
        if row < self.split:
            return row
        else:
            return row -1

    def set_active(self):
        index = self.get_active()
        this_connection = self.connection_tree.visible_items[index]
        this_connection.set_active(True)

    def clear_active(self):
        items = self.connection_tree.visible_items
        for item in items:
            item.set_active(False)

    def add_new_connection(self, widget):
        connection = nm_module.nm_remote_settings.new_wireless_connection(self.ssid)
        self.new_connection_list.append(connection)
        self.main_init_cb(self.ssid, self.new_connection_list)

        
class NoSetting(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)

        label_align = gtk.Alignment(0.5,0.5,0,0)

        label = Label("No active connection")
        label_align.add(label)
        self.add(label_align)

class Security(gtk.VBox):

    def __init__(self, connection, set_button_cb):
        gtk.VBox.__init__(self)
        self.connection = connection
        self.set_button = set_button_cb

        self.setting = self.connection.get_setting("802-11-wireless-security")
        self.security_label = Label("Security:")
        self.key_label = Label("Key:")
        self.wep_index_label = Label("Wep index:")
        self.auth_label = Label("Authentication:")
        self.password_label = Label("Password:")

        self.encry_list = [("None", None),
                      ("WEP (Hex or ASCII)", "none"),
                      ("WEP 104/128-bit Passphrase", "none"),
                      ("WPA WPA2 Personal", "wpa-psk")]
        #entry_item = map(lambda l: (l[1],l[0]), enumerate(self.encry_list))
        self.security_combo = ComboBox(self.encry_list, max_width=222)
        self.security_combo.set_size_request(222, 22)

        self.key_entry = PasswordEntry()
        self.password_entry = PasswordEntry()
        self.show_key_check = CheckButton("Show key")
        self.show_key_check.connect("toggled", self.show_key_check_button_cb)
        self.wep_index_spin = SpinBox(0, 0, 3, 1, 55)
        self.auth_combo = ComboBox([("Open System", "open"),
                                    ("Shared Key", "shared")], max_width=222)

        ## Create table
        self.table = gtk.Table(5, 4, True)
        self.reset()
        self.security_combo.connect("item-selected", self.change_encry_type)
        self.key_entry.entry.connect("changed", self.save_wep_pwd)
        self.password_entry.entry.connect("changed", self.save_wpa_pwd)
        self.wep_index_spin.connect("value-changed", self.wep_index_spin_cb)
        self.auth_combo.connect("item-selected", self.save_auth_cb)
        #self.security_combo.emit("item-selected", None, 0, 0)
            
        #self.reset(True)

        #table_wpa = gtk.Table(3, 4, True)
        #table_wpa.attach(security_label, 0, 1, 0, 1)
        #table_wpa.attach(self.security_combo, 1 ,4, 0 ,1)
        #TODO UI change
        align = gtk.Alignment(0, 0, 0, 0)
        align.set_padding(35, 0, 120, 0)
        align.add(self.table)
        self.table.set_size_request(340, -1)
        self.key_entry.set_size(222, 22)
        self.password_entry.set_size(222, 22)

        self.add(align)

    def reset(self):
        ## Add security
        container_remove_all(self.table)
        self.table.attach(self.security_label, 0, 1, 0, 1)
        self.table.attach(self.security_combo, 1, 4, 0, 1)
        
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
            self.table.attach(self.password_label, 0, 1, 1, 2)
            self.table.attach(self.password_entry, 1, 4, 1, 2)
            self.table.attach(self.show_key_check, 1, 4, 2, 3)
            
            self.password_entry.entry.set_text(secret)

        elif self.security_combo.get_current_item()[1] == "none":
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

            # Retrieve wep properties
            try:
                key = secret
                index = self.setting.wep_tx_keyidx
                auth = self.setting.auth_alg
                self.auth_combo.set_select_index(["open", "shared"].index(auth))
            except:
                key = ""
                index = 0
                auth = "open"
            # must convert long int to int 
            index = int(index)
            self.key_entry.entry.set_text(key)
            self.wep_index_spin.set_value(index)
            self.auth_combo.set_select_index(["open", "shared"].index(auth))

        self.table.show_all()
    def change_encry_type(self, widget, content, value, index):
        self.setting.key_mgmt = value
        # FIXME Maybe needed
        self.setting.adapt_wireless_security_commit()
        if value == "none":
            self.setting.wep_key_type = index
        self.set_button("save", False)
        self.reset()
    def save_wpa_pwd(self, widget, content):
        if self.setting.verify_wpa_psk(content):
            self.setting.psk = content
            check_settings(self.connection, self.set_button)
        else:
            self.set_button("save", False)
            print "invalid"

    def save_wep_pwd(self, widget, content):
        active = self.setting.wep_tx_keyidx
        if self.setting.verify_wep_key(content, active):
            self.setting.set_wep_key(active, content)
            check_settings(self.connection, self.set_button)

            print "wep_valid"
        else:
            self.set_button("save", False)
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
        key = nm_module.secret_agent.agent_get_secrets(self.connection.object_path,
                                                   "802-11-wireless-security",
                                                   "wep-key%d"%value)

        if key == None:
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

    def __init__(self, connection, set_button_cb):
        gtk.VBox.__init__(self)
        self.connection = connection 
        self.set_button = set_button_cb
        self.wireless = self.connection.get_setting("802-11-wireless")
        ### UI
        self.ssid_label = Label("SSID:")
        self.ssid_entry = InputEntry()

        self.mode_label = Label("Mode:")
        self.mode_combo = ComboBox([("Infrastructure","infrastructure"),( "Ad-hoc", "adhoc")], max_width=170)
        
        # TODO need to put this section to personal wifi
        self.band_label = Label("Band:")
        self.band_combo = ComboBox([("Automatic", None),
                                    ("a (5 GHZ)", "a"),
                                    ("b/g (2.4)", "bg")])
        self.channel_label = Label("Channel:")
        self.channel_spin = SpinBox(0, 0, 1500, 1, 55)
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
        #self.init_table(self.mode_combo.get_current_item()[1]) 

        self.table = gtk.Table(8, 2, True)
        # SSID

        #TODO UI change
        align = gtk.Alignment(0, 0, 0, 0)
        align.set_padding(35, 0, 120, 0)
        align.add(self.table)
        self.add(align)
        self.table.set_size_request(340, 227)

        self.ssid_entry.set_size(222, 22)
        self.bssid_entry.set_size(222, 22)
        self.mac_entry.set_size(222, 22)
        self.clone_entry.set_size(222, 22)

        self.reset()
        self.mode_combo.connect("item-selected", self.mode_combo_selected)
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
                self.set_button("save", False)

    def band_combo_selected(self, widget, content, value, index):
        self.wirless.band = value


    def mode_combo_selected(self, widget, content, value, index):
        self.wireless.mode = value
        # FIXME got some problem when adapt wireless commit
        #self.wireless.adapt_wireless_commit()
        self.reset_table()

    def reset_table(self):
        container_remove_all(self.table)
        mode = self.mode_combo.get_current_item()[1]

        self.table.attach(self.ssid_label, 0, 1, 0, 1)
        self.table.attach(self.ssid_entry, 1, 2, 0, 1)
        # Mode
        self.table.attach(self.mode_label, 0, 1, 1, 2)
        self.table.attach(self.mode_combo, 1, 2, 1, 2)
        if mode == "adhoc":
            self.table.attach(self.band_label, 0, 1, 2, 3)
            self.table.attach(self.band_combo, 1, 2, 2, 3)
            self.table.attach(self.channel_label, 0, 1, 3, 4)
            self.table.attach(self.channel_spin, 1, 2, 3, 4)

        # Bssid
        self.table.attach(self.bssid_label, 0, 1, 4, 5)
        self.table.attach(self.bssid_entry, 1, 2, 4, 5)

        # MAC
        self.table.attach(self.mac_address, 0, 1, 5, 6)
        self.table.attach(self.mac_entry, 1, 2, 5, 6)
        # MAC_CLONE
        self.table.attach(self.clone_addr, 0, 1, 6, 7)
        self.table.attach(self.clone_entry, 1,2, 6, 7)
        # MTU
        self.table.attach(self.mtu_spin, 1, 2, 7, 8)
        self.table.attach(self.mtu, 0, 1, 7, 8)

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
        # TODO add update functions
        #connection.adapt_ip4config_commit()
        #self.connection.update()

