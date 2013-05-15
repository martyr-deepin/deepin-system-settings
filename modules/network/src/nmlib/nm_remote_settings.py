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
from nmcache import get_cache
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
import os
import glib
import ConfigParser 
import traceback

class NMRemoteSettings(NMObject):
    '''NMRemoteSettings'''

    def __init__(self):
        NMObject.__init__(self, "/org/freedesktop/NetworkManager/Settings", "org.freedesktop.NetworkManager.Settings")

        self.bus.add_signal_receiver(self.properties_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertiesChanged")
        self.prop_list = ["CanModify", "Hostname"]
        self.init_nmobject_with_properties()
        self.__init_network_config()

    def __init_network_config(self):
        if not os.path.exists(glib.get_user_config_dir()):
            os.mkdir(glib.get_user_config_dir())
        
        self.config_file = os.path.join(glib.get_user_config_dir(), "network.conf")
        if not os.path.exists(self.config_file):
            open(self.config_file, "w").close()

        self.cf = ConfigParser.RawConfigParser()
        self.cf.optionxform = str
        self.cf.read(self.config_file)

        if "conn_priority" not in self.cf.sections():
            self.cf.add_section("conn_priority")

        max_prio = 0
        for conn_uuid in map(lambda x: x.settings_dict["connection"]["uuid"], self.list_connections()):
            if conn_uuid not in self.cf.options("conn_priority"):
                self.cf.set("conn_priority", conn_uuid, 0)

            if self.cf.getint("conn_priority", conn_uuid) > max_prio:
                max_prio = self.cf.getint("conn_priority", conn_uuid)
        
        if max_prio >= 1024:
            for conn_uuid in self.cf.options("conn_priority"):
                self.cf.set("conn_priority", conn_uuid, int(self.cf.getint("conn_priority", conn_uuid)/2))

        self.cf.write(open(self.config_file, "w"))

    def list_connections(self):
        '''return connections object'''
        try:
            return filter(lambda x: "read-only" not in x.settings_dict["connection"] or not x.settings_dict["connection"]["read-only"], 
                            map(lambda x:get_cache().getobject(x), TypeConvert.dbus2py(self.dbus_method("ListConnections")))
                        )
        except:
            traceback.print_exc()
            return []

    def get_connection_by_uuid(self, uuid):
        return get_cache().getobject(self.dbus_method("GetConnectionByUuid", uuid))

    def save_hostname(self, hostname):
        self.dbus_method("SaveHostname", hostname)
    
    def add_connection(self, settings_dict):
        conn_path = self.dbus_method("AddConnection", settings_dict)
        if conn_path:
            nm_connection = get_cache().getobject(conn_path)
            nm_connection.settings_dict = settings_dict
            nm_connection.update()
            get_cache().new_object(conn_path)
            self.cf.set("conn_priority", nm_connection.settings_dict["connection"]["uuid"], 0)
            self.cf.write(open(self.config_file, "w"))
            return nm_connection
        else:
            return None

    def generate_connection_id(self, connection_type):
        from nls import _

        if connection_type == "wired":
            conn_list = self.get_wired_connections()
            conn_start = _("Wired config")
        elif connection_type == "wireless":
            conn_list = self.get_wireless_connections()
            conn_start = _("Wireless config")
        elif connection_type == "dsl":
            conn_list = self.get_pppoe_connections()
            conn_start = _("Dsl config")
        elif connection_type == "vpn":
            conn_list = self.get_vpn_connections()
            conn_start = _("VPN config")
        elif connection_type == "cdma":
            conn_list = self.get_cdma_connections()
            conn_start = _("CDMA config")
        elif connection_type == "gsm":
            conn_list = self.get_gsm_connections()
            conn_start = _("GSM config")
        else:
            return _("Config")

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
        new_connection.settings_dict = settings_dict    

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


        s_ip4config.method = "auto"
        s_ip4config.clear_addresses()
        s_ip4config.clear_routes()
        s_ip4config.clear_dns()

        s_ip6config.method = "auto"
        s_ip6config.routes = []
        s_ip6config.dns = []
        s_ip6config.addresses = []
        
        settings_dict = {"802-11-wireless":s_wireless.prop_dict,
                         "connection":s_connection.prop_dict,
                         "ipv4":s_ip4config.prop_dict
                         ,"ipv6":s_ip6config.prop_dict
                         }
        if key_mgmt:
            s_wireless.security = "802-11-wireless-security"
            s_wireless_security.key_mgmt = key_mgmt
            settings_dict["802-11-wireless-security"] = s_wireless_security.prop_dict
            settings_dict["802-11-wireless-security"]["psk"] = "Password"

        from nmutils.nmconnection import NMConnection
        new_connection = NMConnection()
        for item in settings_dict.iterkeys():
            new_connection.get_setting(item).prop_dict = settings_dict[item]
        new_connection.settings_dict = settings_dict    

        return new_connection    

    def new_adhoc_connection(self, ssid = None, key_mgmt = "none"):
        ###Please pass key_mgmt as the wireless isn't privacy
        s_connection = NMSettingConnection()
        s_wireless = NMSettingWireless()
        s_wireless_security = NMSettingWirelessSecurity()
        s_ip4config = NMSettingIP4Config()

        s_connection.type = "802-11-wireless"
        s_connection.id = self.generate_connection_id("wireless")
        s_connection.autoconnect = True
        s_connection.uuid = uuid.uuid4()
        s_connection.timestamp = time.time()
        s_connection.permissions = []

        s_wireless.mode = "adhoc"
        s_wireless.ssid = ssid

        if key_mgmt:
            s_wireless.security = "802-11-wireless-security"
            s_wireless_security.key_mgmt = key_mgmt
            s_wireless_security.auth_alg = "open"

        s_ip4config.clear_addresses()
        s_ip4config.clear_routes()
        s_ip4config.clear_dns()
        s_ip4config.method = "shared"

        settings_dict = {"802-11-wireless":s_wireless.prop_dict,
                         "802-11-wireless-security":s_wireless_security.prop_dict,
                         "connection":s_connection.prop_dict,
                         "ipv4":s_ip4config.prop_dict
                         }
        # settings_dict["802-11-wireless-security"]["psk"] = "Password"

        from nmutils.nmconnection import NMConnection
        new_connection = NMConnection()
        for item in settings_dict.iterkeys():
            new_connection.get_setting(item).prop_dict = settings_dict[item]
        new_connection.settings_dict = settings_dict    

        return new_connection    

    def new_pppoe_connection(self):
        s_connection = NMSettingConnection()
        s_wired = NMSettingWired()
        s_ip4config = NMSettingIP4Config()
        s_pppoe = NMSettingPPPOE()
        s_ppp = NMSettingPPP()

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
        
        s_pppoe.username = ""
        s_pppoe.password = ""

        settings_dict = {"802-3-ethernet":s_wired.prop_dict,
                         "connection":s_connection.prop_dict,
                         "ipv4":s_ip4config.prop_dict,
                         "pppoe":s_pppoe.prop_dict,
                         "ppp":s_ppp.prop_dict
                         }

        from nmutils.nmconnection import NMConnection
        new_connection = NMConnection()
        for item in settings_dict.iterkeys():
            new_connection.get_setting(item).prop_dict = settings_dict[item]
        new_connection.settings_dict = settings_dict    

        return new_connection    
        
    def new_gsm_connection(self, username = "", password = "", apn = ""):
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
        new_connection.settings_dict = settings_dict    

        return new_connection    

    def new_cdma_connection(self, username = "", password = ""):
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
        new_connection.settings_dict = settings_dict    

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
        new_connection.settings_dict = settings_dict    

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
        new_connection.settings_dict = settings_dict    

        return new_connection    

    def new_connection_finish(self, settings_dict, connection_type = "802-3-ethernet"):
        return self.add_connection(settings_dict)

    def get_can_modify(self):
        return self.properties["CanModify"]

    def get_hostname(self):
        return self.properties["Hostname"]

    def get_wired_connections(self):
        try:
            return filter(lambda x: x.settings_dict["connection"]["type"] == "802-3-ethernet", self.list_connections())
        except:
            return []

    def get_wired_active_connection(self):
        pass

    def get_wireless_connections(self):
        '''return wireless connections object'''
        try:
            return filter(lambda x: x.settings_dict["connection"]["type"] == "802-11-wireless", self.list_connections())
        except:
            return []

    def get_ssid_associate_connections(self, ssid):
        '''return wireless connection objects have the given ssid'''
        try:
            return filter(lambda x: TypeConvert.ssid_ascii2string(x.settings_dict["802-11-wireless"]["ssid"]) == ssid, 
                      self.get_wireless_connections())
        except:
            return []

    def get_ssid_not_associate_connections(self, ssid):
        try:
            return filter(lambda x: TypeConvert.ssid_ascii2string(x.settings_dict["802-11-wireless"]["ssid"]) != ssid, 
                        self.get_wireless_connections())
        except:
            return []

    def get_pppoe_connections(self):
        try:
            return filter(lambda x: x.settings_dict["connection"]["type"] == "pppoe", self.list_connections())
        except:
            return []

    def get_vpn_connections(self):
        try:
            return filter(lambda x: x.settings_dict["connection"]["type"] == "vpn", self.list_connections())
        except:
            return []

    def get_gsm_connections(self):
        try:
            return filter(lambda x: x.settings_dict["connection"]["type"] == "gsm", self.list_connections())
        except:
            return []

    def get_cdma_connections(self):
        try:
            return filter(lambda x: x.settings_dict["connection"]["type"] == "cdma", self.list_connections())
        except:
            return []

    def properties_changed_cb(self, prop_dict):
        self.init_nmobject_with_properties()

import threading
class ThreadVPNSpec(threading.Thread):
    def __init__(self, connection, active_conn_creat_cb):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.connection = connection
        self.active_conn_creat_cb = active_conn_creat_cb
        self.run_flag = True
        self.succeed = False

    def run(self):
        nmclient = get_cache().getobject("/org/freedesktop/NetworkManager")
        for active_conn in nmclient.get_active_connections():
            if active_conn.get_state() == 2:
                for device in active_conn.get_devices():
                    if self.run_flag:
                        try:
                            active = nmclient.activate_connection(self.connection.object_path,
                                                                  device.object_path,
                                                                  active_conn.object_path)
                            self.active_conn_creat_cb(active)
            
                            vpn_connection = get_cache().get_spec_object(active.object_path)

                            while(vpn_connection.get_vpnstate() < 5 and self.run_flag):
                                time.sleep(1)
                            
                            if vpn_connection.get_vpnstate() == 5:
                                self.stop_run()
                                self.succeed = True
                                return True
                            else:
                                continue
                        except:
                            pass
                    else:
                        break
            else:
                continue

        return False
    
    def stop_run(self):
        self.run_flag = False

if __name__ == "__main__":
    nm_remote_settings = NMRemoteSettings()
