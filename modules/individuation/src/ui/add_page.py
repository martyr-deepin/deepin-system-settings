#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
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

import gtk
from dtk.ui.new_treeview import TreeView
from ui.add_item import ExpandItem
from ui.cache_page import CachePage
from ui.download_page import TaskPage
from ui.select_page import UserPage, SystemPage, PicturePage
from ui.utils import switch_box, draw_line
from helper import event_manager
from xdg_support import get_system_wallpaper_dirs, get_download_wallpaper_dir, get_images_dir
from aibizhi import Aibizhi
from bizhi360 import Bizhi360
from nls import _

class AddPage(gtk.HBox):
    
    def __init__(self):
        gtk.HBox.__init__(self)

        self.aibizhi_cache_page = CachePage(Aibizhi())
        self.bizhi360_cache_page = CachePage(Bizhi360())
        
        self.aibizhi_cache_page.cache_view.try_to_fetch()
        self.bizhi360_cache_page.cache_view.try_to_fetch()
        self.system_wallpapers_page = SystemPage(get_system_wallpaper_dirs()[0])
        self.picture_wallpapers_page = PicturePage(get_images_dir())
        self.download_wallpapaers_page = UserPage(get_download_wallpaper_dir())

        self.task_page = TaskPage()
        
        self.__init_navigatebar()
        
        self.switch_page = gtk.VBox()
        self.pack_start(self.navigatebar, False, True)
        self.pack_start(self.switch_page, True, True)
        
        self.switch_page.add(self.system_wallpapers_page)
        event_manager.add_callback("downloading-tasks-number", self.on_download_item_changed)
        self.connect("expose-event", self.on_addpage_expose_event)
        
    def set_theme(self, theme):
        self.system_wallpapers_page.set_theme(theme)
        self.picture_wallpapers_page.set_theme(theme)
        self.download_wallpapaers_page.set_theme(theme)
        self.aibizhi_cache_page.set_theme(theme)
        self.bizhi360_cache_page.set_theme(theme)

    def on_download_item_changed(self, name, obj, data):    
        pass

    def __init_navigatebar(self):    
        self.navigatebar = TreeView(enable_drag_drop=False, enable_multiple_select=False)
        self.navigatebar.connect("single-click-item", self.on_navigatebar_single_click)
        self.navigatebar.set_size_request(132, -1)
        self.navigatebar.draw_mask = self.on_navigatebar_draw_mask
        
        local_expand_item = ExpandItem(_("Library"))
        network_expand_item = ExpandItem(_("From Internet"))
        self.navigatebar.add_items([local_expand_item, 
                                    network_expand_item, 
                                   ])
        local_expand_item.add_childs([(_("System"), self.system_wallpapers_page),
                                      (_("Picture"), self.picture_wallpapers_page), 
                                      (_("Downloaded"), self.download_wallpapaers_page)], expand=True)
        network_expand_item.add_childs([(_("LoveBiZhi HD"), self.aibizhi_cache_page),
                                        (_("360BiZhi"), self.bizhi360_cache_page)], expand=True)        
        
        self.navigatebar.set_highlight_item(self.navigatebar.get_items()[1])
        
    def on_addpage_expose_event(self, widget, event):    
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        self.draw_mask(cr, *rect)
        
    def on_navigatebar_draw_mask(self, cr, x, y, w, h):    
        self.draw_mask(cr, x, y, w, h)
        draw_line(cr, (x + w, y), (0, h), "#d6d6d6")        
        
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
        

    def on_navigatebar_single_click(self, widget, item, column, x, y):
        if item.widget:
            widget.set_highlight_item(item)
            switch_box(self.switch_page, item.widget)
