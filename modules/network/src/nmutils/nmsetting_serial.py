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
from nmlib.nmconstant import NMSettingParamFlags as pflag

class NMSettingSerial (NMSetting):
    '''NMSettingSerial'''

    def __init__(self):
        NMSetting.__init__(self)
        self.name = "serial"
        
    @property    
    def baud(self):
        if "baud" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["baud"])

    @baud.setter
    def baud(self, new_baud):
        self.prop_dict["baud"] = TypeConvert.py2_dbus_uint32(new_baud)

    @property
    def bits(self):
        if "bits" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["bits"])
    
    @bits.setter
    def bits(self, new_bits):
        self.prop_dict["bits"] = TypeConvert.py2_dbus_uint32(new_bits)
    
    @property
    def parity(self):
        if "parity" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["parity"])

    @parity.setter
    def parity(self, new_parity):
        self.prop_dict["parity"] = TypeConvert.py2_dbus_string(new_parity)

    @property
    def stopbits(self):
        if "stopbits" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["stopbits"])

    @stopbits.setter
    def stopbits(self, new_stopbits):
        self.prop_dict["stopbits"] = TypeConvert.py2_dbus_uint32(new_stopbits)

    @property
    def send_delay(self):
        if "send-delay" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["send-delay"])

    @send_delay.setter
    def send_delay(self, new_send_delay):
        self.prop_dict["send-delay"] = TypeConvert.py2_dbus_uint64(new_send_delay)

