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

import uuid
import time
import re
import gobject
from nmobject import NMObject
from nm_utils import TypeConvert
from nmcache import cache
from nmutils.nmsetting_connection import NMSettingConnection
from nmutils.nmsetting_wired import NMSettingWired
from nmutils.nmsetting_ip4config import NMSettingIP4Config
from nmutils.nmsetting_ip6config import NMSettingIP6Config
from nmutils.nmsetting_wireless import NMSettingWireless
from nmutils.nmsetting_wireless_security import NMSettingWirelessSecurity
from nmutils.nmsetting_vpn import NMSettingVpn
from nmutils.nmsetting_pppoe import NMSettingPPPOE
from nmutils.nmsetting_cdma import NMSettingCdma
from nmutils.nmsetting_gsm import NMSettingGsm
from nmutils.nmsetting_serial import NMSettingSerial
from nmutils.nmsetting_ppp import NMSettingPPP

class NMRemoteSettings(NMObject):
    '''NMRemoteSettings'''

    __gsignals__  = {
            "connections-read":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_POINTER,)),
            "new-connection":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
            }

    def __init__(self):
        NMObject.__init__(self, "/org/freedesktop/NetworkManager/Settings", "org.freedesktop.NetworkManager.Settings")
        self.bus.add_signal_receiver(self.properties_changed_cb, dbus_interface = self.object_interface, signal_name = "PropertiesChanged")
        self.bus.add_signal_receiver(self.new_connection_cb, dbus_interface = self.object_interface, signal_name = "NewConnection")

        self.init_nmobject_with_properties()

    def list_connections(self):
        '''return connections object'''
        return map(lambda x:cache.getobject(x), TypeConvert.dbus2py(self.dbus_method("ListConnections")))
    
    def get_connection_by_uuid(self, uuid):
        return cache.getobject(self.dbus_method("GetConnectionByUuid", uuid))

    def save_hostname(self, hostname):
        self.dbus_method("SaveHostname", hostname)
    
    def add_connection(self, settings_dict):
        return cache.getobject(self.dbus_method("AddConnection", settings_dict))

    def generate_connection_id(self, connection_type):

        if connection_type == "wired":
            conn_list = self.get_wired_connections()
            conn_start = "有线连接"
        elif connection_type == "wireless":
            conn_list = self.get_wireless_connections()
            conn_start = "无线连接"
        elif connection_type == "dsl":
            conn_list = self.get_pppoe_connections()
            conn_start = "拨号连接"
        elif connection_type == "vpn":
            conn_list = self.get_vpn_connections()
            conn_start = "VPN连接"
        elif connection_type == "cdma":
            conn_list = self.get_cdma_connections()
            conn_list = "CDMA连接"
        elif connection_type == "gsm":
            conn_list = self.get_gsm_connections()
            conn_start = "GSM连接"
        else:
            return "新建连接"

        index_list = [0, ]
        for conn in conn_list:
            tmp = re.findall("\d+$", conn.settings_dict["connection"]["id"])
            if tmp:
                index_list.append(int(tmp[-1]))

        return "%s" % conn_start + str(1 + max(index_list))        

    def new_wired_connection(self):
        '''return the newly added wired remote connection object'''
        s_connection = NMSettingConnection()
        s_wired = NMSettingWired()
        s_ip4config = NMSettingIP4Config()
        s_ip6config = NMSettingIP6Config()

        s_connection.type = "802-3-ethernet"
        # s_connection.id = "有线连接"
        s_connection.id = self.generate_connection_id("wired")
        s_connection.autoconnect = True
        s_connection.uuid = uuid.uuid4()
        s_connection.timestamp = time.time()

        s_wired.duplex = "full"
        s_wired.clear_s390_options()

        s_ip4config.method = "auto"
        s_ip4config.clear_addresses()
        s_ip4config.clear_routes()
        s_ip4config.clear_dns()
    
        s_ip6config.method = "auto"
        s_ip6config.routes = []
        s_ip6config.dns = []
        s_ip6config.addresses = []

        settings_dict = {"802-3-ethernet":s_wired.prop_dict,
                         "connection":s_connection.prop_dict,
                         "ipv4":s_ip4config.prop_dict
                         ,"ipv6":s_ip6config.prop_dict
                         }

        return self.add_connection(settings_dict)

    def new_wireless_connection(self, ssid = "Wireless Connection"):
        s_connection = NMSettingConnection()
        s_wireless = NMSettingWireless()
        s_wireless_security = NMSettingWirelessSecurity()
        s_ip4config = NMSettingIP4Config()
        s_ip6config = NMSettingIP6Config()

        s_connection.type = "802-11-wireless"
        s_connection.id = self.generate_connection_id("wireless")
        s_connection.autoconnect = True
        s_connection.uuid = uuid.uuid4()
        s_connection.timestamp = time.time()

        s_wireless.mode = "infrastructure"
        s_wireless.ssid = ssid
        s_wireless.security = "802-11-wireless-security"

        s_wireless_security.key_mgmt = "wpa-psk"

        s_ip4config.method = "auto"
        s_ip4config.clear_addresses()
        s_ip4config.clear_routes()
        s_ip4config.clear_dns()

        s_ip6config.method = "auto"
        s_ip6config.routes = []
        s_ip6config.dns = []
        s_ip6config.addresses = []

        settings_dict = {"802-11-wireless":s_wireless.prop_dict,
                         "802-11-wireless-security":s_wireless_security.prop_dict,
                         "connection":s_connection.prop_dict,
                         "ipv4":s_ip4config.prop_dict
                         ,"ipv6":s_ip6config.prop_dict
                         }
        settings_dict["802-11-wireless-security"]["psk"] = "Password"

        return self.add_connection(settings_dict)

    def new_pppoe_connection(self):
        s_connection = NMSettingConnection()
        s_wired = NMSettingWired()
        s_ip4config = NMSettingIP4Config()
        s_pppoe = NMSettingPPPOE()

        s_connection.type = "pppoe"
        # s_connection.id = "DSL连接1"
        s_connection.id = self.generate_connection_id("dsl")
        s_connection.autoconnect = True
        s_connection.uuid = uuid.uuid4()
        s_connection.timestamp = time.time()

        s_wired.duplex = "full"
        s_wired.clear_s390_options()

        s_ip4config.method = "auto"
        s_ip4config.clear_addresses()
        s_ip4config.clear_routes()
        s_ip4config.clear_dns()
        
        s_pppoe.username = "yilang"
        s_pppoe.password = "yilang"

        settings_dict = {"802-3-ethernet":s_wired.prop_dict,
                         "connection":s_connection.prop_dict,
                         "ipv4":s_ip4config.prop_dict,
                         "pppoe":s_pppoe.prop_dict
                         }

        return self.add_connection(settings_dict)
        
    def new_gsm_connection(self):
        s_connection = NMSettingConnection()
        s_gsm = NMSettingGsm
        s_serial = NMSettingSerial()
        s_ppp = NMSettingPPP()
        s_ip4config = NMSettingIP4Config()

        s_gsm.number = "*99#"
        s_gsm.username = ""
        s_gsm.password = ""
        s_gsm.apn = ""

        s_serial.baud = 115200
        s_serial.bits = 8
        s_serial.parity = 'n'
        s_serial.stopbits = 1

        s_connection.type = "gsm"
        # s_connection.id = "gsm连接"
        s_connection.id = self.generate_connection_id("cdma")
        s_connection.autoconnect = False
        s_connection.uuid = uuid.uuid4()
        s_connection.timestamp = time.time()

        s_ip4config.method = "auto"
        s_ip4config.clear_addresses()
        s_ip4config.clear_routes()

        s_ip4config.clear_dns()

        settings_dict = {"gsm":s_gsm.prop_dict,
                         "connection":s_connection.prop_dict,
                         "ipv4":s_ip4config.prop_dict,
                         "serial":s_serial.prop_dict,
                         "ppp":s_ppp.prop_dict
                         }

        return self.add_connection(settings_dict)

    def new_cdma_connection(self):
        s_connection = NMSettingConnection()
        s_cdma = NMSettingCdma()
        s_serial = NMSettingSerial()
        s_ppp = NMSettingPPP()
        s_ip4config = NMSettingIP4Config()

        s_cdma.number = "#777"
        s_cdma.username = "CARD"
        s_cdma.password = "CARD"

        s_serial.baud = 115200
        s_serial.bits = 8
        s_serial.parity = 'n'
        s_serial.stopbits = 1

        s_connection.type = "cdma"
        # s_connection.id = "cdma连接"
        s_connection.id = self.generate_connection_id("cdma")
        s_connection.autoconnect = False
        s_connection.uuid = uuid.uuid4()
        s_connection.timestamp = time.time()

        s_ip4config.method = "auto"
        s_ip4config.clear_addresses()
        s_ip4config.clear_routes()

        s_ip4config.clear_dns()

        settings_dict = {"cdma":s_cdma.prop_dict,
                         "connection":s_connection.prop_dict,
                         "ipv4":s_ip4config.prop_dict,
                         "serial":s_serial.prop_dict,
                         "ppp":s_ppp.prop_dict
                         }

        return self.add_connection(settings_dict)

    def new_vpn_l2tp_connection(self):
        s_connection = NMSettingConnection()
        s_vpn = NMSettingVpn()
        s_ip4config = NMSettingIP4Config()

        s_connection.type = "vpn"
        # s_connection.id = "l2tp连接"
        s_connection.id = self.generate_connection_id("vpn")
        s_connection.autoconnect = True
        s_connection.uuid = uuid.uuid4()
        s_connection.timestamp = time.time()

        s_vpn.service_type = "org.freedesktop.NetworkManager.l2tp"

        s_vpn.set_data_item("user", "ssh_lazycat")
        s_vpn.set_data_item("gateway", "95.143.43.70")
        s_vpn.set_data_item("password-flags", "0")

        s_vpn.set_secret_item("password","123456")

        s_ip4config.method = "auto"
        s_ip4config.clear_addresses()
        s_ip4config.clear_routes()

        s_ip4config.clear_dns()

        settings_dict = {"vpn":s_vpn.prop_dict,
                         "connection":s_connection.prop_dict,
                         "ipv4":s_ip4config.prop_dict
                         }
        #just for debug
        self.l2tp_settings_dict = settings_dict
        #just for debug

        return self.add_connection(settings_dict)

    def new_vpn_pptp_connection(self):
        s_connection = NMSettingConnection()
        s_vpn = NMSettingVpn()
        s_ip4config = NMSettingIP4Config()

        s_connection.type = "vpn"
        # s_connection.id = "pptp_conn"
        s_connection.id = self.generate_connection_id("vpn")
        s_connection.autoconnect = True
        s_connection.uuid = uuid.uuid4()
        s_connection.timestamp = time.time()

        s_vpn.service_type = "org.freedesktop.NetworkManager.pptp"

        s_vpn.set_data_item("user", "wosuopu")
        s_vpn.set_data_item("gateway", "98.126.157.70")
        s_vpn.set_data_item("password-flags", "0")
        s_vpn.set_data_item("require-mppe", "yes")

        s_vpn.set_secret_item("password","654321")

        s_ip4config.method = "auto"
        s_ip4config.clear_addresses()
        s_ip4config.clear_routes()
        s_ip4config.clear_dns()
        # s_ip4config.add_dns("202.114.88.10")
        # s_ip4config.add_dns_search("www.linuxdeepin.com")

        settings_dict = {"vpn":s_vpn.prop_dict,
                         "connection":s_connection.prop_dict,
                         "ipv4":s_ip4config.prop_dict
                         }
        #just for debug
        self.pptp_settings_dict = settings_dict
        #just for debug

        return self.add_connection(settings_dict)

    def get_can_modify(self):
        return self.properties["CanModify"]

    def get_hostname(self):
        return self.properties["Hostname"]

    def get_wired_connections(self):
        return filter(lambda x: x.settings_dict["connection"]["type"] == "802-3-ethernet", self.list_connections())

    def get_wired_active_connection(self):
        for conn in self.get_wired_connections():
            pass

    def get_wireless_connections(self):
        '''return wireless connections object'''
        return filter(lambda x: x.settings_dict["connection"]["type"] == "802-11-wireless", self.list_connections())

    def get_ssid_associate_connections(self, ssid):
        '''return wireless connection objects have the given ssid'''
        return filter(lambda x: TypeConvert.ssid_ascii2string(x.settings_dict["802-11-wireless"]["ssid"]) == ssid, 
                      self.get_wireless_connections())

    def get_ssid_not_associate_connections(self, ssid):
        return filter(lambda x: TypeConvert.ssid_ascii2string(x.settings_dict["802-11-wireless"]["ssid"]) != ssid, 
                      self.get_wireless_connections())
        
    def get_pppoe_connections(self):
        return filter(lambda x: x.settings_dict["connection"]["type"] == "pppoe", self.list_connections())

    def get_vpn_connections(self):
        return filter(lambda x: x.settings_dict["connection"]["type"] == "vpn", self.list_connections())
        
    def get_gsm_connections(self):
        return filter(lambda x: x.settings_dict["connection"]["type"] == "gsm", self.list_connections())

    def get_cdma_connections(self):
        return filter(lambda x: x.settings_dict["connection"]["type"] == "cdma", self.list_connections())

    def properties_changed_cb(self, prop_dict):
        self.init_nmobject_with_properties()

    def new_connection_cb(self, arg):
        self.emit("new-connection", arg)

    def connections_read_cb(self, user_data):
        self.emit("connections-read", user_data)

nm_remote_settings = NMRemoteSettings()

if __name__ == "__main__":
    nm_remote_settings = NMRemoteSettings()
    # nm_remote_settings.new_cdma_connection()
    # print nm_remote_settings.dbus_interface.ListConnections()
    # print nm_remote_settings.get_hostname()
    # print nm_remote_settings.get_can_modify()

    # nm_remote_settings.new_wired_connection()

    # NMRemoteConnection(nm_remote_settings.new_wireless_connection())
    # NMRemoteConnection(nm_remote_settings.new_pppoe_connection())

    # from nmclient import NMClient

    # remote_connection = nm_remote_settings.new_vpn_connection()
    # nmclient = NMClient()
    # device_path = nmclient.get_wireless_device()

    # from nmdevice import NMDevice
    # nmdevice = NMDevice(device_path, None)
    # specific_path = nmdevice.get_active_connection()
    
    # nmclient.activate_connection(remote_connection, device_path, specific_path)
