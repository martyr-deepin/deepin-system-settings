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
import sys
sys.path.append("../")

import dbus
import gobject
import copy
from nmlib.nmconstant import NMSettingCompareFlags as cflags
from nmlib.nmconstant import NMSettingParamFlags as pflags
from nmlib.nmconstant import NMSettingSecretFlags as sflags
# from pynm.nmlib.nm_remote_connection import NMRemoteConnection

from nmlib.nm_utils import TypeConvert

class NMSetting (gobject.GObject, object):
    '''NMSetting'''
    
    def __init__(self):
        gobject.GObject.__init__(self)

        self.name = ""###settings name###
        self.prop_dict = dbus.Dictionary(signature = dbus.Signature('sv'))##{name:value} inited in nm_remote_connection###
        self.prop_flags = {}###name:flags###
        self.prop_list = []
        # self.nm_remote_connection = nm_remote_connection

    def get_name (self):
        return self.name

    # def init_setting_properties(self):

    #     def delete_underline(string):
    #         return filter(lambda x: x not in "-_",string.lower())

    #     if self.name not in self.nm_remote_connection.settings_dict.iterkeys():
    #         self.prop_dict = {}
    #         self.nm_remote_connection.settings_dict[self.name] = dbus.Dictionary(signature = dbus.Signature('sv'))
    #     else:    
    #         self.prop_dict = TypeConvert().dbus2py(copy.deepcopy(self.nm_remote_connection.settings_dict[self.name]))
    #         for key in self.prop_dict.keys():
    #             for prop in self.prop_list:
    #                 if delete_underline(key) == delete_underline(prop):
    #                     setattr(self, prop, self.prop_dict[key])


    def compare_property(self, first, second, name ,flags):
        if first.prop_flags[name] & pflags.NM_SETTING_PARAM_SECRET:
            if first.prop_flags[name] != second.prop_flags[name]:
                return False

            if ((flags & cflags.NM_SETTING_COMPARE_FLAG_IGNORE_AGENT_OWNED_SECRETS)
                and (first.prop_flags[name] & sflags.NM_SETTING_SECRET_FLAG_AGENT_OWNED)):
                return True

            if ((flags & cflags.NM_SETTING_COMPARE_FLAG_IGNORE_NOT_SAVED_SECRETS)
                and (first.prop_flags[name] & sflags.NM_SETTING_SECRET_FLAG_NOT_SAVED)):
                return True

        return getattr(first, name) == getattr(second, name)

    def compare(self, first, second, flags):
        if type(first) != type(second):
            return False
        same = True
        for name in first.prop_list and same:
            if flags & cflags.NM_SETTING_COMPARE_FLAG_FUZZY and (
                first.prop_flags[name] & (pflags.NM_SETTING_PARAM_FUZZY_IGNORE or pflags.NM_SETTING_PARAM_SECRET)):
                continue

            if flags & cflags.NM_SETTING_COMPARE_FLAG_IGNORE_SECRETS and (
                first.prop_flags[name] & pflags.NM_SETTING_PARAM_SECRET):
                continue

            same = self.compare_property(first, second, name, flags)

        return same    


    def duplicate (self):
        nm_setting = NMSetting()
        nm_setting = copy.deepcopy(self.name)
        nm_setting.prop_dict = copy.deepcopy(self.prop_dict)
        nm_setting.prop_flags = copy.deepcopy(self.prop_flags)
        return nm_setting

    def diff (self, b, flags, invert_results):
        pass

    def clear_secrets(self):
        for name in self.prop_flags.iterkeys():
            if self.prop_flags[name] & pflags.NM_SETTING_PARAM_SECRET:
                self.prop_dict[name]= ""

    def __clear_secrets_with_flags(self, prop, func, user_data):
        pass

    def clear_secrets_with_flags(self):
        pass

    def need_secrets (self):
        pass

    def __update_one_secret(self, key, value):
        if key not in self.prop_dict.iterkeys():
            return False
        if not self.prop_flags[key] & pflags.NM_SETTING_PARAM_SECRET:
            return True
        self.prop_dict[key] = value
        return True

    def update_secrets (self, secrets_dict):
        for key, value in enumerate(secrets_dict):
            self.__update_one_secret(key, value)

    def __is_secret_prop(self, secret_name):
        if secret_name not in self.prop_dict.iterkeys():
            print "invalid prop secret_name %s\n" % secret_name
            return False
        else:    
            return self.prop_flags[secret_name] & pflags.NM_SETTING_PARAM_SECRET
    
    def get_secret_flags (self, secret_name):
        if not self.__is_secret_prop(secret_name):
            print "not a secret_prop %s " % secret_name
        else:
            return self.prop_flags[secret_name]

    def set_secret_flags (self, secret_name, out_flags):
        if secret_name not in self.prop_flags.iterkeys():
            print "%s is not a valid property" % secret_name
        elif not self.__is_secret_prop(secret_name):
            print "not a secret_prop %s " % secret_name
        else:
            self.prop_flags[secret_name] = out_flags

    def get_virtual_iface_name (self):
        pass

    def __set_property(self):
        pass

    def __get_property(self):
        pass

