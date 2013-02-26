#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Deepin, Inc.
#               2013 Hailong Qiu
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
from tray_mount_gui import EjecterApp

class MountMedia(object):
    def __init__(self):
        self.height = 40
        self.h_padding = 25
        self.ejecter_app = EjecterApp()
        self.ejecter_app.connect("update-usb", self.ejecter_app_update_usb)
        self.ejecter_app.connect("remove-usb", self.ejecter_app_remove_usb)
        self.ejecter_app.connect("empty-usb", self.ejecter_app_empty_usb)

    def ejecter_app_empty_usb(self, ejecter_app):
        self.hide_mount_tray()

    def ejecter_app_update_usb(self, ejecter_app):
        self.height += self.h_padding
        self.this.set_size_request(180, self.height)
        self.show_mount_tray()

    def ejecter_app_remove_usb(self, ejecter_app): 
        self.height -= self.h_padding
        self.this.resize(1, 1)
        self.this.set_size_request(180, self.height)
        self.hide_mount_tray()

    def show_mount_tray(self):
        if self.ejecter_app.devices != {}:
            self.tray_icon.set_visible(True)
            self.this.hide_menu()
            
    def hide_mount_tray(self):
        if self.ejecter_app.devices == {}:
            self.tray_icon.set_visible(False)
            self.this.hide_menu()

    def init_values(self, this_list):
        self.this = this_list[0]
        self.tray_icon = this_list[1]
        self.tray_icon.set_icon_theme("usb")
        self.hide_mount_tray()

        for value in self.ejecter_app.devices.values():
            self.height += self.h_padding

    def id(slef):
        return "deepin-mount-media-hailongqiu"

    def run(self):
        return True

    def insert(self):
        return 4

    def plugin_widget(self):
        return self.ejecter_app.vbox

    def show_menu(self):
        print self.height
        self.this.set_size_request(180, self.height)

    def hide_menu(self):
        pass



def return_plugin():
    return MountMedia
