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
from utils import BusBase

class Device(BusBase):

    __gsignals__  = {
        "disconnect-requested":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.Device")

        self.bus.add_signal_receiver(self.disconnect_requested_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "DisconnectRequested")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertyChanged")

    def disconnect(self):
        return self.dbus_method("Disconnect")

    def discovery_services(self, string):
        return self.dbus_method("DiscoveryServices", string)

    def cancel_discovery(self):
        return self.dbus_method("CancelDiscovery")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def set_property(self, key, value):
        return self.dbus_method("SetProperty", key, value)

    def disconnect_requested_cb(self):
        self.emit("disconnect-requested")

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)


class Audio(BusBase):

    __gsignals__  = {
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.Audio")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertyChanged")

    def connect(self):
        return self.dbus_method("Connect")

    def disconnect(self):
        return self.dbus_method("Disconnect")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class AudioSource(BusBase):

    __gsignals__  = {
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.AudioSource")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertyChanged")
    def connect(self):
        return self.dbus_method("Connect")

    def disconnect(self):
        return self.dbus_method("Disconnect")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class Control(BusBase):

    __gsignals__  = {
        "connected":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "disconnected":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.Control")

        self.bus.add_signal_receiver(self.connected_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "Connected")

        self.bus.add_signal_receiver(self.disconnected_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "Disconnected")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertyChanged")

    def is_connected(self):
        return bool(self.dbus_method("IsConnected"))

    def volume_up(self):
        return self.dbus_method("VolumeUp")

    def volume_down(self):
        return self.dbus_method("VolumeDown")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def connected_cb(self):
        self.emit("connected")

    def disconected_cb(self):
        self.emit("disconnected")

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class HandsFreeGateway(BusBase):

    __gsignals__  = {
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.HandsFreeGateway")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertyChanged")
    def connect(self):
        return self.dbus_method("Connect")

    def disconnect(self):
        return self.dbus_method("Disconnect")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def register_agent(self, agent_path):
        return self.dbus_method("RegisterAgent", agent_path)

    def unregister_agent(self, agent_path):
        return self.dbus_method("UnregisterAgent", agent_path)
    
    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class Network(BusBase):

    __gsignals__  = {
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.Network")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertyChanged")

    def connect(self):
        return self.dbus_method("Connect")

    def disconnect(self):
        return self.dbus_method("Disconnect")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class Serial(BusBase):

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.Serial")

    def connect(self, string):
        return self.dbus_method("Connect", string)
    
    def connect_fd(self, string):
        return self.dbus_method("ConnectFD", string)

    def disconnect(self, string):
        return self.dbus_method("Disconnect", string)


if __name__ == "__main__":
    pass

