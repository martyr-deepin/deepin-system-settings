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
dbus.mainloop.glib.threads_init()

from xml.dom import minidom
import traceback
import gobject
# import re
from nm_utils import TypeConvert, valid_object_path, valid_object_interface, is_dbus_name_exists
from nm_utils import InvalidObjectPath , InvalidObjectInterface, InvalidService
# from servicemanager import nm_bus
from servicemanager import servicemanager

# name_re = re.compile("[0-9a-zA-Z-]*")
# dbus_loop = gobject.MainLoop()
nm_bus = servicemanager.get_nm_bus()
    
class NMObject(gobject.GObject):
    '''NMObject'''

    def __init__(self, object_path, object_interface, service_name = "org.freedesktop.NetworkManager", bus = nm_bus):
        gobject.GObject.__init__(self)

        self.bus = bus
        self.service_name = service_name

        if not is_dbus_name_exists(service_name, False):
            raise InvalidService(service_name)

        if valid_object_path(object_path):
            self.object_path = object_path
        else:
            raise InvalidObjectPath(object_path)

        if valid_object_interface(object_interface):
            self.object_interface = object_interface
        else:
            raise InvalidObjectInterface(object_interface)

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
        except dbus.exceptions.UnknownMethodException, e:    
            print "unknown dbus method"
            print method_name
            print e
        except dbus.exceptions.DBusException, e:
            print "call dbus method failed:\n"
            print method_name
            print args
            print kwargs
            print e
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
            self.properties_interface.Set(self.object_interface, prop_name, prop_value)
            self.properties[prop_name] = prop_value
        except dbus.exceptions.DBusException:
            print "set property failed"
            traceback.print_exc()

    def introspect(self):
        try:
            return self.introspect_interface.Introspect()
        except dbus.exceptions.DBusException:
            print "Introspect Failed"
            traceback.print_exc()
            return None

    def init_properties_access(self):  
        prop_access_dict = {}
        if not self.introspect():
            print "introspect failed to init_properties_access"
            return None
        try:
            xmldoc = minidom.parseString(str(self.introspect())) 
            root = xmldoc.documentElement
            for node in root.getElementsByTagName("property"):
                prop_access_dict[node.getAttribute("name")] = node.getAttribute("access")
        except:
            print "init properties access failed"
            traceback.print_exc()

        return prop_access_dict    

    def check_property_can_write(self, prop_name):
        if not self.properties_access:
            self.properties_access = self.init_properties_access()

        return "write" in self.properties_access[prop_name]

if __name__ == "__main__":
    pass
