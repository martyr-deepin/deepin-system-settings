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

class DisplayManager:
    def __init__(self):
        self.__xrandr = xrandr
        '''
        By default it is the current screen
        '''
        self.__screen = self.__xrandr.get_current_screen()

    def __del__(self):
        self.__xrandr = None
    
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