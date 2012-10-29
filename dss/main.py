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

from constant import APP_DBUS_NAME, APP_OBJECT_NAME
from theme import app_theme
from dtk.ui.application import Application
from dtk.ui.new_slider import HSlider
from dtk.ui.breadcrumb import Crumb
from dtk.ui.utils import is_dbus_name_exists
from search_page import SearchPage
from content_page import ContentPageInfo
from action_bar import ActionBar
from navigate_page import NavigatePage
import gtk
import subprocess
import os
from module_info import get_module_infos
from dbus.mainloop.glib import DBusGMainLoop
import dbus
import dbus.service
import dbus
import dbus.service

class DBusService(dbus.service.Object):
    def __init__(self, 
                 action_bar,
                 content_page_info,
                 ):
        # Init dbus object.
        bus_name = dbus.service.BusName(APP_DBUS_NAME, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, APP_OBJECT_NAME)

        # Define DBus method.
        def message_receiver(self, *message):
            (message_type, message_content) = message
            if message_type == "send_plug_id":
                (module_id, plug_id) = message_content
                print (module_id, plug_id)
                content_page = content_page_info.get_content_page(module_id)
                content_page.add_plug_id(plug_id)
            elif message_type == "send_module_info":
                (crumb_index, (module_id, crumb_name)) = message_content
                action_bar.bread.add(Crumb(crumb_name, None))
            elif message_type == "send_submodule_info":
                (crumb_index, crumb_name) = message_content
                action_bar.bread.add(Crumb(crumb_name, None))
            else:
                print message
                    
        # Below code export dbus method dyanmically.
        # Don't use @dbus.service.method !
        setattr(DBusService, 
                'message_receiver', 
                dbus.service.method(APP_DBUS_NAME)(message_receiver))
        
def handle_dbus_reply(*reply):
    print "com.deepin.system_settings (reply): %s" % (str(reply))
    
def handle_dbus_error(*error):
    print "com.deepin.system_settings (error): %s" % (str(error))
        
def send_message(module_id, message_type, message_content):
    bus = dbus.SessionBus()
    module_dbus_name = "com.deepin.%s_settings" % (module_id)
    module_object_name = "/com/deepin/%s_settings" % (module_id)
    if is_dbus_name_exists(module_dbus_name):
        bus_object = bus.get_object(module_dbus_name, module_object_name)
        method = bus_object.get_dbus_method("message_receiver")
        method(message_type, 
               message_content,
               reply_handler=handle_dbus_reply,
               error_handler=handle_dbus_error
               )
        
def switch_page(bread, content_page_info, index, label, slider, navigate_page):
    if index == 0:
        if label == "系统设置":
            slider.slide_to_page(navigate_page, "left")
    else:
        send_message(content_page_info.get_active_module_id(),
                     "click_crumb",
                     (index, label))
        
def click_module_menu_item(slider, content_page_info, action_bar, module_info):
    if module_info.id != content_page_info.get_active_module_id():
        action_bar.bread.remove_node_after_index(0)
        start_module_process(slider, content_page_info, module_info.path, module_info.config)
        
def add_crumb(index, label):
    print (index, label)
        
def start_module_process(slider, content_page_info, module_path, module_config):
    module_id = module_config.get("main", "id")
    content_page = content_page_info.get_content_page(module_id)
    content_page_info.set_active_module_id(module_id)
    
    slider.slide_to_page(content_page, "right")
    
    module_dbus_name = "com.deepin.%s_settings" % (module_id)
    if not is_dbus_name_exists(module_dbus_name):
        subprocess.Popen("python %s" % (os.path.join(module_path, module_config.get("main", "program"))), shell=True)
    else:
        send_message(module_id, "show_again", "")
            
if __name__ == "__main__":
    # WARING: only use once in one process
    DBusGMainLoop(set_as_default=True) 
    
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
    module_dict = {}
    for module_info_list in module_infos:
        for module_info in module_info_list:
            module_dict[module_info.id] = module_info
    
    # Init action bar.
    action_bar = ActionBar(module_infos, 
                           lambda bread, index, label: switch_page(bread, content_page_info, index, label, slider, navigate_page),
                           lambda module_info: click_module_menu_item(slider, content_page_info, action_bar, module_info))
    
    # Init slider.
    slider = HSlider()
    
    # Init search page.
    search_page = SearchPage()
    
    # Init navigate page.
    navigate_page = NavigatePage(module_infos, lambda path, config: start_module_process(slider, content_page_info, path, config))
    
    # Append widgets to slider.
    slider.append_page(search_page)
    slider.append_page(navigate_page)
    application.window.connect("realize", lambda w: slider.set_to_page(navigate_page))
    
    # Init content page info.
    content_page_info = ContentPageInfo(slider)
    
    for module_info_list in module_infos:
        for module_info in module_info_list:
            content_page_info.create_content_page(module_info.id)
    
    # Connect widgets.
    body_box.pack_start(slider, True, True)
    main_box.pack_start(action_bar, False, False)
    main_box.pack_start(body_box, True, True)
    main_align.add(main_box)
    application.main_box.pack_start(main_align)
    
    # Start dbus service.
    DBusService(action_bar, content_page_info)
    
    application.run()
