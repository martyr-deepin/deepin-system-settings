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

class Device(BusBase):

    __gsignals__  = {
        "disconnect-requested":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT)),
        "node-created":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, )),
        "node-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, ))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.Device")

        self.bus.add_signal_receiver(self.disconnect_requested_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "DisconnectRequested")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertyChanged")

        self.bus.add_signal_receiver(self.node_created_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "NodeCreated")

        self.bus.add_signal_receiver(self.node_removed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "NodeRemoved")

    def disconnect(self):
        return self.dbus_method("Disconnect")

    def discovery_services(self, pattern):
        return self.dbus_method("DiscoveryServices", pattern)

    def cancel_discovery(self):
        return self.dbus_method("CancelDiscovery")

    def list_nodes(self):
        nodes = self.dbus_method("ListNodes")
        if nodes:
            nodes = map(lambda x:str(x), nodes)

        return nodes    

    def create_node(self, uuid):
        return self.dbus_method("CreateNode", uuid)

    def remove_node(self, node_path):
        return self.dbus_method("RemoveNode", node_path)

    ###Props
    def get_properties(self):
        return self.dbus_method("GetProperties")

    def set_property(self, key, value):
        return self.dbus_method("SetProperty", key, value)

    def get_name(self):
        if "Name" in self.get_properties().keys():
            return self.get_properties()["Name"]

    def get_vendor(self):
        if "Vendor" in self.get_properties().keys():
            return self.get_properties()["Vendor"]

    def get_product(self):
        if "Product" in self.get_properties().keys():
            return self.get_properties()["Product"]

    def get_version(self):
        if "Version" in self.get_properties().keys():
            return self.get_properties()["Version"]

    def get_legacy_pairing(self):
        if "LegacyPairing" in self.get_properties().keys():
            return self.get_properties()["LegacyPairing"]

    def get_alias(self):
        if "Alias" in self.get_properties().keys():
            return self.get_properties()["Alias"]

    def set_alias(self, alias):
        self.set_property("Alias", alias)

    def get_icon(self):
        if "Icon" in self.get_properties().keys():
            return self.get_properties()["Icon"]

    def get_nodes(self):
        nodes = []
        if "Nodes" in self.get_properties().keys():
            nodes =  self.get_properties()["Nodes"]
            if nodes:
                nodes = map(lambda x:str(x), nodes)

        return nodes        

    def get_paired(self):
        if "Paired" in self.get_properties().keys():
            return bool(self.get_properties()["Paired"])

    def get_connected(self):
        if "Connected" in self.get_properties().keys():
            return bool(self.get_properties()["Connected"])

    def get_blocked(self):
        if "Blocked" in self.get_properties().keys():
            return bool(self.get_properties()["Blocked"])

    def set_blocked(self, blocked):    
        self.set_property("Blocked", dbus.Boolean(blocked))

    def get_trusted(self):
        if "Trusted" in self.get_properties().keys():
            return bool(self.get_properties()["Trusted"])

    def set_trusted(self, trusted):    
        self.set_property("Trusted", dbus.Boolean(trusted))

    def get_adapter(self):
        if "Adapter" in self.get_properties().keys():
            return str(self.get_properties()["Adapter"])

    def get_address(self):
        if "Address" in self.get_properties().keys():
            return self.get_properties()["Address"]
        else:
            return None

    def get_class(self):
        if "Class" in self.get_properties().keys():
            return self.get_properties()["Class"]
        else:
            return None

    def get_uuids(self):
        uuids = []
        if "UUIDs" in self.get_properties().keys():
            uuids = self.get_properties()["UUIDs"]
            if uuids:
                uuids = map(lambda x:str(x), uuids)

        return uuids        

    def get_services(self):
        services = []
        if "Services" in self.get_properties().keys():
            services = self.get_properties()["Services"]
            if services:
                services = map(lambda x:str(x), services)

        return services        

    def disconnect_requested_cb(self):
        self.emit("disconnect-requested")

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

    def node_created_cb(self, node_path):
        self.emit("node-created", node_path)

    def node_removed_cb(self, node_path):
        self.emit("node-removed", node_path)

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
    from manager import Manager
    from adapter import Adapter
    
    adapter = Adapter(Manager().get_default_adapter())

    device = Device(adapter.get_devices()[0])

    print "Name:\n    %s" % device.get_name()
    device.set_alias("Long's Phone")
    print "Alias:\n    %s" % device.get_alias()
    print "Paired:\n    %s" % device.get_paired()
    print "Adapter:\n   %s" % device.get_adapter()
    print "Connected:\n   %s" % device.get_connected()
    print "UUIDs:\n   %s" % device.get_uuids()
    print "Address:\n   %s" % device.get_address()
    print "Find Device:\n   %s" %adapter.find_device(device.get_address())
    print "Services:\n   %s" % device.get_services()
    print "Class:\n   %s" % device.get_class()
    device.set_blocked(True)
    print "Blocked:\n   %s" % device.get_blocked()
    device.set_trusted(False)
    print "Trusted:\n   %s" % device.get_trusted()
    print "Icon:\n   %s" % device.get_icon()
