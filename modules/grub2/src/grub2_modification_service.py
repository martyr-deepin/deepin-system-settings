#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang YaoHua
# 
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
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

import gobject
import dbus
import dbus.service
import dbus.mainloop.glib
from grub_setting_utils import get_proper_resolutions

def authWithPolicyKit(sender, connection, action, interactive=1):
    system_bus = dbus.SystemBus()
    obj = system_bus.get_object("org.freedesktop.PolicyKit1", 
                                "/org/freedesktop/PolicyKit1/Authority", 
                                "org.freedesktop.PolicyKit1.Authority")

    authority = dbus.Interface(obj, "org.freedesktop.PolicyKit1.Authority")

    info = dbus.Interface(connection.get_object('org.freedesktop.DBus',
                                                '/org/freedesktop/DBus/Bus', 
                                                False), 
                          'org.freedesktop.DBus')
    pid = info.GetConnectionUnixProcessID(sender) 

    subject = ('unix-process', 
               { 'pid' : dbus.UInt32(pid, variant_level=1),
                 'start-time' : dbus.UInt64(0),
                 }
               )
    details = { '' : '' }
    flags = dbus.UInt32(interactive)
    cancel_id = ''
    (ok, notused, details) = authority.CheckAuthorization(subject, action, details, flags, cancel_id)

    return ok

class Grub2Service(dbus.service.Object):
    
    DBUS_INTERFACE_NAME = "com.deepin.grub2"

    def __init__(self, bus = None):
        if bus is None:
            bus = dbus.SystemBus()

        bus_name = dbus.service.BusName(self.DBUS_INTERFACE_NAME, bus = bus)    
        dbus.service.Object.__init__(self, bus_name, "/")

    @dbus.service.method(DBUS_INTERFACE_NAME, in_signature = "", out_signature = "as", 
                         sender_keyword = 'sender', connection_keyword = 'conn')    
    def getResolutions(self, sender = None, conn = None):
        if not authWithPolicyKit(sender, conn, "com.deepin.grub2.get-proper-resolutions"):
            raise dbus.DBusException("Not authorized with polkit.")
        return get_proper_resolutions()
    
if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default = True)
    Grub2Service()
    mainloop = gobject.MainLoop()
    gobject.timeout_add(60000, lambda : mainloop.quit())
    mainloop.run()
