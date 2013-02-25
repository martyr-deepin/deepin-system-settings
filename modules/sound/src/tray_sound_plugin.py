#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
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

from tray_sound_gui import TrayGui

from subprocess import Popen
import gtk

class SoundTray(object):
    def __init__(self):
        super(SoundTray, self).__init__()
        self.WIN_WIDTH = 250
        self.WIN_HEIGHT = 170
        self.widget = TrayGui()
        self.widget.button_more.connect("clicked", self.on_more_button_clicked_cb)

    def init_values(self, value_list):
        self.this_list = value_list
        self.this = self.this_list[0]
        self.this.set_size_request(self.WIN_WIDTH, self.WIN_HEIGHT)
        self.tray_icon = self.this_list[1]
        self.tray_icon.set_icon_theme("tray_sound_icon")

    def run(self):
        return True

    def id(self):
        return "sound-tray"

    def insert(self):
        return 2

    def plugin_widget(self):
        return self.widget

    def show_menu(self):
        self.this.set_size_request(self.WIN_WIDTH, self.WIN_HEIGHT)
        print "show......."

    def hide_menu(self):
        print "hide..........."

    def on_more_button_clicked_cb(self, button):
        try:
            self.this.hide_menu()
            Popen(("deepin-system-settings", "sound"))
        except Exception, e:
            print e
            pass
        
def return_plugin():
    return SoundTray
