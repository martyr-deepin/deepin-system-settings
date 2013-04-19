#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
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

try:
    import deepin_gsettings
except ImportError:
    print "----------Please Install Deepin GSettings Python Binding----------"
    print "git clone git@github.com:linuxdeepin/deepin-gsettings.git"
    print "------------------------------------------------------------------"
import os
from xml.dom import minidom

class PowerManager:
    '''
    enum
    '''
    nothing     = 0
    hibernate   = 3
    shutdown    = 2
    suspend     = 1

    default = 0
    saving = 1
    high_performance = 2
    customized = 3

    BIG_NUM = 0

    '''
    class docs
    '''
    def __init__(self):
        self.power_settings = deepin_gsettings.new("org.gnome.settings-daemon.plugins.power")
        self.lockdown_settings = deepin_gsettings.new("org.gnome.desktop.screensaver")
        self.session_settings = deepin_gsettings.new("org.gnome.desktop.session")

        self.__powers_xml_filename = "%s/.config/powers.xml" % os.path.expanduser('~')
        self.__xmldoc = minidom.parse(self.__powers_xml_filename)

        self.powers_plan = []

        self.init_xml()

    def init_xml(self):
        self.__xmldoc = minidom.parse(self.__powers_xml_filename)
        if self.__xmldoc != None:
            plans = self.__xmldoc.getElementsByTagName("plan")
            for plan in plans:
                plan_name = plan.attributes["name"].value
                close_monitor = plan.getElementsByTagName("close-monitor")
                suspend = plan.getElementsByTagName("suspend")
                '''
                powers_plan {
                    plan_name, 
                    close_monitor, 
                    suspend
                }
                '''
                self.powers_plan.append(
                    (plan_name, 
                     int(self.__getText(close_monitor[0].childNodes)), 
                     int(self.__getText(suspend[0].childNodes))))

    def get_plan_info(self, plan):
        if plan < 0 or plan >= len(self.powers_plan):
            return None

        return self.powers_plan[plan]

    def __getText(self, nodelist):                                                 
        rc = []                                                                    
        for node in nodelist:                                                      
            if node.nodeType == node.TEXT_NODE:                                    
                rc.append(node.data)                                               
        return ''.join(rc)

    def __get_item_value(self, items, ori_value):
        for item, value in items:
            if ori_value == "nothing" and value == PowerManager.nothing:
                return value
            if ori_value == "hibernate" and value == PowerManager.hibernate:
                return value
            if ori_value == "interactive" and value == PowerManager.shutdown:
                return value
            if ori_value == "shutdown" and value == PowerManager.shutdown:
                return value
            if ori_value == "suspend" and value == PowerManager.suspend:      
                return value  

        return 0
    
    def __set_item_value(self, key, value):
        if value == 0:
            self.power_settings.set_string(key, "nothing")
        elif value == 3:
            self.power_settings.set_string(key, "hibernate")
        elif value == 2:
            self.power_settings.set_string(key, "shutdown")
        elif value == 1:
            self.power_settings.set_string(key, "suspend")
   
    def reset(self):
        self.power_settings.reset("button-power")
        self.power_settings.reset("lid-close-battery-action")
        self.power_settings.reset("button-hibernate")
        # 节能模式  
        self.power_settings.reset("sleep-inactive-battery-timeout")       
        self.power_settings.reset("sleep-inactive-ac-timeout")
        self.power_settings.reset("sleep-display-battery")             
        self.power_settings.reset("sleep-display-ac") 
    
    def get_press_button_power(self, items):
        return self.__get_item_value(items, self.power_settings.get_string("button-power"))
    
    def set_press_button_power(self, value):
        self.__set_item_value("button-power", value)

    def get_close_notebook_cover(self, items):
        return self.__get_item_value(items, self.power_settings.get_string("lid-close-battery-action"))
    
    def set_close_notebook_cover(self, value):
        self.__set_item_value("lid-close-battery-action", value)
        self.__set_item_value("lid-close-ac-action", value)

    def get_press_button_hibernate(self, items):
        return self.__get_item_value(items, self.power_settings.get_string("button-hibernate"))
    
    def set_press_button_hibernate(self, value):
        self.__set_item_value("button-hibernate", value)

    def get_current_plan(self):
        current_plan = self.power_settings.get_string("current-plan")
        if current_plan == "default":
            return 0
        elif current_plan == "saving":
            return 1
        elif current_plan == "high_performance":
            return 2
        else:
            return 3
   
    def set_current_plan(self, value):
        current_plan = "default"
        if value == 0:
            current_plan = "default"
        elif value == 1:
            current_plan = "saving"
        elif value == 2:
            current_plan = "high_performance"
        else:
            current_plan = "customized"
        
        self.power_settings.set_string("current-plan", current_plan)

    def get_suspend_from_xml(self, items, plan):
        i = 0

        for item, value in items:
            if value == plan:
                return i
            i += 1

        return 0
    
    def get_suspend_status(self, items):
        suspend_status_value = self.power_settings.get_int("sleep-inactive-battery-timeout")
        i = 0

        for item, value in items:
            if value == suspend_status_value:
                return i
            i += 1

        return 0

    def set_suspend_status(self, value):
        self.power_settings.set_string("sleep-inactive-battery-type", "suspend")
        self.power_settings.set_int("sleep-inactive-battery-timeout", value)
        self.power_settings.set_string("sleep-inactive-ac-type", "suspend")
        self.power_settings.set_int("sleep-inactive-ac-timeout", value)

    def get_close_harddisk(self, items):
        return 0

    def set_close_harddisk(self, value):
        pass

    def get_close_monitor(self, items):
        close_monitor_value = self.power_settings.get_int("sleep-display-battery")
        i = 0

        for item, value in items:
            if value == close_monitor_value:
                return i
            i += 1

        return 0

    def get_close_monitor_from_xml(self, items, plan):
        i = 0

        for item, value in items:
            if value == plan:
                return i
            i += 1

        return 0

    def set_close_monitor(self, value):
        self.power_settings.set_int("sleep-display-battery", value)
        self.power_settings.set_int("sleep-display-ac", value)
        self.session_settings.set_uint("idle-delay", self.BIG_NUM)

    def get_wakeup_password(self):
        return self.lockdown_settings.get_boolean("lock-enabled")

    def set_wakeup_password(self, value):
        pass

    def get_tray_battery_status(self):
        return self.power_settings.get_boolean("show-tray")

    def set_tray_battery_status(self, value):
        self.power_settings.set_boolean("show-tray", value)
