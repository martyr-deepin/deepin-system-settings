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

import gobject
import dbus
import dbus.service
import dbus.mainloop.glib

class Rejected(dbus.DBusException):
    _dbus_error_name = "org.bluez.Error.Rejected"

class Agent(dbus.service.Object):
	
    def __init__(self, path = "/org/bluez/agent", bus = None):
        if bus is None:
	    bus = dbus.SystemBus()    
    
        dbus.service.Object.__init__(self, bus, path)	
    
        self.exit_on_release = True
    
    def set_exit_on_release(self, exit_on_release):
        self.exit_on_release = exit_on_release
    
    @dbus.service.method("org.bluez.Agent", in_signature="", out_signature="")
    def Release(self):
        if self.exit_on_release:
	   mainloop.quit()
    
    @dbus.service.method("org.bluez.Agent", in_signature="os", out_signature="")
    def Authorize(self, device_path, uuid):
        print "Authorize (%s, %s)" % (device_path, uuid)
        authorize = raw_input("Authorize connection (yes/no): ")
        if (authorize == "yes"):
            return
        raise Rejected("Connection rejected by user")
    
    @dbus.service.method("org.bluez.Agent", in_signature="o", out_signature="s")
    def RequestPinCode(self, device_path):
        print "RequestPinCode (%s)" % (device_path)
        return raw_input("Enter PIN Code: ")
    
    @dbus.service.method("org.bluez.Agent", in_signature="o", out_signature="u")
    def RequestPasskey(self, device_path):
        print "RequestPasskey (%s)" % (device_path)
        passkey = raw_input("Enter passkey: ")
        return dbus.UInt32(passkey)
    
    @dbus.service.method("org.bluez.Agent", in_signature="oub", out_signature="")
    def DisplayPasskey(self, device_path, passkey, entered):
	print "DisplayPasskey (%s, %d)" % (device_path, passkey, entered)
    
    @dbus.service.method("org.bluez.Agent", in_signature="ou", out_signature="")
    def RequestConfirmation(self, device_path, passkey):
        print "RequestConfirmation (%s, %d)" % (device_path, passkey)
        confirm = raw_input("Confirm passkey (yes/no): ")
        if (confirm == "yes"):
            return
        raise Rejected("Passkey doesn't match")
    
    @dbus.service.method("org.bluez.Agent", in_signature="s", out_signature="")
    def ConfirmModeChange(self, mode):
        print "ConfirmModeChange (%s)" % (mode)
        authorize = raw_input("Authorize mode change (yes/no): ")
        if (authorize == "yes"):
	   return
        raise Rejected("Mode change by user")
    
    @dbus.service.method("org.bluez.Agent", in_signature="", out_signature="")
    def Cancel(self):
    	print "Cancel"


if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    path = "/test/agent"

    agent = Agent(path, bus)
    mainloop = gobject.MainLoop()
    mainloop.run()
