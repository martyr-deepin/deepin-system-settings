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

import gtk
import gobject

class BlinkButton(gtk.EventBox):
    ''' '''
    def __init__(self, t=500):
        super(BlinkButton, self).__init__()
        self.__cursor_time = t
        self.__refresh = False
        self.connect("expose-event", self.__expose_cb)
        self.__blink = False
        gobject.timeout_add(self.__cursor_time/2, self.__timeout_cb)

    def __expose_cb(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(0, 0, w, h)
        cr.fill()
        if self.__blink:
            cr.set_source_rgb(0, 0, 0)
            cr.rectangle(0+w/2-1, 0, 1, h)
            cr.fill()
        return True

    def __timeout_cb(self):
        if self.window:
            self.__blink = not self.__blink
            self.queue_draw()
        if self.__refresh:
            self.__refresh = False
            gobject.timeout_add(self.__cursor_time/2, self.__timeout_cb)
            return False
        return True

    def update_time(self, t):
        self.__cursor_time = t
        self.__refresh = True
        

if __name__ == '__main__':
    win = gtk.Window()
    win.set_position(gtk.WIN_POS_CENTER)
    win.set_size_request(100, 30)
    win.connect("destroy", gtk.main_quit)
    
    blink = BlinkButton(1000)
    gobject.timeout_add(5000, lambda : blink.update_time(100))

    win.add(blink)
    win.show_all()
    gtk.main()
