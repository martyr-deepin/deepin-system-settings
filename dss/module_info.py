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

from dtk.ui.utils import get_system_icon_info
from deepin_utils.config import Config
from deepin_utils.file import get_parent_dir
import gtk
import os
from theme import app_theme
from constant import MAIN_LANG

MODULE_DIR = os.path.join(get_parent_dir(__file__, 2), "modules")        
FIRST_MODULE_NAMES = ["display", "desktop", "individuation", "sound", "date_time", "power"]
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
        self.name = self.default_name
        if MAIN_LANG != "en_US":
            self.name = self.config.get("name", MAIN_LANG)
        '''
        TODO: snyh give standard way to get pixbuf
        '''
        icon_infos = [get_system_icon_info("Deepin", "preferences-%s" % self.id), 
                      get_system_icon_info("Deepin", "preferences-%s" % self.id, 16)
                     ]
        
        self.icon_pixbuf = None
        self.menu_icon_pixbuf = None
        if icon_infos[0] and icon_infos[1]:
            self.icon_pixbuf = gtk.gdk.pixbuf_new_from_file(icon_infos[0].get_filename())
            self.menu_icon_pixbuf = gtk.gdk.pixbuf_new_from_file(icon_infos[1].get_filename())
        else:
            self.icon_pixbuf = app_theme.get_pixbuf("navigate/none-big.png").get_pixbuf()
            self.menu_icon_pixbuf = app_theme.get_pixbuf("navigate/none-small.png").get_pixbuf()
            
        self.search_keyword = self.config.get("main", "search_keyword")
        
def get_module_infos():
    all_module_names = filter(lambda module_name: os.path.isdir(os.path.join(MODULE_DIR, module_name)), os.listdir(MODULE_DIR))        
    if "a11y" in all_module_names:
        all_module_names.remove('a11y')
    if "mount_media" in all_module_names:
        all_module_names.remove('mount_media')
    if "tray_power" in all_module_names:
        all_module_names.remove('tray_power')
    extend_module_names = list(set(all_module_names) - set(FIRST_MODULE_NAMES) - set(SECOND_MODULE_NAMES) - set(THIRD_MODULE_NAMES))
    
    return map(lambda names: 
               map(lambda name: ModuleInfo(os.path.join(MODULE_DIR, name)), names), 
                   [FIRST_MODULE_NAMES, SECOND_MODULE_NAMES, THIRD_MODULE_NAMES, extend_module_names])
