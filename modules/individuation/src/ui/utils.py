#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
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

import gtk
from dtk.ui.utils import (color_hex_to_cairo, container_remove_all,
                          cairo_disable_antialias, )
from dtk.ui.button import ToggleButton
from dtk.ui.line import HSeparator
from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
from theme import app_theme

def draw_single_mask(cr, x, y, width, height, color_name):
    if color_name.startswith("#"):
        color = color_name
    else:    
        color = app_theme.get_color(color_name).get_color()
    cairo_color = color_hex_to_cairo(color)
    cr.set_source_rgb(*cairo_color)
    cr.rectangle(x, y, width, height)
    cr.fill()
    
def switch_box(parent, widget):
    '''Switch tab 1.'''
    container_remove_all(parent)
    parent.add(widget)
    parent.show_all()
    
def draw_line(cr, start, end, color_name):
    if color_name.startswith("#"):
        color = color_name
    else:    
        color = app_theme.get_color(color_name).get_color()
    cairo_color = color_hex_to_cairo(color)        
    with cairo_disable_antialias(cr):
        cr.set_line_width(1)
        cr.set_source_rgb(*cairo_color)
        cr.move_to(*start)
        cr.rel_line_to(*end)
        cr.stroke()

def get_separator():
    hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
    # hseparator.set_size_request(500, 10)
    align = gtk.Alignment()
    align.set_padding(10, 10, 14, 0)
    align.set(0, 0, 1, 1)
    align.add(hseparator)
    return align
        
def get_togglebutton():
    toggle = ToggleButton(app_theme.get_pixbuf("toggle_button/inactive_normal.png"), 
                          app_theme.get_pixbuf("toggle_button/active_normal.png"), 
                          inactive_disable_dpixbuf = app_theme.get_pixbuf("toggle_button/inactive_normal.png"), 
                          active_disable_dpixbuf = app_theme.get_pixbuf("toggle_button/inactive_normal.png"))
    return toggle

def get_toggle_group(name, callback=None, active=True):    
    box = gtk.HBox(spacing = 8)
    title = Label(name)
    toggle_button = get_togglebutton()
    toggle_button.set_active(active)
    toggle_button_align = gtk.Alignment()
    toggle_button_align.set(0.5, 0.5, 0, 0)
    toggle_button_align.add(toggle_button)
    box.pack_start(title, False, False)
    box.pack_start(toggle_button_align, False, False)
    if callback:
        toggle_button.connect("toggled", callback)
    return (box, toggle_button) 

def get_combo_group(name, items, callback=None):
    box = gtk.HBox(spacing = 8)
    label = Label(name)
    combo_box = ComboBox(items)
    box.pack_start(label, False, False)
    box.pack_start(combo_box, False, False)
    
    if callback:
        combo_box.connect("item-selected", callback)
    return box, combo_box
