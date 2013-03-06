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
        self.WIN_WIDTH = 188
        self.WIN_HEIGHT = 130
        self.__this_visible = False
        self.__volume_level = None
        self.__mute = None
        self.tray_obj = None

        self.widget_align = gtk.Alignment()
        #self.widget_align.set(0.5, 0.0, 0, 0)
        #self.widget_align.set_padding(10, 10, 10, 10)
        self.widget = TrayGui(self)
        self.widget.connect("stream-changed", self.stream_changed_cb)
        self.widget.button_more.connect("clicked", self.on_more_button_clicked_cb)
        self.widget_align.add(self.widget)

    def init_values(self, value_list):
        self.this_list = value_list
        self.this = self.this_list[0]
        self.tray_obj = self.this_list[1]
        #self.tray_obj.set_icon_theme("tray_sound_icon")
        self.this.set_default_size(self.WIN_WIDTH, self.widget.get_widget_height())
        self.widget.update_tray_icon()

    def set_tray_icon(self, volume_level, mute):
        if not self.tray_obj or volume_level == self.__volume_level and mute == self.__mute:
            return
        self.__volume_level = volume_level
        self.__mute = mute
        if mute:
            self.tray_obj.set_icon_theme("tray_sound_mute")
        else:
            icon_list = ["tray_sound_icon0", "tray_sound_icon1", "tray_sound_icon2", "tray_sound_icon"]
            self.tray_obj.set_icon_theme(icon_list[volume_level])

    def run(self):
        return True

    def id(self):
        return "sound-tray"

    def insert(self):
        return 2

    def plugin_widget(self):
        return self.widget_align

    def show_menu(self):
        self.this.set_size_request(self.WIN_WIDTH, self.widget.get_widget_height())
        self.__this_visible = True
        print "show......."

    def hide_menu(self):
        self.__this_visible = False
        print "hide..........."

    def on_more_button_clicked_cb(self, button):
        try:
            self.this.hide_menu()
            Popen(("deepin-system-settings", "sound"))
        except Exception, e:
            print e
            pass

    def stream_changed_cb(self, widget):
        if self.__this_visible:
            self.this.set_size_request(self.WIN_WIDTH, self.widget.get_widget_height())
            self.this.reshow_with_initial_size()
        
def return_plugin():
    return SoundTray
