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
    import deepin_gsettings                                                      
except ImportError:                                                                 
    print "----------Please Install Deepin GSettings Python Binding----------"   
    print "git clone git@github.com:linuxdeepin/deepin-gsettings.git"            
    print "------------------------------------------------------------------"   
from gtk import gdk

MOUSE_SETTINGS_CONF = "org.gnome.settings-daemon.peripherals.mouse"
TOUCHPAD_SETTINGS_CONF = "org.gnome.settings-daemon.peripherals.touchpad"
MOUSE_SETTINGS = deepin_gsettings.new(MOUSE_SETTINGS_CONF)
TOUCHPAD_SETTINGS = deepin_gsettings.new(TOUCHPAD_SETTINGS_CONF)

TOUCHPAD_DEFAULT_SETTINGS = {
    "left_handed"           : "mouse",
    "motion_acceleration"   : -1.0,
    "motion_threshold"      : -1,
    # MOUSE_DEFAULT_SETTINGS
    "double_click"          : 400,
    "drag_threshold"        : 8}


def touchpad_set_left_handed(left_handed):
    '''
    set touchpad is left-handed
    @param left_handed: is left hand, a string type. must be one of ["left", "right", "mouse"]
    '''
    if left_handed not in ["left", "right", "mouse"]:
        return
    TOUCHPAD_SETTINGS.set_string("left-handed", left_handed)


def touchpad_get_left_handed():
    '''
    get touchpad whether left-handed
    @return: current touchpad left-handed set, a string type
    '''
    return TOUCHPAD_SETTINGS.get_string("left-handed")


def mouse_get_left_handed():
    '''
    get mouse whether left-handed
    @return: current touchpad left-handed set, a string type
    '''
    return MOUSE_SETTINGS.get_boolean("left-handed")


# mouse speed set
def touchpad_set_motion_acceleration(value):
    '''
    set touchpad motion acceleration
    @param value: the acceleration value, a double type, 1.0 ~ 10.0
    '''
    TOUCHPAD_SETTINGS.set_double("motion-acceleration", value)


def touchpad_get_motion_acceleration():
    '''
    get touchpad motion acceleration
    @return: the motion acceleration, a double type
    '''
    return TOUCHPAD_SETTINGS.get_double("motion-acceleration")


# mouse Sensitivity set
def touchpad_set_motion_threshold(value):
    '''
    set touchpad motion threshold
    @param value: the threshold value, an int type, 1 ~ 10
    '''
    TOUCHPAD_SETTINGS.set_int("motion-threshold", int(value))


def touchpad_get_motion_threshold():
    '''
    get touchpad motion acceleration
    @return: the motion acceleration, an int type
    '''
    return TOUCHPAD_SETTINGS.get_int("motion-threshold")


def touchpad_set_double_click(value):
    '''
    set touchpad double click time
    @param value: the double click time, an int type, 100 ~ 1000
    '''
    MOUSE_SETTINGS.set_int("double-click", int(value))


def touchpad_get_double_click():
    '''
    get touchpad double click time
    @return: the double click time, an int type
    '''
    return MOUSE_SETTINGS.get_int("double-click")

def touchpad_set_drag_threshold(value):
    '''
    set drag threshold time out
    @param value: the drag threshold time, an int type, 1 ~ 10
    '''
    MOUSE_SETTINGS.set_int("drag-threshold", int(value))

def touchpad_get_drag_threshold():
    '''
    get drag threshold time out
    @return: the drag threshold time
    '''
    return MOUSE_SETTINGS.get_int("drag-threshold")


def touchpad_set_to_default():
    '''set all value to default'''
    #touchpad_set_left_handed(TOUCHPAD_DEFAULT_SETTINGS["left_handed"])
    #touchpad_set_motion_acceleration(TOUCHPAD_DEFAULT_SETTINGS["motion_acceleration"])
    #touchpad_set_motion_threshold(TOUCHPAD_DEFAULT_SETTINGS["motion_threshold"])
    #touchpad_set_double_click(TOUCHPAD_DEFAULT_SETTINGS["double_click"])
    #touchpad_set_drag_threshold(TOUCHPAD_DEFAULT_SETTINGS["drag_threshold"])
    TOUCHPAD_SETTINGS.reset("left-handed")
    TOUCHPAD_SETTINGS.reset("motion-acceleration")
    TOUCHPAD_SETTINGS.reset("motion-threshold")
    MOUSE_SETTINGS.reset("double-click")
    MOUSE_SETTINGS.reset("drag-threshold")

def touchpad_get_default_settings():
    '''
    get default settings
    @return: the default settings, a dict type
    '''
    return TOUCHPAD_DEFAULT_SETTINGS

def is_has_touchpad():
    devices = gdk.devices_list()
    for d in devices:
        name = d.get_name().lower()
        if "touchpad" in name:
            return True
    return False
