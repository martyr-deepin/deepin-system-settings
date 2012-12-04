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
from nm_secret_agent import secret_agent

class NMRemoteConnection(NMObject, NMConnection):
    '''NMRemoteConnection'''
        
    __gsignals__  = {
            "removed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,)),
            "updated":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,)),
            "visible":(gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE, (str,)),
            "request-password":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,))
            }

    def __init__(self, object_path):
        NMConnection.__init__(self)
        NMObject.__init__(self, object_path, "org.freedesktop.NetworkManager.Settings.Connection")

        self.bus.add_signal_receiver(self.removed_cb, dbus_interface = self.object_interface,
                                     path = self.object_path, signal_name = "Removed")

        self.bus.add_signal_receiver(self.updated_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "Updated")

        # self.settings_dict = self.get_settings()
        self.init_settings_prop_dict()
        self.succeed_flag = 0

        ###used by secret agent
        self.secret_setting_name = ""
        self.secret_method = ""

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
        return self.dbus_method("GetSettings")

    def get_secrets(self, setting_name):
        try:
            return TypeConvert.dbus2py(self.dbus_method("GetSecrets", setting_name))
        except:
            return {}

    def guess_secret_info(self):
        '''guess_secret_info'''
        info_dict = TypeConvert.dbus2py(self.settings_dict)

        if "vpn" in info_dict.iterkeys():
            self.secret_setting_name = "vpn"
            self.secret_method = "password"
            return (self.secret_setting_name, self.secret_method)

        elif "pppoe" in info_dict.iterkeys() and "802-3-ethernet" in info_dict.iterkeys():
            self.secret_setting_name = "pppoe"
            self.secret_method = "password"
            return (self.secret_setting_name, self.secret_method)

        elif "802-11-wireless" in info_dict.iterkeys() and "802-11-wireless-security" in info_dict.iterkeys():

            self.secret_setting_name = "802-11-wireless-security"

            if "key-mgmt" in info_dict["802-11-wireless-security"].iterkeys():
                if info_dict["802-11-wireless-security"]["key-mgmt"] == "wpa-psk":
                    self.secret_method = "psk"
                    return (self.secret_setting_name, self.secret_method)
                    
                elif info_dict["802-11-wireless-security"]["key-mgmt"] == "none":
                    if "wep-key-type" in info_dict["802-11-wireless-security"].iterkeys():

                        if "wep-tx-keyidx" in info_dict["802-11-wireless-security"].iterkeys():
                            if info_dict["802-11-wireless-security"]["wep-tx-keyidx"] == 0:
                                self.secret_method = "wep-key0"
                            elif info_dict["802-11-wireless-security"]["wep-tx-keyidx"] == 1:
                                self.secret_method = "wep-key1"
                            elif info_dict["802-11-wireless-security"]["wep-tx-keyidx"] == 2:
                                self.secret_method = "wep-key2"
                            elif info_dict["802-11-wireless-security"]["wep-tx-keyidx"] == 3:
                                self.secret_method = "wep-key3"
                            else:
                                print "unsupported wep key idx"

                            return (self.secret_setting_name, self.secret_method)    
                        else:
                            self.secret_method = "wep-key0"
                            return (self.secret_setting_name, self.secret_method)
                    else:
                        print "must have wep-key-type to indicate wep connection"

                elif info_dict["802-11-wireless-security"]["key-mgmt"] == "wpa-eap":
                    print "no agent available for wpa-eap"
                    
                elif info_dict["802-11-wireless-security"]["key-mgmt"] == "ieee8021x":
                    if "auth-alg" in info_dict["802-11-wireless-security"].iterkeys():
                        if info_dict["802-11-wireless-security"]["auth-alg"] == "leap":
                            self.secret_method = "leap-password"
                            return (self.secret_setting_name, self.secret_method)
                    else:
                        print "no ageent available for dynamic wep"
                else:
                    print "unknown key mgmt"

            else:
                print "must have key mgmt for 802.11 wireless security"

        elif "802-3-ethernet" in info_dict.iterkeys():
            self.secret_setting_name = None
            self.secret_method = None

        elif "ppp" in info_dict.iterkeys():
            self.secret_setting_name = ""
            self.secret_method = ""

        elif "802-1x" in info_dict.iterkeys():
            self.secret_setting_name = ""
            self.secret_method = ""

        elif "cdma" in info_dict.iterkeys():
            self.secret_setting_name = "cdma"
            self.secret_method = "password"

        elif "gsm" in info_dict.iterkeys():
            self.secret_setting_name = "gsm"
            self.secret_method = "password"

        else:
            self.secret_setting_name = None
            self.secret_method = None

    def update(self):
        try:
            self.guess_secret_info()
            if self.secret_setting_name != None and self.secret_method != None:
                secret_agent.agent_save_secrets(self.object_path, self.secret_setting_name, self.secret_method)

            self.dbus_interface.Update(self.settings_dict, reply_handler = self.update_finish, error_handler = self.update_error)
            # print secret_agent.agent_get_secrets(self.object_path, self.secret_setting_name, self.secret_method)
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
