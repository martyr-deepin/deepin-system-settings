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


from tray_shutdown_gui import Gui

class TrayShutdownPlugin(object):
    def __init__(self):
        self.gui = Gui()
        self.gui.stop_btn.connect("clicked", self.stop_btn_clicked)
        self.gui.restart_btn.connect("clicked", self.restart_btn_clicked)
        self.gui.suspend_btn.connect("clicked", self.suspend_btn_clicked)
        self.gui.logout_btn.connect("clicked", self.logout_btn_clicked)

    def stop_btn_clicked(self, widget):
        self.this.hide_menu()
        self.gui.cmd_dbus.stop()

    def restart_btn_clicked(self, widget):
        self.this.hide_menu()
        self.gui.cmd_dbus.restart()

    def suspend_btn_clicked(self, widget):
        self.this.hide_menu()
        self.gui.cmd_dbus.suspend()

    def logout_btn_clicked(self, widget):
        self.this.hide_menu()
        self.gui.cmd_dbus.logout(0)

    def init_values(self, this_list):
        self.this_list = this_list
        self.this = self.this_list[0]
        self.tray_icon = self.this_list[1]
        #user_pixbuf = self.tray_icon.load_icon("user")
        #self.gui.user_icon.set_from_pixbuf(user_pixbuf)
        self.tray_icon.set_icon_theme("tray_user_icon")

    def run(self):
        return True

    def insert(self):
        return 0
        
    def id(self):
        return "tray-shutdown-plugin-hailongqiu"

    def plugin_widget(self):
        return self.gui 

    def show_menu(self):
        self.this.set_size_request(160, -1)
        print "shutdown show menu..."

    def hide_menu(self):
        print "shutdown hide menu..."

def return_plugin():
    return TrayShutdownPlugin 


