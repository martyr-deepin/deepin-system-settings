#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Deepin, Inc.
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
    "deepin-date_time-settings", 
    "1.0",
    "01",
    os.path.join(get_parent_dir(__file__, 2), "skin"),
    os.path.join(get_parent_dir(__file__, 2), "app_theme"),
    )

from dtk.ui.timezone import TimeZone
from dtk.ui.datetime import DateTime
from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
from dtk.ui.button import ToggleButton
from dtk.ui.constant import DEFAULT_FONT_SIZE, ALIGN_START, ALIGN_END
from dtk.ui.utils import get_optimum_pixbuf_from_file
import gobject
import gtk

class DatetimeView(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)

        self.timezone_items = []
        i = -11
        j = 0
        while i < 12:
            self.timezone_items.append(("%d时区" % i, j))
            
            i += 1
            j += 1

        '''
        timezone map && datetime
        '''
        self.timezone_align = self.__setup_align()
        self.timezone_box = gtk.HBox(spacing=40)
        self.timezone = TimeZone(width=400, height=230)
        self.datetime = DateTime(12, 12, width=400, height=145, box_spacing=180)
        self.__widget_pack_start(self.timezone_box, [self.timezone, self.datetime])
        self.timezone_align.add(self.timezone_box)
        '''
        choose timezone
        '''
        self.set_align = self.__setup_align()
        self.set_box = gtk.HBox(spacing=10)
        self.timezone_label = self.__setup_label("时区")
        self.timezone_combo = ComboBox(self.timezone_items, max_width = 340)
        self.auto_set_time_label = self.__setup_label("自动设置时间", 100)
        self.auto_set_time_toggle = self.__setup_toggle()
        self.time_display_label = self.__setup_label("24小时置显示", 100)
        self.time_display_toggle = self.__setup_toggle()
        self.__widget_pack_start(self.set_box, 
                                 [self.timezone_label, 
                                  self.timezone_combo, 
                                  self.auto_set_time_label, 
                                  self.auto_set_time_toggle, 
                                  self.time_display_label, 
                                  self.time_display_toggle])
        self.set_align.add(self.set_box)
        '''
        this->gtk.VBox pack_start
        '''
        self.__widget_pack_start(self, [self.timezone_align, self.set_align])
    
    def __combo_item_selected(self, widget, item_text=None, item_value=None, item_index=None, object=None):
        pass

    def __setup_label(self, text="", width=50, align=ALIGN_END):
        label = Label(text, None, DEFAULT_FONT_SIZE, align, width)
        return label

    def __setup_combo(self, items=[], width=120):
        combo = ComboBox(items, None, 0, width)
        return combo

    def __setup_toggle(self):
        toggle = ToggleButton(app_theme.get_pixbuf("inactive_normal.png"), 
            app_theme.get_pixbuf("active_normal.png"))
        return toggle

    def __setup_align(self, xalign=0.5, yalign=0.5, xscale=1.0, yscale=1.0, 
                      padding_top=20, padding_bottom=20, padding_left=20, padding_right=20):
        align = gtk.Alignment()
        align.set(xalign, yalign, xscale, yscale)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        return align

    def __widget_pack_start(self, parent_widget, widgets=[], expand=False, fill=False):
        if parent_widget == None:
            return
        for item in widgets:
            parent_widget.pack_start(item, expand, fill)

gobject.type_register(DatetimeView)
