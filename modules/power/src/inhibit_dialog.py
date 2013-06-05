#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Changjin
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

from tray_shutdown_gui import Gui
from tray_dialog import InhibitDialog
import gtk
import sys

if __name__ == '__main__':
    gui = Gui()
    action = {
        #'switch': (None, None),
        'logout': (gui.cmd_dbus.logout, 1),
        'suspend': (gui.cmd_dbus.suspend, None),
        #'hibernate': (None, None),
        'shutdown': (gui.cmd_dbus.new_stop, None),
        'reboot': (gui.cmd_dbus.new_restart, None),
    }
    if len(sys.argv) < 2 or sys.argv[1] not in action:
        exit()

    def dialog_hide(widget):
        gtk.timeout_add(5, widget.destroy)

    dialog = InhibitDialog()
    dialog.connect("hide", dialog_hide)
    dialog.connect("destroy", lambda w : gtk.main_quit())

    dialog.set_bg_pixbuf(gtk.gdk.pixbuf_new_from_file('/usr/share/deepin-system-tray/src/image/on_off_dialog/deepin_on_off_bg.png'))
    dialog.show_pixbuf = gtk.gdk.pixbuf_new_from_file('/usr/share/deepin-system-tray/src/image/on_off_dialog/deepin_hibernate.png')
    dialog.show_image.set_from_pixbuf(dialog.show_pixbuf)

    dialog.show_dialog()
    dialog.run_exec = action[sys.argv[1]][0]
    dialog.argv = action[sys.argv[1]][1]
    dialog.show_all()

    gtk.main()
