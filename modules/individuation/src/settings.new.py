#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012~2013 Deepin, Inc.
#               2012~2013 Kaisheng Ye
#
# Author:     Kaisheng Ye <kaisheng.ye@gmail.com>
# Maintainer: Kaisheng Ye <kaisheng.ye@gmail.com>
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

import os
from xdg_support import get_config_dir

from deepin_utils.config import Config
from deepin_utils.file import touch_file

CONFIG_INFO_PATH = os.path.join(get_config_dir(), "settings.ini")

def get_config_info_config():
    config_info_config = Config(CONFIG_INFO_PATH)
    if os.path.exists(CONFIG_INFO_PATH):
        config_info_config.load()
    else:
        touch_file(CONFIG_INFO_PATH)
        config_info_config.load()
    return config_info_config

def get_config_info(section, key):
    config = get_config_info_config()
    if config.has_option(section, key):
        return config.get(section, key)
    else:
        return None

def set_config_info(section, key, value):
    config = get_config_info_config()
    config.set(section, key, value)
    config.write()

def get_favorites():
    return get_config_info("settings", "favorites")

def set_favorites(keys):
    set_config_info("settings", "favorites", keys)

def get_system_deletes():
    return get_config_info("settings", "system_deletes")

def set_system_deletes(keys):
    set_config_info("settings", "system_deletes", keys)
