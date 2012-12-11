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

try:
    import deepin_xrandr
except ImportError:
    print "----------Please Install Deepin XRandR Python Binding----------"
    print "git clone git@github.com:linuxdeepin/deepin-xrandr.git"
    print "---------------------------------------------------------------"

try:
    import deepin_gsettings
except ImportError:
    print "----------Please Install Deepin GSettings Python Binding----------"
    print "git clone git@github.com:linuxdeepin/deepin-gsettings.git"
    print "------------------------------------------------------------------"

import re
import os
from dtk.ui.utils import run_command

class DisplayManager:
    def __init__(self):
        self.__deepin_xrandr = deepin_xrandr.new()
        self.__xrandr_settings = deepin_gsettings.new("org.gnome.settings-daemon.plugins.xrandr")
        self.__power_settings = deepin_gsettings.new("org.gnome.settings-daemon.plugins.power")
        self.__session_settings = deepin_gsettings.new("org.gnome.desktop.session")

    def __del__(self):
        self.__deepin_xrandr.delete()
        self.__deepin_xrandr = None
        self.__xrandr_settings.delete()
        self.__xrandr_settings = None
        self.__power_settings.delete()
        self.__power_settings = None
        self.__session_settings.delete()
        self.__session_settings = None
    
    def get_output_names(self):
        output_names = self.__xrandr_settings.get_strv("output-names")
        ret_output_names = []
        i = 0

        while i < len(output_names):
            '''
            TODO: NULL means disconnected
            '''
            if output_names[i] != "NULL":
                ret_output_names.append(output_names[i])

            i += 1
 
        return ret_output_names

    def get_screen_sizes(self, output_name):
        return self.__deepin_xrandr.get_screen_sizes(output_name)

    def get_screen_size(self):
        return self.__xrandr_settings.get_string("screen-size")

    def get_screen_size_index(self, items):
        screen_size = self.get_screen_size()
        i = 0
        
        for item in items:
            if item[0] == screen_size:
                return i
            i += 1

        return 0
    
    def set_screen_size(self, output_name, size):
        self.__xrandr_settings.set_string("screen-size", size)
        run_command("xrandr --output %s --mode %s" % (output_name, size))

    def get_screen_rotation(self):
        return self.__xrandr_settings.get_string("screen-rotation")

    def get_screen_rotation_index(self):
        rotation = self.get_screen_rotation()

        if rotation == "normal":
            return 0
        if rotation == "right":
            return 1
        if rotation == "left":
            return 2
        if rotation == "inverted":
            return 3
        
        return 0
    
    def set_screen_rotation(self, rotation):
        rotation_str = "normal"

        if rotation == 1:
            rotation_str = "normal"
        elif rotation == 2:
            rotation_str = "right"
        elif rotation == 3:
            rotation_str = "left"
        elif rotation == 4:
            rotation_str = "inverted"

        self.__xrandr_settings.set_string("screen-rotation", rotation_str)

    def get_screen_brightness(self):
        return self.__xrandr_settings.get_double("brightness") * 100.0
    
    def set_screen_brightness(self, value):
        self.__xrandr_settings.set_double("brightness", value)

    '''
    TODO: unit is second
    '''
    def get_close_monitor(self):
        '''
        TODO: I use notebook so consider battery at first :)
        '''
        return self.__power_settings.get_int("sleep-display-battery")

    def __get_duration_index(self, value, items):
        i = 0

        for item in items:
            if item[1] == value:
                return i

            i += 1

        return 0
    
    def get_close_monitor_index(self, items):
        return self.__get_duration_index(self.get_close_monitor() / 60, items)

    def set_close_monitor(self, value):
        self.__power_settings.set_int("sleep-display-battery", value * 60)
        self.__power_settings.set_int("sleep-display-ac", value * 60)

    '''
    TODO: unit is second
    '''
    def get_lock_display(self):
        return self.__session_settings.get_uint("idle-delay")

    def get_lock_display_index(self, items):
        return self.__get_duration_index(self.get_lock_display() / 60, items)

    def set_lock_display(self, value):
        self.__session_settings.set_uint("idle-delay", value * 60)
