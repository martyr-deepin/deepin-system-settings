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
import gudev
import os
import traceback
from nmobject import NMObject
from nmcache import cache

udev_client = gudev.Client("net")

class NMDevice(NMObject):
    '''NMDevice'''

    __gsignals__  = {
            "state-changed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT, gobject.TYPE_UINT, gobject.TYPE_UINT)),
            "device-active":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT,)),
            "device-deactive":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT,)),
            "device-available":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT,)),
            "device-unavailable":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT,))
            }

    def __init__(self, device_object_path, device_interface = "org.freedesktop.NetworkManager.Device"):
        NMObject.__init__(self, device_object_path, device_interface)
        self.prop_list = ["Capabilities", "DeviceType", "ActiveConnection", "Dhcp4Config", "Dhcp6Config", "Driver", "FirmwareMissing", "Interface", "IpInterface", "Ip4Config", "Ip6Config", "Managed", "State"]
        self.bus.add_signal_receiver(self.state_changed_cb, dbus_interface = self.object_interface, path = self.object_path, signal_name = "StateChanged")
        self.init_nmobject_with_properties()
        self.udev_device = ""

    def get_capabilities(self):
        return self.properties["Capabilities"]

    def get_device_type(self):
        return self.properties["DeviceType"]

    def get_active_connection(self):
        '''return active connection object'''
        return cache.getobject(self.properties["ActiveConnection"])

    def is_active(self):
        try:
            if self.get_state() == 100 and self.get_active_connection():
                return True
            else:
                return False
        except:
            return False

    def is_connection_active(self, connection_path):
        return connection_path == self.get_real_active_connection()

    def get_real_active_connection(self):
        if self.get_active_connection():
            return self.get_active_connection().get_connection()

    def get_dhcp4_config(self):
        return cache.getobject(self.properties["Dhcp4Config"])

    def get_dhcp6_config(self):
        return cache.getobject(self.properties["Dhcp6Config"])

    def get_driver(self):
        return self.properties["Driver"]

    def get_firmware_missing(self):
        return self.properties["FirmwareMissing"]

    def get_iface(self):
        return self.properties["Interface"]

    def get_ip_iface(self):
        return self.properties["IpInterface"]

    def get_ip4_config(self):
        return cache.getobject(self.properties["Ip4Config"])

    def get_ip6_config(self):
        return cache.getobject(self.properties["Ip6Config"])

    def get_managed(self):
        return self.properties["Managed"]

    def get_state(self):
        return self.properties["State"]
    
    def get_udi(self):
        return self.properties["Udi"]

    def get_udev_device(self):
        if self.udev_device:
            pass
        else:
            try:
                self.udev_device =  udev_client.query_by_sysfs_path(self.get_udi())
                if not self.udev_device:
                    self.udev_device =  udev_client.query_by_subsystem_and_name("net", self.get_iface())
            except:
                traceback.print_exc()
        return self.udev_device    

    def get_vendor(self):
        if self.get_udev_device().has_property("ID_VENDOR_FROM_DATABASE"):
            return self.get_udev_device().get_property("ID_VENDOR_FROM_DATABASE")

    def get_product(self):
        if self.get_udev_device().has_property("ID_MODEL_FROM_DATABASE"):
            return self.get_udev_device().get_property("ID_MODEL_FROM_DATABASE")

    def get_device_desc(self):
        self.udev_device = self.get_udev_device()

        if self.udev_device.has_property("ID_VENDOR_FROM_DATABASE") and self.udev_device.has_property("ID_MODEL_FROM_DATABASE"):
            return self.udev_device.get_property("ID_VENDOR_FROM_DATABASE") + " "+self.udev_device.get_property("ID_MODEL_FROM_DATABASE")
        elif self.udev_device.has_property("ID_MODEL_FROM_DATABASE"):
            return self.udev_device.get_property("ID_MODEL_FROM_DATABASE")

        elif self.udev_device.has_property("ID_MODEL_ID"):
            cmd = "lspci -s %s" % self.udev_device.get_property("ID_MODEL_ID").split("/")[-1]
            return os.popen(cmd).read().split(":")[-1].split("(")[0]

        elif self.udev_device.has_property("DEVPATH"):
            cmd = "lspci -s %s" % self.udev_device.get_property("DEVPATH").split("/")[-3]
            return os.popen(cmd).read().split(":")[-1].split("(")[0]

        else:
            cmd = "lspci -s %s" % self.udev_device.get_sysfs_path().split("/")[-3]
            return os.popen(cmd).read().split(":")[-1].split("(")[0]

    def nm_device_disconnect(self):
        self.dbus_method("Disconnect", reply_handler = self.disconnect_finish, error_handler = self.disconnect_error)

    def disconnect_finish(self, *reply):
        pass
        
    def disconnect_error(self, *error):
        pass

    def state_changed_cb(self, new_state, old_state, reason):
        self.emit("state-changed", new_state, old_state, reason)
        self.init_nmobject_with_properties()

        if old_state != 100 and new_state == 100:
            self.emit("device-active", reason)
        elif old_state == 100 and new_state != 100:
            self.emit("device-deactive", reason)

        if old_state < 30 and new_state >= 30:
            self.emit("device-available", new_state)
        elif old_state >=30 and new_state < 30:
            self.emit("device-unavailable", new_state)

if __name__ == "__main__":
    nmdevice = NMDevice("/org/freedesktop/NetworkManager/Devices/1")
    print nmdevice.get_product()
    # print nmdevice.properties
    # nmdevice.nm_device_disconnect()
    print nmdevice.get_state()
