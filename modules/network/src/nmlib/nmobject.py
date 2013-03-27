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
from nm_utils import TypeConvert, valid_object_path, valid_object_interface, is_dbus_name_exists
from nm_utils import InvalidObjectPath , InvalidObjectInterface, InvalidService
from servicemanager import servicemanager

#nm_bus = servicemanager.get_nm_bus()
    
class NMObject(gobject.GObject):
    '''NMObject'''

    def __init__(self, object_path, object_interface, service_name = "org.freedesktop.NetworkManager", bus = None):
        gobject.GObject.__init__(self)

        if bus:
            self.bus = bus
        else:
            self.bus = self.get_system_bus() 
        self.service_name = service_name

        #if not is_dbus_name_exists(service_name, False):
        #    raise InvalidService(service_name)

        if valid_object_path(object_path):
            self.object_path = object_path
        else:
            raise InvalidObjectPath(object_path)

        if valid_object_interface(object_interface):
            self.object_interface = object_interface
        else:
            raise InvalidObjectInterface(object_interface)

        self.dbus_proxy = self.get_dbus_proxy(service_name, object_path)
        self.dbus_interface = self.get_dbus_interface(service_name, object_path, object_interface)
        self.properties_interface = None
        self.introspect_interface = None

    def get_system_bus(self):
        try:
            return servicemanager.get_nm_bus()
        except:
            print "get system bus failed\n"
            #traceback.print_exc()
            return None

    def get_dbus_proxy(self, service_name, object_path):
        try:
            if is_dbus_name_exists(service_name, False):
                return self.bus.get_object(service_name, object_path)
            else:
                return None
        except:
            print "get dbus proxy failed\n"
            #traceback.print_exc()
            return None

    def get_dbus_interface(self, service_name,  object_path, object_interface):
        if is_dbus_name_exists(service_name, False):
            if not self.dbus_proxy:
                self.dbus_proxy = self.get_dbus_proxy(service_name, object_path)
            try:
                return dbus.Interface(self.dbus_proxy, object_interface);
            except:
                print "get dbus interface failed\n"
                #traceback.print_exc()
                return None
        else:
            return None

    def get_properties_interface(self, service_name, object_path):
        if is_dbus_name_exists(service_name, False):
            if not self.dbus_proxy:
                self.dbus_proxy = self.get_dbus_proxy(service_name, object_path)
            try:
                return dbus.Interface(self.dbus_proxy, "org.freedesktop.DBus.Properties")
            except:
                print "get properties interface failed\n"
                #traceback.print_exc()
                return None
        else:
            return None

    def get_introspect_interface(self, service_name, object_path):
        if is_dbus_name_exists(service_name, False):
            if not self.dbus_proxy:
                self.dbus_proxy = self.get_dbus_proxy(service_name, object_path)
            try:
                return dbus.Interface(self.dbus_proxy, "org.freedesktop.DBus.Introspectable")
            except:
                print "get introspect interface failed\n"
                #traceback.print_exc()
                return None
        else:
            return None

    def init_nmobject_with_properties(self):  
        if is_dbus_name_exists(self.service_name, False):
            if not self.dbus_proxy:
                self.dbus_proxy = self.get_dbus_proxy(self.service_name, self.object_path)

            if not self.properties_interface:
                self.properties_interface = self.get_properties_interface(self.service_name, self.object_path)

            if not self.introspect_interface:
                self.introspect_interface = self.get_introspect_interface(self.service_name, self.object_path)
                
            self.properties = self.init_properties()
            self.properties_access = {}
        else:
            pass

    def dbus_method(self, method_name, *args, **kwargs):
        if is_dbus_name_exists(self.service_name, False):
            if not self.dbus_interface:
                self.dbus_interface = self.get_dbus_interface(self.service_name, self.object_path, self.object_interface)
            try:
                return apply(getattr(self.dbus_interface, method_name), args, kwargs)
            except:
                print "call dbus_method failed\n"
                print self, method_name
                traceback.print_exc()
        else:
            pass

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
