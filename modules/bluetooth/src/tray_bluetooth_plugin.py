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
from theme import app_theme
from dtk.ui.label import Label
from dtk.ui.constant import ALIGN_START, ALIGN_MIDDLE, ALIGN_END
from dtk.ui.button import ToggleButton
from dtk.ui.new_treeview import TreeItem, TreeView
from vtk.button import SelectButton
from deepin_utils.process import run_command
import gtk
import gobject
from nls import _

class DeviceItem(TreeItem):
    def __init__(self):
        pass

gobject.type_register(DeviceItem)

class TrayBluetoothPlugin(object):
    def __init__(self):
        self.manager = Manager()
        self.adapter = None
        self.width = 130

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

    def __bluetooth_selected(self, widget, event):                                 
        self.this.hide_menu()                         
        run_command("deepin-system-settings bluetooth")

    def plugin_widget(self):
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
        plugin_box.pack_start(select_button_align, False, False)
        return plugin_box

    def show_menu(self):
        self.this.set_size_request(self.width, 80)

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
