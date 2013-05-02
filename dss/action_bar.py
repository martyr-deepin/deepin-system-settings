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

from nls import _
from theme import app_theme
from dtk.ui.cache_pixbuf import CachePixbuf
from dtk.ui.draw import draw_pixbuf
from dtk.ui.entry import InputEntry
from dtk.ui.button import ImageButton
from dtk.ui.breadcrumb import Bread
from dtk.ui.poplist import IconTextItem
from dtk.ui.utils import propagate_expose, color_hex_to_cairo
import itertools
import gtk
import gobject
import locale

class ActionBar(gtk.Alignment):
    '''
    class docs
    '''
	
    def __init__(self, 
                 module_infos, 
                 switch_page, 
                 click_module_item, 
                 backward_cb=None, 
                 forward_cb=None, 
                 search_cb=None):
        '''
        init docs
        '''
        # Init.
        gtk.Alignment.__init__(self)
        self.module_infos = module_infos
        self.set(0.5, 0.5, 1, 1)
        self.set_padding(0, 0, 0, 0)
        self.set_size_request(-1, 32)

        # Init action box.
        self.main_box = gtk.HBox()
        
        self.cache_bg_pixbuf = CachePixbuf()
        self.bg_pixbuf = app_theme.get_pixbuf("crumb/crumbs_bg.png")

        # Init action button.
        self.backward_align = gtk.Alignment()
        self.backward_align.set(0, 0, 0, 0)
        self.backward_align.set_padding(8, 5, 10, 0)
        self.backward_button = ImageButton(
            app_theme.get_pixbuf("action_button/backward_normal.png"),
            app_theme.get_pixbuf("action_button/backward_hover.png"),
            app_theme.get_pixbuf("action_button/backward_press.png"),
            insensitive_dpixbuf = app_theme.get_pixbuf("action_button/backward_normal.png")
            )
        self.backward_cb = backward_cb
        self.backward_button.connect("clicked", self.__backward_clicked)
        self.backward_align.add(self.backward_button)
        self.forward_align = gtk.Alignment()
        self.forward_align.set(0, 0, 0, 0)
        self.forward_align.set_padding(8, 5, 10, 0)
        self.forward_button = ImageButton(
            app_theme.get_pixbuf("action_button/forward_normal.png"),
            app_theme.get_pixbuf("action_button/forward_hover.png"),
            app_theme.get_pixbuf("action_button/forward_press.png"),
            insensitive_dpixbuf = app_theme.get_pixbuf("action_button/forward_normal.png")
            )
        self.forward_cb = forward_cb
        self.forward_button.connect("clicked", self.__forward_clicked)
        self.forward_align.add(self.forward_button)
        self.action_box = gtk.HBox()
        self.action_align = gtk.Alignment()
        self.action_align.set(0.5, 0, 0, 0)
        self.action_align.set_padding(0, 0, 5, 5)
        self.bread_align = gtk.Alignment()
        self.bread_align.set(0, 0.5, 1, 0)
        self.bread_align.set_padding(0, 0, 4, 4)
        
        # Init navigate bar.
        self.navigate_bar = gtk.HBox()
        self.bread = Bread(crumb = [(_("System Settings"), 
                             map(lambda module_info: ModuleMenuItem(module_info, click_module_item),
                                 list(itertools.chain(*module_infos)))),
                            ], 
                           show_left_right_box = False)
        #self.bread.set_size(-1, 24)
        self.bread.connect("item_clicked", switch_page)
        
        # Init search entry.
        self.search_button = ImageButton(
            app_theme.get_pixbuf("entry/search_normal.png"),
            app_theme.get_pixbuf("entry/search_hover.png"),
            app_theme.get_pixbuf("entry/search_press.png"),
            )
        self.search_cb = search_cb
        self.search_entry = InputEntry(action_button=self.search_button)
        self.search_entry.set_size(150, 24)
        self.search_entry.entry.connect("changed", self.__search_changed)
        self.search_entry.entry.connect("press-return", self.__search_press_enter)
        self.search_align = gtk.Alignment()
        self.search_align.set(0.5, 0.5, 0, 0)
        self.search_align.set_padding(5, 0, 5, 10)
        
        # Connect widgets.
        self.action_align.add(self.action_box)
        self.bread_align.add(self.bread)
        self.search_align.add(self.search_entry)
        self.action_box.pack_start(self.backward_align)
        self.action_box.pack_start(self.forward_align)
        self.navigate_bar.pack_start(self.bread_align, True, True)
        self.main_box.pack_start(self.action_align, False, False)
        self.main_box.pack_start(self.navigate_bar, True, True)
        self.main_box.pack_start(self.search_align, False, False)
        self.add(self.main_box)
        
        # Connect signals.
        self.connect("expose-event", self.expose_action_bar)
   
    def __search_changed(self, widget, event):
        if self.search_cb:
            self.search_cb()

    def __search_press_enter(self, widget):
        if self.search_cb:
            self.search_cb()

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
        
        cr.set_source_rgba(*color_hex_to_cairo("#aeaeae"))
        cr.rectangle(rect.x, rect.y, rect.width, 1)
        cr.rectangle(rect.x, rect.y + rect.height - 1, rect.width, 1)
        cr.fill()
        
        # Propagate expose.
        propagate_expose(widget, event)
        
        return True
    
gobject.type_register(ActionBar)

class ModuleMenuItem(IconTextItem):
    '''
    class docs
    '''
	
    def __init__(self, module_info, click_callback):
        '''
        init docs
        '''
        name = module_info.name
        if len(locale.getdefaultlocale()):
            if locale.getdefaultlocale()[0].find("zh_") != 0:
                name = module_info.default_name
        else:
            name = module_info.default_name

        IconTextItem.__init__(
            self, 
            (module_info.menu_icon_pixbuf,
             module_info.menu_icon_pixbuf,
             module_info.menu_icon_pixbuf,
             ),
            name
            )
        self.module_info = module_info
        self.click_callback = click_callback
        
    def button_press(self, column, offset_x, offset_y):
        self.click_callback(self.module_info)
        
gobject.type_register(ModuleMenuItem)
        
