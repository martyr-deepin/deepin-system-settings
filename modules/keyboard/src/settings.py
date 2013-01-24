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

import gconf
from gtk import gdk

# typing setting
KEYBOARD_SETTINGS_CONF = "org.gnome.settings-daemon.peripherals.keyboard"
TOUCHPAD_SETTINGS_CONF = "org.gnome.settings-daemon.peripherals.touchpad"
DESKTOP_SETTINGS_CONF = "org.gnome.desktop.interface"
# layout setting
XKB_DESKTOP_SETTINGS_CONF = "org.gnome.libgnomekbd.desktop"
XKB_KEYBOARD_SETTINGS_CONF = "org.gnome.libgnomekbd.keyboard"
# shortcuts setting
WM_SHORTCUTS_SETTINGS_CONF = "org.gnome.desktop.wm.keybindings"
SHORTCUTS_SETTINGS_CONF = "org.gnome.settings-daemon.plugins.media-keys"
DP_SHORTCUTS_SETTINGS_CONF = "org.gnome.settings-daemon.plugins.keybindings"

# typing setting
KEYBOARD_SETTINGS = deepin_gsettings.new(KEYBOARD_SETTINGS_CONF)
TOUCHPAD_SETTINGS = deepin_gsettings.new(TOUCHPAD_SETTINGS_CONF)
DESKTOP_SETTINGS = deepin_gsettings.new(DESKTOP_SETTINGS_CONF)
# layout setting
XKB_DESKTOP_SETTINGS = deepin_gsettings.new(XKB_DESKTOP_SETTINGS_CONF)
XKB_KEYBOARS_SETTINGS = deepin_gsettings.new(XKB_KEYBOARD_SETTINGS_CONF)
# shortcuts setting
WM_SHORTCUTS_SETTINGS = deepin_gsettings.new(WM_SHORTCUTS_SETTINGS_CONF)
SHORTCUTS_SETTINGS = deepin_gsettings.new(SHORTCUTS_SETTINGS_CONF)
DP_SHORTCUTS_SETTINGS = deepin_gsettings.new(DP_SHORTCUTS_SETTINGS_CONF)
GCONF_CLIENT = gconf.client_get_default()

KEYBOARD_DEFAULT_SETTINGS = {
    # keyboard set
    "delay"                : 500,
    "repeat-interval"      : 30,
    # desktop intreface set
    "cursor-blink-time"    : 1200,
    # touchpad set
    "disable-while-typing" : False}

XKB_KEYBOARD_DEFAULT_SETTINGS = {
    # XKeyBoard set
    "default-group"        : -1,
    "group-per-window"     : False,
    "layouts"              : '[]',
    "options"              : '[]'}

#####################
# typing set
def keyboard_set_repeat_delay(value):
    '''
    set keyboard repeat delay
    @param value: the delay time, 100 ~ 2000
    '''
    if not KEYBOARD_SETTINGS.get_boolean("repeat"):
        KEYBOARD_SETTINGS.set_boolean("repeat", True)
    KEYBOARD_SETTINGS.set_uint("delay", int(value))


def keyboard_get_repeat_delay():
    '''
    get keyboard repeat delay
    @return: the delay time, an int type
    '''
    return KEYBOARD_SETTINGS.get_uint("delay")


def keyboard_set_repeat_interval(value):
    '''
    set keyboard repeat interval time
    @param value: the interval time, 2000 ~ 20
    '''
    if not KEYBOARD_SETTINGS.get_boolean("repeat"):
        KEYBOARD_SETTINGS.set_boolean("repeat", True)
    KEYBOARD_SETTINGS.set_uint("repeat-interval", int(value))


def keyboard_get_repeat_interval():
    '''
    get keyboard repeat interval time
    @return: the repeat interval time, an int type
    '''
    return KEYBOARD_SETTINGS.get_uint("repeat-interval")


# desktop set
def keyboard_set_cursor_blink_time(value):
    '''
    set keyboard repeat interval time
    @param value: the interval time, 2500 ~ 100
    '''
    if not DESKTOP_SETTINGS.get_boolean("cursor-blink"):
        DESKTOP_SETTINGS.set_boolean("cursor-blink", True)
    DESKTOP_SETTINGS.set_int("cursor-blink-time", int(value))


def keyboard_get_cursor_blink_time():
    '''
    get keyboard repeat interval time
    @return: the repeat interval time, an int type
    '''
    return DESKTOP_SETTINGS.get_int("cursor-blink-time")


# touchpad set
def keyboard_set_disable_touchpad_while_typing(is_disable):
    '''
    set disable touchpad while typing
    @param is_disable: if touchpad is disable, a boolean type
    '''
    TOUCHPAD_SETTINGS.set_boolean("disable-while-typing", is_disable)


def keyboard_get_disable_touchpad_while_typing():
    '''
    get disable touchpad while typing
    @return: True if set to disable, otherwise False
    '''
    return TOUCHPAD_SETTINGS.get_boolean("disable-while-typing")


def keyboard_set_to_default():
    '''set all value to default'''
    #keyboard_set_repeat_delay(KEYBOARD_DEFAULT_SETTINGS["delay"])
    #keyboard_set_repeat_interval(KEYBOARD_DEFAULT_SETTINGS["repeat-interval"])
    #keyboard_set_cursor_blink_time(KEYBOARD_DEFAULT_SETTINGS["cursor-blink-time"])
    #keyboard_set_disable_touchpad_while_typing(KEYBOARD_DEFAULT_SETTINGS["disable-while-typing"])
    KEYBOARD_SETTINGS.reset("delay")
    KEYBOARD_SETTINGS.reset("repeat-interval")
    DESKTOP_SETTINGS.reset("cursor-blink-time")
    TOUCHPAD_SETTINGS.reset("disable-while-typing")


def keyboard_get_default_settings():
    '''
    get default settings
    @return: the default settings, a dict type
    '''
    return KEYBOARD_DEFAULT_SETTINGS


#####################
# layout set
def xkb_get_default_group():
    '''
    get the desktop window default-group layout
    @return: the default group, an int num
    '''
    return XKB_DESKTOP_SETTINGS.get_int("default-group")


def xkb_set_default_group(default_group):
    '''
    set the desktop window default-group layout
    @param default_group: the default group, an int type
    '''
    return XKB_DESKTOP_SETTINGS.set_int("default-group", int(default_group))


def xkb_get_group_per_window():
    '''
    get if per window has diff layout
    @return: True if per window has diff layout, otherwise False
    '''
    return XKB_DESKTOP_SETTINGS.get_boolean("group-per-window")


def xkb_set_group_per_window(value):
    '''
    set the desktop per window has diff layout
    @param value: a bool type
    '''
    return XKB_DESKTOP_SETTINGS.set_boolean("group-per-window", value)


def xkb_get_layouts():
    '''
    get keyboard layouts
    @return: a list contain some string of layouts.
    '''
    return XKB_KEYBOARS_SETTINGS.get_strv("layouts")


def xkb_set_layouts(value):
    '''
    set keyboard layouts
    @param value: a list contain some string of layouts
    '''
    return XKB_KEYBOARS_SETTINGS.set_strv("layouts", value)


def xkb_get_options():
    '''
    get keyboard options
    @return: a list contain some string of options.
    '''
    return XKB_KEYBOARS_SETTINGS.get_strv("options")


def xkb_set_options(value):
    '''
    set keyboard options
    @param value: a list contain some string of options
    '''
    return XKB_KEYBOARS_SETTINGS.set_strv("options", value)


def xkb_set_to_default():
    '''set all value to default'''
    XKB_KEYBOARS_SETTINGS.reset("layouts")
    #XKB_KEYBOARS_SETTINGS.reset("model")
    #XKB_KEYBOARS_SETTINGS.reset("options")


def xkb_get_default_settings():
    '''
    get default settings
    @return: the default settings, a dict type
    '''
    return XKB_KEYBOARD_DEFAULT_SETTINGS


#####################
# shortcuts set
def shortcuts_wm_get(key):
    '''
    get the wm keybindings
    @param key: the keybing's name, a string type
    @return: a list contain some string of keymap.
    '''
    return WM_SHORTCUTS_SETTINGS.get_strv(key)


def shortcuts_wm_set(key, value):
    '''
    set the wm keybindings
    @param key: the keybinding's name, a string type
    @param value: a list contain some string of keymap
    '''
    return WM_SHORTCUTS_SETTINGS.set_strv(key, value)


def shortcuts_media_get(key):
    '''
    get the media keybindings
    @param key: the keybinding's name, a string type
    @return: a string contain the the keymap.
    '''
    return SHORTCUTS_SETTINGS.get_string(key)


def shortcuts_media_set(key, value):
    '''
    set the wm keybindings
    @param key: the keybinding's name, a string type
    @param value: a string contain the keymap
    '''
    return SHORTCUTS_SETTINGS.set_string(key, value)


def shortcuts_custom_get(key):
    '''
    get the custom keybindings
    @param key: the keybinding's name, a string type
    @return: a 3-tuple contain action, binding and name
    '''
    client = GCONF_CLIENT
    base_dir = '/desktop/gnome/keybindings'
    action = client.get("%s/%s/action" %(base_dir, key)).get_string()
    binding = client.get("%s/%s/binding" %(base_dir, key)).get_string()
    name = client.get("%s/%s/name" %(base_dir, key)).get_string()
    return (action, binding, name)

def shortcuts_custom_set(key, key_binding):
    '''
    set the custom keybindings
    @param key: the keybinding's name, a string type
    @param key_binding: a 3-tuple contain action, binding and name
    '''
    client = GCONF_CLIENT
    base_dir = '/desktop/gnome/keybindings'
    v = gconf.Value(gconf.VALUE_STRING)
    v.set_string(key_binding[0])
    client.set("%s/%s/action" % (base_dir, key), v)
    v.set_string(key_binding[1])
    client.set("%s/%s/binding" % (base_dir, key), v)
    v.set_string(key_binding[2])
    client.set("%s/%s/name" % (base_dir, key), v)

def is_has_touchpad():
    devices = gdk.devices_list()
    for d in devices:
        if "touchpad" in d.get_name().lower():
            return True
    return False
