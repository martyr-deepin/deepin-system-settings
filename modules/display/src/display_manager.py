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

from xrandr import xrandr
import re
from dtk.ui.utils import run_command

class DisplayManager:
    def __init__(self):
        self.__xrandr = xrandr
        '''
        By default it is the current screen
        '''
        self.__screen = self.__xrandr.get_current_screen()

    def __del__(self):
        self.__xrandr = None
    
    def get_output_names(self):
        return self.__screen.get_output_names()
    
    def get_screen_count(self):
        return self.__xrandr.get_screen_count()

    def get_current_screen(self):
        return self.__xrandr.get_current_screen()

    def set_current_screen(self, index):
        self.__screen = self.__xrandr.set_current_screen(index)
    
    '''
    TODO: it need to support several screens such as 0, 1, ... n
    '''
    def get_screen_sizes(self):
        return self.__screen.get_available_sizes()

    def set_screen_size(self, size):
        match = re.search('(\d+) x (\d+)', size)
        output_names = self.get_output_names()
        i = 0
        
        '''
        FIXME: HOWTO set other outputs?
        while (i < len(output_names)):
            run_command("xrandr --output %s --mode %sx%s" % (output_names[i], match.group(1), match.group(2)))
        '''
        
        run_command("xrandr --output LVDS --mode %sx%s" % (match.group(1), match.group(2)))

    def set_screen_rotation(self, rotation):
        run_command("xrandr -o %s" % (rotation))
    
    def get_screen_rots(self):
        return self.__screen.get_rotations()
