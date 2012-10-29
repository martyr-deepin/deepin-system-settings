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

from nm import get_wireless_device
from pynm.nmlib.nmdevice import NMDevice
from pynm.nmlib.nmdevice_wifi import NMDeviceWifi
from pynm.nmlib.nmdhcp4config import NMDHCP4Config
# from pynm.nmlib.nmdhcp6config import NMDHCP6Config
from pynm.nmlib.nmip4config import NMIP4Config
# from pynm.nmlib.nmip6config import NMIP6Config
from pynm.nmlib.nm_active_connection import NMActiveConnection
from pynm.nmlib.nm_remote_connection import NMRemoteConnection
from pynm.nmlib.nmaccesspoint import NMAccessPoint
from pynm.nmlib.nm_utils import TypeConvert

device = NMDevice(get_wireless_device())
wireless_device = NMDeviceWifi(device.object_path)

# ip4config = NMIP4Config(device.get_ip4_config())
# ip6config = NMIP6Config(device.get_ip6_config())
# dhcp4config = NMDHCP4Config(device.get_dhcp4_config())
# dhcp6config = NMDHCP6Config(device.get_dhcp6_config())

active_connection = NMActiveConnection(device.get_active_connection())
remote_connection = NMRemoteConnection(active_connection.get_connection())


# active_ap = NMAccessPoint(wireless_device.get_active_access_point())
# aps_path = wireless_device.get_access_points()

from pynm.nmlib.nmclient import NMClient
from pynm.nmlib.nm_remote_settings import NMRemoteSettings
remote_setting = NMRemoteSettings()

def disconnect():
    device.nm_device_disconnect()

def is_managed():
    '''device is managed by kernel or managed by network-manager'''
    return device.get_managed()

def get_state():
    return device.get_state()

def get_hw_address():
    return wireless_device.get_hw_address()

def get_perm_hw_address():
    return wireless_device.get_perm_hw_address()

def get_mode():
    return wireless_device.get_mode()

def get_ip4_info():
    print "\n#########IP4 INFO #########"
    print "same to wired.py ,pass"
    print "#########IP4 INFO #########\n"

def get_dhcp4_info():
    print "\n#########DHCP4 INFO #########"
    print "same to wired.py ,pass"
    print "#########DHCP4 INFO #########\n"
    
def get_connection_info():
    print "\n#########Active Connection INFO #########"
    print "same to wired.py ,pass"
    print "SpecificObject:"
    print active_connection.get_specific_object()
    print "#########Active Connection INFO #########\n"

def get_active_ap_info():
    print "\n#########Active AP INFO #########"
    print "Ap ssid:"
    print active_ap.get_ssid()
    print "Ap hw address :"
    print active_ap.get_hw_address()
    print "Ap flags:"
    print active_ap.get_flags()
    print "Ap wpa flags:"
    print active_ap.get_wpa_flags()
    print "Ap rsn flags:"
    print active_ap.get_rsn_flags()
    print "Ap frequency:"
    print active_ap.get_frequency()
    print "Ap max bit:"
    print active_ap.get_max_bitrate()
    print "Ap mode:"
    print active_ap.get_mode()
    print "Ap strength:"
    print active_ap.get_strength()

    print "#########Active AP INFO #########\n"

def list_ap():
    pass

def connection_setting():
    print "\n#########Connection Setting #########"
    print "same to wired.py ,pass"
    print "#########Connection Setting #########\n"

def wireless_setting():
    print "\n#########Wireless Setting #########"

    from pynm.nmutils.nmsetting_wireless import NMSettingWireless
    # wireless = NMSettingWireless()
    wireless = remote_connection.get_setting("802-11-wireless") 
    print "\n###get###\n"

    print " band:%s\n" % wireless.band
    print " bssid:%s\n" % wireless.bssid
    print " channel:%s\n" % wireless.channel
    print " cloned_mac_address:%s\n" % wireless.cloned_mac_address
    print " hidden:%s\n" % wireless.hidden
    print " mac_address:%s\n" % wireless.mac_address
    print " mac_address_blacklist:%s\n" % wireless.mac_address_blacklist
    print " mode:%s\n" % wireless.mode
    print " mtu:%s\n" % wireless.mtu
    print " rate:%s\n" % wireless.rate
    print " security:%s\n" % wireless.security
    print " seen_bssids:%s\n" % wireless.seen_bssids
    print " ssid:%s\n" % wireless.ssid
    print " tx_power:%s\n" % wireless.tx_power

    print "\n###set###\n"

    def adhoc():
        wireless.mode = "adhoc"
        wireless.band = "bg"
        wireless.channel = 6

    def infrastructure():
        wireless.mode = "infrastructure"

    # infrastructure()    
    # # wireless.band = "bg"
    # # wireless.channel = 6
    # wireless.ssid = "我要设置的SSID"
    # wireless.bssid = "设备的BSSID"
    # wireless.mac_address = "44:44:44:44:44:44"
    # wireless.cloned_mac_address = "11:22:33:44:55:66"
    # wireless.mtu = 1000

    # remote_connection.update()
    print "#########Wireless Setting #########\n"

def security_setting():
    print "\n#########security Setting #########"

    ws_s = remote_connection.get_setting("802-11-wireless-security")

    print "\n###get###\n"
    
    print ws_s.prop_dict

    print "\n###set###\n"

    print "#########security Setting #########\n"

def ip4_setting():
    print "\n#########IP4 Setting #########"
    print "same to wired.py ,pass"
    print "#########IP4 Setting #########\n"

def ip6_setting():
    print "\n#########IP6 Setting #########"
    pass
    print "#########IP6 Setting #########\n"

def x1208_setting():
    print "\n#########8021x Setting #########"
    pass
    print "#########8021x Setting #########\n"

def add_wireless_connection():
    return remote_setting.new_wireless_connection()

def active_wireless_connection(conn_path):
    device_path = get_wireless_device()
    specific_object = wireless_device.get_ap_by_ssid("DeepinWork")

    NMClient().activate_connection(conn_path,device_path,specific_object)


if __name__ == "__main__":

    # get_connection_info()
    # get_active_ap_info()
    # list_ap()
    wireless_setting()
    # security_setting()
    # add_wireless_connection()
    # active_wireless_connection(add_wireless_connection())

    pass





