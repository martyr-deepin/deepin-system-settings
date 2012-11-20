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

class NMSettingVpn(NMSetting):
    '''NMSettingVpn'''
    
    def __init__(self):
        NMSetting.__init__(self)
        self.name = "vpn"

    @property    
    def service_type(self):
        if "service-type" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["service-type"])

    @service_type.setter
    def service_type(self, new_service_type):
        self.prop_dict["service-type"] = TypeConvert.py2_dbus_string(new_service_type)

    @property
    def user_name(self):
        if "user-name" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["user-name"])

    @user_name.setter
    def user_name(self, new_user_name):
        self.prop_dict["user-name"] = TypeConvert.py2_dbus_string(new_user_name)

    @property
    def secrets(self):
        if "secrets" not in self.prop_dict.iterkeys():
            self.prop_dict["secrets"] = dbus.Dictionary({}, signature = dbus.Signature('ss'))
        return TypeConvert.dbus2py(self.prop_dict["secrets"])

    @secrets.setter
    def secrets(self, new_secrets):
        self.prop_dict["secrets"] = dbus.Dictionary(new_secrets, signature = dbus.Signature('ss'))

    @secrets.deleter
    def secrets(self):
        self.prop_dict["secrets"] = dbus.Dictionary({}, signature = dbus.Signature('ss'))

    def get_secret_item(self, item):
        return self.secrets[item]

    def set_secret_item(self, item, value):
        if "secrets" not in self.prop_dict.iterkeys():
            self.prop_dict["secrets"] = dbus.Dictionary({}, signature = dbus.Signature('ss'))
        self.prop_dict["secrets"][item] = value

    def delete_secret_item(self, item):
        del self.prop_dict["secrets"][item]

    @property
    def data(self):
        if "data" not in self.prop_dict.iterkeys():
            self.prop_dict["data"] = dbus.Dictionary({}, signature = dbus.Signature('ss'))
        return TypeConvert.dbus2py(self.prop_dict["data"])

    @data.setter
    def data(self, new_data):
        self.prop_dict["data"] = dbus.Dictionary(new_data, signature = dbus.Signature('ss'))

    @data.deleter
    def data(self):
        self.prop_dict["data"] = dbus.Dictionary({}, signature = dbus.Signature('ss'))

    def get_data_item(self, item):
        if item in self.data.iterkeys():
            return self.data[item]

    def set_data_item(self, item, value):
        if "data" not in self.prop_dict.iterkeys():
            self.prop_dict["data"] = dbus.Dictionary({}, signature = dbus.Signature('ss'))
        self.prop_dict["data"][item] = value

    def delete_data_item(self, item):
        del self.prop_dict["data"][item]



if __name__ == "__main__":
    pass
