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

class NMDHCP6Config(NMObject):
    '''NMDHCP6Config'''

    def __init__(self, dhcp6_config_object_path):
        NMObject.__init__(self, dhcp6_config_object_path, "org.freedesktop.NetworkManager.DHCP6Config")
        self.prop_list = ["Options"]
        self.init_nmobject_with_properties()
        self.options = self.get_options()

        self.bus().add_signal_receiver(self.properties_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertiesChanged")


    def get_options(self):
        return self.properties["Options"]

    def get_one_option(self, option):
        return self.options[option]

    def properties_changed_cb(self, prop_dict):
        self.init_nmobject_with_properties()

if __name__ == "__main__":
    nm_dhcp6_config = NMDHCP6Config("/org/freedesktop/NetworkManager/DHCP6Config/2")
    print nm_dhcp6_config.properties
    print nm_dhcp6_config.options
