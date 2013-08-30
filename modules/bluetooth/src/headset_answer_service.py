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

class HeadsetAnswerService(dbus.service.Object):

    DBUS_INTERFACE_NAME = "com.deepin.BluetoothHeadset"

    def __init__(self, bus = None):
        bus = dbus.SessionBus()
        name = dbus.service.BusName(HeadsetAnswerService.DBUS_INTERFACE_NAME, bus)
        dbus.service.Object.__init__(self, name, "/com/deepin/bluetooth")
        
        gobject.timeout_add(5000, self.AnswerRequested)

    @dbus.service.method(DBUS_INTERFACE_NAME, in_signature='', out_signature='')
    def SendAnswerReqest(self):
        print "SendAnswerRequest"
        self.AnswerRequested()
        
    @dbus.service.signal(DBUS_INTERFACE_NAME, signature='')
    def AnswerRequested(self):
        print "AnswerRequest"
    
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
HeadsetAnswerService()

main_loop = gobject.MainLoop()
main_loop.run()
