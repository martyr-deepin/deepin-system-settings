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
import pango
from nls import _
from tray_shutdown_dbus import CmdDbus
from vtk.button import SelectButton
from dtk.ui.line import HSeparator
import os
import sys
sys.path.append("/usr/share/deepin-system-settings/dss")
from theme import app_theme
from vtk.utils import get_text_size


WIDTH = 120

class Gui(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.init_values()
        self.init_widgets()

    def init_values(self):
        self.cmd_dbus = CmdDbus()

    def init_widgets(self):
        icon_width = icon_height = 30
        #
        self.user_hbox = gtk.HBox()
        self.user_icon = gtk.Image()
        self.user_icon.set_from_file(self.cmd_dbus.get_user_image_path())
        #
        user_pixbuf = self.user_icon.get_pixbuf()
        new_user_pixbuf = user_pixbuf.scale_simple(icon_width, icon_height, gtk.gdk.INTERP_BILINEAR)
        if new_user_pixbuf:
            try:
                self.user_icon.set_from_pixbuf(new_user_pixbuf)
            except Exception, e:
                print "set user icon[error]:", e

        #
        user_name = self.cmd_dbus.get_user_name()
        user_name_width = get_text_size(user_name)[0]
        if user_name_width > WIDTH: 
            de_user_name = user_name.decode("utf-8")
            user_name = de_user_name[0:10] + "..."
        self.user_label_ali = gtk.Alignment(0, 0, 1, 1)
        self.user_label_ali.set_padding(0, 0, 5, 0)
        self.user_label = gtk.Label(user_name)
        self.user_label_ali.add(self.user_label)
        self.user_hbox.pack_start(self.user_icon, False, False)
        self.user_hbox.pack_start(self.user_label_ali, False, False)
        #
        self.h_separator_top_ali = gtk.Alignment(0, 0, 1, 1)
        self.h_separator_top_ali.set_padding(5, 5, 0, 0)
        self.h_separator_top = HSeparator(
                app_theme.get_shadow_color("hSeparator").get_color_info(), 
                0, 
                0)
        self.h_separator_top_ali.add(self.h_separator_top)
        #
        self.stop_btn = SelectButton(_("shutdown"), font_size=10)
        self.restart_btn = SelectButton(_("restart"), font_size=10)
        self.suspend_btn = SelectButton(_("suspend"), font_size=10)
        self.logout_btn = SelectButton(_("logout"), font_size=10)
        #
        self.stop_btn.set_size_request(WIDTH, 25)
        self.restart_btn.set_size_request(WIDTH, 25)
        self.suspend_btn.set_size_request(WIDTH, 25)
        self.logout_btn.set_size_request(WIDTH, 25)
        #
        self.pack_start(self.user_hbox, True, True)
        self.pack_start(self.h_separator_top_ali, True, True)
        self.pack_start(self.stop_btn, True, True)
        self.pack_start(self.restart_btn, True, True)
        self.pack_start(self.suspend_btn, True, True)
        self.pack_start(self.logout_btn, True, True)

if __name__ == "__main__":
    win = gtk.Window(gtk.TOPLEVEL_WINDOW)
    win.add(SelectButton("策划"))
    win.show_all()
    gtk.main()
