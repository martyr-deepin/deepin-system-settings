#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
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

from dtk.ui.label import Label
from dtk.ui.button import OffButton
from dtk.ui.line import HSeparator
from dtk.ui.hscalebar import HScalebar
from dtk.ui.box import ImageBox
from nls import _
from constant import *

import gtk

class TrayGui(gtk.VBox):
    '''sound tray gui'''
    def __init__(self):
        super(TrayGui, self).__init__(False)

        hbox = gtk.HBox(False)
        hbox.set_spacing(WIDGET_SPACING)
        hseparator = HSeparator([(0, ("#FFFFFF", 1.0), (1, ("#FFFFFF", 1.0)))], 0, 0)
        hseparator.set_size_request(150, 10)
        hbox.pack_start(self.__make_align(Label(_("Device"))), False, False)
        hbox.pack_start(self.__make_align(hseparator), False, False)
        self.pack_start(hbox, False, False)

        hbox = gtk.HBox(False)
        hbox.set_spacing(WIDGET_SPACING)
        speaker_img = ImageBox(app_theme.get_pixbuf("sound/speaker-3.png"))
        speaker_scale = HScalebar(show_value=True, format_value="%", value_min=0, value_max=150)
        speaker_mute_button = OffButton()
        hbox.pack_start(self.__make_align(speaker_img), False, False)
        hbox.pack_start(self.__make_align(speaker_scale))
        hbox.pack_start(self.__make_align(speaker_mute_button), False, False)
        self.pack_start(hbox, False, False)

        hbox = gtk.HBox(False)
        hbox.set_spacing(WIDGET_SPACING)
        microphone_img = ImageBox(app_theme.get_pixbuf("sound/microphone.png"))
        microphone_scale = HScalebar(show_value=True, format_value="%", value_min=0, value_max=150)
        microphone_mute_button = OffButton()
        hbox.pack_start(self.__make_align(microphone_img), False, False)
        hbox.pack_start(self.__make_align(microphone_scale))
        hbox.pack_start(self.__make_align(microphone_mute_button), False, False)
        self.pack_start(hbox, False, False)

        self.pack_start(self.__make_align(HSeparator([(0, ("#FFFFFF", 1.0), (1, ("#FFFFFF", 1.0)))], 0, 0)), False, False)
        self.pack_start(self.__make_align(Label(_("更多高级选项..."))), False, False)

        self.set_size_request(240, 150)
        
    def __make_align(self, widget=None, xalign=1.0, yalign=0.5, xscale=0.0,
                     yscale=0.0, padding_top=0, padding_bottom=0, padding_left=0,
                     padding_right=0, height=CONTAINNER_HEIGHT):
        align = gtk.Alignment()
        align.set_size_request(-1, height)
        align.set(xalign, yalign, xscale, yscale)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        if widget:
            align.add(widget)
        return align
