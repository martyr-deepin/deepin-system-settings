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
from pynm.nmlib.nmdevice import NMDevice
from pynm.nmlib.nmdevice_ethernet import NMDeviceEthernet
from pynm.nmlib.nmdhcp4config import NMDHCP4Config
# from pynm.nmlib.nmdhcp6config import NMDHCP6Config
from pynm.nmlib.nmip4config import NMIP4Config
# from pynm.nmlib.nmip6config import NMIP6Config
# from pynm.nmlib.nm_active_connection import NMActiveConnection
from pynm.nmlib.nm_remote_connection import NMRemoteConnection
from pynm.nmlib.nm_remote_settings import NMRemoteSettings


device = NMDevice(get_wired_device(), None)
wired_device = NMDeviceEthernet(device.object_path)

ip4config = NMIP4Config(device.get_ip4_config())
# ip6config = NMIP6Config(device.get_ip6_config())
dhcp4config = NMDHCP4Config(device.get_dhcp4_config())
# dhcp6config = NMDHCP6Config(device.get_dhcp6_config())

remote_setting = NMRemoteSettings()

# active_connection = NMActiveConnection(device.get_active_connection())
# remote_connection = NMRemoteConnection(active_connection.get_connection())
pppoe_connection = NMRemoteConnection(remote_setting.get_pppoe_connections()[0])


def get_ip4_info():
    pass

def get_dhcp4_info():
    pass
    
def get_connection_info():
    pass

def connection_setting():
    pass

def wired_setting():
    pass

def ip4_setting():
    pass

def ip6_setting():
    pass

def pppoe_setting():
    print "\n#########PPPOE Setting #########"
    # from pynm.nmutils.nmsetting_pppoe import NMSettingPPPOE
    pppoe = pppoe_connection.get_setting("pppoe")

    print "\n###get###\n"

    print " service:%s\n" % pppoe.service
    print " username:%s\n" % pppoe.username
    print " password:%s\n" % pppoe.password
    print " password_flags:%s\n" % pppoe.password_flags

    print "\n###set###\n"
    pppoe.username = "yilang"
    pppoe.password = "deepin"

    pppoe_connection.update()
    print "#########PPPOE Setting #########\n"

def ppp_setting():
    print "\n#########PPP Setting #########"
    # from pynm.nmutils.nmsetting_ppp import NMSettingPPP
    # ppp = NMSettingPPP(pppoe_connection)
    ppp = pppoe_connection.get_setting("ppp")
    print "\n###get###\n"

    print " noauth:%s\n" % ppp.noauth
    print " refuse_eap:%s\n" % ppp.refuse_eap
    print " refuse_pap:%s\n" % ppp.refuse_pap
    print " refuse_chap:%s\n" % ppp.refuse_chap
    print " refuse_mschap:%s\n" % ppp.refuse_mschap
    print " refuse_mschapv2:%s\n" % ppp.refuse_mschapv2
    print " nobsdcomp:%s\n" % ppp.nobsdcomp
    print " nodeflate:%s\n" % ppp.nodeflate
    print " no_vj_comp:%s\n" % ppp.no_vj_comp
    print " require_mppe:%s\n" % ppp.require_mppe
    print " require_mppe_128:%s\n" % ppp.require_mppe_128
    print " mppe_stateful:%s\n" % ppp.mppe_stateful
    print " crtscts:%s\n" % ppp.crtscts
    print " baud:%s\n" % ppp.baud
    print " mru:%s\n" % ppp.mru
    print " mtu:%s\n" % ppp.mtu
    print " lcp_echo_failure:%s\n" % ppp.lcp_echo_failure
    print " lcp_echo_interval:%s\n" % ppp.lcp_echo_interval

    print "\n###set###\n"

    # ppp.noauth = False
    ppp.refuse_eap = True
    ppp.refuse_pap = True
    ppp.refuse_chap = True
    ppp.refuse_mschap = True
    ppp.refuse_mschapv2 = False

    ppp.require_mppe = True
    ppp.require_mppe_128 = False
    ppp.mppe_stateful = True
    ppp.nobsdcomp = True
    ppp.nodeflate = False
    ppp.no_vj_comp = True
    ppp.lcp_echo_interval = True

    pppoe_connection.update()
    print "#########PPP Setting #########\n"

def new_pppoe_connection():
    NMRemoteConnection(remote_setting.new_pppoe_connection())

if __name__ == "__main__":

    # pppoe_setting()
    ppp_setting()
    pass





