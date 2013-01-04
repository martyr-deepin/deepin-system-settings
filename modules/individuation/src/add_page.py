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

from dtk.ui.new_treeview import TreeView

from add_item import ExpandItem
from cache_page import CachePage
from download_page import DownloadPage
from ui_utils import switch_box, draw_line
from aibizhi import Aibizhi
from bizhi360 import Bizhi360


class AddPage(gtk.HBox):
    
    def __init__(self):
        gtk.HBox.__init__(self)
        
        self.aibizhi_cache_page = CachePage(Aibizhi())
        self.bizhi360_cache_page = CachePage(Bizhi360())
        
        self.aibizhi_cache_page.cache_view.try_to_fetch()
        self.bizhi360_cache_page.cache_view.try_to_fetch()
        
        self.download_page = DownloadPage()
        
        self.__init_navigatebar()
        
        self.switch_page = gtk.VBox()
        self.pack_start(self.navigatebar, False, True)
        self.pack_start(self.switch_page, True, True)
        
        self.connect("expose-event", self.on_addpage_expose_event)
        
    def __init_navigatebar(self):    
        self.navigatebar = TreeView(enable_drag_drop=False, enable_multiple_select=False)
        self.navigatebar.connect("single-click-item", self.on_navigatebar_single_click)
        self.navigatebar.set_size_request(132, -1)
        self.navigatebar.draw_mask = self.on_navigatebar_draw_mask
        
        local_expand_item = ExpandItem("计算机")
        download_expand_item = ExpandItem("下载管理")
        network_expand_item = ExpandItem("网络壁纸")
        self.navigatebar.add_items([local_expand_item, download_expand_item, network_expand_item])
        
        local_expand_item.add_childs([(name, None) for name in ["主文件夹", "桌面", "视频", "图片", "音乐", "文件系统"]], expand=True)
        download_expand_item.add_childs([("正在下载", self.download_page),
                                         ("下载历史", None)], 
                                        expand=True)
        network_expand_item.add_childs([("爱壁纸", self.aibizhi_cache_page),
                                        ("360壁纸", self.bizhi360_cache_page)], expand=True)        
        
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
            switch_box(self.switch_page, item.widget)
    
