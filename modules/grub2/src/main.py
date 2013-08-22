#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang YaoHua
# 
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
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
from deepin_utils.file import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from theme import app_theme

import gtk
from constant import *
from dtk.ui.label import Label
from module_frame import ModuleFrame

class GrubSettings(object):
    def __init__(self, module_frame):
        super(GrubSettings, self).__init__()
        self.module_frame = module_frame
        
        self.__init_widgets()
        
    def __init_widgets(self):
        label = Label("Hello")
        self.module_frame.add(label)
        
        
    def __setup_title_align(self,
                            pixbuf,
                            text,
                            padding_top=FRAME_TOP_PADDING,
                            padding_left=TEXT_WINDOW_LEFT_PADDING):
        align = self.__setup_align(padding_top = padding_top, padding_left = padding_left)
        align_box = gtk.VBox(spacing = WIDGET_SPACING)
        title_box = gtk.HBox(spacing = WIDGET_SPACING)
        image = ImageBox(pixbuf)
        label = self.__setup_title_label(text)
        separator = self.__setup_separator()
        self.__widget_pack_start(title_box, [image, label])
        self.__widget_pack_start(align_box, [title_box, separator])
        align.add(align_box)
        return align


if __name__ == "__main__":
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))
    GrubSettings(module_frame)
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            module_frame.send_module_info()
        elif message_type == "exit":
            module_frame.exit()

    module_frame.module_message_handler = message_handler        
    module_frame.run()
