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
import dbus
import dbus.service
import gtk
from theme_view import ThemeView
from theme_setting_view import ThemeSettingView
from dtk.ui.slider import Slider

def send_plug_id(plug):
    if bus.request_name(app_dbus_name) != dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
        bus_object = bus.get_object(app_dbus_name, app_object_name)
        method = bus_object.get_dbus_method("receive_plug_id")
        method(plug.get_id())
            
def switch_setting_view(slider, theme_setting_view, theme):
    slider.slide_to(theme_setting_view)
    theme_setting_view.set_theme(theme)
        
if __name__ == "__main__":
    # WARING: only use once in one process
    DBusGMainLoop(set_as_default=True) 
    
    # Init dbus.
    bus = dbus.SessionBus()
    app_dbus_name = "com.deepin.system_settings"
    app_object_name = "/com/deepin/system_settings"
    
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
    plug.connect("destroy", lambda w: gtk.main_quit())
    plug.connect("realize", send_plug_id)    
    plug.connect("realize", lambda w: slider.set_widget(theme_view))
    
    # Show.
    plug.show_all()
    
    gtk.main()
