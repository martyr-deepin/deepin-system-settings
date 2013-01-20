#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Deepin, Inc.
#               2012 Hailong Qiu
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



DBUS_CONSOLEKIT = 'org.freedesktop.ConsoleKit'
DBUS_CONSOLEKIT_MANAGER = '/org/freedesktop/ConsoleKit/Manager'
DBUS_POINT_MANAGER = 'org.freedesktop.ConsoleKit.Manager'

DBUS_UPOWER = "org.freedesktop.UPower"
DBUS_UPOWER_U = "/org/freedesktop/UPower"
DBUS_POINT_UPOWER = "org.freedesktop.UPower"


class CmdDbus(object):
    def __init__(self):
        self.__session_bus = dbus.SystemBus()
        # restart stop.
        oper_obj = self.__create_obj(DBUS_CONSOLEKIT, DBUS_CONSOLEKIT_MANAGER)
        self.restart = self.__get_method(oper_obj, "Restart", DBUS_POINT_MANAGER)
        self.stop    = self.__get_method(oper_obj, "Stop", DBUS_POINT_MANAGER)
        # suspend.
        oper_obj = self.__create_obj(DBUS_UPOWER, DBUS_UPOWER_U)
        self.suspend = self.__get_method(oper_obj, "Suspend", DBUS_UPOWER)

    def __create_obj(self, dbus_, dbus__):
        return self.__session_bus.get_object(dbus_, dbus__)

    def __get_method(self, obj, name, dbus__):
        return obj.get_dbus_method(name, dbus__)

if __name__ == "__main__":
    cmd_dbus = CmdDbus()
    print cmd_dbus.suspend
    print cmd_dbus.stop
    print cmd_dbus.restart()
    
