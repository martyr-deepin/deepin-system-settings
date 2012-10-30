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

class NMCache(object):

    def __init__(self):
        self.cache_dict = {}
        self.spec_cache_dict = {}
    
    def new_object(self, path):
        key = path.split("/")[-2]

        if path in self.cache_dict.iterkeys():
            return self.cache_dict[path]
        elif key == "Settings":
            try:
                from nm_remote_connection import NMRemoteConnection
                return NMRemoteConnection(path)
            except:
                pass
        elif key == "Devices":
            try:
                from nmdevice import NMDevice
                return NMDevice(path)
            except:
                pass
        elif key == "AccessPoint":
            try:
                from nmaccesspoint import NMAccessPoint
                return NMAccessPoint(path)
            except:
                pass
        elif key == "ActiveConnection":
            try:
                from nm_active_connection import NMActiveConnection
                return NMActiveConnection(path)
            except:
                pass
        elif key == "IP4Config":
            try:
                from nmip4config import NMIP4Config
                return NMIP4Config(path)
            except:
                pass
        elif key == "DHCP4Config":
            try:
                from nmdhcp4config import NMDHCP4Config
                return NMDHCP4Config(path)
            except:
                pass
        elif key == "IP6Config":
            try:
                from nmip6config import NMIP6Config
                return NMIP6Config(path)
            except:
                pass
        elif key == "DHCP6Config":
            try:
                from nmdhcp6config import NMDHCP6Config
                return NMDHCP6Config(path)
            except:
                pass
        else:
            print "unsupport type"
            print path

    def putobject(self, path, object):
        if path not in self.cache_dict.iterkeys():
            self.cache_dict[path] = object
        else:
            print "already stored the object"
    
    def getobject(self, path):
        if path in self.cache_dict.iterkeys():
            return self.cache_dict[path]
        else:
            self.putobject(path, self.new_object(path))
            return self.cache_dict[path]

    def delobject(self, path):
        if path in self.cache_dict.iterkeys():
            del self.cache_dict[path]
    
    def clearcache(self):
        self.cache_dict.clear()
    
    def replaceobject(self, path, object):
        if path in self.cache_dict.iterkeys():
            self.cache_dict[path] = object
        else:
            print "doesn't exist"

    def new_spec_object(self, path):
        if path in self.spec_cache_dict.iterkeys():
            return self.cache_dict[path]

        key = self.getobject(path).get_device_type()
        if key == 1:
            try:
                from nmdevice_ethernet import NMDeviceEthernet
                return NMDeviceEthernet(path)
            except:
                pass
        elif key == 2:
            try:
                from nmdevice_wifi import NMDeviceWifi
                return NMDeviceWifi(path)
            except:
                pass
        elif key == 8:
            try:
                from nmdevice_modem import NMDeviceModem
                return NMDeviceModem(path)
            except:
                pass
        else:
            print "unsupport spec type"
            print path

    def put_spec_object(self, path, object):
        if path not in self.spec_cache_dict.iterkeys():
            self.spec_cache_dict[path] = object
        else:
            print "already stored the object"

    def get_spec_object(self, path):
        if path in self.spec_cache_dict.iterkeys():
            return self.spec_cache_dict[path]
        else:
            self.put_spec_object(path, self.new_spec_object(path))
            return self.spec_cache_dict[path]

    def del_spec_object(self, path):
        if path in self.spec_cache_dict.iterkeys():
            del self.spec_cache_dict[path]

    def clear_spec_cache(self):
        self.spec_cache_dict.clear()

    def replace_spec_object(self, path, object):
        if path in self.spec_cache_dict.iterkeys():
            self.spec_cache_dict[path] = object
        else:
            print "doesn't exist"

cache = NMCache()

if __name__ == "__main__":
    ap = []
    for i in range(10):
        ap.append(cache.getobject("/org/freedesktop/NetworkManager/AccessPoint/0"))
    for i in range(len(ap)):
        print ap[i]
