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

class NMSettingAdsl(NMSetting):
    '''NMSettingAdsl'''
    
    def __init__(self):
        NMSetting.__init__(self)
        self.name = "adsl"

    @property    
    def encapsulation(self):
        return self._encapsulation

    @encapsulation.setter
    def encapsulation(self, new_encapsulation):
        self._encapsulation = new_encapsulation

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, new_password):
        self._password = new_password

    @property
    def password_flags(self):
        return self._password_flags

    @password_flags.setter
    def password_flags(self, new_password_flags):
        self._password_flags = new_password_flags

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, new_protocol):
        self._protocol = new_protocol

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, new_username):
        self._username = new_username

    @property
    def vci(self):
        return self._vci

    @vci.setter
    def vci(self, new_vci):
        self._vci = new_vci

    @property
    def vpi(self):
        return self._vpi

    @vpi.setter
    def vpi(self, new_vpi):
        self._vpi = new_vpi
