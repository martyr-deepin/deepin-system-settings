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
        #action = client.get("%s/action" %(dirs)).get_string()
        binding = client.get("%s/binding" %(dirs)).get_string()
        #if not binding:
            #binding = _("disable")
        name = client.get("%s/name" %(dirs)).get_string()
        item = AccelEntry(binding, check_shortcut_conflict)
        item.settings_description = name
        item.settings_key = dirs
        item.settings_obj = client
        item.settings_type = item.TYPE_GCONF
        item.settings_value_type = item.TYPE_STRING
        item_list.append(item)
    ACCEL_ENTRY_LIST += item_list
    return item_list
