#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
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
from bus_utils import BusBase

class Adapter(BusBase):

    __gsignals__  = {
        "device-created":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "device-disappeared":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "device-found":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT)),
        "device-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, adapter_path):
        print "DEBUG ", adapter_path
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
        if address not in self.get_address_records():
            return str(self.dbus_method("CreateDevice", address))
        else:
            return self.find_device(address)

    def cancel_device_creation(self, address):
        return self.dbus_method("CancelDeviceCreation", address)

    def create_paired_device(self, address, agent_path, capability,
                             reply_handler_cb = None, error_handler_cb = None):
        if reply_handler_cb and error_handler_cb:
            return self.dbus_method("CreatePairedDevice", address, agent_path, capability,
                                    reply_handler = reply_handler_cb,
                                    error_handler = error_handler_cb)

        return self.dbus_method("CreatePairedDevice", address, agent_path, capability,
                                reply_handler = self.create_paired_reply,
                                error_handler = self.create_paired_error)

    def create_paired_reply(self, device):
        print "paried %s succeed\n" % device

    def create_paired_error(self, error):
        print "paired %s error\n" % error

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

    def get_address_records(self):
        addresses = []
        try:
            from device import Device
            for item in self.get_devices():
                addresses.append(Device(item).get_address())
        except:
            pass

        return addresses

    def start_discovery(self):
        if not self.get_discoverable():
            self.set_discoverable(True)
        self.dbus_method("StartDiscovery")

    def stop_discovery(self):
        self.dbus_method("StopDiscovery")

    def register_agent(self, agent_path, capability):
        if capability in ["DisplayOnly", "DisplayYesNo", "KeyboardOnly", "NoInputNoOutput", ""]:
            self.agent = agent_path
            print "register agent: %s" % agent_path
            return self.dbus_method("RegisterAgent", agent_path, capability)
        else:
            pass

    def unregister_agent(self, agent_path):
        return self.dbus_method("UnRegisterAgent")

    def request_session(self):
        return self.dbus_method("RequestSession")

    def release_session(self):
        return self.dbus_method("ReleaseSession")

    ###Props
    def get_properties(self):
        if self.dbus_method("GetProperties"):
            return self.dbus_method("GetProperties")
        else:
            return {}

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

    def device_found_cb(self, address, values):
        self.emit("device-found", address, values)

    def device_removed_cb(self, dev_path):
        self.emit("device-removed", dev_path)

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class Service(BusBase):

    def __init__(self, adapter_path):
        BusBase.__init__(self, path = adapter_path, interface = "org.bluez.Service")

    def add_record(self, record):
        return int(self.dbus_method("AddRecord"), record)

    def remove_record(self, handle):
        return self.dbus_method("RemoveRecord", handle)

    def request_authorization(self, address, handle):
        return self.dbus_method("RequestAuthorization", address, handle)

    def cancel_authorization(self):
        return self.dbus_method("CancelAuthorization")

    def update_record(self, handle, record):
        return self.dbus_method("UpdateRecord", handle, record)

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

    def register(self, uuid, bridge):
        return self.dbus_method("Register", uuid, bridge)

    def unregister(self, uuid):
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

    def create_proxy(self, pattern, address):
        return str(self.dbus_method("CreateProxy", pattern, address))

    def remove_proxy(self, path):
        return self.dbus_method("RemoveProxy", path)

    def list_proxies(self):
        proxies = self.dbus_method("ListProxies")
        if proxies:
            return map(lambda x:str(x), proxies)
        else:
            return []

    def proxy_created_cb(self, path):
        self.emit("proxy-created", path)

    def proxy_removed_cb(self, path):
        self.emit("proxy-removed", path)

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

if __name__ == "__main__":
    pass
