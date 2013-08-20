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

import os
import gtk
import gio
from tray_mount_gui import EjecterApp

class MountMedia(EjecterApp):
    def __init__(self):
        EjecterApp.__init__(self)

    def device_btn_icon_image_button_press_event(self, widget, event, uri):
        # 打开文件管理器.
        if event.button == 1:
            if uri:
                self.run_open_dir_command(uri)

    def device_btn_open_btn_clicked(self, widget, uri):
        # 打开文件管理器.
        if uri:
            self.run_open_dir_command(uri)
    
    def run_open_dir_command(self, uri):
        # 打开文件管理器的命令.
        os.popen("xdg-open %s" % (uri))
        self.this.hide_menu()

    def device_btn_close_btn_clicked(self, widget, drive, volume, mount):
        # 挂载的开关.
        print "device_btn_close_btn_clicked...", 
        op = gio.MountOperation()
        if mount:
            mount.unmount(self.cancall_opeartion, flags=gio.MOUNT_UNMOUNT_NONE)
        else:
            if volume:
                volume.mount(op, self.cancall_opeartion, flags=gio.MOUNT_UNMOUNT_NONE)

    def cancall_opeartion(self, object, res):
        pass

    def set_menu_size(self, height):
        if self.size_check:
            print "set_size_request..."
            if height == 75: # 无移动设备挂载.
                print "无移动设备挂载了... .."
                self.this.hide_menu()
                self.tray_icon.hide()
                self.tray_icon.set_no_show_all(True)
            else:
                old_width, old_height = self.this.get_size_request()
                print "old_height", old_height, "height", height
                if old_height != height:
                    self.tray_icon.show_all()
                    self.tray_icon.set_no_show_all(False)
                    # self.this.hide_menu()
                    self.this.set_size_request(self.width, height)
                    # self.this.show_menu()
                    self.this.show_all() # hacked by hualet, bugfix: traymenu will become scrap 
        else:                            # if you plugin in an usb stick and then remove it mercilessly
            try:
                if height == 75:
                    self.tray_icon.hide()
                    self.tray_icon.set_no_show_all(True)
                else:
                    self.tray_icon.show_all()
                    self.tray_icon.set_no_show_all(False)
            except:
                pass

    def init_values(self, this_list):
        self.this = this_list[0]
        self.tray_icon = this_list[1]
        self.tray_icon.set_icon_theme("usb")
        #self.hide_mount_tray()
        if self.height == 75:
            self.tray_icon.set_no_show_all(True)

    def id(slef):
        return "deepin-mount-media-hailongqiu"

    def run(self):
        return True

    def insert(self):
        return 4

    def plugin_widget(self):
        return self.vbox

    def show_menu(self):
        self.size_check = True
        print "set size_check True"
        #print self.height
        self.this.set_size_request(self.width, self.height)

    def hide_menu(self):
        self.size_check = False
        print "set size_check False"

def return_insert():
    return 4

def return_id():
    return "mount_media"

def return_plugin():
    return MountMedia
