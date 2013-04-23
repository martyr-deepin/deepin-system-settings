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

from nmobject import NMObject
from nmcache import get_cache
import time
import threading

class ThreadVPNAuto(threading.Thread):

    def __init__(self, active_path, connections):
        threading.Thread.__init__(self)
        self.activeconn = get_cache().getobject(active_path)
        self.conns = connections
        self.run_flag = True

    def run(self):
        for conn in self.conns:
            if self.run_flag:
                try:
                    nmclient = get_cache().getobject("/org/freedesktop/NetworkManager")
                    active_conn = nmclient.activate_connection(conn.object_path, 
                                                                self.activeconn.properties["Devices"][0],
                                                                self.activeconn.object_path)
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
                break
        self.stop_run()

    def stop_run(self):
        self.run_flag = False


class NMActiveConnection(NMObject):
    '''NMActiveConnection'''

    def __init__(self, active_connection_object_path, interface = "org.freedesktop.NetworkManager.Connection.Active"):
        NMObject.__init__(self, active_connection_object_path, interface)

        self.prop_list = ["Vpn", "Master", "Uuid", "Connection", "SpecificObject", "Devices", "State", "Default", "Default6"]
        self.init_nmobject_with_properties()
        self.bus.add_signal_receiver(self.properties_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertiesChanged")

        self.thread_vpnauto = None

    def device_vpn_disconnect(self):
        if self.thread_vpnauto:
            self.thread_vpnauto.stop_run()

    def get_vpn(self):
        return self.properties["Vpn"]

    def get_master(self):
        return self.properties["Master"]

    def get_uuid(self):
        return self.properties["Uuid"]

    def get_connection(self):
        return get_cache().getobject(self.properties["Connection"])

    def get_specific_object(self):
        return self.properties["SpecificObject"]

    def get_devices(self):
        try:
            return map(lambda x:get_cache().getobject(x), self.properties["Devices"])
        except:
            return []

    def get_state(self):
        return self.properties["State"]

    def get_default(self):
        return self.properties["Default"]
    
    def get_default6(self):
        return self.properties["Default6"]

    def vpn_auto_connect(self):
        nm_remote_settings = get_cache().getobject("/org/freedesktop/NetworkManager/Settings")
        if self.get_state() != 2:
            return False
        elif nm_remote_settings.get_vpn_connections():
            vpn_prio_connections = sorted(nm_remote_settings.get_vpn_connections(),
                                        key = lambda x:int(nm_remote_settings.cf.get("conn_priority", x.settings_dict["connection"]["uuid"])),
                                        reverse = True)

            self.thread_vpnauto = ThreadVPNAuto(self.object_path, vpn_prio_connections)
            self.thread_vpnauto.setDaemon(True)
            self.thread_vpnauto.start()

    ###Signals###
    def properties_changed_cb(self, prop_dict):
        self.init_nmobject_with_properties()

if __name__ == "__main__":
    nm_active_connection = NMActiveConnection("/org/freedesktop/NetworkManager/ActiveConnection/4");
    print nm_active_connection.properties
