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
import keyring
import getpass
import traceback
import dbus
import dbus.service
import dbus.mainloop.glib
from nmobject import NMObject

class NMAgentManager(NMObject):
    '''NMAgentManager'''
        
    __gsignals__  = {
            "registration-result":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_NONE,))
            }
        
    def __init__(self):
        NMObject.__init__(self, "/org/freedesktop/NetworkManager/AgentManager", "org.freedesktop.NetworkManager.AgentManager")
        self.bus.add_signal_receiver(self.access_point_added_cb, dbus_interface = self.object_interface, signal_name = "AccessPointAdded")
        self.connect("registration-result", self.registration_result_cb)

        self.auto_register = ""
        self.identifier = ""
        self.registered = ""

    def register(self, identifier):
        try:
            self.dbus_interface.Register(identifier)
        except:
            traceback.print_exc()

    def unregister(self):
        try:
            self.dbus_interface.UnRegister()
        except:
            traceback.print_exc()

    def validate_identifier(self, identifier):
        if len(identifier) < 3 or len(identifier) > 255:
            return False
        if identifier.startswith('.') or identifier.endswith('.'):
            return False
        li = list(identifier)
        for i in range(li):
            if li[i] == '.' and li[i+1] == '.':
                return False
            if not li[i].isalnum() and li[i] not in ["_","-","."]:
                return False
        return True    

    ###Signals###
    def registration_result_cb(self):
        self.emit("registration-result")

agent_manager = NMAgentManager()

class NMSecretAgent(dbus.service.Object):
    '''NMSecretAgent'''
    
    DBUS_SECRET_AGENT = "org.freedesktop.NetworkManager.SecretAgent"
    
    def __init__(self):

        dbus.service.Object.__init__(self, dbus.SystemBus(), "/org/freedesktop/NetworkManager/SecretAgent")
        agent_manager.register("org.freedesktop.NetworkManager.SecretAgent")

    def generate_service_name(self, uuid, setting_name):
        return "nm_" + uuid + "_" + setting_name 

    @dbus.service.method(DBUS_SECRET_AGENT,
                         in_signature='ossu',
                         out_signature='a{sa{sv}}',
                         sender_keyword='sender',
                         connection_keyword='conn')
    def GetSecrets(self, connection, setting_name, hints, flags, sender, conn):
        service = self.generate_service_name(connection.settings_dict["connection"]["uuid"], setting_name)
        username = getpass.getuser()
        return keyring.get_password(service, username)

    @dbus.service.method(DBUS_SECRET_AGENT,
                         in_signature='os',
                         out_signature='',
                         sender_keyword='sender',
                         connection_keyword='conn')
    def CancelGetSecrets(self, connection_path, setting_name, sender, conn):
        pass


    @dbus.service.method(DBUS_SECRET_AGENT,
                         in_signature="os",
                         out_signature='',
                         sender_keyword='sender',
                         connection_keyword='conn')
    def SaveSecrets(self, connection, setting_name, sender, conn):
        service = self.generate_service_name(connection.settings_dict["connection"]["uuid"], setting_name)
        username = getpass.getuser()
        password = connection.get_secrets(setting_name)
        keyring.set_password(service, username, password)

    @dbus.service.method(DBUS_SECRET_AGENT,
                         in_signature='a{sa{sv}}o',
                         out_signature='',
                         sender_keyword='sender',
                         connection_keyword='conn')
    def DeleteSecrets(self, connection, connection_path, sender, conn):
        service = self.generate_service_name()
        username = getpass.get_user()
        if keyring.get_password(service, username):
            keyring.set_password(service, username, "")

if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)  
    agent = NMSecretAgent()
    mainloop = gobject.MainLoop()
    mainloop.run()
    
