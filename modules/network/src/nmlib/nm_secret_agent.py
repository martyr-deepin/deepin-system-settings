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
        
    def __init__(self):
        NMObject.__init__(self, "/org/freedesktop/NetworkManager/AgentManager", "org.freedesktop.NetworkManager.AgentManager")

    def register(self, identifier):
        try:
            if self.validate_identifier(identifier):
                self.dbus_method("Register", identifier, reply_handler = self.register_finish, error_handler = self.register_error)
        except:
            traceback.print_exc()

    def register_finish(self, *reply):
        pass

    def register_error(self, *error):
        pass

    def unregister(self):
        try:
            self.dbus_method("UnRegister", reply_handler = self.unregister_finish, error_handler = self.unregister_error)
        except:
            traceback.print_exc()

    def unregister_finish(self, *reply):
        pass

    def unregister_error(self, *error):
        pass

    def validate_identifier(self, identifier):
        if len(identifier) < 3 or len(identifier) > 255:
            return False
        if identifier.startswith('.') or identifier.endswith('.'):
            return False
        li = list(identifier)
        for i in range(len(li)):
            if li[i] == '.' and li[i+1] == '.':
                return False
            if not li[i].isalnum() and li[i] not in ["_","-","."]:
                return False
        return True    


agent_manager = NMAgentManager()

class NMSecretAgent(NMObject):
    '''NMSecretAgent'''
    # __gsignals__  = {
    #         "registration-result":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_NONE,)),
    #         }
    
    def __init__(self):
        self.auto_register = ""
        self.identifier = "org.freedesktop.NetworkManager.SecretAgent"
        self.registered = ""
        
        agent_manager.register(self.identifier)

    def generate_service_name(self, uuid, setting_name):
        return "nm_" + uuid +"_" + setting_name

    def GetSecrets(self, connection, setting_name):
        service = self.generate_service_name(connection.settings_dict["connection"]["uuid"], setting_name)
        username = getpass.getuser()
        return keyring.get_password(service, username)

    def CancelGetSecrets(self, connection, setting_name):
        pass

    def SaveSecrets(self, connection, setting_name):
        service = self.generate_service_name(connection.settings_dict["connection"]["uuid"], setting_name)
        username = getpass.getuser()
        password = connection.get_secrets(setting_name)
        keyring.set_password(service, username, password)

    def DeleteSecrets(self, connection, setting_name):
        service = self.generate_service_name(connection.settings_dict["connection"]["uuid"], setting_name)
        username = getpass.get_user()
        if keyring.get_password(service, username):
            keyring.set_password(service, username, "")

# secret_agent = NMSecretAgent()

if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)  
    agent = NMSecretAgent()
    mainloop = gobject.MainLoop()
    mainloop.run()
    
