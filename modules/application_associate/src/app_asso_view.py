#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2012 Zhai Xiang
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

from dtk.ui.init_skin import init_skin
from dtk.ui.utils import get_parent_dir
import os

app_theme = init_skin(
    "deepin-application-associate-settings", 
    "1.0",
    "01",
    os.path.join(get_parent_dir(__file__, 2), "skin"),
    os.path.join(get_parent_dir(__file__, 2), "theme"),
    )

from dtk.ui.tab_window import TabBox
from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
from dtk.ui.constant import DEFAULT_FONT_SIZE, ALIGN_START, ALIGN_END
import gobject
import gtk

from app_view import AppView
from media_view import MediaView

class AppMain(gtk.Alignment):

    def __init__(self):
        gtk.Alignment.__init__(self, 0.5, 0.5, 1, 1)
        self.set_padding(15, 15, 27, 27)
        self.add(AppAssoView())

class AppAssoView(TabBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        TabBox.__init__(self)
        #self.set_size_request(722, 356)
        
        self.app_box = AppView()
        self.autorun_box = MediaView()
        self.boot_box = gtk.VBox()

        self.add_items([("应用程序", self.app_box), 
                        ("自动运行", self.autorun_box), 
                        ("启动项", self.boot_box)])

    def __setup_label(self, text="", align=ALIGN_END):
        label = Label(text, None, DEFAULT_FONT_SIZE, align, 140)
        return label

    def __setup_combo(self, items=[]):
        combo = ComboBox(items, None, 0, 120)
        return combo

    '''
    temperary pixbuf I am not a designer :)
    '''
    def __setup_toggle(self):
        toggle = ToggleButton(app_theme.get_pixbuf("inactive_normal.png"), 
            app_theme.get_pixbuf("active_normal.png"))
        return toggle

    def __setup_align(self):
        align = gtk.Alignment()
        align.set(0.0, 0.5, 0, 0)
        align.set_padding(self.label_padding_y, self.label_padding_y, self.label_padding_x, 0)
        return align

    def __widget_pack_start(self, parent_widget, widgets=[]):
        if parent_widget == None:
            return
        for item in widgets:
            parent_widget.pack_start(item, False, False)

    def __combo_item_selected(self, widget, item_text=None, item_value=None, item_index=None, object=None):
        if object == "press_button_power":
            return

        if object == "close_notebook_cover":
            return

        if object == "press_button_hibernate":
            return

        if object == "hibernate_status":
            return

        if object == "close_harddisk":
            return

        if object == "close_monitor":
            return

    def __toggled(self, widget, object=None):
        if object == "wakeup_password":
            return

        if object == "tray_battery_status":
            return

gobject.type_register(AppAssoView)        
