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

class Core(BusBase):
    
    def __init__(self, path = "/org/pulseaudio/core1", interface = "org.PulseAudio.Core1"):
        BusBase.__init__(self, path, interface)

        self.init_dbus_properties()
        
    ###Props    
    def get_interface_revision(self):
        return self.properties["InterfaceRevision"]

    def get_name(self):
        return self.properties["Name"]

    def get_version(self):
        return self.properties["Version"]
    
    def get_is_local(self):
        return self.properties["IsLoacl"]

    def get_username(self):
        return self.properties["Username"]

    def get_hostname(self):
        return self.properties["Hostname"]

    def get_default_channels(self):
        return self.properties["DefaultChannels"]

    def set_default_channels(self):
        pass

    def get_default_sample_format(self):
        return self.properties["DefaultSampleFormat"]

    def set_default_sample_format(self):
        pass

    def get_default_sample_rate(self):
        return self.properties["DefaultSampleRate"]

    def get_cards(self):
        if self.properties["Cards"]:
            return map(lambda x:str(x), self.properties["Cards"])
        else:
            return []

    def get_sinks(self):
        if self.properties["Sinks"]:
            return map(lambda x:str(x), self.properties["Sinks"])
        else:
            return []

    def get_fallback_sink(self):
        pass

    def set_fallback_sink(self):
        pass

    def get_sources(self):
        if self.properties["Sources"]:
            return map(lambda x:str(x), self.properties["Sources"])
        else:
            return []

    def get_fallback_source(self):
        pass

    def set_fallback_source(self):
        pass

    def get_palyback_streams(self):
        if self.properties["PlaybackStreams"]:
            return map(lambda x:str(x), self.properties["PlaybackStreams"])
        else:
            return []

    def get_record_streams(self):
        if self.properties["RecordStreams"]:
            return map(lambda x:str(x), self.properties["RecordStreams"])
        else:
            return []

    def get_samples(self):
        if self.properties["Samples"]:
            return map(lambda x:str(x), self.properties["Samples"])
        else:
            return []

    def get_modules(self):
        if self.properties["Modules"]:
            return map(lambda x:str(x), self.properties["Modules"])
        else:
            return []

    def get_clients(self):
        if self.properties["Clients"]:
            return map(lambda x:str(x), self.properties["Clients"])
        else:
            return []

    def get_my_client(self):
        return self.properties["MyClient"]

    def get_extensions(self):
        return self.properties["Extensions"]
    
    ###Methods
    def get_card_by_name(self, name):
        return str(self.dbus_method("GetCardByName", name))

    def get_sink_by_name(self, name):
        return str(self.dbus_method("GetSinkByName", name))

    def get_source_by_name(self, name):
        return str(self.dbus_method("GetSourceByName", name))

    def get_sample_by_name(self, name):
        return str(self.dbus_method("GetSampleByName", name))

    def upload_sample(self, name, sample_format, sample_rate, channels, default_volume, property_list, data):
        return str(self.dbus_method("UploadSample", name, sample_format, sample_rate,
                                    channels, default_volume, property_list, data))
        
    def load_module(self, name, arguments):
        return str(self.dbus_method("LoadModule", name, arguments))
        
    def exit(self):
        self.call_async("Exit", reply_handler = None, error_handler = None)

    def listen_for_signal(self, signal):
        if self.dbus_method("ListenForSignal", signal):
            return map(lambda x:str(x), self.dbus_method("ListenForSignal", signal))
        else:
            return []

    def stop_listening_for_signal(self, signal):
        self.call_async("StopListeningForSignal", signal)

    ###Signals
    
    
if __name__ == "__main__":
    core = Core()
    print core.get_modules()
    print "\n\n\n"
    print core.get_sources()
    print "\n\n\n"
    print core.get_sinks()
    print "\n\n\n"
