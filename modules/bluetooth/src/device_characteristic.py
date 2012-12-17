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

class DeviceCharacteristic(BusBase):

    def __init__(self, path):
        BusBase.__init__(self, path = path , interface = "org.bluez.Characteristic")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def get_uuid(self):
        if "UUID" in self.get_properties().keys():
            return self.get_properties()["UUID"]

    def get_name(self):
        if "Name" in self.get_properties().keys():
            return self.get_properties()["Name"]

    def get_description(self):
        if "Description" in self.get_properties().keys():
            return self.get_properties()["Description"]

    def get_format(self):
        if "Format" in self.get_properties().keys():
            return self.get_properties()["Format"]

    def get_value(self):
        if "Value" in self.get_properties().keys():
            return self.get_properties()["Value"]

    def set_value(self, value):
        return self.set_property("Value", value)

    def get_representation(self):
        if "Representation" in self.get_properties().keys():
            return self.get_properties()["Representation"]

if __name__ == "__main__":
    pass
