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
    
    def __init__(self, path ,interface = "org.PulseAudio.Core1.Client"):
        BusBase.__init__(self, path, interface)

        self.init_dbus_properties()
        
    ###Props    
    def get_index(self):
        return self.properties["Index"]
        
    def get_driver(self):
        return self.properties["Driver"]

    def get_owner_module(self):
        return self.properties["OwnerModule"]

    def get_playback_streams(self):
        if self.properties["PlaybackStreams"]:
            return map(lambda x:str(x), self.properties["PlaybackStreams"])
        else:
            return []

    def get_record_streams(self):
        if self.properties["RecordStreams"]:
            return map(lambda x:str(x), self.properties["RecordStreams"])
        else:
            return []

    def get_property_list(self):
        return self.properties["PropertyList"]

    ###Methods
    def kill(self):
        self.call_async("Kill", reply_handler = None, error_handler = None)

    def update_properties(self, property_list, update_mode):
        self.call_async("UpdateProperties", property_list, update_mode, reply_handler = None, error_handler = None)

    def remove_properties(self, key):
        self.call_async("RemoveProperties", key, reply_handler = None, error_handler = None)

    ###Signals

    
    
if __name__ == "__main__":
    core = Core()
    print    core.get_name()