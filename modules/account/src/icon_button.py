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

from theme import app_theme
from dtk.ui.utils import color_hex_to_cairo
import gtk
import gobject

class IconButton(gtk.EventBox):
    '''docstring for IconButton'''
    __gsignals__ = {
        "del-pressed": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "pressed": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())}

    def __init__(self, pixbuf=None, image_path='', padding_x=2, padding_y=2, can_del=False):
        super(IconButton, self).__init__()
        self.connect("expose-event", self.__expose_cb)
        self.padding_x = padding_x
        self.padding_y = padding_y
        self.image_path = image_path
        self.can_del = can_del

        self.add_events(gtk.gdk.ENTER_NOTIFY_MASK)
        self.add_events(gtk.gdk.LEAVE_NOTIFY_MASK)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.add_events(gtk.gdk.BUTTON_RELEASE_MASK)

        self.connect("enter-notify-event", lambda w,e: self.set_state(gtk.STATE_PRELIGHT))
        self.connect("leave-notify-event", lambda w,e: self.set_state(gtk.STATE_NORMAL))
        self.connect("button-press-event", self.__on_button_press_cb)

        self.del_bg_pixbuf = app_theme.get_pixbuf("account/X_bg.png")
        self.del_fg_pixbuf = app_theme.get_pixbuf("account/X_fg.png")
        self.bg_offset_x = 0
        self.bg_offset_y = 0
        self.bg_width = 0
        self.bg_height = 0
        self.set_from_pixbuf(pixbuf)

    def __expose_cb(self, widget, event):
        ''' expose-event callback'''
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        if widget.get_state() == gtk.STATE_PRELIGHT:
            #cr.set_source_rgb(*color_hex_to_cairo(app_theme.get_color("globalHoverFill").get_color()))
            cr.set_source_rgb(*color_hex_to_cairo("#ddf3ff"))
            print "enter notify"
            cr.rectangle(*widget.allocation)
        else:
            cr.set_source_rgb(1, 1, 1)
            cr.rectangle(*widget.allocation)
        cr.fill()
        cr.paint()
        if self.pixbuf:
            cr.set_source_pixbuf(self.pixbuf, self.padding_x, self.padding_y)
            cr.paint()
        if self.can_del:
            bg_pixbuf = self.del_bg_pixbuf.get_pixbuf()
            fg_pixbuf = self.del_fg_pixbuf.get_pixbuf()
            cr.set_source_pixbuf(bg_pixbuf, self.bg_offset_x, self.bg_offset_y)
            cr.paint()
            cr.set_source_pixbuf(fg_pixbuf, self.fg_offset_x, self.fg_offset_y)
            cr.paint()
        return True
    
    def __on_button_press_cb(self, widget, event):
        x = event.x
        y = event.y
        if self.can_del and self.bg_offset_x <= x <= self.bg_offset_x + self.bg_width and\
                self.bg_offset_y <= y <= self.bg_offset_y + self.bg_height:
            self.emit("del-pressed")
        else:
            self.emit("pressed")

    def set_from_pixbuf(self, pixbuf):
        '''
        @param pixbuf: a gtk.gdk.Pixbuf object
        '''
        self.pixbuf = pixbuf
        if pixbuf:
            width = pixbuf.get_width()+2*self.padding_x
            height = pixbuf.get_height()+2*self.padding_y
            self.set_size_request(width, height)
            self.queue_draw()

            bg_pixbuf = self.del_bg_pixbuf.get_pixbuf()
            fg_pixbuf = self.del_fg_pixbuf.get_pixbuf()
            self.bg_width = w1 = bg_pixbuf.get_width()
            self.bg_height = h1 = bg_pixbuf.get_height()
            w2 = fg_pixbuf.get_width()
            h2 = fg_pixbuf.get_height()
            self.bg_offset_x = width - w1
            self.bg_offset_y = 0
            self.fg_offset_x = self.bg_offset_x + (w1 - w2) / 2
            self.fg_offset_y = self.bg_offset_y + (h1 - h2) / 2

    def get_image_path(self):
        return self.image_path
gobject.type_register(IconButton)
