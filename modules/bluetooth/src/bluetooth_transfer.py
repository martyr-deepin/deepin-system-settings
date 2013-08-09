#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang YaoHua
#
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
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

from bt.manager import Manager
from bt.adapter import Adapter
from bt.device import Device
from ods.OdsManager import OdsManager
from helper import notify_message
from nls import _
import os
from bluetooth_dialog import BluetoothProgressDialog, BluetoothReplyDialog

class BluetoothTransfer(OdsManager):
    def __init__(self):
        OdsManager.__init__(self)
        self.GHandle("server-created", self.on_server_created)

        self.create_server()

    def start_server(self, pattern):
        server = self.get_server(pattern)
        if server != None:
            if pattern == "opp":
                server.Start(os.path.expanduser("~"), True, False)
                return True
        else:
            return False

    def on_server_created(self, inst, server, pattern):
        def on_started(server):
            print pattern, "server_created"

        server.GHandle("started", on_started)
        server.GHandle("session-created", self.on_session_created)
        server.pattern = pattern
        self.start_server(pattern)

    def on_session_created(self, server, session):
        print server.pattern, "session created"
        if server.pattern != "opp":
            return

        session.GHandle("transfer-progress", self.transfer_progress)
        session.GHandle("cancelled", self.transfer_finished, "cancelled")
        session.GHandle("disconnected", self.transfer_finished, "disconnected")
        session.GHandle("transfer-completed", self.transfer_finished, "completed")
        session.GHandle("error-occurred", self.transfer_finished, "error")
        session.GHandle("transfer-started", self.on_transfer_started)

        session.transfer = {}

        session.server = server

    def on_transfer_started(self, session, filename, local_path, total_bytes):
        self.progress_dialog = BluetoothProgressDialog()
        info = session.server.GetServerSessionInfo(session.object_path)
        try:
            dev = Device(Adapter(Manager().get_default_adapter()).create_device(info["BluetoothAddress"]))
            name = dev.get_alias()
        except Exception, e:
            print e
            name = info["BluetoothAddress"]

        session.transfer["filename"] = filename
        session.transfer["filepath"] = local_path
        session.transfer["total"] = total_bytes
        session.transfer["failed"] = False

        session.transfer["address"] = info["BluetoothAddress"]
        session.transfer["name"] = name

        session.Accept()

    def transfer_progress(self, session, bytes_transferred):
        print bytes_transferred / float(session.transfer["total"])
        self.progress_dialog.cancel_cb = lambda : session.Cancel()
        self.progress_dialog.set_message(_("Receiving file from %s") % session.transfer["name"])
        self.progress_dialog.set_progress(bytes_transferred / float(session.transfer["total"]) * 100)
        self.progress_dialog.show_all()

    def transfer_finished(self, session, arg):
        if arg in ["error", "cancelled"]:
            reply_dlg = BluetoothReplyDialog(_("Transfer failed!"), is_succeed=False)
            reply_dlg.set_keep_above(True)
            reply_dlg.show_all()
            session.transfer["failed"] = True
            if self.progress_dialog.get_visible():
                self.progress_dialog.destroy()
        if arg == "completed":  # signal "completed" will be received even the transfer failed
            if not session.transfer["failed"]:
                reply_dlg = BluetoothReplyDialog(_("Transfer completed!"))
                reply_dlg.set_keep_above(True)
                reply_dlg.show_all()
                if self.progress_dialog.get_visible():
                    self.progress_dialog.destroy()
