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
import threading
import time
from nmdevice import NMDevice
from nmcache import cache
from nm_utils import TypeConvert

nmclient = cache.getobject("/org/freedesktop/NetworkManager")
nm_remote_settings = cache.getobject("/org/freedesktop/NetworkManager/Settings")

class NMDeviceWifi(NMDevice):
    '''NMDeviceWifi'''
        
    __gsignals__  = {
            "access-point-added":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
            "access-point-removed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
            }

    def __init__(self, wifi_device_object_path):
        NMDevice.__init__(self, wifi_device_object_path, "org.freedesktop.NetworkManager.Device.Wireless")
        self.prop_list = ["HwAddress", "PermHwAddress", "Mode", "Bitrate", "ActiveAccessPoint", "WirelessCapabilities"]

        self.bus.add_signal_receiver(self.access_point_added_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "AccessPointAdded")

        self.bus.add_signal_receiver(self.access_point_removed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "AccessPointRemoved")

        self.bus.add_signal_receiver(self.properties_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertiesChanged")

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

    def connection_compatible(self, connection):
        info_dict = TypeConvert.dbus2py(connection.settings_dict)

        if info_dict["connection"]["type"] != "802-11-wireless":
            return False
        
        if "802-11-wireless" not in info_dict.iterkeys():
            return False

        if self.get_perm_hw_address():
            if "mac-address" in info_dict.iterkeys():
                if self.get_perm_hw_address() != info_dict["802-11-wireless"]["mac-address"]:
                    return False

        if "802-11-wireless-security" in info_dict.iterkeys():
            if info_dict["802-11-wireless-security"]["key-mgmt"] in ["wpa-none", "wpa-psk", "wpa-eap"]:
                caps = self.get_capabilities()
                if not caps & 4 or not caps & 8 or not caps & 16 or not caps & 32:
                    return False

                protos = info_dict["802-11-wireless-security"]["proto"]
                if protos:
                    if "rsn" in protos and "wpa" not in protos:
                        if not caps & 8 or not caps & 32:
                            return False
        return True        

    def get_access_points(self):
        ap = self.dbus_method("GetAccessPoints")
        if ap:
            return map(lambda x:cache.getobject(x), TypeConvert.dbus2py(ap))
        else:
            return []

    def active_ssid_connection(self, ssid):
        '''try only one connection now'''
        if cache.getobject(self.object_path).is_active():
            conn = cache.getobject(self.object_path).get_active_connection().get_connection()
            if TypeConvert.ssid_ascii2string(conn.settings_dict["802-11-wireless"]["ssid"])== ssid:
                return None
        else:
            pass

        connections = nm_remote_settings.get_ssid_associate_connections(ssid)
        if connections:
            conn = sorted(connections, key = lambda x:nm_remote_settings.cf.get("conn_priority", x.settings_dict["connection"]["uuid"]), 
                    reverse = True)[0]
            try:
                specific = self.get_ap_by_ssid(ssid)
                nmclient.activate_connection(conn.object_path, self.object_path, specific.object_path)
                if cache.getobject(self.object_path).is_active():
                    return None
                else:
                    return conn
            except:
                return conn
        else:
            return nm_remote_settings.new_wireless_connection(ssid, None)

    def auto_connect(self):
        if cache.getobject(self.object_path).is_active():
            return True
        if cache.getobject(self.object_path).get_state() < 30:
            return False

        print "wireless auto connect"

        wireless_connections = nm_remote_settings.get_wireless_connections()
        if wireless_connections:
            wireless_prio_connections = sorted(nm_remote_settings.get_wireless_connections(),
                                            key = lambda x: nm_remote_settings.cf.get("conn_priority", x.settings_dict["connection"]["uuid"]),
                                            reverse = True)

        #######Please update ssid record first#######################
########################################################################
###########################################################################

            import threading

            def active_connection():
                for conn in wireless_prio_connections:
                    ssid = TypeConvert.ssid_ascii2string(conn.settings_dict["802-11-wireless"]["ssid"])
                    print ssid
                    if ssid in self.__get_ssid_record():
                        try:
                            specific = self.get_ap_by_ssid(ssid)
                            active_conn = nmclient.activate_connection(conn.object_path, self.object_path, specific.object_path)
                            while(active_conn.get_state() == 1):
                                time.sleep(1)
                            if active_conn.get_state() == 2:
                                return True
                            else:
                                continue
                        except:
                            pass
                    else:
                        continue
            t = threading.Thread(target = active_connection)
            t.setDaemon(True)
            t.start()

        else:
            pass

    def update_ap_list(self):
        try:
            ssids = self.__get_ssid_record()
            if ssids:
                return map(lambda ssid:self.__get_same_ssid_ap(ssid)[0], ssids)
        except:    
            return []

    def update_opt_ap_list(self):
        '''return the ap list whoes item have the most strength signal with the same ssid'''
        try:
            ssids = self.__get_ssid_record()
            if ssids:
                aps = map(lambda ssid:self.get_ap_by_ssid(ssid), ssids)
                return filter(lambda ap: ap.get_mode() != 1, aps)
        except:    
            return []

    def order_ap_list(self):
        '''order different ssis ap'''
        try:
            aps = self.update_opt_ap_list()
            if aps:
                return sorted(self.update_opt_ap_list(), key = lambda x:(101 - int(x.get_strength())))
        except:
            return []

    def get_ap_by_ssid(self, ssid):
        '''get the optimal ap according to the given ssid'''
        try:
            ssid_aps = self.__get_same_ssid_ap(ssid)
            if ssid_aps:
                return sorted(ssid_aps, key = lambda x:x.get_strength())[-1]
        except:    
            return []

    def __get_ssid_record(self):
        '''return the uniquee str ssid of access points'''
        try:
            aps = self.origin_ap_list
            if aps:
                return list(set(map(lambda x:x.get_ssid(), self.origin_ap_list)))
        except:
            return []

    def __get_same_ssid_ap(self, ssid):
        '''return accesspoints that have the same ssid'''
        try:
            if self.origin_ap_list:
                return filter(lambda x:x.get_ssid() == ssid, self.origin_ap_list)
        except:
            return []
    #Signals##
    def access_point_added_cb(self, ap_object_path):
        # self.origin_ap_list = self.get_access_points()
        # self.update_ap_list()
        # self.emit("access-point-added", cache.getobject(ap_object_path))
        cache.clearcache()
        cache.clear_spec_cache()
        pass

    def access_point_removed_cb(self, ap_object_path):
        # self.origin_ap_list = self.get_access_points()
        # self.update_ap_list()
        # self.emit("access-point-removed", cache.getobject(ap_object_path))
        cache.clearcache()
        cache.clear_spec_cache()
        pass

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
