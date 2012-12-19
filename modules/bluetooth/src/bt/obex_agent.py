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

import sys
import dbus
import dbus.service
import dbus.mainloop.glib

class ObexAgent(dbus.service.Object):
    def __init__(self, conn=None, obj_path=None):
        dbus.service.Object.__init__(self, conn, obj_path)

    @dbus.service.method("org.openobex.Agent",
                    in_signature="o", out_signature="s")
    def Request(self, path):
        print "Transfer started"
        transfer = dbus.Interface(bus.get_object("org.openobex.client",
                    path), "org.openobex.Transfer")
        properties = transfer.GetProperties()
        for key in properties.keys():
            print "  %s = %s" % (key, properties[key])
        return ""

    @dbus.service.method("org.openobex.Agent",
                    in_signature="ot", out_signature="")
    def Progress(self, path, transferred):
        print "Transfer progress (%d bytes)" % (transferred)
        return

    @dbus.service.method("org.openobex.Agent",
                    in_signature="o", out_signature="")
    def Complete(self, path):
        print "Transfer finished"
        return

    @dbus.service.method("org.openobex.Agent",
                    in_signature="os", out_signature="")
    def Error(self, path, error):
        print "Transfer finished with an error: %s" % (error)
        return

    @dbus.service.method("org.openobex.Agent",
                    in_signature="", out_signature="")
    def Release(self):
        mainloop.quit()
        return

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SessionBus()
    client = dbus.Interface(bus.get_object("org.openobex.client", "/"),
                            "org.openobex.Client")

    if (len(sys.argv) < 3):
        print "Usage: %s <device> <file> [file*]" % (sys.argv[0])
        sys.exit(1)

    path = "/test/agent"
    agent = ObexAgent(bus, path)

    mainloop = gobject.MainLoop()

    client.SendFiles({ "Destination": sys.argv[1] }, sys.argv[2:], path)

    mainloop.run()
