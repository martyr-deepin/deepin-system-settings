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


from theme import app_theme
from dtk.ui.hscalebar import HScalebar
from dtk.ui.constant import DEFAULT_FONT, DEFAULT_FONT_SIZE
from dtk.ui.draw import draw_pixbuf, draw_text, draw_line
from dtk.ui.utils import (color_hex_to_cairo, get_content_size, cairo_state, cairo_disable_antialias)
import gtk

class MyHScalebar(HScalebar):
    def __init__(self, 
                 show_value=False,
                 show_value_type=gtk.POS_TOP,
                 show_point_num=0,
                 format_value="",
                 value_min = 0,
                 value_max = 100,  
                 line_height=6):
        super(MyHScalebar, self).__init__(
            show_value = show_value,
            show_value_type = show_value_type,
            show_point_num = show_point_num,
            format_value = format_value,
            value_min  = value_min ,
            value_max  = value_max ,
            line_height = line_height)

    def draw_bg_and_fg(self, cr, rect):    
        with cairo_disable_antialias(cr):
            '''
            background y
            '''
            x, y, w, h = rect         
            bg_x = rect.x + self.point_width/2
            bg_y = rect.y + rect.height/2 - self.line_height/2
            bg_w = rect.width - self.point_width
            cr.set_source_rgb(*color_hex_to_cairo(self.bg_inner2_color))
            cr.set_line_width(self.line_width)
            cr.rectangle(bg_x, 
                         bg_y, 
                         bg_w, 
                         self.line_height)
            cr.fill()
            
            cr.set_source_rgb(*color_hex_to_cairo(self.bg_side_color))
            cr.set_line_width(self.line_width)
            cr.rectangle(bg_x, bg_y, bg_w, self.line_height)
            cr.stroke()

            cr.set_source_rgb(*color_hex_to_cairo(self.bg_corner_color))
            cr.set_line_width(self.line_width)
            draw_line(cr, 
                      x + self.point_width / 2 + 1, 
                      bg_y, 
                      x + self.point_width / 2 + 2, 
                      bg_y)
            draw_line(cr, 
                      x + w - self.point_width / 2 - 1, 
                      bg_y, 
                      x + w - self.point_width / 2 - 2, 
                      bg_y)
            draw_line(cr, 
                      x + self.point_width / 2 + 1, 
                      bg_y + self.line_height, 
                      x + self.point_width / 2 + 2, 
                      bg_y + self.line_height)
            draw_line(cr, 
                      x + w - self.point_width / 2 - 1, 
                      bg_y + self.line_height, 
                      x + w - self.point_width / 2 - 2, 
                      bg_y + self.line_height)        
            
            if self.enable_check:
                fg_inner_color = self.fg_inner_color
                fg_side_color  = self.fg_side_color
                fg_corner_color = self.fg_corner_color
            else:
                fg_inner_color = self.bg_inner1_color 
                fg_side_color  = self.bg_side_color 
                fg_corner_color = self.bg_corner_color 
