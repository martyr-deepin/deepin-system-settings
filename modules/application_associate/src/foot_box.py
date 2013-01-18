#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Zeng Zhi
# 
# Author:     Zeng Zhi <zengzhilg@gmail.com>
# Maintainer: Zeng Zhi <zengzhilg@gmail.com>
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
from dtk.ui.label import Label
import style
class FootBox(gtk.HBox):

    def __init__(self, adjustment=10):
        gtk.HBox.__init__(self)
        self.set_size_request(-1, 35)
        self.adjustment = adjustment
        self.init_ui()

    def expose_line(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        style.draw_out_line(cr, rect)

    def init_ui(self):
        self.tip_align = gtk.Alignment(0, 0.5, 0, 1)
        self.tip = Label("")
        self.tip_align.set_padding(5, 5, 20, 0)
        self.tip_align.add(self.tip)

        self.button_box = gtk.HBox(spacing=4)
        self.buttons_align = gtk.Alignment(1, 0.5, 0, 0)
        self.buttons_align.set_padding(0, 0, 0, self.adjustment)
        self.buttons_align.add(self.button_box)
        
        self.pack(self, [self.tip_align], True, True)
        self.pack_end(self.buttons_align, False, False)
    
    def pack(self, parent, widgets, expand=False, fill=False):
        for widget in widgets:
            parent.pack_start(widget, expand, fill)

    def set_buttons(self, buttons_list):
        width = 0
        for button in buttons_list:
            width += button.get_size_request()[0]
        self.button_box.set_size_request(width, -1)
        self.pack(self.button_box, buttons_list)
        self.queue_draw()

    def set_tip(self, new_tip):
        self.tip.set_text(new_tip)
