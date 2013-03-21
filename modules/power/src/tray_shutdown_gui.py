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
from vtk.utils import cairo_disable_antialias
from vtk.color import color_hex_to_cairo
from dtk.ui.line import HSeparator
from dtk.ui.utils import set_clickable_cursor
import os
import sys
sys.path.append("/usr/share/deepin-system-settings/dss")
from theme import app_theme
from vtk.utils import get_text_size

WIDTH = 120
HEIGHT = 25

class Gui(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.init_values()
        self.init_widgets()

    def init_values(self):
        self.cmd_dbus = CmdDbus()
        self.gui_theme = app_theme

    def init_widgets(self):
        self.icon_width = self.icon_height = HEIGHT
        #
        self.user_hbox = gtk.HBox()
        self.user_icon = gtk.Image()
        self.user_icon.set_size_request(HEIGHT, HEIGHT)
        #
        user_name = self.cmd_dbus.get_user_name()
        user_name_width = get_text_size(user_name)[0]
        if user_name_width > WIDTH: 
            de_user_name = user_name.decode("utf-8")
            user_name = de_user_name[0:10] + "..."
        self.user_label_ali = gtk.Alignment(0, 0, 1, 1)
        self.user_label_ali.set_padding(0, 0, 5, 0)
        self.user_label_event = gtk.EventBox()
        self.user_label = gtk.Label(user_name)
        self.user_label_event.add(self.user_label)
        self.user_label_ali.add(self.user_label_event)
        self.user_icon.connect_after("expose-event", self.user_label_event_expose_event)
        #
        self.user_hbox.pack_start(self.user_icon, False, False)
        self.user_hbox.pack_start(self.user_label_ali, False, False)
        #
        self.h_separator_top_ali = gtk.Alignment(1, 1, 1, 1)
        self.h_separator_top_ali.set_padding(5, 5, 0, 0)
        hseparator_color = [(0, ("#777777", 0.0)),
                            (0.5, ("#000000", 0.3)), 
                            (1, ("#777777", 0.0))]
        self.h_separator_top = HSeparator(hseparator_color, 0, 0)
        self.h_separator_top_ali.add(self.h_separator_top)

        self.switch_separator_bottom = HSeparator(hseparator_color, 0, 0)
        self.switch_separator_bottom_ali = gtk.Alignment(1, 1, 1, 1)
        self.switch_separator_bottom_ali.set_padding(5, 5, 0, 0)
        self.switch_separator_bottom_ali.add(self.switch_separator_bottom)
        #
        ali_padding = 100  
        font_size = 10
        self.switch_btn = SelectButton(_("切换用户"), 
                                       font_size=font_size, 
                                       ali_padding=ali_padding)
        self.stop_btn = SelectButton(_("shutdown"), 
                                     font_size=font_size, 
                                     ali_padding=ali_padding)
        self.restart_btn = SelectButton(_("restart"), 
                                        font_size=font_size, 
                                        ali_padding=ali_padding)
        self.suspend_btn = SelectButton(_("suspend"), 
                                        font_size=font_size, 
                                        ali_padding=ali_padding)
        self.logout_btn = SelectButton(_("logout"), 
                                       font_size=font_size, 
                                       ali_padding=ali_padding)
        self.lock_btn = SelectButton(_("锁屏"), 
                                     font_size=font_size, 
                                     ali_padding=ali_padding)
        #
        self.switch_btn.set_size_request(WIDTH, HEIGHT)
        self.stop_btn.set_size_request(WIDTH, HEIGHT)
        self.restart_btn.set_size_request(WIDTH, HEIGHT)
        self.suspend_btn.set_size_request(WIDTH, HEIGHT)
        self.logout_btn.set_size_request(WIDTH, HEIGHT)
        self.lock_btn.set_size_request(WIDTH, HEIGHT)
        #
        self.pack_start(self.user_hbox, True, True)
        self.pack_start(self.h_separator_top_ali, True, True)
        self.pack_start(self.switch_btn, True, True)
        self.pack_start(self.switch_separator_bottom_ali, True, True)
        self.pack_start(self.stop_btn, True, True)
        self.pack_start(self.restart_btn, True, True)
        self.pack_start(self.suspend_btn, True, True)
        self.pack_start(self.logout_btn, True, True)

        if self.cmd_dbus.real_name != "Guest":
            self.pack_start(self.lock_btn, True, True)
        set_clickable_cursor(self.user_label_event)

    def user_label_event_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        size = HEIGHT
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*color_hex_to_cairo("#d2d2d2"))
            cr.set_line_width(1)
            cr.rectangle(rect.x, rect.y, size, size)
            cr.stroke()
        return True

if __name__ == "__main__":
    win = gtk.Window(gtk.TOPLEVEL_WINDOW)
    win.add(SelectButton("策划"))
    win.show_all()
    gtk.main()
