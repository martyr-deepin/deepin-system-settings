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
from nmlib.nmconstant import NMVlanFlags, NMVlanPriorityMap
from nmlib.nmconstant import NMSettingParamFlags as pflag

class NMSettingVlan(NMSetting):
    '''NMSettingVlan'''

    def __init__(self):
        NMSetting.__init__(self)
        self.name = "vlan"

    @property    
    def iface_name(self):
        return self._iface_name

    @iface_name.setter
    def iface_name(self, new_iface_name):
        self._iface_name = new_iface_name

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        self._parent = new_parent

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, new_id):
        self._id = new_id

    @property
    def flags(self):
        return self._flags

    @flags.setter
    def flags(self, new_flags):
        self._flags = new_flags

    # def __get_max_prio(self,map, from):
    #     pass

    def __priority_map_new_from_str(self, map ,str):
        pass
    
    def __get_map(self, map):
        pass
    
    def __set_map(self, map, list):
        pass

    def add_priority_str(self, map, str):
        pass

    def get_num_priorities(self, map):
        pass

    def get_priority(self):
        pass

    def add_priority(self):
        pass

    def remove_priority(self):
        pass

    def clear_priorities(self):
        pass

    def __verify(self):
        pass

    def __get_virtual_iface_name(self):
        pass

    def __priority_stringlist_to_maplist(self):
        pass

    def __set_priority(self):
        pass

    def __get_priority(self):
        pass

    def __priority_maplist_to_stringlist(self):
        pass
