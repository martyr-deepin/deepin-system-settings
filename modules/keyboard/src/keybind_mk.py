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
from keybind_all import shortcuts_group_dict, TYPE_WM, TYPE_MEDIA, TYPE_COMPIZ, TYPE_DP
from accel_entry import AccelEntry
import settings

ACCEL_ENTRY_LIST = []

def check_shortcut_conflict(origin_entry, tmp_accel_buf):
    global ACCEL_ENTRY_LIST
    for accel in ACCEL_ENTRY_LIST:
        if accel != origin_entry and tmp_accel_buf == accel.accel_buffer:
            return accel
    return None

def get_all_shortcuts_entry(gst_list):
    global ACCEL_ENTRY_LIST
    item_dict = {}
    keys_list = {}
    keys_list[TYPE_WM] = gst_list[TYPE_WM].list_keys()
    keys_list[TYPE_MEDIA] = gst_list[TYPE_MEDIA].list_keys()
    keys_list[TYPE_DP] = gst_list[TYPE_DP].list_keys()
    keys_list[TYPE_COMPIZ] = ["next-key", "prev-key"]
    for group in shortcuts_group_dict:
        item_dict[group] = []
        for key in shortcuts_group_dict[group]:
            if key['type'] in keys_list and key['name'] in keys_list[key['type']]:
                if key['type'] == TYPE_DP:
                    item = get_shortcuts_dp_shortcut_entry(gst_list[TYPE_DP], key)
                elif key['type'] == TYPE_COMPIZ:
                    item = get_shortcuts_compiz_shortcut_entry(gst_list[TYPE_COMPIZ], key)
                    if not item:
                        continue
                else:
                    if key['value-type'] == AccelEntry.TYPE_STRV:
                        key_name = gst_list[key['type']].get_strv(key['name'])
                        if key_name:
                            key_name = key_name[0]
                        else:
                            key_name = ""
                    else:
                        key_name = gst_list[key['type']].get_string(key['name'])
                    item = AccelEntry(key_name, check_shortcut_conflict)
                    item.settings_description = key['description']
                    item.settings_key = key['name']
                    item.settings_obj = gst_list[key['type']]
                    item.settings_type = item.TYPE_GSETTINGS
                    item.settings_value_type = key['value-type']
                item_dict[group].append(item)
        ACCEL_ENTRY_LIST += item_dict[group]
    return item_dict

######################################
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

def get_shortcuts_dp_shortcut_entry(gsettings, key_dict):
    '''
    get org.gnome.settings-daemon.plugins.keybindings keybindings 
    @param accel_entry_list: a AccelEntry list that add this item
    '''
    key1_name = parse_dp_shortcut_string(gsettings.get_string(key_dict['name']))
    item = AccelEntry(key1_name[1], check_shortcut_conflict)
    item.settings_description = key_dict['description']
    item.settings_key = key_dict['name']
    item.settings_obj = gsettings
    item.settings_type = item.TYPE_DP_GSETTINGS
    item.settings_value_type = key_dict['command']
    return item

def get_shortcuts_compiz_shortcut_entry(gsettings, key_dict):
    key_name = settings.shortcuts_compiz_get(key_dict['name'])
    item = AccelEntry(key_name, check_shortcut_conflict)
    item.settings_description = key_dict['description']
    item.settings_key = key_dict['name']
    item.settings_obj = gsettings
    item.settings_type = item.TYPE_CMP_GSETTINGS
    return item

def get_shortcuts_custom_shortcut_entry(client, del_callback=None):
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
        item = AccelEntry(binding, check_shortcut_conflict, can_del=True)
        if del_callback:
            item.connect("accel-del", del_callback)
        item.settings_description = name
        item.settings_key = dirs
        item.settings_obj = client
        item.settings_type = item.TYPE_GCONF
        item.settings_value_type = item.TYPE_STRING
        item_list.append(item)
    ACCEL_ENTRY_LIST += item_list
    return item_list
