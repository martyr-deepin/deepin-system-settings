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

    def __init__(self):
        NMObject.__init__(self, "/org/freedesktop/NetworkManager/Settings", "org.freedesktop.NetworkManager.Settings")

        self.bus.add_signal_receiver(self.properties_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertiesChanged")

        self.init_nmobject_with_properties()

    def list_connections(self):
        '''return connections object'''
        conns = self.dbus_method("ListConnections")
        if conns:
            return map(lambda x:cache.getobject(x), TypeConvert.dbus2py(conns))
        else:
            return []

    def get_connection_by_uuid(self, uuid):
        return cache.getobject(self.dbus_method("GetConnectionByUuid", uuid))

    def save_hostname(self, hostname):
        self.dbus_method("SaveHostname", hostname)
    
    def add_connection(self, settings_dict):
        conn_path = self.dbus_method("AddConnection", settings_dict)
        if conn_path:
            return cache.getobject(conn_path)
        else:
            return None

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
            conn_start = "CDMA连接"
        elif connection_type == "gsm":
            conn_list = self.get_gsm_connections()
            conn_start = "GSM连接"
        else:
            return "新建连接"

        index_list = [0, ]
        if conn_list:
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

        from nmutils.nmconnection import NMConnection
        new_connection = NMConnection()
        for item in settings_dict.iterkeys():
            new_connection.get_setting(item).prop_dict = settings_dict[item]

        return new_connection    

    def new_wireless_connection(self, ssid = None, key_mgmt = "wpa-psk"):
        ###Please pass key_mgmt as the wireless isn't privacy
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
        s_connection.permissions = []

        s_wireless.mode = "infrastructure"
        s_wireless.ssid = ssid

        if key_mgmt:
            s_wireless.security = "802-11-wireless-security"
            s_wireless_security.key_mgmt = key_mgmt

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

        from nmutils.nmconnection import NMConnection
        new_connection = NMConnection()
        for item in settings_dict.iterkeys():
            new_connection.get_setting(item).prop_dict = settings_dict[item]

        return new_connection    

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

        from nmutils.nmconnection import NMConnection
        new_connection = NMConnection()
        for item in settings_dict.iterkeys():
            new_connection.get_setting(item).prop_dict = settings_dict[item]

        return new_connection    
        
    def new_gsm_connection(self, username = "username", password = "password", apn = "apn"):
        s_connection = NMSettingConnection()
        s_gsm = NMSettingGsm()
        s_serial = NMSettingSerial()
        s_ppp = NMSettingPPP()
        s_ip4config = NMSettingIP4Config()

        s_gsm.number = "*99#"
        s_gsm.username = username
        s_gsm.password = password
        s_gsm.apn = apn

        s_serial.baud = 115200
        s_serial.bits = 8
        s_serial.parity = 'n'
        s_serial.stopbits = 1

        s_connection.type = "gsm"
        # s_connection.id = "gsm连接"
        s_connection.id = self.generate_connection_id("gsm")
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

        from nmutils.nmconnection import NMConnection
        new_connection = NMConnection()
        for item in settings_dict.iterkeys():
            new_connection.get_setting(item).prop_dict = settings_dict[item]

        return new_connection    

    def new_cdma_connection(self, username = "username", password = "password"):
        s_connection = NMSettingConnection()
        s_cdma = NMSettingCdma()
        s_serial = NMSettingSerial()
        s_ppp = NMSettingPPP()
        s_ip4config = NMSettingIP4Config()

        s_cdma.number = "#777"
        s_cdma.username = username
        s_cdma.password = password

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

        from nmutils.nmconnection import NMConnection
        new_connection = NMConnection()
        for item in settings_dict.iterkeys():
            new_connection.get_setting(item).prop_dict = settings_dict[item]

        return new_connection    

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

        s_vpn.set_data_item("user", "")
        s_vpn.set_data_item("gateway", "")
        s_vpn.set_data_item("password-flags", "0")

        s_vpn.set_secret_item("password","")

        s_ip4config.method = "auto"
        s_ip4config.clear_addresses()
        s_ip4config.clear_routes()

        s_ip4config.clear_dns()

        settings_dict = {"vpn":s_vpn.prop_dict,
                         "connection":s_connection.prop_dict,
                         "ipv4":s_ip4config.prop_dict
                         }

        from nmutils.nmconnection import NMConnection
        new_connection = NMConnection()
        for item in settings_dict.iterkeys():
            new_connection.get_setting(item).prop_dict = settings_dict[item]

        return new_connection    

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

        s_vpn.set_data_item("user", "")
        s_vpn.set_data_item("gateway", "")
        s_vpn.set_data_item("password-flags", "0")
        s_vpn.set_data_item("require-mppe", "yes")
        s_vpn.set_data_item("refuse-eap", "yes")

        s_vpn.set_secret_item("password","")

        s_ip4config.method = "auto"
        s_ip4config.clear_addresses()
        s_ip4config.clear_routes()
        s_ip4config.clear_dns()

        settings_dict = {"vpn":s_vpn.prop_dict,
                         "connection":s_connection.prop_dict,
                         "ipv4":s_ip4config.prop_dict
                         }

        from nmutils.nmconnection import NMConnection
        new_connection = NMConnection()
        for item in settings_dict.iterkeys():
            new_connection.get_setting(item).prop_dict = settings_dict[item]

        return new_connection    

    def new_connection_finish(self, settings_dict, connection_type):

        return self.add_connection(settings_dict)

    def get_can_modify(self):
        return self.properties["CanModify"]

    def get_hostname(self):
        return self.properties["Hostname"]

    def get_wired_connections(self):
        if self.list_connections():
            return filter(lambda x: x.settings_dict["connection"]["type"] == "802-3-ethernet", self.list_connections())
        else:
            return []

    def get_wired_active_connection(self):
        for conn in self.get_wired_connections():
            pass

    def get_wireless_connections(self):
        '''return wireless connections object'''
        if self.list_connections():
            return filter(lambda x: x.settings_dict["connection"]["type"] == "802-11-wireless", self.list_connections())
        else:
            return []

    def get_ssid_associate_connections(self, ssid):
        '''return wireless connection objects have the given ssid'''
        if self.get_wireless_connections():
            return filter(lambda x: TypeConvert.ssid_ascii2string(x.settings_dict["802-11-wireless"]["ssid"]) == ssid, 
                      self.get_wireless_connections())
        else:
            return []

    def get_ssid_not_associate_connections(self, ssid):
        if self.get_wireless_connections():
            return filter(lambda x: TypeConvert.ssid_ascii2string(x.settings_dict["802-11-wireless"]["ssid"]) != ssid, 
                      self.get_wireless_connections())
        else:
            return []
    def get_pppoe_connections(self):
        if self.list_connections():
            return filter(lambda x: x.settings_dict["connection"]["type"] == "pppoe", self.list_connections())
        else:
            return []

    def get_vpn_connections(self):
        if self.list_connections():
            return filter(lambda x: x.settings_dict["connection"]["type"] == "vpn", self.list_connections())
        else:
            return []

    def get_gsm_connections(self):
        if self.list_connections():
            return filter(lambda x: x.settings_dict["connection"]["type"] == "gsm", self.list_connections())
        else:
            return []

    def get_cdma_connections(self):
        if self.list_connections():
            return filter(lambda x: x.settings_dict["connection"]["type"] == "cdma", self.list_connections())
        else:
            return []

    def properties_changed_cb(self, prop_dict):
        self.init_nmobject_with_properties()

if __name__ == "__main__":
    nm_remote_settings = NMRemoteSettings()
