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

class SerialProxy(BusBase):

    def __init__(self, proxy_path):
        BusBase.__init__(self, path = proxy_path , interface = "org.bluez.SerialProxy")

    def enable(self):
        return self.dbus_method("Enable")

    def disable(self):
        return self.dbus_method("Disable")

    def get_properties(self):
        return self.dbus_method("GetInfo")

    def set_serial_paramemters(self, rate, data, stop, parity):
        return self.dbus_method("SetSerialParamemters", rate, data, stop, parity)

    def get_uuid(self):
        if "uuid" in self.get_properties().keys():
            return self.get_properties()["uuid"]

    def get_address(self):
        if "address" in self.get_properties().keys():
            return self.get_properties()["address"]

    def get_channel(self):
        if "channel" in self.get_properties().keys():
            return self.get_properties()["channel"]

    def get_enabled(self):
        if "enabled" in self.get_properties().keys():
            return self.get_properties()["enabled"]

    def get_connected(self):
        if "connected" in self.get_properties().keys():
            return self.get_properties()["connected"]

if __name__ == "__main__":
    pass
