#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Zeng Zhi
# 
# Author:     Zeng Zhi <zengzhilg@gmail.com>
# Maintainer: Zeng Zhi <zengzhilg@gmail.com>
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
from nmlib.nmclient import NMClient
from nmlib.nm_remote_settings import NMRemoteSettings
from nmlib.nmcache import NMCache, cache
from nmlib.nm_secret_agent import NMSecretAgent

class NModule(object):

    def __init__(self):
        self.client = NMClient()
        self.setting = NMRemoteSettings()
        self.agent = NMSecretAgent()

    @property
    def nmclient(self):
        return self.client
    @nmclient.setter
    def nmclient(self, val):
        self.client = val
    @property
    def nm_remote_settings(self):
        return self.setting
    @nm_remote_settings.setter
    def nm_remote_settings(self, val):
        self.setting = NMRemoteSettings()

    @property
    def secret_agent(self):
        return self.agent
    @secret_agent.setter
    def secret_agent(self, val):
        self.agent = NMSecretAgent()

nm_module = NModule()
#wired_device = nmclient.get_wired_devices()[0]
#wireless_device = nmclient.get_wireless_devices()[0]
#if nmclient.get_wireless_devices() != []:
#else:
    #wireless_device = []
##wireless_device = []
