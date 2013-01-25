#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
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

def test_fake_icon():
    bus = dbus.SystemBus()
    pwd_object = bus.get_object("com.deepin.passwdservice", "/")
    pwd_interface = dbus.Interface(pwd_object, "com.deepin.passwdservice")

    account_object = bus.get_object("org.freedesktop.Accounts", "/org/freedesktop/Accounts")
    account_interface = dbus.Interface(account_object, "org.freedesktop.Accounts")

    user_list = []
    for userpath in account_interface.ListCachedUsers():
        user_object = bus.get_object("org.freedesktop.Accounts", userpath)
        user_interface = dbus.Interface(user_object, "org.freedesktop.DBus.Properties")
        username = user_interface.Get("org.freedesktop.Accounts.User", "UserName")
        user_list.append(username)

    for user in user_list:
        print pwd_interface.get_user_fake_icon(user)

if __name__ == "__main__":
    test_fake_icon()
