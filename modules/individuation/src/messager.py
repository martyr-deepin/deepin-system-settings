#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Zhai Xiang
# 
# Author:     Zhai Xiang <zhaixiang@linuxdeepin.com>
# Maintainer: Zhai Xiang <zhaixiang@linuxdeepin.com>
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

from deepin_utils.ipc import is_dbus_name_exists
from constant import APP_DBUS_NAME, APP_OBJECT_NAME
import dbus

class Messager():
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        pass

    def __handle_dbus_replay(self, *reply):                                     
        pass                                                                    
                                                                                
    def __handle_dbus_error(self, *error):                                      
        pass                                                                    
                                                                                
    def send_message(self, message_type, message_content):                    
        if is_dbus_name_exists(APP_DBUS_NAME):                                  
            bus_object = dbus.SessionBus().get_object(APP_DBUS_NAME, APP_OBJECT_NAME)
            method = bus_object.get_dbus_method("message_receiver")             
            method(message_type,                                                
                   message_content,                                             
                   reply_handler=self.__handle_dbus_replay,                     
                   error_handler=self.__handle_dbus_error)       
