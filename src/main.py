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

def start_module_process(slider, content_page, module_path, module_config):
    print "start module process"
    
    module_id = module_config.get("main", "id")
    if content_page.module_id != module_id:
        content_page.module_id = module_id
        slider.slide_to(content_page)
        
        subprocess.Popen("python %s" % (os.path.join(module_path, module_config.get("main", "program"))), shell=True)
            
if __name__ == "__main__":
    # Init application.
    application = Application()

    # Set application default size.
    application.set_default_size(846, 547)
    application.window.set_resizable(False)

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
    
    # Init action bar.
    action_bar = ActionBar()
    
    # Init slider.
    slider = Slider(default_index=1)
    
    # Init search page.
    search_page = SearchPage()
    
    # Init content page.
    content_page = ContentPage()
    
    # Init navigate page.
    navigate_page = NavigatePage(lambda path, config: start_module_process(slider, content_page, path, config))
    
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
    
    application.run()
