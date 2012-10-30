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

'''
There is no org.gnome.power-manager suspend or hibernate keys in gnome 3 any more, 
so could not using gsettings set/get dbus style.
I want to use /etc/acpi/* script way at first, if /var/run/acpid.socket is available to 
control acpid daemon, then removed script way.
'''
class PowerManager:
    '''
    enum
    '''
    nothing     = 0
    hibernate   = 1
    poweroff    = 2

    '''
    class docs
    '''
    def __init__(self):
        self.config = Config(os.path.join(get_parent_dir(__file__, 2), "src/config.ini"))
        self.config.load()

    def m_get_item(self, section, key, items=[]):
        i = 0
        
        if section == "power_button_config":
            for item, value in items:
                if self.config.get(section, key) == "nothing" and value == PowerManager.nothing:
                    return value
                if self.config.get(section, key) == "hibernate" and value == PowerManager.hibernate:
                    return value
                if self.config.get(section, key) == "poweroff" and value == PowerManager.poweroff:
                    return value

        if section == "power_save_config":
            for item, value in items:
                if self.config.get(section, key) == str(value):
                    return i
                i = i + 1

        return 0

    def m_set_value(self, section, key, value):
        if section == None or key == None or value == None:
            return

        if section == "power_button_config":
            if value == PowerManager.nothing:
                self.config.set(section, key, "nothing")
            elif value == PowerManager.hibernate:
                self.config.set(section, key, "hibernate")
            elif value == PowerManager.poweroff:
                self.config.set(section, key, "poweroff")
            else:
                pass
        else:
            self.config.set(section, key, value)
        self.config.write()

    def m_set_action_script(self, value):
        if value == PowerManager.nothing:
            os.system("sudo echo 'action=/etc/acpi/nothing.sh' >> /etc/acpi/events/default")
        elif value == PowerManager.hibernate:
            os.system("sudo echo 'action=/etc/acpi/hibernate.sh' >> /etc/acpi/events/default")
        elif value == PowerManager.poweroff:
            os.system("sudo echo 'action=/etc/acpi/poweroff.sh' >> /etc/acpi/events/default")
        else:
            os.system("sudo echo 'action=/etc/acpi/nothing.sh' >> /etc/acpi/events/default")
        os.system("sudo /etc/init.d/acpid restart")

    def get_press_power_button(self, items):
        return self.m_get_item("power_button_config", "press_power_button", items)

    def set_press_power_button(self, value):
        self.m_set_value("power_button_config", "press_power_button", value)
        os.system("sudo echo 'event=button/power' > /etc/acpi/events/default")
        self.m_set_action_script(value)

    def get_close_notebook_cover(self, items):
        return self.m_get_item("power_button_config", "close_notebook_cover", items)
    
    def set_close_notebook_cover(self, value):
        self.m_set_value("power_button_config", "close_notebook_cover", value)
        os.system("sudo echo 'event=button/lid' > /etc/acpi/events/default")
        self.m_set_action_script(value)

    def get_press_hibernate_button(self, items):
        return self.m_get_item("power_button_config", "press_hibernate_button", items)

    def set_press_hibernate_button(self, value):
        self.m_set_value("power_button_config", "press_hibernate_button", value)
        os.system("sudo echo 'event=button/hibernate' > /etc/acpi/events/default")
        self.m_set_action_script(value)

    def get_hibernate_status(self, items):
        return self.m_get_item("power_save_config", "hibernate_status", items)

    def set_hibernate_status(self, value):
        self.m_set_value("power_save_config", "hibernate_status", str(value))

    def get_close_harddisk(self, items):
        return self.m_get_item("power_save_config", "close_harddisk", items)

    def set_close_harddisk(self, value):
        self.m_set_value("power_save_config", "close_harddisk", str(value))

    def get_close_monitor(self, items):
        return self.m_get_item("power_save_config", "close_monitor", items)

    def set_close_monitor(self, value):
        self.m_set_value("power_save_config", "close_monitor", str(value))

    def get_wakeup_password(self):
        if self.config.get("other", "wakeup_password") == "False":
            return False
        return True

    def set_wakeup_password(self, value):
        self.m_set_value("other", "wakeup_password", str(value))

    def get_tray_battery_status(self):
        if self.config.get("other", "tray_battery_status") == "False":
            return False
        return True

    def set_tray_battery_status(self, value):
        self.m_set_value("other", "tray_battery_status", str(value))
