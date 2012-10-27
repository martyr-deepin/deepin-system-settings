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
    "deepin-power-settings", 
    "1.0",
    "01",
    os.path.join(get_parent_dir(__file__), "skin"),
    os.path.join(get_parent_dir(__file__), "app_theme"),
    )

import pango
import os
import math
import dtk_cairo_blur
from dtk.ui.config import Config
from dtk.ui.label import Label
from dtk.ui.constant import COLOR_NAME_DICT, DEFAULT_FONT_SIZE
from dtk.ui.theme import ui_theme
from dtk.ui.draw import draw_window_frame, draw_pixbuf, draw_text
from dtk.ui.utils import alpha_color_hex_to_cairo, get_optimum_pixbuf_from_file, cairo_disable_antialias, color_hex_to_cairo, cairo_state
import cairo
import gobject
import gtk

class PowerView(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)
        self.label_padding_x = 10
        self.label_padding_y = 10
       
        self.power_button_config_label = Label("电源按钮设置")
        self.power_button_config_align = gtk.Alignment()
        self.power_button_config_align.set(0.0, 0.5, 0, 0)
        self.power_button_config_align.set_padding(self.label_padding_y, self.label_padding_y, self.label_padding_x, 0)
        self.power_save_config_label = Label("电源节能设置")
        self.power_save_config_align = gtk.Alignment()
        self.power_save_config_align.set(0.0, 0.5, 0, 0)
        self.power_save_config_align.set_padding(self.label_padding_y, self.label_padding_y, self.label_padding_x, 0)
        
        self.power_button_config_align.add(self.power_button_config_label)
        self.pack_start(self.power_button_config_align, False, False)
        self.power_save_config_align.add(self.power_save_config_label)
        self.pack_start(self.power_save_config_align, False, False)

gobject.type_register(PowerView)        
