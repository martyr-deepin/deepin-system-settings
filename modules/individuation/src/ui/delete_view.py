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

import os
import deepin_gsettings
from dtk.ui.iconview import IconView
from dtk.ui.scrolled_window import ScrolledWindow
from helper import event_manager
from ui.wallpaper_item import DeleteItem
from theme_manager import background_gsettings
import common

class DeleteView(IconView):
    
    def __init__(self, padding_x=8, padding_y=10):
        IconView.__init__(self, padding_x=padding_x, padding_y=padding_y)
        
        event_manager.add_callback("wallpapers-deleted", self.on_wallpapers_deleted)
        self.theme = None

    def set_theme(self, theme):    
        self.theme = theme
        self.clear()
        
        self.add_system_wallpapers(self.theme.get_system_wallpapers())        
        self.add_user_wallpapers(self.theme.get_user_wallpapers())
        
    def is_exists(self, image):    
        if self.theme == None:
            return False

        if image in self.theme.get_user_wallpapers():
            return True
        return False
    
    def add_user_wallpapers(self, image_paths, save=False):
        self.add_images(image_paths)
        if save:
            if self.theme == None:
                return
    
    def add_system_wallpapers(self, image_paths):
        self.add_images(image_paths)
        
    def add_images(self, images):
        items = map(lambda image: DeleteItem(image, self.theme), images)
        self.add_items(items, insert_pos=-1)

    def is_deletable(self):
        for item in self.items:
            if item.is_tick:
                return True

        return False

    def delete_wallpaper(self):
        for item in self.items:
            if item.is_tick:
                self.theme.remove_option("system_wallpaper", item.image_path.split("/")[-1])
                self.theme.remove_option("user_wallpaper", item.image_path)

        self.theme.save()
        self.set_theme(self.theme)
    
    def is_select_all(self):
        for item in self.items:
            if not item.is_tick:
                return False

        return True

    def select_all(self):
        is_select_all = self.is_select_all()

        for item in self.items:
            if is_select_all:
                item.untick()
            else:
                item.tick()
            
    def on_wallpapers_deleted(self, name, obj, image_paths):        
        items = filter(lambda item: item.image_path in image_paths, self.items)
        if items:        
            self.delete_items(items)
        
    def get_scrolled_window(self):    
        scrolled_window = ScrolledWindow()
        scrolled_window.add_child(self)
        return scrolled_window
    
    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
