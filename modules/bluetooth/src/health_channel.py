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

class HealthChannel(BusBase):

    def __init__(self, path):
        BusBase.__init__(self, path = path, interface = "org.bluez.HealthChannel")

    def acquire(self):
        return self.dbus_method("Acquire")

    def release(self):
        return self.dbus_method("Release")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def get_type(self):
        if "Type" in self.get_properties().keys():
            return self.get_properties()["Type"]

    def get_device(self):
        if "Device" in self.get_properties().keys():
            return self.get_properties()["Device"]

    def get_application(self):
        if "Application" in self.get_properties().keys():
            return self.get_properties()["Application"]


if __name__ == "__main__":
    pass
