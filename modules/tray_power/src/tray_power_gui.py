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
import sys
import os
from nls import _
from vtk.button import SelectButton 
from vtk.draw import draw_text
from vtk.utils import get_text_size
from vtk.theme import vtk_theme
from dtk.ui.line import HSeparator


LOAD_IMAGE_PATH = os.path.dirname(sys.argv[0]) 
HSEPARATOR_COLOR = [(0,   ("#777777", 0.0)),
                    (0.5, ("#000000", 0.3)),
                    (1,   ("#777777", 0.0))]


class PowerGui(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.hbox = gtk.HBox()
        # init top widgets.
        self.icon  = vtk_theme.name.get_image("power/power_icon.png") 
        self.label = gtk.Label(_("电源"))
        self.label.connect("expose-event", self.label_expose_event)
        self.hbox.pack_start(self.icon, False, False) 
        self.hbox.pack_start(self.label, False, False)
        # init mid widgets.
        self.top_line_ali = gtk.Alignment(1.0, 1.0, 1.0, 1.0)
        self.top_line_ali.set_padding(5, 5, 0, 0)
        self.top_line    = HSeparator(HSEPARATOR_COLOR, 0, 0) 
        self.top_line_ali.add(self.top_line)
        self.one_mode_btn  = SelectButton(_("平衡模式"), ali_padding=125)
        self.two_mode_btn  = SelectButton(_("节能模式"), ali_padding=125)
        self.tree_mode_btn  = SelectButton(_("高性能模式"), ali_padding=125)
        self.one_mode_btn.connect("clicked", self.one_mode_btn_clicked)
        self.two_mode_btn.connect("clicked", self.two_mode_btn_clicked)
        self.tree_mode_btn.connect("clicked", self.tree_mode_btn_clicked)
        mode_height = 25
        self.one_mode_btn.set_size_request(-1, mode_height)
        self.two_mode_btn.set_size_request(-1, mode_height)
        self.tree_mode_btn.set_size_request(-1, mode_height)
        # init bottom widgets
        self.bottom_line_ali = gtk.Alignment(1.0, 1.0, 1.0, 1.0)
        self.bottom_line_ali.set_padding(5, 5, 0, 0)
        self.bottom_line = HSeparator(HSEPARATOR_COLOR, 0, 0)
        self.bottom_line_ali.add(self.bottom_line)
        self.click_btn   = SelectButton("更多高级选项...", ali_padding=5)
        self.click_btn.set_size_request(-1, 25)
        # add all widgets.
        self.pack_start(self.hbox, False, False)
        self.pack_start(self.top_line_ali, False, False)
        self.pack_start(self.one_mode_btn, False, False)
        self.pack_start(self.two_mode_btn, False, False)
        self.pack_start(self.tree_mode_btn, False, False)
        self.pack_start(self.bottom_line_ali, False, False)
        self.pack_start(self.click_btn, False, False)

    def label_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        #
        draw_text(cr, widget.get_label(), rect.x + 5, rect.y, text_color="#000000")      
        #
        return True

    def one_mode_btn_clicked(self, widget):
        self.set_mode_bit(widget)

    def two_mode_btn_clicked(self, widget):
        self.set_mode_bit(widget)

    def tree_mode_btn_clicked(self, widget):
        self.set_mode_bit(widget)

    def set_mode_bit(self, widget):
        self.one_mode_btn.text_color = "#000000" 
        self.two_mode_btn.text_color = "#000000"
        self.tree_mode_btn.text_color = "#000000"
        self.one_mode_btn.queue_draw()
        self.two_mode_btn.queue_draw()
        self.tree_mode_btn.queue_draw()
        # set press color.
        widget.text_color = "#3da1f7"

