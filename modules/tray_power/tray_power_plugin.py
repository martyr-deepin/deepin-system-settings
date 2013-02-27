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
try:
    import deepin_gsettings
except ImportError:
    print "Please install deepin GSettings Python Binding!!"



class TrayPower(object):
    def __init__(self):
        self.power_set = deepin_gsettings.new("org.gnome.settings-daemon.plugins.power")
        self.power_set.connect("changed", self.power_set_changed)

    def power_set_changed(self, key):
        print "power_set_changed", key
        if key != "percentage":
            return False
        self.update_power_icon(self.power_settings.get_int("percentage"))

    def update_power_icon(self, percentage):
        self.tray_icon.set_tooltip_markup("电源还剩%s" % (percentage))
        if percentage >= 51 and percentage <= 100:
            self.tray_icon.set_icon_theme("battery100")
        elif percentage >= 21 and percentage <= 50:
            self.tray_icon.set_icon_theme("battery50")
        elif percentage >= 0 and percentage <= 20:
            self.tray_icon.set_icon_theme("battery20")

    def init_values(self, this_list):
        self.this = this_list[0]
        self.tray_icon = this_list[1]
        # visible icon pixbuf.
        xrandr_settings = deepin_gsettings.new("org.gnome.settings-daemon.plugins.xrandr")
        self.tray_icon.set_visible(xrandr_settings.get_boolean("is-laptop"))
        percentage = self.power_set.get_int("percentage")
        print "percentage......:", percentage
        self.update_power_icon(percentage)
        self.tray_icon.connect("enter-notify-event", self.tray_icon_enter_notify_event)
        self.tray_icon.connect("leave-notify-event", self.tray_icon_leave_notify_event)
        self.tray_icon.connect("button-press-event", self.tray_icon_button_press_event)

    def tray_icon_enter_notify_event(self, widget, event):
        print "tray_icon_enter_notify_event..."

    def tray_icon_leave_notify_event(self, widget, event):
        print "tray_icon_leave_notify_event..."

    def tray_icon_button_press_event(self, widget, event):
        print "tray_icon_button_press_event..."

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
