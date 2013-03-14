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

from dtk.ui.label import Label
from dtk.ui.utils import color_hex_to_cairo
from dtk.ui.draw import draw_line
from dtk.ui.constant import ALIGN_MIDDLE
from constant import *
import gtk
import gobject

class StatusBar(gtk.HBox):
    '''docstring for StatusBar'''
    def __init__(self):
        super(StatusBar, self).__init__(False)
        self.__count = 0
        self.__timeout_id = None
        self.text_label = Label("", text_x_align=ALIGN_MIDDLE,
                                label_width=500,
                                enable_select=False,
                                enable_double_click=False)
        text_align = gtk.Alignment()
        text_align.set(0.0, 0.5, 0.0, 0.0)
        text_align.add(self.text_label)

        self.button_hbox = gtk.HBox(False)
        self.button_hbox.set_spacing(WIDGET_SPACING)
        button_align = gtk.Alignment()
        button_align.set(1.0, 0.5, 0.0, 0.0)
        button_align.set_padding(0, 0, 0, 10)
        button_align.add(self.button_hbox)

        self.pack_start(text_align)
        self.pack_start(button_align)

        self.set_size_request(WINDOW_WIDTH, STATUS_HEIGHT)
        self.connect("expose-event", self.draw_background)

    def draw_background(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))
        cr.rectangle(x, y+1, w, h-1)
        cr.fill()

        cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
        draw_line(cr, x, y + 1, x + w, y + 1)

    def set_text(self, text):
        self.__count += 1
        if self.__timeout_id:
            gtk.timeout_remove(self.__timeout_id)
        self.text_label.set_text(text)
        self.__timeout_id = gobject.timeout_add(3000, self.hide_text)

    def hide_text(self):
        self.__count -= 1
        self.__timeout_id = None
        self.text_label.set_text("")

    def set_buttons(self, buttons):
        self.clear_button()
        for bt in buttons:
            self.button_hbox.pack_start(bt, False, False)
        self.show_all()

    def get_buttons(self):
        return self.button_hbox.get_children()

    def clear_button(self):
        self.button_hbox.foreach(self.button_hbox.remove)
        
gobject.type_register(StatusBar)
