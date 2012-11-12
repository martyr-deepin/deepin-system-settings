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

class NMAccessPoint(NMObject):
    '''NMAccessPoint'''

    def __init__(self, ap_object_path):
        NMObject.__init__(self, ap_object_path, "org.freedesktop.NetworkManager.AccessPoint")
        self.prop_list = ["Flags", "WpaFlags", "RsnFlags", "Ssid", "Frequency", "Mode", "MaxBitrate", "Strength", "HwAddress"]
        self.init_nmobject_with_properties()
        self.bssid = ""

        self.bus().add_signal_receiver(self.properties_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertiesChanged")

    ###Methods###
    def get_flags(self):
        return self.properties["Flags"]

    def get_wpa_flags(self):
        return self.properties["WpaFlags"]

    def get_rsn_flags(self):
        return self.properties["RsnFlags"]

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

    def get_mode(self):
        return self.properties["Mode"]

    def get_max_bitrate(self):
        return self.properties["MaxBitrate"]

    def get_strength(self):
        return self.properties["Strength"]

    def filter_connections (self, connections):
        pass

    def get_hw_address(self):
        return self.properties["HwAddress"]

    def properties_changed_cb(self, prop_dict):
        pass

if __name__ == "__main__":
    nm_access_point = NMAccessPoint("/org/freedesktop/NetworkManager/AccessPoint/840")
    print nm_access_point.properties
