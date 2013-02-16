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

import gobject
import dbus
import dbus.service
import dbus.mainloop.glib
import gtk
from dtk.ui.constant import ALIGN_MIDDLE
from dtk.ui.label import Label
from dtk.ui.button import Button
from dtk.ui.dialog import DIALOG_MASK_SINGLE_PAGE, DialogBox
from constant import *

class AgentDialog(DialogBox):                                                 
    def __init__(self,                                                          
                 title,                                                         
                 message,                                                       
                 default_width=400,                                             
                 default_height=220,                                            
                 confirm_callback=None,                                         
                 cancel_callback=None, 
                 confirm_button_text="Yes", 
                 cancel_button_text="No"):                                         
        DialogBox.__init__(self, "", default_width, default_height, DIALOG_MASK_SINGLE_PAGE)
        self.confirm_callback = confirm_callback                                
        self.cancel_callback = cancel_callback                                  
                                  
        self.title_align = gtk.Alignment()
        self.title_align.set(0, 0, 0, 0)
        self.title_align.set_padding(0, 0, FRAME_LEFT_PADDING, 8)
        self.title_label = Label(title, wrap_width=300)

        self.label_align = gtk.Alignment()                                      
        self.label_align.set(0.5, 0.5, 0, 0)                                    
        self.label_align.set_padding(0, 0, 8, 8)                                
        self.label = Label(message, text_x_align=ALIGN_MIDDLE, text_size=55)   
                                                                                
        self.confirm_button = Button(confirm_button_text)                                   
        self.cancel_button = Button(cancel_button_text)                                
                                                                                
        self.confirm_button.connect("clicked", lambda w: self.click_confirm_button())
        self.cancel_button.connect("clicked", lambda w: self.click_cancel_button())
        
        self.body_box.pack_start(self.title_align, False, False)
        self.title_align.add(self.title_label)
        self.body_box.pack_start(self.label_align, True, True)                  
        self.label_align.add(self.label)                                        
                                                                                
        self.right_button_box.set_buttons([self.cancel_button, self.confirm_button])

    def click_confirm_button(self):                                             
        if self.confirm_callback != None:                                       
            self.confirm_callback()                                             
                                                                                
        self.destroy()                                                          
                                                                                
    def click_cancel_button(self):                                              
        if self.cancel_callback != None:                                        
            self.cancel_callback()                                              
                                                                                
        self.destroy()                                                          
                                                                                
gobject.type_register(AgentDialog)

class Rejected(dbus.DBusException):
    _dbus_error_name = "org.bluez.Error.Rejected"

class Agent(dbus.service.Object):
	
    def __init__(self, 
                 path = "/org/bluez/agent", 
                 gui = False, 
                 message_text = "Please confirm", 
                 confirm_text = "Yes", 
                 cancel_text = "No", 
                 bus = None):
        self.gui = gui
        self.message_text = message_text
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        
        if bus is None:
	    bus = dbus.SystemBus()    
    
        dbus.service.Object.__init__(self, bus, path)	
    
        self.exit_on_release = True
    
    def set_exit_on_release(self, exit_on_release):
        self.exit_on_release = exit_on_release

    def __request_confirmed(self):
        return

    def __request_canceled(self):
        print "Passkey doesn't match"
        return

    @dbus.service.method("org.bluez.Agent", in_signature="", out_signature="")
    def Release(self):
        if self.exit_on_release:
	   mainloop.quit()
    
    @dbus.service.method("org.bluez.Agent", in_signature="os", out_signature="")
    def Authorize(self, device_path, uuid):
        print "Authorize (%s, %s)" % (device_path, uuid)
        authorize = raw_input("Authorize connection (yes/no): ")
        if (authorize == "yes"):
            return
        raise Rejected("Connection rejected by user")
    
    @dbus.service.method("org.bluez.Agent", in_signature="o", out_signature="s")
    def RequestPinCode(self, device_path):
        print "RequestPinCode (%s)" % (device_path)
        return raw_input("Enter PIN Code: ")
    
    @dbus.service.method("org.bluez.Agent", in_signature="o", out_signature="u")
    def RequestPasskey(self, device_path):
        print "RequestPasskey (%s)" % (device_path)
        passkey = raw_input("Enter passkey: ")
        return dbus.UInt32(passkey)
    
    @dbus.service.method("org.bluez.Agent", in_signature="oub", out_signature="")
    def DisplayPasskey(self, device_path, passkey, entered):
	print "DisplayPasskey (%s, %d)" % (device_path, passkey, entered)
    
    @dbus.service.method("org.bluez.Agent", in_signature="ou", out_signature="")
    def RequestConfirmation(self, device_path, passkey):
        print "RequestConfirmation (%s, %d)" % (device_path, passkey)
        if self.gui:
            dlg = AgentDialog(self.message_text, 
                              str(passkey), 
                              confirm_button_text = self.confirm_text, 
                              cancel_button_text = self.cancel_text)
            dlg.show_all()
            return
        else:
            confirm = raw_input("Confirm passkey (yes/no): ")
            if (confirm == "yes"):
                return
            raise Rejected("Passkey doesn't match")
    
    @dbus.service.method("org.bluez.Agent", in_signature="s", out_signature="")
    def ConfirmModeChange(self, mode):
        print "ConfirmModeChange (%s)" % (mode)
        authorize = raw_input("Authorize mode change (yes/no): ")
        if (authorize == "yes"):
	   return
        raise Rejected("Mode change by user")
    
    @dbus.service.method("org.bluez.Agent", in_signature="", out_signature="")
    def Cancel(self):
    	print "Cancel"

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    path = "/test/agent"

    agent = Agent(path, bus)
    mainloop = gobject.MainLoop()
    mainloop.run()
