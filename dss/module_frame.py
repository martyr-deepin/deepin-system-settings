#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
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
from constant import APP_DBUS_NAME, APP_OBJECT_NAME
from dtk.ui.config import Config
from dtk.ui.utils import is_dbus_name_exists
from dbus.mainloop.glib import DBusGMainLoop
import dbus
import dbus.service

class ModuleService(dbus.service.Object):
    def __init__(self, 
                 bus_name, 
                 module_dbus_name, 
                 module_object_name, 
                 message_handler
                 ):
        # Init dbus object.
        dbus.service.Object.__init__(self, bus_name, module_object_name)
                
        def wrap_message_handler(self, *a, **kw):
            message_handler(*a, **kw)
        
        # Below code export dbus method dyanmically.
        # Don't use @dbus.service.method !
        setattr(ModuleService, 
                'message_receiver', 
                dbus.service.method(module_dbus_name)(wrap_message_handler))

class ModuleFrame(gtk.Plug):
    '''
    class docs
    '''
	
    def __init__(self, module_config_path):
        '''
        init docs
        '''
        gtk.Plug.__init__(self, 0)
        self.module_config_path = module_config_path
        self.module_config = Config(self.module_config_path)
        self.module_config.load()
        self.module_id = self.module_config.get("main", "id")
        
        # WARING: only use once in one process
        DBusGMainLoop(set_as_default=True) 
        
        # Init threads.
        gtk.gdk.threads_init()
    
        # Init dbus.
        self.bus = dbus.SessionBus()
        
        # Init module dbus.
        self.module_dbus_name = "com.deepin.%s_settings" % (self.module_id)
        self.module_object_name = "/com/deepin/%s_settings" % (self.module_id)
        self.module_bus_name = dbus.service.BusName(
            self.module_dbus_name, 
            bus=self.bus)
        
        # Handle signals.
        self.connect("realize", self.module_frame_realize)
        self.connect("destroy", self.module_frame_exit)
        
    def run(self):    
        if not hasattr(self, "module_message_handler"):
            raise Exception, "Please customize your own module_message_handler for module_frame"
        
        # Start dbus service.
        ModuleService(self.module_bus_name, 
                      self.module_dbus_name, 
                      self.module_object_name,
                      self.module_message_handler)
        
        # Show.
        self.show_all()
        
        gtk.main()
        
    def module_frame_realize(self, widget):
        self.send_module_info()
        self.send_plug_id()
        
    def module_frame_exit(self, widget):
        print "%s module exit" % (self.module_id)
        
        gtk.main_quit()
        
    def send_message(self, message_type, message_content):    
        if is_dbus_name_exists(APP_DBUS_NAME):
            bus_object = self.bus.get_object(APP_DBUS_NAME, APP_OBJECT_NAME)
            method = bus_object.get_dbus_method("message_receiver")
            method(message_type, 
                   message_content,
                   reply_handler=self.handle_dbus_reply,
                   error_handler=self.handle_dbus_error
                   )
            
    def handle_dbus_reply(self, *reply):
        print "%s (reply): %s" % (self.module_dbus_name, str(reply))
        
    def handle_dbus_error(self, *error):
        print "%s (error): %s" % (self.module_dbus_name, str(error))
    
    def send_plug_id(self):
        self.send_message("send_plug_id", (self.module_id, self.get_id()))
        
    def send_module_info(self):
        self.send_message("send_module_info", 
                          (1, 
                           (self.module_config.get("main", "id"), 
                            self.module_config.get("name", "zh_CN"))
                           ))
        
    def send_submodule_crumb(self, crumb_index, crumb_name):
        self.send_message("send_submodule_info", (crumb_index, crumb_name))

gobject.type_register(ModuleFrame)
