#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang YaoHua
# 
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
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
from ConfigParser import ConfigParser
parser = ConfigParser()

CFG_FILE = os.path.expanduser("~/.config/deepin-system-settings/mount_media/mount_media.ini")

if not os.path.exists(CFG_FILE):
    os.makedirs(os.path.dirname(CFG_FILE))
    with open(CFG_FILE, "w") as cfg:
        parser.add_section("mount_media")
        parser.set("mount_media", "auto_mount", "false")
        parser.write(cfg)
else:
    with open(CFG_FILE) as cfg:
        parser.readfp(cfg)
        
def get_auto_mount():
    return parser.getboolean("mount_media", "auto_mount")

def set_auto_mount(auto_mount):
    if auto_mount:
        with open(CFG_FILE, "w") as cfg:
            parser.set("mount_media", "auto_mount", "true")
            parser.write(cfg)
    else:
        with open(CFG_FILE, "w") as cfg:
            parser.set("mount_media", "auto_mount", "false")
            parser.write(cfg)
