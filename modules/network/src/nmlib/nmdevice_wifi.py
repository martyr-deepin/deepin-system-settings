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
import traceback
from nmdevice import NMDevice
from nmcache import cache
from nm_utils import TypeConvert
from nmclient import nmclient
from nm_remote_settings import nm_remote_settings

class NMDeviceWifi(NMDevice):
    '''NMDeviceWifi'''
        
    __gsignals__  = {
            "access-point-added":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
            "access-point-removed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
            "try-ssid-begin":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
            "try-ssid-end":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
            }

    def __init__(self, wifi_device_object_path):
        NMDevice.__init__(self, wifi_device_object_path, "org.freedesktop.NetworkManager.Device.Wireless")
        self.prop_list = ["HwAddress", "PermHwAddress", "Mode", "Bitrate", "ActiveAccessPoint", "WirelessCapabilities"]

        self.bus.add_signal_receiver(self.access_point_added_cb, dbus_interface = self.object_interface, signal_name = "AccessPointAdded")
        self.bus.add_signal_receiver(self.access_point_removed_cb, dbus_interface = self.object_interface, signal_name = "AccessPointRemoved")
        self.bus.add_signal_receiver(self.properties_changed_cb, dbus_interface = self.object_interface, signal_name = "PropertiesChanged")

        self.init_nmobject_with_properties()
        self.origin_ap_list = self.get_access_points()

    def get_hw_address(self):
        return self.properties["HwAddress"]
    
    def get_perm_hw_address(self):
        return self.properties["PermHwAddress"]

    def get_mode(self):
        return self.properties["Mode"]

    def get_bitrate(self):
        return self.properties["Bitrate"]

    def get_active_access_point(self):
        '''return active access point object'''
        return cache.getobject(self.properties["ActiveAccessPoint"])
        
    def get_capabilities(self):
        return self.properties["WirelessCapabilities"]

    def get_access_points(self):
        return map(lambda x:cache.getobject(x), TypeConvert.dbus2py(self.dbus_method("GetAccessPoints")))

    def get_access_points_async(self):
        try:
            self.dbus_interface.GetAccessPoints(reply_handler = self.get_ap_finish, error_handler = self.get_ap_error)
        except:
            traceback.print_exc()

    def get_ap_finish(self, result):    
        self.origin_ap_list = map(lambda x:cache.getobject(x), TypeConvert.dbus2py(result))

    def get_ap_error(self, error):
        print "get access points failed!\n"
        print error

    def auto_connect(self):
        if cache.getobject(self.object_path).is_active():
            return True
        if cache.getobject(self.object_path).get_state() < 30:
            return False
        # wireless_connections = nm_remote_settings.get_wireless_connections()
        # wireless_connections = sorted(nm_remote_settings.get_wireless_connections(), key = lambda x:x.succeed_flag)
        from nm_secret_agent import secret_agent
        wireless_connections = sorted(nm_remote_settings.get_wireless_connections(),
                                      key = lambda x:secret_agent.get_conn_priority(x.object_path))

        if len(wireless_connections) != 0:
            for conn in wireless_connections:
                ssid = conn.get_setting("802-11-wireless").ssid
                if ssid not in self.__get_ssid_record():
                    continue
                else:
                    try:
                        specific = self.get_ap_by_ssid(ssid)
                        self.emit("try-ssid-begin", specific)
                        nmclient.activate_connection(conn.object_path, self.object_path, specific.object_path)
                        if cache.getobject(self.object_path).is_active():
                            self.emit("try-ssid-end", specific)
                            return True
                        else:
                            self.emit("try-ssid-end", specific)
                            continue
                    except:
                        continue
            else:
                return False
        else:
            return False

    def update_ap_list(self):
        return map(lambda ssid:self.__get_same_ssid_ap(ssid)[0], self.__get_ssid_record())

    def update_opt_ap_list(self):
        '''return the ap list whoes item have the most strength signal with the same ssid'''
        return map(lambda ssid:self.get_ap_by_ssid(ssid), self.__get_ssid_record())

    def order_ap_list(self):
        '''order different ssis ap'''
        return sorted(self.update_opt_ap_list(), key = lambda x:(101 - int(x.get_strength())))

    def get_ap_by_ssid(self, ssid):
        return sorted(self.__get_same_ssid_ap(ssid), key = lambda x:x.get_strength())[-1]

    def __get_ssid_record(self):
        return list(set(map(lambda x:x.get_ssid(), self.origin_ap_list)))

    def __get_same_ssid_ap(self, ssid):
        return filter(lambda x:x.get_ssid() == ssid, self.origin_ap_list)

    #Signals##
    def access_point_added_cb(self, ap_object_path):
        self.origin_ap_list = self.get_access_points()
        self.update_ap_list()
        self.emit("access-point-added", cache.getobject(ap_object_path))

    def access_point_removed_cb(self, ap_object_path):
        self.origin_ap_list = self.get_access_points()
        self.update_ap_list()
        self.emit("access-point-removed", cache.getobject(ap_object_path))

    def properties_changed_cb(self, prop_dict):
        self.init_nmobject_with_properties()

if __name__ == "__main__":
    wifi_device = NMDeviceWifi("/org/freedesktop/NetworkManager/Devices/0")
    # print wifi_device.update_ap_list()
    # for ap in wifi_device.update_ap_list():
    #     if ap.get_ssid() == "CMCC":
    #         print ap.get_strength()

    # print wifi_device.get_ap_by_ssid("CMCC")
    # print wifi_device.get_ap_by_ssid("CMCC").get_strength()
    # wifi_device.get_access_points_async()
    # print wifi_device.order_ap_list()
    # gobject.MainLoop().run()
