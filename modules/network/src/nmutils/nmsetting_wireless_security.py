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

import dbus
from nmsetting import NMSetting
from nmlib.nm_utils import TypeConvert

class NMSettingWirelessSecurity (NMSetting):
    '''NMSettingWirelessSecurity'''

    def __init__(self):
        NMSetting.__init__(self)

        self.name = "802-11-wireless-security"

    @property    
    def key_mgmt(self):
        if "key-mgmt" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["key-mgmt"])

    @key_mgmt.setter
    def key_mgmt(self, new_key_mgmt):
        if new_key_mgmt in ["none", "ieee8021x", "wpa-none", "wpa-psk", "wpa-eap"]:
            self.prop_dict["key-mgmt"] = TypeConvert.py2_dbus_string(new_key_mgmt)

    @property
    def proto(self):
        if "proto" not in self.prop_dict.iterkeys():
            self.clear_proto()
        return TypeConvert.dbus2py(self.prop_dict["proto"])

    @proto.setter
    def proto(self, new_proto):
        self.prop_dict["proto"] = TypeConvert.py2_dbus_array(new_proto)
    
    def add_proto(self, proto):
        if proto not in self.prop_dict["proto"] and proto in ["wpa", "rsn"]:
            self.prop_dict.append(proto)

    def remove_proto(self, proto):        
        if proto in self.prop_dict["proto"]:
            self.prop_dict["proto"].remove(proto)

    def clear_proto(self):
        self.prop_dict["proto"] = dbus.Array([], signature = dbus.Signature('s'))

    @property
    def pairwise(self):
        if "pairwise" not in self.prop_dict.iterkeys():
            self.clear_pairwise()
        return TypeConvert.dbus2py(self.prop_dict["pairwise"])

    @pairwise.setter
    def pairwise(self, new_pairwise):
        self.prop_dict["pairwise"] = TypeConvert.py2_dbus_array(new_pairwise)

    def add_pairwise(self, pairwise):
        if pairwise not in self.prop_dict["pairwise"] and pairwise in ["wep40", "wep104", "tkip", "ccmp"]:
            self.prop_dict["pairwise"].append(pairwise)

    def remove_pairwise(self, pairwise):        
        if pairwise in self.prop_dict["pairwise"]:
            self.prop_dict["pairwise"].remove(pairwise)

    def clear_pairwise(self):
        self.prop_dict["pairwise"] = dbus.Array([], signature = dbus.Signature('s'))

    @property
    def group(self):
        if "group" not in self.prop_dict.iterkeys():
            self.clear_group()
        return TypeConvert.dbus2py(self.prop_dict["group"])

    @group.setter
    def group(self, new_group):
        self.prop_dict["group"] = TypeConvert.py2_dbus_array(new_group)

    def add_group(self, group):
        if group not in self.prop_dict["group"] and group in ["wep40", "wep104", "tkip", "ccmp"]:
            self.prop_dict["group"].append(group)

    def remove_group(self, group):        
        if group in self.prop_dict["group"]:
            self.prop_dict["group"].remove(group)

    def clear_group(self):
        self.prop_dict["group"] = dbus.Array([], signature = dbus.Signature('s'))

    @property    
    def psk(self):
        if "psk" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["psk"])

    @psk.setter
    def psk(self, new_psk):
        self.prop_dict["psk"] = TypeConvert.py2_dbus_string(new_psk)

    @property
    def psk_flags(self):
        if "psk-flags" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["psk-flags"])

    @psk_flags.setter
    def psk_flags(self, new_psk_flags):
        self.prop_dict["psk-flags"] = TypeConvert.py2_dbus_uint32(new_psk_flags)

    @property
    def leap_username(self):
        if "leap-username" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["lead-username"])

    @leap_username.setter
    def leap_username(self, new_leap_username):
        self.prop_dict["leap-username"] = TypeConvert.py2_dbus_string(new_leap_username)

    @property
    def leap_password(self):
        if "leap-password" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["leap-password"])

    @leap_password.setter
    def leap_password(self, new_leap_password):
        self.prop_dict["leap-password"] = TypeConvert.py2_dbus_string(new_leap_password)

    @property
    def leap_password_flags(self):
        if "leap-password-flags" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["leap-password-flags"])

    @leap_password_flags.setter
    def leap_password_flags(self, new_leap_password_flags):
        self.prop_dict["leap-password-flags"] = TypeConvert.py2_dbus_uint32(new_leap_password_flags)

    @property
    def wep_key0(self):
        if "wep-key0" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["wep-key0"])
    
    @wep_key0.setter
    def wep_key0(self, new_wep_key0):
        self.prop_dict["wep-key0"] = TypeConvert.py2_dbus_string(new_wep_key0)

    @property
    def wep_key1(self):
        if "wep-key1" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["wep-key1"])
    
    @wep_key0.setter
    def wep_key1(self, new_wep_key1):
        self.prop_dict["wep-key1"] = TypeConvert.py2_dbus_string(new_wep_key1)

    @property
    def wep_key2(self):
        if "wep-key2" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["wep-key2"])
    
    @wep_key2.setter
    def wep_key2(self, new_wep_key2):
        self.prop_dict["wep-key2"] = TypeConvert.py2_dbus_string(new_wep_key2)

    @property
    def wep_key3(self):
        if "wep-key3" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["wep-key3"])
    
    @wep_key3.setter
    def wep_key3(self, new_wep_key3):
        self.prop_dict["wep-key3"] = TypeConvert.py2_dbus_string(new_wep_key3)

    def get_wep_key(self, idx):
        if idx == 0:
            return self.wep_key0
        elif idx ==1:
            return self.wep_key1
        elif idx == 2:
            return self.wep_key2
        elif idx == 3:
            return self.wep_key3
        else:
            print "invalid idx"

    def set_wep_key(self, idx, key):
        if idx == 0:
            self.wep_key0 = key
        elif idx == 1:
            self.wep_key1 = key
        elif idx == 2:
            self.wep_key2 = key
        elif idx == 3:
            self.wep_key3 = key
        else:
            print "invalid idx"
        
    @property        
    def wep_tx_keyidx(self):
        if "wep-tx-keyidx" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["wep-tx-keyidx"])
        else:
            return 0

    @wep_tx_keyidx.setter
    def wep_tx_keyidx(self, new_wep_tx_keyidx):
        self.prop_dict["wep-tx-keyidx"] = TypeConvert.py2_dbus_uint32(new_wep_tx_keyidx)

    @property
    def auth_alg(self):
        if "auth-alg" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["auth-alg"])

    @auth_alg.setter
    def auth_alg(self, new_auth_alg):
        if new_auth_alg in ["open", "shared", "leap"]:
            self.prop_dict["auth-alg"] = TypeConvert.py2_dbus_string(new_auth_alg)

    @property
    def wep_key_flags(self):
        if "wep-key-flags" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["wep-key-flags"])

    @wep_key_flags.setter
    def wep_key_flags(self, new_wep_key_flags):
        self.prop_dict["wep-key-flags"] = TypeConvert.py2_dbus_uint32(new_wep_key_flags)

    @property
    def wep_key_type(self):
        if "wep-key-type" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["wep-key-type"])

    @wep_key_type.setter
    def wep_key_type(self, new_wep_key_type):
        self.prop_dict["wep-key-type"] = TypeConvert.py2_dbus_uint32(new_wep_key_type)

    def verify_wep_key(self, key, wep_type):
        if not key:
            return False
	keylen = len(key);
        if wep_type == 1 or wep_type == 0:
            import string
            if keylen == 10 or keylen == 26:
                for i in range(keylen):
                    if key[i] not in "0123456789ABCDEFabcdef":
                        return False
            elif keylen == 5 or keylen == 13:
                for i in range(keylen):
                    if key[i] not in string.ascii_letters:
                        return False
            else:
                return False
        elif wep_type == 2:
            if not keylen or keylen > 64:
                return False
        else:
            return False
        return True

    def verify_wpa_psk(self, psk):
        psklen = len(psk)
        if psklen < 8 or psklen > 64:
            return False
        if psklen == 64:
            for i in range(psklen):
                if psk[i] not in "0123456789ABCDEFabcdef":
                    return False
        return True        

    def adapt_wireless_security_commit(self):
        if self.prop_dict["auth-alg"] in ["open", "shared"]:
            self.adapt_wep_commit()
        elif self.prop_dict["auth-alg"] == "leap":
            self.adapt_leap_commit()
        elif self.prop_dict["key-mgmt"] == "ieee8021x":
            self.adapt_dynamic_wep_commit()
        elif self.prop_dict["key-mgmt"] == "wpa-psk":
            self.adapt_wpa_psk_commit()
        elif self.prop_dict["key-mgmt"] == "wpa-eap":
            self.adapt_wpa_commit()
        else:
            pass

    def adapt_wep_commit(self):
        for key in self.prop_dict.keys():
            if key not in ["auth-alg", "key-mgmt", "wep-key-type", "wep-tx-keyidx",
                           "wep-key0", "wep-key1", "wep-key2", "wep-key3"]:
                del self.prop_dict[key]

    def adapt_leap_commit(self):
        for key in self.prop_dict.keys():
            if key not in ["auth-alg", "key-mgmt", "leap-username", "leap-password"]:
                del self.prop_dict[key]

    def adapt_dynamic_wep_commit(self):
        '''need adapt 802-1x'''
        for key in self.prop_dict.keys():
            if key not in ["key-mgmt", "group", "pairwise"]:
                del self.prop_dict[key]
                
    def adapt_wpa_psk_commit(self):
        for key in self.prop_dict.keys():
            if key not in ["key-mgmt"]:
                del self.prop_dict[key]

    def adapt_wpa_commit(self):
        '''need adapt 802-1x'''                
        for key in self.prop_dict.keys():
            if key not in ["key-mgmt"]:
                del self.prop_dict[key]

if __name__ == "__main__":
    pass


