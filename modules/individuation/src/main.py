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


import sys
import os
import gtk
import shutil
from deepin_utils.file import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))

from dtk.ui.slider import HSlider
from ui.local_page import MainBox
from module_frame import ModuleFrame
from constant import PAGE_WIDTH, PAGE_HEIGHT
from helper import event_manager
from theme_manager import theme_manager
from xdg_support import get_images_dir, get_download_wallpaper_dir
from nls import _

class DeepinIndividuation(object):
    
    config_file = os.path.join(get_parent_dir(__file__, 2), "config.ini")
    
    def __init__(self):
        
        # Init theme datas.
        self.__init_data()
        argv = ""
        for theme in theme_manager.get_user_themes() + theme_manager.get_system_themes():
            argv += theme.get_name() + ";"
        self.module_frame = ModuleFrame(self.config_file, argv)
        
        # Init slider.
        self.slider = HSlider()
    
        self.all_page = MainBox()
    
        # Add widgets in slider.
        self.all_page.set_size_request(PAGE_WIDTH, PAGE_HEIGHT)
        
        # Connect events.
        event_manager.add_callback("add-local-wallpapers", self.add_local_wallpappers)
        
        # Connect widgets.
        self.module_frame.add(self.slider)
        self.module_frame.connect("realize", lambda w: self.slider.set_to_page(self.all_page))
        self.module_frame.module_message_handler = self.message_handler
        self.module_frame.run()        

    def add_local_wallpappers(self, name, obj, theme):
        d = gtk.FileChooserDialog(
                "Choose Pictures",
                None,
                gtk.FILE_CHOOSER_ACTION_OPEN,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                 gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT)
                )
        d.set_select_multiple(True)
        d.set_current_folder(get_images_dir())
        pic_filter = gtk.FileFilter()
        pic_filter.set_name(_("Image files"))
        pic_filter.add_mime_type("image/*")
        d.add_filter(pic_filter)
        response = d.run()
        if(response == gtk.RESPONSE_ACCEPT):
            filenames = d.get_filenames()
            wallpapper_path = get_download_wallpaper_dir()
            for name in filenames:
                shutil.copy2(name, wallpapper_path)
        d.destroy()

    def __init_data(self):
        theme_manager.load()
        theme_manager.untitled_theme(theme_manager.get_default_theme())
    
    def message_handler(self, *message):
        (message_type, message_content) = message
        if message_type == "click_crumb":
            (crumb_index, crumb_label) = message_content
                
        elif message_type == "show_again":
            self.module_frame.send_module_info()

        elif message_type == "switch-theme":
            theme = None

            for item in theme_manager.get_user_themes() + theme_manager.get_system_themes():
                if item.get_name() == message_content:
                    theme = item
                    break

            if theme:
                print "DEBUG", theme
                event_manager.emit("theme-detail", theme)

        elif message_type == "exit":
            self.module_frame.exit()

if __name__ == "__main__":
    DeepinIndividuation()
