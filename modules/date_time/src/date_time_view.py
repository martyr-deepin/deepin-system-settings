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

from theme import app_theme
from dtk.ui.timezone import TimeZone
from dtk.ui.datetime import DateTime
from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
from dtk.ui.button import ToggleButton
from dtk.ui.spin import SpinBox
from dtk.ui.constant import DEFAULT_FONT_SIZE, ALIGN_START, ALIGN_END
from dtk.ui.utils import color_hex_to_cairo
import gobject
import gtk
from constant import *
from datetime import DeepinDateTime

class DatetimeView(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)

        self.deepin_dt = DeepinDateTime()
        self.current_tz_gmtoff = self.deepin_dt.get_gmtoff()

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
        self.timezone_align = self.__setup_align(padding_top = TEXT_WINDOW_TOP_PADDING, 
                                                 padding_left = TEXT_WINDOW_LEFT_PADDING)
        self.timezone_box = gtk.HBox()
        self.timezone = TimeZone(self.current_tz_gmtoff, 
                                 380, 
                                 230, 
                                 TEXT_WINDOW_TOP_PADDING, 
                                 TEXT_WINDOW_LEFT_PADDING)
        self.timezone.connect("changed", self.__timezone_changed)
        self.datetime_box = gtk.VBox()
        self.datetime_align = self.__setup_align(padding_top = 0, padding_left = 80)
        self.datetime = DateTime()
        self.datetime_align.add(self.datetime)
        self.datetime_edit_align = self.__setup_align(padding_left = 100)
        self.datetime_edit_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.hour_spin = SpinBox(12, 0, 24, 1)
        self.min_spin = SpinBox(12, 0, 60, 1)
        self.__widget_pack_start(self.datetime_edit_box, [self.hour_spin, self.min_spin])
        self.datetime_edit_align.add(self.datetime_edit_box)
        self.__widget_pack_start(self.datetime_box, [self.datetime_align])
        self.__widget_pack_start(self.timezone_box, [self.timezone, self.datetime_box])
        self.timezone_align.add(self.timezone_box)
        '''
        choose timezone
        '''
        self.set_align = self.__setup_align(padding_left = TEXT_WINDOW_LEFT_PADDING)
        self.set_box = gtk.HBox(spacing=WIDGET_SPACING)
        self.timezone_label = self.__setup_label(text = "时区", width = 30, align = ALIGN_START)
        self.timezone_combo = ComboBox(self.timezone_items, max_width = 340)
        self.timezone_combo.set_select_index(self.current_tz_gmtoff + 11)
        self.timezone_combo.connect("item-selected", self.__combo_item_selected)
        self.auto_set_time_label = self.__setup_label("自动设置时间", 100)
        self.auto_set_time_align = self.__setup_align(padding_top = 4, padding_left = 0, padding_right = 0)
        self.auto_set_time_toggle = self.__setup_toggle()
        self.auto_set_time_align.add(self.auto_set_time_toggle)
        self.time_display_label = self.__setup_label("24小时置显示", 100)
        self.time_display_align = self.__setup_align(padding_top = 4, padding_left = 0, padding_right = 0)
        self.time_display_toggle = self.__setup_toggle()
        self.time_display_align.add(self.time_display_toggle)
        self.__widget_pack_start(self.set_box, 
                                 [self.timezone_label, 
                                  self.timezone_combo, 
                                  self.auto_set_time_label, 
                                  self.auto_set_time_align, 
                                  self.time_display_label, 
                                  self.time_display_align])
        self.set_align.add(self.set_box)
        '''
        this->gtk.VBox pack_start
        '''
        self.__widget_pack_start(self, [self.timezone_align, self.set_align])

        self.connect("expose-event", self.__expose)

    def __timezone_changed(self, widget, timezone):
        self.timezone_combo.set_select_index(timezone + 11)
        self.deepin_dt.set_timezone_by_gmtoff(timezone)

    def __expose(self, widget, event):                                           
        cr = widget.window.cairo_create()                                        
        rect = widget.allocation                                    
        
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)                        
        cr.fill()
    
    def __combo_item_selected(self, widget, item_text=None, item_value=None, item_index=None):
        self.timezone.set_timezone(item_value - 11)
        self.deepin_dt.set_timezone_by_gmtoff(item_value - 11)

    def __setup_label(self, text="", width=50, align=ALIGN_END):
        label = Label(text, None, DEFAULT_FONT_SIZE, align, width)
        return label

    def __setup_toggle(self):
        toggle = ToggleButton(app_theme.get_pixbuf("toggle_button/inactive_normal.png"), 
            app_theme.get_pixbuf("toggle_button/active_normal.png"))
        return toggle

    def __setup_align(self, 
                      xalign=0, 
                      yalign=0, 
                      xscale=0, 
                      yscale=0, 
                      padding_top=BETWEEN_SPACING, 
                      padding_bottom=0, 
                      padding_left=TEXT_WINDOW_LEFT_PADDING, 
                      padding_right=20):
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
