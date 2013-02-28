#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Deepin, Inc.
#               2013 Zhai Xiang
# 
# Author:     Zhai Xiang <zhaixiang@linuxdeepin.com>
# Maintainer: Zhai Xiang <zhaixiang@linuxdeepin.com>
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

from dtk.ui.draw import draw_line
from dtk.ui.utils import color_hex_to_cairo
from dtk.ui.label import Label
from dtk.ui.constant import ALIGN_MIDDLE
import gtk
import gobject
from constant import TITLE_FONT_SIZE, CONTENT_FONT_SIZE, TREEVIEW_BORDER_COLOR
from theme import app_theme

class StatusBox(gtk.HBox):
    def __init__(self, width=800):
        gtk.HBox.__init__(self)

        self.width = width
        
        self.status_label = Label(text = "",                                     
                                  text_size = CONTENT_FONT_SIZE,                    
                                  text_x_align = ALIGN_MIDDLE,                      
                                  label_width = 600,                                
                                  enable_select = False)

        self.set_size_request(self.width, -1)
        self.pack_start(self.status_label, False, False)

        self.connect("expose-event", self.__expose)

    def hide_status(self):
        self.status_label.set_text("")

    def set_status(self, text):
        self.status_label.set_text(text)
        gobject.timeout_add(3000, self.hide_status)

    def __expose(self, widget, event):
        cr = widget.window.cairo_create()                                       
        rect = widget.allocation                                                
                                                                                
        cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))           
        draw_line(cr, rect.x, rect.y + 1, rect.x + self.width, rect.y + 1)

gobject.type_register(StatusBox)
