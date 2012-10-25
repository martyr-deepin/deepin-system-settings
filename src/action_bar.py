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

from theme import app_theme
from dtk.ui.entry import InputEntry
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
	
    def __init__(self, module_infos, switch_page):
        '''
        init docs
        '''
        # Init.
        gtk.Alignment.__init__(self)
        self.set(0.5, 0.5, 1, 1)
        self.set_padding(0, 0, 0, 0)
        self.set_size_request(-1, 36)

        # Init action box.
        self.main_box = gtk.HBox()
        
        # Init action button.
        self.backward_button = ImageButton(
            app_theme.get_pixbuf("action_button/backward_normal.png"),
            app_theme.get_pixbuf("action_button/backward_hover.png"),
            app_theme.get_pixbuf("action_button/backward_press.png"),
            )
        self.forward_button = ImageButton(
            app_theme.get_pixbuf("action_button/forward_normal.png"),
            app_theme.get_pixbuf("action_button/forward_hover.png"),
            app_theme.get_pixbuf("action_button/forward_press.png"),
            )
        self.action_box = gtk.HBox()
        self.action_align = gtk.Alignment()
        self.action_align.set(0.5, 0, 0, 0)
        self.action_align.set_padding(0, 0, 5, 5)
        
        # Init navigate bar.
        self.navigate_bar = gtk.HBox()
        self.bread = Bread([("系统设置", 
                             map(lambda module_info: IconTextItem((module_info.menu_icon_pixbuf,
                                                              module_info.menu_icon_pixbuf,
                                                              module_info.menu_icon_pixbuf,
                                                              ),
                                                             module_info.name),
                                 list(itertools.chain(*module_infos)))),
                            ])
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
        self.search_align.set_padding(0, 0, 5, 5)
        
        # Connect widgets.
        self.action_align.add(self.action_box)
        self.search_align.add(self.search_entry)
        self.action_box.pack_start(self.backward_button)
        self.action_box.pack_start(self.forward_button)
        self.navigate_bar.pack_start(self.bread, True, True)
        self.main_box.pack_start(self.action_align, False, False)
        self.main_box.pack_start(self.navigate_bar, True, True)
        self.main_box.pack_start(self.search_align, False, False)
        self.add(self.main_box)
        
        # Connect signals.
        self.connect("expose-event", self.expose_action_bar)
        
    def expose_action_bar(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y, w, h = rect.x, rect.y, rect.width, rect.height

        cr.set_source_rgba(1, 1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()

gobject.type_register(ActionBar)
