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

import deepin_gsettings

class PowerManager:
    '''
    enum
    '''
    nothing     = 0
    hibernate   = 1
    shutdown    = 2

    '''
    class docs
    '''
    def __init__(self):
        self.power_settings = deepin_gsettings.new("org.gnome.settings-daemon.plugins.power")
        self.lockdown_settings = deepin_gsettings.new("org.gnome.desktop.lockdown")

    def __get_item_value(self, items, ori_value):
        for item, value in items:
            if ori_value == "nothing" and value == PowerManager.nothing:
                return value
            if ori_value == "hibernate" and value == PowerManager.hibernate:
                return value
            if ori_value == "shutdown" and value == PowerManager.shutdown:
                return value

        return 0
    
    def __set_item_value(self, key, value):
        if value == 0:
            self.power_settings.set_string(key, "nothing")
        elif value == 1:
            self.power_settings.set_string(key, "hibernate")
        elif value == 2:
            self.power_settings.set_string(key, "shutdown")
    
    def get_press_button_power(self, items):
        return self.__get_item_value(items, self.power_settings.get_string("button-power"))
    
    def set_press_button_power(self, value):
        self.__set_item_value("button-power", value)

    def get_close_notebook_cover(self, items):
        '''
        TODO: I use notebook so consider battery first :)
        '''
        return self.__get_item_value(items, self.power_settings.get_string("lid-close-battery-action"))
    
    def set_close_notebook_cover(self, value):
        self.__set_item_value("lid-close-battery-action", value)
        self.__set_item_value("lid-close-ac-action", value)

    def get_press_button_hibernate(self, items):
        return self.__get_item_value(items, self.power_settings.get_string("button-hibernate"))
    
    def set_press_button_hibernate(self, value):
        self.__set_item_value("button-hibernate", value)

    '''
    TODO: idle-dim-item unit is minute
    '''
    def get_hibernate_status(self, items):
        hibernate_status_value = self.power_settings.get_int("idle-dim-time")
        i = 0

        for item, value in items:
            if value == hibernate_status_value:
                return i
            i += 1

        return 0

    def set_hibernate_status(self, value):
        self.power_settings.set_int("idle-dim-time", value)

    def get_close_harddisk(self, items):
        return 0

    def set_close_harddisk(self, value):
        pass

    '''
    TODO: unit is second
    '''
    def get_close_monitor(self, items):
        close_monitor_value = self.power_settings.get_int("sleep-display-battery") / 60
        i = 0

        for item, value in items:
            if value == close_monitor_value:
                return i
            i += 1

        return 0

    def set_close_monitor(self, value):
        self.power_settings.set_int("sleep-display-battery", value * 60)
        self.power_settings.set_int("sleep-display-ac", value * 60)

    def get_wakeup_password(self):
        return self.lockdown_settings.get_boolean("disable-lock-screen")

    def set_wakeup_password(self, value):
        self.lockdown_settings.set_boolean("disable-lock-screen", value)

    def get_tray_battery_status(self):
        return True

    def set_tray_battery_status(self, value):
        pass
