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

from tray_sound_gui import TrayGui
import gtk

def stream_changed_cb(widget, win):
    #print "height:", widget.get_widget_height()
    #win.set_allocation((0, 0, 220, widget.get_widget_height()))
    win.set_size_request(220, widget.get_widget_height())
    win.reshow_with_initial_size()
    print win.get_allocation(), widget.stream_num
    print "-------------------"

if __name__ == '__main__':
    win = gtk.Window()
    win.connect("destroy", gtk.main_quit)
    #win.set_size_request(220, 170)
    win.set_default_size(220, 170)
    tray = TrayGui()
    #tray.connect("stream-changed", lambda w: win.set_size_request(220, tray.get_widget_height()))
    tray.connect("stream-changed", stream_changed_cb, win)

    win.add(tray)
    win.show_all()
    gtk.main()
