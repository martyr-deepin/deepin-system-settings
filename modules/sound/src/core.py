#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
#             Long Changjin <admin@longchangjin.cn>
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
import dbus

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

        self.listen_for_signal("", dbus.Array([], signature = 'o'))

        #self.dbus_proxy.connect_to_signal("NewCard", self.new_card_cb, dbus_interface = 
                                          #self.object_interface, arg0 = None)

        #self.dbus_proxy.connect_to_signal("CardRemoved", self.card_removed_cb, dbus_interface = 
                                          #self.object_interface, arg0 = None)

        #self.dbus_proxy.connect_to_signal("NewSink", self.new_sink_cb, dbus_interface = 
                                          #self.object_interface, arg0 = None)

        #self.dbus_proxy.connect_to_signal("SinkRemoved", self.sink_removed_cb, dbus_interface = 
                                          #self.object_interface, arg0 = None)
        ######
        self.bus.add_signal_receiver(self.new_card_cb, signal_name = "NewCard", dbus_interface = 
                                     self.object_interface, path = self.object_path)

        self.bus.add_signal_receiver(self.card_removed_cb, signal_name = "CardRemoved", dbus_interface = 
                                     self.object_interface, path = self.object_path)
        
        self.bus.add_signal_receiver(self.new_sink_cb, signal_name = "NewSink", dbus_interface = 
                                     self.object_interface, path = self.object_path)

        self.bus.add_signal_receiver(self.sink_removed_cb, signal_name = "SinkRemoved", dbus_interface = 
                                     self.object_interface, path = self.object_path)
        
        self.bus.add_signal_receiver(self.fallback_sink_updated_cb, signal_name = "FallbackSinkUpdated", dbus_interface = 
                                     self.object_interface, path = self.object_path)

        self.bus.add_signal_receiver(self.fallback_sink_unset_cb, signal_name = "FallbackSinkUnset", dbus_interface = 
                                     self.object_interface, path = self.object_path)
        
        self.bus.add_signal_receiver(self.new_source_cb, signal_name = "NewSource", dbus_interface = 
                                     self.object_interface, path = self.object_path)

        self.bus.add_signal_receiver(self.source_removed_cb, signal_name = "SourceRemoved", dbus_interface = 
                                     self.object_interface, path = self.object_path)
        
        self.bus.add_signal_receiver(self.fallback_source_udpated_cb, signal_name = "FallbackSourceUpdated", dbus_interface = 
                                     self.object_interface, path = self.object_path)

        self.bus.add_signal_receiver(self.fallback_source_unset_cb, signal_name = "FallbackSourceUnset", dbus_interface = 
                                     self.object_interface, path = self.object_path)
        
        self.bus.add_signal_receiver(self.new_playback_stream_cb, signal_name = "NewPlaybackStream", dbus_interface = 
                                     self.object_interface, path = self.object_path)

        self.bus.add_signal_receiver(self.playback_stream_removed_cb, signal_name = "PlaybackStreamRemoved", dbus_interface = 
                                     self.object_interface, path = self.object_path)
        
        self.bus.add_signal_receiver(self.new_record_stream_cb, signal_name = "NewRecordStream", dbus_interface = 
                                     self.object_interface, path = self.object_path)

        self.bus.add_signal_receiver(self.record_stream_removed_cb, signal_name = "RecordStreamRemoved", dbus_interface = 
                                     self.object_interface, path = self.object_path)
        
        self.bus.add_signal_receiver(self.new_sample_cb, signal_name = "NewSample", dbus_interface = 
                                     self.object_interface, path = self.object_path)

        self.bus.add_signal_receiver(self.sample_removed_cb, signal_name = "SampleRemoved", dbus_interface = 
                                     self.object_interface, path = self.object_path)
        
        self.bus.add_signal_receiver(self.new_module_cb, signal_name = "NewModule", dbus_interface = 
                                     self.object_interface, path = self.object_path)

        self.bus.add_signal_receiver(self.module_removed_cb, signal_name = "ModuleRemoved", dbus_interface = 
                                     self.object_interface, path = self.object_path)
        
        self.bus.add_signal_receiver(self.new_client_cb, signal_name = "NewClient", dbus_interface = 
                                     self.object_interface, path = self.object_path)

        self.bus.add_signal_receiver(self.client_removed_cb, signal_name = "ClientRemoved", dbus_interface = 
                                     self.object_interface, path = self.object_path)
        
        self.bus.add_signal_receiver(self.new_extension_cb, signal_name = "NewExtension", dbus_interface = 
                                     self.object_interface, path = self.object_path)

        self.bus.add_signal_receiver(self.extension_removed_cb, signal_name = "ExtensionRemoved", dbus_interface = 
                                     self.object_interface, path = self.object_path)
        
    ###Props    
    def get_interface_revision(self):
        return int(self.get_property("InterfaceRevision"))

    def get_name(self):
        return str(self.get_property("Name"))

    def get_version(self):
        return str(self.get_property("Version"))
    
    def get_is_local(self):
        return bool(self.get_property("IsLocal"))

    def get_username(self):
        return str(self.get_property("Username"))

    def get_hostname(self):
        return str(self.get_property("Hostname"))

    def get_default_channels(self):
        if self.get_property("DefaultChannels"):
            return map(lambda x:int(x), self.get_property("DefaultChannels"))
        else:
            return []

    def set_default_channels(self, default_channels):
        try:
            self.set_property("DefaultChannels", default_channels)
        except:
            traceback.print_exc()

    def get_default_sample_format(self):
        return int(self.properties["DefaultSampleFormat"])

    def set_default_sample_format(self, default_sample_format):
        try:
            self.set_property("DefaultSampleFormat", default_sample_format)
        except:
            traceback.print_exc()

    def get_default_sample_rate(self):
        return int(self.properties["DefaultSampleRate"])

    def set_default_sample_rate(self, default_sample_rate):
        try:
            self.set_property("DefaultSampleRate", default_sample_rate)
        except:
            traceback.print_exc()

    def get_cards(self):
        if self.get_property("Cards"):
            return map(lambda x:str(x), self.get_property("Cards"))
        else:
            return []

    def get_sinks(self):
        if self.get_property("Sinks"):
            return map(lambda x:str(x), self.get_property("Sinks"))
        else:
            return []

    def get_fallback_sink(self):
        return str(self.get_property("FallbackSink"))

    def set_fallback_sink(self, fallback_sink):
        try:
            self.set_property("FallbackSink", dbus.ObjectPath(fallback_sink))
        except:
            traceback.print_exc()

    def get_sources(self):
        if self.get_property("Sources"):
            return map(lambda x:str(x), self.get_property("Sources"))
        else:
            return []

    def get_fallback_source(self):
        return str(self.get_property("FallbackSource"))

    def set_fallback_source(self, fallback_source):
        try:
            self.set_property("FallbackSource", dbus.ObjectPath(fallback_source))
        except:
            traceback.print_exc()

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

    def get_samples(self):
        if self.get_property("Samples"):
            return map(lambda x:str(x), self.get_property("Samples"))
        else:
            return []

    def get_modules(self):
        if self.get_property("Modules"):
            return map(lambda x:str(x), self.get_property("Modules"))
        else:
            return []

    def get_clients(self):
        if self.get_property("Clients"):
            return map(lambda x:str(x), self.get_property("Clients"))
        else:
            return []

    def get_my_client(self):
        return str(self.get_property("MyClient"))

    def get_extensions(self):
        return str(self.get_property("Extensions"))
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

    def listen_for_signal(self, signal, objects):
        self.call_async("ListenForSignal", signal, objects)

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
