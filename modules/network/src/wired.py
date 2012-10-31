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
from nmlib.nmclient import nmclient
#from nmlib.nmdevice_ethernet import NMDeviceEthernet
from nmlib.nm_remote_settings import nm_remote_settings
# from nmlib.nm_remote_connection import NMRemoteConnection
# from nmlib.nm_active_connection import NMActiveConnection
#from nmlib.nmdevice_wifi import NMDeviceWifi
from nmlib.nmcache import cache
# from nmlib.nmdevice import NMDevice
# from nmlib.nm_utils import TypeConvert

# wired_device = NMDevice(nmclient.get_wired_devices()[0])
wired_device = nmclient.get_wired_devices()[0]
#print nmclient.get_wireless_devices()
# wireless_device = NMDevice(nmclient.get_wireless_devices()[0])
wireless_device = nmclient.get_wireless_devices()[0]
#wireless_device.get_active_connection()

#activate_connection = NMActiveConnection(wireless_device.get_active_connection())
#print activate_connection.get_specific_object()
#remote_connection = NMRemoteConnection(activate_connection.get_connection())
#print remote_connection
#ethernet = NMDeviceEthernet(wired_device.object_path)

#if not device.get_active_connection() == "/":
    #activate_connection = NMActiveConnection(device.get_active_connection())
    #remote_connection = NMRemoteConnection(activate_connection.get_connection())
#else:
    #activate_connection = None
    #remote_connection = NMRemoteConnection(nm_remote_settings.get_wired_connections()[0])
