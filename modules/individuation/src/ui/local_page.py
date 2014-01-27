#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012~2013 Deepin, Inc.
#               2012~2013 Kaisheng Ye
#
# Author:     Kaisheng Ye <kaisheng.ye@gmail.com>
# Maintainer: Kaisheng Ye <kaisheng.ye@gmail.com>
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
import os

from dtk.ui.label import Label
from dtk.ui.line import HSeparator
from dtk.ui.treeview import TreeView

from theme import app_theme
from constant import TITLE_FONT_SIZE
from nls import _
from xdg_support import get_download_wallpaper_dir, get_favorite_dir
from aibizhi import Aibizhi
from bizhi360 import Bizhi360
from settings import global_settings
from helper import event_manager

from ui.cache_page import CachePage
from ui.utils import switch_box, draw_line
from ui.add_item import ExpandItem
from ui.select_page import FavoritePage, LocalPicturePage
from ui.download_page import TaskPage
from ui.wallpaper_item import AddItem

FavoritesTitle = _("My Favorites")
LocalWallpapersTitle = _("Local Wallpapers")

def get_favorite_number():
    return len(os.listdir(get_favorite_dir()))

class MainBox(gtk.HBox):
    def __init__(self):
        gtk.HBox.__init__(self)
        self.connect("expose-event", self.on_page_expose_event)

        self.aibizhi_cache_page = CachePage(Aibizhi())
        self.bizhi360_cache_page = CachePage(Bizhi360())
        self.aibizhi_cache_page.cache_view.try_to_fetch()
        self.bizhi360_cache_page.cache_view.try_to_fetch()

        self.favorites_page = FavoritePage(get_favorite_dir())
        self.pictures_page = LocalPicturePage(get_download_wallpaper_dir())

        self.add_item = AddItem()
        self.pictures_page.select_view.add_items([self.add_item])

        self.task_page = TaskPage()
        
        self.switch_page = gtk.VBox()
        self.__init_navigatebar()

        self.pack_start(self.navigatebar, False, True)
        self.pack_start(self.switch_page, True, True)

        event_manager.add_callback("switch-to-local-pictures", self.switch_to_local_pictures)

    def switch_to_local_pictures(self, name, obj, data=None):
        item = self.navigatebar.get_items()[2]
        self.on_navigatebar_single_click(self.navigatebar, item, 0, 0, 0)

    def __init_navigatebar(self):
        self.navigatebar = TreeView(enable_drag_drop=False, enable_multiple_select=False)
        self.navigatebar.connect("single-click-item", self.on_navigatebar_single_click)
        self.navigatebar.set_size_request(132, -1)
        self.navigatebar.draw_mask = self.on_navigatebar_draw_mask
        
        local_expand_item = ExpandItem(_("Library"))
        network_expand_item = ExpandItem(_("Internet"))
        self.navigatebar.add_items([local_expand_item, 
                                    network_expand_item, 
                                   ])
        local_expand_item.add_childs([
            (FavoritesTitle, self.favorites_page),
            (LocalWallpapersTitle, self.pictures_page),
            ],
            expand=True)
        network_expand_item.add_childs([(_("360 Wallpaper"), self.bizhi360_cache_page), 
                                        (_("LoveWallpaper"), self.aibizhi_cache_page),
                                       ], expand=True)        
        
        if get_favorite_number() == 0:
            self.navigatebar.set_highlight_item(self.navigatebar.get_items()[2])
            self.switch_page.add(self.pictures_page)
        else:
            self.navigatebar.set_highlight_item(self.navigatebar.get_items()[1])
            self.switch_page.add(self.favorites_page)

    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()

    def on_page_expose_event(self, widget, event):    
        cr = widget.window.cairo_create()
        width, height= widget.size_request()
        self.draw_mask(cr, 0, 0, width, height)

    def on_navigatebar_draw_mask(self, cr, x, y, w, h):    
        self.draw_mask(cr, x, y, w, h)
        draw_line(cr, (x + w, y), (0, h), "#d6d6d6")        

    def on_navigatebar_single_click(self, widget, item, column, x, y):
        if item.widget:
            widget.set_highlight_item(item)
            switch_box(self.switch_page, item.widget)

