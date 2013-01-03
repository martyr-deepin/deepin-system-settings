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
from wallpaper_item import CacheItem
from cache_manager import cache_thread_pool

import common

class CacheView(IconView):
    
    def __init__(self, network_interface, padding_x=8, padding_y=10):
        IconView.__init__(self, padding_x=padding_x, padding_y=padding_y)
        
        self.connect("double-click-item", self.__on_double_click_item)
        self.connect("single-click-item", self.__on_single_click_item)
        self.__fetch_thread_id = 0
        self.network_interface = network_interface
        
    def get_scrolled_window(self):    
        scrolled_window = ScrolledWindow()
        scrolled_window.add_child(self)
        return scrolled_window
    
    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
        
    def __on_double_click_item(self, widget, item, x, y):
        pass
        
    def __on_single_click_item(self, widget, item, x, y):
        pass
    
    def fetch_failed(self):
        pass
    
    def fetch_successed(self):
        pass
        
    def try_to_fetch(self):    
        self.clear()
        self.network_interface.clear()
        self.__fetch_thread_id += 1
        fetch_thread_id = copy.deepcopy(self.__fetch_thread_id)
        common.ThreadFetch(
            fetch_funcs=(self.fetch_images, ()),
            success_funcs=(self.load_images, (fetch_thread_id,)),
            fail_funcs=(self.fetch_failed, ())
            ).start()
        
    def fetch_images(self):    
        return self.network_interface.fetch_images()
    
    @post_gui
    def load_images(self, ret, thread_id):
        cache_items = []
        thread_items = []
        images = self.network_interface.get_images()
        
        for image in images:
            cache_item = CacheItem(image)
            if not cache_item.is_loaded:
                thread_items.append(cache_item)
            cache_items.append(cache_item)    
            
        if thread_items:    
            cache_thread_pool.add_missions(thread_items)
        self.add_items(cache_items)    
        self.fetch_successed()
        
class CachePage(gtk.VBox):        
    
    def __init__(self, network_interface):
        
        gtk.VBox.__init__(self)
        self.set_spacing(10)
        
        self.cache_view = CacheView(network_interface)
        self.cache_view_sw = self.cache_view.get_scrolled_window()
        
        self.try_button = Button("再试一次")
        self.try_button.connect("clicked", self.on_try_button_clicked)
        try_button_align = gtk.Alignment()
        try_button_align.set(1.0, 0.5, 0, 0)
        try_button_align.set_padding(0, 5, 0, 10)
        try_button_align.add(self.try_button)
        
        self.pack_start(self.cache_view_sw, True, True)
        self.pack_start(try_button_align, False, True)
        
    def on_try_button_clicked(self, widget):    
        self.cache_view.try_to_fetch()
        
