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

from utils import BusBase

class Service(BusBase):

    def __init__(self, service_path):
        BusBase.__init__(self, path = service_path , interface = "org.bluez.Characteristic")

    def discovery_characteristics(self):
        characteristics = self.dbus_method("DiscoveryCharacteristics")
        if characteristics:
            return map(lambda x:str(x), characteristics)
        else:
            return []

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def get_uuid(self):
        if "UUID" in self.get_properties().keys():
            return self.get_properties()["UUID"]

    def register_characteristics_watcher(self, watcher_path):
        return self.dbus_method("RegisterCharacteristicsWatcher", watcher_path)

    def unregister_characteristics_watcher(self, watcher_path):
        return self.dbus_method("UnregisterCharacteristicsWatcher", watcher_path)

if __name__ == "__main__":
    from manager import Manager
    from adapter import Adapter
    from device import Device

    adapter = Adapter(Manager().get_default_adapter())
    device = Device(adapter.get_devices()[0])
    service = Service(device.get_services()[0])

    print "uuid:\n    %s" % service.get_uuid()
