#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
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
import sys
import dbus
import dbus.service
import dbus.mainloop.glib
from dtk.ui.dialog import DialogBox
from dtk.ui.progressbar import ProgressBar
from dtk.ui.label import Label
from dtk.ui.button import Button
from dtk.ui.constant import ALIGN_MIDDLE
from nls import _
from constant import *

class ProgressDialog(DialogBox):                                                
    DIALOG_MASK_SINGLE_PAGE = 0                                                 
                                                                                
    def __init__(self, title, default_width=300, default_height=130, cancel_cb=None):
        DialogBox.__init__(self, title, default_width, default_height, self.DIALOG_MASK_SINGLE_PAGE)
                                                                                
        self.cancel_cb = cancel_cb                                              
                                                                                
        self.progress_align = gtk.Alignment()                                   
        self.progress_align.set(0, 0, 0, 0)                                     
        self.progress_align.set_padding(10, 10, 10, 10)                         
        self.progress_bar = ProgressBar()                                       
        self.progress_bar.set_size_request(default_width, -1)                   
        self.progress_align.add(self.progress_bar)                              
        self.percentage_align = gtk.Alignment()                                 
        self.percentage_align.set(0, 0, 0, 0)                                   
        self.percentage_align.set_padding(0, 10, 0, 0)                          
        self.percentage_label = Label("0%", text_x_align=ALIGN_MIDDLE)          
        self.percentage_label.set_size_request(default_width, -1)               
        self.percentage_align.add(self.percentage_label)                        
        self.cancel_align = gtk.Alignment()                                     
        self.cancel_align.set(0, 0, 0, 0)                                       
        self.cancel_align.set_padding(20, 0, 200, 0)                            
        self.cancel_button = Button(_("Cancel"))                                
        self.cancel_button.set_size_request(70, WIDGET_HEIGHT)
        self.cancel_align.add(self.cancel_button)                               
                                                                                
        self.body_box.pack_start(self.progress_align, False, False)             
        self.body_box.pack_start(self.percentage_align, False, False)           
        self.body_box.pack_start(self.cancel_align)                             
                                                                                
gobject.type_register(ProgressDialog)

class GuiObexAgent(dbus.service.Object):
    def __init__(self, conn=None, obj_path=None):
        dbus.service.Object.__init__(self, conn, obj_path)

        self.progress_dialog = ProgressDialog(_("Send File"))

    @dbus.service.method("org.openobex.Agent",
                    in_signature="o", out_signature="s")
    def Request(self, path):
        self.progress_dialog.show_all()
        print "Transfer started"
        transfer = dbus.Interface(bus.get_object("org.openobex.client",
                    path), "org.openobex.Transfer")
        print "DEBUG transfer"
        properties = transfer.GetProperties()
        for key in properties.keys():
            print "  %s = %s" % (key, properties[key])
        return ""

    @dbus.service.method("org.openobex.Agent",
                    in_signature="ot", out_signature="")
    def Progress(self, path, transferred):
        print "Transfer progress (%d bytes)" % (transferred)
        return

    @dbus.service.method("org.openobex.Agent",
                    in_signature="o", out_signature="")
    def Complete(self, path):
        print "Transfer finished"
        self.progress_dialog.destroy()
        return

    @dbus.service.method("org.openobex.Agent",
                    in_signature="os", out_signature="")
    def Error(self, path, error):
        print "Transfer finished with an error: %s" % (error)
        return

    @dbus.service.method("org.openobex.Agent",
                    in_signature="", out_signature="")
    def Release(self):
        mainloop.quit()
        return

def send_file(address, filename):
    print "send file"
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SessionBus()

    client = dbus.Interface(bus.get_object("org.openobex.client", "/"),         
                            "org.openobex.Client")                              
                                 
    path = "/org/bluez/agent/sendto"                                            
    agent = GuiObexAgent(bus, path)                                                
    print "before mainloop" 
    mainloop = gobject.MainLoop()
    print "after mainloop"
    client.SendFiles({ "Destination": address }, filename, path)
    print "gui_obex_agent"
    mainloop.run()
