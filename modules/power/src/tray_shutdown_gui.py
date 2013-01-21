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
        self.stop_btn = SelectButton("关机")
        self.restart_btn= SelectButton("重启")
        self.suspend_btn = SelectButton("挂起")
        self.logout_btn = SelectButton("注销")
        #
        self.pack_start(self.stop_btn, False, False)
        self.pack_start(self.restart_btn, False, False)
        self.pack_start(self.suspend_btn, False, False)
        self.pack_start(self.logout_btn, False, False)

# call trayicon vtk api.
from vtk.draw import draw_text
from vtk.utils import get_text_size
from vtk.color import color_hex_to_cairo

class SelectButton(gtk.Button):        
    def __init__(self, 
                 text="", 
                 bg_color="#ebf4fd",
                 line_color="#7da2ce"):
        gtk.Button.__init__(self)
        # init values.
        self.text = text
        self.bg_color = bg_color
        self.line_color = line_color
        self.draw_check = False
        width, height = get_text_size(self.text)
        print "size", width, height
        self.set_size_request(width + 8, height + 8)        
        # init events.
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.connect("button-press-event", self.select_button_button_press_event)
        self.connect("button-release-event", self.select_button_button_release_event)
        self.connect("expose-event", self.select_button_expose_event)        

    def select_button_button_press_event(self, widget, event):
        widget.grab_add()

    def select_button_button_release_event(self, widget, event):
        widget.grab_remove()
        
    def select_button_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        # 
        if widget.state == gtk.STATE_PRELIGHT:
            print "select_button_expose_event........"
            # draw rectangle.
            cr.set_source_rgb(*color_hex_to_cairo(self.bg_color))
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.fill()
            cr.set_line_width(1)
            cr.set_source_rgb(*color_hex_to_cairo(self.line_color))
            cr.rectangle(rect.x + 2,
                         rect.y + 2, 
                         rect.width - 4, 
                         rect.height - 4)
            cr.stroke()            
        # draw text.
        draw_text(cr, self.text,
                  rect.x + 5,
                  rect.y + rect.height/2 - get_text_size(self.text)[1]/2,
                  text_size=8, 
                  text_color="#000000")        
        return True


