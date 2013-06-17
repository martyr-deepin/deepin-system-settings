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
import dbus.service
import dbus.mainloop.glib
import gobject
    
mainloop = gobject.MainLoop()

NETWORK_SERVICE     = "com.deepin.network"
NETWORK_INTERFACE   = "com.deepin.network"
NETWORK_PATH        = "/com/deepin/network"

class NetworkService(dbus.service.Object):

    def __init__(self):
        self.bus = dbus.SystemBus()
        bus_name = dbus.service.BusName(NETWORK_SERVICE, self.bus)

        dbus.service.Object.__init__(self, bus_name, NETWORK_PATH)

    '''
    @dbus.service.method(NETWORK_INTERFACE, in_signature = "", out_signature = "")
    def fix_unmanaged(self):
        lines = []
        with open("/etc/NetworkManager/NetworkManager.conf") as cf:
            try:
                lines = cf.readlines()
                for i in range(len(lines)):
                    if lines[i].startswith("managed"):
                        lines[i] = "managed=true\n"
            except:
                traceback.print_exc()

        with open("/etc/NetworkManager/NetworkManager.conf", "w") as pf:
            try:
                pf.writelines(lines)
            except:
                traceback.print_exc()

        with open("/etc/network/interfaces", "w") as it:
            try:
                it.write("auto lo\n")
                it.write("iface lo inet loopback\n")
            except:
                traceback.print_exc()

        os.system("service network-manager restart")
    '''
    @dbus.service.method(NETWORK_INTERFACE, in_signature = "s", out_signature = "s")
    def getget(self, address):
        return address

    @dbus.service.method(NETWORK_INTERFACE, in_signature = "s", out_signature = "s")
    def get_ap_sec(self, address):
        from wpa_cli import get_encry_by_bssid
        return get_encry_by_bssid(address)

        #from iwlistparse import parse_security
        #from deepin_utils.process import get_command_output
        #from nm_utils import TypeConvert
        
        #if not TypeConvert.is_valid_mac_address(address):
            #return None

        #command = ["/sbin/iwlist"]
        #command.append(interface)
        #command.append("scan")

        #try:
            #iwlist_output = map(lambda x: x.rstrip(), get_command_output(command))
            #return parse_security(iwlist_output, address)
        #except:
            #traceback.print_exc()
            #return None
    
    @dbus.service.signal(NETWORK_INTERFACE)
    def DeviceChanged(self, device_index):
        print "DeviceChanged emited", device_index
        return

    @dbus.service.method(NETWORK_INTERFACE,
                         in_signature='i', out_signature='')
    def emitDeviceChanged(self, index):
        self.DeviceChanged(index)
        return

    @dbus.service.signal(NETWORK_INTERFACE)
    def VpnSettingChange(self, conn_path):
        print "VpnSettingAdded emit"
        return 

    @dbus.service.method(NETWORK_INTERFACE,
                         in_signature='o', out_signature='')
    def emitVpnSettingChange(self, conn_path):
        self.VpnSettingChange(conn_path)
        return

    @dbus.service.signal(NETWORK_INTERFACE)
    def VpnStart(self, path):
        return 

    @dbus.service.method(NETWORK_INTERFACE,
                         in_signature='o', out_signature='')
    def emitVpnStart(self, active_path):
        self.VpnStart(active_path)
        return

    @dbus.service.signal(NETWORK_INTERFACE)
    def userToggleOff(self, network_type):
        return 

    @dbus.service.method(NETWORK_INTERFACE,
                         in_signature='s', out_signature='')
    def emitUserToggleOff(self, network_type):
        self.userToggleOff(network_type)
        return

if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default = True)
    NetworkService()
    #gobject.timeout_add(60000, lambda :mainloop.quit()) 
    mainloop.run()
