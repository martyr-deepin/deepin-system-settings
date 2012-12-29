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


import os
from dtk.ui.config import Config
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.iconview import IconView
from dtk.ui.label import Label
import gobject
import gtk

from dtk.ui.utils import get_parent_dir
from theme_item import ThemeItem


THEME_DIR = os.path.join(get_parent_dir(__file__, 2), "theme")
BACKGROUND_DIR = os.path.join(get_parent_dir(__file__, 2), "background")

class Theme(object):
    '''
    class docs
    '''
	
    def __init__(self, theme_file):
        '''
        init docs
        '''
        self.theme_file = theme_file
        self.config = Config(os.path.join(THEME_DIR, self.theme_file))
        self.config.load()
        self.name = self.config.get("theme", "name")
        self.color = self.config.get("window", "color")
        self.enable_gaussian = self.config.get("window", "enable_gaussian")
        self.enable_advanced_menu = self.config.get("window", "enable_advanced_menu")
        self.title = self.config.get("name", "zh_CN")
        self.system_wallpapers = map(lambda (k, v): k, self.config.config_parser.items("system_wallpaper"))
        self.user_wallpapers = map(lambda (k, v): k, self.config.config_parser.items("user_wallpaper"))
        
    def get_wallpaper_paths(self):
        user_wallpaper_files = map(lambda wallpaper_file: os.path.join(BACKGROUND_DIR, wallpaper_file), self.user_wallpapers)
        system_wallpaper_files = map(lambda wallpaper_file: os.path.join(BACKGROUND_DIR, wallpaper_file), self.system_wallpapers)
        return user_wallpaper_files + system_wallpaper_files

class ThemeView(ScrolledWindow):
    '''
    class docs
    '''
	
    def __init__(self, switch_setting_view):
        '''
        init docs
        '''
        ScrolledWindow.__init__(self, 0, 0)
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.switch_setting_view = switch_setting_view
        self.themes = map(lambda theme_file: Theme(theme_file), 
                          filter(lambda theme_file: os.path.isfile(os.path.join(THEME_DIR, theme_file)) and theme_file.endswith("ini"), os.listdir(THEME_DIR)))
        self.label_padding_x = 10
        self.label_padding_y = 10
        
        self.theme_box = gtk.VBox()
        self.user_theme_label = Label("我的主题")
        self.user_theme_align = gtk.Alignment()
        self.user_theme_align.set(0.0, 0.5, 0, 0)
        self.user_theme_align.set_padding(self.label_padding_y, self.label_padding_y, self.label_padding_x, 0)
        self.user_theme_view = IconView()
        self.user_theme_view.draw_mask = self.draw_mask
        self.user_theme_scrolledwindow = ScrolledWindow()
        self.system_theme_label = Label("系统主题")
        self.system_theme_align = gtk.Alignment()
        self.system_theme_align.set(0.0, 0.5, 0, 0)
        self.system_theme_align.set_padding(self.label_padding_y, self.label_padding_y, self.label_padding_x, 0)
        self.system_theme_view = IconView()
        self.system_theme_view.draw_mask = self.draw_mask
        self.system_theme_scrolledwindow = ScrolledWindow()
        
        self.user_theme_align.add(self.user_theme_label)
        self.theme_box.pack_start(self.user_theme_align, False, False)
        self.user_theme_scrolledwindow.add_child(self.user_theme_view)
        self.theme_box.pack_start(self.user_theme_scrolledwindow, False, False)
        self.system_theme_align.add(self.system_theme_label)
        self.theme_box.pack_start(self.system_theme_align, False, False)
        self.system_theme_scrolledwindow.add_child(self.system_theme_view)
        self.theme_box.pack_start(self.system_theme_scrolledwindow, True, True)
        self.add_child(self.theme_box)
        
        self.user_theme_align.connect("expose-event", self.expose_label_align)
        self.system_theme_align.connect("expose-event", self.expose_label_align)
        
        self.init_theme_view()
        
    def init_theme_view(self):
        user_theme_items = map(lambda theme: ThemeItem(theme, self.switch_setting_view), self.themes)
        system_theme_items = map(lambda theme: ThemeItem(theme, self.switch_setting_view), self.themes)
        
        self.user_theme_view.add_items(user_theme_items)
        self.system_theme_view.add_items(system_theme_items)
        
    def expose_label_align(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        self.draw_mask(cr, rect.x, rect.y, rect.width, rect.height)
                
    def draw_mask(self, cr, x, y, w, h):
        '''
        Draw mask interface.
        
        @param cr: Cairo context.
        @param x: X coordiante of draw area.
        @param y: Y coordiante of draw area.
        @param w: Width of draw area.
        @param h: Height of draw area.
        '''
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
        
gobject.type_register(ThemeView)        

