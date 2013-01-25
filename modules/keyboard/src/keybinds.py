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

from nls import _
from keybind_list import media_shortcuts_group_dict, wm_shortcuts_group_dict
from accel_entry import AccelEntry

ACCEL_ENTRY_LIST = []

def check_shortcut_conflict(origin_entry, tmp_accel_buf):
    global ACCEL_ENTRY_LIST
    for accel in ACCEL_ENTRY_LIST:
        if accel != origin_entry and tmp_accel_buf == accel.accel_buffer:
            return accel
    return None

def get_shortcuts_shortcut_entry(gsettings, group_dict, value_type):
    '''
    @param gsettings: a GSettings object
    @return: a dict contain ShortcutItem
    '''
    keys_list = gsettings.list_keys()
    item_dict = {}
    global ACCEL_ENTRY_LIST
    for group in group_dict:
        item_dict[group] = []
        for key in group_dict[group]:
            if key['name'] in keys_list:
                if value_type == AccelEntry.TYPE_STRV:
                    key_name = gsettings.get_strv(key['name'])
                    if key_name:
                        key_name = key_name[0]
                    else:
                        key_name = ""
                else:
                    key_name = gsettings.get_string(key['name'])
                #if not key_name:
                    #key_name = _('disable')
                item = AccelEntry(key_name, check_shortcut_conflict)
                item.settings_description = key['description']
                item.settings_key = key['name']
                item.settings_obj = gsettings
                item.settings_type = item.TYPE_GSETTINGS
                item.settings_value_type = value_type
                item_dict[group].append(item)
        ACCEL_ENTRY_LIST += item_dict[group]
    return item_dict

def get_shortcuts_wm_shortcut_entry(gsettings):
    return get_shortcuts_shortcut_entry(gsettings, wm_shortcuts_group_dict, AccelEntry.TYPE_STRV)

def get_shortcuts_media_shortcut_entry(gsettings):
    return get_shortcuts_shortcut_entry(gsettings, media_shortcuts_group_dict, AccelEntry.TYPE_STRING)

def parse_dp_shortcut_string(accel_name):
    '''
    @param accel_name: a accel and command str
    @return: a 2-tuple container command name and Accel
    '''
    key_name = accel_name.split(';', 1)
    if len(key_name) >=2:
        command_name = key_name[0]
        accelname = key_name[1]
    else:
        command_name = ""
        accelname = ""
    return (command_name, accelname)

def get_shortcuts_dp_shortcut_entry(gsettings, accel_entry_list):
    '''
    get org.gnome.settings-daemon.plugins.keybindings keybindings 
    @param accel_entry_list: a AccelEntry list that add this item
    '''
    keys_list = gsettings.list_keys()
    print keys_list
    if "key1" in keys_list:
        key1_name = parse_dp_shortcut_string(gsettings.get_string("key1"))
        item = AccelEntry(key1_name[1], check_shortcut_conflict)
        item.settings_description = _("Launcher")
        item.settings_key = "key1"
        item.settings_obj = gsettings
        item.settings_type = item.TYPE_DP_GSETTINGS
        #item.settings_value_type = key1_name[0]
        item.settings_value_type = "launcher"
        accel_entry_list.append(item)
    if "key2" in keys_list:
        key2_name = parse_dp_shortcut_string(gsettings.get_string("key2"))
        item = AccelEntry(key2_name[1], check_shortcut_conflict)
        item.settings_description = _("Terminal")
        item.settings_key = "key2"
        item.settings_obj = gsettings
        item.settings_type = item.TYPE_DP_GSETTINGS
        #item.settings_value_type = key2_name[0]
        item.settings_value_type = "gnome-terminal"
        accel_entry_list.append(item)
    if "key3" in keys_list:
        key3_name = parse_dp_shortcut_string(gsettings.get_string("key3"))
        item = AccelEntry(key3_name[1], check_shortcut_conflict)
        item.settings_description = _("Lock screen")
        item.settings_key = "key3"
        item.settings_obj = gsettings
        item.settings_type = item.TYPE_DP_GSETTINGS
        item.settings_value_type = "lock"
        accel_entry_list.append(item)


def get_shortcuts_custom_shortcut_entry(client):
    '''
    @param client: a GConf Client type
    @return: a list contain ShortcutItem
    '''
    base_dir = '/desktop/gnome/keybindings'
    dir_list = client.all_dirs(base_dir)
    item_list = []
    global ACCEL_ENTRY_LIST
    for dirs in dir_list:
        name = client.get("%s/name" %(dirs))
        if not name:
            continue
        name = name.get_string()
        binding = client.get("%s/binding" %(dirs))
        if binding:
            binding = binding.get_string()
        else:
            binding = ""
        item = AccelEntry(binding, check_shortcut_conflict)
        item.settings_description = name
        item.settings_key = dirs
        item.settings_obj = client
        item.settings_type = item.TYPE_GCONF
        item.settings_value_type = item.TYPE_STRING
        item_list.append(item)
    ACCEL_ENTRY_LIST += item_list
    return item_list
