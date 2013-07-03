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

from nmdevice import NMDevice
from nmcache import get_cache
import time
import threading
from nm_utils import TypeConvert

class ThreadWiredAuto(threading.Thread):

    def __init__(self, device_path, connections):
        threading.Thread.__init__(self)
        self.device = get_cache().get_spec_object(device_path)
        self.conns = connections
        self.run_flag = True

    def run(self):
        for conn in self.conns:
            if self.run_flag:
                if "mac-address" in conn.settings_dict["802-3-ethernet"].iterkeys():
                    if TypeConvert.dbus2py(conn.settings_dict["802-3-ethernet"]["mac-address"]) != self.device.get_hw_address():
                            print "connection mac address doesn't match the device"
                            continue
                    else:
                        pass
                try:
                    nmclient = get_cache().getobject("/org/freedesktop/NetworkManager")
                    active_conn = nmclient.activate_connection(conn.object_path, self.device.object_path, "/")

                    while(active_conn.get_state() == 1 and self.run_flag):
                        time.sleep(1)

                    if active_conn.get_state() == 2:
                        self.stop_run()
                        return True
                    else:
                        continue
                except:
                    pass
            else:
                return True
        self.stop_run()
        return True

    def stop_run(self):
        self.run_flag = False

class NMDeviceEthernet(NMDevice):
    '''NMDeviceEthernet'''
    def __init__(self, ethernet_device_object_path):
        NMDevice.__init__(self, ethernet_device_object_path, "org.freedesktop.NetworkManager.Device.Wired")
        self.prop_list = ["Carrier", "HwAddress", "PermHwAddress", "Speed"]
        self.init_nmobject_with_properties()
        self.bus.add_signal_receiver(self.properties_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertiesChanged")

        self.thread_wiredauto = None
        self.thread_dslauto = None

    def remove_signals(self):
        pass

    ###Methods###
    def device_wired_disconnect(self):
        if self.thread_wiredauto:
            self.thread_wiredauto.stop_run()
        get_cache().getobject(self.object_path).nm_device_disconnect()

    def device_dsl_disconnect(self):
        if self.thread_dslauto:
            self.thread_dslauto.stop_run()

    def get_carrier(self):
        return self.properties["Carrier"]

    def get_hw_address(self):
        return self.properties["HwAddress"]

    def get_perm_hw_address(self):
        return self.properties["PermHwAddress"]

    def get_speed(self):
        return self.properties["Speed"]

    def auto_connect(self):
        if get_cache().getobject(self.object_path).is_active():
            return True
        if get_cache().getobject(self.object_path).get_state() < 30:
            return False

        nm_remote_settings = get_cache().getobject("/org/freedesktop/NetworkManager/Settings")
        if nm_remote_settings.get_wired_connections():

            wired_prio_connections = sorted(nm_remote_settings.get_wired_connections(),
                                    key = lambda x: int(nm_remote_settings.cf.get("conn_priority", x.settings_dict["connection"]["uuid"])),
                                    reverse = True)

            self.thread_wiredauto = ThreadWiredAuto(self.object_path, wired_prio_connections)
            self.thread_wiredauto.setDaemon(True)
            self.thread_wiredauto.start()

        else:
            try:
                nmconn = nm_remote_settings.new_wired_connection()
                conn = nm_remote_settings.new_connection_finish(nmconn.settings_dict)
                nmclient = get_cache().getobject("/org/freedesktop/NetworkManager")
                nmclient.activate_connection(conn.object_path, self.object_path, "/")
            except:
                return False

    def dsl_auto_connect(self):
        nm_remote_settings = get_cache().getobject("/org/freedesktop/NetworkManager/Settings")
        if not get_cache().getobject(self.object_path).is_active():
            return False

        elif not nm_remote_settings.get_pppoe_connections():
            return False
        else:
            pppoe_prio_connections = sorted(nm_remote_settings.get_pppoe_connections(),
                                    key = lambda x: int(nm_remote_settings.cf.get("conn_priority", x.settings_dict["connection"]["uuid"])),
                                    reverse = True)

            self.thread_dslauto = ThreadWiredAuto(self.object_path, pppoe_prio_connections)
            self.thread_dslauto.setDaemon(True)
            self.thread_dslauto.start()

    def properties_changed_cb(self, prop_dict):
        pass
        #self.init_nmobject_with_properties()

if __name__ == "__main__":
    ethernet_device = NMDeviceEthernet ("/org/freedesktop/NetworkManager/Devices/0")
    print ethernet_device.properties
