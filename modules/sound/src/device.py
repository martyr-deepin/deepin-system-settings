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

class Device(BusBase):

    __gsignals__  = {
            "volume-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
            "mute-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,)),
            "state-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_UINT,)),
            "active-port-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "property-list-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
            }
    
    def __init__(self, path, interface = "org.PulseAudio.Core1.Device"):
        BusBase.__init__(self, path, interface)

        self.init_dbus_properties()

        self.dbus_proxy.connect_to_signal("VolumeUpdated", self.volume_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("MuteUpdated", self.mute_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("StateUpdated", self.state_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("ActivePortUpdated", self.active_port_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("PropertyListUpdated", self.property_list_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)


    ###Props    
    def get_index(self):
        return self.properties["Index"]

    def get_name(self):
        return self.properties["Name"]

    def get_driver(self):
        return self.properties["Driver"]

    def get_owner_module(self):
        return str(self.properties["OwnerModule"])

    def get_card(self):
        return str(self.properties["Card"])

    def get_sample_format(self):
        return self.properties["SampleFormat"]

    def get_sample_rate(self):
        return self.properties

    def get_channels(self):
        if self.properties["Channels"]:
            return map(lambda x:int(x), self.properties["Channels"])

    def get_volume(self):
        if self.properties["Volume"]:
            return map(lambda x:int(x), self.properties["Volume"])
        else:
            return []

    def set_volume(self, volume):
        try:
            self.dbus_interface.Set(self.object_interface, "Volume", volume)
        except:
            traceback.print_exc()

    def get_has_flat_volume(self):
        return self.properties["HasFlatVolume"]

    def get_has_convertible_to_decibel_volume(self):
        return self.properties["HasConvertibleToDecibelVolume"]

    def get_base_volume(self):
        return self.properties["BaseVolume"]
    
    def get_volume_steps(self):
        return self.properties["VolumeSteps"]

    def get_mute(self):
        return self.properties["Mute"]

    def set_mute(self, muted):
        try:
            self.property_interface.Set(self.object_interface, "Mute", muted)
        except:
            traceback.print_exc()

    def get_has_hardware_volume(self):
        return self.properties["HasHardwareVolume"]

    def get_has_hardware_mute(self):
        return self.properties["HasHardwareMute"]

    def get_configured_latency(self):
        return self.properties["ConfiguredLatency"]
    
    def get_has_dynamic_latency(self):
        return self.properties["HasDynamicLatency"]

    def get_latency(self):
        return self.properties["Latency"]

    def get_is_hardware_device(self):
        return self.properties["IsHardwareDevice"]

    def get_is_network_device(self):
        return self.properties["IsNetworkDevice"]

    def get_state(self):
        return self.properties["State"]

    def get_ports(self):
        if self.properties["ports"]:
            return map(lambda x:str(x), self.properties["ports"])
        else:
            return []

    def get_active_port(self):
        return str(self.properties["ActivePort"])

    def set_active_port(self, active_port):
        try:
            self.property_interface.Set(self.object_interface, "ActivePort", active_port)
        except:
            traceback.print_exc()

    def get_property_list(self):
        return self.properties["PropertyList"]

    ###Methods
    def suspend(self, bool):
        self.call_async("suspend", bool, reply_handler = None, error_handler = None)

    def get_port_by_name(self, name):
        return str(self.dbus_method("GetPortByName", name))

    ###Signals
    def volume_updated_cb(self, volume):
        self.emit("volume-updated", volume)

    def mute_updated_cb(self, mute):
        self.emit("mute-updated", mute)

    def state_updated_cb(self, state):
        self.emit("state-updated", state)

    def active_port_updated_cb(self, port):
        self.emit("active-port-updated", port)

    def property_list_updated_cb(self, property_list):
        self.emit("property-list-updated", property_list)


class Sink(Device):

    def __init__(self, path, interface = "org.PulseAudio.Core1.Sink"):
        Device.__init__(self, path, interface)
    
        self.init_dbus_properties()

    def get_monitor_source(self):
        return str(self.properties["MonitorSource"])

class Source(Device):

    def __init__(self, path, interface = "org.PulseAudio.Core1.Source"):
        Device.__init__(self, path, interface)
        
        self.init_dbus_properties()

    def get_monitor_of_sink(self):
        return str(self.properties["MonitorOfSink"])

class DevicePort(BusBase):
    
    def __init__(self, path, interface = "org.PulseAudio.Core1.DevicePort"):
        BusBase.__init__(self, path, interface)
        
        self.init_dbus_properties()

    def get_index(self):
        return self.properties["Index"]

    def get_name(self):
        return self.properties["Name"]

    def get_description(self):
        return self.properties["Description"]

    def get_priority(self):
        return self.properties["Priority"]

if __name__ == "__main__":
    pass
