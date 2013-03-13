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

from theme import app_theme
from dtk.ui.progressbar import ProgressBar
from dtk.ui.box import ImageBox
from dtk.ui.label import Label
from dtk.ui.button import Button
from dtk.ui.dialog import DialogBox
from dtk.ui.constant import ALIGN_START, ALIGN_MIDDLE, ALIGN_END
import gobject
import gtk
from constant import *
from nls import _

class BluetoothProgressDialog(DialogBox):                                                
    DIALOG_MASK_SINGLE_PAGE = 0                                                 
                                                                                
    def __init__(self, default_width=300, default_height=160, cancel_cb=None):
        DialogBox.__init__(self, "", default_width, default_height, self.DIALOG_MASK_SINGLE_PAGE)

        self.cancel_cb = cancel_cb                                              
        
        self.message_align = gtk.Alignment()
        self.message_align.set(0, 0, 0, 0)
        self.message_align.set_padding(0, 0, 10, 0)
        self.message_label = Label("")
        self.message_align.add(self.message_label)
        self.progress_align = gtk.Alignment()                                   
        self.progress_align.set(0, 0, 0, 0)                                     
        self.progress_align.set_padding(20, 0, 10, 10)                         
        self.progress_bar = ProgressBar()                                       
        self.progress_bar.set_size_request(default_width, -1)                   
        self.progress_align.add(self.progress_bar)                              
        self.percentage_align = gtk.Alignment()                                 
        self.percentage_align.set(0, 0, 0, 0)                                   
        self.percentage_align.set_padding(10, 0, 140, 0)                          
        self.percentage_label = Label("0%")          
        self.percentage_label.set_size_request(default_width, -1)               
        self.percentage_align.add(self.percentage_label)                        
        self.cancel_align = gtk.Alignment()                                     
        self.cancel_align.set(0, 0, 0, 0)                                       
        self.cancel_align.set_padding(20, 0, 200, 0)                            
        self.cancel_button = Button(_("Cancel"))                                
        self.cancel_button.set_size_request(70, WIDGET_HEIGHT)
        self.cancel_button.connect("clicked", self.__on_cancel_button_clicked)
        self.cancel_align.add(self.cancel_button)                               
                                        
        self.body_box.pack_start(self.message_align, False, False)
        self.body_box.pack_start(self.progress_align, False, False)             
        self.body_box.pack_start(self.percentage_align, False, False)           
        self.body_box.pack_start(self.cancel_align)

    def set_message(self, message):
        self.message_label.set_text(message)

    def set_progress(self, progress):
        self.progress_bar.progress_buffer.progress = progress
        self.percentage_label.set_text("%d" % progress + "%")

    def __on_cancel_button_clicked(self, widget):
        if self.cancel_cb:
            self.cancel_cb()
            self.destroy()
                                                                                
gobject.type_register(BluetoothProgressDialog)

class BluetoothReplyDialog(DialogBox):                                                
    DIALOG_MASK_SINGLE_PAGE = 0                                                 
                                                                                
    def __init__(self, message, default_width=300, default_height=140, is_succeed=True):
        DialogBox.__init__(self, "", default_width, default_height, self.DIALOG_MASK_SINGLE_PAGE)

        self.hbox = gtk.HBox()
        self.image_align = gtk.Alignment()
        self.image_align.set(0, 0, 0, 0)
        self.image_align.set_padding(0, 0, 20, 0)
        self.image_box = ImageBox(app_theme.get_pixbuf("bluetooth/succeed.png"))
        if not is_succeed:
            self.image_box = ImageBox(app_theme.get_pixbuf("bluetooth/failed.png"))
        self.image_align.add(self.image_box)
        self.message_align = gtk.Alignment()
        self.message_align.set(0, 0, 0, 0)
        self.message_align.set_padding(0, 0, 10, 0)
        self.message_label = Label(message, wrap_width = 200)
        self.message_align.add(self.message_label)
        self.hbox.pack_start(self.image_align)
        self.hbox.pack_start(self.message_align)
        self.confirm_align = gtk.Alignment()                                     
        self.confirm_align.set(0, 0, 0, 0)                                       
        self.confirm_align.set_padding(20, 0, 200, 0)                            
        self.confirm_button = Button(_("Ok"))                                
        self.confirm_button.set_size_request(70, WIDGET_HEIGHT)
        self.confirm_button.connect("clicked", lambda widget : self.destroy())
        self.confirm_align.add(self.confirm_button)

        self.body_box.pack_start(self.hbox, False, False)
        self.body_box.pack_start(self.confirm_align, False, False)

gobject.type_register(BluetoothReplyDialog)
