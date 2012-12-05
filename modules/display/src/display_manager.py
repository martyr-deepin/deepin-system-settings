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

try:
    from xrandr import xrandr
except ImportError:
    print "----------Please Install Python XRandR Binding----------"
    print "git clone git@github.com:linuxdeepin/deepin-xrandr.git"
    print "--------------------------------------------------------"

import re
import os
from dtk.ui.config import Config
from dtk.ui.utils import run_command, get_parent_dir

class DisplayManager:
    def __init__(self):
        self.__xrandr = xrandr
        '''
        By default it use the current screen
        '''
        self.__screen = self.__xrandr.get_current_screen()
        self.__config = Config(os.path.join(get_parent_dir(__file__, 2), "src/config.ini"))
        self.__config.load()

    def __del__(self):
        self.__xrandr = None
        self.__screen = None
        self.__config = None
    
    def get_output_names(self):
        return self.__screen.get_output_names()
    
    def get_screen_count(self):
        return self.__xrandr.get_screen_count()

    def get_current_screen(self):
        return self.__xrandr.get_current_screen()

    def set_current_screen(self, index):
        self.__screen = self.__xrandr.set_current_screen(index)
    
    def get_screen_sizes(self):
        return self.__screen.get_available_sizes()

    def get_screen_size(self):
        return self.__screen.get_size()
    
    def get_screen_size_index(self, items):
        i = 0
        width, height, width_mm, height_mm = self.get_screen_size()
        
        for item in items:
            match = re.search('(\d+) x (\d+)', item[0])
            if int(match.group(1)) == width and int(match.group(2)) == height:
                return i
            i += 1

        return 0
    
    def set_screen_size(self, size):
        match = re.search('(\d+) x (\d+)', size)
        output_names = self.get_output_names()
        i = 0
        
        while (i < len(output_names)):
            if self.__screen.get_output_by_name(output_names[i]).is_connected():
                run_command("xrandr --output %s --mode %sx%s" % (output_names[i], match.group(1), match.group(2)))
            i += 1

    def get_screen_rotation(self):
        return self.__screen.get_rotation()
    
    def get_screen_rotation_index(self, items):
        rotation = self.get_screen_rotation()
        i = 0

        while (i < len(items)):
            if items[i] == rotation:
                return i
            i += 1
        
        return 0
    
    def set_screen_rotation(self, rotation):
        run_command("xrandr -o %s" % (rotation))
    
    def get_screen_rots(self):
        return self.__screen.get_rotations()

    def get_screen_brightness(self):
        return float(self.__config.get("screen", "brightness")) * 100.0
    
    def set_screen_brightness(self, value):
        output_names = self.get_output_names()
        i = 0

        while (i < len(output_names)):
            if self.__screen.get_output_by_name(output_names[i]).is_connected():
                run_command("xrandr --output %s --brightness %f" % (output_names[i], value))
            i += 1

        self.__config.set("screen", "brightness", str(value))
        self.__config.write()
