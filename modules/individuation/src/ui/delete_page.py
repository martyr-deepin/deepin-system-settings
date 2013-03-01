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

from theme import app_theme
import gtk
import gobject
from dtk.ui.tab_window import TabBox
from dtk.ui.label import Label
from dtk.ui.button import Button, CheckButton
from dtk.ui.scalebar import HScalebar
from dtk.ui.constant import ALIGN_END
from ui.wallpaper_item import ITEM_PADDING_Y
from ui.wallpaper_view import WallpaperView
from constant import STATUS_HEIGHT, WIDGET_HEIGHT
from helper import event_manager
from nls import _

class DeletePage(TabBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        TabBox.__init__(self)

        self.draw_title_background = self.draw_tab_title_background
        self.theme = None
        
        self.wallpaper_box = gtk.VBox()
        self.wallpaper_view = WallpaperView(padding_x=30, padding_y=ITEM_PADDING_Y)
        self.wallpaper_view_sw = self.wallpaper_view.get_scrolled_window()
        
        self.action_align = gtk.Alignment()
        self.action_align.set_padding(5, 5, 500, 5)
        self.action_box = gtk.HBox(spacing = 10)
        self.back_button = Button(_("Back"))
        self.back_button.set_size_request(80, WIDGET_HEIGHT)
        self.back_button.connect("clicked", self.__on_back)
        self.select_all_button = Button(_("Select All"))
        self.select_all_button.set_size_request(80, WIDGET_HEIGHT)
        self.select_all_button.connect("clicked", self.__on_select_all)
        self.delete_button = Button(_("Delete"))
        self.delete_button.set_size_request(80, WIDGET_HEIGHT)
        self.delete_button.connect("clicked", self.__on_delete)
        self.action_box.pack_start(self.back_button, False, False)
        self.action_box.pack_start(self.select_all_button, False, False)
        self.action_box.pack_start(self.delete_button, False, False)
        self.action_align.add(self.action_box)
        
        self.wallpaper_box.pack_start(self.wallpaper_view_sw, True, True)
        self.wallpaper_box.pack_start(self.action_align, False, False)

    def __on_back(self, widget):
        event_manager.emit("back-to-detailpage", self.theme)

    def __on_select_all(self, widget):
        self.wallpaper_view.select_all(True)

    def __on_delete(self, widget):
        self.wallpaper_view.delete_wallpaper()

    def draw_tab_title_background(self, cr, widget):
        rect = widget.allocation
        cr.set_source_rgb(1, 1, 1)    
        cr.rectangle(0, 0, rect.width, rect.height - 1)
        cr.fill()

    def set_theme(self, theme):
        self.theme = theme
        
        '''
        TODO: self.theme.name
        '''
        self.delete_items(self.tab_items)
        self.add_items([(self.theme.get_name(), self.wallpaper_box),                   
                       ])
        
        self.wallpaper_view.set_theme(theme, True)
        self.wallpaper_view.select_all(False)
        
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
        
gobject.type_register(DeletePage)        