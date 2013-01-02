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
from dtk.ui.tab_window import TabBox
from dtk.ui.timezone import TimeZone
from dtk.ui.datetime import DateTime
from dtk.ui.spin import TimeSpinBox
from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
from dtk.ui.button import ToggleButton
from dtk.ui.constant import ALIGN_START, ALIGN_END
from dtk.ui.utils import color_hex_to_cairo
import os
import gobject
import gtk
try:
    import deepin_lunar
except ImportError:
    print "===Please Install Deepin Lunar Python Binding==="
    print "git clone git@github.com:xiangzhai/liblunar.git"
    print "==============================================="
try:                                                                            
    import deepin_gsettings                                                     
except ImportError:                                                             
    print "----------Please Install Deepin GSettings Python Binding----------"  
    print "git clone git@github.com:linuxdeepin/deepin-gsettings.git"           
    print "------------------------------------------------------------------"  

from constant import *
from nls import _
from deepin_dt import DeepinDateTime
import threading as td

class AutoSetTimeThread(td.Thread):
    def __init__(self, ThisPtr):
        td.Thread.__init__(self)
        self.setDaemon(True)
        self.ThisPtr = ThisPtr

    def run(self):
        self.ThisPtr.auto_set_time()

class DatetimeView(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)

        self.datetime_settings = deepin_gsettings.new("com.deepin.dde.datetime")

        self.__deepin_dt = DeepinDateTime()
        self.current_tz_gmtoff = self.__deepin_dt.get_gmtoff()

        self.timezone_items = []
        i = -11
        j = 0
        while i < 12:
            self.timezone_items.append(("%d时区" % i, j))
            
            i += 1
            j += 1

        self.tab_align = self.__setup_align(padding_top = FRAME_TOP_PADDING, padding_left = 0)
        self.tab_box = TabBox()
        self.tab_box.set_size_request(800, -1)
        self.tab_box.draw_title_background = self.__draw_title_background
        '''
        datetime box
        '''
        self.datetime_box = gtk.VBox()
        self.datetime_box.connect("expose-event", self.__expose)
        self.datetime_align = self.__setup_align()
        self.set_datetime_box = gtk.HBox()
        if os.environ['LANGUAGE'].find("zh_") == 0:
            self.calendar = deepin_lunar.new()
        else:
            self.calendar = gtk.Calendar()
        self.calendar.set_size_request(360, 280)
        self.datetime_widget_box = gtk.VBox()
        self.datetime_widget_align = self.__setup_align(padding_top = 0, padding_left = 90)
        self.datetime_widget = DateTime()
        self.datetime_widget_align.add(self.datetime_widget)
        self.set_time_align = self.__setup_align(padding_top = 20, padding_left = 130)
        self.set_time_spin = TimeSpinBox()
        self.set_time_spin.set_size_request(100, -1)
        self.set_time_spin.connect("value-changed", self.__time_changed)
        self.set_time_align.add(self.set_time_spin)
        self.auto_time_align = self.__setup_align(padding_top = 20, padding_left = 0)
        self.auto_time_box = gtk.HBox(spacing = BETWEEN_SPACING)
        self.auto_time_label = self.__setup_label(_("Auto Set Time"))
        self.auto_time_toggle = self.__setup_toggle()
        is_auto_set_time = self.datetime_settings.get_boolean("is-auto-set")
        if is_auto_set_time == True:
            AutoSetTimeThread(self).start()
        self.auto_time_toggle.set_active(is_auto_set_time)
        #self.auto_time_toggle.connect("toggled", self.__toggled, "auto_time_toggle")
        self.time_display_label = self.__setup_label("24 %s" % _("Hour Display"))
        self.time_display_toggle = self.__setup_toggle()
        self.__widget_pack_start(self.auto_time_box, 
                                 [self.auto_time_label, 
                                  self.auto_time_toggle, 
                                  self.time_display_label, 
                                  self.time_display_toggle])
        self.auto_time_align.add(self.auto_time_box)
        self.__widget_pack_start(self.datetime_widget_box, 
                                 [self.datetime_widget_align, 
                                  self.set_time_align, 
                                  self.auto_time_align])
        self.__widget_pack_start(self.set_datetime_box, 
                                 [self.calendar, self.datetime_widget_box])
        self.datetime_align.add(self.set_datetime_box)
        self.__widget_pack_start(self.datetime_box, [self.datetime_align])
        '''
        timezone box
        '''
        self.timezone_box = gtk.VBox()
        self.timezone_box.connect("expose-event", self.__expose)
        self.timezone_align = self.__setup_align(padding_top = TEXT_WINDOW_TOP_PADDING, 
                                                 padding_left = TEXT_WINDOW_LEFT_PADDING)
        self.timezone = TimeZone(self.current_tz_gmtoff,                        
                                 680,                                           
                                 300,                                           
                                 TEXT_WINDOW_TOP_PADDING + FRAME_TOP_PADDING,                       
                                 TEXT_WINDOW_LEFT_PADDING)                      
        self.timezone.connect("changed", self.__timezone_changed)
        self.timezone_align.add(self.timezone)
        self.set_timezone_align = self.__setup_align(padding_top = 10, 
                                                     padding_left = TEXT_WINDOW_LEFT_PADDING)
        self.set_timezone_box = gtk.HBox(spacing=WIDGET_SPACING)                         
        self.timezone_label = self.__setup_label(text = _("TimeZone"), width = 60, align = ALIGN_START)
        self.timezone_combo = ComboBox(self.timezone_items, max_width = 340)    
        self.timezone_combo.set_select_index(self.current_tz_gmtoff + 11)       
        self.timezone_combo.connect("item-selected", self.__combo_item_selected)
        self.__widget_pack_start(self.set_timezone_box, [self.timezone_label, self.timezone_combo])
        self.set_timezone_align.add(self.set_timezone_box)
        self.__widget_pack_start(self.timezone_box, [self.timezone_align, self.set_timezone_align])
        '''
        TabBox add_items
        '''
        self.tab_box.add_items([(_("DateTime"), self.datetime_box), 
                                (_("TimeZone"), self.timezone_box)])
        self.tab_align.add(self.tab_box)
        self.pack_start(self.tab_align)
        self.connect("expose-event", self.__expose)
    
    def auto_set_time(self):
        self.__deepin_dt.set_using_ntp(True)

    def __time_changed(self, widget, hour, min, sec):
        self.__deepin_dt.set_time_by_hms(hour, min, sec)

    def __timezone_changed(self, widget, timezone):
        self.timezone_combo.set_select_index(timezone + 11)
        self.__deepin_dt.set_timezone_by_gmtoff(timezone)

    def __expose(self, widget, event):
        cr = widget.window.cairo_create()                                       
        rect = widget.allocation                                                
                                                                                
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                     
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)                       
        cr.fill()        

    def __draw_title_background(self, cr, widget):                                           
        rect = widget.allocation                                    
        
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                 
        cr.rectangle(rect.x, 
                     rect.y - FRAME_TOP_PADDING, 
                     rect.width, 
                     rect.height - 1)                        
        cr.fill()
    
    def __combo_item_selected(self, widget, item_text=None, item_value=None, item_index=None):
        self.timezone.set_timezone(item_value - 11)
        self.__deepin_dt.set_timezone_by_gmtoff(item_value - 11)

    def __setup_label(self, text="", width=100, align=ALIGN_END):
        label = Label(text, None, CONTENT_FONT_SIZE, align, width)
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
                      padding_top=TEXT_WINDOW_TOP_PADDING, 
                      padding_bottom=0, 
                      padding_left=TEXT_WINDOW_LEFT_PADDING, 
                      padding_right=0):
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
