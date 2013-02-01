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


from tray_time import TrayTime, TRAY_TIME_12_HOUR, TRAY_TIME_24_HOUR
from tray_time import TRAY_TIME_CN_TYPE, TRAY_TIME_EN_TYPE
from dtk.ui.utils import set_clickable_cursor
from deepin_utils.process import run_command
from dtk.ui.constant import ALIGN_END
from vtk.button import SelectButton
from dtk.ui.label import Label
from nls import _
import locale
import deepin_lunar
import dltk_calendar
import gtk

class TrayTimePlugin(object):
    def __init__(self):
        self.tray_time = TrayTime()
        self.tray_time.connect("send-time", self.tray_time_send)

    def tray_time_send(self, traytime, text, type, language_type):
        time_p = ""
        if type == TRAY_TIME_12_HOUR:
            time_p = text[0]
        hour = text[0 + type]
        min = text[1 + type]
        show_str = "%s %s:%s" % (time_p, hour, min)
        if language_type == TRAY_TIME_EN_TYPE:
            show_str = "%s:%s %s" % (hour, min, time_p)
        
        self.tray_icon.set_text(show_str)

    def init_values(self, this_list):
        self.this_list = this_list
        self.this = self.this_list[0]
        self.tray_icon = self.this_list[1]
        self.tray_icon.set_text("12:12:12")

    def run(self):
        return True
    
    def insert(self):
        return 0
        
    def id(self):
        return "tray-time-plugin-hailongqiu"

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

    def __on_day_selected(self, widget, event):
        self.this.hide_menu()                                                   
        run_command("deepin-system-settings date_time")        

    def plugin_widget(self):
        align = self.__setup_align()
        box = gtk.VBox(spacing = 5)
        calendar_align = self.__setup_align()
        calendar = deepin_lunar.new()
        self.calendar = deepin_lunar.new()                                      
        if len(locale.getdefaultlocale()):                                      
            if locale.getdefaultlocale()[0].find("zh_") != 0:                   
                self.calendar = dltk_calendar.new()                             
        else:                                                                   
            self.calendar = dltk_calendar.new()
        calendar.set_day_padding(0)
        calendar.get_handle().set_property("show-details", False)
        calendar.get_handle().set_size_request(200, 172)
        calendar_align.add(calendar.get_handle())
        select_align = self.__setup_align()
        select_button = SelectButton(_("Change DateTime settings"), 
                                     font_size = 10, 
                                     ali_padding = 5)
        select_button.set_size_request(200, 25)
        select_align.add(select_button)
        select_button.connect("button-press-event", self.__on_day_selected)
        box.pack_start(calendar_align, False, False)
        box.pack_start(select_align, False, False)
        align.add(box)
        return align

    def show_menu(self):
        self.this.set_size_request(200, 233)
        print "menu show...."

    def hide_menu(self):
        print "menu hide....."



def return_plugin():
    return TrayTimePlugin


