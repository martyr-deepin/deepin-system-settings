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

class NMSettingPPPOE (NMSetting):
    '''NMSettingPPPOE'''

    def __init__(self):
        NMSetting.__init__(self)
        self.name = "pppoe"

    @property    
    def service(self):
        if "service" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["service"])

    @service.setter
    def service(self, new_service):
        self.prop_dict["service"] = TypeConvert.py2_dbus_string(new_service)

    @property
    def username(self):
        if "username" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["username"])

    @username.setter
    def username(self, new_username):
        self.prop_dict["username"] = TypeConvert.py2_dbus_string(new_username)

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
            return TypeConvert.dbus2py(self.prop_dict["password-flags"])

    @password_flags.setter
    def password_flags(self, new_password_flags):
        self.prop_dict["password-flags"] = TypeConvert.py2_dbus_uint32(new_password_flags)

if __name__ == "__main__":
    pass
    
