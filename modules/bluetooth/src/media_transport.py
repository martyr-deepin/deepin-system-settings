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
import gobject
from utils import BusBase

class MediaTranport(BusBase):

    __gsignals__  = {
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,))
            }

    def __init__(self, path):
        BusBase.__init__(self, path = path, interface = "org.bluez.MediaTranport")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertyChanged")

    def release(self, accesstype):
        return self.dbus_method("Release", accesstype)

    ###Props    
    def get_properties(self):
        return self.dbus_method("GetProperties")

    def set_property(self, key, value):
        return self.dbus_method("SetProperty", key, value)

    def get_device(self):
        if "Device" in self.get_properties().keys():
            return self.get_properties()["Device"]
        else:
            return None

    def get_uuid(self):
        if "UUID" in self.get_properties().keys():
            return self.get_properties()["UUID"]

    def get_codec(self):
        if "Codec" in self.get_properties().keys():
            return self.get_properties()["Codec"]

    def get_configuration(self):
        if "Configuration" in self.get_properties().keys():
            return self.get_properties()["Configuration"]

    def get_delay(self):
        if "Delay" in self.get_properties().keys():
            return self.get_properties()["Delay"]

    def get_nrec(self):
        if "NREC" in self.get_properties().keys():
            return self.get_properties()["NREC"]

    def get_inbandringtone(self):
        if "InbandRingtone" in self.get_properties().keys():
            return self.get_properties()["InbandRingtone"]

    def get_routing(self):
        if "Routing" in self.get_properties().keys():
            return self.get_properties()["Routing"]

    def set_delay(self, delay):
        self.set_property("Delay", delay)

    def set_nrec(self, nrec):
        self.set_property("NREC", nrec)

    def set_inbandringtone(self, inbandringtone):
        self.set_property("NREC", inbandringtone)

    ###Signals
    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)
    
if __name__ == "__main__":
    pass
