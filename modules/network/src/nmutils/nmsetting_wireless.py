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

from nmsetting import NMSetting
from nmlib.nm_utils import TypeConvert
import dbus

class NMSettingWireless (NMSetting):
    '''NMSettingWireless'''

    def __init__(self):
        NMSetting.__init__(self)
        self.name = "802-11-wireless"
    # def _match_cipher(self, cipher, expected, wpa_flags, rsn_flags, flag):
    #     if not cipher.equals(expected):
    #         return False
    #     elif not wpa_flags & flag or not rsn_flags & flag:
    #         return False
    #     else:
    #         return True

    # def add_seen_bssid(self, bssid):
    #     lower_bssid = bssid.tolower()
    #     if lower_bssid in self.seen_bssids:
    #         pass
    #     else:
    #         self.seen_bssids.append(lower_bssid)

    @property
    def seen_bssids(self):
        if "seen-bssids" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py([TypeConvert.ssid_ascii2string(x) for x in self.prop_dict["seen-bssids"]])

    @seen_bssids.setter
    def seen_bssids(self, new_seen_bssids):
        self.prop_dict["seen-bssids"] = dbus.Array(new_seen_bssids, signature = dbus.Signature('s'))
    
    @property        
    def band(self):
        if "band" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["band"])

    @band.setter
    def band(self, new_band):
        self.prop_dict["band"] = TypeConvert.pyt2_dbus_string(new_band)

    @property
    def bssid(self):
        if "bssid" in self.prop_dict.iterkeys():
            return TypeConvert.ssid_ascii2string(self.prop_dict["bssid"])

    @bssid.setter
    def bssid(self, new_bssid):
        self.prop_dict["bssid"] = TypeConvert.ssid_string2ascii(new_bssid)

    @property
    def channel(self):
        if "channel" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["channel"])
        else:
            return 0

    @channel.setter
    def channel(self,new_channel):
        self.prop_dict["channel"] = TypeConvert.py2_dbus_uint32(new_channel)

    @property
    def cloned_mac_address(self):
        if "cloned-mac-address" in self.prop_dict.iterkeys():
            return TypeConvert.mac_address_array2string(self.prop_dict["cloned-mac-address"])

    @cloned_mac_address.setter
    def cloned_mac_address(self, new_cloned_mac_address):
        self.prop_dict["cloned-mac-address"] = TypeConvert.mac_address_string2array(new_cloned_mac_address)

    @property
    def hidden(self):
        if "hidden" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["hidden"])
        else:
            return False

    @hidden.setter
    def hidden(self, new_hidden):
        self.prop_dict["hidden"] = TypeConvert.py2_dbus_boolean(new_hidden)

    @property
    def mac_address(self):
        if "mac-address" in self.prop_dict.iterkeys():
            return TypeConvert.mac_address_array2string(self.prop_dict["mac-address"])

    @mac_address.setter
    def mac_address(self, new_mac_address):
        self.prop_dict["mac-address"] = TypeConvert.mac_address_string2array(new_mac_address)

    @property
    def mac_address_blacklist(self):
        if "mac-address-blacklist" in self.prop_dict.iterkeys():
            return self.prop_dict["mac-address-blacklist"]

    @mac_address_blacklist.setter
    def mac_address_blacklist(self, new_mac_address_blacklist):
        self.prop_dict["mac-address-blacklist"] = TypeConvert.py2_dbus_array(new_mac_address_blacklist)

    @property
    def mode(self):
        if "mode" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["mode"])

    @mode.setter
    def mode(self, new_mode):
        if new_mode  in ["adhoc","infrastructure"]:
            self.prop_dict["mode"] = new_mode

    @property
    def mtu(self):
        if "mtu" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["mtu"])
        else:
            return 0

    @mtu.setter
    def mtu(self, new_mtu):
        self.prop_dict["mtu"] = TypeConvert.py2_dbus_uint32(new_mtu)

    @property
    def rate(self):
        if "rate" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["rate"])
        else:
            return 0

    @rate.setter
    def rate(self, new_rate):
        self.prop_dict["rate"] = TypeConvert.py2_dbus_uint32(new_rate)

    @property
    def security(self):
        if "security" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["security"])

    @security.setter
    def security(self, new_security):
        self.prop_dict["security"] = TypeConvert.py2_dbus_string(new_security)

    @security.deleter
    def security(self):
        if "security" in self.prop_dict.iterkeys():
            del self.prop_dict["security"]

    @property
    def ssid(self):
        if "ssid" in self.prop_dict.iterkeys():
            return TypeConvert.ssid_ascii2string(self.prop_dict["ssid"])

    @ssid.setter
    def ssid(self, new_ssid):
        self.prop_dict["ssid"] = TypeConvert.ssid_string2ascii(new_ssid)
    
    @property
    def tx_power(self):
        if "tx-power" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["tx-power"])
        else:
            return 0

    @tx_power.setter
    def tx_power(self,new_tx_power):
        self.prop_dict["tx-power"] = TypeConvert.py2_dbus_uint32(new_tx_power)

    def get_num_seen_bssids(self):
        return len(self.seen_bssids)

    def ap_security_compatible(self, s_wireless_serc, ap_flags, ap_wpa, ap_rsn, ap_mode):
        pass

    def adapt_wireless_commit(self):
        if self.prop_dict["mode"] == "infrastructure":
            self.adapt_infrastructure_commit()
        elif self.prop_dict["mode"] == "adhoc":
            self.adapt_adhoc_commit()
        else:
            pass

    def adapt_infrastructure_commit(self):
        for key in self.prop_dict.iterkeys():
            if key not in ["bssid", "cloned-mac-address", "mac-address", "mode",
                           "mtu", "security", "ssid"]:
                del self.prop_dict[key]

    def adapt_adhoc_commit(self):
        '''need limit encrpty method in wireless security'''
        for key in self.prop_dict.iterkeys():
            if key not in ["band","bssid", "channel", "cloned-mac-address", "mac-address", "mode",
                           "mtu", "ssid"]:
                del self.prop_dict[key]
