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

class IconButton(gtk.EventBox):
    '''docstring for IconButton'''
    def __init__(self, pixbuf=None, image_path='', padding_x=5, padding_y=5):
        super(IconButton, self).__init__()
        self.connect("expose-event", self.__expose_cb)
        self.padding_x = padding_x
        self.padding_y = padding_y
        self.image_path = image_path

        self.add_events(gtk.gdk.ENTER_NOTIFY_MASK)
        self.add_events(gtk.gdk.LEAVE_NOTIFY_MASK)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.add_events(gtk.gdk.BUTTON_RELEASE_MASK)

        self.connect("enter-notify-event", lambda w,e: self.set_state(gtk.STATE_PRELIGHT))
        self.connect("leave-notify-event", lambda w,e: self.set_state(gtk.STATE_NORMAL))
        self.set_from_pixbuf(pixbuf)

    def __expose_cb(self, widget, event):
        ''' expose-event callback'''
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        if widget.get_state() == gtk.STATE_PRELIGHT:
            cr.set_source_rgb(*color_hex_to_cairo(app_theme.get_color("globalHoverFill").get_color()))
            cr.rectangle(*widget.allocation)
        else:
            cr.set_source_rgb(1, 1, 1)
            cr.rectangle(*widget.allocation)
        cr.fill()
        cr.paint()
        if self.pixbuf:
            cr.set_source_pixbuf(self.pixbuf, self.padding_x, self.padding_y)
        cr.paint()
        return True
    
    def set_from_pixbuf(self, pixbuf):
        '''
        @param pixbuf: a gtk.gdk.Pixbuf object
        '''
        self.pixbuf = pixbuf
        if pixbuf:
            self.set_size_request(pixbuf.get_width()+2*self.padding_x,
                                  pixbuf.get_height()+2*self.padding_y)
            self.queue_draw()

    def get_image_path(self):
        return self.image_path
