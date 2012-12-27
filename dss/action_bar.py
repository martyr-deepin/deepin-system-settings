#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
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

from theme import app_theme
from dtk.ui.cache_pixbuf import CachePixbuf
from dtk.ui.draw import draw_pixbuf
from dtk.ui.new_entry import InputEntry
from dtk.ui.button import ImageButton
from dtk.ui.breadcrumb import Bread
from dtk.ui.poplist import IconTextItem
import itertools
import gtk
import gobject

class ActionBar(gtk.Alignment):
    '''
    class docs
    '''
	
    def __init__(self, 
                 module_infos, 
                 switch_page, 
                 click_module_item, 
                 backward_cb=None, 
                 forward_cb=None):
        '''
        init docs
        '''
        # Init.
        gtk.Alignment.__init__(self)
        self.module_infos = module_infos
        self.set(0.5, 0.5, 1, 1)
        self.set_padding(0, 0, 0, 0)
        self.set_size_request(-1, 36)

        # Init action box.
        self.main_box = gtk.HBox()
        
        self.cache_bg_pixbuf = CachePixbuf()
        self.bg_pixbuf = app_theme.get_pixbuf("crumbs_bg.png")

        # Init action button.
        self.backward_align = gtk.Alignment()
        self.backward_align.set(0, 0, 0, 0)
        self.backward_align.set_padding(10, 5, 10, 0)
        self.backward_button = ImageButton(
            app_theme.get_pixbuf("action_button/backward_normal.png"),
            app_theme.get_pixbuf("action_button/backward_hover.png"),
            app_theme.get_pixbuf("action_button/backward_press.png"),
            )
        self.backward_cb = backward_cb
        self.backward_button.connect("clicked", self.__backward_clicked)
        self.backward_align.add(self.backward_button)
        self.forward_align = gtk.Alignment()
        self.forward_align.set(0, 0, 0, 0)
        self.forward_align.set_padding(10, 5, 10, 0)
        self.forward_button = ImageButton(
            app_theme.get_pixbuf("action_button/forward_normal.png"),
            app_theme.get_pixbuf("action_button/forward_hover.png"),
            app_theme.get_pixbuf("action_button/forward_press.png"),
            )
        self.forward_cb = forward_cb
        self.forward_button.connect("clicked", self.__forward_clicked)
        self.forward_align.add(self.forward_button)
        self.action_box = gtk.HBox()
        self.action_align = gtk.Alignment()
        self.action_align.set(0.5, 0, 0, 0)
        self.action_align.set_padding(0, 0, 5, 5)
        
        # Init navigate bar.
        self.navigate_bar = gtk.HBox()
        self.bread = Bread(crumb = [("系统设置", 
                             map(lambda module_info: ModuleMenuItem(module_info, click_module_item),
                                 list(itertools.chain(*module_infos)))),
                            ], 
                           show_left_right_box = False)
        self.bread.connect("item_clicked", switch_page)
        
        # Init search entry.
        self.search_button = ImageButton(
            app_theme.get_pixbuf("entry/search_normal.png"),
            app_theme.get_pixbuf("entry/search_hover.png"),
            app_theme.get_pixbuf("entry/search_press.png"),
            )
        self.search_entry = InputEntry(action_button=self.search_button)
        self.search_entry.set_size(150, 24)
        self.search_align = gtk.Alignment()
        self.search_align.set(0.5, 0.5, 0, 0)
        self.search_align.set_padding(5, 0, 5, 5)
        
        # Connect widgets.
        self.action_align.add(self.action_box)
        self.search_align.add(self.search_entry)
        self.action_box.pack_start(self.backward_align)
        self.action_box.pack_start(self.forward_align)
        self.navigate_bar.pack_start(self.bread, True, True)
        self.main_box.pack_start(self.action_align, False, False)
        self.main_box.pack_start(self.navigate_bar, True, True)
        self.main_box.pack_start(self.search_align, False, False)
        self.add(self.main_box)
        
        # Connect signals.
        self.connect("expose-event", self.expose_action_bar)
    
    def __backward_clicked(self, widget):
        if self.backward_cb:
            self.backward_cb()

    def __forward_clicked(self, widget):
        if self.forward_cb:
            self.forward_cb()
    
    def expose_action_bar(self, widget, event):
        cr = widget.window.cairo_create()                                        
        rect = widget.allocation
        
        self.cache_bg_pixbuf.scale(self.bg_pixbuf.get_pixbuf(), rect.width, rect.height)
        draw_pixbuf(cr, self.cache_bg_pixbuf.get_cache(), rect.x, rect.y)

gobject.type_register(ActionBar)

class ModuleMenuItem(IconTextItem):
    '''
    class docs
    '''
	
    def __init__(self, module_info, click_callback):
        '''
        init docs
        '''
        IconTextItem.__init__(
            self, 
            (module_info.menu_icon_pixbuf,
             module_info.menu_icon_pixbuf,
             module_info.menu_icon_pixbuf,
             ),
            module_info.name
            )
        self.module_info = module_info
        self.click_callback = click_callback
        
    def button_press(self, column, offset_x, offset_y):
        self.click_callback(self.module_info)
        
gobject.type_register(ModuleMenuItem)
        
