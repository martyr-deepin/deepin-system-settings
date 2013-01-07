#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
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

from deepin_utils.process import run_command
from dtk.ui.iconview import IconView
from dtk.ui.scrolled_window import ScrolledWindow

from helper import event_manager

from ui.wallpaper_item import AddItem, WallpaperItem


class WallpaperView(IconView):
    
    def __init__(self, padding_x=8, padding_y=10):
        IconView.__init__(self, padding_x=padding_x, padding_y=padding_y)
        self.add_item = AddItem()
        self.add_items([self.add_item])
        
        # self.connect("double-click-item", self.__on_double_click_item)
        self.connect("single-click-item", self.__on_single_click_item)
        
        event_manager.add_callback("add-wallpapers", self.on_add_wallpapers)
        
    def set_theme(self, theme):    
        self.theme = theme
        self.clear()
        self.add_items([self.add_item])
        self.add_images(self.theme.get_wallpaper_paths())
        
    def add_images(self, images):        
        items = map(lambda image: WallpaperItem(image), images)
        self.add_items(items, insert_pos=-1)
        
    def on_add_wallpapers(self, name, obj, image_paths):    
        self.add_images(image_paths)
        self.theme.add_user_wallpapers(image_paths)
        
    def get_scrolled_window(self):    
        scrolled_window = ScrolledWindow()
        scrolled_window.add_child(self)
        return scrolled_window
    
    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
        
    def __on_single_click_item(self, widget, item, x, y):    
        if hasattr(item, "image_path"):
            run_command("gsettings set com.deepin.dde.background picture-uris 'file://%s'" % item.image_path)        
