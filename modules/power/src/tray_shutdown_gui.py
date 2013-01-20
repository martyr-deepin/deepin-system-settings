#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Deepin, Inc.
#               2012 Hailong Qiu
#
# Author:     Hailong Qiu <356752238@qq.com>
# Maintainer: Hailong Qiu <356752238@qq.com>
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

import gtk
from tray_shutdown_dbus import CmdDbus

class Gui(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.init_values()
        self.init_widgets()

    def init_values(self):
        self.cmd_dbus = CmdDbus()

    def init_widgets(self):
        self.stop_btn = gtk.Button("关机")
        self.restart_btn= gtk.Button("重启")
        self.suspend_btn = gtk.Button("休眠")
        #
        self.stop_btn.connect("clicked", self.stop_btn_clicked)
        self.restart_btn.connect("clicked", self.restart_btn_clicked)
        self.suspend_btn.connect("clicked", self.suspend_btn_clicked)
        #
        self.pack_start(self.stop_btn, False, False)
        self.pack_start(self.restart_btn, False, False)
        self.pack_start(self.suspend_btn, False, False)

    def stop_btn_clicked(self, widget):
        print self.cmd_dbus.stop()

    def restart_btn_clicked(self, widget):
        print self.cmd_dbus.restart()

    def suspend_btn_clicked(self, widget):
        print self.cmd_dbus.suspend()

