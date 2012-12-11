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
from nm_utils import TypeConvert

a_table = {
     7:5035,
     8:5040,
     9:5045,
    11:5055,
    12:5060,
    16:5080,
    34:5170,
    36:5180,
    38:5190,
    40:5200,
    42:5210,
    44:5220,
    46:5230,
    48:5240,
    50:5250,
    52:5260,
    56:5280,
    58:5290,
    60:5300,
    64:5320,
   100:5500,
   104:5520,
   108:5540,
   112:5560,
   116:5580,
   120:5600,
   124:5620,
   128:5640,
   132:5660,
   136:5680,
   140:5700,
   149:5745,
   152:5760,
   153:5765,
   157:5785,
   160:5800,
   161:5801,
   165:5825,
   183:4915,
   184:4920,
   185:4925,
   187:4935,
   188:4945,
   192:4960,
   196:4980
}

bg_table = { 
    1:2412,
    2:2417,
    3:2422,
    4:2427,
    5:2432,
    6:2437,
    7:2442,
    8:2447,
    9:2452,
    10:2457,
    11:2462,
    12:2467,
    13:2472,
    14:2484
}

class NMAccessPoint(NMObject):
    '''NMAccessPoint'''

    def __init__(self, ap_object_path):
        NMObject.__init__(self, ap_object_path, "org.freedesktop.NetworkManager.AccessPoint")
        self.prop_list = ["Flags", "WpaFlags", "RsnFlags", "Ssid", "Frequency", "Mode", "MaxBitrate", "Strength", "HwAddress"]
        self.init_nmobject_with_properties()
        self.bssid = ""

        self.bus.add_signal_receiver(self.properties_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertiesChanged")

    ###Methods###
    def get_flags(self):
        return self.properties["Flags"]

    def get_wpa_flags(self):
        return self.properties["WpaFlags"]

    def get_rsn_flags(self):
        return self.properties["RsnFlags"]

    def get_key_mgmt(self):
        pass

    def get_ssid (self):
        if self.properties["Ssid"]:
            return TypeConvert.ssid_ascii2string(self.properties["Ssid"])
        else:
            return None

    def get_bytearray_ssid(self):
        return self.properties["Ssid"]

    def get_bssid(self):
        return self.bssid

    def get_frequency(self):
        return self.properties["Frequency"]

    def get_channel(self):
        ###get channel from frequency
        if self.get_frequency() > 4900:
            for key, value in enumerate(a_table):
                if value < self.get_frequency():
                    continue
                else:
                    return key
        else:
            for key, value in enumerate(bg_table):
                if value < self.get_frequency():
                    continue
                else:
                    return key

        return 0
    
    def get_mode(self):
        return self.properties["Mode"]

    def get_max_bitrate(self):
        return self.properties["MaxBitrate"]

    def get_strength(self):
        return self.properties["Strength"]

    def filter_connections (self, connections):
        return filter(lambda x: self.is_connection_valid(x), connections)

    def is_connection_valid(self, connection):
        info_dict = TypeConvert.dbus2py(connection.settings_dict)

        if info_dict["connection"]["type"] != "802-11-wireless":
            return False
        
        if "802-11-wireless" not in info_dict.iterkeys():
            return False

        if self.get_ssid() != info_dict["802-11-wireless"]["ssid"]:
            return False
            
        if self.get_bssid() != None and info_dict["802-11-wireless"]["bssid"] != None:
            pass
        
        if self.get_mode() != None:
            if self.get_mode() == 0 or "mode" not in info_dict["802-11-wireless"].iterkeys():
                return False

            if self.get_mode() == 1 and info_dict["802-11-wireless"]["mode"] !="adhoc":
                return False

            if self.get_mode() == 2 and info_dict["802-11-wireless"]["mode"] != "infrastructure":
                return False

        if self.get_frequency() > 0:
            if info_dict["802-11-wireless"]["band"] == "a":
                if self.get_frequency() < 4915 or self.get_frequency() > 5825:
                    return False

            if info_dict["802-11-wireless"]["band"] == "bg":
                if self.get_frequency() < 2412 or self.get_frequency() > 2484:
                    return False

            if "channel" in info_dict["802-11-wireless"].iterkeys():
                if self.get_channel() != info_dict["802-11-wireless"]["channel"]:
                    return False

        ###assert wireless security
        if not "802-11-wireless-security" in info_dict.iterkeys():
            if self.get_flags() ==1 or self.get_wpa_flags() !=0 or self.get_rsn_flags() != 0:
                return False
        else:
            if "key-mgmt" not in info_dict["802-11-wireless-security"].iterkeys():
                return False

            ###static wep
            elif info_dict["802-11-wireless-security"]["key-mgmt"] == "none":
                if self.get_flags() == 0 or self.get_wpa_flags() != 0 or self.get_rsn_flags() != 0:
                    return False
                return True
            ###adhoc wpa    
            elif info_dict["802-11-wireless-security"]["key-mgmt"] == "wpa-none":
                if self.get_mode() != 1:
                    return False
                return True
            
            else:
                if self.get_mode() != 2:
                    return False
                
                ###dynamic wep or leap
                if self.info_dict["802-11-wireless-security"]["key-mgmt"] == "ieee8021x":
                    if self.get_flags() == 0:
                        return False

                    if self.get_wpa_flags() != 0:
                        if self.get_wpa_flags() != 200:
                            return False

                        if self.get_wpa_flags() not in [1, 2, 10, 20]:
                            return False

                        pass
                        pass
                        pass
                        pass


                elif self.info_dict["802-11-wireless-security"]["key-mgmt"] == "wpa-psk":
                    if self.get_wpa_flags() != 100 and self.get_rsn_flags() != 100:
                        return False
                
                elif self.info_dict["802-11-wireless-security"]["key-mgmt"] == "wpa-eap":
                    if self.get_wpa_flags() != 200 and self.get_rsn_flags() != 200:
                        return False
        return True        

                
    def get_hw_address(self):
        return self.properties["HwAddress"]

    def properties_changed_cb(self, prop_dict):
        pass

if __name__ == "__main__":
    nm_access_point = NMAccessPoint("/org/freedesktop/NetworkManager/AccessPoint/840")
    print nm_access_point.properties
