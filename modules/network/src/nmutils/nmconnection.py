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
from nmlib.nm_utils import TypeConvert

class NMConnection(gobject.GObject):
    '''NMConnection'''

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

        self.settings_dict = {} ####{name:{prop_key:prop_value}, initied in NMRemoteConnection, read from this
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

    def get_setting(self, setting_name):
        if setting_name not in self.settings_info.iterkeys():
            return "unknown setting_name"
        else:
            if not getattr(self, self.settings_info[setting_name][3]):
                setattr(self, self.settings_info[setting_name][3], apply(self.settings_info[setting_name][0]))
            return getattr(self, self.settings_info[setting_name][3])    

    def check_setting_finish(self):
        ###check if user complete his setting, avoid the missing property exception
        info_dict = TypeConvert.dbus2py(self.settings_dict)
        try:
            ###wired
            if info_dict["connection"]["type"] == "802-3-ethernet":
                if info_dict["ipv4"]["method"] == "manual" and not info_dict["ipv4"]["addresses"]:
                    return False

                return True
            ###wireless
            elif info_dict["connection"]["type"] == "802-11-wireless":
                if info_dict["ipv4"]["method"] == "manual" and not info_dict["ipv4"]["addresses"]:
                    return False

                if len(info_dict["802-11-wireless"]["ssid"]) == 0:
                    return False

                if "802-11-wireless-security" in info_dict.iterkeys():
                    if info_dict["802-11-wireless-security"]["key-mgmt"] == "none":

                        ####wep
                        if "wep-tx-keyidx" in info_dict["802-11-wireless-security"].iterkeys():
                            if info_dict["802-11-wireless-security"]["wep-tx-keyidx"] == 0:
                                if not info_dict["802-11-wireless-security"]["wep-key0"]:
                                    return False

                            elif info_dict["802-11-wireless-security"]["wep-tx-keyidx"] == 1:
                                if not info_dict["802-11-wireless-security"]["wep-key1"]:
                                    return False

                            elif info_dict["802-11-wireless-security"]["wep-tx-keyidx"] == 2:
                                if not info_dict["802-11-wireless-security"]["wep-key2"]:
                                    return False

                            elif info_dict["802-11-wireless-security"]["wep-tx-keyidx"] == 3:
                                if not info_dict["802-11-wireless-security"]["wep-key3"]:
                                    return False
                            else:
                                    return False
                        else:
                            if not info_dict["802-11-wireless-security"]["wep-key0"]:
                                return False

                        ###psk    
                    elif info_dict["802-11-wireless-security"]["key-mgmt"] == "wpa-psk":
                        if not info_dict["802-11-wireless-secrets"]["psk"]:
                            return False

                    elif info_dict["802-11-wireless-security"]["key-mgmt"] == "ieee8021x":
                        # currently not support
                        return False

                    elif info_dict["802-11-wireless-security"]["key-mgmt"] == "wpa-eap":
                        # currently not support
                        return False
                    else:
                        return False

                return True

            elif info_dict["connection"]["type"] == "pppoe":
                if info_dict["ipv4"]["method"] == "manual" and not info_dict["ipv4"]["addresses"]:
                    return False

                if not info_dict["pppoe"]["username"]:
                    return False

                return True

            elif info_dict["connection"]["type"] == "vpn":
                if info_dict["ipv4"]["method"] == "manual" and not info_dict["ipv4"]["addresses"]:
                    return False

                if not info_dict["vpn"]["secrets"] or not info_dict["vpn"]["data"]:
                    return False

                return True

            elif info_dict["connection"]["type"] == "cdma":
                if info_dict["ipv4"]["method"] == "manual" and not info_dict["ipv4"]["addresses"]:
                    return False

                return True

            elif info_dict["connection"]["type"] == "gsm":
                if info_dict["ipv4"]["method"] == "manual" and not info_dict["ipv4"]["addresses"]:
                    return False

                return True

            else:
                return False
        except:        
            return False

    def check_setting_commit(self):
        ###delete invalid setting property before update
        info_dict = TypeConvert.dbus2py(self.settings_dict)
        try:
            if info_dict["connection"]["type"] == "802-3-ethernet":
                if not self.get_setting("802-3-ethernet").wired_valid():
                    ###or raise exception
                    return False
                self.get_setting("ipv4").adapt_ip4config_commit()

                if "ipv6" in info_dict.iterkeys():
                    self.get_setting("ipv6").apapt_ip6config_commit()

            elif info_dict["connection"]["type"] == "802-11-wireless":
                self.get_setting("802-11-wireless").adapt_wireless_commit()

                if "802-11-wireless-security" in info_dict.iterkeys():
                    self.get_setting("802-11-wireles-security").adapt_wireless_security_commit()

                self.get_setting("ipv4").adapt_ip4config_commit()

                if "ipv6" in info_dict.iterkeys():
                    self.get_setting("ipv6").apapt_ip6config_commit()

            elif info_dict["connection"]["type"] == "pppoe":
                if not self.get_setting("802-3-ethernet").wired_valid():
                    return False
                self.get_setting("ipv4").adapt_ip4config_commit()

                if "ipv6" in info_dict.iterkeys():
                    self.get_setting("ipv6").apapt_ip6config_commit()

            elif info_dict["connection"]["type"] == "vpn":
                pass
            elif info_dict["connection"]["type"] == "cdma":
                pass
            elif info_dict["connection"]["type"] == "gsm":
                pass
            else:
                print "invalid connection_type"
        except:        
            pass

    def guess_secret_info(self):
        '''guess_secret_info'''
        info_dict = TypeConvert.dbus2py(self.settings_dict)

        if "vpn" in info_dict.iterkeys():
            self.secret_setting_name = "vpn"
            self.secret_method = "password"
            return (self.secret_setting_name, self.secret_method)

        elif "pppoe" in info_dict.iterkeys() and "802-3-ethernet" in info_dict.iterkeys():
            self.secret_setting_name = "pppoe"
            self.secret_method = "password"
            return (self.secret_setting_name, self.secret_method)

        elif "802-11-wireless" in info_dict.iterkeys():
            ###for wireless no password
            if not "802-11-wireless-security" in info_dict.iterkeys():
                self.secret_setting_name = None
                self.secret_method = None
                return (self.secret_setting_name, self.secret_method)

            ###for wireless has password
            self.secret_setting_name = "802-11-wireless-security"

            if "key-mgmt" in info_dict["802-11-wireless-security"].iterkeys():
                ###for wpa/psk
                if info_dict["802-11-wireless-security"]["key-mgmt"] == "wpa-psk":
                    self.secret_method = "psk"
                    return (self.secret_setting_name, self.secret_method)
                    
                elif info_dict["802-11-wireless-security"]["key-mgmt"] == "none":
                ###for wep    
                    if "wep-key-type" in info_dict["802-11-wireless-security"].iterkeys():
                        if "wep-tx-keyidx" in info_dict["802-11-wireless-security"].iterkeys():
                            if info_dict["802-11-wireless-security"]["wep-tx-keyidx"] == 0:
                                self.secret_method = "wep-key0"
                            elif info_dict["802-11-wireless-security"]["wep-tx-keyidx"] == 1:
                                self.secret_method = "wep-key1"
                            elif info_dict["802-11-wireless-security"]["wep-tx-keyidx"] == 2:
                                self.secret_method = "wep-key2"
                            elif info_dict["802-11-wireless-security"]["wep-tx-keyidx"] == 3:
                                self.secret_method = "wep-key3"
                            else:
                                print "unsupported wep key idx"
                                self.secret_method = None

                            return (self.secret_setting_name, self.secret_method)    
                        else:
                            ###set default for wep key index
                            self.secret_method = "wep-key0"
                            return (self.secret_setting_name, self.secret_method)
                    else:
                        # print "must have wep-key-type to indicate wep connection"
                        self.secret_method = None
                        return (self.secret_setting_name, self.secret_method)

                ###for wpa    
                elif info_dict["802-11-wireless-security"]["key-mgmt"] == "wpa-eap":
                    # print "no agent available for wpa-eap"
                    self.secret_method = None
                    return (self.secret_setting_name, self.secret_method)

                elif info_dict["802-11-wireless-security"]["key-mgmt"] == "ieee8021x":
                    if "auth-alg" in info_dict["802-11-wireless-security"].iterkeys():
                        if info_dict["802-11-wireless-security"]["auth-alg"] == "leap":
                            self.secret_method = "leap-password"
                            return (self.secret_setting_name, self.secret_method)
                    else:
                        # print "no ageent available for dynamic wep"
                        self.secret_method = None
                        return (self.secret_setting_name, self.secret_method)
                else:
                    # print "unknown key mgmt"
                    self.secret_method = None
                    return (self.secret_setting_name, self.secret_method)

            else:
                # print "must have key mgmt for 802.11 wireless security"
                self.secret_method = None
                return (self.secret_setting_name, self.secret_method)

        elif "gsm" in info_dict.iterkeys():
            self.secret_setting_name = "gsm"
            self.secret_method = "password"
            return (self.secret_setting_name, self.secret_method)

        elif "802-3-ethernet" in info_dict.iterkeys():
            self.secret_setting_name = None
            self.secret_method = None
            return (self.secret_setting_name, self.secret_method)

        elif "ppp" in info_dict.iterkeys():
            self.secret_setting_name = ""
            self.secret_method = ""
            return (self.secret_setting_name, self.secret_method)

        elif "802-1x" in info_dict.iterkeys():
            self.secret_setting_name = ""
            self.secret_method = ""
            return (self.secret_setting_name, self.secret_method)

        elif "cdma" in info_dict.iterkeys():
            self.secret_setting_name = "cdma"
            self.secret_method = "password"
            return (self.secret_setting_name, self.secret_method)

        else:
            self.secret_setting_name = None
            self.secret_method = None
            return (self.secret_setting_name, self.secret_method)
