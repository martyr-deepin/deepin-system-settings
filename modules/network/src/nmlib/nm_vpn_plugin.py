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

from nmobject import NMObject

class NMVpnPlugin(NMObject):
    '''NMVpnPlugin'''

    # __gsignals__ = {}
    def __init__(self, object_path = "/org/freedesktop/NetworkManager/VPN/Plugin", 
                 object_interface = "org.freedesktop.NetworkManager.VPN.Plugin",
                 service_name = "org.freedesktop.NetworkManager.l2tp-ppp"):
        
        NMObject.__init__(self, object_path, object_interface, service_name)

    def init_properties(self):
        self.init_nmobject_with_properties()

    def get_state(self):
        self.init_properties()
        return self.properties["State"]

    def connect(self, connection_dict):
        self.dbus_interface.Connect(connection_dict)

    def disconnect(self):
        self.dbus_interface.Disconnect()

    def need_secrets(self, settings_dict):
        return self.dbus_interface.NeedSecrets(settings_dict)

    def set_failure(self, reason):
        self.dbus_interface.SetFailure(reason)

    def set_ip4config(self, config_dict):
        self.dbus_interface.SetIp4Config(config_dict)


class NMVpnL2tpPlugin(NMVpnPlugin):
    '''NMVpnL2tpPlugin'''
    
    def __init__(self):
        NMVpnPlugin.__init__(self, object_path = "/org/freedesktop/NetworkManager/l2tp/ppp",
                             object_interface = "org.freedesktop.NetworkManager.l2tp.ppp",
                             service_name = "org.freedesktop.NetworkManager.l2tp-ppp")

    def need_secrets(self):
        return self.dbus_interface.NeedSecrets()

    def set_ip4config(self, config_dict):
        return self.dbus_interface.SetIp4Config(config_dict)

    def set_state(self, state):
        return self.dbus_interface.SetState(state)

class NMVpnPptpPlugin(NMVpnPlugin):
    '''NMVpnPptpPlugin'''

    def __init__(self):
        NMVpnPlugin.__init__(self, object_path = "/org/freedesktop/NetworkManager/pptp/ppp",
                             object_interface = "org.freedesktop.NetworkManager.pptp.ppp",
                             service_name = "org.freedesktop.NetworkManager.pptp-ppp")

    def need_secrets(self):
        return self.dbus_interface.NeedSecrets()

    def set_ip4config(self, config_dict):
        return self.dbus_interface.SetIp4Config(config_dict)

    def set_state(self, state):
        return self.dbus_interface.SetState(state)

