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

class Adapter(BusBase):

    __gsignals__  = {
        "device-created":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "device-disappeared":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "device-found":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "device-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT)),
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,))
            }

    def __init__(self, adapter_path):
        BusBase.__init__(self, path = adapter_path, interface = "org.bluez.Adapter")

        self.bus.add_signal_receiver(self.device_created_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "DeviceCreated")

        self.bus.add_signal_receiver(self.device_disappeared_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "DeviceDisappeared")

        self.bus.add_signal_receiver(self.device_found_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "DeviceFound")

        self.bus.add_signal_receiver(self.device_removed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "DeviceRemoved")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertyChanged")

    def create_device(self, address):
        return str(self.dbus_method("CreateDevice", address))

    def cancel_device_creation(self, address):
        return self.dbus_method("CancelDeviceCreation", address)
    
    def create_paired_device(self, address, agent_path, capability):
        return str(self.dbus_method("CreatePairedDevice", address, agent_path, capability))
    
    def find_device(self, address):
        return str(self.dbus_method("FindDevice", address))

    def remove_device(self, dev_path):
        return self.dbus_method("RemoveDevice", dev_path)

    def get_devices(self):
        devices = []

        if "Devices" in self.get_properties().keys():
            devices = self.get_properties()["Devices"]
            if devices:
                devices = map(lambda x:str(x), devices)
        else:
            devices = self.dbus_method("ListDevices")
            if devices:
                devices = map(lambda x:str(x), devices)

        return devices    

    def start_discovery(self):
        if not self.get_discoverable():
            self.set_discoverable(True)
        self.dbus_method("StartDiscovery")

    def stop_discovery(self):
        self.dbus_method("StopDiscovery")

    def register_agent(self, agent_path, capability):
        return self.dbus_method("RegisterAgent", agent_path, capability)
    
    def unregister_agent(self, agent_path):
        return self.dbus_method("UnRegisterAgent")

    def request_session(self):
        return self.dbus_method("RequestSession")

    def release_session(self):
        return self.dbus_method("ReleaseSession")

    ###Props    
    def get_properties(self):
        return self.dbus_method("GetProperties")

    def set_property(self, key, value):
        return self.dbus_method("SetProperty", key, value)

    def get_name(self):
        if "Name" in self.get_properties().keys():
            return self.get_properties()["Name"]
        else:
            return None

    def set_name(self, name):
        self.set_property("Name", str(name))

    def get_powered(self):
        if "Powered" in self.get_properties().keys():
            return self.get_properties()["Powered"]
        else:
            return False

    def set_powered(self, powered):
        self.set_property("Powered", dbus.Boolean(powered))

    def get_discoverable(self):
        if "Discoverable" in self.get_properties().keys():
            return self.get_properties()["Discoverable"]
        else:
            return False

    def set_discoverable(self, discoverable):
        self.set_property("Discoverable", dbus.Boolean(discoverable))

    def get_discovering(self):
        if "Discovering" in self.get_properties().keys():
            return self.get_properties()["Discovering"]
        else:
            return False

    def get_discoverable_timeout(self):
        if "DiscoverableTimeout" in self.get_properties().keys():
            return self.get_properties()["DiscoverableTimeout"]
        else:
            return 0

    def set_discoverable_timeout(self, timeout):
        self.set_property("DiscoverableTimeout", dbus.UInt32(timeout))

    def get_pairable(self):
        if "Pairable" in self.get_properties().keys():
            return self.get_properties()["Pairable"]
        else:
            return False

    def set_pairable(self, pairable):
        self.set_property("Pairable", dbus.Boolean(pairable))

    def get_pairable_timeout(self):
        if "PairableTimeout" in self.get_properties().keys():
            return self.get_properties()["PairableTimeout"]
        else:
            return 0

    def set_pairable_timeout(self, timeout):
        self.set_property("PairableTimeout", dbus.UInt32(timeout))

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

    ###Signals
    def device_created_cb(self, dev_path):
        self.emit("device-created", dev_path)

    def device_disappeared_cb(self, address):
        self.emit("device-disappeared", address)

    def device_found_cb(self, dev_string, values):
        self.emti("device-found", dev_string, values)

    def device_removed_cb(self, dev_path):
        self.emit("device-removed", dev_path)

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class Service(BusBase):

    def __init__(self, adapter_path):
        BusBase.__init__(self, path = adapter_path, interface = "org.bluez.Service")

    def add_record(self, record_xml):
        return int(self.dbus_method("AddRecord"), record_xml)

    def remove_record(self, record_id):
        return self.dbus_method("RemoveRecord", record_id)

    def request_authorization(self, record_str, record_int):
        return self.dbus_method("RequestAuthorization", record_str, record_int)

    def cancel_authorization(self):
        return self.dbus_method("CancelAuthorization")

    def update_record(self, record_id, record_xml):
        return self.dbus_method("UpdateRecord", record_id, record_xml)

class Media(BusBase):

    def __init__(self, adapter_path):
        BusBase.__init__(self, path = adapter_path, interface = "org.bluez.Media")
            
    def register_end_point(self, endpoint, properties):
        return self.dbus_method("RegisterEndPoint", endpoint, properties)

    def unregister_end_point(self, endpoint):
        return self.dbus_method("UnregisterEndPoint", endpoint)

    def register_player(self, player, properties, metadata):
        return self.dbus_method("RegisterPlayer", player, properties, metadata)

    def unregister_player(self, player_path):
        return self.dbus_method("UnregisterPlayer", player_path)

class NetworkServer(BusBase):

    def __init__(self, adapter_path):
        BusBase.__init__(self, path = adapter_path, interface = "org.bluez.NetworkServer")

    def register(self, string1, string2):
        return self.dbus_method("Register", string1, string2)

    def unregister(self, string1):
        return self.dbus_method("Unregister")

class OutOfBand(BusBase):

    def __init__(self, adapter_path):
        BusBase.__init__(self, path = adapter_path, interface = "org.bluez.OutOfBand")

    def add_remote_data(self, data_string, array1, array2):
        self.dbus_method("AddRemoteData", data_string, array1, array2)

    def remove_remote_data(self, data_string):
        return self.dbus_method("RemoveRemoteData", data_string)
        
    def read_local_data(self):
        return self.dbus_method("ReadLocalData")

class SerialProxyManager(BusBase):

    __gsignals__  = {
        "proxy-created":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "proxy-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            }

    def __init__(self, adapter_path):
        BusBase.__init__(self, path = adapter_path, interface = "org.bluez.SerialProxyManager")

        self.bus.add_signal_receiver(self.proxy_created_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "ProxyCreated")

        self.bus.add_signal_receiver(self.proxy_removed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "ProxyRemoved")

    def create_proxy(self, string1, string2):
        return str(self.dbus_method("CreateProxy"), string1, string2)

    def remove_proxy(self, proxy_string):
        return self.dbus_method("RemoveProxy", proxy_string)

    def list_proxies(self):
        proxies = self.dbus_method("ListProxies")
        if proxies:
            return map(lambda x:str(x), proxies)
        else:
            return []

    def proxy_created_cb(self, proxy_string):
        self.emit("proxy-created", proxy_string)

    def proxy_removed_cb(self, proxy_string):
        self.emit("proxy-removed", proxy_string)

class SimAccess(BusBase):

    def __init__(self, adapter_path):
        BusBase.__init__(self, path = adapter_path, interface = "org.bluez.SimAccess")

    def disconnect(self):
        return self.dbus_method("Disconnect")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def get_connected(self):
        if "Connected" in self.get_properties().keys():
            return self.get_properties()["Connected"]
        else:
            return False

def test_adapter():
    from manager import Manager
    manager = Manager()
    adapter = Adapter(manager.get_default_adapter())

    from device import Device
    device_address = Device(adapter.get_devices()[0]).get_address()
    print "find device:\n    %s" % adapter.find_device(device_address)
    print "remove device:\n    %s" % adapter.remove_device(adapter.find_device(device_address))
    # print "create device:\n    %s" % adapter.create_device(device_address)

    print "get devices:\n    %s" % adapter.get_devices()

    adapter.set_name("Long Wei's PC")
    print "get name:\n    %s" % adapter.get_name()

    adapter.set_powered(True)
    print "get powered:\n    %s" % adapter.get_powered()

    adapter.set_discoverable(True)
    print "get discoverable:\n    %s" % adapter.get_discoverable()

    print "get discovering:\n    %s" % adapter.get_discovering()

    adapter.set_discoverable_timeout(120)
    print "get discoverable_timeout:\n    %s" % adapter.get_discoverable_timeout()

    adapter.set_pairable(True)
    print "get pairable:\n    %s" % adapter.get_pairable()

    adapter.set_pairable_timeout(180)
    print "get pairable timeout:\n    %s" % adapter.get_pairable_timeout()

    print "get class:\n    %s" % adapter.get_class()
    print "get address:\n    %s" % adapter.get_address()
    print "get uuids:\n    %s" % adapter.get_uuids()



def test_service():
    pass
    
if __name__ == "__main__":
    test_adapter()

    # test_service()
