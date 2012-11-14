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
import dbus
import traceback

#Channel positions
#
#    0 : Mono
#    1 : Front left
#    2 : Front right
#    3 : Front center
#    4 : Rear center
#    5 : Rear left
#    6 : Rear right
#    7 : LFE
#    8 : Front left of center
#    9 : Front right of center
#    10 : Side left
#    11 : Side right
#    12 : Aux 0
#    13 : Aux 1
#    14 : Aux 2
#    15 : Aux 3
#    16 : Aux 4
#    17 : Aux 5
#    18 : Aux 6
#    19 : Aux 7
#    20 : Aux 8
#    21 : Aux 9
#    22 : Aux 10
#    23 : Aux 11
#    24 : Aux 12
#    25 : Aux 13
#    26 : Aux 14
#    27 : Aux 15
#    28 : Aux 16
#    29 : Aux 17
#    30 : Aux 18
#    31 : Aux 19
#    32 : Aux 20
#    33 : Aux 21
#    34 : Aux 22
#    35 : Aux 23
#    36 : Aux 24
#    37 : Aux 25
#    38 : Aux 26
#    39 : Aux 27
#    40 : Aux 28
#    41 : Aux 29
#    42 : Aux 30
#    43 : Aux 31
#    44 : Top center
#    45 : Top front left
#    46 : Top front right
#    47 : Top front center
#    48 : Top rear left
#    49 : Top rear right
#    50 : Top rear center 
#
#Device states
#
#    0 : Running, the device is being used by at least one non-corked stream.
#    1 : Idle, the device is active, but no non-corked streams are connected to it.
#    2 : Suspended, the device is not in use and may be currently closed. 

try:
    PA_CORE = core.Core()
    PA_SINK_LIST = PA_CORE.get_sinks()
    PA_SOURCE_LIST = PA_CORE.get_sources()
except:
    print "PulseAudio dbus error:"
    traceback.print_exc()
    PA_CORE = None
    PA_SINK_LIST = []
    PA_SOURCE_LIST = []

PA_DEVICE = {}
PA_CHANNELS = {}
if PA_SINK_LIST:
    for sink in PA_SINK_LIST:
        PA_DEVICE[sink] = device.Device(sink)
        PA_CHANNELS[sink] = PA_DEVICE[sink].get_channels()

if PA_SOURCE_LIST:
    for source in PA_SOURCE_LIST:
        PA_DEVICE[source] = device.Device(source)
        PA_CHANNELS[source] = PA_DEVICE[source].get_channels()

print PA_DEVICE
print PA_CHANNELS
