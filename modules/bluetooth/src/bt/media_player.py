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

class MediaPlayer(dbus.service.Object):

    def __init__(self, path = "/org/bluez/mediaplayer", bus = None):
        if bus is None:
	    bus = dbus.SystemBus()    
    
        dbus.service.Object.__init__(self, bus, path)	
	
    @property
    def Equalizer(self):
	pass

    @property
    def Repeat(self):
	pass    

    @property
    def Shuffle(self):
	pass

    @property
    def Scan(self):
	pass

    @property
    def Status(self):
    ###readonly	    
	pass    
    
    @property
    def Position(self):
    ###readonly
	pass    

    @dbus.service.method("org.bluez.MediaPlayer", in_signature="sv", out_signature="")
    def SetProperty(self, key, value):
	pass
    
    @dbus.service.method("org.bluez.MediaPlayer", in_signature="", out_signature="")
    def Release(self):
	pass
    
    @dbus.service.signal("org.bluez.MediaPlayer", in_signature="sv", out_signature="")
    def PropertyChanged(self, setting, value):
	pass
    
    @dbus.service.signal("org.bluez.MediaPlayer", in_signature="v", out_signature="")
    def TrackChanged(self, metadata):
	pass    
    
    
    

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    path = "/test/mediaplayer"

    mediaplayer = MediaPlayer(path, bus)
    mainloop = gobject.MainLoop()
    mainloop.run()
