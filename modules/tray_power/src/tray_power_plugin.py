#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Deepin, Inc.
#               2013 Hailong Qiu
#
# Author:     Hailong Qiu <356752238@qq.com>
# Maintainer: Hailong Qiu <356752238@qq.com>
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

import gtk
import dbus
from nls import _
from deepin_utils.process import run_command
from vtk.timer import Timer
try:
    import deepin_gsettings
except ImportError:
    print "Please install deepin GSettings Python Binding!!"


POWER_SETTING_GSET = "org.gnome.settings-daemon.plugins.power"
XRANDR_SETTINGS_GSET = "org.gnome.settings-daemon.plugins.xrandr"
RUN_COMMAND = "deepin-system-settings power"

# dbus string values.
ORG_UPOWER_NAME = "org.freedesktop.UPower"
ORG_UPOWER_PATH = "/org/freedesktop/UPower"
ORG_UPOWER_INTERFACES = "org.freedesktop.UPower"
ORG_DBUS_PROPER = "org.freedesktop.DBus.Properties"
ORG_UPOWER_DEVICE = "org.freedesktop.Upower.Device"

class TrayPower(object):
    def __init__(self):
        self.__init_dbus_inter()
        self.timer = Timer(100)
        self.timer.connect("Tick", self.timer_double_tick_event)
        self.double_check = False
        self.timer_check = False
        self.power_set = deepin_gsettings.new(POWER_SETTING_GSET)
        self.power_set.connect("changed", self.power_set_changed)

    def __init_dbus_inter(self):
        session_bus = dbus.SystemBus()
        power_obj = session_bus.get_object(ORG_UPOWER_NAME, ORG_UPOWER_PATH)
        power_inter = dbus.Interface(power_obj, dbus_interface=ORG_UPOWER_INTERFACES)
        acpi_path = power_inter.EnumerateDevices()
        acpi_obj = session_bus.get_object(ORG_UPOWER_NAME, acpi_path[0])
        self.acpi_inter = dbus.Interface(acpi_obj, dbus_interface=ORG_DBUS_PROPER)

    def power_set_changed(self, key):
        self.online_value = self.acpi_inter.Get(ORG_UPOWER_DEVICE, "Online")
        if key != "percentage": 
            return 
        #
        value = self.power_set.get_double("percentage")
        self.update_power_icon(int(value))
        self.modify_battery_icon(self.online_value, value)

    def modify_battery_icon(self, online_value, value):
        if online_value and value != 100:
            self.tray_icon.set_tooltip_text(_("battery charging"))
            self.tray_icon.set_icon_theme("tray_battery")

    def update_power_icon(self, percentage):
        if percentage >= 90 and percentage <= 100:
            self.tray_icon.set_icon_theme("battery100")
        elif percentage >= 21 and percentage <= 98:
            self.tray_icon.set_icon_theme("battery50")
        elif percentage >= 0 and percentage <= 20:
            self.tray_icon.set_icon_theme("battery20")
        #
        self.tray_icon.set_tooltip_text(_("Power supply surplus") + str(int(percentage)))

    def init_values(self, this_list):
        self.this = this_list[0]
        self.tray_icon = this_list[1]
        # visible icon pixbuf.
        xrandr_settings = deepin_gsettings.new(XRANDR_SETTINGS_GSET)
        visible_check = xrandr_settings.get_boolean("is-laptop")
        self.tray_icon.set_visible(visible_check)
        if visible_check:
            # get power value.
            percentage = self.power_set.get_double("percentage")
            self.update_power_icon(percentage)
            self.online_value = self.acpi_inter.Get(ORG_UPOWER_DEVICE, "Online")
            self.modify_battery_icon(self.online_value, percentage)
            # init tray_icon events.
            self.tray_icon.connect("button-press-event", self.tray_icon_button_press_event)

    def tray_icon_button_press_event(self, widget, event):
        if event.button == 1:
            if not self.timer_check:
                self.timer_check = True
            # run command.
            if self.double_check and self.timer.Enabled and self.timer_check:
                run_command(RUN_COMMAND)
            #
            self.double_check = True
            self.timer.Enabled = True

    def timer_double_tick_event(self, tick):
        self.double_check = False
        self.timer_check = False
        tick.Enabled = False

    def id(slef):
        return "deepin-tray-power-hailongqiu"

    def run(self):
        return True

    def insert(self):
        return 3

    def plugin_widget(self):
        return None

    def show_menu(self):
        pass

    def hide_menu(self):
        pass

def return_plugin():
    return TrayPower
