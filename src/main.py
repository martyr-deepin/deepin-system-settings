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

from theme import app_theme
from dtk.ui.application import Application
from dtk.ui.slider import Slider
from search_page import SearchPage
from content_page import ContentPage
from action_bar import ActionBar
from navigate_page import NavigatePage
import gtk
import subprocess
import os
from module_info import get_module_infos
from dbus.mainloop.glib import DBusGMainLoop
import dbus
import dbus.service

class DBusService(dbus.service.Object):
    def __init__(self, 
                 bus_name, 
                 app_dbus_name, 
                 app_object_name, 
                 content_page,
                 ):
        # Init dbus object.
        dbus.service.Object.__init__(self, bus_name, app_object_name)

        # Define DBus method.
        def message_receiver(self, *message):
            (message_type, message_content) = message
            if message_type == "send_plug_id":
                content_page.add_plug_id(message_content)
            else:
                print message
                    
        # Below code export dbus method dyanmically.
        # Don't use @dbus.service.method !
        setattr(DBusService, 
                'message_receiver', 
                dbus.service.method(app_dbus_name)(message_receiver))

def switch_page(index, label, slider, navigate_page):
    if index == 0 and label == "系统设置":
        slider.slide_to(navigate_page)
        
def add_crumb(index, label):
    print (index, label)
        
def start_module_process(slider, content_page, module_path, module_config):
    print "start module process"
    
    module_id = module_config.get("main", "id")
    if content_page.module_id != module_id:
        content_page.module_id = module_id
        slider.slide_to(content_page)
        
        subprocess.Popen("python %s" % (os.path.join(module_path, module_config.get("main", "program"))), shell=True)
            
if __name__ == "__main__":
    # WARING: only use once in one process
    DBusGMainLoop(set_as_default=True) 
    
    # Build DBus name.
    app_dbus_name = "com.deepin.system_settings"
    app_object_name = "/com/deepin/system_settings"
    app_bus_name = dbus.service.BusName(app_dbus_name, bus=dbus.SessionBus())
    
    # Init application.
    application = Application()

    # Set application default size.
    application.window.set_geometry_hints(
        None,
        846, 547,
        846, 547,
        )

    # Set application icon.
    application.set_icon(app_theme.get_pixbuf("icon.ico"))
    
    # Set application preview pixbuf.
    application.set_skin_preview(app_theme.get_pixbuf("frame.png"))
    
    # Add titlebar.
    application.add_titlebar(
        ["theme", "min", "close"], 
        app_theme.get_pixbuf("logo.png"), 
        None,
        "系统设置",
        )
    
    # Init main box.
    main_align = gtk.Alignment()
    main_align.set(0.5, 0.5, 1, 1)
    main_align.set_padding(0, 2, 2, 2)
    main_box = gtk.VBox()
    body_box = gtk.VBox()
    
    # Init module infos.
    module_infos = get_module_infos()
    
    # Init action bar.
    action_bar = ActionBar(module_infos, lambda bread, index, label: switch_page(index, label, slider, navigate_page))
    
    # Init slider.
    slider = Slider()
    
    # Init search page.
    search_page = SearchPage()
    
    # Init content page.
    content_page = ContentPage()
    
    # Init navigate page.
    navigate_page = NavigatePage(module_infos, lambda path, config: start_module_process(slider, content_page, path, config))
    
    # Append widgets to slider.
    slider.append_widget(search_page)
    slider.append_widget(navigate_page)
    slider.append_widget(content_page)
    search_page.set_size_request(834, 474)
    navigate_page.set_size_request(834, 474)
    content_page.set_size_request(834, 474)
    application.window.connect("realize", lambda w: slider.set_widget(navigate_page))
    
    # Connect widgets.
    body_box.pack_start(slider, True, True)
    main_box.pack_start(action_bar, False, False)
    main_box.pack_start(body_box, True, True)
    main_align.add(main_box)
    application.main_box.pack_start(main_align)
    
    # Start dbus service.
    DBusService(app_bus_name, app_dbus_name, app_object_name, content_page)
    
    application.run()
