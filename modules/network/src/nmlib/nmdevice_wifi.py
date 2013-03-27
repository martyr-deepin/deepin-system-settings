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
from nmcache import get_cache
cache = get_cache()
from nm_utils import TypeConvert, nm_alive

nmclient = cache.getobject("/org/freedesktop/NetworkManager")
nm_remote_settings = cache.getobject("/org/freedesktop/NetworkManager/Settings")
print nmclient, nm_remote_settings, "Debug in nmdevice_wifi"

class ThreadWifiAuto(threading.Thread):

    def __init__(self, device_path, connections):
        threading.Thread.__init__(self)
        self.device = cache.get_spec_object(device_path)
        self.conns = connections
        self.run_flag = True

    def run(self):
            for conn in self.conns:
                if self.run_flag:
                    ssid = TypeConvert.ssid_ascii2string(conn.settings_dict["802-11-wireless"]["ssid"])
                    if ssid in self.device.get_ssid_record():
                        try:
                            specific = self.device.get_ap_by_ssid(ssid)
                            active_conn = nmclient.activate_connection(conn.object_path, self.device.object_path, specific.object_path)
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
                        continue
                else:
                    return False

            self.stop_run()

    def stop_run(self):
        self.run_flag = False

class NMDeviceWifi(NMDevice):
    '''NMDeviceWifi'''
        
    __gsignals__  = {
            "access-point-added":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            "access-point-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
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
        self.thread_wifiauto = None

        ###only used for ap added/removed signal
        self.ap_record_dict = {}
        self.init_ap_record_dict()

    def init_ap_record_dict(self):
        try:
            accesspoints_path = self.dbus_method("GetAccessPoints")
            from nmaccesspoint import NMAccessPoint 
            for ap_path in accesspoints_path:
                self.ap_record_dict[ap_path] = NMAccessPoint(ap_path).get_ssid()
        except:
            traceback.print_exc()
            return []

    def device_wifi_disconnect(self):
        if self.thread_wifiauto:
            self.thread_wifiauto.stop_run()
        cache.getobject(self.object_path).nm_device_disconnect()

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
        try:
            ap = self.dbus_method("GetAccessPoints")
            return map(lambda x:cache.getobject(x), TypeConvert.dbus2py(ap))
        except:
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
            conn = sorted(connections, key = lambda x: int(nm_remote_settings.cf.get("conn_priority", x.settings_dict["connection"]["uuid"])), 
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

        wireless_connections = nm_remote_settings.get_wireless_connections()
        if wireless_connections:
            wireless_prio_connections = sorted(nm_remote_settings.get_wireless_connections(),
                                        key = lambda x: int(nm_remote_settings.cf.get("conn_priority", x.settings_dict["connection"]["uuid"])),
                                        reverse = True)

            self.thread_wifiauto = ThreadWifiAuto(self.object_path, wireless_prio_connections)
            self.thread_wifiauto.setDaemon(True)
            self.thread_wifiauto.start()
        else:
            pass

    def update_ap_list(self):
        try:
            ssids = self.get_ssid_record()
            return map(lambda ssid:self.__get_same_ssid_ap(ssid)[0], ssids)
        except:    
            return []

    def update_opt_ap_list(self):
        '''return the ap list whoes item have the most strength signal with the same ssid'''
        try:
            ssids = self.get_ssid_record()
            aps = map(lambda ssid:self.get_ap_by_ssid(ssid), ssids)
            return filter(lambda ap: ap.get_mode() != 1, aps)
        except:    
            return []

    def order_ap_list(self):
        '''order different ssis ap'''
        try:
            return sorted(self.update_opt_ap_list(), key = lambda x:(101 - int(x.get_strength())))
        except:
            return []

    def get_ap_by_ssid(self, ssid):
        '''get the optimal ap according to the given ssid'''
        try:
            ssid_aps = self.__get_same_ssid_ap(ssid)
            return sorted(ssid_aps, key = lambda x:x.get_strength())[-1]
        except:    
            return []

    def get_ssid_record(self):
        '''return the uniquee str ssid of access points'''
        try:
            return list(set(map(lambda x:x.get_ssid(), self.origin_ap_list)))
        except:
            return []

    def __get_same_ssid_ap(self, ssid):
        '''return accesspoints that have the same ssid'''
        try:
            return filter(lambda x:x.get_ssid() == ssid, self.origin_ap_list)
        except:
            return []
    #Signals##
    @nm_alive
    def access_point_added_cb(self, ap_object_path):
        try:
            from nmaccesspoint import NMAccessPoint
            added_ssid = NMAccessPoint(ap_object_path).get_ssid()
    
            if added_ssid not in set(self.ap_record_dict.values()):
                self.origin_ap_list = self.get_access_points()
                self.emit("access-point-added")
                #print ap_object_path, added_ssid
                #cache.clearcache()
                #cache.clear_spec_cache()
            self.ap_record_dict[ap_object_path] = added_ssid
        except:
            traceback.print_exc()

    @nm_alive
    def access_point_removed_cb(self, ap_object_path):
        try:
            removed_ssid = self.ap_record_dict[ap_object_path]
            if len(filter(lambda x: x == removed_ssid, self.ap_record_dict.values())) == 1:
                self.origin_ap_list = self.get_access_points()
                self.emit("access-point-removed")
                #print ap_object_path, removed_ssid
                #cache.clearcache()
                #cache.clear_spec_cache()
            del self.ap_record_dict[ap_object_path]
        except:
            traceback.print_exc()

    @nm_alive
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
