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
import traceback

def get_ap_security(interface, address):
    '''interface: wlan0 for wireless device
       address: bssid of access point
    '''
    try:
        bus = dbus.SystemBus()
        proxy = bus.get_object("com.deepin.network", "/com/deepin/network")
        interface = dbus.Interface(proxy, "com.deepin.network")

        return interface.get_ap_sec(interface, address)
    except:
        print "parse ap sec with dbus failed"
        traceback.print_exc()

        from iwlistparse import parse_security
        from deepin_utils.process import get_command_output

        command = ["/sbin/iwlist"]
        command.append(interface)
        command.append("scan")

        iwlist_output = map(lambda x: x.rstrip(), get_command_output(command))
    
        return parse_security(iwlist_output, address)

if __name__ == "__main__":
    print get_ap_security("wlan0", "5C:63:BF:7E:ED:64")

