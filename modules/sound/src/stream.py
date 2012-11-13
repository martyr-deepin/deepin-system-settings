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
import traceback

class Stream(BusBase):
    
    __gsignals__  = {
            "device-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "sample-rate-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_UINT,)),
            "volume-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
            "mute-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,)),
            "property-list-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
            "stream-event":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            } 

    def __init__(self, path ,interface = "org.PulseAudio.Core1.Stream"):
        BusBase.__init__(self, path, interface)

        self.init_dbus_properties()
                
        self.dbus_proxy.connect_to_signal("DeviceUpdated", self.device_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("SampleRateUpdated", self.sample_rate_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("VolumeUpdated", self.volume_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("MuteUpdated", self.mute_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("PropertyListUpdated", self.property_list_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("StreamEvent", self.stream_event_cb, dbus_interface = 
                                          self.object_interface, arg0 = None, arg1 = None)

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

    def set_volume(self, volume):
        try:
            self.property_interface.Set(self.object_interface, "Volume", volume)
        except:
            traceback.print_exc()
            
    def get_volume_writable(self):
        return self.properties["VolumeWritable"]

    def get_mute(self):
        return self.properties["Mute"]

    def set_mute(self, muted):
        try:
            self.property_interface.Set(self.object_interface, "Mute", muted)
        except:
            traceback.print_exc()

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
    def device_updated_cb(self, device):
        self.emit("device-updated", device)

    def sample_rate_updated_cb(self, sample_rate):
        self.emit("sample-rate-updated", sample_rate)

    def volume_updated_cb(self, volume):
        self.emit("volume-updated", volume)

    def mute_updated_cb(self, muted):
        self.emit("mute-updated", muted)

    def property_list_updated_cb(self, property_list):
        self.emit("property-list-updated", property_list)

    def stream_event_cb(self, name, property_list):
        self.emit("stream-event", name, property_list)

class StreamRestore(BusBase):
    
    __gsignals__  = {
            "new-entry":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "entry-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,))
            } 

    def __init__(self, path = "/org/pulseaudio/stream_restore1", interface = "org.PulseAudio.Ext.StreamRestore1"):
        BusBase.__init__(self, path, interface)
        
        self.init_dbus_properties()

        self.dbus_proxy.connect_to_signal("NewEntry", self.new_entry_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("EntryRemoved", self.entry_removed_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)


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
    def new_entry_cb(self, entry):
        self.emit("new-entry", entry)
    
    def entry_removed_cb(self, entry):
        self.emit("entry-removed", entry)


class RestoreEntry(BusBase):

    __gsignals__  = {
            "device-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "volume-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
            "mute-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))
            } 

    def __init__(self, path , interface = "org.PulseAudio.Ext.StreamRestore1.RestoreEntry"):

        BusBase.__init__(self, path, interface)

        self.init_dbus_properties()

        self.dbus_proxy.connect_to_signal("DeviceUpdated", self.device_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("MuteUpdated", self.mute_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("VolumeUpdated", self.volume_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)
    ###Props    
    def get_index(self):
        return self.properties["Index"]

    def get_name(self):
        return self.properties["Name"]

    def get_device(self):
        return self.properties["Device"]

    def set_device(self, device):
        try:
            self.property_interface.Set(self.object_interface, "Device", device)
        except:
            traceback.print_exc()

    def get_volume(self):
        if self.properties["Volume"]:
            return map(lambda x:int(x), self.properties["Volume"])
        else:
            return []

    def set_volume(self, volume):
        try:
            self.property_interface.Set(self.object_interface, "Volume", volume)
        except:
            traceback.print_exc()

    def get_mute(self):
        return self.properties["Mute"]

    def set_mute(self, muted):
        try:
            self.property_interface.Set(self.object_interface, "Mute", muted)
        except:
            traceback.print_exc()

    ####Methods
    def remove(self):
        self.call_async("Remove", reply_handler = None, error_handler = None)

    ###Signals
    def device_updated_cb(self, device):
        self.emit("device-updated", device)

    def volume_updated_cb(self, volume):
        self.emit("volume-updated", volume)

    def mute_updated_cb(self, muted):
        self.emit("mute-updated", muted)

if __name__ == "__main__":
    pass
