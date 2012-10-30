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
import traceback
from nmobject import NMObject
from nmutils.nmconnection import NMConnection
from nm_utils import TypeConvert

class NMRemoteConnection(NMObject, NMConnection):
    '''NMRemoteConnection'''
        
    __gsignals__  = {
            "removed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,)),
            "updated":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,)),
            "visible":(gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE, (str,))
            }

    def __init__(self, object_path):
        NMConnection.__init__(self)
        NMObject.__init__(self, object_path, "org.freedesktop.NetworkManager.Settings.Connection")
        # self.dbus_interface.connect_to_signal("Removed", self.removed_cb)
        # self.dbus_interface.connect_to_signal("Updated", self.updated_cb)
        self.bus.add_signal_receiver(self.removed_cb, dbus_interface = self.object_interface, signal_name = "Removed")
        self.bus.add_signal_receiver(self.updated_cb, dbus_interface = self.object_interface, signal_name = "Updated")

        # self.settings_dict = self.get_settings()
        self.init_settings_prop_dict()

    def is_active(self):
        pass

    def delete(self):
        try:
            self.dbus_interface.Delete(reply_handler = self.delete_finish, error_handler = self.delete_error)
        except:
            traceback.print_exc()
            
    def delete_finish(self):
        pass

    def delete_error(self, error):
        print error

    def get_settings(self):
        return TypeConvert.dbus2py(self.dbus_method("GetSettings"))

    def get_secrets(self, setting_name):
        return TypeConvert.dbus2py(self.dbus_method("GetSecrets", setting_name))
        
    def update(self):
        try:
            self.dbus_interface.Update(self.settings_dict, reply_handler = self.update_finish, error_handler = self.update_error)
        except:
            traceback.print_exc()

    def update_sync(self):    
        self.dbus_method("Update", self.update_settings_prop_dict())

    def update_async(self):
        try:
            self.dbus_interface.Update(self.settings_dict, reply_handler = self.update_finish, error_handler = self.update_error)
        except:
            traceback.print_exc()

    def update_finish(self):
        print "update finished"

    def update_error(self, error):
        print "update settings failed!\n"
        print error

    def init_settings_prop_dict(self):
        self.settings_dict = self.get_settings()
        for item in self.settings_dict.iterkeys():
            # self.get_setting(item).prop_dict = copy.deepcopy(self.settings_dict[item])
            self.get_setting(item).prop_dict = self.settings_dict[item]

    def update_settings_prop_dict(self):
        '''because of shallow copy, settings_dict automatic update when prop_dict changed'''
        # for item in self.settings_dict.iterkeys():
        #     self.settings_dict[item] = self.get_setting(item).prop_dict
        return self.settings_dict    

    ###Signals###
    def removed_cb(self):
        self.emit("removed", self.object_path)

    def updated_cb(self):
        self.emit("updated", self.object_path)

    def visible_cb(self, arg):
        self.emit("visible", arg)

if __name__ == "__main__":
    nm_remote_connection = NMRemoteConnection("/org/freedesktop/NetworkManager/Settings/7")
