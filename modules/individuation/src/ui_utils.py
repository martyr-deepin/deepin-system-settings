#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
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

from dtk.ui.utils import (color_hex_to_cairo, container_remove_all,
                          cairo_disable_antialias, )
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
    
