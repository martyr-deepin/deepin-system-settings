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

import sys
sys.path.append("../")

import dbus
import gobject
from nmlib.nmobject import NMObject
from nmlib.nm_utils import TypeConvert
# from mmdevice import MMDevice

mm_bus = dbus.SystemBus()

class MMObject(NMObject):
    '''MMObject'''

    def __init__(self, object_path = "/org/freedesktop/ModemManager",object_interface = "org.freedesktop.ModemManager"):
        NMObject.__init__(self, object_path, object_interface, service_name = "org.freedesktop.ModemManager", bus = mm_bus)

    def init_mmobject_with_properties(self):
        self.init_nmobject_with_properties()

class MMClient(MMObject):
    '''MMClient'''
        
    __gsignals__  = {
            "device-added":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,)),
            "device-removed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,))
            }
    
    def __init__(self):
        MMObject.__init__(self)

        self.bus.add_signal_receiver(self.device_added_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "DeviceAdded")

        self.bus.add_signal_receiver(self.device_removed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "DeviceRemoved")

    def enumerate_devices(self):
        return TypeConvert.dbus2py(self.dbus_method("EnumerateDevices"))

    def set_logging(self, level):
        self.dbus_method("SetLogging", level, reply_handler = self.set_logging_finish, error_handler = self.set_logging_error)

    def set_logging_finish(self, *reply):
        pass

    def set_logging_error(self, *error):
        pass

    def get_cdma_device(self):
        from mmdevice import MMDevice

        return filter(lambda x:MMDevice(x).get_type() == 2, self.enumerate_devices())

    def get_gsm_device(self):
        from mmdevice import MMDevice

        return filter(lambda x:MMDevice(x).get_type() == 1, self.enumerate_devices())

    def device_added_cb(self, device_path):
        print "device_added_cb"
        print device_path
        self.emit("device-added", device_path)

    def device_removed_cb(self, device_path):
        print "device_removed_cb"
        print device_path
        self.emit("device-removed", device_path)

if __name__ == "__main__":
    print "test import"
