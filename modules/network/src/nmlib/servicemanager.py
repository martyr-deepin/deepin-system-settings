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
# nm_bus = dbus.SystemBus()
# def refresh_nm_bus():
#     global nm_bus
#     nm_bus = dbus.SystemBus()
#     return nm_bus

manager_proxy = manager_bus.get_object("org.freedesktop.DBus", "/org/freedesktop/DBus")
manager_interface = dbus.Interface(manager_proxy, "org.freedesktop.DBus")

class ServiceManager(gobject.GObject):
        
    __gsignals__  = {
            "name-owner-changed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,)),
            "service-start":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,)),
            "service-stop":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,))
            }
    
    def __init__(self):
        gobject.GObject.__init__(self)

        manager_bus.add_signal_receiver(self.name_lost_cb, dbus_interface = "org.freedesktop.DBus",
                                        path = "/org/freedesktop/DBus", signal_name = "NameLost")

        manager_bus.add_signal_receiver(self.name_owner_changed_cb, dbus_interface = "org.freedesktop.DBus",
                                        path = "/org/freedesktop/DBus", signal_name = "NameOwnerChanged")

        manager_bus.add_signal_receiver(self.name_accuired_cb, dbus_interface = "org.freedesktop.DBus",
                                        path = "/org/freedesktop/DBus", signal_name = "NameAccuired")

        self.nm_bus = dbus.SystemBus()

    def get_nm_bus(self):
        self.nm_bus = None
        self.nm_bus = dbus.SystemBus()

    def list_names(self):
        return map(lambda x:str(x), manager_interface.ListNames())

    def name_has_owner(self, name):
        return manager_interface.NameHasOwner(name)

    def get_name_owner(self, name):
        if self.name_has_owner(name):
            return manager_interface.GetNameOwner(name)

    def name_owner_changed_cb(self, wellknown, old_name, new_name):
        if wellknown == "org.freedesktop.NetworkManager":
            if old_name and not new_name:
                self.emit("service-stop", "org.freedesktop.NetworkManager")
            if new_name and not old_name:
                self.emit("service-start", "org.freedesktop.NetworkManager")
        else:
            pass

    def name_lost_cb(self, *args):
        print "name lost"
        print args

    def name_accuired_cb(self, *args):
        print "name accuired"
        print args

servicemanager = ServiceManager()
