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

class HandsfreeAgent(dbus.service.Object):

    def __init__(self, path = "/org/bluez/handsfreeagent", bus = None):
	if bus is None:
	   bus = dbus.SystemBus()    
	dbus.service.Object.__init__(self, bus, path)	
    
    @dbus.service.method("org.bluez.HandsfreeAgent", in_signature="", out_signature="")
    def Release(self):
        if self.exit_on_release:
	   mainloop.quit()
    
    @dbus.service.method("org.bluez.HandsfreeAgent", in_signature="ou", out_signature="")
    def NewConnection(self, fd, version):
        pass

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    path = "/test/handsfreeagent"

    handsfree_agent = HandsfreeAgent(path, bus)
    mainloop = gobject.MainLoop()
    mainloop.run()
