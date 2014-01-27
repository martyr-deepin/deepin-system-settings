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

from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.label import Label
import gtk
from ui.status_box import StatusBox
from ui.theme_view import UserThemeView, SystemThemeView
from ui.utils import get_separator
from constant import TITLE_FONT_SIZE, CONTENT_FONT_SIZE, TREEVIEW_BORDER_COLOR
from theme import app_theme
from nls import _

class ThemePage(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)

        self.status_box = StatusBox()

        self.scroll = ScrolledWindow()
        self.scroll.set_size_request(800, 432)
        self.scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        self.label_padding_x = 10
        self.label_padding_y = 10
        
        self.theme_box = gtk.VBox()
        self.user_theme_label = Label(_("My Themes"), text_size=TITLE_FONT_SIZE, 
                                      text_color=app_theme.get_color("globalTitleForeground"))
        self.user_theme_view = UserThemeView(status_box = self.status_box)
        self.user_theme_scrolledwindow = self.user_theme_view.get_scrolled_window()
        
        self.system_theme_label = Label(_("System Themes"), text_size=TITLE_FONT_SIZE, 
                                      text_color=app_theme.get_color("globalTitleForeground"))
        self.system_theme_view = SystemThemeView(status_box = self.status_box)
        self.system_theme_scrolledwindow = self.system_theme_view.get_scrolled_window()
        
        self.theme_box.pack_start(self.user_theme_label, False, False)
        self.theme_box.pack_start(get_separator(), False, False)
        self.theme_box.pack_start(self.user_theme_scrolledwindow, False, False)
        
        self.theme_box.pack_start(self.system_theme_label, False, False)
        self.theme_box.pack_start(get_separator(), False, False)
        self.theme_box.pack_start(self.system_theme_scrolledwindow, True, True)
        
        main_align = gtk.Alignment()
        main_align.set_padding(15, 0, 20, 20)
        main_align.set(1, 1, 1, 1)
        main_align.add(self.theme_box)
        
        self.scroll.add_child(main_align)
        
        main_align.connect("expose-event", self.expose_label_align)

        self.pack_start(self.scroll, False, False)
        self.pack_start(self.status_box)
        
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
