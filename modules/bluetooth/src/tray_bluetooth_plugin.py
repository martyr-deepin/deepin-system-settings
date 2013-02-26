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

from bt.manager import Manager
from dtk.ui.label import Label
import gtk

class TrayBluetoothPlugin(object):
    def __init__(self):
        self.manager = Manager()

    def init_values(self, this_list):
        self.this = this_list[0]
        self.tray_icon = this_list[1]
        self.tray_icon.set_icon_theme("enable")
        if self.manager.get_default_adapter() == "None":
            self.tray_icon.set_visible(False)

    def id(slef):
        return "deepin-bluetooth-plugin-hailongqiu"

    def run(self):
        return True

    def insert(self):
        return 2

    def plugin_widget(self):
        plugin_align = self.__setup_align()
        
        return plugin_align

    def show_menu(self):
        self.this.set_size_request(160, 180)

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

def return_plugin():
    return TrayBluetoothPlugin
