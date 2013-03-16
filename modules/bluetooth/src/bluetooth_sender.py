#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Deepin, Inc.
#               2013 Zhai Xiang
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

from dtk.ui.dialog import OpenFileDialog
from constant import *
from nls import _
from ods.OdsManager import OdsManager
from helper import event_manager
import os

class BluetoothSender:
    def __init__(self, adapter, device):
        self.adapter = adapter
        self.device = device
        
        event_manager.add_callback("cancel", self.__on_cancel)

    def __on_session_connected(self, session):
        self.__session = session
        if self.__session and self.__session.Connected:                            
            self.__session.SendFile(self.filename) 
 
    def __on_session_disconnected(self, session):
        if self.__session:
            self.__session.Close()

    def __on_session_error(self, session, name, msg):
        send_message("dialog", 
                     ("bluetooth", "progress", "", str("-1"))
                    )
        send_message("dialog", 
                     ("bluetooth", "reply", _("Failed!\nerror msg: %s") % msg, "False")
                    )

    def __on_cancel(self, name, obj, argv):                                            
        def reply(*args):                                               
            self.__session.Disconnect()                               
                                                                                
        if self.__session:                                                
            if self.__session.Connected:                              
                self.__session.Cancel(reply_handler=reply, error_handler=reply)
            else:                                                   
                self.__ods_manager.CancelSessionConnect(self.__session.object_path)

    def __on_transfer_started(self, session, filename, path, size):
        send_message("dialog", 
                     ("bluetooth", "progress", _("Sending file to %s") % self.device.get_name(), "")
                    )

    def __on_transfer_progress(self, session, progress):
        progress_value = int(float(progress) / float(self.total_bytes) * 100.0)
        send_message("dialog", 
                     ("bluetooth", "progress", "", str(progress_value))
                    )

    def __on_transfer_completed(self, session):
        send_message("dialog", 
                     ("bluetooth", "progress", "", str(-1))
                    )

        self.__session.Disconnect()
        self.__session.Close()

        send_message("dialog", ("bluetooth", "reply", _("Succeed!"), ""))

    def __on_session_created(self, manager, session):
        self.__session = session
        session.GHandle("connected", self.__on_session_connected)          
        session.GHandle("disconnected", self.__on_session_disconnected)    
        session.GHandle("error-occurred", self.__on_session_error)         
        session.GHandle("transfer-started", self.__on_transfer_started)    
        session.GHandle("transfer-progress", self.__on_transfer_progress) 
        session.GHandle("transfer-completed", self.__on_transfer_completed)

    def __on_session_destroyed(self, manager, path):                          
        if self.__session.object_path == path:                            
            self.__session = None

    def __create_session(self):
        def on_error(msg):
            print "create session error", msg

        props = self.adapter.get_properties()
        self.__ods_manager.create_session(self.device.get_address(), props["Address"], error_handler=on_error)

    def __send_file(self, filename):
        self.filename = filename
        self.total_bytes = os.path.getsize(self.filename)
        self.__ods_manager = OdsManager()
        self.__ods_manager.GHandle("session-created", self.__on_session_created)
        self.__ods_manager.GHandle("session-destroyed", self.__on_session_destroyed)
        self.__create_session()

    def do_send_file(self):
        OpenFileDialog(_("Select File"), None, lambda name : self.__send_file(name), None)
