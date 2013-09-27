#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
#             Wang Yaohua <mr.asianwang@gmail.com>
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

import dbus
import gobject
from bus_utils import BusBase
from utils import bluetooth_uuid_to_string

class Device(BusBase):

    __gsignals__  = {
        "disconnect-requested":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT)),
        "node-created":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, )),
        "node-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, ))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.Device")
        self.device_path = device_path

        self.bus.add_signal_receiver(self.disconnect_requested_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "DisconnectRequested")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertyChanged")

        self.bus.add_signal_receiver(self.node_created_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "NodeCreated")

        self.bus.add_signal_receiver(self.node_removed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "NodeRemoved")

    def disconnect(self):
        return self.dbus_method("Disconnect")

    def discover_services(self, pattern = ""):
        return self.dbus_method("DiscoverServices", pattern)

    def cancel_discovery(self):
        return self.dbus_method("CancelDiscovery")

    def list_nodes(self):
        nodes = self.dbus_method("ListNodes")
        if nodes:
            nodes = map(lambda x:str(x), nodes)

        return nodes

    def create_node(self, uuid):
        return self.dbus_method("CreateNode", uuid)

    def remove_node(self, node_path):
        return self.dbus_method("RemoveNode", node_path)

    ###Props
    def get_properties(self):
        return self.dbus_method("GetProperties")

    def set_property(self, key, value):
        return self.dbus_method("SetProperty", key, value)

    def get_name(self):
        if "Name" in self.get_properties().keys():
            return self.get_properties()["Name"]

    def get_vendor(self):
        if "Vendor" in self.get_properties().keys():
            return self.get_properties()["Vendor"]

    def get_product(self):
        if "Product" in self.get_properties().keys():
            return self.get_properties()["Product"]

    def get_version(self):
        if "Version" in self.get_properties().keys():
            return self.get_properties()["Version"]

    def get_legacy_pairing(self):
        if "LegacyPairing" in self.get_properties().keys():
            return self.get_properties()["LegacyPairing"]

    def get_alias(self):
        if "Alias" in self.get_properties().keys():
            return self.get_properties()["Alias"]

    def set_alias(self, alias):
        self.set_property("Alias", alias)

    def get_icon(self):
        if "Icon" in self.get_properties().keys():
            return self.get_properties()["Icon"]

    def get_nodes(self):
        nodes = []
        if "Nodes" in self.get_properties().keys():
            nodes =  self.get_properties()["Nodes"]
            if nodes:
                nodes = map(lambda x:str(x), nodes)

        return nodes

    def get_paired(self):
        if "Paired" in self.get_properties().keys():
            return bool(self.get_properties()["Paired"])

    def get_connected(self):
        if "Connected" in self.get_properties().keys():
            return bool(self.get_properties()["Connected"])

    def get_blocked(self):
        if "Blocked" in self.get_properties().keys():
            return bool(self.get_properties()["Blocked"])

    def set_blocked(self, blocked):
        self.set_property("Blocked", dbus.Boolean(blocked))

    def get_trusted(self):
        if "Trusted" in self.get_properties().keys():
            return bool(self.get_properties()["Trusted"])

    def set_trusted(self, trusted):
        self.set_property("Trusted", dbus.Boolean(trusted))

    def get_adapter(self):
        if "Adapter" in self.get_properties().keys():
            return str(self.get_properties()["Adapter"])

    def get_address(self):
        if "Address" in self.get_properties().keys():
            return self.get_properties()["Address"]
        else:
            return None

    def get_class(self):
        if "Class" in self.get_properties().keys():
            return self.get_properties()["Class"]
        else:
            return None

    def get_uuids(self):
        uuids = []
        if "UUIDs" in self.get_properties().keys():
            uuids = self.get_properties()["UUIDs"]
            if uuids:
                uuids = map(lambda x:str(x), uuids)

        return uuids

    def get_services(self):
        if "Services" in self.get_properties().keys():
            services = self.get_properties()["Services"]
            if services:
                services = map(lambda x:str(x), services)
            return services
        return []

    def disconnect_requested_cb(self):
        self.emit("disconnect-requested")

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

    def node_created_cb(self, node_path):
        self.emit("node-created", node_path)

    def node_removed_cb(self, node_path):
        self.emit("node-removed", node_path)

class Audio(BusBase):

    __gsignals__  = {
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.Audio")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertyChanged")

    def a_connect(self):
        return self.dbus_method("Connect")

    def a_disconnect(self):
        return self.dbus_method("Disconnect")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def get_state(self):
        if "State" in self.get_properties().keys():
            return self.get_properties()["State"]

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class Headset(BusBase):

    __gsignals__  = {
        "answer-requested":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.Headset")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertyChanged")

        self.bus.add_signal_receiver(self.answer_requested_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "AnswerRequested")

    def hs_connect(self):
        return self.dbus_method("Connect")

    def hs_disconnect(self):
        return self.dbus_method("Disconnect")

    def is_connected(self):
        return self.dbus_method("IsConnected")

    def indicate_call(self):
        return self.dbus_method("IndicateCall")

    def cancel_call(self):
        return self.dbus_method("CancelCall")

    def play(self):
        return self.dbus_method("Play")

    def stop(self):
        return self.dbus_method("Stop")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def set_property(self, key, value):
        return self.dbus_method("SetProperty", key, value)

    def get_state(self):
        if "State" in self.get_properties().keys():
            return self.get_properties()["State"]

    def get_connected(self):
        if "Connected" in self.get_properties().keys():
            return self.get_properties()["Connected"]

    def get_playing(self):
        if "Playing" in self.get_properties().keys():
            return self.get_properties()["Playing"]
        else:
            return self.dbus_method("IsPlaying")

    def get_speaker_gain(self):
        if "SpeakerGain" in self.get_properties().keys():
            return self.get_properties()["SpeakerGain"]
        else:
            return self.dbus_method("GetSpeakerGain")

    def set_speaker_gain(self, gain):
        self.set_property("SpeakerGain", gain)

    def get_microphone_gain(self):
        if "MicrophoneGain" in self.get_properties().keys():
            return self.get_properties()["MicrophoneGain"]
        else:
            return self.dbus_method("GetMicrophoneGain")

    def set_microphone_gain(self, gain):
        self.set_property("MicrophoneGain", gain)

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

    def answer_requested_cb(self, key, value):
        self.emit("answer-requested", key, value)

class AudioSink(BusBase):

    __gsignals__  = {
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.AudioSink")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertyChanged")
    def as_connect(self):
        return self.dbus_method("Connect")

    def as_disconnect(self):
        return self.dbus_method("Disconnect")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def get_state(self):
        if "State" in self.get_properties().keys():
            return self.get_properties()["State"]

    def get_connected(self):
        if "Connected" in self.get_properties().keys():
            return self.get_properties()["Connected"]

    def get_playing(self):
        if "Playing" in self.get_properties().keys():
            return self.get_properties()["Playing"]

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class AudioSource(BusBase):

    __gsignals__  = {
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.AudioSource")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertyChanged")
    def as_connect(self):
        return self.dbus_method("Connect")

    def as_disconnect(self):
        return self.dbus_method("Disconnect")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def get_state(self):
        # Possible values: "disconnected", "connecting", "connected", "playing"
        if "State" in self.get_properties().keys():
            return self.get_properties()["State"]

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class HeadsetFreeGateway(BusBase):

    __gsignals__  = {
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT)),
        "ring":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "call-terminated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "call-started":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "call-ended":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.HeadsetGateway")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertyChanged")

        self.bus.add_signal_receiver(self.ring_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "Ring")

        self.bus.add_signal_receiver(self.call_terminated_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "CallTerminated")

        self.bus.add_signal_receiver(self.call_started_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "CallStarted")

        self.bus.add_signal_receiver(self.call_ended_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "CallEnded")

    def hfg_connect(self):
        return self.dbus_method("Connect")

    def hfg_disconnect(self):
        return self.dbus_method("Disconnect")

    def answer_call(self):
        return self.dbus_method("AnswerCall")

    def terminate_call(self):
        return self.dbus_method("TerminateCall")

    def call(self, number):
        return self.dbus_method("Call", number)

    def get_operator_name(self):
        return self.dbus_method("GetOperatorName")

    def send_dtmf(self, digits):
        return self.dbus_method("SendDTMF", digits)

    def get_subscriber_number(self):
        return self.dbus_method("GetSubscriberNumber")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def get_connected(self):
        if "Connected" in self.get_properties().keys():
            return self.get_properties()["Connected"]

    def get_registration_status(self):
        if "RegistrationStatus" in self.get_properties().keys():
            return self.get_properties()["RegistrationStatus"]

    def get_signal_strength(self):
        if "SignalStrength" in self.get_properties().keys():
            return self.get_properties()["SignalStrength"]

    def get_roaming_status(self):
        if "RoamingStatus" in self.get_properties().keys():
            return self.get_properties()["RoamingStatus"]

    def get_battery_charge(self):
        if "BatteryCharge" in self.get_properties().keys():
            return self.get_properties()["BatteryCharge"]

    def get_speaker_gain(self):
        if "Connected" in self.get_properties().keys():
            return self.get_properties()["Connected"]

    def get_microphone_gain(self):
        if "MicrophoneGain" in self.get_properties().keys():
            return self.get_properties()["MicrophoneGain"]

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

    def ring_cb(self, number):
        self.emit("ring", number)

    def call_terminated_cb(self):
        self.emit("call-terminated")

    def call_started_cb(self):
        self.emit("call-started")

    def call_ended_cb(self):
        self.emit("call-ended")

class Control(BusBase):

    __gsignals__  = {
        "connected":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "disconnected":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.Control")

        self.bus.add_signal_receiver(self.connected_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "Connected")

        self.bus.add_signal_receiver(self.disconnected_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "Disconnected")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertyChanged")

    def volume_up(self):
        return self.dbus_method("VolumeUp")

    def volume_down(self):
        return self.dbus_method("VolumeDown")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def get_connected(self):
        if "Connected" in self.get_properties().keys():
            return self.get_properties()["Connected"]
        else:
            return bool(self.dbus_method("IsConnected"))

    def connected_cb(self):
        self.emit("connected")

    def disconnected_cb(self):
        self.emit("disconnected")

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class HealthManager(BusBase):

    __gsignals__  = {
        "channel-connected":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "channel-deleted":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.HealthDevice")

        self.bus.add_signal_receiver(self.channel_connected_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "ChannelConnected")

        self.bus.add_signal_receiver(self.channel_deleted_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "ChannelDeleted")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertyChanged")

    def echo(self):
        return self.dbus_method("Echo")

    def create_channel(self, application, configuration):
        return self.dbus_method("CreateChannel", application, configuration)

    def destroy_channel(self, channel):
        return self.dbus_method("DestroyChannel", channel)

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def get_mainchannel(self):
        if "MainChannel" in self.get_properties().keys():
            return self.get_properties()["MainChannel"]

    def channel_connected_cb(self, channel):
        self.emit("channel-connected", channel)

    def channel_deleted_cb(self, channel):
        self.emit("disconnected", channel)

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class HandsfreeGateway(BusBase):

    __gsignals__  = {
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.HandsfreeGateway")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertyChanged")
    def hfg_connect(self):
        return self.dbus_method("Connect")

    def hfg_disconnect(self):
        return self.dbus_method("Disconnect")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def get_state(self):
        if "State" in self.get_properties().keys():
            return self.get_properties()["State"]

    def register_agent(self, agent_path):
        return self.dbus_method("RegisterAgent", agent_path)

    def unregister_agent(self, agent_path):
        return self.dbus_method("UnregisterAgent", agent_path)

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class Network(BusBase):

    __gsignals__  = {
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.Network")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertyChanged")

    def n_connect(self, uuid):
        return self.dbus_method("Connect", uuid)

    def n_disconnect(self):
        return self.dbus_method("Disconnect")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def get_connected(self):
        if "Connected" in self.get_properties().keys():
            return self.get_properties()["Connected"]

    def get_interface(self):
        if "Interface" in self.get_properties().keys():
            return self.get_properties()["Interface"]

    def get_uuid(self):
        if "UUID" in self.get_properties().keys():
            return self.get_properties()["UUID"]

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class Input(BusBase):

    __gsignals__  = {
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.Input")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "PropertyChanged")

    def i_connect(self):
        return self.dbus_method("Connect")

    def i_disconnect(self):
        return self.dbus_method("Disconnect")

    def get_properties(self):
        return self.dbus_method("GetProperties")

    def get_connected(self):
        if "Connected" in self.get_properties().keys():
            return self.get_properties()["Connected"]

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

class Serial(BusBase):

    def __init__(self, device_path):
        BusBase.__init__(self, path = device_path, interface = "org.bluez.Serial")

    def s_connect(self, pattern):
        return self.dbus_method("Connect", pattern)

    def connect_fd(self, pattern):
        return self.dbus_method("ConnectFD", pattern)

    def s_disconnect(self, device):
        return self.dbus_method("Disconnect", device)


if __name__ == "__main__":
    from manager import Manager
    from adapter import Adapter

    adapter = Adapter(Manager().get_default_adapter())

    device = Device(adapter.get_devices()[0])

    # print "Name:\n    %s" % device.get_name()
    # device.set_alias("Long's Phone")
    # print "Alias:\n    %s" % device.get_alias()
    # print "Paired:\n    %s" % device.get_paired()
    # print "Adapter:\n   %s" % device.get_adapter()
    # print "Connected:\n   %s" % device.get_connected()
    # print "UUIDs:\n   %s" % device.get_uuids()
    # print "Address:\n   %s" % device.get_address()
    # print "Find Device:\n   %s" %adapter.find_device(device.get_address())
    # print "Services:\n   %s" % device.get_services()
    # print "Class:\n   %s" % device.get_class()
    # device.set_blocked(True)
    # print "Blocked:\n   %s" % device.get_blocked()
    # device.set_trusted(False)
    # print "Trusted:\n   %s" % device.get_trusted()
    # print "Icon:\n   %s" % device.get_icon()

    # from utils import bluetooth_uuid_to_string
    # for uuid in device.get_uuids():
    #     print bluetooth_uuid_to_string(uuid)

    from utils import bluetooth_class_to_type
    print bluetooth_class_to_type(device.get_class())
