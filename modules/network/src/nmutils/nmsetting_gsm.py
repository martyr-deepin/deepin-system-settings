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

class NMSettingGsm (NMSetting):
    '''NMSettingGsm'''

    def __init__(self):
        NMSetting.__init__(self)
        self.name = "gsm"

    @property    
    def number(self):
        if "number" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["number"])

    @number.setter
    def number(self, new_number):
        self.prop_dict["number"] = TypeConvert.py2_dbus_string(new_number)

    @property
    def username(self):
        if "username" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["username"])

    @username.setter
    def username(self, new_user_name):
        self.prop_dict["username"] = TypeConvert.py2_dbus_string(new_user_name)
    
    @property
    def password(self):
        if "password" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["password"])

    @password.setter
    def password(self, new_password):
        self.prop_dict["password"] = TypeConvert.py2_dbus_string(new_password)

    @property
    def password_flags(self):
        if "password-flags" in self.prop_dict.iterkeys():
            return self.prop_dict["password-flags"]

    @password_flags.setter
    def password_flags(self, new_password_flags):
        self.prop_dict["password-flags"] = TypeConvert.py2_dbus_uint32(new_password_flags)

    @property
    def apn(self):
        if "apn" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["apn"])

    @apn.setter
    def apn(self, new_apn):
        self.prop_dict["apn"] = TypeConvert.py2_dbus_string(new_apn)

    @property
    def network_id(self):
        if "network-id" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["network-id"])

    @network_id.setter
    def network_id(self, new_network_id):
        self.prop_dict["network-id"] = TypeConvert.py2_dbus_string(new_network_id)

    @property
    def network_type(self):
        if "network-type" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["network-type"])

    @network_type.setter
    def network_type(self, new_network_type):
        self.prop_dict["network-type"] = TypeConvert.py2_dbus_uint32(new_network_type)

    @property
    def allowed_bands(self):
        if "allowed-bands" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["allowed-bands"])

    @allowed_bands.setter
    def allowed_bands(self, new_allowed_bands):
        self.prop_dict["allowed-bands"] = TypeConvert.py2_dbus_uint32(new_allowed_bands)

    @property
    def pin(self):
        if "pin" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["pin"])

    @pin.setter
    def pin(self, new_pin):
        self.prop_dict["pin"] = TypeConvert.py2_dbus_string(new_pin)

    @property
    def pin_flags(self):
        if "pin-flags" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["pin-flags"])

    @pin_flags.setter
    def pin_flags(self, new_pin_flags):
        self.prop_dict["pin-flags"] = TypeConvert.py2_dbus_uint32(new_pin_flags)

    @property
    def home_only(self):
        if "home-only" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["home-only"])

    @home_only.setter
    def home_only(self, new_home_only):
        self.prop_dict["home-only"] = TypeConvert.py2_dbus_boolean(new_home_only)
