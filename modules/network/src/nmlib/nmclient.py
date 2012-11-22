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
# from nmdevice import NMDevice
# from nm_active_connection import NMActiveConnection
import traceback
from nmcache import cache

class NMClient(NMObject):
    '''NMClient'''
        
    __gsignals__  = {
            "device-added":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str, )),
            "device-removed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,)),
            "state-changed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT, )),
            "permisson-changed":(gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE, ()),
            "activate-succeed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,)),
            "activate-failed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,))
            }

    def __init__(self):
        NMObject.__init__(self, "/org/freedesktop/NetworkManager", "org.freedesktop.NetworkManager")
        self.prop_list = ["NetworkingEnabled", "WirelessEnabled", "WirelessHardwareEnabled", "WwanEnabled", "Version",
                          "WwanHardwareEnabled", "WimaxEnabled", "WimaxHardwareEnabled", "ActivateConnections", "State"]

        self.manager_running = False
        self.init_nmobject_with_properties()

        self.bus().add_signal_receiver(self.permisson_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "CheckPermissions")

        self.bus().add_signal_receiver(self.device_added_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "DeviceAdded")

        self.bus().add_signal_receiver(self.device_removed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "DeviceRemoved")

        self.bus().add_signal_receiver(self.properties_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertiesChanged")

        self.bus().add_signal_receiver(self.state_changed_cb,dbus_interface = self.object_interface, 
                                     path = self.object_path,signal_name = "StateChanged")
        self.devices = self.get_devices()

    def get_devices(self):
        '''return father device objects'''
        if self.dbus_method("GetDevices"):
            return map(lambda x: cache.getobject(x), TypeConvert.dbus2py(self.dbus_method("GetDevices")))
        else:
            return []

    def get_wired_devices(self):
        # return filter(lambda x:x.get_device_type() == 1, self.get_devices())
        if self.devices:
            return filter(lambda x:x.get_device_type() == 1, self.devices)
        else:
            return []

    def get_wired_device(self):
        return self.get_wired_devices()[0]

    def get_wireless_devices(self):

        if self.devices:
            return filter(lambda x:x.get_device_type() == 2, self.devices)
        else:
            return []

    def get_wireless_device(self):
        return self.get_wireless_devices()[0]

    def get_modem_devices(self):
        if self.devices:
            return filter(lambda x:x.get_device_type() == 8, self.devices)
        else:
            return []

    def get_modem_device(self):
        return self.get_modem_devices()[0]

    def get_device_by_iface(self, iface):
        # return cache.getobject(self.dbus_method("GetDeviceByIpIface", iface))
        device = self.dbus_method("GetDeviceByIpIface", iface)
        if device:
            return cache.getobject(device)
        else:
            return None

    def activate_connection(self, connection_path, device_path, specific_object_path):
        '''used for multi activate, must run one by one'''
        try:
            active = self.dbus_interface.ActivateConnection(connection_path, device_path, specific_object_path)
            print "##",active
            if active:
                self.emit("activate-succeed", connection_path)
                cache.getobject(connection_path).succeed_flag -= 2
                # secret_agent.increase_conn_priority(connection_path)
                return cache.getobject(active)
            else:
                self.emit("activate-failed", connection_path)
                cache.getobject(connection_path).succeed_flag += 1
                # secret_agent.decrease_conn_priority(connection_path)
        except:
            traceback.print_exc()

    def activate_connection_async(self, connection_path, device_path, specific_object_path):
        '''used for only one activate'''
        try:
            active = self.dbus_interface.ActivateConnection(connection_path, device_path, specific_object_path,                                                                                reply_handler = self.activate_finish, error_handler = self.activate_error)
            print "##",active
            if active:
                self.emit("activate-succeed", connection_path)
                cache.getobject(connection_path).succeed_flag -= 2
                # secret_agent.increase_conn_priority(connection_path)
            else:
                self.emit("activate-failed", connection_path)
                cache.getobject(connection_path).succeed_flag += 1
                # secret_agent.decrease_conn_priority(connection_path)
        except:
            traceback.print_exc()

    def activate_finish(self, active_path):
        if active_path:
            active = cache.getobject(active_path)
            self.emit("activate-succeed", active.get_connection().object_path)
            active.get_connection().succeed_flag -= 2
            # secret_agent.increase_conn_priority(active.get_connection().object_path)
            return active
    
    def activate_error(self, *error):
        pass

    def add_and_activate_connection(self, connection_path, device_path, specific_object_path):
        try:
            active = self.dbus_interface.AddAndActivateConnection(connection_path, device_path, specific_object_path)
            if active:
                self.emit("activate-succeed", connection_path)
                cache.getobject(connection_path).succeed_flag -= 2
                # secret_agent.increase_conn_priority(connection_path)
                return cache.getobject(active)
            else:
                self.emit("activate-failed", connection_path)
                cache.getobject(connection_path).succeed_flag += 1
                # secret_agent.decrease_conn_priority(connection_path)
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
            active = cache.getobject(active_path)
            self.emit("activate-succeed", active.get_connection().object_path)
            active.get_connection().succeed_flag -= 2
            # secret_agent.increase_conn_priority(active.get_connection().object_path)
            return active

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
        if self.properties["ActiveConnections"]:
            return map(lambda x: cache.getobject(x), self.properties["ActiveConnections"])
        else:
            return []

    def get_vpn_active_connection(self):
        if self.get_active_connections():
            return filter(lambda x:x.get_vpn() == 1, self.get_active_connections())[0]
        else:
            return []

    def get_wired_active_connection(self):
        if self.get_active_connections():
            return filter(lambda x:x.get_devices()[0] == self.get_wired_device(), self.get_active_connections())[0]
        else:
            return []

    def get_wireless_active_connection(self):
        if self.get_active_connections():
            return filter(lambda x:x.get_devices()[0] == self.get_wireless_device(), self.get_active_connections())[0]
        else:
            return []

    def get_pppoe_active_connection(self):
        pass

    def get_gsm_active_connection(self):
        pass

    def get_cdma_active_connection(self):
        # return filter(lambda x:NMActiveConnection(x).get_devices()[0] == self.get_cdma_device(), self.get_active_connections())[0]
        pass

    ###Signals ###
    def device_added_cb(self, device_object_path):
        # self.devices = self.get_devices()
        # self.emit("device-added", device_object_path)
        pass

    def device_removed_cb(self, device_object_path):
        # self.devices = self.get_devices()
        # self.emit("device-removed", device_object_path)
        pass

    def permisson_changed_cb(self):
        print "permisson_changed_cb triggerd in nmclient"
        self.emit("permission-changed")

    def state_changed_cb(self, state):
        print "network manager state:%s" %state
        self.emit("state-changed", TypeConvert.dbus2py(state))
    
    def properties_changed_cb(self, prop_dict):
        self.init_nmobject_with_properties()

# nmclient = NMClient()


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
