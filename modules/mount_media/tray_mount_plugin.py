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
        self.ejecter_app = EjecterApp()
        pass

    def init_values(self, this_list):
        self.this = this_list[0]
        self.tray_icon = this_list[1]
        self.tray_icon.set_icon_theme("usb")

    def id(slef):
        return "deepin-mount-media-hailongqiu"

    def run(self):
        return True

    def insert(self):
        return 4

    def plugin_widget(self):
        return self.ejecter_app.vbox

    def show_menu(self):
        self.this.set_size_request(250, 180)

    def hide_menu(self):
        pass



def return_plugin():
    return MountMedia
