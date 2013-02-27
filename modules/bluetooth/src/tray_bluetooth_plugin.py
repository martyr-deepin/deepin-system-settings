#! /usr/bin/env python                                                          
# -*- coding: utf-8 -*-                                                         
                                                                                
# Copyright (C) 2013 Deepin, Inc.                                        
#               2013 Zhai Xiang                                          
#                                                                               
# Author:     Zhai Xiang <zhaixiang@linuxdeepin.com>                            
# Maintainer: Zhai Xiang <zhaixiang@linuxdeepin.com>                            
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

import sys                                                                      
import os                                                                       
from deepin_utils.file import get_parent_dir                                    
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))

from bt.manager import Manager
from bt.adapter import Adapter
from bt.device import Device
from theme import app_theme
from dtk.ui.draw import draw_text
from dtk.ui.label import Label
from dtk.ui.constant import ALIGN_START, ALIGN_MIDDLE, ALIGN_END
from dtk.ui.button import ToggleButton
from dtk.ui.new_treeview import TreeItem, TreeView
from vtk.button import SelectButton
from deepin_utils.process import run_command
import gobject
import gtk
import pango
import time
import threading as td
from nls import _

class DiscoveryDeviceThread(td.Thread):                                         
    def __init__(self, ThisPtr):                                                
        td.Thread.__init__(self)                                                
        self.setDaemon(True)                                                    
        self.ThisPtr = ThisPtr                                                  
                                                                                
    def run(self):                                                              
        try:                                                                    
            for dev in self.ThisPtr.adapter.get_devices():                      
                self.ThisPtr.adapter.remove_device(dev)                         
                                                                                
            self.ThisPtr.adapter.start_discovery()                              
                                                                                
            while True:                                                         
                time.sleep(1)                                                   
        except Exception, e:                                                    
            print "class DiscoveryDeviceThread got error: %s" % e

class DeviceItem(TreeItem):
    ITEM_HEIGHT = 15
    NAME_WIDTH = 100
    
    def __init__(self, name):
        TreeItem.__init__(self)
        self.name = name

    def __render_name(self, cr, rect):                                           
        draw_text(cr, 
                  self.name, 
                  rect.x, 
                  rect.y, 
                  rect.width, 
                  rect.height)

    def get_height(self):
        return self.ITEM_HEIGHT

    def get_column_widths(self):
        return [self.NAME_WIDTH]

    def get_column_renders(self):
        return [self.__render_name]

gobject.type_register(DeviceItem)

class TrayBluetoothPlugin(object):
    def __init__(self):
        self.manager = Manager()
        self.adapter = None
        self.width = 130
        self.height = 80

    def init_values(self, this_list):
        self.this = this_list[0]
        self.tray_icon = this_list[1]
        self.tray_icon.set_icon_theme("enable")
        if self.manager.get_default_adapter() != "None":
            self.adapter = Adapter(self.manager.get_default_adapter())
        else:
            self.tray_icon.set_visible(False)

    def id(slef):
        return "deepin-bluetooth-plugin-hailongqiu"

    def run(self):
        return True

    def insert(self):
        pass

    def __adapter_toggled(self, widget):
        if self.adapter == None:
            return

        self.adapter.set_powered(widget.get_active())
        if self.adapter.get_powered():
            DiscoveryDeviceThread(self).start()

    def __bluetooth_selected(self, widget, event):                                 
        self.this.hide_menu()                         
        run_command("deepin-system-settings bluetooth")

    def __device_found(self, adapter, address, values):                         
        if address not in adapter.get_address_records():                        
            device = Device(adapter.create_device(address))                     
            items = []                                                          
                                                                                
            '''                                                                 
            FIXME: why there is no Name key sometime?                           
            '''                                                                 
            if not values.has_key("Name"):                                      
                return                                                          
            items.append(DeviceItem(values['Name']))
            self.device_treeview.add_items(items)
            self.device_treeview.set_size_request(-1, len(items) * DeviceItem.ITEM_HEIGHT)
            if len(items):
                self.height = self.height + len(items) * DeviceItem.ITEM_HEIGHT
            else:
                self.height = 80
            self.this.set_size_request(self.width, self.height)
        else:                                                                   
            if adapter.get_discovering():                                       
                adapter.stop_discovery()                                        
                pass

    def plugin_widget(self):
        self.device_treeview = TreeView()
        self.adapter.connect("device-found", self.__device_found)

        if self.adapter.get_powered():                                      
            DiscoveryDeviceThread(self).start()

        plugin_box = gtk.VBox()
        adapter_box = gtk.HBox(spacing = 10)
        adapter_label = self.__setup_label(_("Adapter"))
        adapter_toggle = self.__setup_toggle()
        if self.adapter:
            adapter_toggle.set_active(self.adapter.get_powered())
        adapter_toggle.connect("toggled", self.__adapter_toggled)
        select_button_align = self.__setup_align(padding_top = 5)
        select_button = SelectButton(_("More devices"),             
                                     font_size = 10,                            
                                     ali_padding = 5)                           
        select_button.set_size_request(self.width, 25)                          
        select_button.connect("button-press-event", self.__bluetooth_selected)
        select_button_align.add(select_button)
        adapter_box.pack_start(adapter_label, False, False)
        adapter_box.pack_start(adapter_toggle, False, False)
        plugin_box.pack_start(adapter_box, False, False)
        plugin_box.pack_start(self.device_treeview, False, False)
        plugin_box.pack_start(select_button_align, False, False)
        return plugin_box

    def show_menu(self):
        self.this.set_size_request(self.width, self.height)

    def hide_menu(self):
        pass

    def __setup_align(self, 
                      xalign=0, 
                      yalign=0, 
                      xscale=0, 
                      yscale=0,                
                      padding_top=0,                                 
                      padding_bottom=0,                                            
                      padding_left=0,                       
                      padding_right=0):                                           
        align = gtk.Alignment()                                                    
        align.set(xalign, yalign, xscale, yscale)                                  
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        return align

    def __setup_label(self, text="", width=50, align=ALIGN_START):                  
        return Label(text, None, 9, align, width, False, False, False)

    def __setup_toggle(self):                                                      
        return ToggleButton(app_theme.get_pixbuf("toggle_button/inactive_normal.png"), 
            app_theme.get_pixbuf("toggle_button/active_normal.png"),               
            inactive_disable_dpixbuf = app_theme.get_pixbuf("toggle_button/inactive_normal.png"))

def return_plugin():
    return TrayBluetoothPlugin
