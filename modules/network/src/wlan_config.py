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
from dtk.ui.new_treeview import TreeView
from dtk.ui.label import Label
from dtk.ui.spin import SpinBox
from dtk.ui.utils import container_remove_all
from dtk.ui.combo import ComboBox
from nm_modules import nm_module
from nmlib.nmcache import cache
from foot_box import FootBox
#from widgets import SettingButton
from settings_widget import EntryTreeView, SettingItem, ShowOthers, AddSettingItem
import gtk

#from nmlib.nm_utils import TypeConvert
from shared_widget import IPV4Conf, IPV6Conf
from nmlib.nm_remote_connection import NMRemoteConnection
import style
from constants import FRAME_VERTICAL_SPACING
from nls import _

def check_settings(connection, fn):
    if connection.check_setting_finish():
        fn('save', True)
        print "pass"
    else:
        fn("save", False)
        print "not pass"

class WirelessSetting(gtk.Alignment):

    def __init__(self, slide_back_cb, change_crumb_cb):

        gtk.Alignment.__init__(self, 0, 0, 0, 0)
        self.slide_back = slide_back_cb
        self.change_crumb = change_crumb_cb

        # Add UI Align
        style.set_main_window(self)

        main_vbox = gtk.VBox()
        self.foot_box = FootBox()
        hbox = gtk.HBox()
        hbox.connect("expose-event",self.expose_line)
        main_vbox.pack_start(hbox, False, False)
        main_vbox.pack_start(self.foot_box, False, False)
        self.add(main_vbox)

        self.wireless = None
        self.ipv4 = None
        self.ipv6 = None
        self.security = None

        self.tab_window = TabBox(dockfill = False)
        self.tab_window.draw_title_background = self.draw_tab_title_background
        self.tab_window.set_size_request(674, 415)
        self.items = [(_("Wireless"), NoSetting()),
                      (_("Security"), NoSetting()),
                      (_("IPV4"), NoSetting()),
                      (_("IPv6"), NoSetting())]
        self.tab_window.add_items(self.items)

        self.sidebar = SideBar( None,self.init, self.check_click, self.set_button)

        # Build ui
        hbox.pack_start(self.sidebar, False , False)
        hbox.pack_start(self.tab_window ,True, True)

        self.save_button = Button()
        self.save_button.connect("clicked", self.save_changes)
        self.foot_box.set_buttons([self.save_button])

        self.connect("expose-event", self.expose_event)
        style.draw_separator(self.sidebar, 3)

    def expose_line(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        style.draw_out_line(cr, rect, exclude=["left", "right", "top"])

    def draw_tab_title_background(self, cr, widget):
        rect = widget.allocation
        cr.set_source_rgb(1, 1, 1)    
        cr.rectangle(0, 0, rect.width, rect.height - 1)
        cr.fill()
        
    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb( 1, 1, 1) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

    def init(self, access_point, new_connection_list=None, init_connections=False, all_adhoc=False):
        self.ssid = access_point
        if init_connections:
            self.sidebar.new_connection_list = []
        # Get all connections  
        connection_associate = nm_module.nm_remote_settings.get_ssid_associate_connections(self.ssid)
        # Check connections
        if connection_associate == []:
            connection = nm_module.nm_remote_settings.new_wireless_connection(self.ssid)
            connection_associate.append(connection)
            self.sidebar.new_connection_list.append(connection)
            connections = connection_associate

        if new_connection_list:
            connection_associate += new_connection_list
        connections = connection_associate

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
        self.tab_window.tab_items[0] = (_("Wireless"), self.wireless)
        self.tab_window.tab_items[2] = (_("IPV4"),self.ipv4)
        self.tab_window.tab_items[3] = (_("IPV6"),self.ipv6)
        self.tab_window.tab_items[1] = (_("Security"), self.security)
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
        if widget.label == "save":
            if connection.check_setting_finish():
                this_index = self.connections.index(connection)
                if isinstance(connection, NMRemoteConnection):
                    connection.update()
                else:
                    index = self.sidebar.new_connection_list.index(connection)
                    nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')
                    self.sidebar.new_connection_list.pop(index)
                    self.init(self.wireless.wireless.ssid, self.sidebar.new_connection_list)

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

            if ap == None:
                nm_module.nmclient.activate_connection_async(connection.object_path,
                                           wireless_device.object_path,
                                           "/")

            else:
                device_wifi.emit("try-ssid-begin", self.ssid)
                # Activate
                nm_module.nmclient.activate_connection_async(connection.object_path,
                                           wireless_device.object_path,
                                           ap.object_path)
            self.change_crumb()
            self.slide_back() 
        
    def set_button(self, name, state):
        if name == "save":
            self.save_button.set_label(_("save"))
            self.save_button.set_sensitive(state)
        else:
            self.save_button.set_label(_("connect"))
            self.save_button.set_sensitive(state)

class SideBar(gtk.VBox):

    def __init__(self, connections, main_init_cb, check_click_cb, set_button_cb):
        gtk.VBox.__init__(self, False)
        self.connections = connections
        self.main_init_cb = main_init_cb
        self.check_click_cb = check_click_cb
        self.set_button = set_button_cb
        self.all_adhoc = False

        # Build ui
        self.buttonbox = gtk.VBox()
        self.pack_start(self.buttonbox, False, False)
        style.add_separator(self)
        
        add_button = AddSettingItem(_("New Connection"),self.add_new_connection)
        self.pack_start(TreeView([add_button]), False, False)
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
        for index, connection in enumerate(self.connections):
            cons.append(SettingItem(connection,
                                    self.setting[index],
                                    self.check_click_cb, 
                                    self.delete_item_cb,
                                    self.set_button))

            def resize_tree_cb():
                self.connection_tree.set_size_request(-1,len(self.connection_tree.visible_items) * self.connection_tree.visible_items[0].get_height())

                
            #cons.append(ShowOthers(other_connections, resize_tree_cb))

        self.connection_tree.add_items(cons)


        self.connection_tree.show_all()

        self.buttonbox.pack_start(self.connection_tree, False, False)

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
        if self.new_connection_list == []:
            container_remove_all(self.buttonbox)
        else:
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

    def add_new_connection(self):
        if self.all_adhoc:
            connection = nm_module.nm_remote_settings.new_adhoc_connection("")
        else:
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
    ENTRY_WIDTH = 222

    def __init__(self, connection, set_button_cb):
        gtk.VBox.__init__(self)
        self.connection = connection
        self.set_button = set_button_cb

        self.setting = self.connection.get_setting("802-11-wireless-security")
        self.security_label = Label(_("Security:"))
        self.key_label = Label(_("Key:"))
        self.wep_index_label = Label(_("Wep index:"))
        self.auth_label = Label(_("Authentication:"))
        self.password_label = Label(_("Password:"))

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

        self.reset()
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
                self.setting.set_wep_key(index, secret)
                self.wep_index_spin.set_value(index)
                self.auth_combo.set_select_index(["open", "shared"].index(auth))
        self.queue_draw()

    def change_encry_type(self, widget, content, value, index):
        if value == None:
            self.connection.del_setting("802-11-wireless-security")
            del self.connection.get_setting("802-11-wireless").security
            self.reset(security=False)
            self.set_button("save", True)
        else:
            self.connection.get_setting("802-11-wireless").security = "802-11-wireless-security"
            self.connection.reinit_setting("802-11-wireless-security")
            self.setting = self.connection.get_setting("802-11-wireless-security")
            print "change encry type", self.setting
            self.setting.key_mgmt = value
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
        wep_type = self.setting.wep_key_type
        if self.setting.verify_wep_key(content, wep_type):
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
    ENTRY_WIDTH = 222

    def __init__(self, connection, set_button_cb):
        gtk.VBox.__init__(self)
        self.connection = connection 
        self.set_button = set_button_cb
        self.wireless = self.connection.get_setting("802-11-wireless")
        ### UI
        self.ssid_label = Label(_("SSID:"))
        self.ssid_entry = InputEntry()

        self.mode_label = Label(_("Mode:"))
        self.mode_combo = ComboBox([(_("Infrastructure"),"infrastructure"),(_("Ad-hoc"), "adhoc")], max_width=self.ENTRY_WIDTH)
        
        # TODO need to put this section to personal wifi
        self.band_label = Label(_("Band:"))
        self.band_combo = ComboBox([(_("Automatic"), None),
                                    ("a (5 GHZ)", "a"),
                                    ("b/g (2.4)", "bg")],
                                    max_width=self.ENTRY_WIDTH)
        self.channel_label = Label(_("Channel:"))
        self.channel_spin = SpinBox(0, 0, 1500, 1, self.ENTRY_WIDTH)
        # BSSID
        self.bssid_label = Label(_("BSSID:"))
        self.bssid_entry = InputEntry()
        self.mac_address = Label(_("Device Mac Address:"))
        self.mac_entry = InputEntry()
        self.clone_addr = Label(_("Cloned Mac Address:"))
        self.clone_entry = InputEntry()
        self.mtu = Label(_("MTU:"))
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
                self.set_button("save", False)

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

