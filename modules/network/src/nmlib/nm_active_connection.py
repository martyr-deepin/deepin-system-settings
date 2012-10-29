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

from nmobject import NMObject
from nm_utils import TypeConvert
from nmcache import cache

class NMActiveConnection(NMObject):
    '''NMActiveConnection'''

    def __init__(self, active_connection_object_path, interface = "org.freedesktop.NetworkManager.Connection.Active"):
        NMObject.__init__(self, active_connection_object_path, interface)

        self.prop_list = ["Vpn", "Master", "Uuid", "Connection", "SpecificObject", "Devices", "State", "Default", "Default6"]
        self.init_nmobject_with_properties()
        self.bus.add_signal_receiver(self.properties_changed_cb, dbus_interface = self.object_interface, signal_name = "PropertiesChanged")

    def get_vpn(self):
        return self.properties["Vpn"]

    def get_master(self):
        return self.properties["Master"]

    def get_uuid(self):
        return self.properties["Uuid"]

    def get_connection(self):
        return cache.getobject(self.properties["Connection"])

    def get_specific_object(self):
        return self.properties["SpecificObject"]

    def get_devices(self):
        return map(lambda x:cache.getobject(x), self.properties["Devices"])

    def get_state(self):
        return self.properties["State"]

    def get_default(self):
        return self.properties["Default"]
    
    def get_default6(self):
        return self.properties["Default6"]

    ###Signals###
    def properties_changed_cb(self, prop_dict):
        print "PropertiesChanged"
        print TypeConvert.dbus2py(prop_dict)

if __name__ == "__main__":
    nm_active_connection = NMActiveConnection("/org/freedesktop/NetworkManager/ActiveConnection/4");
    print nm_active_connection.properties
