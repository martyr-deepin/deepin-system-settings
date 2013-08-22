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

import dbus
import dbus.mainloop.glib
from nls import _
from tray_power_gui import PowerGui
from dtk.ui.dbus_notify import DbusNotify
from deepin_utils.process import run_command
try:
    import deepin_gsettings
except ImportError:
    print "Please install deepin GSettings Python Binding!!"


POWER_SETTING_GSET = "org.gnome.settings-daemon.plugins.power"
RUN_COMMAND = "deepin-system-settings power"

# dbus string values.
ORG_UPOWER_NAME = "org.freedesktop.UPower"
ORG_UPOWER_PATH = "/org/freedesktop/UPower"
ORG_UPOWER_INTERFACES = "org.freedesktop.UPower"
ORG_DBUS_PROPER = "org.freedesktop.DBus.Properties"
ORG_UPOWER_DEVICE = "org.freedesktop.Upower.Device"

class TrayPower(object):
    def __init__(self):
        super(TrayPower, self).__init__()
        self.power_set = deepin_gsettings.new(POWER_SETTING_GSET)
        self.gui = PowerGui(self.power_set)
        self.gui.click_btn.connect("clicked", self.click_btn_clicked_event)
        try:
            self.__init_dbus_inter()
        except Exception, e:
            print "traypower[error]:", e
            self.power_inter = None
            self.power_proper = None
        self.power_set.connect("changed", self.power_set_changed)
        self.__get_current_plan()

    def click_btn_clicked_event(self, widget):
        self.this.hide_menu()
        run_command(RUN_COMMAND) 

    def __init_dbus_inter(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.sys_bus = dbus.SystemBus()
        power_obj = self.sys_bus.get_object(ORG_UPOWER_NAME, ORG_UPOWER_PATH)
        self.power_inter = dbus.Interface(power_obj, dbus_interface=ORG_UPOWER_INTERFACES)
        self.power_proper = dbus.Interface(power_obj, dbus_interface=ORG_DBUS_PROPER)
        self.sys_bus.add_signal_receiver(self.__power_dbus_changed, signal_name="Changed",
                                         dbus_interface=ORG_UPOWER_INTERFACES, path=ORG_UPOWER_PATH)
        self.sys_bus.add_signal_receiver(self.__power_dbus_device_changed, signal_name="DeviceAdded",
                                         dbus_interface=ORG_UPOWER_INTERFACES, path=ORG_UPOWER_PATH)
        self.sys_bus.add_signal_receiver(self.__power_dbus_device_changed, signal_name="DeviceChanged",
                                         dbus_interface=ORG_UPOWER_INTERFACES, path=ORG_UPOWER_PATH)
        self.sys_bus.add_signal_receiver(self.__power_dbus_device_changed, signal_name="DeviceRemoved",
                                         dbus_interface=ORG_UPOWER_INTERFACES, path=ORG_UPOWER_PATH)

    def __power_dbus_changed(self):
        self.online_value = self.get_line_power()
        value = self.power_set.get_double("percentage")
        self.update_power_icon(int(value))
        self.modify_battery_icon(value)

    def __power_dbus_device_changed(self, dev_path):
        self.has_battery = self.get_has_battery()
        value = self.power_set.get_double("percentage")
        self.update_power_icon(int(value))
        self.modify_battery_icon(value)
    
    @property
    def percentage_low_threshhold(self):
        return 20
        
    @property
    def percentage_low(self):
        return self.power_set.get_int("percentage-low")
    
    @property
    def percentage_low_critical(self):
        return self.power_set.get_int("percentage-critical")
        
    def get_has_battery(self):
        ''' whether power has battery '''
        try:
            devices = self.power_inter.EnumerateDevices()
            for dev in devices:
                dev_obj = self.sys_bus.get_object(ORG_UPOWER_NAME, dev)
                dev_inter = dbus.Interface(dev_obj, dbus_interface=ORG_DBUS_PROPER)
                if dev_inter.Get(ORG_UPOWER_DEVICE, "Type") == 2:
                    return True
            return False
        except:
            return False

    def get_line_power(self):
        ''' Whether power is currently being provided through line power '''
        try:
            return not self.power_proper.Get(ORG_UPOWER_INTERFACES, "OnBattery")
        except:
            return False

    def __get_current_plan(self):
        current_plan = self.power_set.get_string("current-plan")            
        if current_plan == "balance":                                       
            self.gui.set_mode_bit(self.gui.one_mode_btn)                    
        elif current_plan == "saving":                                      
            self.gui.set_mode_bit(self.gui.two_mode_btn)                    
        elif current_plan == "high-performance":                            
            self.gui.set_mode_bit(self.gui.tree_mode_btn)                  
        elif current_plan == "customized":                                  
            self.gui.set_mode_bit(self.gui.customized_mode_btn)             
        else:                                                               
            pass                                                            

    def power_set_changed(self, key):
        if key == "show-tray":
            self.visible_power_tray()
            return

        if key == "percentage":
            value = self.power_set.get_double("percentage")
            self.update_power_icon(int(value))
            self.modify_battery_icon(value)
            return

        if key == "current-plan":
            self.__get_current_plan()

    def visible_power_tray(self):
        show_value = self.power_set.get_boolean("show-tray")
        if show_value:
            self.tray_icon.set_no_show_all(False)
            self.tray_icon.show_all()
        else:
            self.tray_icon.set_no_show_all(True)
            self.tray_icon.hide()

    def modify_battery_icon(self, value):
        if not self.online_value:
            return
        if self.has_battery:
            self.tray_icon.set_icon_theme("tray_battery")
            if value >= 99.8:
                self.tray_icon.set_tooltip_text(_("Fully charged"))
            else:
                self.tray_icon.set_tooltip_text(
                        _("Charging, %s remaining") % (str(int(value)) + '%'))
        else:
            self.tray_icon.set_icon_theme("computer_d")
            self.tray_icon.set_tooltip_text("")

    def update_power_icon(self, percentage):
        if self.online_value:
            return
        self.check_for_warning(percentage)
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
            string = _("Fully charged")

        self.tray_icon.set_tooltip_text(string)
        
    def check_for_warning(self, percentage):
        if percentage == self.percentage_low_threshhold or percentage == self.percentage_low or percentage == self.percentage_low_critical:
            ntf = DbusNotify("deepin-system-settings", "/usr/share/icons/Deepin/apps/48/preferences-power.png")
            ntf.set_summary(_("Low power(%s%%)" % percentage))
            ntf.set_body(_("Your battery is running low, please charge!"))
            ntf.notify()


    def init_values(self, this_list):
        self.this = this_list[0]
        self.tray_icon = this_list[1]
        # visible icon pixbuf.
        self.has_battery = self.get_has_battery()
        self.online_value = self.get_line_power()
        self.visible_power_tray()
        if self.has_battery:
            # get power value.
            percentage = self.power_set.get_double("percentage")
            self.update_power_icon(percentage)
            self.modify_battery_icon(percentage)
            # init tray_icon events.
        else:
            self.tray_icon.set_icon_theme("computer_d")

    def id(self):
        return "deepin-tray-power-hailongqiu"

    def run(self):
        return True

    def insert(self):
        return 3

    def plugin_widget(self):
        return self.gui

    def show_menu(self):
        self.this.set_size_request(175, 200)

    def hide_menu(self):
        pass

def return_insert():
    return 5
    
def return_id():
    return "power"

def return_plugin():
    return TrayPower
