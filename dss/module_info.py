#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
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
from deepin_utils.file import get_parent_dir
import gtk
import os

MODULE_DIR = os.path.join(get_parent_dir(__file__, 2), "modules")        
FIRST_MODULE_NAMES = ["display", "sound", "individuation", "date_time", "power"]
SECOND_MODULE_NAMES = ["keyboard", "mouse", "touchpad", "printer", "network", "bluetooth", "driver"]
THIRD_MODULE_NAMES = ["account", "application_associate", "system_information"]

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
        self.id = self.config.get("main", "id")
        # TODO: lihongwu req to support i18n
        self.default_name = self.config.get("name", "default")
        self.name = self.config.get("name", "zh_CN")
        self.icon_pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(self.path, self.config.get("main", "icon")))
        '''
        self.icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
            gtk.icon_theme_get_default().lookup_icon("preferences-%s" % self.id, 48, gtk.ICON_LOOKUP_NO_SVG))
        '''
        self.menu_icon_pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(self.path, self.config.get("main", "menu_icon")))
        self.search_keyword = self.config.get("main", "search_keyword")
        
def get_module_infos():
    all_module_names = filter(lambda module_name: os.path.isdir(os.path.join(MODULE_DIR, module_name)), os.listdir(MODULE_DIR))        
    all_module_names.remove('a11y')
    extend_module_names = list(set(all_module_names) - set(FIRST_MODULE_NAMES) - set(SECOND_MODULE_NAMES) - set(THIRD_MODULE_NAMES))
    
    return map(lambda names: 
               map(lambda name: ModuleInfo(os.path.join(MODULE_DIR, name)), names), 
                   [FIRST_MODULE_NAMES, SECOND_MODULE_NAMES, THIRD_MODULE_NAMES, extend_module_names])
