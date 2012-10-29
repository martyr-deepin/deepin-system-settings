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

class NMSettingOlpcMesh(NMSetting):
    '''NMSettingOlpcMesh'''
    
    def __init__(self):
        NMSetting.__init__(self)
        self.name = "802-11-olpc-mesh"

    @property    
    def ssid(self):
        return self._ssid

    @ssid.setter
    def ssid(self, new_ssid):
        self._ssid = new_ssid

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, new_channel):
        self._channel = new_channel

    @property
    def dhcp_anycast_addr(self):
        return self._dhcp_anycast_addr

    @dhcp_anycast_addr.setter
    def dhcp_anycast_addr(self, new_dhcp_anycast_addr):
        self._dhcp_anycast_addr = new_dhcp_anycast_addr
