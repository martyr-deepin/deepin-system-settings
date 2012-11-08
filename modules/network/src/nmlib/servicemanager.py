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

import gobject
import dbus

manager_bus = dbus.SystemBus()
manager_proxy = manager_bus.get_object("org.freedesktop.DBus", "/org/freedesktop/DBus")
manager_interface = dbus.Interface(manager_proxy, "org.freedesktop.DBus")

class ServiceManager(gobject.GObject):
        
    __gsignals__  = {
            "name-lost":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,)),
            "nameowner-changed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,))
            }
    
    def __init__(self):
        gobject.GObject.__init__()

        manager_bus.add_signal_receiver(self.name_lost_cb, dbus_interface = "org.freedesktop.DBus",
                                        path = "/org/freedesktop/DBus", signal_name = "NameLost")

        manager_bus.add_signal_receiver(self.nameowner_changed_cb, dbus_interface = "org.freedesktop.DBus",
                                        path = "/org/freedesktop/DBus", signal_name = "NameOwnerChanged")

    def name_has_owner(self, name):
        pass

    def name_lost_cb(self, *args):
        print args
        if args == "org.freedesktop.NetworkManager":
            print "service networkmanager stop"

    def nameowner_changed_cb(self, wellknown, old_name, new_name):
        if wellknown == "org.freedesktop.NetworkManager" and not new_name:
            self.emit("nameowner-changed", wellknown)

servicemanager = ServiceManager()
