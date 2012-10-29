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

import os
from dtk.ui.utils import get_parent_dir
from dtk.ui.config import Config

class PowerManager():
    '''
    class docs
    '''
    def __init__(self):
        self.config = Config(os.path.join(get_parent_dir(__file__, 2), "src/config.ini"))
        self.config.load()

    def m_get_item(self, section, key, items=[]):
        for item, i in items:
            if item == self.config.get(section, key):
                return i

        return 0

    def m_set_value(self, section, key, value):
        if section == None or key == None or value == None:
            return
        self.config.set(section, key, value)

    def get_press_power_button(self, items):
        return self.m_get_item("press_button_config", "press_power_button", items)

    def get_close_notebook_cover(self, items):
        return self.m_get_item("press_button_config", "close_notebook_cover", items)
