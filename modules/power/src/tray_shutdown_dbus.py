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



DBUS_GNOME_SESSION = "org.gnome.SessionManager"
DBUS_GNOME_SESSION_MANAGER = "/org/gnome/SessionManager"
DBUS_GNOME_SESSION_POINT   = "org.gnome.SessionManager"

DBUS_CONSOLEKIT = 'org.freedesktop.ConsoleKit'
DBUS_CONSOLEKIT_MANAGER = '/org/freedesktop/ConsoleKit/Manager'
DBUS_POINT_MANAGER = 'org.freedesktop.ConsoleKit.Manager'

DBUS_UPOWER = "org.freedesktop.UPower"
DBUS_UPOWER_U = "/org/freedesktop/UPower"
DBUS_POINT_UPOWER = "org.freedesktop.UPower"

DBUS_ACCOUNTS = "org.freedesktop.Accounts"
DBUS_ACCOUNTS_USER_1000 = "/org/freedesktop/Accounts/User1000"
DBUS_ACCOUNTS_PROPERTIES = "org.freedesktop.DBus.Properties"
DBUS_ACCOUNTS_USER = "org.freedesktop.Accounts.User"



class CmdDbus(object):
    def __init__(self):
        self.__session_bus = dbus.SystemBus()
        # restart stop.
        oper_obj = self.__create_obj(DBUS_CONSOLEKIT, DBUS_CONSOLEKIT_MANAGER)
        self.new_restart = self.__get_method(oper_obj, "Restart", DBUS_POINT_MANAGER)
        self.new_stop    = self.__get_method(oper_obj, "Stop", DBUS_POINT_MANAGER)
        # suspend.
        oper_obj = self.__create_obj(DBUS_UPOWER, DBUS_UPOWER_U)
        self.suspend = self.__get_method(oper_obj, "Suspend", DBUS_UPOWER)
        #
        self.__session_bus = dbus.SessionBus()
        oper_obj = self.__create_obj(DBUS_GNOME_SESSION, DBUS_GNOME_SESSION_MANAGER)
        self.interface = dbus.Interface(oper_obj, dbus_interface=DBUS_GNOME_SESSION_POINT)
        # 用户DBUS连接.
        import getpass
        current_user = getpass.getuser()
        user_bus = dbus.SystemBus()
        user_oper_obj = user_bus.get_object("org.freedesktop.Accounts", "/org/freedesktop/Accounts")
        user_inter = dbus.Interface(user_oper_obj, dbus_interface="org.freedesktop.Accounts")
        user_oper_obj = user_bus.get_object(DBUS_ACCOUNTS, user_inter.FindUserByName(current_user))
        self.__user_interface = dbus.Interface(user_oper_obj, dbus_interface=DBUS_ACCOUNTS_PROPERTIES)
        self.real_name = self.__user_interface.Get("org.freedesktop.Accounts.User", "RealName")
        #

    def get_user_name(self):
        return self.__user_interface.Get(DBUS_ACCOUNTS_USER, "UserName")

    def get_user_image_path(self):
        return self.__user_interface.Get(DBUS_ACCOUNTS_USER, "IconFile")

    def stop(self):
        self.interface.Shutdown()

    def restart(self):
        self.interface.RequestReboot()

    def logout(self, id):
        self.interface.Logout(id)
        
    def __create_obj(self, bus_name, bus_path):
        return self.__session_bus.get_object(bus_name, bus_path)

    def __get_method(self, obj, member, dbus_interface):
        return obj.get_dbus_method(member, dbus_interface)

if __name__ == "__main__":
    cmd_dbus = CmdDbus()
    #cmd_dbus.stop()
    
