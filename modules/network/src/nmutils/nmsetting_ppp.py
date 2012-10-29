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

from nmsetting import NMSetting
from nmlib.nmconstant import NMSettingParamFlags as pflag
from nmlib.nm_utils import TypeConvert

class NMSettingPPP (NMSetting):
    '''NMSettingPPP'''

    def __init__(self):
        NMSetting.__init__(self)
        self.name = "ppp"

    @property    
    def noauth(self):
        if "noauth" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["noauth"])
    
    @noauth.setter
    def noauth(self, new_noauth):
        self.prop_dict["noauth"] = TypeConvert.py2_dbus_boolean(new_noauth)

    @property
    def refuse_eap(self):
        if "refuse-eap" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["refuse-eap"])

    @refuse_eap.setter
    def refuse_eap(self, new_refuse_eap):
        self.prop_dict["refuse-eap"] = TypeConvert.py2_dbus_boolean(new_refuse_eap)

    @property
    def refuse_pap(self):
        if "refuse-pap" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["refuse-pap"])

    @refuse_pap.setter
    def refuse_pap(self, new_refuse_pap):
        self.prop_dict["refuse-pap"] = TypeConvert.py2_dbus_boolean(new_refuse_pap)

    @property
    def refuse_chap(self):
        if "refuse-chap" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["refuse-chap"])

    @refuse_chap.setter
    def refuse_chap(self, new_refuse_chap):
        self.prop_dict["refuse-chap"] = TypeConvert.py2_dbus_boolean(new_refuse_chap)

    @property
    def refuse_mschap(self):
        if "refuse-mschap" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["refuse-mschap"])

    @refuse_mschap.setter
    def refuse_mschap(self, new_refuse_mschap):
        self.prop_dict["refuse-mschap"] = TypeConvert.py2_dbus_boolean(new_refuse_mschap)

    @property
    def refuse_mschapv2(self):
        if "refuse_mschapv2" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["refuse-mschapv2"])

    @refuse_mschapv2.setter
    def refuse_mschapv2(self, new_refuse_mschapv2):
        self.prop_dict["refuse-mschapv2"] = TypeConvert.py2_dbus_boolean(new_refuse_mschapv2)

    @property
    def nobsdcomp(self):
        if "nobsdcomp" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["nobsdcomp"])
    
    @nobsdcomp.setter
    def nobsdcomp(self, new_nobsdcomp):
        self.prop_dict["nobsdcomp"] = TypeConvert.py2_dbus_boolean(new_nobsdcomp)

    @property
    def nodeflate(self):
        if "nodeflate" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["nodeflate"])

    @nodeflate.setter
    def nodeflate(self, new_nodeflate):
        self.prop_dict["nodeflate"] = TypeConvert.py2_dbus_boolean(new_nodeflate)

    @property
    def no_vj_comp(self):
        if "no-vj-comp" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["no-vj-comp"])

    @no_vj_comp.setter
    def no_vj_comp(self, new_no_vj_comp):
        self.prop_dict["no-vj-comp"] = TypeConvert.py2_dbus_boolean(new_no_vj_comp)

    @property
    def require_mppe(self):
        if "require-mppe" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["require-mppe"])

    @require_mppe.setter
    def require_mppe(self, new_require_mppe):
        self.prop_dict["new_require_mppe"] = TypeConvert.py2_dbus_boolean(new_require_mppe)

    @property
    def require_mppe_128(self):
        if "require-mppe-128" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["require-mppe-128"])

    @require_mppe_128.setter
    def require_mppe_128(self, new_require_mppe_128):
        self.prop_dict["require-mppe-128"] = TypeConvert.py2_dbus_boolean(new_require_mppe_128)

    @property
    def mppe_stateful(self):
        if "mppe_stateful" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["mppe_stateful"])

    @mppe_stateful.setter
    def mppe_stateful(self ,new_mppe_stateful):
        self.prop_dict["mppe-stateful"] = TypeConvert.py2_dbus_boolean(new_mppe_stateful)

    @property
    def crtscts(self):
        if "crtscts" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["crtscts"])

    @crtscts.setter
    def crtscts(self, new_crtscts):
        self.prop_dict["crtscts"] = TypeConvert.py2_dbus_boolean(new_crtscts)

    @property
    def baud(self):
        if "baud" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["baud"])

    @baud.setter
    def baud(self, new_baud):
        self.prop_dict["baud"] = TypeConvert.py2_dbus_uint32(new_baud)

    @property
    def mru(self):
        if "mru" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["mru"])

    @mru.setter
    def mru(self, new_mru):
        self.prop_dict["mru"] = TypeConvert.py2_dbus_uint32(new_mru)

    @property
    def mtu(self):
        if "mtu" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["mtu"])

    @mtu.setter
    def mtu(self, new_mtu):
        self.prop_dict["mtu"] = TypeConvert.py2_dbus_uint32(new_mtu)

    @property
    def lcp_echo_failure(self):
        if "lcp-echo-failure" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["lcp-echo-failure"])

    @lcp_echo_failure.setter
    def lcp_echo_failure(self, new_lcp_echo_failure):
        self.prop_dict["lcp-echo-failure"] = TypeConvert.py2_dbus_uint32(new_lcp_echo_failure)

    @property
    def lcp_echo_interval(self):
        if "lcp-echo-interval" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["lcp-echo-interval"])

    @lcp_echo_interval.setter
    def lcp_echo_interval(self, new_lcp_echo_interval):
        return TypeConvert.py2_dbus_uint32(new_lcp_echo_interval)

