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

class NMIP6Config(NMObject):
    '''NMIP6Config'''

    def __init__(self, ip6config_object_path):
        NMObject.__init__(self, ip6config_object_path, "org.freedesktop.NetworkManager.IP6Config")
        self.prop_list = ["addresses", "domains", "nameservers", "routes"]
        self.init_nmobject_with_properties()
    # ###Props###    
    #     self.addresses = ""
    #     self.domains = ""
    #     self.nameservers = ""
    #     self.routes = ""

    ###Methods###
    def get_addresses(self):
        return self.properties["addresses"]

    def get_domains(self):
        return self.properties["domains"]

    def get_nameservers(self):
        return self.properties["nameservers"]

    def get_routes(self):
        return self.properties["routes"]

if __name__ == "__main__":
    nm_ip6config = NMIP6Config("/org/freedesktop/NetworkManager/IP6Config/4")
    print nm_ip6config.properties
