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


from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.label import Label
import gtk

from theme_view import ThemeView
from theme_manager import theme_manager



class ThemePage(ScrolledWindow):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        ScrolledWindow.__init__(self, 0, 0)
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.label_padding_x = 10
        self.label_padding_y = 10
        
        self.theme_box = gtk.VBox()
        self.user_theme_label = Label("我的主题")
        self.user_theme_align = gtk.Alignment()
        self.user_theme_align.set(0.0, 0.5, 0, 0)
        self.user_theme_align.set_padding(self.label_padding_y, self.label_padding_y, self.label_padding_x, 0)
        self.user_theme_view = ThemeView()
        self.user_theme_scrolledwindow = self.user_theme_view.get_scrolled_window()
        
        self.system_theme_label = Label("系统主题")
        self.system_theme_align = gtk.Alignment()
        self.system_theme_align.set(0.0, 0.5, 0, 0)
        self.system_theme_align.set_padding(self.label_padding_y, self.label_padding_y, self.label_padding_x, 0)
        self.system_theme_view = ThemeView()
        self.system_theme_scrolledwindow = self.system_theme_view.get_scrolled_window()
        
        self.user_theme_align.add(self.user_theme_label)
        self.theme_box.pack_start(self.user_theme_align, False, False)
        self.theme_box.pack_start(self.user_theme_scrolledwindow, False, False)
        self.system_theme_align.add(self.system_theme_label)
        self.theme_box.pack_start(self.system_theme_align, False, False)
        self.theme_box.pack_start(self.system_theme_scrolledwindow, True, True)
        self.add_child(self.theme_box)
        
        self.user_theme_align.connect("expose-event", self.expose_label_align)
        self.system_theme_align.connect("expose-event", self.expose_label_align)
        self.init_theme_view()
        
    def init_theme_view(self):
        user_themes = theme_manager.get_user_themes()
        system_themes = theme_manager.get_system_themes()
        self.user_theme_view.add_themes(user_themes)
        self.system_theme_view.add_themes(system_themes)
        
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
