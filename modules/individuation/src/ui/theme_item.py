#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hou Shaohui
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
import cairo
import pango
import gobject
import math
import dtk_cairo_blur

from dtk.ui.constant import COLOR_NAME_DICT, DEFAULT_FONT_SIZE
from dtk.ui.theme import ui_theme
from dtk.ui.draw import draw_window_frame, draw_pixbuf, draw_text
from dtk.ui.utils import (alpha_color_hex_to_cairo, get_optimum_pixbuf_from_file,
                          cairo_disable_antialias, color_hex_to_cairo, cairo_state,
                          is_in_rect)

from theme import app_theme
from constant import CONTENT_FONT_SIZE

class ThemeItem(gobject.GObject):
    '''
    Icon item.
    '''
	
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    
    ITEM_WIDTH = 180
    ITEM_HEIGHT = 185
    
    def __init__(self, theme):
        '''
        Initialize ItemIcon class.
        
        @param pixbuf: Icon pixbuf.
        '''
        gobject.GObject.__init__(self)
        self.theme = theme
        self.name = self.theme.get_name()
        self.hover_flag = False
        self.highlight_flag = False
        self.pixbufs = []
        self.wallpaper_offset_x = 55
        self.wallpaper_offset_y = 20
        self.wallpaper_width = 100
        self.wallpaper_height = 75
        self.wallpaper_render_offset = 15
        self.wallpaper_frame_size = 4
        self.window_frame_padding_x = 40
        self.window_frame_padding_y = 100
        self.window_frame_width = 48
        self.window_frame_height = 48
        self.reflection_height = 23
        self.title_padding_y = 10
        self.title_size = CONTENT_FONT_SIZE
        
        self.hover_offset = 5
        self.hover_stroke_dcolor = app_theme.get_color("globalHoverStroke")
        self.hover_fill_dcolor = app_theme.get_color("globalHoverFill")
        self.highlight_fill_color = "#7db7f2"
        self.highlight_stroke_color = "#396497"
        self.hover_response_rect = gtk.gdk.Rectangle(
            self.hover_offset, self.hover_offset, 
            self.ITEM_WIDTH - self.hover_offset * 2, 
            self.ITEM_HEIGHT - self.hover_offset * 2) 
    
    def rename_theme(self, name):
        self.name = name
        self.theme.reload()
        self.emit_redraw_request()

    def emit_redraw_request(self):
        '''
        Emit `redraw-request` signal.
        
        This is IconView interface, you should implement it.
        '''
        self.emit("redraw-request")
        
    def get_width(self):
        '''
        Get item width.
        
        This is IconView interface, you should implement it.
        '''
        return self.ITEM_WIDTH
        
    def get_height(self):
        '''
        Get item height.
        
        This is IconView interface, you should implement it.
        '''
        return self.ITEM_HEIGHT
    
    def render(self, cr, rect):
        '''
        Render item.
        
        This is IconView interface, you should implement it.
        
        '''
        
        # Draw background.
        if self.highlight_flag:                
            with cairo_disable_antialias(cr):
                cr.set_source_rgb(*color_hex_to_cairo(self.highlight_fill_color))
                cr.rectangle(rect.x + self.hover_offset, 
                             rect.y + self.hover_offset, 
                             rect.width - self.hover_offset * 2, 
                             rect.height - self.hover_offset * 2)
                cr.fill_preserve()
                cr.set_line_width(1)
                cr.set_source_rgb(*color_hex_to_cairo(self.highlight_stroke_color))
                cr.stroke()
        
        elif self.hover_flag:
            with cairo_disable_antialias(cr):
                cr.set_source_rgb(*color_hex_to_cairo(self.hover_fill_dcolor.get_color()))
                cr.rectangle(rect.x + self.hover_offset, 
                             rect.y + self.hover_offset, 
                             rect.width - self.hover_offset * 2, 
                             rect.height - self.hover_offset * 2)
                cr.fill_preserve()
                cr.set_line_width(1)
                cr.set_source_rgb(*color_hex_to_cairo(self.hover_stroke_dcolor.get_color()))
                cr.stroke()
                

                
        # Draw wallpapers.
        if self.pixbufs == []:
            wallpaper_paths = self.theme.get_wallpaper_paths()
            wallpaper_count = len(wallpaper_paths)
            for wallpaper_file in wallpaper_paths[wallpaper_count - 3:wallpaper_count]:
                self.pixbufs.append(get_optimum_pixbuf_from_file(wallpaper_file, self.wallpaper_width, self.wallpaper_height))
                
        theme_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, rect.width, rect.height)   
        theme_surface_cr = gtk.gdk.CairoContext(cairo.Context(theme_surface))
        
        with cairo_state(theme_surface_cr):
            reflection_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 
                                                    self.wallpaper_width + self.wallpaper_frame_size * 2 + 2, 
                                                    self.reflection_height)
            
            reflection_surface_cr = gtk.gdk.CairoContext(cairo.Context(reflection_surface))
            wallpaper_x = self.wallpaper_offset_x
            wallpaper_y = self.wallpaper_offset_y
        
            for (index, pixbuf) in enumerate(self.pixbufs):
                wallpaper_draw_x = wallpaper_x - 3 * self.wallpaper_render_offset + \
                    (len(self.pixbufs) - index) * self.wallpaper_render_offset
                wallpaper_draw_y = wallpaper_y + 3 * self.wallpaper_render_offset - \
                    (len(self.pixbufs) - index) * self.wallpaper_render_offset
                
                self.render_wallpaper(theme_surface_cr, pixbuf, wallpaper_draw_x, wallpaper_draw_y)
                
                if index == len(self.pixbufs) - 1:
                    self.render_wallpaper(reflection_surface_cr, 
                                          pixbuf, 
                                          self.wallpaper_frame_size + 1, 
                                          self.wallpaper_frame_size + 1,
                                          True)
                    
                    i = 0
                    while (i <= self.reflection_height):
                        with cairo_state(theme_surface_cr):
                            theme_surface_cr.rectangle(
                                wallpaper_draw_x - self.wallpaper_frame_size - 1, 
                                wallpaper_draw_y + self.wallpaper_height + self.wallpaper_frame_size + i,
                                self.wallpaper_width + self.wallpaper_frame_size * 2 + 2,
                                1)
                            theme_surface_cr.clip()
                            theme_surface_cr.set_source_surface(
                                reflection_surface, 
                                wallpaper_draw_x - self.wallpaper_frame_size - 1, 
                                wallpaper_draw_y + self.wallpaper_frame_size + self.wallpaper_height
                                )
                            theme_surface_cr.paint_with_alpha(1.0 - (math.sin(i * math.pi / 2 / self.reflection_height)))
                        i += 1    
            
        # Paint wallpapers.
        cr.set_source_surface(theme_surface, rect.x, rect.y)                
        cr.paint()
        
        # Init window coordiante.
        window_frame_x = rect.x + self.window_frame_padding_x
        window_frame_y = rect.y + self.window_frame_padding_y
        
        # Paint gaussian area.
        '''
        gaussian_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.window_frame_width, self.window_frame_height)   
        gaussian_surface_cr = gtk.gdk.CairoContext(cairo.Context(gaussian_surface))
        gaussian_surface_cr.set_source_surface(theme_surface, -self.window_frame_padding_x, -self.window_frame_padding_y)
        gaussian_surface_cr.paint()
        dtk_cairo_blur.gaussian_blur(gaussian_surface, 3)
        cr.set_source_surface(gaussian_surface, window_frame_x, window_frame_y)
        cr.paint()
        '''

        # Draw window frame.
        '''
        cr.set_source_rgba(*alpha_color_hex_to_cairo((COLOR_NAME_DICT[self.theme.get_color()], 0.5)))
        cr.rectangle(window_frame_x + 1, window_frame_y, self.window_frame_width - 2, 1)
        cr.rectangle(window_frame_x, window_frame_y + 1, self.window_frame_width, self.window_frame_height - 2)
        cr.rectangle(window_frame_x + 1, window_frame_y + self.window_frame_height - 1, self.window_frame_width - 2, 1) 
        cr.fill()
        
        draw_window_frame(cr, window_frame_x, window_frame_y, self.window_frame_width, self.window_frame_height,
                          ui_theme.get_alpha_color("window_frame_outside_1"),
                          ui_theme.get_alpha_color("window_frame_outside_2"),
                          ui_theme.get_alpha_color("window_frame_outside_3"),
                          ui_theme.get_alpha_color("window_frame_inside_1"),
                          ui_theme.get_alpha_color("window_frame_inside_2"),
                          )
        '''

        draw_text(cr, 
                  self.name, 
                  rect.x, 
                  rect.y + self.window_frame_padding_y + self.window_frame_height + self.title_padding_y, 
                  rect.width,
                  DEFAULT_FONT_SIZE,
                  self.title_size,
                  alignment=pango.ALIGN_CENTER
                  )
        
    def render_wallpaper(self, cr, pixbuf, wallpaper_draw_x, wallpaper_draw_y, reflection=False):    
        cr.set_source_rgba(1, 1, 1, 1)
        cr.rectangle(wallpaper_draw_x - self.wallpaper_frame_size,
                     wallpaper_draw_y - self.wallpaper_frame_size,
                     self.wallpaper_width + self.wallpaper_frame_size * 2,
                     self.wallpaper_height + self.wallpaper_frame_size * 2)
        cr.fill()
        
        with cairo_disable_antialias(cr):
            cr.set_line_width(1)
            cr.set_source_rgb(*color_hex_to_cairo("#A4A7A7"))
            
            cr.rectangle(wallpaper_draw_x - self.wallpaper_frame_size,
                         wallpaper_draw_y - self.wallpaper_frame_size,
                         self.wallpaper_width + self.wallpaper_frame_size * 2 + 1,
                         self.wallpaper_height + self.wallpaper_frame_size * 2 + 1)
            cr.stroke()

            cr.rectangle(wallpaper_draw_x,
                         wallpaper_draw_y,
                         self.wallpaper_width + 1,
                         self.wallpaper_height + 1)
            cr.stroke()
        
        if reflection:
            cr.translate(wallpaper_draw_x - self.wallpaper_frame_size - 1,
                         wallpaper_draw_y + self.wallpaper_height + self.wallpaper_frame_size + 1)
            cr.scale(1, -1)
        
        draw_pixbuf(cr, pixbuf, wallpaper_draw_x, wallpaper_draw_y)
        
    def icon_item_motion_notify(self, x, y):
        '''
        Handle `motion-notify-event` signal.
        
        This is IconView interface, you should implement it.
        '''
        if is_in_rect((x, y), (self.hover_response_rect.x,
                               self.hover_response_rect.y,
                               self.hover_response_rect.width,
                               self.hover_response_rect.height)):
            self.hover_flag = True
        else:    
            self.hover_flag = False
        
        self.emit_redraw_request()
        
    def icon_item_lost_focus(self):
        '''
        Lost focus.
        
        This is IconView interface, you should implement it.
        '''
        self.hover_flag = False
        
        self.emit_redraw_request()
        
    def icon_item_highlight(self):
        '''
        Highlight item.
        
        This is IconView interface, you should implement it.
        '''
        self.highlight_flag = True

        self.emit_redraw_request()
        
    def icon_item_normal(self):
        '''
        Set item with normal status.
        
        This is IconView interface, you should implement it.
        '''
        self.highlight_flag = False
        
        self.emit_redraw_request()
    
    def icon_item_button_press(self, x, y):
        '''
        Handle button-press event.
        
        This is IconView interface, you should implement it.
        '''
        pass        
    
    def icon_item_button_release(self, x, y):
        '''
        Handle button-release event.
        
        This is IconView interface, you should implement it.
        '''
        pass
    
    def icon_item_single_click(self, x, y):
        '''
        Handle single click event.
        
        This is IconView interface, you should implement it.
        '''
        pass

    def icon_item_double_click(self, x, y):
        '''
        Handle double click event.
        
        This is IconView interface, you should implement it.
        '''
        pass
    
    def icon_item_release_resource(self):
        '''
        Release item resource.

        If you have pixbuf in item, you should release memory resource like below code:

        >>> del self.pixbuf
        >>> self.pixbuf = None

        This is IconView interface, you should implement it.
        
        @return: Return True if do release work, otherwise return False.
        
        When this function return True, IconView will call function gc.collect() to release object to release memory.
        '''
        for pixbuf in self.pixbufs:
            del pixbuf
        self.pixbufs = []    
        
        # Return True to tell IconView call gc.collect() to release memory resource.
        return True
        
gobject.type_register(ThemeItem)
