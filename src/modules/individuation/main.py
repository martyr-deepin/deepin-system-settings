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

from dbus.mainloop.glib import DBusGMainLoop
from dtk.ui.utils import is_dbus_name_exists
import dbus
import dbus.service
import gtk
from theme_view import ThemeView
from theme_setting_view import ThemeSettingView
from dtk.ui.slider import Slider
from dtk.ui.config import Config
from dtk.ui.utils import get_parent_dir
import os

class DBusService(dbus.service.Object):
    def __init__(self, 
                 bus_name, 
                 module_dbus_name, 
                 module_object_name, 
                 slider, 
                 theme_view
                 ):
        # Init dbus object.
        dbus.service.Object.__init__(self, bus_name, module_object_name)

        # Define DBus method.
        def message_receiver(self, *message):
            (message_type, message_content) = message
            if message_type == "click_crumb":
                (crumb_index, crumb_label) = message_content
                if crumb_index == 1:
                    slider.slide_to(theme_view)
            elif message_type == "show_again":
                slider.set_widget(theme_view)
                send_module_info()
                
        # Below code export dbus method dyanmically.
        # Don't use @dbus.service.method !
        setattr(DBusService, 
                'message_receiver', 
                dbus.service.method(module_dbus_name)(message_receiver))
        

def handle_dbus_reply(*reply):
    print "com.deepin.individuation_settings (reply): %s" % (str(reply))
    
def handle_dbus_error(*error):
    print "com.deepin.individuation_settings (error): %s" % (str(error))
    
def send_message(message_type, message_content):
    bus = dbus.SessionBus()
    if is_dbus_name_exists(app_dbus_name):
        bus_object = bus.get_object(app_dbus_name, app_object_name)
        method = bus_object.get_dbus_method("message_receiver")
        method(message_type, 
               message_content,
               reply_handler=handle_dbus_reply,
               error_handler=handle_dbus_error
               )
        
def send_plug_id(plug):
    send_message("send_plug_id", plug.get_id())
    
def send_module_info():
    config = Config(os.path.join(get_parent_dir(__file__), "config.ini"))
    config.load()
    send_message("send_module_info", 
                 (1, 
                  (config.get("main", "id"), config.get("name", "zh_CN"))
                  ))

def send_submodule_crumb(crumb_index, crumb_name):
    send_message("send_submodule_info", (crumb_index, crumb_name))
            
def switch_setting_view(slider, theme_setting_view, theme):
    slider.slide_to(theme_setting_view)
    theme_setting_view.set_theme(theme)
    
    send_submodule_crumb(2, "主题设置")
    
def module_exit(widget):
    print "module exit"
    
    gtk.main_quit()
    
if __name__ == "__main__":
    # WARING: only use once in one process
    DBusGMainLoop(set_as_default=True) 
    
    # Init dbus.
    bus = dbus.SessionBus()
    app_dbus_name = "com.deepin.system_settings"
    app_object_name = "/com/deepin/system_settings"
    
    # Init module dbus.
    module_dbus_name = "com.deepin.individuation_settings"
    module_object_name = "/com/deepin/individuation_settings"
    module_bus_name = dbus.service.BusName(module_dbus_name, bus=dbus.SessionBus())
    
    # Init threads.
    gtk.gdk.threads_init()

    # Init plug window.
    plug = gtk.Plug(0)
    
    # Init slider.
    slider = Slider()
    
    # Init theme setting view.
    theme_setting_view = ThemeSettingView()
    
    # Init theme view.
    theme_view = ThemeView(lambda theme: switch_setting_view(slider, theme_setting_view, theme))
    
    # Add widgets in slider.
    slider.append_widget(theme_view)
    slider.append_widget(theme_setting_view)
    theme_view.set_size_request(834, 474)
    theme_setting_view.set_size_request(834, 474)
        
    # Connect widgets.
    plug.add(slider)

    # Handle signals.
    plug.connect("destroy", module_exit)
    plug.connect("realize", send_plug_id)    
    plug.connect("realize", lambda w: send_module_info())    
    plug.connect("realize", lambda w: slider.set_widget(theme_view))
    
    # Start dbus service.
    DBusService(module_bus_name, module_dbus_name, module_object_name, slider, theme_view)
    
    # Show.
    plug.show_all()
    
    gtk.main()
