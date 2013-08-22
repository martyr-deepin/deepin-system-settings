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
from dtk.ui.constant import ALIGN_START, ALIGN_END
from dtk.ui.line import HSeparator
from dtk.ui.box import ImageBox
from dtk.ui.label import Label
from dtk.ui.button import CheckButton, Button
from dtk.ui.combo import ComboBox
from module_frame import ModuleFrame
from grub_setting_utils import get_proper_resolutions
from nls import _

ALIGN_SPACING = 10

RESOLUTIONS = get_proper_resolutions()

class GrubSettings(object):
    def __init__(self, module_frame):
        super(GrubSettings, self).__init__()
        self.module_frame = module_frame
        
        self.__init_widgets()
        
    def __init_widgets(self):
        self.main_align = gtk.Alignment(0, 0, 1, 1)
        self.main_align.set_padding(TEXT_WINDOW_TOP_PADDING-25, 
                                    0, 
                                    TEXT_WINDOW_LEFT_PADDING-40, 
                                    TEXT_WINDOW_RIGHT_WIDGET_PADDING)
        self.main_vbox = gtk.VBox()
        self.main_vbox.set_spacing(ALIGN_SPACING)
        
        self.appearance_title_align = self.__setup_title_align(
            app_theme.get_pixbuf("desktop/icon.png"),
            _("Appearance Settings"),
            TEXT_WINDOW_TOP_PADDING,
            TEXT_WINDOW_LEFT_PADDING)
        
        self.customize_resolution_hbox = gtk.HBox()
        self.customize_resolution_check = self.__setup_checkbutton(_("Customize resolution:"), padding_x=2)
        self.customize_resolution_combo = self.__setup_combo(RESOLUTIONS)
        self.customize_resolution_hbox.pack_start(self.customize_resolution_check, True, True, 0)
        self.customize_resolution_hbox.pack_start(self.customize_resolution_combo, True, True, 0)
        self.customize_resolution_align = self.__setup_align()
        self.customize_resolution_align.add(self.customize_resolution_hbox)
        self.appearance_vbox = gtk.VBox()
        self.appearance_vbox.pack_start(self.customize_resolution_align, False, False, 0)
        
        self.main_vbox.pack_start(self.appearance_title_align, False, False, 0)
        self.main_vbox.pack_start(self.appearance_vbox, False, False, 0)
        self.module_frame.add(self.main_vbox)
        
    def __setup_checkbutton(self, label_text, padding_x=0):
        return CheckButton(label_text, padding_x)

    def __setup_button(self, label):
        return Button(label)

    def __setup_label(self, text="", text_size=CONTENT_FONT_SIZE, align=ALIGN_END):
        return Label(text, None, text_size, align, 200, False, False, False)

    def __setup_combo(self, items=[]):
        combo = ComboBox(items, None, 0, max_width = 285, fixed_width = 285)
        combo.set_size_request(-1, WIDGET_HEIGHT)
        return combo

    def __setup_toggle(self):
        return ToggleButton(app_theme.get_pixbuf("toggle_button/inactive_normal.png"),
            app_theme.get_pixbuf("toggle_button/active_normal.png"))

    def __setup_entry(self, content=""):
        entry = InputEntry(content)
        entry.set_size(215, WIDGET_HEIGHT)
        return entry

    def __setup_align(self,
                      padding_top=8,
                      padding_bottom=0,
                      padding_left=TEXT_WINDOW_LEFT_PADDING + IMG_WIDTH + WIDGET_SPACING,
                      padding_right=0):
        align = gtk.Alignment()
        align.set(0.0, 0.5, 0, 0)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        return align
    
    def __setup_title_label(self,
                            text="",
                            text_color=app_theme.get_color("globalTitleForeground"),
                            text_size=TITLE_FONT_SIZE,
                            text_x_align=ALIGN_START,
                            label_width=180):
        return Label(text = text,
                     text_color = text_color,
                     text_size = text_size,
                     text_x_align = text_x_align,
                     label_width = label_width,
                     enable_select = False,
                     enable_double_click = False)
    
    def __setup_separator(self):
        hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        hseparator.set_size_request(500, HSEPARATOR_HEIGHT)
        return hseparator
    
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

    def __widget_pack_start(self, parent_widget, widgets=[]):
        if parent_widget == None:
            return
        for item in widgets:
            parent_widget.pack_start(item, False, False)


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
