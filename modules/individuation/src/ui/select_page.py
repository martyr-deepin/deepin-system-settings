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

import gtk
import copy

from dtk.ui.button import Button
from dtk.ui.iconview import IconView
from dtk.ui.threads import post_gui
from dtk.ui.scrolled_window import ScrolledWindow

from ui.wallpaper_item import SelectItem
from cache_manager import cache_thread_pool
from helper import event_manager

import common

class SelectView(IconView):
    
    def __init__(self, monitor_dir, padding_x=8, padding_y=10):
        IconView.__init__(self, padding_x=padding_x, padding_y=padding_y)
        
        # self.connect("double-click-item", self.__on_double_click_item)
        # self.connect("single-click-item", self.__on_single_click_item)
        
        self.monitor_dir = monitor_dir
        self.__init_monitor_images()
        
    def __init_monitor_images(self):    
        items = []
        for image_path in common.walk_images(self.monitor_dir):
            items.append(SelectItem(image_path))
        if items:    
            self.add_items(items)
            
    def add_images(self, images):        
        items = map(lambda image: SelectItem(image), images)
        self.add_items(items)
        
    def get_scrolled_window(self):    
        scrolled_window = ScrolledWindow()
        scrolled_window.add_child(self)
        return scrolled_window
    
    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
        
    def emit_add_wallpapers(self):    
        tick_items = filter(lambda item : item.is_tick, self.items)
        if tick_items:
            image_paths = map(lambda item: item.image_path, tick_items)
            event_manager.emit("add-wallpapers", image_paths)
        
        
class SystemPage(gtk.VBox):        
    
    def __init__(self, monitor_dir):
        
        gtk.VBox.__init__(self)
        self.set_spacing(10)
        
        self.select_view = SelectView(monitor_dir)
        self.select_view_sw = self.select_view.get_scrolled_window()
        
        add_button = Button("添加")
        add_button.connect("clicked", self.on_add_wallpapers)
        
        control_box = gtk.HBox(10)
        control_box.pack_start(add_button, False, False)
        
        control_align = gtk.Alignment()
        control_align.set(1.0, 0.5, 0, 0)
        control_align.set_padding(0, 5, 0, 10)
        control_align.add(control_box)
        self.pack_start(self.select_view_sw, True, True)
        self.pack_start(control_align, False, True)
        
    def on_add_wallpapers(self, widget):    
        self.select_view.emit_add_wallpapers()
        
class UserPage(gtk.VBox):        
    
    def __init__(self, monitor_dir, listen_download_signal=False):
        
        gtk.VBox.__init__(self)
        self.set_spacing(10)
        
        self.select_view = SelectView(monitor_dir)
        self.select_view_sw = self.select_view.get_scrolled_window()
        
        delete_button = Button("删除选中")
        add_button = Button("添加")
        add_button.connect("clicked", self.on_add_wallpapers)
        
        control_box = gtk.HBox(10)
        control_box.pack_start(delete_button, False, False)
        control_box.pack_start(add_button, False, False)
        
        control_align = gtk.Alignment()
        control_align.set(1.0, 0.5, 0, 0)
        control_align.set_padding(0, 5, 0, 10)
        control_align.add(control_box)
        
        self.pack_start(self.select_view_sw, True, True)
        self.pack_start(control_align, False, True)
        
        if listen_download_signal:
            event_manager.add_callback("download-image-finish", self.on_download_image_finish)
            
    def on_download_image_finish(self, name, obj, data):        
        self.select_view.add_images([data])
        
    def on_add_wallpapers(self, widget):    
        self.select_view.emit_add_wallpapers()
        
