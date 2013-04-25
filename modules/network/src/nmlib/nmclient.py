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
from nmobject import NMObject
from nm_utils import TypeConvert
import traceback
import dbus
from nmcache import get_cache

class NMClient(NMObject):
    '''NMClient'''
        
    __gsignals__  = {
            "device-added":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, )),
            "device-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "state-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_UINT, )),
            "permission-changed":(gobject.SIGNAL_RUN_LAST,gobject.TYPE_NONE, ()),
            }

    def __init__(self):
        NMObject.__init__(self, "/org/freedesktop/NetworkManager", "org.freedesktop.NetworkManager")

        self.prop_list = ["NetworkingEnabled", "WirelessEnabled", "WirelessHardwareEnabled", "WwanEnabled", "Version",
                          "WwanHardwareEnabled", "WimaxEnabled", "WimaxHardwareEnabled", "ActivateConnections", "State"]

        self.manager_running = False
        self.init_nmobject_with_properties()

        self.bus.add_signal_receiver(self.permisson_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "CheckPermissions")

        self.bus.add_signal_receiver(self.device_added_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "DeviceAdded")

        self.bus.add_signal_receiver(self.device_removed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "DeviceRemoved")

        self.bus.add_signal_receiver(self.properties_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertiesChanged")

        self.bus.add_signal_receiver(self.state_changed_cb,dbus_interface = self.object_interface, 
                                     path = self.object_path,signal_name = "StateChanged")
        self.devices = self.get_devices()

        for device in self.devices:
            if not device.get_managed():
                gobject.timeout_add(3000, lambda : self.fix_unmanaged())

    def fix_unmanaged(self):
        try:
            print "fix unmanaged"
            bus = dbus.SystemBus()
            proxy = bus.get_object("com.deepin.network", "/com/deepin/network")
            interface = dbus.Interface(proxy, "com.deepin.network")

            interface.fix_unmanaged()
        except:
            traceback.print_exc()

    def get_devices(self):
        '''return father device objects'''
        try:
            return map(lambda x: get_cache().getobject(x), TypeConvert.dbus2py(self.dbus_method("GetDevices")))
        except:
            return []

    def get_wired_devices(self):
        self.devices = self.get_devices()
        try:
            return filter(lambda x:x.get_device_type() == 1, self.devices)
        except:
            return []

    def get_wired_device(self):
        try:
            return self.get_wired_devices()[0]
        except:
            return None

    def get_wireless_devices(self):
        self.devices = self.get_devices()
        try:
            return filter(lambda x:x.get_device_type() == 2, self.devices)
        except:
            return []

    def get_wireless_device(self):
        try:
            return self.get_wireless_devices()[0]
        except:
            return None

    def get_modem_devices(self):
        self.devices = self.get_devices()
        try:
            return filter(lambda x:x.get_device_type() == 8, self.devices)
        except:
            return []

    def get_modem_device(self):
        try:
            return self.get_modem_devices()[0]
        except:
            return None

    def get_device_by_iface(self, iface):
        device = self.dbus_method("GetDeviceByIpIface", iface)
        if device:
            return get_cache().getobject(device)
        else:
            return None

    def activate_connection(self, connection_path, device_path, specific_object_path):
        '''used for multi activate, must run one by one'''
        try:
            active = self.dbus_interface.ActivateConnection(connection_path, device_path, specific_object_path)
            if active:
                if "vpn" in get_cache().getobject(connection_path).settings_dict.iterkeys():
                    vpn_active_connection = get_cache().get_spec_object(active)
                    
                    if vpn_active_connection.get_vpnstate() in [1, 2, 3, 4]:
                        vpn_active_connection.emit("vpn-connecting")
                        return get_cache().getobject(active)

                    elif vpn_active_connection.get_vpnstate() == 5:
                        vpn_active_connection.emit("vpn-connected")
                        return get_cache().getobject(active)

                    else:
                        vpn_active_connection.emit("vpn-disconnected")
                        return get_cache().getobject(active)

                else:    
                    return get_cache().getobject(active)
            else:
                return None
        except:
            traceback.print_exc()
            return None

    def activate_connection_async(self, connection_path, device_path, specific_object_path):
        '''used for only one activate'''
        try:
            self.dbus_interface.ActivateConnection(connection_path, device_path, specific_object_path,
                                reply_handler = self.activate_finish, error_handler = self.activate_error)
        except:
            traceback.print_exc()

    def activate_finish(self, active_path):
        if active_path:
            return get_cache().getobject(active_path)
    
    def activate_error(self, *error):
        pass

    def add_and_activate_connection(self, connection_path, device_path, specific_object_path):
        try:
            active = self.dbus_interface.AddAndActivateConnection(connection_path, device_path, specific_object_path)
            if active:
                return get_cache().getobject(active)
        except:
            traceback.print_exc()

    def add_and_activate_connection_async(self, connection_path, device_path, specific_object_path):
        try:
            self.dbus_interface.AddAndActivateConnection(connection_path, device_path, specific_object_path,
                                             reply_handler = self.add_activate_finish, error_handler = self.add_activate_error)
        except:
            traceback.print_exc()

    def add_activate_finish(self, active_path):
        if active_path:
            return get_cache().getobject(active_path)

    def add_activate_error(self, *error):
        pass

    def deactive_connection(self, active_object_path):
        return self.dbus_method("DeactivateConnection", active_object_path)

    def deactive_connection_async(self, active_object_path):
        try:
            self.dbus_interface.DeactivateConnection(active_object_path, reply_handler = self.deactive_finish, 
                                                     error_handler = self.deactive_error)
        except:
            traceback.print_exc()

    def deactive_finish(self, *reply):
        pass

    def deactive_error(self, *error):
        print error

    def nm_client_sleep(self, sleep_flag):
        return self.dbus_method("Sleep", sleep_flag)

    def get_permissions(self):
        return self.dbus_method("GetPermissions")

    def get_permission_result(self, permission):
        return self.get_permissions()[permission]

    def networking_set_enabled(self, enabled):
        return self.dbus_method("Enable", enabled)
            
    def networking_get_enabled(self):
        return self.properties["NetworkingEnabled"]

    def wireless_get_enabled(self):
        return self.properties["WirelessEnabled"]

    def wireless_set_enabled(self, enabled):
        self.set_property("WirelessEnabled", enabled)
    
    def wireless_hardware_get_enabled(self):
        return self.properties["WirelessHardwareEnabled"]

    def wwan_get_enabled(self):
        return self.properties["WwanEnabled"]

    def wwan_set_enabled(self, enabled):
        self.set_property("WwanEnabled", enabled)

    def wwan_hardware_get_enabled(self):
        return self.properties["WwanHardwareEnabled"]

    def wimax_get_enabled(self):
        return self.properties["WimaxEnabled"]

    def wimax_set_enabled(self, enabled):
        self.set_property("WimaxEnabled", enabled)

    def wimax_get_hardware_enabled(self):
        return self.properties["WimaxHardwareEnabled"]

    def get_version(self):
        return self.properties["Version"]

    def get_state(self):
        return self.properties["State"]

    def get_manager_running(self):
        return self.manager_running

    def get_active_connections(self):
        '''return active connections objects'''
        try:
            return filter(lambda x: x.get_state() == 2, map(lambda x: get_cache().getobject(x), self.properties["ActiveConnections"]))
        except:
            return []

    def get_anti_vpn_active_connection(self):
        try:
            return filter(lambda x:x.get_vpn() != 1, self.get_active_connections())
        except:
            return []

    def get_vpn_active_connection(self):
        try:
            return filter(lambda x:x.get_vpn() == 1, self.get_active_connections())
        except:
            return []

    def get_wired_active_connection(self):
        try:
            return filter(lambda x:x.get_devices()[0] == self.get_wired_device(), self.get_active_connections())
        except:
            return []

    def get_wireless_active_connection(self):
        try:
            return filter(lambda x:x.get_devices()[0] == self.get_wireless_device(), self.get_active_connections())
        except:
            return []

    def get_pppoe_active_connection(self):
        pass

    def get_mobile_active_connection(self):
        try:
            return filter(lambda x: x.get_devices()[0].get_device_type() == 8, self.get_active_connections())
        except:
            return []

    ###Signals ###
    def device_added_cb(self, device_object_path):
        if not filter(lambda d: d.object_path == device_object_path, self.devices):
            self.emit("device-added", device_object_path)

    def device_removed_cb(self, device_object_path):
        self.emit("device-removed", device_object_path)
        ##try:
        #    device = get_cache().getobject(device_object_path)
        #    device.remove_signals()
        #except:
        #    pass

        #try:
        #    spec_device = get_cache().get_spec_object(device_object_path)
        #    spec_device.remove_signals()
        #except:
        #    pass

    def permisson_changed_cb(self):
        self.emit("permission-changed")

    def state_changed_cb(self, state):
        self.emit("state-changed", TypeConvert.dbus2py(state))
    
    def properties_changed_cb(self, prop_dict):
        self.init_nmobject_with_properties()

if __name__ == "__main__":
    from nmobject import dbus_loop
    
    # print nmclient.get_state()
    # nmclient.networking_set_enabled(False)

    # nmclient.update_properties()
    # print nmclient.get_state()

    # nmclient.networking_set_enabled(True)
    # nmclient.update_properties()
    # print nmclient.get_state()

    # nmclient.dbus_proxy.StateChanged(10)

    dbus_loop.run()
