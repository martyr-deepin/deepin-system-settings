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

try:
    import deepin_pulseaudio
except ImportError:
    print "----------Please Install Deepin Pulseaudio Python Binding----------"   
    print "git clone git@github.com:linuxdeepin/pypulseaudio.git"
    print "------------------------------------------------------------------"   
    exit(1)

MAX_VOLUME_VALUE = deepin_pulseaudio.VOLUME_UI_MAX
NORMAL_VOLUME_VALUE = deepin_pulseaudio.VOLUME_NORM

PULSE = deepin_pulseaudio.new()

def get_volume_balance(channel_num, volume_list, channel_list):
    return deepin_pulseaudio.volume_get_balance(channel_num, volume_list, channel_list)

def get_fallback_sink_index():
    name = PULSE.get_fallback_sink()
    dev = PULSE.get_output_devices()
    for key in dev.keys():
        if name == dev[key]['name']:
            return key
    return None

def get_fallback_source_index():
    name = PULSE.get_fallback_source()
    dev = PULSE.get_input_devices()
    for key in dev.keys():
        if name == dev[key]['name']:
            return key
    return None
