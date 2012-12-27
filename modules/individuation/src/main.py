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
from dtk.ui.utils import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from theme import app_theme

from dtk.ui.new_slider import HSlider
from theme_setting_view import ThemeSettingView
from theme_view import ThemeView
from module_frame import ModuleFrame
from constant import PAGE_WIDTH, PAGE_HEIGHT

if __name__ == "__main__":
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))
    
    # Init slider.
    slider = HSlider()
    
    # Init theme setting view.
    theme_setting_view = ThemeSettingView()
    
    def switch_setting_view(slider, theme_setting_view, theme):
        slider.slide_to_page(theme_setting_view, "right")
        theme_setting_view.set_theme(theme)
        
        module_frame.send_submodule_crumb(2, "主题设置")
    
    # Init theme view.
    theme_view = ThemeView(lambda theme: switch_setting_view(slider, theme_setting_view, theme))
    
    # Add widgets in slider.
    slider.append_page(theme_view)
    slider.append_page(theme_setting_view)
    theme_view.set_size_request(PAGE_WIDTH, PAGE_HEIGHT)
    theme_setting_view.set_size_request(PAGE_WIDTH, PAGE_HEIGHT)
        
    # Connect widgets.
    module_frame.add(slider)
    
    module_frame.connect("realize", lambda w: slider.set_to_page(theme_view))
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "click_crumb":
            (crumb_index, crumb_label) = message_content
            if crumb_index == 1:
                slider.slide_to_page(theme_view, "left")
        elif message_type == "show_again":
            slider.set_to_page(theme_view)
            module_frame.send_module_info()

    module_frame.module_message_handler = message_handler        
    
    module_frame.run()
