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
import traceback
from nm_utils import valid_object_path

class NewObjectFailed(Exception):

    def __init__(self, path):
        self.path = path

    def __str__(self):
        return repr("NewObjectFailed:" + self.path)

class NMCache(object):

    def __init__(self):
        self.cache_dict = {}
        self.spec_cache_dict = {}
    
    def new_object(self, path):
        if valid_object_path(path):
            key = path.split("/")[-2]
        else:    
            raise NewObjectFailed(path)

        if path in self.cache_dict.iterkeys():
            return self.cache_dict[path]
        elif key == "Settings":
            try:
                from nm_remote_connection import NMRemoteConnection
                remote_connection =  NMRemoteConnection(path)
                if remote_connection:
                    return remote_connection
                else:
                    raise NewObjectFailed(path)
            except NewObjectFailed, e:
                print "create object:%s failed" % e.path
            except:
                traceback.print_exc()
        elif key == "Devices":
            try:
                from nmdevice import NMDevice
                device = NMDevice(path)
                if device:
                    return device
                else:
                    raise NewObjectFailed(path)
            except NewObjectFailed, e:
                print "create object:%s failed" % e.path
            except:
                traceback.print_exc()
        elif key == "AccessPoint":
            try:
                from nmaccesspoint import NMAccessPoint
                ap = NMAccessPoint(path)
                if ap:
                    return ap
                else:
                    raise NewObjectFailed(path)
            except NewObjectFailed, e:
                print "create object:%s failed" % e.path
            except:
                traceback.print_exc()
        elif key == "ActiveConnection":
            try:
                from nm_active_connection import NMActiveConnection
                active_connection = NMActiveConnection(path)
                if active_connection:
                    return active_connection
                else:
                    raise NewObjectFailed(path)
            except NewObjectFailed, e:
                print "create object:%s failed" % e.path
            except:
                traceback.print_exc()
        elif path.split("/")[-1] == "NetworkManager":
            try:
                from nmclient import NMClient
                nmclient = NMClient()
                if nmclient:
                    return nmclient
                else:
                    raise NewObjectFailed(path)
            except NewObjectFailed, e:
                print "create object:%s failed" % e.path
            except:
                traceback.print_exc()
        elif path.split("/")[-1] == "Settings":
            try:
                from nm_remote_settings import NMRemoteSettings
                nm_remote_settings = NMRemoteSettings()
                if nm_remote_settings:
                    return nm_remote_settings
                else:
                    raise NewObjectFailed(path)
            except NewObjectFailed, e:
                print "create object:%s failed" % e.path
            except:
                traceback.print_exc()
        elif path.split("/")[-1] == "AgentManager":
            try:
                from nm_secret_agent import NMAgentManager
                agent_manager = NMAgentManager()
                if agent_manager:
                    return agent_manager
                else:
                    raise NewObjectFailed(path)
            except NewObjectFailed, e:
                print "create object:%s failed" % e.path
            except:
                traceback.print_exc()
        elif key == "IP4Config":
            try:
                from nmip4config import NMIP4Config
                ip4config = NMIP4Config(path)
                if ip4config:
                    return ip4config
                else:
                    raise NewObjectFailed(path)
            except NewObjectFailed, e:
                print "create object:%s failed" % e.path
            except:
                traceback.print_exc()
        elif key == "DHCP4Config":
            try:
                from nmdhcp4config import NMDHCP4Config
                dhcp4config = NMDHCP4Config(path)
                if dhcp4config:
                    return dhcp4config
                else:
                    raise NewObjectFailed(path)
            except NewObjectFailed, e:
                print "create object:%s failed" % e.path
            except:
                traceback.print_exc()
        elif key == "IP6Config":
            try:
                from nmip6config import NMIP6Config
                ip6config = NMIP6Config(path)
                if ip6config:
                    return ip6config
                else:
                    raise NewObjectFailed(path)
            except NewObjectFailed, e:
                print "create object:%s failed" % e.path
            except:
                traceback.print_exc()
        elif key == "DHCP6Config":
            try:
                from nmdhcp6config import NMDHCP6Config
                dhcp6config = NMDHCP6Config(path)
                if dhcp6config:
                    return dhcp6config
                else:
                    raise NewObjectFailed(path)
            except NewObjectFailed, e:
                print "create object:%s failed" % e.path
            except:
                traceback.print_exc()
        else:
            print "unsupport type"
            print path

    def putobject(self, path, object):
        if path not in self.cache_dict.keys():
            self.cache_dict[path] = object
        else:
            print "already stored the object"
    
    def getobject(self, path):
        if path in self.cache_dict.keys():
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

        if "Devices" in path:
            key = self.getobject(path).get_device_type()
            if key == 1:
                try:
                    from nmdevice_ethernet import NMDeviceEthernet
                    device_ethernet = NMDeviceEthernet(path)
                    if device_ethernet:
                        return device_ethernet
                    else:
                        raise NewObjectFailed(path)
                except NewObjectFailed, e:
                    print "create object:%s failed" % e.path
                except:
                    traceback.print_exc()
            elif key == 2:
                try:
                    from nmdevice_wifi import NMDeviceWifi
                    device_wifi = NMDeviceWifi(path)
                    if device_wifi:
                        return device_wifi
                    else:
                        raise NewObjectFailed(path)
                except NewObjectFailed, e:
                    print "create object:%s failed" % e.path
                except:
                    traceback.print_exc()
            elif key == 8:
                try:
                    from nmdevice_modem import NMDeviceModem
                    device_modem = NMDeviceModem(path)
                    if device_modem:
                        return device_modem
                    else:
                        raise NewObjectFailed(device_modem)
                except NewObjectFailed, e:
                    print "create object:%s failed" % e.path
                except:
                    traceback.print_exc()
            else:
                print "unsupport device type"
                print path

        elif "ActiveConnection" in path:
            try:
                from nm_vpn_connection import NMVpnConnection
                vpn_connection = NMVpnConnection(path)
                if vpn_connection:
                    return vpn_connection
                else:
                    raise NewObjectFailed(vpn_connection)
            except NewObjectFailed ,e:
                print "create object:%s failed" % e.path

        else:
            print "unsupport spec path"
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
