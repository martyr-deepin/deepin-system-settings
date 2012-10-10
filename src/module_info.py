#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
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

from dtk.ui.config import Config
import gtk
import os

MODULE_DIR = os.path.join(os.path.dirname(__file__), "modules")        

class ModuleInfo(object):
    '''
    class docs
    '''
	
    def __init__(self, module_path):
        '''
        init docs
        '''
        self.path = module_path
        self.config = Config(os.path.join(self.path, "config.ini"))
        self.config.load()
        self.name = self.config.get("name", "zh_CN")
        self.icon_pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(self.path, self.config.get("main", "icon")))
        self.menu_icon_pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(self.path, self.config.get("main", "menu_icon")))
        
def get_module_infos():
    all_module_names = filter(lambda module_name: os.path.isdir(os.path.join(MODULE_DIR, module_name)), os.listdir(MODULE_DIR))        
    first_module_names = ["screen", "sound", "individuation", "date_time", "power"]
    second_module_names = ["keyboard", "mouse", "touchpad", "printer", "network", "bluetooth", "driver"]
    third_module_names = ["account", "auxiliary", "application_associate", "system_information"]
    extend_module_names = list(set(all_module_names) - set(first_module_names) - set(second_module_names) - set(third_module_names))
    
    return map(lambda names: 
               map(lambda name: ModuleInfo(os.path.join(MODULE_DIR, name)), names), 
                   [first_module_names, second_module_names, third_module_names, extend_module_names])
