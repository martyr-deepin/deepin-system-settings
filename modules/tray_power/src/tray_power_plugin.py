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
from tray_power_gui import PowerGui
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
        self.gui = PowerGui()
        self.gui.click_btn.connect("clicked", self.click_btn_clicked_event)
        #
        self.error = False
        try:
            self.__init_dbus_inter()
        except Exception, e:
            print "traypower[error]:", e
            self.error = True
        self.power_set = deepin_gsettings.new(POWER_SETTING_GSET)
        self.power_set.connect("changed", self.power_set_changed)

    def click_btn_clicked_event(self, widget):
        self.this.hide_menu()
        run_command(RUN_COMMAND) 

    def __init_dbus_inter(self):
        session_bus = dbus.SystemBus()
        power_obj = session_bus.get_object(ORG_UPOWER_NAME, ORG_UPOWER_PATH)
        power_inter = dbus.Interface(power_obj, dbus_interface=ORG_UPOWER_INTERFACES)
        acpi_path = power_inter.EnumerateDevices()
        acpi_obj = session_bus.get_object(ORG_UPOWER_NAME, acpi_path[0])
        self.acpi_inter = dbus.Interface(acpi_obj, dbus_interface=ORG_DBUS_PROPER)

    def power_set_changed(self, key):
        if not self.error:
            self.online_value = self.acpi_inter.Get(ORG_UPOWER_DEVICE, "Online")
        if key not in  ["percentage", "show-tray"]: 
            return 
        #
        value = self.power_set.get_double("percentage")
        self.update_power_icon(int(value))
        self.visible_power_tray()
        self.modify_battery_icon(self.online_value, value)

    def visible_power_tray(self):
        show_value = self.power_set.get_boolean("show-tray")
        if show_value:
            self.tray_icon.set_no_show_all(False)
            self.tray_icon.show_all()
        else:
            self.tray_icon.set_no_show_all(True)
            self.tray_icon.hide()

    def modify_battery_icon(self, online_value, value):
        if online_value:
            self.tray_icon.set_tooltip_text(_("charging"))
            self.tray_icon.set_icon_theme("tray_battery")

    def update_power_icon(self, percentage):
        if percentage >= 91 and percentage <= 100:
            self.tray_icon.set_icon_theme("battery91-100")
        elif percentage >= 81 and percentage <= 90:
            self.tray_icon.set_icon_theme("battery81-90")
        elif percentage >= 71 and percentage <= 80:
            self.tray_icon.set_icon_theme("battery71-80")
        elif percentage >= 61 and percentage <= 70:
            self.tray_icon.set_icon_theme("battery61-70")
        elif percentage >= 51 and percentage <= 60:
            self.tray_icon.set_icon_theme("battery51-60")
        elif percentage >= 31 and percentage <= 50:
            self.tray_icon.set_icon_theme("battery31-50")
        elif percentage >= 21 and percentage <= 30:
            self.tray_icon.set_icon_theme("battery21-30")
        elif percentage >= 0 and percentage <= 20:
            self.tray_icon.set_icon_theme("battery0-10-20")
        #
        string = _("%s remaining") % (str(int(percentage)) + '%')
        if int(percentage) == 100:
            string = _("fully charged")

        self.tray_icon.set_tooltip_text(string)

    def init_values(self, this_list):
        self.this = this_list[0]
        self.tray_icon = this_list[1]
        # visible icon pixbuf.
        xrandr_settings = deepin_gsettings.new(XRANDR_SETTINGS_GSET)
        visible_check = xrandr_settings.get_boolean("is-laptop")
        #self.tray_icon.set_visible(visible_check)
        self.visible_power_tray()
        if visible_check:
            # get power value.
            percentage = self.power_set.get_double("percentage")
            self.update_power_icon(percentage)
            self.online_value = self.acpi_inter.Get(ORG_UPOWER_DEVICE, "Online")
            self.modify_battery_icon(self.online_value, percentage)
            # init tray_icon events.
        else:
            self.tray_icon.set_icon_theme("computer_d")

    def id(slef):
        return "deepin-tray-power-hailongqiu"

    def run(self):
        return True

    def insert(self):
        return 3

    def plugin_widget(self):
        return self.gui

    def show_menu(self):
        self.this.set_size_request(175, 172)

    def hide_menu(self):
        pass

def return_insert():
    return 5
    
def return_id():
    return "power"

def return_plugin():
    return TrayPower

