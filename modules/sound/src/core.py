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

class Core(BusBase):
        
    __gsignals__  = {
            "new-card":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "card-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "new-sink":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "sink-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "fallback-sink-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "fallback-sink-unset":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            "new-source":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "source-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "fallback-source-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "fallback-source-unset":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            "new-playback-stream":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "playback-stream-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "new-record-stream":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "record-stream-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "new-sample":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "sample-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "new-module":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "module-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "new-client":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "client-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "new-extension":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "extension-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,))
            }
    
    def __init__(self, path = "/org/pulseaudio/core1", interface = "org.PulseAudio.Core1"):
        BusBase.__init__(self, path, interface)

        self.init_dbus_properties()
        
        self.dbus_proxy.connect_to_signal("NewCard", self.new_card_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("CardRemoved", self.card_removed_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("NewSink", self.new_sink_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("SinkRemoved", self.sink_removed_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("FallbackSinkUpdated", self.fallback_sink_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("FallbackSinkUnset", self.fallback_sink_unset_cb, dbus_interface = 
                                          self.object_interface)

        self.dbus_proxy.connect_to_signal("NewPlaybackStream", self.new_playback_stream_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("PlaybackStreamRemoved", self.playback_stream_removed_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("NewRecordStream", self.new_record_stream_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("RecordStreamRemoved", self.record_stream_removed_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("NewSample", self.new_sample_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("SampleRemoved", self.sample_removed_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)
        
        self.dbus_proxy.connect_to_signal("NewModule", self.new_module_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)
        
        self.dbus_proxy.connect_to_signal("ModuleRemoved", self.module_removed_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)
        
        self.dbus_proxy.connect_to_signal("NewClient", self.new_client_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)
        
        self.dbus_proxy.connect_to_signal("ClientRemoved", self.client_removed_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)
        
        self.dbus_proxy.connect_to_signal("NewExtension", self.new_extension_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)
        
        self.dbus_proxy.connect_to_signal("ExtensionRemoved", self.extension_removed_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)
        
    ###Props    
    def get_interface_revision(self):
        return self.properties["InterfaceRevision"]

    def get_name(self):
        return self.properties["Name"]

    def get_version(self):
        return self.properties["Version"]
    
    def get_is_local(self):
        return self.properties["IsLocal"]

    def get_username(self):
        return self.properties["Username"]

    def get_hostname(self):
        return self.properties["Hostname"]

    def get_default_channels(self):
        if self.properties["DefaultChannels"]:
            return map(lambda x:int(x), self.properties["DefaultChannels"])
        else:
            return []

    def set_default_channels(self, default_channels):
        try:
            self.property_interface.Set(self.object_interface, "DefaultChannels", default_channels)
        except:
            traceback.print_exc()

    def get_default_sample_format(self):
        return self.properties["DefaultSampleFormat"]

    def set_default_sample_format(self, default_sample_format):
        try:
            self.property_interface.Set(self.object_interface, "DefaultSampleFormat", default_sample_format)
        except:
            traceback.print_exc()

    def get_default_sample_rate(self):
        return self.properties["DefaultSampleRate"]

    def set_default_sample_rate(self, default_sample_rate):
        try:
            self.property_interface.Set(self.object_interface, "DefaultSampleRate", default_sample_rate)
        except:
            traceback.print_exc()

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
        return str(self.properties["FallbackSink"])

    def set_fallback_sink(self, fallback_sink):
        try:
            self.property_interface.Set(self.object_interface, "FallbackSink", fallback_sink)
        except:
            traceback.print_exc()

    def get_sources(self):
        if self.properties["Sources"]:
            return map(lambda x:str(x), self.properties["Sources"])
        else:
            return []

    def get_fallback_source(self):
        return str(self.properties["FallbackSource"])

    def set_fallback_source(self, fallback_source):
        try:
            self.property_interface.Set(self.object_interface, "FallbackSource", fallback_source)
        except:
            traceback.print_exc()

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
    def new_card_cb(self, card):
        self.emit("new-card", card)

    def card_removed_cb(self, card):
        self.emit("card-removed", card)
    
    def new_sink_cb(self, sink):
        self.emit("new-sink", sink)
    
    def sink_removed_cb(self, sink):
        self.emit("sink-removed", sink)

    def fallback_sink_updated_cb(self, sink):
        self.emit("fallback-sink-updated", sink)

    def fallback_sink_unset_cb(self):
        self.emit("fallback-sink-unset")

    def new_source_cb(self, source):
        self.emit("new-source", source)

    def source_removed_cb(self, source):
        self.emit("source-removed", source)

    def fallback_source_udpated_cb(self, source):
        self.emit("fallback-source-updated", source)

    def fallback_source_unset_cb(self):
        self.emit("fallback-source-unset")

    def new_playback_stream_cb(self, playback_stream):
        self.emit("new-playback-stream", playback_stream)

    def playback_stream_removed_cb(self, playback_stream):
        self.emit("playback-stream-removed", playback_stream)

    def new_record_stream_cb(self, record_stream):
        self.emit("new-record-stream", record_stream)

    def record_stream_removed_cb(self, record_stream):
        self.emit("record-stream-removed", record_stream)

    def new_sample_cb(self, sample):
        self.emit("new-sample", sample)

    def sample_removed_cb(self, sample):
        self.emit("sample-removed", sample)

    def new_module_cb(self, module):
        self.emit("new-module", module)

    def module_removed_cb(self, module):
        self.emit("module-removed", module)

    def new_client_cb(self, client):
        self.emit("new-client", client)

    def client_removed_cb(self, client):
        self.emit("client-removed", client)

    def new_extension_cb(self, extension):
        self.emit("new-extension", extension)

    def extension_removed_cb(self, extension):
        self.emit("extension-removed", extension)

if __name__ == "__main__":
    core = Core()
    print core.get_modules()
    print "\n\n\n"
    print core.get_sources()
    print "\n\n\n"
    print core.get_sinks()
    print "\n\n\n"
