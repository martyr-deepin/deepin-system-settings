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

from bus_utils import BusBase

class DeviceService(BusBase):

    def __init__(self, service_path):
        BusBase.__init__(self, path = service_path , interface = "org.bluez.Characteristic")

    def discover_characteristics(self):
        characteristics = self.dbus_method("DiscoverCharacteristics")
        if characteristics:
            return map(lambda x:str(x), characteristics)
        else:
            return []

    def register_characteristics_watcher(self, agent):
        return self.dbus_method("RegisterCharacteristicsWatcher", agent)

    def unregister_characteristics_watcher(self, agent):
        return self.dbus_method("UnregisterCharacteristicsWatcher", agent)

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def set_property(self, key, value):
        return self.dbus_method("SetProperty", key, value)

    def get_uuid(self):
        if "UUID" in self.get_properties().keys():
            return self.get_properties()["UUID"]

    def get_name(self):
        if "Name" in self.get_properties().keys():
            return self.get_properties()["Name"]

    def get_description(self):
        if "Description" in self.get_properties().keys():
            return self.get_properties()["Description"]

    def get_characteristics(self):
        if "Characteristics" in self.get_properties().keys():
            return self.get_properties()["Characteristics"]

if __name__ == "__main__":
    from manager import Manager
    from adapter import Adapter
    from device import Device

    adapter = Adapter(Manager().get_default_adapter())
    device = Device(adapter.get_devices()[0])
    service = DeviceService(device.get_services()[0])

    print "uuid:\n    %s" % service.get_uuid()
