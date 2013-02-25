#! /usr/bin/env python                                                          
# -*- coding: utf-8 -*-                                                         
                                                                                
# Copyright (C) 2012 ~ 2013 Deepin, Inc.                                        
#               2012 ~ 2013 Zhai Xiang                                          
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

import gtk

class TrayBluetoothPlugin(object):
    def __init__(self):
        pass

    def init_values(self, this_list):
        self.this = this_list[0]
        self.tray_icon = this_list[1]
        self.tray_icon.set_icon_theme("enable")

    def id(slef):
        return "deepin-bluetooth-plugin-hailongqiu"

    def run(self):
        return True

    def insert(self):
        return 2

    def plugin_widget(self):
        return gtk.Button("BLUEZ")

    def show_menu(self):
        self.this.set_size_request(160, 180)

    def hide_menu(self):
        pass

def return_plugin():
    return TrayBluetoothPlugin
