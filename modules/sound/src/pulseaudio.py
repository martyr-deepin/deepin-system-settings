#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
#             Long Changjin <admin@longchangjin.cn>
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
import subprocess
import dbus
import gobject
import traceback
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
'''
TODO: open the thread-safe switch
'''
gobject.threads_init()
dbus.mainloop.glib.threads_init()

client_bus = None

def connect_bus():
    if 'PULSE_DBUS_SERVER' in os.environ:
        address = os.environ['PULSE_DBUS_SERVER']
    else:
        bus = dbus.SessionBus()

        monitor_object = bus.get_object("org.freedesktop.DBus", "/org/freedesktop/DBus")
        monitor_interface = dbus.Interface(monitor_object, "org.freedesktop.DBus")

        i = 0
        while i < 5:
            if "org.PulseAudio1" not in monitor_interface.ListNames():
                i = i + 1
                try:
                    while int(os.popen("ps -ef |grep pulseaudio | wc -l").read().strip()) > 1:
                        command = "pulseaudio --kill"
                        subprocess.Popen("nohup %s > /dev/null 2>&1" % command, shell=True)
    
                    command = "pulseaudio --start"
                    subprocess.Popen("nohup %s > /dev/null 2>&1" % command, shell=True)
                except:
                    print "StartServiceByName:org.PulseAudio1 Failed"
                    continue
            else:
                print "time tried to connect pulseaudio dbus:%s" % i
                break
    
        server_lookup = bus.get_object("org.PulseAudio1", "/org/pulseaudio/server_lookup1")
        prop_interface = dbus.Interface(server_lookup, "org.freedesktop.DBus.Properties")
        address = prop_interface.Get("org.PulseAudio.ServerLookup1", "Address")
        try:    
            global client_bus
            client_bus = dbus.connection.Connection(address)
        except:
            client_bus = None
            print "return pulseaudio client bus failed"

connect_bus()

class BusBase(gobject.GObject):
    
    def __init__(self, path, interface, bus = client_bus):

        gobject.GObject.__init__(self)
        self.object_path = path
        self.object_interface = interface
        self.bus = bus
        try:
            self.dbus_proxy = self.bus.get_object(object_path = self.object_path)
            self.dbus_interface = dbus.Interface(self.dbus_proxy, self.object_interface)
        #except dbus.exceptions.DBusException:
        except :
            #traceback.print_exc()
            print "dbus connect error"

    # def init_dbus_properties(self):        
    #     try:
    #         self.properties_interface = dbus.Interface(self.dbus_proxy, "org.freedesktop.DBus.Properties" )
    #     except dbus.exceptions.DBusException:
    #         traceback.print_exc()

    #     if self.properties_interface:
    #         try:
    #             self.properties = self.properties_interface.GetAll(self.object_interface)
    #         except:
    #             print "get properties failed"
    #             traceback.print_exc()

    def get_property(self, prop_name):
        try:
            self.property_interface = dbus.Interface(self.dbus_proxy, "org.freedesktop.DBus.Properties")
        except dbus.exceptions.DBusException:
            print "get property_interface failed", prop_name
            #traceback.print_exc()
            return None
   
        if self.property_interface:    
            try:
                return self.property_interface.Get(self.object_interface, prop_name)
            except:
                print "get properties failed (%s)" % prop_name
                #traceback.print_exc()
                return None
        else:
            return None

    def set_property(self, prop_name, prop_value):
        try:
            self.property_interface = dbus.Interface(self.dbus_proxy, "org.freedesktop.DBus.Properties")
        except dbus.exceptions.DBusException:
            print "set property_interface failed", prop_name
            #traceback.print_exc()
            return None
   
        if self.property_interface:    
            try:
                return self.property_interface.Set(self.object_interface, prop_name, prop_value)
            except:
                print "set properties failed", prop_name, prop_value
                #traceback.print_exc()

    def dbus_method(self, method_name, *args, **kwargs):
        try:
            return apply(getattr(self.dbus_interface, method_name), args, kwargs)
        except dbus.exceptions.DBusException:
            print "call dbus method failed:%s\n" % method_name
            traceback.print_exc()

    def call_async(self, method_name, *args, **kwargs):
        try:
            return apply(getattr(self.dbus_interface, method_name), args, kwargs)
        except dbus.exceptions.DBusException:
            print "call dbus method failed:%s\n" % method_name
            traceback.print_exc()

if __name__ == "__main__":

    def run():
        core = connect_bus().get_object(object_path="/org/pulseaudio/core1")
        source_paths = core.Get("org.PulseAudio.Core1", "Sources", dbus_interface="org.freedesktop.DBus.Properties")
        mainloop = gobject.MainLoop()
        print source_paths
    
        gobject.timeout_add(1000, lambda : mainloop.quit())
    
        mainloop.run()
    
    for i in range(10000):
        run()
        
