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

class Adapter(BusBase):

    __gsignals__  = {
        "device-created":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "device-disappeared":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "device-found":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "device-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYDICT)),
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

    def create_device(self, string):
        return str(self.dbus_method("CreateDevice"))

    def cancel_device_creation(self, string):
        return self.dbus_method("CancelDeviceCreation")
    
    def create_paired_device(self, string1, string2, string3):
        return str(self.dbus_method("CreatePairedDevice", string1, string2, string3))
    
    def find_device(self, dev_id):
        return str(self.dbus_method("FindDevice"), dev_id)

    def remove_device(self, dev_path):
        return self.dbus_method("RemoveDevice", dev_path)

    def list_devices(self):
        devices = self.dbus_method("GetDevices")
        if devices:
            return map(lambda x:str(x), devices)
        else:
            return []

    def start_discovery(self):
        self.dbus_method("StartDiscovery")

    def stop_discovery(self):
        self.dbus_method("StopDiscovery")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def set_property(self, key, value):
        return self.dbus_method("SetProperty", key, value)

    def register_agent(self, string1, string2):
        return self.dbus_method("RegisterAgent", string1, string2)
    
    def unregister_agent(self, agent_path):
        return self.dbus_method("UnRegisterAgent")

    def request_session(self):
        return self.dbus_method("RequestSession")

    def release_session(self):
        return self.dbus_method("ReleaseSession")

    ###Signals
    def device_created_cb(self, dev_path):
        self.emit("device-created", dev_path)

    def device_disappeared_cb(self, dev_string):
        self.emit("device-disappeared", dev_string)

    def device_found_cb(self, dev_string, dev_dict):
        self.emti("device-found", dev_string, dev_dict)

    def device_removed_cb(self, dev_path):
        self.emit("device-removed", dev_path)

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class Service(BusBase):

    def __init__(self, adapter_path):
        BusBase.__init__(self, path = adapter_path, interface = "org.bluez.Service")

    def add_record(self, record_str):
        return int(self.dbus_method("AddRecord"), record_str)

    def remove_record(self, record_int):
        return self.dbus_method("RemoveRecord", record_int)

    def request_authorization(self, record_str, record_int):
        return self.dbus_method("RequestAuthorization", record_str, record_int)

    def cancel_authorization(self):
        return self.dbus_method("CancelAuthorization")

    def update_record(self, record_int, record_str):
        return self.dbus_method("UpdateRecord", record_int, record_str)

class Media(BusBase):

    def __init__(self, adapter_path):
        BusBase.__init__(self, path = adapter_path, interface = "org.bluez.Media")
            
    def register_end_point(self,string1, dict1):
        return self.dbus_method("RegisterEndPoint", string1, dict1)

    def unregister_end_point(self, end_point_path):
        return self.dbus_method("UnregisterEndPoint", end_point_path)

    def register_player(self, string1, dict1, dict2):
        return self.dbus_method("RegisterPlayer", string1, dict1, dict2)

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

if __name__ == "__main__":
    pass
