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

MOUSE_SETTINGS_CONF = "org.gnome.settings-daemon.peripherals.mouse"
MOUSE_SETTINGS = deepin_gsettings.new(MOUSE_SETTINGS_CONF)

MOUSE_DEFAULT_SETTINGS = {
    "left_handed"           : False,
    "motion_acceleration"   : 1.0,
    "motion_threshold"      : 1,
    "double_click"          : 400}

def mouse_set_left_handed(left_handed):
    '''
    set mouse is left-handed
    @param left_handed: is left hand, a bool type
    '''
    MOUSE_SETTINGS.set_boolean("left-handed", left_handed)


def mouse_get_left_handed():
    '''
    get mouse whether left-handed
    @return: True if is left hand, otherwise False
    '''
    return MOUSE_SETTINGS.get_boolean("left-handed")


# mouse speed set
def mouse_set_motion_acceleration(value):
    '''
    set mouse motion acceleration
    @param value: the acceleration value, a double type, 1.0 ~ 10.0
    '''
    MOUSE_SETTINGS.set_double("motion-acceleration", value)


def mouse_get_motion_acceleration():
    '''
    get mouse motion acceleration
    @return: the motion acceleration, a double type
    '''
    return MOUSE_SETTINGS.get_double("motion-acceleration")


# mouse Sensitivity set
def mouse_set_motion_threshold(value):
    '''
    set mouse motion threshold
    @param value: the threshold value, an int type, 1 ~ 10
    '''
    MOUSE_SETTINGS.set_int("motion-threshold", int(value))


def mouse_get_motion_threshold():
    '''
    get mouse motion acceleration
    @return: the motion acceleration, an int type
    '''
    return MOUSE_SETTINGS.get_int("motion-threshold")


def mouse_set_double_click(value):
    '''
    set mouse double click time
    @param value: the double click time, an int type, 100 ~ 1000
    '''
    MOUSE_SETTINGS.set_int("double-click", int(value))


def mouse_get_double_click():
    '''
    get mouse double click time
    @return: the double click time, an int type
    '''
    return MOUSE_SETTINGS.get_int("double-click")


def mouse_set_to_default():
    '''set all value to default'''
    #mouse_set_left_handed(MOUSE_DEFAULT_SETTINGS["left_handed"])
    #mouse_set_motion_acceleration(MOUSE_DEFAULT_SETTINGS["motion_acceleration"])
    #mouse_set_motion_threshold(MOUSE_DEFAULT_SETTINGS["motion_threshold"])
    #mouse_set_double_click(MOUSE_DEFAULT_SETTINGS["double_click"])
    MOUSE_SETTINGS.reset("left-handed")
    MOUSE_SETTINGS.reset("motion-acceleration")
    MOUSE_SETTINGS.reset("motion-threshold")
    MOUSE_SETTINGS.reset("double-click")


def mouse_get_default_settings():
    '''
    get default settings
    @return: the default settings, a dict type
    '''
    return MOUSE_DEFAULT_SETTINGS

# TODO 增加鼠标滚轮设置
