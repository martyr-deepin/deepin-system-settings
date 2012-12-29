#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
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

from dtk.ui.utils import color_hex_to_cairo
from dtk.ui.label import Label
import gobject
import gtk
from constant import *
    
class FootBox(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)

        self.__is_init_ui = False
        

    def __init_ui(self):
        self.align = self.__setup_align()
        self.box = gtk.HBox()
        self.notice_label = self.__setup_label("DEBUG")
        self.box.pack_start(self.notice_label, False, False)
        self.align.add(self.box)
        self.pack_start(self.align)

        self.__is_init_ui = True

    def hide(self):
        self.hide_all()

    def show(self):
        if not self.__is_init_ui:
            self.__init_ui()
        
        self.show_all()
    
    def __expose(self, widget, event):
        cr = widget.window.cairo_create()                                       
        rect = widget.allocation                                                
        
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                     
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)                       
        cr.fill()
    
    def __setup_align(self, 
                      padding_top=5, 
                      padding_bottom=5, 
                      padding_left=5,
                      padding_right=5):
        align = gtk.Alignment()
        align.set(0, 0, 0, 0)
        align.set_padding(padding_top, 
                          padding_bottom, 
                          padding_left, 
                          padding_right)
        align.connect("expose-event", self.__expose)
        return align

    def __setup_label(self, 
                      text="", 
                      text_size=CONTENT_FONT_SIZE, 
                      label_width=600, 
                      wrap_width=None):
        label = Label(text = text, 
                      text_size = text_size, 
                      label_width = label_width, 
                      wrap_width = wrap_width)
        return label

gobject.type_register(FootBox)
