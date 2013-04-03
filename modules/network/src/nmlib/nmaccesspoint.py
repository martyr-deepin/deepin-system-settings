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

        self.match = self.bus.add_signal_receiver(self.properties_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertiesChanged")

    def remove_signals(self):
        try:
            self.bus.remove_signal_receiver(self.match, dbus_interface = self.object_interface,
                                         path = self.object_path, signal_name = "PropertiesChanged")
        except:
            print "remove signals failed"


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

    def get_security_method(self):
        NM_802_11_AP_FLAGS_PRIVACY = 0x1
        NM_802_11_AP_SEC_NONE = 0x0
        NM_802_11_AP_SEC_KEY_MGMT_802_1X = 0x200

        wpa_flags = self.get_wpa_flags()
        rsn_flags = self.get_rsn_flags()
        flags = self.get_flags()

        if flags & NM_802_11_AP_FLAGS_PRIVACY:
            if wpa_flags == NM_802_11_AP_SEC_NONE and rsn_flags == NM_802_11_AP_SEC_NONE :
                return "wep" 
            elif not (wpa_flags & NM_802_11_AP_SEC_KEY_MGMT_802_1X ) and not (rsn_flags & NM_802_11_AP_SEC_KEY_MGMT_802_1X) :
                return "wpa" 
            else:
                return "enterprise"
        else:
            return "none"

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
        if self.get_flags() != None:
            flags = self.get_flags()
        else:
            flags = 0

        if self.get_wpa_flags() != None:
            wpa_flags = self.get_wpa_flags()
        else:
            wpa_flags = 0

        if self.get_rsn_flags() != None:
            rsn_flags = self.get_rsn_flags()
        else:
            rsn_flags = 0

        if not "802-11-wireless-security" in info_dict.iterkeys():
            if flags == 1 or wpa_flags !=0 or rsn_flags != 0:
                return False

            return True
        else:
            if "key-mgmt" not in info_dict["802-11-wireless-security"].iterkeys():
                return False

            ###static wep
            elif info_dict["802-11-wireless-security"]["key-mgmt"] == "none":
                if not flags & 1 or wpa_flags != 0 or rsn_flags != 0:
                    return False
                return True

            ###adhoc wpa    
            elif info_dict["802-11-wireless-security"]["key-mgmt"] == "wpa-none":
                if self.get_mode() != 1:
                    return False
                return True

            # stuff after this point requires infrastructure
            else:
                if self.get_mode() != 2:
                    return False
                
                ###dynamic wep or leap
                if self.info_dict["802-11-wireless-security"]["key-mgmt"] == "ieee8021x":
                    if not flags & 1:
                        return False

                # if the ap is advertising a WPA IE, make sure it supports WEP ciphers
                    if wpa_flags != 0:
                        if not wpa_flags & 512:
                            return False

                        # quick check; can't use AP if it doesn't support at least one
			# WEP cipher in both pairwise and group suites.
                        if not (wpa_flags & (1 | 2)) or not (wpa_flags & (16 | 32)):
                            return False

			# Match at least one pairwise cipher with AP's capability if the
			# wireless-security setting explicitly lists pairwise ciphers
                        if "pairwise" in self.info_dict["802-11-wireless-security"].iterkeys():
                            if self.info_dict["802-11-wireless-security"]["pairwise"]:
                                found = False
                                for cipher in self.info_dict["802-11-wireless-security"]["pairwise"]:
                                    if self.match_cipher(cipher, "wep40", wpa_flags, wpa_flags, 1):
                                        found = True
                                        break
                                    if self.match_cipher(cipher, "wep104", wpa_flags, wpa_flags, 2):
                                        found = True
                                        break
                                if not found:
                                    return False

                            else:
                                pass
                        else:
                            pass

			# Match at least one group cipher with AP's capability if the
			# wireless-security setting explicitly lists group ciphers
                        if "group" in self.info_dict["802-11-wireless-security"].iterkeys():
                            if self.info_dict["802-11-wireless-security"]["group"]:
                                found = False
                                for cipher in self.info_dict["802-11-wireless-security"]["group"]:
                                    if self.match_cipher(cipher, "wep40", wpa_flags, wpa_flags, 16):
                                        found = True
                                        break
                                    if self.match_cipher(cipher, "wep104", wpa_flags, wpa_flags, 32):
                                        found = True
                                        break
                                if not found:
                                    return False
                            else:
                                pass
                        else:
                            pass

                    return True

                # WPA[2]-PSK and WPA[2] Enterprise 
                elif self.info_dict["802-11-wireless-security"]["key-mgmt"] == "wpa-psk" or "wpa-eap":
                    if self.info_dict["802-11-wireless-security"]["key-mgmt"] == "wpa-psk":
                        if not (wpa_flags & 256) and not (rsn_flags & 256):
                            return False
                
                    elif self.info_dict["802-11-wireless-security"]["key-mgmt"] == "wpa-eap":
                        if not (wpa_flags & 512) and not (rsn_flags & 512):
                            return False

                 #   FIXME: should handle WPA and RSN separately here to ensure that
		 #   if the Connection only uses WPA we don't match a cipher against
		 #   the AP's RSN IE instead

	         #   Match at least one pairwise cipher with AP's capability if the
		 #   wireless-security setting explicitly lists pairwise ciphers
                    if "pairwise" in self.info_dict["802-11-wireless-security"].iterkeys():
                        if self.info_dict["802-11-wireless-security"]["pairwise"]:
                            found = False
                            for cipher in self.info_dict["802-11-wireless-security"]["pairwise"]:
                                if self.match_cipher(cipher, "tkip", wpa_flags, rsn_flags, 8):
                                    found = True
                                    break
                                if self.match_cipher(cipher, "ccmp", wpa_flags, rsn_flags, 10):
                                    found = True
                                    break

                            if not found:
                                return False

                        else:
                            pass
                    else:
                        pass

		#    Match at least one group cipher with AP's capability if the
		#    wireless-security setting explicitly lists group ciphers
                    if "group" in self.info_dict["802-11-wireless-security"].iterkeys():
                        if self.info_dict["802-11-wireless-security"]["group"]:
                            found = False
                            for cipher in self.info_dict["802-11-wireless-security"]["group"]:
                                if self.match_cipher(cipher, "wep40", wpa_flags, rsn_flags, 16):
                                    found = True
                                    break
                                if self.match_cipher(cipher, "wep104", wpa_flags, rsn_flags, 32):
                                    found = True
                                    break
                                if self.match_cipher(cipher, "tkip", wpa_flags, rsn_flags, 64):
                                    found = True
                                    break
                                if self.match_cipher(cipher, "ccmp", wpa_flags,rsn_flags, 128):
                                    found = True
                                    break

                            if not found:
                                return False
                        else:
                            pass
                    else:
                        pass

                    return True    
        return True        

    def match_cipher(self, cipher, expected, wpa_flags, rsn_flags, flag):
        if cipher != expected:
            return False
        
        if not (wpa_flags & flag) and not (rsn_flags & flag):
            return False

        return True

    def get_hw_address(self):
        return self.properties["HwAddress"]

    def properties_changed_cb(self, prop_dict):
        self.init_nmobject_with_properties()
if __name__ == "__main__":
    #nm_access_point = NMAccessPoint("/org/freedesktop/NetworkManager/AccessPoint/840")
    #print nm_access_point.properties
    from nmclient import NMClient
    from nmdevice_wifi import NMDeviceWifi
    nmclient = NMClient()
    wifi = NMDeviceWifi(nmclient.get_wireless_device().object_path)
    for ap in wifi.get_access_points():
        if ap.get_ssid() == "daydayup" or ap.get_ssid() == "DeepinWork":
            print ap.get_ssid()
            print ap.object_path
            print "security", ap.get_security_method()

    from nmdevice import NMDevice
    print NMDevice(wifi.object_path).get_active_connection().get_specific_object()
