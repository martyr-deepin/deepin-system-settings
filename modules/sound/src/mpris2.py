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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import dbus
import dbus.mainloop.glib
import gobject
import xml.etree.ElementTree as ET

class Mpris2(object):
    def __init__(self):
        super(Mpris2, self).__init__()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
     
        self.bus = dbus.SessionBus()
        self.bus.add_signal_receiver(self.name_owner_changed_cb, dbus_interface='org.freedesktop.DBus', signal_name='NameOwnerChanged')
        self.bus_path = self.bus.get_object('org.freedesktop.DBus', '/')
        self.get_pid = self.bus_path.get_dbus_method('GetConnectionUnixProcessID', 'org.freedesktop.DBus')
        self.process_list = []
        
    def parse_xml(self, data):
        root = ET.fromstring(data)
        mpris = None
        mpris_method = []
        mpris_signal = []
        mpris_property = []
        for child in root:
            if child.tag == "interface" and child.attrib['name'] == 'org.mpris.MediaPlayer2.Player':
                mpris = child
                break

        if mpris is not None:
            for i in mpris:
                if i.tag == "method":
                    mpris_method.append(i.attrib['name'])
                if i.tag == "signal":
                    mpris_signal.append(i.attrib['name'])
                if i.tag == "property":
                    mpris_property.append(i.attrib['name'])

        print mpris_method
        print mpris_signal
        print mpris_property

    def introspectable(self, obj):
        introspect = dbus.Interface(obj, 'org.freedesktop.DBus.Introspectable')
        data = introspect.Introspect()
        self.parse_xml(data)

    def get_properties(self, obj):
        property_manager = dbus.Interface(obj, 'org.freedesktop.DBus.Properties')
        properties = property_manager.GetAll('org.mpris.MediaPlayer2.Player')
        for k in properties:
            print k, properties[k]

    def name_owner_changed_cb(self, name, old_owner, new_owner):
        if not name.startswith('org.mpris.MediaPlayer2'):
            return
        if new_owner:
            pid = self.get_pid(new_owner)
            op = "add"
            if pid not in self.process_list:
                self.process_list.append(pid)
            obj = self.bus.get_object(name, '/org/mpris/MediaPlayer2')
            self.get_properties(obj)
            self.introspectable(obj)
        elif old_owner:
            pid = self.get_pid(old_owner)
            op = "remove"
            if pid in self.process_list:
                self.process_list.remove(pid)
        else:
            pid = -1
            op = "NULL"
        print "op: '%s'\tname:'%s'\told:'%s'\tnew:'%s'\tpid:%d" % (op, name, old_owner, new_owner, pid), self.process_list

if __name__ == '__main__':
    mainloop = gobject.MainLoop()
    Mpris2()
    print "Running example service."
    mainloop.run()
