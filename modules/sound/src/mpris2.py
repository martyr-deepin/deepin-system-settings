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

class Mpris2(gobject.GObject):

    __gsignals__ = {
        "new": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (int,)),
        "removed": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (int,)),
        "changed": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (int, gobject.TYPE_PYOBJECT))}

    def __init__(self):
        super(Mpris2, self).__init__()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.mpris_process = {} # pid -> dbus_object
        self.mpris_list = {}    # name -> pid
     
        self.bus = dbus.SessionBus()
        self.bus.add_signal_receiver(self.name_owner_changed_cb, dbus_interface='org.freedesktop.DBus', signal_name='NameOwnerChanged')
        self.bus_path = self.bus.get_object('org.freedesktop.DBus', '/')
        self.get_pid = self.bus_path.get_dbus_method('GetConnectionUnixProcessID', 'org.freedesktop.DBus')
        self.get_name_list = self.bus_path.get_dbus_method('ListNames', 'org.freedesktop.DBus')
        
    def parse_xml(self, data, pid):
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

        self.mpris_process[pid]['method'] = mpris_method

    def introspectable(self, pid):
        if pid not in self.mpris_process:
            return None
        obj = self.mpris_process[pid]['obj']
        introspect = dbus.Interface(obj, 'org.freedesktop.DBus.Introspectable')
        data = introspect.Introspect()
        self.parse_xml(data, pid)

    def get_properties(self, pid):
        if pid not in self.mpris_process:
            return None
        obj = self.mpris_process[pid]['obj']
        obj.connect_to_signal("PropertiesChanged",
                              self.property_changed_cb,
                              'org.freedesktop.DBus.Properties',
                              sender_keyword="unique",
                              #destination_keyword="des",
                              #interface_keyword="if",
                              #member_keyword="mem",
                              #path_keyword="path",
                              #message_keyword="mesg"
                              )
        property_manager = dbus.Interface(obj, 'org.freedesktop.DBus.Properties')
        properties = property_manager.GetAll('org.mpris.MediaPlayer2.Player')
        identity = property_manager.Get('org.mpris.MediaPlayer2', 'Identity')
        desktop_entry = property_manager.Get('org.mpris.MediaPlayer2', 'DesktopEntry')
        self.mpris_process[pid]['property'] = properties
        self.mpris_process[pid]['property']['Identity'] = identity
        self.mpris_process[pid]['property']['DesktopEntry'] = desktop_entry
        #print "get property---------------", obj, identity
        #for k in properties:
            #print k, properties[k]
        #print "-"*5

    def get_mpris_list(self):
        dbus_list = self.get_name_list()
        for name in dbus_list:
            if not name.startswith('org.mpris.MediaPlayer2'):
                continue
            try:
                pid = self.get_pid(name)
                if pid in self.mpris_process:
                    continue
                obj = self.bus.get_object(name, '/org/mpris/MediaPlayer2')
                self.mpris_list[name] = pid
                self.mpris_process[pid] = {}
                self.mpris_process[pid]['obj'] = obj
                self.get_properties(pid)
                self.introspectable(pid)
                self.emit("new", pid)
            except:
                if pid in self.mpris_process:
                    del self.mpris_process[pid]

    def name_owner_changed_cb(self, name, old_owner, new_owner):
        if not name.startswith('org.mpris.MediaPlayer2'):
            return
        if new_owner:
            try:
                pid = self.get_pid(new_owner)
                op = "add"
                obj = self.bus.get_object(name, '/org/mpris/MediaPlayer2')
                self.mpris_list[new_owner] = pid
                self.mpris_process[pid] = {}
                self.mpris_process[pid]['obj'] = obj
                self.get_properties(pid)
                self.introspectable(pid)
                self.emit("new", pid)
            except:
                if pid in self.mpris_process:
                    del self.mpris_process[pid]
        elif old_owner:
            try:
                #print "name changed:", old_owner, self.mpris_list
                pid = self.get_pid(old_owner)
            except:
                if old_owner in self.mpris_list:
                    pid = self.mpris_list[old_owner]
                    del self.mpris_list[old_owner]
                else:
                    pid = None
            op = "remove"
            if pid in self.mpris_process:
                del self.mpris_process[pid]
            if pid:
                self.emit("removed", pid)
        else:
            pid = -1
            op = "NULL"
        #print "op: '%s'\tname:'%s'\told:'%s'\tnew:'%s'\tpid:%d" % (op, name, old_owner, new_owner, pid), self.mpris_process

    def property_changed_cb(self, ifname, changed, invalid, **kw):
        #print ifname, "property changed", kw
        pid = self.get_pid(kw['unique'])
        for k in changed:
            #print k, changed[k]
            self.mpris_process[pid]['property'][k] = changed[k]
        self.emit("changed", pid, changed)
        #print "invalid:^^^^^^^^^^^^^^^^6", invalid
        #print "-"*20
if __name__ == '__main__':
    mainloop = gobject.MainLoop()
    Mpris2()
    print "Running example service."
    mainloop.run()
