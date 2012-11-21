#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
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

import core
import device
import card
import dbus
import traceback

#Channel positions
#
#0 : Mono; 1 : Front left; 2 : Front right; 3 : Front center; 4 : Rear center; 5 : Rear left
#6 : Rear right; 7 : LFE; 8 : Front left of center; 9 : Front right of center; 10 : Side left
#11 : Side right; 12 : Aux 0; 13 : Aux 1; 14 : Aux 2; 15 : Aux 3
#16 : Aux 4; 17 : Aux 5; 18 : Aux 6; 19 : Aux 7; 20 : Aux 8
#21 : Aux 9; 22 : Aux 10; 23 : Aux 11; 24 : Aux 12; 25 : Aux 13
#26 : Aux 14; 27 : Aux 15; 28 : Aux 16; 29 : Aux 17; 30 : Aux 18
#31 : Aux 19; 32 : Aux 20; 33 : Aux 21; 34 : Aux 22; 35 : Aux 23
#36 : Aux 24; 37 : Aux 25; 38 : Aux 26; 39 : Aux 27; 40 : Aux 28
#41 : Aux 29; 42 : Aux 30; 43 : Aux 31; 44 : Top center; 45 : Top front left
#46 : Top front right; 47 : Top front center; 48 : Top rear left; 49 : Top rear right; 50 : Top rear center 
#
#Device states
#
#    0 : Running, the device is being used by at least one non-corked stream.
#    1 : Idle, the device is active, but no non-corked streams are connected to it.
#    2 : Suspended, the device is not in use and may be currently closed. 

DEVICE_STATE_RUNNING = 0
DEVICE_STATE_IDLE = 1
DEVICE_STATE_SUSPENDED = 2

FULL_VOLUME_VALUE = 65536   # the 100% volume
MAX_VOLUME_VALUE = 99957    # the max volume

try:
    PA_CORE = core.Core()
    PA_SINK_LIST = PA_CORE.get_sinks()
    PA_SOURCE_LIST = PA_CORE.get_sources()
    PA_CARD_LIST = PA_CORE.get_cards()
except:
    print "PulseAudio dbus error: ---------------------------------------------"
    traceback.print_exc()
    PA_CORE = None
    PA_SINK_LIST = []
    PA_SOURCE_LIST = []
    PA_CARD_LIST = []

try:
    CURRENT_SINK = PA_CORE.get_fallback_sink()
except:
    CURRENT_SINK = None
try:
    CURRENT_SOURCE = PA_CORE.get_fallback_source()
except:
    CURRENT_SOURCE = None

PA_CARDS = {}           # All Device that this Card container.
PA_CARDS[None] = {"obj": None, "sink": [], "source": []}
for cards in PA_CARD_LIST:
    PA_CARDS[cards] = {"obj": card.Card(cards), "sink": [], "source": []}

PA_DEVICE = {}    # All Device
PA_CHANNELS = {}  # Each Channels

LEFT_CHANNELS = [1, 5, 8, 10, 45, 48]
RIGHT_CHANNELS = [2, 6, 9, 11, 46, 49]
def init_dev_list(dev_list, dev_type):
    global PA_DEVICE
    global PA_CHANNELS
    global PA_CARDS
    for d in dev_list:
        dev = device.Device(d)
        if dev_type == 'sink':
            if not dev.get_ports() and d != CURRENT_SINK: # if the device does not have any ports, ignore it
                continue
        else:
            if not dev.get_ports() and d != CURRENT_SOURCE: # if the device does not have any ports, ignore it
                continue
        PA_DEVICE[d] = dev
        dev_channels = {}
        channels = PA_DEVICE[d].get_channels()
        dev_channels["channel_num"] = len(channels)
        dev_channels["left"] = []
        dev_channels["right"] = []
        dev_channels["other"] = []
        i = 0
        while i < dev_channels["channel_num"]:
            if channels[i] in LEFT_CHANNELS:
                dev_channels["left"].append(i)
            elif channels[i] in RIGHT_CHANNELS:
                dev_channels["right"].append(i)
            else:
                dev_channels["other"].append(i)
            i += 1
        try:
            cards = dev.get_card()
            PA_CARDS[cards][dev_type].append(dev)
        except:
            traceback.print_exc()
        PA_CHANNELS[d] = dev_channels

init_dev_list(PA_SINK_LIST, 'sink')
init_dev_list(PA_SOURCE_LIST, 'source')

###############################################
def get_object_property_list(obj):
    '''
    get DBus Object PropertyList
    @param obj: a PulseAudio DBus Object object
    @return: a dict type
    '''
    prop_list = obj.get_property_list()
    prop = {}
    if not prop_list:
        return prop
    for k in prop_list:
        prop[k] = str(bytearray(prop_list[k]))
    return prop

def get_volume(dev):
    '''
    get device volume
    @param dev: a device path
    @return: a int type
    '''
    return max(PA_DEVICE[dev].get_volume())

def set_volume(dev, volume):
    '''
    get device volume
    @param dev: a device path
    @param volume: a int type
    '''
    volumes_list = [volume] * PA_CHANNELS[dev]["channel_num"]
    PA_DEVICE[dev].set_volume(dbus.Array(volumes_list, signature=dbus.Signature('u')))

def set_volumes(dev, volumes):
    '''
    get device volume
    @param dev: a device path
    @param volumes: a list contain left-volume and right-volume
    '''
    volumes_list = [0] * PA_CHANNELS[dev]["channel_num"]
    for channel in PA_CHANNELS[dev]["left"]:
        volumes_list[channel] = volumes[0]
    for channel in PA_CHANNELS[dev]["right"]:
        volumes_list[channel] = volumes[1]
    for channel in PA_CHANNELS[dev]["other"]:
        if volumes[0] < volumes[1]:     # is right channel
            volumes_list[channel] = volumes[1]
        else:                           # is left channel
            volumes_list[channel] = volumes[0]
    PA_DEVICE[dev].set_volume(dbus.Array(volumes_list, signature=dbus.Signature('u')))

def get_volumes(dev):
    '''
    get device volume
    @param dev: a device path
    @return: a list contain left-volume and right-volume
    '''
    d = PA_DEVICE[dev]
    volume = d.get_volume()
    left_volumes = []
    right_volumes = []
    for channel in PA_CHANNELS[dev]['left']:
        left_volumes.append(volume[channel])
    for channel in PA_CHANNELS[dev]['right']:
        right_volumes.append(volume[channel])
    if not left_volumes:
        left_volumes.append(0)
    if not right_volumes:
        right_volumes.append(0)
    return [max(left_volumes), max(right_volumes)]

def set_mute(dev, is_mute):
    '''
    get device whether mute
    @param dev: a device path
    @param is_mute: whether is mute, a bool type
    '''
    device.Device(dev).set_mute(is_mute)

def get_mute(dev):
    '''
    get device whether mute
    @param dev: a device path
    @return: a bool type
    '''
    return device.Device(dev).get_mute()

def get_port_list(dev):
    '''
    get device port list
    @param dev: a device path
    @return: a list contain some tuple which format :(device_port, ...), index
    '''
    d = device.Device(dev)
    ports = d.get_ports()
    if not ports:
        return []
    back = []
    active_port = d.get_active_port()
    i = 0
    n = 0
    for port in ports:
        p = device.DevicePort(port)
        if port == active_port:
            n = i
        back.append(p)
        i += 1
    return (back, n)
##########################################################
def refresh_info():
    ''' refresh and update pulseaudio info '''
    if not PA_CORE:
        return
    # get device list
    global PA_SINK_LIST
    global PA_SOURCE_LIST
    global PA_CARD_LIST
    try:
        PA_SINK_LIST = PA_CORE.get_sinks()
        PA_SOURCE_LIST = PA_CORE.get_sources()
        PA_CARD_LIST = PA_CORE.get_cards()
    except:
        print "PulseAudio dbus error: ---------------------------------------------"
        traceback.print_exc()
        PA_SINK_LIST = []
        PA_SOURCE_LIST = []
        PA_CARD_LIST = []
    # get current device
    global CURRENT_SINK
    global CURRENT_SOURCE
    try:
        CURRENT_SINK = PA_CORE.get_fallback_sink()
    except:
        CURRENT_SINK = None
    try:
        CURRENT_SOURCE = PA_CORE.get_fallback_source()
    except:
        CURRENT_SOURCE = None
    global PA_DEVICE
    global PA_CHANNELS
    global PA_CARDS
    PA_CARDS = {}
    PA_CARDS[None] = {"obj": None, "sink": [], "source": []}
    for cards in PA_CARD_LIST:
        PA_CARDS[cards] = {"obj": card.Card(cards), "sink": [], "source": []}
    PA_DEVICE = {}
    PA_CHANNELS = {}
    init_dev_list(PA_SINK_LIST, 'sink')
    init_dev_list(PA_SOURCE_LIST, 'source')


#print PA_CORE
#print PA_DEVICE
#print PA_CHANNELS
#print PA_SINK_LIST
#print PA_SOURCE_LIST
#print PA_CARD_LIST
#print PA_CARDS
#print CURRENT_SINK, CURRENT_SOURCE
