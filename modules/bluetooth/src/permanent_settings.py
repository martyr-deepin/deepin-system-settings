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

BLUETOOTH_CONFIG_PATH = os.path.expanduser("~/.config/deepin-system-settings/bluetooth/settings.cfg")

class PermanentSettings(object):
    def __init__(self):
        try:
            self.cfg_parser = ConfigParser()
            if not os.path.exists(BLUETOOTH_CONFIG_PATH):
                os.makedirs(os.path.dirname(BLUETOOTH_CONFIG_PATH))
                with open(BLUETOOTH_CONFIG_PATH, "w") as cfg_fileobj:
                    self.cfg_parser.add_section("General")
                    self.cfg_parser.set("General", "Powered", "true")
                    self.cfg_parser.set("General", "Disable-Icon-When-Close", "false")
                    self.cfg_parser.write(cfg_fileobj)
            else:
                with open(BLUETOOTH_CONFIG_PATH) as cfg_fileobj:
                    self.cfg_parser.readfp(cfg_fileobj)
        except Exception, e:
            print e

    def set_powered(self, value):
        value = "true" if value else "false"
        with open(BLUETOOTH_CONFIG_PATH, "w") as cfg_fileobj:
            self.cfg_parser.set("General", "Powered", value)
            self.cfg_parser.write(cfg_fileobj)
            
    def get_powered(self):
        return self.cfg_parser.getboolean("General", "Powered")
    
    def set_disable_icon_when_close(self, value):
        with open(BLUETOOTH_CONFIG_PATH, "w") as cfg_fileobj:
            self.cfg_parser.set("General", "Disable-Icon-When-Close", str(value))
            self.cfg_parser.write(cfg_fileobj)
            
    def get_disable_icon_when_close(self):
        return self.cfg_parser.getboolean("General", "Disable-Icon-When-Close")
            
permanent_settings = PermanentSettings()
