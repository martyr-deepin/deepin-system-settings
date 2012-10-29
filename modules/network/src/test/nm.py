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
sys.path.append("../../")

from pynm.nmlib.nmclient import NMClient
from pynm.nmlib.nmdevice import NMDevice

nmclient = NMClient()

def set_nm_enable(enable):
    nmclient.networking_set_enabled(enable)

def set_wireless_enable(enable):
    nmclient.wireless_set_enabled(enable)

def list_device():
    return nmclient.get_devices()

# def is_wired_device(device_object_path):
#     nmdevice = NMDevice(device_object_path, None)
#     if nmdevice.get_device_type() == 1:
#         return True
#     else:
#         return False

# def is_wireless_device(device_object_path):
#     nmdevice = NMDevice(device_object_path, None)
#     if nmdevice.get_device_type() == 2:
#         return True
#     else:
#         return False

def get_wired_device():
    return nmclient.get_wired_device()

def get_wireless_device():
    return nmclient.get_wireless_device()

def disconnect_wired():
    nmdevice = NMDevice(get_wired_device(), None)
    nmdevice.dbus_interface.Disconnect()

def disconnect_wireless():
    nmdevice = NMDevice(get_wireless_device(), None)
    nmdevice.dbus_interface.Disconnect()
    
def get_active_connections():
    return nmclient.get_active_connections()

def deactive_connection(connection_object_path):
    nmclient.deactive_connection(connection_object_path)

if __name__ == "__main__":
    # set_nm_enable(True)
    # set_wireless_enable(False)
    print list_device()
    # print get_active_connections()
    print get_wired_device()
    # print get_wireless_device()
    # disconnect_wireless()

    pass
