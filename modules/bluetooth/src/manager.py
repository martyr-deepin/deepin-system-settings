#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
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

import gobject
from utils import BusBase

class Manager(BusBase):

    __gsignals__  = {
        "adapter-added":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "adapter-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "default-adapter-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "property-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, gobject.TYPE_PYOBJECT))
            }

    def __init__(self):
        BusBase.__init__(self, path = "/", interface = "org.bluez.Manager")

        self.bus.add_signal_receiver(self.adapter_added_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "AdapterAdded")

        self.bus.add_signal_receiver(self.adapter_removed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "AdapterRemoved")

        self.bus.add_signal_receiver(self.default_adapter_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "DefaultAdapterChanged")

        self.bus.add_signal_receiver(self.property_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "PropertyChanged")

    def get_default_adapter(self):
        return str(self.dbus_method("DefaultAdapter"))

    def find_adapter(self, dev_id):
        return str(self.dbus_method("FindAdapter", dev_id))
 
    def get_properties(self):
        return dict(self.dbus_method("GetProperties"))

    def list_adapters(self):
        adapters = self.dbus_method("ListAdapters")
        if adapters:
            return map(lambda x:str(x), adapters)
        else:
            return []

    def adapter_added_cb(self, path):
        self.emit("adapter-added", path)

    def adapter_removed_cb(self, path):
        self.emit("adapter-removed", path)

    def default_adapter_changed_cb(self, path):
        self.emit("default-adapter-changed", path)

    def property_changed_cb(self, key, value):
        self.emit("property-changed", key, value)

if __name__ == "__main__":
    manager = Manager()
    print manager.get_properties()
    print manager.list_adapters()
