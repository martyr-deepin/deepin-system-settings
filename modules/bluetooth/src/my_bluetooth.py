#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Deepin, Inc.
#               2013 Zhai Xiang
# 
# Author:     Zhai Xiang <zhaixiang@linuxdeepin.com>
# Maintainer: Zhai Xiang <zhaixiang@linuxdeepin.com>
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

from bt.manager import Manager                                                  
from bt.adapter import Adapter                                                  
from bt.device import Device                                                    
from bt.utils import bluetooth_class_to_type

class MyBluetooth():
    def __init__(self, 
                 adapter_removed_cb=None, 
                 default_adapter_changed_cb=None, 
                 device_found_cb=None):
        self.__adapter_removed_cb = adapter_removed_cb
        self.__default_adapter_changed_cb = default_adapter_changed_cb
        
        self.manager = Manager()
        if self.__adapter_removed_cb:
            self.manager.connect("adapter-removed", self.__adapter_removed)
        if self.__default_adapter_changed_cb:
            self.manager.connect("default-adapter-changed", self.__default_adapter_changed)
        self.adapter = None
        self.default_adapter = self.manager.get_default_adapter()
        
        if self.default_adapter != "None":
            self.adapter = Adapter(self.default_adapter)
            self.adapter.set_powered(True)
            self.adapter.set_discoverable(True)
            self.adapter.set_pairable(True)
            if device_found_cb:
                self.adapter.connect("device-found", device_found_cb)

    def get_devices(self):
        ret = []
        
        if self.adapter == None:
            return ret

        devices = self.adapter.get_devices()
        i = 0
        ret = []
        
        while i < len(devices):
            ret.append(Device(devices[i]))
            i += 1

        return ret

    def __adapter_removed(self, manager, path):
        if self.__adapter_removed_cb != None:
            self.__adapter_removed_cb()

    def __default_adapter_changed(self, manager, path):
        if self.__default_adapter_changed_cb != None:
            self.__default_adapter_changed_cb()
