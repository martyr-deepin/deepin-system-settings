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

from pulseaudio import BusBase
import gobject

class Client(BusBase):
    
    
    __gsignals__  = {
            "property-list-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
            "client-event":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT,))
            }

    def __init__(self, path ,interface = "org.PulseAudio.Core1.Client"):
        BusBase.__init__(self, path, interface)
        
        self.dbus_proxy.connect_to_signal("PropertyListUpdated", self.property_list_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("ClientEvent", self.client_event_cb, dbus_interface = 
                                          self.object_interface, arg0 = None, arg1 = None)
    ###Props    
    def get_index(self):
        return int(self.get_property("Index"))
        
    def get_driver(self):
        return str(self.get_property("Driver"))

    def get_owner_module(self):
        return str(self.get_property("OwnerModule"))

    def get_playback_streams(self):
        if self.get_property("PlaybackStreams"):
            return map(lambda x:str(x), self.get_property("PlaybackStreams"))
        else:
            return []

    def get_record_streams(self):
        if self.get_property("RecordStreams"):
            return map(lambda x:str(x), self.get_property("RecordStreams"))
        else:
            return []

    def get_property_list(self):
        return dict(self.get_property("PropertyList"))

    ###Methods
    def kill(self):
        self.call_async("Kill", reply_handler = None, error_handler = None)

    def update_properties(self, property_list, update_mode):
        self.call_async("UpdateProperties", property_list, update_mode, reply_handler = None, error_handler = None)

    def remove_properties(self, key):
        self.call_async("RemoveProperties", key, reply_handler = None, error_handler = None)

    ###Signals
    def property_list_updated_cb(self, property_list):
        self.emit("property-list-updated", property_list)

    def client_event_cb(self, name, property_list):
        self.emit("client-event", name, property_list)
    
if __name__ == "__main__":
    pass
