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
import sys
sys.path.append("../")

import dbus
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default = True)

from xml.dom import minidom
import traceback
import gobject
import re
from nm_utils import TypeConvert

name_re = re.compile("[0-9a-zA-Z-]*")
dbus_loop = gobject.MainLoop()
nm_bus = dbus.SystemBus()

class NMObject(gobject.GObject):
    '''NMObject'''
    def __init__(self, object_path, object_interface, service_name = "org.freedesktop.NetworkManager", bus = nm_bus):
        gobject.GObject.__init__(self)

        self.bus = bus

        if self.valid_object_path(object_path):
            self.object_path = object_path
        else:
            print "invalid object path :%s" % object_path
            raise dbus.exceptions.DBusException

        if self.valid_object_interface(object_interface):
            self.object_interface = object_interface
        else:
            print "invalid object path :%s" % object_interface
            raise dbus.exceptions.DBusException

        try:
            self.dbus_proxy = self.bus.get_object (service_name, object_path)
            self.dbus_interface = dbus.Interface (self.dbus_proxy, object_interface)
        except dbus.exceptions.DBusException:
            traceback.print_exc()

    def init_nmobject_with_properties(self):  
        try:
            self.properties_interface = dbus.Interface (self.dbus_proxy, "org.freedesktop.DBus.Properties" )
            self.introspect_interface = dbus.Interface (self.dbus_proxy, "org.freedesktop.DBus.Introspectable")
        except dbus.exceptions.DBusException:
            traceback.print_exc()

        self.properties = self.init_properties()
        self.properties_access = {}

    def dbus_method(self, method_name, *args, **kwargs):
        try:
            # return TypeConvert.dbus2py(apply(getattr(self.dbus_interface, method_name), args, kwargs))
            return apply(getattr(self.dbus_interface, method_name), args, kwargs)

        except dbus.exceptions.DBusException:
            traceback.print_exc()

    def init_properties(self): 
        try:
            return TypeConvert.dbus2py(self.properties_interface.GetAll(self.object_interface))
        except dbus.exceptions.DBusException:
            prop = {}
            for key in self.prop_list:
                prop[key] = ""
            return prop

    def update_properties(self):
        self.clear_properties ()
        self.properties = self.init_properties()

    def clear_properties(self):
        self.properties.clear()
        
    def get_property(self, prop_name):
        return self.properties[prop_name]

    def set_property(self, prop_name, prop_value):
        if not self.check_property_can_write(prop_name):
            print "sorry, cann't write to the prop:%s" % prop_name
        try:
            self.properties_interface.set(self.dbus_interface, prop_name, prop_value)
            self.properties[prop_name] = prop_value
        except dbus.exceptions.DBusException:
            traceback.print_exc()

    def introspect(self):
        try:
            return self.introspect_interface.Introspect()
        except dbus.exceptions.DBusException:
            traceback.print_exc()

    def init_properties_access(self):  
        prop_access_dict = {}
        xmldoc = minidom.parseString(str(self.introspect())) 
        root = xmldoc.documentElement
        for node in root.getElementsByTagName("property"):
            prop_access_dict[node.getAttribute("name")] = node.getAttribute("access")

        return prop_access_dict    

    def check_property_can_write(self, prop_name):
        if not self.properties_access:
            self.properties_access = self.init_properties_access()

        return "write" in self.properties_access[prop_name]

    def valid_object_path(self, object_path):
        if not isinstance(object_path, str):
            return False
        if not object_path.startswith("/"):
            return False

        return all(map(lambda x:name_re.match(x), object_path.split(".")))    

    def valid_object_interface(self, object_interface):
        if not isinstance(object_interface, str):
            return False
        if object_interface.startswith("."):
            return False
        if len(object_interface.split(".")) < 2:
            return False

        for item in object_interface.split("."):
            if len(item) == 0:
                return False
            if item[0].isdigit():
                return False

        return all(map(lambda x:name_re.match(x), object_interface.split(".")))    




