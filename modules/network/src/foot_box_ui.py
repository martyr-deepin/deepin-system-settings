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
from dtk.ui.button import Button
import style
from helper import Dispatcher
from timer import Timer
from nls import _
import pango
'''
signals set-button, set-tip
'''
class FootBox(gtk.HBox):
    def __init__(self):
        gtk.HBox.__init__(self)
        self.set_size_request(-1, 35)

        self.apply_method = None
        self.init_ui()

        self.timer = Timer(3000, self.__clear_tips)

        Dispatcher.connect("button-change", self.set_button)
        Dispatcher.connect("set-tip", self.set_tip)

    def expose_line(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        style.draw_out_line(cr, rect)

    def init_ui(self):
        self.tip_align = gtk.Alignment(0, 0.5, 0, 1)
        self.tip = Label("",
                         text_x_align=pango.ALIGN_CENTER,
                         label_width=500)
        self.tip_align.set_padding(5, 5, 20, 0)
        self.tip_align.add(self.tip)


        self.btn_delete = Button(_("Delete"))
        self.btn_delete.connect("clicked", self.delete_click)
        self.btn_delete.set_no_show_all(True)
        self.btn_save = Button()
        self.btn_save.connect("clicked", self.button_click)

        button_box = gtk.HBox(spacing=10)
        button_box.pack_start(self.btn_delete)
        button_box.pack_start(self.btn_save)

        self.buttons_align = gtk.Alignment(1, 0.5, 0, 0)
        self.buttons_align.set_padding(0, 0, 0, 10)
        self.buttons_align.add(button_box)
        self.pack(self, [self.tip_align], True, True)
        self.pack_end(self.buttons_align, False, False)
    
    def pack(self, parent, widgets, expand=False, fill=False):
        for widget in widgets:
            parent.pack_start(widget, expand, fill)

    def set_lock(self, state):
        self.__setting_module.set_lock(state)

    def get_lock(self):
        return self.__setting_module.get_lock()

    def set_button(self, widget, content, state):
        #print "DEBUG:set button", content, state, self.get_lock()

        self.__setting_module.set_button(content, state)
        self.btn_save.set_label(_("save"))

        if self.get_lock():
            self.btn_save.set_sensitive(False)
        else:
            if content == "apply":
                #self.btn_save.set_label(_("save"))
                self.btn_save.set_sensitive(False)
            else:
                
                #self.btn_save.set_label("save")
                self.btn_save.set_sensitive(state)

    def delete_click(self, widget):
        if self.focus_connection:
            Dispatcher.delete_setting(self.focus_connection)
            Dispatcher.to_main_page()

    def show_delete(self, connection):
        self.btn_delete.show()
        self.focus_connection = connection

    def hide_delete(self):
        self.btn_delete.hide()
        self.focus_connection = None
            

        #if content == "save":
            #if state and not self.get_lock():
                #Dispatcher.emit("setting-saved")
            #else:
                #self.btn_save.set_label(_("connect"))
                #self.btn_save.set_sensitive(False)
        #else:
            #self.btn_save.set_label(_("connect"))
            #self.btn_save.set_sensitive(True)

    def get_button(self):
        return self.__setting_module.get_button_state()

    def set_setting(self, module):
        self.__setting_module = module

    def button_click(self, widget):
        #if self.btn_save.label == "save":
        Dispatcher.emit("setting-saved")
        #elif self.btn_save.label == _("connect"):
            #Dispatcher.set_tip("setting saved")
            #Dispatcher.emit("setting-appled")

    def __clear_tips(self):
        self.tip.set_text("")

    def set_tip(self, widget, new_tip):
        self.tip.set_text(_("Tip:") + new_tip)
        self.timer.restart()
