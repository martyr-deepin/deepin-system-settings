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

import gobject
import copy
from nmsetting import NMSetting
from nmsetting_wired import NMSettingWired
from nmsetting_wireless import NMSettingWireless
from nmsetting_adsl import NMSettingAdsl
from nmsetting_ppp import NMSettingPPP
from nmsetting_pppoe import NMSettingPPPOE
from nmsetting_vlan import NMSettingVlan
from nmsetting_bond import NMSettingBond
from nmsetting_bluetooth import NMSettingBluetooth
from nmsetting_serial import NMSettingSerial
from nmsetting_wimax import NMSettingWimax
from nmsetting_vpn import NMSettingVpn
from nmsetting_802_1x import NMSetting8021x
from nmsetting_connection import NMSettingConnection
from nmsetting_ip4config import NMSettingIP4Config
from nmsetting_ip6config import NMSettingIP6Config
from nmsetting_gsm import NMSettingGsm
from nmsetting_cdma import NMSettingCdma
from nmsetting_olpcmesh import NMSettingOlpcMesh
from nmsetting_infiniband import NMSettingInfiniband
from nmsetting_wireless_security import NMSettingWirelessSecurity

class NMConnection(gobject.GObject):
    '''NMConnection'''

    # __gsignals__ = {
    #     "secrets-cleared":(gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE, (gobject.TYPE_NONE,)),
    #     "secrets-updated":(gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE,(str,)),
    #     }
    def __init__(self):
        gobject.GObject.__init__(self)

        self.nm_setting_wired = ""
        self.nm_setting_wireless = ""
        self.nm_setting_wireless_security = ""
        self.nm_setting_wimax = ""
        self.nm_setting_vpn = ""
        self.nm_setting_vlan = ""
        self.nm_setting_serial = ""
        self.nm_setting_ppp = ""
        self.nm_setting_pppoe = ""
        self.nm_setting_ip6_config = ""
        self.nm_setting_ip4_config = ""
        self.nm_setting_infiniband = ""
        self.nm_setting_olpc_mesh = ""
        self.nm_setting_gsm = ""
        self.nm_setting_cdma = ""
        self.nm_setting_connection = ""
        self.nm_setting_bond = ""
        self.nm_setting_bluetooth = ""
        self.nm_setting_802_1x = ""
        self.nm_setting_adsl = ""

        self.settings_dict = {} ####{name:{prop_key:prop_value}, initied in NMRemoteConnection
        self.settings_info = {} ####{name:[type, priority, get_method, base_type]}
        self.init_settings_info()

    def init_settings_info(self):
        self.settings_info["802-3-ethernet"] = [NMSettingWired, 0, "get_setting_wired", "nm_setting_wired", False]
        self.settings_info["802-11-wireless"] = [NMSettingWireless, 1, "get_setting_wireless", "nm_setting_wireless", False]
        self.settings_info["802-11-wireless-security"] = [NMSettingWirelessSecurity, 1, "get_setting_wireless_security",
                                                          "nm_setting_wireless_security", True]
        self.settings_info["wimax"] = [NMSettingWimax, 1, "get_setting_wimax", "nm_setting_wimax", True]
        self.settings_info["vpn"] = [NMSettingVpn, 1 ,"get_setting_vpn", "nm_setting_vpn", True]
        self.settings_info["vlan"] = [NMSettingVlan, 1, "get_setting_vlan", "nm_setting_vlan",True]
        self.settings_info["serial"] = [NMSettingSerial, 1, "get_setting_serial", "nm_setting_serial",True]
        self.settings_info["ppp"] = [NMSettingPPP, 1, "get_setting_ppp", "nm_setting_ppp", True]
        self.settings_info["pppoe"] = [NMSettingPPPOE, 1, "get_setting_pppoe", "nm_setting_pppoe", True]
        self.settings_info["ipv6"] = [NMSettingIP6Config, 1, "get_setting_ip6_config", "nm_setting_ip6_config", True]
        self.settings_info["ipv4"] = [NMSettingIP4Config, 1, "get_setting_ip4_config", "nm_setting_ip4_config", True]
        self.settings_info["infiniband"] = [NMSettingInfiniband, 1, "get_setting_infiniband", "nm_setting_infiniband", True]
        self.settings_info["802-11-olpc-mesh"] = [NMSettingOlpcMesh, 1, "get_setting_olpc_mesh", "nm_setting_olpc_mesh", True]
        self.settings_info["gsm"] = [NMSettingGsm, 1, "get_setting_gsm", "nm_setting_gsm", True]
        self.settings_info["cdma"] = [NMSettingCdma, 1, "get_setting_cdma", "nm_setting_cdma", True]
        self.settings_info["connection"] = [NMSettingConnection, 1, "get_setting_connection", "nm_setting_connection", True]
        self.settings_info["bond"] = [NMSettingBond, 1, "get_setting_bond", "nm_setting_bond", True]
        self.settings_info["bluetooth"] = [NMSettingBluetooth, 1, "get_setting_bluetooth", "nm_setting_bluetooth", True]
        self.settings_info["802-1x"] = [NMSetting8021x, 1, "get_setting_802_1x", "nm_setting_802_1x", True]
        self.settings_info["adsl"] = [NMSettingAdsl, 1, "get_setting_adsl", "nm_setting_adsl", True]

    # def get_setting(self, setting_name):
    #     return getattr(self, self.settings_info[setting_name][2])()

    def get_setting(self, setting_name):
        if setting_name not in self.settings_info.iterkeys():
            return "unknown setting_name"
        else:
            if not getattr(self, self.settings_info[setting_name][3]):
                setattr(self, self.settings_info[setting_name][3], apply(self.settings_info[setting_name][0]))
            return getattr(self, self.settings_info[setting_name][3])    

    def get_setting_type(self, setting_name):
        return self.settings_info[setting_name][0]

    def get_setting_priority(self, setting_name):
        return self.settings_info[setting_name][1]

    def get_setting_base_type(self, setting_name):
        return self.settings_info[setting_name][4]

    def add_setting(self, setting):
        if isinstance(setting, NMSetting):
            if setting.name not in self.settings_info.iterkeys():
                print "error:%s unknown setting" % setting.name
            elif setting.name not in self.settings_dict.iterkeys():
                self.settings_dict[setting.name] = setting
            else:
                print "error:%s has already added" % setting.name
        else:
            print "error:%s is not a type of NMSetting" % setting.name

    def remove_setting(self, setting_name):
        if setting_name not in self.settings_dict.iterkeys():
            print "error:%s hadn't been added" % setting_name
        else:
            del self.settings_dict[setting_name]

    def update_setting(self, setting):
        self.remove_setting(setting.name)
        self.add_setting(setting)
        setattr(self, self.settings_info[setting.name][3], setting)

    def replace_settings(self, new_settings):
        self.settings_dict.clear()
        self.settings_dict = copy.deepcopy(new_settings)
        return self.settings_dict

    def update_secrets(self, setting_name, secrets_dict):
        if setting_name:
            setting = self.get_setting(setting_name)
            if not setting:
                return False
            setting.update_secrets(secrets_dict)
        else:
            pass

    def need_secrets(self, hints):
        pass
    
    def clear_secrets(self):
        for setting in self.settings_dict.values():
            setting.clear_secrets()
	# g_signal_emit (connection, signals[SECRETS_CLEARED], 0);

    def clear_secrets_with_flags(self, func, user_data):
        for setting in self.settings_dict.values():
            setting.clear_secrets_with_flags()
	# g_signal_emit (connection, signals[SECRETS_CLEARED], 0);

    def get_uuid(self):
        return self.get_setting["connection"].get_uuid()

    def get_id(self):
        return self.get_setting["connection"].get_id()


    # def get_setting_connection(self):
    #     if not self.nm_setting_connection:
    #         self.nm_setting_connection = NMSettingConnection()

    #     return self.nm_setting_connection

    # def get_setting_802_1x(self):
    #     if not self.nm_setting_802_1x:
    #         self.nm_setting_802_1x = NMSetting8021x()

    #     return self.nm_setting_802_1x

    # def get_setting_adsl(self):
    #     if not self.nm_setting_adsl:
    #         self.nm_setting_adsl = NMSettingAdsl()

    #     return self.nm_setting_adsl

    # def get_setting_bluetooth(self):
    #     if not self.nm_setting_bluetooth:
    #         self.nm_setting_bluetooth = NMSettingBluetooth()

    #     return self.nm_setting_bluetooth

    # def get_setting_bond(self):
    #     if not self.nm_setting_bond:
    #         self.nm_setting_bond = NMSettingBond()

    #     return self.nm_setting_bond

    # def get_setting_cdma(self):
    #     if not self.nm_setting_cdma:
    #         self.nm_setting_cdma = NMSettingCdma()

    #     return self.nm_setting_cdma

    # def get_setting_gsm(self):
    #     if not self.nm_setting_gsm:
    #         self.nm_setting_gsm = NMSettingGsm()

    #     return self.nm_setting_gsm

    # def get_setting_infiniband(self):
    #     if not self.nm_setting_infiniband:
    #         self.nm_setting_infiniband = NMSettingInfiniband()

    #     return self.nm_setting_infiniband

    # def get_setting_ip4_config(self):
    #     if not self.nm_setting_ip4_config:
    #         self.nm_setting_ip4_config = NMSettingIP4Config()

    #     return self.nm_setting_ip4_config

    # def get_setting_ip6_config(self):
    #     if not self.nm_setting_ip6_config:
    #         self.nm_setting_ip6_config = NMSettingIP6Config()

    #     return self.nm_setting_ip6_config

    # def get_setting_olpc_mesh(self):
    #     if not self.nm_setting_olpc_mesh:
    #         self.nm_setting_olpc_mesh = NMSettingOlpcMesh()

    #     return self.nm_setting_olpc_mesh

    # def get_setting_ppp(self):
    #     if not self.nm_setting_ppp:
    #         self.nm_setting_ppp = NMSettingPPP()

    #     return self.nm_setting_ppp

    # def get_setting_pppoe(self):
    #     if not self.nm_setting_pppoe:
    #         self.nm_setting_pppoe = NMSettingPPPOE()

    #     return self.nm_setting_pppoe

    # def get_setting_serial(self):
    #     if not self.nm_setting_serial:
    #         self.nm_setting_serial = NMSettingSerial()

    #     return self.nm_setting_serial

    # def get_setting_vlan(self):
    #     if not self.nm_setting_vlan:
    #         self.nm_setting_vlan = NMSettingVlan()

    #     return self.nm_setting_vlan

    # def get_setting_vpn(self):
    #     if not self.nm_setting_vpn:
    #         self.nm_setting_vpn = NMSettingVpn()

    #     return self.nm_setting_vpn

    # def get_setting_wimax(self):
    #     if not self.nm_setting_wimax:
    #         self.nm_setting_wimax = NMSettingWimax()

    #     return self.nm_setting_wimax

    # def get_setting_wired(self):
    #     if not self.nm_setting_wired:
    #         self.nm_setting_wired = NMSettingWired()

    #     return self.nm_setting_wired

    # def get_setting_wireless(self):
    #     if not self.nm_setting_wireless:
    #         self.nm_setting_wireless = NMSettingWireless()

    #     return self.nm_setting_wireless

    # def get_setting_wireless_security(self):
    #     if not self.nm_setting_wireless_security:
    #         self.nm_setting_wireless_security = NMSettingWirelessSecurity()

    #     return self.nm_setting_wireless_security

    ###Signals###
    def secrets_cleared_cb(self):
        pass

    def secrets_updated_cb(self, setting_name):
        pass
