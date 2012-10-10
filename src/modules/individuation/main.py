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

from dtk.ui.init_skin import init_skin
from dtk.ui.utils import get_parent_dir
import os
app_theme = init_skin(
    "deepin-individuation-settings", 
    "1.0",
    "01",
    os.path.join(get_parent_dir(__file__), "skin"),
    os.path.join(get_parent_dir(__file__), "app_theme"),
    )

from dbus.mainloop.glib import DBusGMainLoop
import dbus
import dbus.service
import gtk
from theme import ThemeView

def send_plug_id(plug):
    if bus.request_name(app_dbus_name) != dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
        bus_object = bus.get_object(app_dbus_name, app_object_name)
        method = bus_object.get_dbus_method("receive_plug_id")
        method(plug.get_id())
            
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
    
    # Init wallpaper box.
    theme_view = ThemeView()
    
    # Init window theme box.
    window_theme_box = gtk.VBox()
        
    # Connect widgets.
    plug.add(theme_view)

    # Handle signals.
    plug.connect("destroy", lambda w: gtk.main_quit())
    plug.connect("realize", send_plug_id)    
    
    # Show.
    plug.show_all()
    
    gtk.main()
