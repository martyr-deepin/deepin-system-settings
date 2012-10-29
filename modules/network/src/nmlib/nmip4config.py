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
from nm_utils import TypeConvert

class NMIP4Config(NMObject):
    '''NMIP4Config'''

    def __init__(self, ip4config_object_path):
        NMObject.__init__(self, ip4config_object_path, "org.freedesktop.NetworkManager.IP4Config")
        self.prop_list = ["Addresses", "Domains", "Nameservers", "Routes", "WinsServers"]
        self.init_nmobject_with_properties()

    def get_addresses(self):
        return [TypeConvert.ip4address_net2native(item) for item in self.properties["Addresses"]]

    def get_domains(self):
        return self.properties["Domains"]

    def get_nameservers(self):
        return [TypeConvert.ip4_net2native(item) for item in self.properties["Nameservers"]]

    def get_routes(self):
        return [TypeConvert.ip4route_net2native(item) for item in self.properties["Routes"]]

    def get_wins_servers(self):
        return self.properties["WinsServers"]

if __name__ == "__main__":
    nm_ip4config = NMIP4Config("/org/freedesktop/NetworkManager/IP4Config/2")
    pass
 
