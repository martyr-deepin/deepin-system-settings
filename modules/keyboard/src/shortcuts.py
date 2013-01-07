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
# along with this program.  If not, see <http://www.gnu.org/licenses}.

from nls import _
from treeitem import ShortcutItem
from keybind_list import media_shortcuts_group_dict, wm_shortcuts_group_dict

def get_shortcuts_wm_shortcut_item(gsettings):
    '''
    @param gsettings: a GSettings object
    @return: a dict contain ShortcutItem
    '''
    keys_list = gsettings.list_keys()
    item_dict = {}
    for group in wm_shortcuts_group_dict:
        item_dict[group] = []
        for key in wm_shortcuts_group_dict[group]:
            if key['name'] in keys_list:
                key_name = gsettings.get_strv(key['name'])
                if not key_name:
                    key_name = _('disable')
                else:
                    key_name = key_name[0]
                item = ShortcutItem(key['description'], key_name, key['name'])
                item.set_accel_buffer_from_accel(key_name)
                accel_label = item.accel_buffer.get_accel_label()
                if accel_label:
                    item.keyname = accel_label
                item.set_data('setting-type', 'gsettings')
                item.set_data('setting-data-type', 'strv')
                item.set_data('settings', gsettings)
                item_dict[group].append(item)
    return item_dict

def get_shortcuts_media_shortcut_item(gsettings):
    '''
    @param gsettings: a GSettings object
    @return: a dict contain ShortcutItem
    '''
    keys_list = gsettings.list_keys()
    item_dict = {}
    for group in media_shortcuts_group_dict:
        item_dict[group] = []
        for key in media_shortcuts_group_dict[group]:
            if key['name'] in keys_list:
                key_name = gsettings.get_string(key['name'])
                if not key_name:
                    key_name = _('disable')
                item = ShortcutItem(key['description'], key_name, key['name'])
                item.set_accel_buffer_from_accel(key_name)
                accel_label = item.accel_buffer.get_accel_label()
                if accel_label:
                    item.keyname = accel_label
                item.set_data('setting-type', 'gsettings')
                item.set_data('setting-data-type', 'string')
                item.set_data('settings', gsettings)
                item_dict[group].append(item)
    return item_dict

def get_shortcuts_custom_shortcut_item(client):
    '''
    @param client: a GConf Client type
    @return: a list contain ShortcutItem
    '''
    base_dir = '/desktop/gnome/keybindings'
    dir_list = client.all_dirs(base_dir)
    item_list = []
    for dirs in dir_list:
        name = client.get("%s/name" %(dirs))
        if not name:
            continue
        name = name.get_string()
        action = client.get("%s/action" %(dirs))
        if not action:
            continue
        action = action.get_string()
        binding = client.get("%s/binding" %(dirs))
        if binding:
            binding = binding.get_string()
        if not binding:
            binding = _("disable")
        item = ShortcutItem(name, binding, action)
        item.set_accel_buffer_from_accel(binding)
        accel_label = item.accel_buffer.get_accel_label()
        if accel_label:
            item.keyname = accel_label
        item.set_data('gconf-dir', dirs)
        item.set_data('setting-type', 'gconf')
        item.set_data('settings', client)
        item_list.append(item)
    return item_list
