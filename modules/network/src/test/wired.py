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

from nm import get_wired_device
from nmlib.nmdevice import NMDevice
from nmlib.nmdevice_ethernet import NMDeviceEthernet
from nmlib.nmdhcp4config import NMDHCP4Config
# from nmlib.nmdhcp6config import NMDHCP6Config
from nmlib.nmip4config import NMIP4Config
# from nmlib.nmip6config import NMIP6Config

device = NMDevice(get_wired_device())
wired_device = NMDeviceEthernet(device.object_path)

ip4config = NMIP4Config(device.get_ip4_config())
# ip6config = NMIP6Config(device.get_ip6_config())
# dhcp4config = NMDHCP4Config(device.get_dhcp4_config())
# dhcp6config = NMDHCP6Config(device.get_dhcp6_config())

from nmlib.nm_remote_connection import NMRemoteConnection
from nmlib.nm_active_connection import NMActiveConnection
activate_connection = NMActiveConnection(device.get_active_connection())
remote_connection = NMRemoteConnection(activate_connection.get_connection())
from nmlib.nm_remote_settings import NMRemoteSettings
remote_setting = NMRemoteSettings()

# remote_connection = NMRemoteConnection(remote_setting.get_wired_connections()[0])

def disconnect():
    device.nm_device_disconnect()

def is_managed():
    '''device is managed by kernel or managed by network-manager'''
    return device.get_managed()

def get_state():
    return device.get_state()

def get_hw_address():
    return wired_device.get_hw_address()

def get_speed():
    return wired_device.get_speed()

def get_ip4_info():
    print "\n#########IP4 INFO #########"

    print "addresses list:[address/prefix/gateway]:"
    print ip4config.get_addresses()
    print "routes list:[dest/prefix/next_hop/metric]:"
    print ip4config.get_routes()
    print "domains list:"
    print ip4config.get_domains()
    print "nameservers list:"
    print ip4config.get_nameservers()
    print "wins servers list:"
    print ip4config.get_wins_servers()

    print "#########IP4 INFO #########\n"

def get_dhcp4_info():
    print "\n#########DHCP4 INFO #########"

    print "dhcp4 options:"
    print dhcp4config.get_options()

    print "#########DHCP4 INFO #########\n"
    
def get_connection_info():
    print "\n#########Active Connection INFO #########"
    print "uuid:"
    print activate_connection.get_uuid()
    print "state:"
    print activate_connection.get_state()
    print "default:"
    print activate_connection.get_default()

    print "#########Active Connection INFO #########\n"

def connection_setting():
    print "\n#########Connection Setting #########"

    # from nmutils.nmsetting_connection import NMSettingConnection
    cs = remote_connection.get_setting("connection")

    print "\n###get###\n"
    print "autoconnect: %s\n" % cs.autoconnect
    print "id:%s\n" % cs.id
    print "master:%s\n" % cs.master
    print "permissions:%s\n" % cs.permissions
    print "read_only:%s\n" % cs.read_only
    print "slave_type:%s\n" % cs.slave_type
    print "timestamp:%s\n" % cs.timestamp
    print "type:%s\n" % cs.type
    print "uuid:%s\n" % cs.uuid
    print "zone:%s\n" % cs.zone

    print "\n###set###\n"

    # cs.autoconnect = False
    # cs.id = "我想设置的连接名称"
    # cs.read_only = False
    # # cs.clear_permissions()
    # # cs.add_permission("user","yilang","None")

    # remote_connection.update()
    print "#########Connection Setting #########\n"

def wired_setting():
    print "\n#########Wired Setting #########"

    # from nmutils.nmsetting_wired import NMSettingWired
    ws = remote_connection.get_setting("802-3-ethernet")
    def get():
        print "\n###get###\n"
        print " auto_negotiate:%s\n" % ws.auto_negotiate
        print " cloned_mac_address:%s\n" % ws.cloned_mac_address
        print " duplex:%s\n" % ws.duplex
        print " mac_address:%s\n" % ws.mac_address
        print " mac_address_blacklist:%s\n" % ws.mac_address_blacklist
        print " mtu:%s\n" % ws.mtu
        print " port:%s\n" % ws.port
        print " s390_nettype:%s\n" % ws.s390_nettype
        print " s390_options:%s\n" % ws.s390_options
        print " s390_subchannels:%s\n" % ws.s390_subchannels
        print " speed:%s\n" % ws.speed

    get()    
    print "\n###set###\n"
    ws.cloned_mac_address = "11:22:33:44:55:77"
    ws.mtu = 0
    remote_connection.update()
    get()
    print "#########Wired Setting #########\n"

def ip4_setting():
    print "\n#########IP4 Setting #########"

    # from nmutils.nmsetting_ip4config import NMSettingIP4Config
    ip4s = remote_connection.get_setting("ipv4")

    print "\n###get###\n"

    print " method:%s\n" % ip4s.method
    print " dns:%s\n" % ip4s.dns
    print " dns_search:%s\n" % ip4s.dns_search
    print " addresses:%s\n" % ip4s.addresses
    print " routes:%s\n" % ip4s.routes
    print " ignore_auto_routes:%s\n" % ip4s.ignore_auto_routes
    print " ignore_auto_dns:%s\n" % ip4s.ignore_auto_dns
    print " dhcp_client_id:%s\n" % ip4s.dhcp_client_id
    print " dhcp_send_hostname:%s\n" % ip4s.dhcp_send_hostname
    print " dhcp_hostname:%s\n" % ip4s.dhcp_hostname
    print " never_default:%s\n" % ip4s.never_default
    print " may_fail:%s\n" % ip4s.may_fail

    # print ip4s.prop_dict

    print "\n###set###\n"
    def set_router():
        ip4s.add_route(["202.114.88.0","255.255.255.0","10.0.0.1", 10])
        ip4s.add_route(["102.114.88.0","255.255.255.0","10.0.0.1", 50])
        ip4s.add_route(["112.114.88.0","255.255.255.0","10.0.0.1", 4])
        ip4s.remove_route(["102.114.88.0","255.255.255.0","10.0.0.1", 50])
        ip4s.ignore_auto_routes = True
        ip4s.never_default = True

    def auto():
        ip4s.method = "auto"
        ip4s.dhcp_client_id = "my option60 is yilang's pc"
        
    def manual():
        ip4s.method = "manual"
        ip4s.add_address(["192.39.5.7","255.255.255.0","192.39.5.1"])
        ip4s.add_address(["192.39.5.8","255.255.255.0","192.39.5.1"])
        ip4s.add_address(["192.39.5.9","255.255.255.0","192.39.5.1"])
        ip4s.remove_address(["192.39.5.7","255.255.255.0","192.39.5.1"])

        ip4s.add_dns("202.114.88.10")
        ip4s.add_dns("202.114.88.11")
        ip4s.add_dns("202.114.88.12")
        ip4s.remove_dns("202.114.88.11")

        ip4s.add_dns_search("corp.linuxdeepin.com")
        ip4s.add_dns_search("corp.linuxdeepin.cn")
        ip4s.remove_dns_search("corp.linuxdeepin.com")

    def link_local():
        ip4s.method = "link-local"
        ip4s.may_fail = True

    def shared():
        ip4s.method = "shared"
        ip4s.may_fail = False

    def disabled():
        ip4s.method = "disabled"
        
    auto()    
    #manual()    
    # link_local()    
    # shared()    
    # disabled()    
    set_router()

    ###must adapt the settings_dict###
    # ip4s.adapt_ip4config_commit()
    remote_connection.update()
    print "#########IP4 Setting #########\n"

def ip6_setting():
    print "\n#########IP6 Setting #########"

    pass

    print "#########IP6 Setting #########\n"

def x1208_setting():
    print "\n#########8021x Setting #########"

    from nmutils.nmsetting_802_1x import NMSetting8021x
    xs = NMSetting8021x(remote_connection)

    print "\n###get###\n"

    print " eap:%s\n" % xs.eap
    print " identity:%s\n" % xs.identity
    print " anonymous_identity:%s\n" % xs.anonymous_identity
    print " pac_file:%s\n" % xs.pac_file
    print " ca_cert:%s\n" % xs.ca_cert
    print " ca_path:%s\n" % xs.ca_path
    print " subject_match:%s\n" % xs.subject_match
    print " altsubject_matches:%s\n" % xs.altsubject_matches
    print " client_cert:%s\n" % xs.client_cert
    print " phase1_peapver:%s\n" % xs.phase1_peapver
    print " phase1_peaplabel:%s\n" % xs.phase1_peaplabel
    print " phase1_fast_provisioning:%s\n" % xs.phase1_fast_provisioning
    print " phase2_auth:%s\n" % xs.phase2_auth
    print " phase2_autheap:%s\n" % xs.phase2_autheap
    print " phase2_ca_cert:%s\n" % xs.phase2_ca_cert
    print " phase2_ca_path:%s\n" % xs.phase2_ca_path
    print " phase2_subject_match:%s\n" % xs.phase2_subject_match
    print " phase2_altsubject_matches:%s\n" % xs.phase2_altsubject_matches
    print " phase2_client_cert:%s\n" % xs.phase2_client_cert
    print " password:%s\n" % xs.password
    print " password_flags:%s\n" % xs.password_flags
    print " password_raw:%s\n" % xs.password_raw
    print " password_raw_flags:%s\n" % xs.password_raw_flags
    print " pin:%s\n" % xs.pin
    print " pin_flags:%s\n" % xs.pin_flags
    print " private_key:%s\n" % xs.private_key
    print " private_key_password:%s\n" % xs.private_key_password
    print " phase2_private_key:%s\n" % xs.phase2_private_key
    print " phase2_private_key_password:%s\n" % xs.phase2_private_key_password
    print " phase2_private_key_password_flags:%s\n" % xs.phase2_private_key_password_flags
    print " system_ca_certs:%s\n" % xs.system_ca_certs

    print "\n###set###\n"

    pass
    # remote_connection.update()

    print "#########8021x Setting #########\n"
    
def add_wired_connection():
    return remote_setting.new_wired_connection()

def active_connection(conn_path):
    ##as autoconnect is True, it will try to connect since instance
    NMRemoteConnection(conn_path)

    # from nmlib.nm_utils import TypeConvert
    # conn_path = TypeConvert.dbus2py(conn_path)
    # device_path = get_wired_device()
    # specific_object = "/"

    # from nmlib.nmclient import NMClient

    # NMClient().activate_connection(conn_path,device_path,specific_object)

if __name__ == "__main__":
    # print remote_connection.settings_dict
    # disconnect()
    #get_ip4_info()
    # get_dhcp4_info()
    #get_connection_info()
    # connection_setting()
    #wired_setting()
    ip4_setting()
    # x1208_setting()
    # add_wired_connection()
    # activate_connection(add_wired_connection())
    pass
