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

import os
from bt.manager import Manager
from bt.adapter import Adapter
from bt.device import Device
from ods.OdsManager import OdsManager

from nls import _
from dtk.ui.dialog import ConfirmDialog
from deepin_utils.process import run_command
from bluetooth_dialog import BluetoothProgressDialog, BluetoothReplyDialog

TRANSFER_DIR = "~"

class BluetoothTransfer(OdsManager):
    def __init__(self):
        OdsManager.__init__(self)
        self.GHandle("server-created", self.on_server_created)

    def start_server(self, pattern):
        server = self.get_server(pattern)
        if server != None:
            if pattern == "opp":
                server.Start(os.path.expanduser(TRANSFER_DIR), True, False)
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
        session.GHandle("cancelled", self.transfer_cancelled)
        session.GHandle("disconnected", self.transfer_disconnected)
        session.GHandle("transfer-completed", self.transfer_finished)
        session.GHandle("error-occurred", self.transfer_error)
        session.GHandle("transfer-started", self.on_transfer_started)

        session.transfer = {}

        session.server = server

    def on_transfer_started(self, session, filename, local_path, total_bytes):
        session.transfer["progress_dialog"] = BluetoothProgressDialog()
        session.transfer["progress_dialog"].set_keep_above(True)
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
        session.transfer["cancelled"] = False

        session.transfer["address"] = info["BluetoothAddress"]
        session.transfer["name"] = name

        def confirm_clicked():
            session.Accept()
            session.Transfer["accept"] = True
        session.transfer["confirm_dialog"] = ConfirmDialog(_("Incoming file from %s" % name),
                                       _("Accept incoming file %s?") % filename,
                                       confirm_callback=lambda : session.Accept(),
                                       cancel_callback=lambda : session.Reject())
        session.transfer["confirm_dialog"].confirm_button.set_label(_("Accept"))
        session.transfer["confirm_dialog"].cancel_button.set_label(_("Reject"))
        session.transfer["confirm_dialog"].set_keep_above(True)
        session.transfer["confirm_dialog"].show_all()

    def transfer_progress(self, session, bytes_transferred):
        print bytes_transferred / float(session.transfer["total"])
        session.transfer["progress_dialog"].cancel_cb = lambda : session.Cancel()
        session.transfer["progress_dialog"].set_message(_("Receiving file from %s") % session.transfer["name"])
        session.transfer["progress_dialog"].set_progress(bytes_transferred / float(session.transfer["total"]) * 100)
        session.transfer["progress_dialog"].show_all()

    def transfer_finished(self, session):
        print "transfer_finished"
        if not session.transfer["cancelled"]:
            # reply_dlg = BluetoothReplyDialog(_("Transfer completed!"))
            # reply_dlg.set_keep_above(True)
            # reply_dlg.show_all()
            
            run_command("xdg-open %s" % TRANSFER_DIR)

            if session.transfer["progress_dialog"].get_visible():
                session.transfer["progress_dialog"].destroy()

    def transfer_cancelled(self, session):
        print "transfer_cancelled"
        session.transfer["cancelled"] = True

    def transfer_disconnected(self, sesssion):
        print "transfer_disconnected"

    def transfer_error(self, session, name, msg):
        print "transfer_errer", name, msg
        if not session.transfer["cancelled"]:
            reply_dlg = BluetoothReplyDialog(_("Failed to receive the file : %s") % msg, is_succeed=False)
            reply_dlg.set_keep_above(True)
            reply_dlg.show_all()

        if session.transfer["progress_dialog"].get_visible():
            session.transfer["progress_dialog"].destroy()
        if session.transfer["confirm_dialog"].get_visible():
            session.transfer["confirm_dialog"].destroy()
