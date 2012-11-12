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

class Stream(BusBase):
    
    def __init__(self, path ,interface = "org.PulseAudio.Core1.Stream"):
        BusBase.__init__(self, path, interface)

        self.init_dbus_properties()
        
    ###Props    
    def get_index(self):
        return self.properties["Index"]
        
    def get_driver(self):
        return self.properties["Driver"]

    def get_owner_module(self):
        return self.properties["OwnerModule"]

    def get_client(self):
        return str(self.properties["Client"])

    def get_device(self):
        return str(self.properties["Device"])

    def get_sample_format(self):
        return self.properties["SampleFormat"]

    def get_smaple_rate(self):
        return self.properties["SampleRate"]

    def get_channels(self):
        if self.properties["Channels"]:
            return map(lambda x:int(x), self.properties["Channels"])
        else:
            return []

    def get_volume(self):
        if self.properties["Volume"]:
            return map(lambda x:int(x), self.properties["Volume"])
        else:
            return []

    def set_volume(self):
        pass

    def get_volume_writable(self):
        return self.properties["VolumeWritable"]

    def get_mute(self):
        return self.properties["Mute"]

    def set_mute(self):
        pass

    def get_buffer_latency(self):
        return self.properties["BufferLatency"]

    def get_device_latency(self):
        return self.properties["DeviceLatency"]

    def get_resample_method(self):
        return self.properties["ResampleMethod"]
    
    def get_property_list(self):
        return self.properties["PropertyList"]

    ###Methods
    def move(self, device):
        self.call_async("Move", device, reply_handler = None, error_handler = None)

    def kill(self):
        self.call_async("Kill", reply_handler = None, error_handler = None)
        
    ###Signal

class StreamRestore(BusBase):
    
    def __init__(self, path = "/org/pulseaudio/stream_restore1", interface = "org.PulseAudio.Ext.StreamRestore1"):
        BusBase.__init__(self, path, interface)
        
        self.init_dbus_properties()

    ###Props    
    def get_interface_revision(self):
        return self.properties["InterfaceRevision"]

    def get_entries(self):
        if self.properties["Entries"]:
            return map(lambda x:str(x), self.properties["Entries"])
        else:
            return []

    ###Methods
    def add_entry(self, name, device, volume, mute, apply_immediately):
        return str(self.dbus_method("AddEntry", name, device, volume, mute, apply_immediately))

    def get_entry_by_name(self, name):
        return str(self.dbus_method("GetEntryByName", name))

    ###Signals
    

class RestoreEntry(BusBase):

    def __init__(self, path , interface = "org.PulseAudio.Ext.StreamRestore1.RestoreEntry"):

        BusBase.__init__(self, path, interface)

        self.init_dbus_properties()

    ###Props    
    def get_index(self):
        return self.properties["Index"]

    def get_name(self):
        return self.properties["Name"]

    def get_device(self):
        return self.properties["Device"]

    def set_device(self):
        pass

    def get_voluem(self):
        pass

    def set_volume(self):
        pass

    def get_mute(self):
        pass

    def set_mute(self):
        pass

    ####Methods
    def remove(self):
        self.call_async("Remove", reply_handler = None, error_handler = None)

if __name__ == "__main__":
    pass