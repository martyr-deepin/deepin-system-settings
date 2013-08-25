#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Deepin, Inc.
#               2011 Hou Shaohui
#
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou ShaoHui <houshao55@gmail.com>
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

import pango
import gtk
import pangocairo
import math

def get_font_families():
    '''Get all font families in system.'''
    fontmap = pangocairo.cairo_font_map_get_default()
    return sorted(map(lambda f: f.get_name(), fontmap.list_families()))
    
def create_right_align(paddings=None):    
    align = gtk.Alignment()
    if paddings:
        align.set_padding(*paddings)
    align.set(0, 0, 0, 1)
    return align
    
def create_left_align(paddings=None):
    align = gtk.Alignment()
    if paddings:
        align.set_padding(*paddings)
    align.set(0, 0, 1, 0)
    return align
    
def create_top_align(paddings=None):
    align = gtk.Alignment()
    if paddings:
        align.set_padding(*paddings)
    align.set(1, 0, 0, 0)
    return align

def create_bottom_align(paddings=None):
    align = gtk.Alignment()
    if paddings:
        align.set_padding(paddings=None)
    align.set(0, 1, 0, 0)
    return align

def set_widget_hcenter(widget):
    hbox = gtk.HBox()
    hbox.pack_start(create_right_align(), True, True)
    hbox.pack_start(widget, False, False)
    hbox.pack_start(create_left_align(), True, True)
    return hbox

def set_widget_vcenter(widget):
    vbox = gtk.VBox()
    vbox.pack_start(create_bottom_align(), True, True)
    vbox.pack_start(widget, False, True)
    vbox.pack_start(create_top_align(), True, True)
    return vbox

def set_widget_left(widget, paddings=None):
    hbox = gtk.HBox()
    hbox.pack_start(widget, False, False)
    hbox.pack_start(create_left_align(paddings), True, True)
    return hbox

def set_widget_right(widget, paddings=None):
    hbox = gtk.HBox()
    hbox.pack_start(create_right_align(paddings), True, True)
    hbox.pack_start(widget, False, False)    
    return hbox

def set_widget_resize(widget1, widget2, sizes1=(80, 22), sizes2=(175, 22), spacing=5):
    main_box = gtk.HBox(spacing=spacing)
    sub_box1 = gtk.HBox()
    sub_box1.set_size_request(*sizes1)
    sub_box1.add(set_widget_right(widget1))
    main_box.pack_start(sub_box1)
    
    sub_box = gtk.HBox()
    sub_box.set_size_request(*sizes2)
    sub_box.add(set_widget_left(widget2))
    main_box.pack_start(sub_box)
    return main_box
