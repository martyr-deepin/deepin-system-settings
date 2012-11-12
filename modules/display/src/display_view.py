#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2012 Zhai Xiang
# 
# Author:     Zhai Xiang <zhaixiang@linuxdeepin.com>
# Maintainer: Zhai Xiang <zhaixiang@linuxdeepin.com>
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
    os.path.join(get_parent_dir(__file__, 2), "skin"),
    os.path.join(get_parent_dir(__file__, 2), "app_theme"),
    )

from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
from dtk.ui.button import ToggleButton
from dtk.ui.constant import DEFAULT_FONT_SIZE, ALIGN_START, ALIGN_END
from dtk.ui.utils import get_optimum_pixbuf_from_file
import gobject
import gtk

class DisplayView(gtk.VBox):
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

    def m_setup_label(self, text="", align=ALIGN_END):
        label = Label(text, None, DEFAULT_FONT_SIZE, align, 140)
        return label

    def m_setup_combo(self, items=[]):
        combo = ComboBox(items, None, 0, 120)
        return combo

    '''
    temperary pixbuf I am not a designer :)
    '''
    def m_setup_toggle(self):
        toggle = ToggleButton(app_theme.get_pixbuf("inactive_normal.png"), 
            app_theme.get_pixbuf("active_normal.png"))
        return toggle

    def m_setup_align(self):
        align = gtk.Alignment()
        align.set(0.0, 0.5, 0, 0)
        align.set_padding(self.label_padding_y, self.label_padding_y, self.label_padding_x, 0)
        return align

    def m_widget_pack_start(self, parent_widget, widgets=[]):
        if parent_widget == None:
            return
        for item in widgets:
            parent_widget.pack_start(item, False, False)

gobject.type_register(DisplayView)        
