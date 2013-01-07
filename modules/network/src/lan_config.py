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
from dtk.ui.tab_window import TabBox
from dtk.ui.button import Button,ToggleButton, RadioButton, CheckButton
from dtk.ui.new_entry import InputEntry
from dtk.ui.label import Label
from dtk.ui.spin import SpinBox
from dtk.ui.utils import container_remove_all
from dtk.ui.draw import color_hex_to_cairo, draw_window_rectangle, draw_line
from dtk.ui.new_treeview import TreeView
from dtk.ui.line import VSeparator, HSeparator
#from dtk.ui.droplist import Droplist
from nm_modules import nm_module
#from widgets import SettingButton
from settings_widget import EntryTreeView, SettingItem, AddSettingItem
from nmlib.nm_utils import TypeConvert
from nmlib.nmcache import cache
from nmlib.nm_remote_connection import NMRemoteConnection
from shared_widget import IPV4Conf, IPV6Conf
import gtk
wired_device = []

from constants import FRAME_VERTICAL_SPACING, CONTENT_FONT_SIZE, WIDGET_HEIGHT, CONTAINNER_HEIGHT
import style
from nls import _

def expose_background(widget, event):
    cr = widget.window.cairo_create()
    rect = widget.allocation
    cr.set_source_rgb( 1, 1, 1) 
    cr.rectangle(rect.x, rect.y, rect.width, rect.height)
    cr.fill()

class WiredSetting(gtk.Alignment):

    def __init__(self, slide_back_cb, change_crumb_cb):
        #gtk.HBox.__init__(self, spacing=FRAME_VERTICAL_SPACING)
        gtk.Alignment.__init__(self, 0, 0, 0, 0)
        self.slide_back = slide_back_cb
        self.change_crumb = change_crumb_cb
        
        # Add UI Align
        style.set_main_window(self)
        #hbox = gtk.HBox(spacing=FRAME_VERTICAL_SPACING)
        hbox = gtk.HBox()
        self.add(hbox)

        self.wired = None
        self.ipv4 = None
        self.ipv6 = None

        self.tab_window = TabBox(dockfill = False)
        self.tab_window.draw_title_background = self.draw_tab_title_background
        self.tab_window.set_size_request(674, 408)
        self.items = [(_("Wired"), NoSetting()),
                      (_("IPv4 Settings"), NoSetting()),
                      (_("IPv6 Settings"), NoSetting())]
        self.tab_window.add_items(self.items)
        #self.tab_window.connect("expose-event", self.expose_outline)
        self.sidebar = SideBar( None, self.init, self.check_click, self.set_button)
        # Build ui
        hbox.pack_start(self.sidebar, False , False)
        vbox = gtk.VBox()
        vbox.pack_start(self.tab_window ,True, True)
        #hbox.pack_start(VSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0), False, False)
        hbox.pack_start(vbox, True, True)
        #hbox = gtk.HBox()

        self.save_button = Button("Save")
        button_box = gtk.HBox()
        button_box.add(self.save_button)
        self.save_button.connect("clicked", self.save_changes)
        self.set_button("save", False)

        buttons_aligns = gtk.Alignment(0.5 , 1, 0, 0)
        buttons_aligns.add(button_box)
        vbox.pack_start(buttons_aligns, False , False)
        #hbox.connect("expose-event", self.expose_event)

        style.draw_background_color(self)
        style.draw_separator(self.sidebar, 3)

        
    def draw_tab_title_background(self, cr, widget):
        rect = widget.allocation
        cr.set_source_rgb(1, 1, 1)    
        cr.rectangle(0, 0, rect.width, rect.height - 1)
        cr.fill()
        

    def init(self, device=None, new_connection=None, init_connection=False):
        print "Wired start init"
        # Get all connections
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

        if new_connection:
            self.connections += new_connection
        else:
            self.sidebar.new_connection_list = []
            
        self.wired_setting = [Wired(con, self.set_button) for con in self.connections]
        self.ipv4_setting = [IPV4Conf(con, self.set_button) for con in self.connections]
        self.ipv6_setting = [IPV6Conf(con, self.set_button) for con in self.connections]

        self.sidebar.init(self.connections, self.ipv4_setting)
        index = self.sidebar.get_active()
        self.wired = self.wired_setting[index]
        self.ipv4 = self.ipv4_setting[index]
        self.ipv6 = self.ipv6_setting[index]

        self.init_tab_box()

    def init_tab_box(self):
        self.tab_window.tab_items[0] = (_("Wired"), self.wired)
        self.tab_window.tab_items[1] = (_("IPV4 Settings") ,self.ipv4)
        self.tab_window.tab_items[2] = (_("IPV6 Settings"),self.ipv6)
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

    def set_button(self, name, state):
        if name == "save":
            self.save_button.set_label(name)
            self.save_button.set_sensitive(state)
        else:
            self.save_button.set_label("connect")
            self.save_button.set_sensitive(state)

    
    def save_changes(self, widget):
        connection = self.ipv4.connection
        if widget.label == "save":
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
            self.apply_changes()

    def apply_changes(self):
        connection = self.ipv4.connection
        nm_module.nmclient.activate_connection_async(connection.object_path,
                                           wired_device.object_path,
                                           "/")
        self.device_ethernet = cache.get_spec_object(wired_device.object_path)
        self.device_ethernet.emit("try-activate-begin")
        self.change_crumb()
        self.slide_back()
        
class SideBar(gtk.VBox):
    def __init__(self, connections, main_init_cb, check_click_cb, set_button_cb):
        gtk.VBox.__init__(self, False)
        self.connections = connections
        self.main_init_cb = main_init_cb
        self.check_click_cb = check_click_cb
        self.set_button = set_button_cb

        self.buttonbox = gtk.VBox()
        self.pack_start(self.buttonbox, False, False)
        style.add_separator(self) 

        add_button = AddSettingItem(_("New Connection"),self.add_new_setting)
        self.pack_start(TreeView([add_button]), False, False)
        self.new_connection_list =[]
        
        #TODO UI change
        self.set_size_request(160, -1 )

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
            cons.append(SettingItem(connection,
                                    self.setting[index],
                                    self.check_click_cb, 
                                    self.delete_item_cb,
                                    self.set_button))
        self.connection_tree.add_items(cons)


        self.connection_tree.show_all()

        self.buttonbox.pack_start(self.connection_tree, False, False, 0)

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

    def add_new_setting(self):
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


class Wired(gtk.VBox):
    ENTRY_WIDTH = 222

    def __init__(self, connection, set_button_callback=None):
        gtk.VBox.__init__(self)
        
        self.ethernet = connection.get_setting("802-3-ethernet")
        self.connection = connection
        self.set_button = set_button_callback
        table = gtk.Table(3, 2, False)
        
        mac_address = Label(_("Device Mac Address:"), text_size=CONTENT_FONT_SIZE)
        table.attach(style.wrap_with_align(mac_address), 0, 1, 0, 1)

        self.mac_entry = InputEntry()
        table.attach(style.wrap_with_align(self.mac_entry), 1, 2, 0, 1)

        clone_addr = Label(_("Cloned Mac Address:"), text_size=CONTENT_FONT_SIZE)
        table.attach(style.wrap_with_align(clone_addr), 0, 1, 1, 2)
        self.clone_entry = InputEntry()
        table.attach(style.wrap_with_align(self.clone_entry), 1,2, 1, 2)

        mtu = Label(_("MTU:"))
        table.attach(style.wrap_with_align(mtu), 0,1,2,3)
        self.mtu_spin = SpinBox(0,0, 1500, 1, self.ENTRY_WIDTH)
        table.attach(style.wrap_with_align(self.mtu_spin), 1,2,2,3)
        
        # TODO UI change
        #self.connect("expose-event", expose_background)
        style.draw_background_color(self)
        style.set_table(table)
        align = style.set_box_with_align(table, "text")
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
                setattr(self.ethernet, types, value)
                if self.connection.check_setting_finish():
                    self.set_button("save", True)
            else:
                self.set_button("save", False)
                if value is "":
                    #delattr(self.ethernet, types)
                    self.set_button("save", True)
        else:
            setattr(self.ethernet, types, value)
            if self.connection.check_setting_finish():
                self.set_button("save", True)
