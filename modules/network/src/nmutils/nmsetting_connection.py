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

import dbus
from nmsetting import NMSetting
from nmlib.nm_utils import TypeConvert

class NMSettingConnection (NMSetting):
    '''NMSettingConnection'''

    def __init__(self):
        NMSetting.__init__(self)
        self.name = "connection"

    @property
    def permissions(self):
        if "permissions" in self.prop_dict.iterkeys():
            return TypeConvert().dbus2py(self.prop_dict["permissions"])

    @permissions.setter
    def permissions(self, new_permissions):
        self.prop_dict["permissions"] = TypeConvert.py2_dbus_array(new_permissions)

    def add_permission(self, type, id, reserved):
        self.prop_dict["permissions"].append(":".join([type,id,reserved]))


    def permissions_user_allowed (self, uname):
        return uname in map(lambda x: x[1], self.prop_dict["permissions"])

    def remove_permission (self, id):
        if self.permissions_user_allowed(id):
            self.prop_dict["permissions"] = filter(lambda x: x[1] != id, self.prop_dict["permissions"])

    def clear_permissions(self):
        self.prop_dict["permissions"] = dbus.Array(signature = dbus.Signature('s'))

    @property
    def autoconnect(self):
        if "autoconnect" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["autoconnect"])
        else:
            return True

    @autoconnect.setter
    def autoconnect(self, new_autoconnect):
        self.prop_dict["autoconnect"] = TypeConvert.py2_dbus_boolean(new_autoconnect)

    @property
    def id(self):
        if "id" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["id"])

    @id.setter
    def id(self, new_id):
        self.prop_dict["id"] = TypeConvert.py2_dbus_string(new_id)

    @property
    def master(self):
        if "master" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["master"])

    @master.setter
    def master(self, new_master):
        self.prop_dict["master"] = TypeConvert.py2_dbus_string(new_master)
    
    @property
    def read_only(self):
        if "read-only" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["read-only"])
        else:
            return False
    
    @read_only.setter
    def read_only(self, new_read_only):
        self.prop_dict["read_only"] = TypeConvert.py2_dbus_boolean(new_read_only)

    @property
    def slave_type(self):
        if "slave-type" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["slave-type"])

    @slave_type.setter
    def slave_type(self, new_slave_type):
        self.prop_dict["slave-type"] = TypeConvert.py2_dbus_string(new_slave_type)

    @property
    def timestamp(self):
        if "timestamp" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["timestamp"])
        else:
            return  0

    @timestamp.setter
    def timestamp(self, new_timestamp):
        self.prop_dict["timestamp"] = TypeConvert.py2_dbus_uint64(new_timestamp)

    @property
    def type(self):
        if "type" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["type"])

    @type.setter
    def type(self, new_type):
        self.prop_dict["type"] = TypeConvert.py2_dbus_string(new_type)

    @property
    def uuid(self):
        if "uuid" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["uuid"])

    @uuid.setter
    def uuid(self, new_uuid):
        # self.prop_dict["uuid"] = TypeConvert.py2_dbus_string(new_uuid)
        self.prop_dict["uuid"] = dbus.String(new_uuid)

    @property
    def zone(self):
        if "zone" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["zone"])

    @zone.setter
    def zone(self, new_zone):
        self.prop_dict["zone"] = TypeConvert.py2_dbus_string(new_zone)
