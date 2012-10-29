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
import sys
sys.path.append("../")

from pynm.nmlib.nm_remote_connection import NMRemoteConnection
from pynm.nmlib.nm_remote_settings import NMRemoteSettings

remote_setting = NMRemoteSettings()
# vpn_connection = NMRemoteConnection(remote_setting.get_vpn_connections()[0])

from pynm.nmlib.nmclient import NMClient
nmclient = NMClient()
# active_connection = nmclient.get_vpn_active_connection()
# from pynm.nmlib.nm_active_connection import NMActiveConnection
# remote_connection = NMRemoteConnection(NMActiveConnection(active_connection).get_connection())

def connection_setting():
    pass

def ip4_setting():
    pass

def ppp_setting():
    print "\n#########PPP Setting #########"
    pass
    print "#########PPP Setting #########\n"

def vpn_setting():
    print "\n#########VPN Setting #########"
    
    vpn_connection = NMRemoteConnection(remote_setting.get_vpn_connections()[0])

    vpn = vpn_connection.get_setting("vpn")

    print "\n###get###\n"

    print " service_type:%s\n" % vpn.service_type
    print " user_name:%s\n" % vpn.user_name
    print " data:%s\n" % vpn.data
    print " data->user:%s\n" % vpn.user
    print " data->domain:%s\n" % vpn.domain
    print " data->password-flags:%s\n" % vpn.password_flags
    print " data->gateway:%s\n" % vpn.gateway

    print " secrets:%s\n" % vpn.secrets
    
    print "\n###set###\n"
    # vpn.ipsec_enable = "yes"
    # vpn.ipsec_psk = "123456"
    # vpn.ipsec_group_name = "VPNG"
    
    # vpn_connection.update()
    print "#########VPN Setting #########\n"

def vpn_active_connection():
    print "\n#########VPN Active Connection #########"

    active_connection = nmclient.get_vpn_active_connection()

    from pynm.nmlib.nm_vpn_connection import NMVpnConnection
    vpn_active_connection = NMVpnConnection(active_connection)
    
    print vpn_active_connection.get_banner()
    print vpn_active_connection.get_vpnstate()

    print "#########VPN Active Connection #########\n"

def connect():
    from pynm.nmlib.nm_vpn_plugin import NMVpnPlugin
    
    vpn_plugin = NMVpnPlugin(service_name = "org.freedesktop.NetworkManager.l2tp")
    
    # setting = NMRemoteConnection(remote_setting.new_vpn_l2tp_connection()).settings_dict
    con_path = remote_setting.new_vpn_l2tp_connection()

    # vpn_plugin.connect(remote_setting.l2tp_settings_dict)

    # print "active it"
    nmclient.activate_connection(con_path, nmclient.get_wireless_device(), nmclient.get_wireless_active_connection())
    # print "success activate "
    # print vpn_plugin.need_secrets(remote_setting.l2tp_settings_dict)

def connect_pptp():
    from pynm.nmlib.nm_vpn_plugin import NMVpnPlugin
    
    vpn_plugin = NMVpnPlugin(service_name = "org.freedesktop.NetworkManager.pptp")

    con_path = remote_setting.new_vpn_pptp_connection()

    vpn_plugin.connect(remote_setting.pptp_settings_dict)

    NMRemoteConnection(con_path)
    nmclient.activate_connection(con_path, nmclient.get_wireless_device(), nmclient.get_wireless_active_connection())


def pptp_set_ip4config():
    from pynm.nmlib.nm_vpn_plugin import NMVpnPlugin
    vpn_plugin = NMVpnPlugin(service_name = "org.freedesktop.NetworkManager.pptp")

    from pynm.nmlib.nm_vpn_plugin import NMVpnPptpPlugin
    pptp_plugin = NMVpnPptpPlugin()

    from pynm.nmutils.nmsetting_ip4config import NMSettingIP4Config
    ip4config = NMSettingIP4Config()

    ip4config.method = "auto"
    ip4config.add_dns("202.114.88.10")
    ip4config.add_dns_search("www.testdns.com")

    print ip4config.prop_dict
    print "\n"
    # pptp_plugin.set_ip4config(ip4config.prop_dict)
    vpn_plugin.set_ip4config(ip4config.prop_dict)

    vpn_connection = NMRemoteConnection(remote_setting.get_vpn_connections()[0])
    print vpn_connection.settings_dict
    vpn_connection.update()

def disconnect_active_vpn():
    from pynm.nmlib.nm_vpn_plugin import NMVpnPlugin
    
    vpn_plugin = NMVpnPlugin(service_name = "org.freedesktop.NetworkManager.pptp")
    print "state before disconnect:\n"
    print vpn_plugin.get_state()
    print "disconnect:\n"
    vpn_plugin.disconnect()
    print "state after disconnect:\n"
    print vpn_plugin.get_state()

def need_secrets():
    from pynm.nmlib.nm_vpn_plugin import NMVpnPlugin, NMVpnPptpPlugin

    vpn_plugin = NMVpnPlugin(service_name = "org.freedesktop.NetworkManager.pptp")
    pptp_plugin = NMVpnPptpPlugin()

    print vpn_connection.settings_dict
    print vpn_plugin.need_secrets(vpn_connection.settings_dict)

    # # print vpn_plugin.get_state()
    # print pptp_plugin.need_secrets()
    # print pptp_plugin.get_state()

if __name__ == "__main__":
    
    # vpn_setting()
    # vpn_active_connection()
    # disconnect_active_vpn()
    # need_secrets()
    connect()
    # connect_pptp()
    # pptp_set_ip4config()
    pass

