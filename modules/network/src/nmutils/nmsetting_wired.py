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
from nmlib.nmconstant import NMSettingParamFlags as pflag
from nmlib.nm_utils import TypeConvert
import dbus

class NMSettingWired (NMSetting):
    '''NMSettingWired'''

    def __init__(self):
        NMSetting.__init__(self)
        self.name = "802-3-ethernet"

    @property    
    def auto_negotiate(self):
        if "auto-negotiate" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["auto-negotiate"])
        else:
            return True

    @auto_negotiate.setter
    def auto_negotiate(self, new_auto_negotiate):
        self.prop_dict["auto_negotiate"] = TypeConvert.py2_dbus_boolean(new_auto_negotiate)

    @property
    def cloned_mac_address(self):
        if "cloned-mac-address" in self.prop_dict.iterkeys():
            return TypeConvert.mac_address_array2string(self.prop_dict["cloned-mac-address"])

    @cloned_mac_address.setter
    def cloned_mac_address(self, new_cloned_mac_address):
        self.prop_dict["cloned-mac-address"] = TypeConvert.mac_address_string2array(new_cloned_mac_address)

    @property
    def mac_address(self):
        if "mac-address" in self.prop_dict.iterkeys():
            return TypeConvert.mac_address_array2string(self.prop_dict["mac-address"])

    @mac_address.setter
    def mac_address(self, new_mac_address):
        self.prop_dict["mac-address"] = TypeConvert.mac_address_string2array(new_mac_address)

    @property
    def duplex(self):
        if "duplex" in self.prop_dict.iterkeys():
            return self.prop_dict["duplex"]

    @duplex.setter
    def duplex(self, new_duplex):
        self.prop_dict["duplex"] = TypeConvert.py2_dbus_string(new_duplex)

    ###need detail handle###    
    @property
    def mac_address_blacklist(self):
        if "mac-address-blacklist" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["mac-address-blacklist"])

    @mac_address_blacklist.setter
    def mac_address_blacklist(self, new_mac_address_blacklist):
        self.prop_dict["mac-address-blacklist"] = TypeConvert.py2_dbus_array(new_mac_address_blacklist)

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
    def port(self):
        if "port" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["port"])

    @port.setter
    def port(self, new_port):
        self.prop_dict["port"] = TypeConvert.py2_dbus_string(new_port)

    @property
    def s390_nettype(self):
        if "s390-nettype" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["s390-nettype"])

    @s390_nettype.setter
    def s390_nettype(self, new_s390_nettype):
        self.prop_dict["s390-nettype"] = TypeConvert.py2_dbus_string(new_s390_nettype)

    @property
    def s390_options(self):
        if "s390-options" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["s390-options"])

    @s390_options.setter
    def s390_options(self, new_s390_options):
        self.prop_dict["s390-options"] = TypeConvert.py2_dbus_dictionary(new_s390_options)

    def clear_s390_options(self):
        self.prop_dict["s390-options"] = dbus.Dictionary({}, signature = dbus.Signature('ss'))

    def add_s390_option(self, key, item):
        if key not in self.WiredValid().valid_s390_opts:
            print "invalid key "
            return False
        elif key in self.s390_options.keys():
            print "key already in s390_options"
            return False
        elif len(item) < 0 or len(item) > 200:
            print "invalid item "
            return False
        else:
            self.s390_options[key] = item
            return True

    def get_num_s390_options(self):
        return len(self._s390_options)

    def get_s390_options(self, idx):
        if idx > self.get_num_s390_options() or idx < 0:
            print "invalid index"
            return False
        else:
            out_key = self._s390_options.keys()[idx]
            out_value = self._s390_options[out_key]
            return (out_key, out_value)

    def remove_s390_option(self, key):
        if key not in self.s390_options.keys():
            pass
        else:
            del self.s390_options[key]

    def get_s390_option_by_key(self, key):
        if key in self.s390_options.keys():
            return self.s390_options[key]
        else:
            print "the key :%s is not in s390_options " % key

    @property        
    def s390_subchannels(self):
        if "s390-subchannels" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["s390-subchannels"])

    @s390_subchannels.setter
    def s390_subchannels(self, new_s390_subchannels):
        self.prop_dict["s390-subchannels"] = TypeConvert.py2_dbus_array(new_s390_subchannels)

    @property
    def speed(self):
        if "speed" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["speed"])
        else:
            return 0

    @speed.setter
    def speed(self, new_speed):
        self.prop_dict["speed"] = TypeConvert.py2_dbus_uint32(new_speed)
            
    def __verify(self):
        valid = self.WiredValid()
        if self.port and self.port not in valid.valid_ports:
            return False
        if self.duplex and self.duplex not in valid.valid_duplex:
            return False
        else:
            return True

    class WiredValid:
        def __init__(self):
            self.valid_s390_opts = [
        	"portno", "layer2", "portname", "protocol", "priority_queueing",
                "buffer_count", "isolation", "total", "inter", "inter_jumbo", "route4",
                "route6", "fake_broadcast", "broadcast_mode", "canonical_macaddr",
                "checksupynm.mm.ng", "sniffer", "large_send", "ipato_enable", "ipato_invert4",
                "ipato_add4", "ipato_invert6", "ipato_add6", "vipa_add4", "vipa_add6",
                "rxip_add4", "rxip_add6", "lancmd_timeout", "ctcprot"
                ]    
            self.valid_ports = ["tp", "aui", "bnc", "mii"]
            self.valid_duplex = ["half", "full"]
            self.valid_nettype = ["qeth", "lcs", "ctc"]

