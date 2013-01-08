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


from dtk.ui.iconview import IconView
from dtk.ui.scrolled_window import ScrolledWindow

from ui.theme_item import ThemeItem
from helper import event_manager

class ThemeView(IconView):
    
    def __init__(self, padding_x=20, padding_y=0):
        IconView.__init__(self, padding_x=padding_x, padding_y=padding_y)
        
        self.connect("double-click-item", self.__on_double_click_item)
        self.connect("single-click-item", self.__on_single_click_item)
        
    def get_scrolled_window(self):    
        scrolled_window = ScrolledWindow()
        scrolled_window.add_child(self)
        return scrolled_window
    
    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
        
    def __on_double_click_item(self, widget, item, x, y):
        event_manager.emit("theme-detail", item.theme)
    
    def __on_single_click_item(self, widget, item, x, y):
        event_manager.emit("apply-theme", item.theme)
    
    def add_themes(self, themes):
        theme_items = [ThemeItem(theme_file) for theme_file in themes ]
        self.add_items(theme_items)
        
