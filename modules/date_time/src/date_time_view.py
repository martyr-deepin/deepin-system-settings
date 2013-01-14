#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Zhai Xiang
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
from dtk.ui.button import Button
from dtk.ui.datetime import DateTimeHTCStyle
from dtk.ui.spin import TimeSpinBox
from dtk.ui.box import ImageBox
from dtk.ui.label import Label
from dtk.ui.line import HSeparator
from dtk.ui.combo import ComboBox
from dtk.ui.button import ToggleButton
from dtk.ui.constant import ALIGN_START, ALIGN_END
from dtk.ui.utils import color_hex_to_cairo
import os
import gobject
import gtk
import time
try:
    import deepin_lunar
except ImportError:
    print "===Please Install Deepin Lunar Python Binding==="
    print "git clone git@github.com:linuxdeepin/liblunar.git"
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

class SetDateThread(td.Thread):
    def __init__(self, dt, day, month, year):
        td.Thread.__init__(self)
        self.setDaemon(True)
        self.__deepin_dt = dt
        self.year = year
        self.month = month
        self.day = day

    def run(self):
        self.__deepin_dt.set_date(self.day, self.month, self.year)

class SecondThread(td.Thread):
    def __init__(self, ThisPtr):
        td.Thread.__init__(self)
        self.setDaemon(True)
        self.ThisPtr = ThisPtr

    def run(self):
        while True:
            self.ThisPtr.set_cur_time_label()
            time.sleep(1)

class AutoSetTimeThread(td.Thread):
    def __init__(self, ThisPtr):
        td.Thread.__init__(self)
        self.setDaemon(True)
        self.ThisPtr = ThisPtr

    def run(self):
        self.ThisPtr.auto_set_time()

class DatetimeView(gtk.HBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        gtk.HBox.__init__(self)

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
       
        self.is_24hour = self.datetime_settings.get_boolean("is-24hour")
        '''
        left align
        '''
        self.left_align = self.__setup_align(
            padding_top = TEXT_WINDOW_TOP_PADDING, 
            padding_left = TEXT_WINDOW_LEFT_PADDING)
        '''
        left box
        '''
        self.left_box = gtk.VBox()
        '''
        calendar title
        '''
        self.calendar_title_align = self.__setup_title_align(
            app_theme.get_pixbuf("datetime/calendar.png"), _("Calendar"))
        '''
        current date
        '''
        self.cur_date_align = self.__setup_align()
        self.cur_date_label = self.__setup_label(
            _("Current Date: %d-%d-%d") % (time.localtime().tm_year, 
                                           time.localtime().tm_mon, 
                                           time.localtime().tm_mday), 
            150)
        self.cur_date_align.add(self.cur_date_label)
        '''
        calendar widget
        '''
        self.calendar_align = self.__setup_align(padding_top = BETWEEN_SPACING, 
            padding_bottom = 10)
        if os.environ['LANGUAGE'].find("zh_") == 0:
            self.calendar = deepin_lunar.new()
        else:
            self.calendar = gtk.Calendar()
        self.calendar.mark_day(time.localtime().tm_mday)
        if os.environ['LANGUAGE'].find("zh_") == 0:
            self.calendar.get_handle().set_size_request(300, 280)
            self.calendar.get_handle().connect("day-selected", self.__on_day_selected, self.calendar)
            self.calendar_align.add(self.calendar.get_handle())
        else:
            self.calendar.set_size_request(300, 280)
            self.calendar_align.add(self.calendar) 
        self.change_date_box = gtk.HBox(spacing = 5)
        self.change_date_align = self.__setup_align()
        self.change_date_button = Button(_("Change Date"))
        self.change_date_button.set_size_request(80, WIDGET_HEIGHT)
        self.change_date_button.connect("button-press-event", self.__on_change_date)
        self.change_date_align.add(self.change_date_button)
        self.edit_date_align = self.__setup_align(padding_left = 110)
        self.edit_date_box = gtk.HBox(spacing = 5)
        self.cancel_date_button = Button(_("Cancel"))
        self.cancel_date_button.set_size_request(50, WIDGET_HEIGHT)
        self.cancel_date_button.connect("button-press-event", self.__on_cancel_change_date)
        self.confirm_date_button = Button(_("Confirm"))
        self.confirm_date_button.set_size_request(50, WIDGET_HEIGHT)
        self.confirm_date_button.connect("button-press-event", self.__on_confirm_change_date)
        self.__widget_pack_start(self.edit_date_box, 
            [self.cancel_date_button, self.confirm_date_button])
        self.edit_date_align.add(self.edit_date_box)
        self.__widget_pack_start(self.change_date_box, 
            [self.edit_date_align, self.change_date_align])
        self.edit_date_align.set_child_visible(False)
        '''
        left box && align
        '''
        self.__widget_pack_start(self.left_box, 
            [self.calendar_title_align, 
             self.cur_date_align, 
             self.calendar_align, 
             self.change_date_box])
        self.left_align.add(self.left_box)
        '''
        right align
        '''
        self.right_align = self.__setup_align(
            padding_top = TEXT_WINDOW_TOP_PADDING, padding_left = TEXT_WINDOW_LEFT_PADDING)
        '''
        right box
        '''
        self.right_box = gtk.VBox()
        '''
        time title
        '''
        self.time_title_align = self.__setup_title_align(
            app_theme.get_pixbuf("datetime/time.png"), _("Time"))
        '''
        current time
        '''
        self.cur_time_align = self.__setup_align()
        if self.is_24hour:
            self.cur_time_label = self.__setup_label(
                _("Current Time: %s %02d:%02d:%02d (%d Hour)") % 
                  (time.strftime('%p'), 
                   time.localtime().tm_hour, 
                   time.localtime().tm_min, 
                   time.localtime().tm_sec, 
                   24), 
                260)
        else:
            self.cur_time_label = self.__setup_label(                           
                _("Current Time: %s %02d:%02d:%02d (%d Hour)") %                
                  (time.strftime('%p'),                                         
                   time.localtime().tm_hour,                                    
                   time.localtime().tm_min,                                     
                   time.localtime().tm_sec,                                     
                   12),                                                         
                260)     

        self.cur_time_align.add(self.cur_time_label)
        '''
        DateTime widget
        '''
        self.datetime_widget_align = self.__setup_align(padding_top = BETWEEN_SPACING)
        self.datetime_widget = DateTimeHTCStyle(is_24hour = self.is_24hour)
        self.datetime_widget_align.add(self.datetime_widget)
        self.set_time_align = self.__setup_align()
        '''
        auto time get && set
        '''
        self.auto_time_align = self.__setup_align(padding_top = TEXT_WINDOW_TOP_PADDING)
        self.auto_time_box = gtk.HBox(spacing = BETWEEN_SPACING)
        self.auto_time_label = self.__setup_label(_("Auto Set Time"))
        self.auto_time_toggle = self.__setup_toggle()
        is_auto_set_time = self.datetime_settings.get_boolean("is-auto-set")
        if is_auto_set_time:
            AutoSetTimeThread(self).start()
        self.auto_time_toggle_align = self.__setup_align(padding_top = 4)
        self.auto_time_toggle.set_active(is_auto_set_time)
        self.auto_time_toggle.connect("toggled", self.__toggled, "auto_time_toggle")
        self.auto_time_toggle_align.add(self.auto_time_toggle)
        '''
        set time
        '''
        self.set_time_spin_align = self.__setup_align(padding_left = 10)
        self.set_time_box = gtk.HBox()
        self.set_time_label = self.__setup_label(_("Manual Set"), 70)
        self.set_time_spin = TimeSpinBox(is_24hour = self.is_24hour)                 
        self.set_time_spin.set_size_request(85, -1)                               
        self.set_time_spin.connect("value-changed", self.__time_changed)
        self.__widget_pack_start(self.set_time_box, 
            [self.set_time_label, self.set_time_spin])
        self.set_time_spin_align.add(self.set_time_box)
        self.__widget_pack_start(self.auto_time_box, 
                                 [self.auto_time_label, 
                                  self.auto_time_toggle_align, 
                                  self.set_time_spin_align]) 
        if is_auto_set_time:
            self.set_time_spin_align.set_child_visible(False)
        self.auto_time_align.add(self.auto_time_box)
        '''
        24hour display
        '''
        self.time_display_align = self.__setup_align(padding_top = BETWEEN_SPACING)
        self.time_display_box = gtk.HBox(spacing = BETWEEN_SPACING)
        self.time_display_label = self.__setup_label("24 %s" % _("Hour Display"))
        self.time_display_toggle_align = self.__setup_align()
        self.time_display_toggle = self.__setup_toggle()                        
        self.time_display_toggle.set_active(self.is_24hour)                          
        self.time_display_toggle.connect("toggled", self.__toggled, "time_display_toggle")
        self.time_display_toggle_align.add(self.time_display_toggle)
        self.__widget_pack_start(self.time_display_box, 
            [self.time_display_label, self.time_display_toggle_align])
        self.time_display_align.add(self.time_display_box)
        '''
        timezone
        '''
        self.timezone_title_align = self.__setup_title_align(
            app_theme.get_pixbuf("datetime/globe-green.png"), 
            _("TimeZone"), 
            TEXT_WINDOW_TOP_PADDING)
        self.timezone_combo_align = self.__setup_align(padding_top = 6)
        self.timezone_combo = ComboBox(self.timezone_items, max_width = 325)
        self.timezone_combo.set_select_index(self.__deepin_dt.get_gmtoff() + 11)
        self.timezone_combo_align.add(self.timezone_combo)

        self.__widget_pack_start(self.right_box, 
                                 [self.time_title_align, 
                                  self.cur_time_align, 
                                  self.datetime_widget_align, 
                                  self.auto_time_align, 
                                  self.time_display_align, 
                                  self.timezone_title_align, 
                                  self.timezone_combo_align])
        self.right_align.add(self.right_box)
       
        self.__widget_pack_start(self, [self.left_align, self.right_align])

        self.connect("expose-event", self.__expose)

        SecondThread(self).start()

    def set_cur_time_label(self):
        is_24hour = 24
        hour_value = time.localtime().tm_hour

        if not self.is_24hour: 
            is_24hour = 12
            if hour_value > 12:
                hour_value -= 12
        
        self.cur_time_label.set_text(                           
             _("Current Time: %s %02d:%02d:%02d (%d Hour)") %                
               (time.strftime('%p'),                                         
                hour_value,                                    
                time.localtime().tm_min,                                     
                time.localtime().tm_sec,                                     
                is_24hour))     
  
    def __on_day_selected(self, object, widget):
        pass

    def __on_change_date(self, widget, event):
        self.edit_date_align.set_padding(0, 0 , 195, 0)
        self.change_date_align.set_padding(0, 0, -100, 0)
        self.edit_date_align.set_child_visible(True)
        self.change_date_align.set_child_visible(False)
        self.calendar.clear_marks()

    def __hide_edit_date(self):
        self.edit_date_align.set_padding(0, 0, 110, 0)                          
        self.change_date_align.set_padding(0, 0, 0, 0)                          
        self.edit_date_align.set_child_visible(False)                           
        self.change_date_align.set_child_visible(True) 

    def __on_cancel_change_date(self, widget, event):
        self.__hide_edit_date()

    def __on_confirm_change_date(self, widget, event):
        self.__hide_edit_date()
        year, month, day = self.calendar.get_date()
        self.cur_date_label.set_text(_("Current Date: %d-%d-%d") % (year, month, day))
        self.calendar.mark_day(day)
        SetDateThread(self.__deepin_dt, day, month, year).start()

    def __setup_separator(self):                                                
        hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        hseparator.set_size_request(300, 10)                                    
        return hseparator                                                       
                                                                                
    def __setup_title_label(self,                                               
                            text="",                                            
                            text_color=app_theme.get_color("globalTitleForeground"),
                            text_size=TITLE_FONT_SIZE,                          
                            text_x_align=ALIGN_START,                           
                            label_width=180):                                   
        return Label(text = text,                                               
                     text_color = text_color,                                   
                     text_size = text_size,                                     
                     text_x_align = text_x_align,                               
                     label_width = label_width)     
    
    def __setup_title_align(self,                                                  
                            pixbuf,                                                
                            text,                                                  
                            padding_top=0,                         
                            padding_left=0):                
        align = self.__setup_align(padding_top = padding_top, padding_left = padding_left)            
        align_box = gtk.VBox(spacing = WIDGET_SPACING)                             
        title_box = gtk.HBox(spacing = WIDGET_SPACING)                             
        image = ImageBox(pixbuf)                                                   
        label = self.__setup_title_label(text)                                     
        separator = self.__setup_separator()                                       
        self.__widget_pack_start(title_box, [image, label])                        
        self.__widget_pack_start(align_box, [title_box, separator])                
        align.add(align_box)                                                    
        return align    
    
    def __toggled(self, widget, argv):
        if argv == "auto_time_toggle":
            is_auto_set_time = widget.get_active()
            self.datetime_settings.set_boolean("is-auto-set", is_auto_set_time)
            if is_auto_set_time:
                self.set_time_spin_align.set_child_visible(False)
                AutoSetTimeThread(self).start()
            else:
                self.set_time_spin_align.set_child_visible(True)
            return

        if argv == "time_display_toggle":
            self.is_24hour = widget.get_active()
            self.datetime_settings.set_boolean("is-24hour", self.is_24hour)
            self.datetime_widget.set_is_24hour(self.is_24hour)
            self.set_time_spin.set_24hour(self.is_24hour)

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

    def __setup_label(self, text="", width=90, align=ALIGN_START):
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
                      padding_top=0, 
                      padding_bottom=0, 
                      padding_left=0, 
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
