#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
#             Zhai Xiang <zhaixiang83@gmail.com>
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
import random
import gobject
from math import radians
import time
import os
from dtk.ui.utils import (get_optimum_pixbuf_from_file, cairo_disable_antialias,
                          run_command, is_in_rect, color_hex_to_cairo, 
                          get_content_size, cairo_state)
from dtk.ui.draw import draw_pixbuf, draw_shadow, draw_text
from dtk.ui.threads import post_gui
from dtk.ui.thread_pool import MissionThread
from theme import app_theme
from cache_manager import SMALL_SIZE, cache_manager
from helper import event_manager
import common
import deepin_gsettings
from nls import _

ITEM_PADDING_X = 20
ITEM_PADDING_Y = 10

class WallpaperItem(gobject.GObject):
    '''
    Icon item.
    '''
	
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    
    def __init__(self, path, readonly, theme):
        '''
        Initialize ItemIcon class.
        
        @param pixbuf: Icon pixbuf.
        '''
        gobject.GObject.__init__(self)

        self.background_settings = deepin_gsettings.new("com.deepin.dde.background")

        self.image_path = path
        self.readonly = readonly
        self.theme = theme
        self.pixbuf = None
        self.hover_flag = False
        self.highlight_flag = False
        self.wallpaper_width = SMALL_SIZE["x"]
        self.wallpaper_height = SMALL_SIZE["y"]
        self.width = self.wallpaper_width + ITEM_PADDING_X * 2
        self.height = self.wallpaper_height + ITEM_PADDING_Y * 2
        
        self.is_hover = False
        self.hover_stroke_dcolor = app_theme.get_color("globalHoverStroke")
        self.hover_response_rect = gtk.gdk.Rectangle(
            ITEM_PADDING_X, ITEM_PADDING_Y ,
            self.wallpaper_width, self.wallpaper_height
            ) 
        
        self.tick_normal_dpixbuf = app_theme.get_pixbuf("individuation/tick_normal.png")
        self.tick_gray_dpixbuf = app_theme.get_pixbuf("individuation/tick_gray.png")

        self.cross_normal_dpixbuf = app_theme.get_pixbuf("individuation/cross_normal.png")
        self.cross_gray_dpixbuf = app_theme.get_pixbuf("individuation/cross_gray.png")
        
        if readonly:
            self.is_tick = self.theme.get_system_wallpaper_status(path)
        else:    
            if self.theme == None:
                self.is_tick = False
            else:
                self.is_tick = self.theme.get_user_wallpaper_status(path)
            
        self.tick_area = None
        
    def do_apply_wallpaper(self):
        self.background_settings.set_string("picture-uri", "file://" + self.image_path)

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
        return self.width
        
    def get_height(self):
        '''
        Get item height.
        
        This is IconView interface, you should implement it.
        '''
        return self.height
    
    def render(self, cr, rect):
        '''
        Render item.
        
        This is IconView interface, you should implement it.
        '''
        # Init.
        if self.pixbuf == None:
            self.pixbuf = get_optimum_pixbuf_from_file(self.image_path, self.wallpaper_width, self.wallpaper_height)
            
        wallpaper_x = rect.x + (rect.width - self.wallpaper_width) / 2
        wallpaper_y = rect.y + (rect.height - self.wallpaper_height) / 2
        
        # Draw shadow.
        drop_shadow_padding = 7
        drop_shadow_radious = 7
        draw_shadow(
            cr,
            wallpaper_x,
            wallpaper_y,
            self.wallpaper_width + drop_shadow_padding,
            self.wallpaper_height + drop_shadow_padding,
            drop_shadow_radious,
            app_theme.get_shadow_color("window_shadow")
            )

        outside_shadow_padding = 4
        outside_shadow_radious = 5
        draw_shadow(
            cr,
            wallpaper_x - outside_shadow_padding,
            wallpaper_y - outside_shadow_padding,
            self.wallpaper_width + outside_shadow_padding * 2,
            self.wallpaper_height + outside_shadow_padding * 2,
            outside_shadow_radious,
            app_theme.get_shadow_color("window_shadow")
            )
        
        # Draw wallpaper.
        draw_pixbuf(cr, self.pixbuf, wallpaper_x, wallpaper_y)    
        
        # Draw wallpaper frame.
        with cairo_disable_antialias(cr):
            cr.set_line_width(2)
            cr.set_source_rgba(1, 1, 1, 1)
            cr.rectangle(wallpaper_x, wallpaper_y, self.wallpaper_width, self.wallpaper_height)
            cr.stroke()
            
        if self.is_hover:    
            cr.rectangle(wallpaper_x, wallpaper_y, self.wallpaper_width, self.wallpaper_height)
            cr.set_source_rgb(*color_hex_to_cairo(self.hover_stroke_dcolor.get_color()))
            cr.stroke()
            
        if self.is_tick:    
            tick_pixbuf = self.tick_normal_dpixbuf.get_pixbuf()
        else:    
            tick_pixbuf = self.tick_gray_dpixbuf.get_pixbuf()
            
        tick_x = wallpaper_x + self.wallpaper_width - tick_pixbuf.get_width() / 2 
        tick_y = wallpaper_y - tick_pixbuf.get_height() / 2
        if self.tick_area is None:
            self.tick_area = gtk.gdk.Rectangle(
                tick_x - rect.x,
                tick_y - rect.y,
                tick_pixbuf.get_width(),
                tick_pixbuf.get_height())
            
        if self.is_tick:    
            draw_pixbuf(cr, tick_pixbuf, tick_x, tick_y)
        else:
            draw_pixbuf(cr, self.tick_gray_dpixbuf.get_pixbuf(), tick_x, tick_y)    
                
    def tick(self):            
        self.is_tick = True
        self.set_theme_tick(self.is_tick)
        self.emit_redraw_request()
        
    def untick(self):    
        self.is_tick = False
        self.set_theme_tick(self.is_tick)
        self.emit_redraw_request()
        
    def toggle_tick(self):    
        self.is_tick = not self.is_tick
        self.set_theme_tick(self.is_tick)
        self.emit_redraw_request()
        
    def set_theme_tick(self, value):    
        if self.readonly:
            self.theme.set_system_wallpaper_status(self.image_path, value)
        else:    
            if self.theme == None:
                return

            self.theme.set_user_wallpaper_status(self.image_path, value)
        
    def icon_item_motion_notify(self, x, y):
        '''
        Handle `motion-notify-event` signal.
        
        This is IconView interface, you should implement it.
        '''
        if is_in_rect((x, y), (self.hover_response_rect.x,
                               self.hover_response_rect.y,
                               self.hover_response_rect.width,
                               self.hover_response_rect.height)):
            self.is_hover = True
            
        else:    
            self.is_hover = False
            
        self.emit_redraw_request()    
            
        
    def icon_item_lost_focus(self):
        '''
        Lost focus.
        
        This is IconView interface, you should implement it.
        '''
        
        self.is_hover = False
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
        self.toggle_tick()                                                      
        event_manager.emit("select-wallpaper", self)

    def icon_item_double_click(self, x, y):
        '''
        Handle double click event.
        
        This is IconView interface, you should implement it.
        '''
        self.is_tick = True
        self.emit_redraw_request()
        self.do_apply_wallpaper()

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
        if self.pixbuf:
            del self.pixbuf
        self.pixbuf = None    
        
        # Return True to tell IconView call gc.collect() to release memory resource.
        return True

class DeleteItem(gobject.GObject):
    '''
    Icon item.
    '''
	
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    
    def __init__(self, path, theme):
        '''
        Initialize ItemIcon class.
        
        @param pixbuf: Icon pixbuf.
        '''
        gobject.GObject.__init__(self)

        self.image_path = path
        self.theme = theme
        self.pixbuf = None
        self.hover_flag = False
        self.highlight_flag = False
        self.wallpaper_width = SMALL_SIZE["x"]
        self.wallpaper_height = SMALL_SIZE["y"]
        self.width = self.wallpaper_width + ITEM_PADDING_X * 2
        self.height = self.wallpaper_height + ITEM_PADDING_Y * 2
        
        self.is_hover = False
        self.hover_stroke_dcolor = app_theme.get_color("globalHoverStroke")
        self.hover_response_rect = gtk.gdk.Rectangle(
            ITEM_PADDING_X, ITEM_PADDING_Y ,
            self.wallpaper_width, self.wallpaper_height
            ) 

        self.cross_normal_dpixbuf = app_theme.get_pixbuf("individuation/cross_normal.png")
        self.cross_gray_dpixbuf = app_theme.get_pixbuf("individuation/cross_gray.png")
        
        self.is_tick = False
        self.tick_area = None
        
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
        return self.width
        
    def get_height(self):
        '''
        Get item height.
        
        This is IconView interface, you should implement it.
        '''
        return self.height
    
    def render(self, cr, rect):
        '''
        Render item.
        
        This is IconView interface, you should implement it.
        '''
        # Init.
        if self.pixbuf == None:
            self.pixbuf = get_optimum_pixbuf_from_file(self.image_path, self.wallpaper_width, self.wallpaper_height)
            
        wallpaper_x = rect.x + (rect.width - self.wallpaper_width) / 2
        wallpaper_y = rect.y + (rect.height - self.wallpaper_height) / 2
        
        # Draw shadow.
        drop_shadow_padding = 7
        drop_shadow_radious = 7
        draw_shadow(
            cr,
            wallpaper_x,
            wallpaper_y,
            self.wallpaper_width + drop_shadow_padding,
            self.wallpaper_height + drop_shadow_padding,
            drop_shadow_radious,
            app_theme.get_shadow_color("window_shadow")
            )

        outside_shadow_padding = 4
        outside_shadow_radious = 5
        draw_shadow(
            cr,
            wallpaper_x - outside_shadow_padding,
            wallpaper_y - outside_shadow_padding,
            self.wallpaper_width + outside_shadow_padding * 2,
            self.wallpaper_height + outside_shadow_padding * 2,
            outside_shadow_radious,
            app_theme.get_shadow_color("window_shadow")
            )
        
        # Draw wallpaper.
        draw_pixbuf(cr, self.pixbuf, wallpaper_x, wallpaper_y)    
        
        # Draw wallpaper frame.
        with cairo_disable_antialias(cr):
            cr.set_line_width(2)
            cr.set_source_rgba(1, 1, 1, 1)
            cr.rectangle(wallpaper_x, wallpaper_y, self.wallpaper_width, self.wallpaper_height)
            cr.stroke()
            
        if self.is_hover:    
            cr.rectangle(wallpaper_x, wallpaper_y, self.wallpaper_width, self.wallpaper_height)
            cr.set_source_rgb(*color_hex_to_cairo(self.hover_stroke_dcolor.get_color()))
            cr.stroke()
            
        if self.is_tick:    
            tick_pixbuf = self.cross_normal_dpixbuf.get_pixbuf()
        else:    
            tick_pixbuf = self.cross_gray_dpixbuf.get_pixbuf()
            
        tick_x = wallpaper_x + self.wallpaper_width - tick_pixbuf.get_width() / 2 
        tick_y = wallpaper_y - tick_pixbuf.get_height() / 2
        if self.tick_area is None:
            self.tick_area = gtk.gdk.Rectangle(
                tick_x - rect.x,
                tick_y - rect.y,
                tick_pixbuf.get_width(),
                tick_pixbuf.get_height())
            
        if self.is_tick:    
            draw_pixbuf(cr, tick_pixbuf, tick_x, tick_y)
        else:
            if self.is_hover:    
                draw_pixbuf(cr, tick_pixbuf, tick_x, tick_y)    
                
    def tick(self):            
        self.is_tick = True
        self.set_theme_tick(self.is_tick)
        self.emit_redraw_request()
        
    def untick(self):    
        self.is_tick = False
        self.set_theme_tick(self.is_tick)
        self.emit_redraw_request()
        
    def toggle_tick(self):    
        self.is_tick = not self.is_tick
        self.set_theme_tick(self.is_tick)
        self.emit_redraw_request()
        
    def set_theme_tick(self, value):    
        pass
        
    def icon_item_motion_notify(self, x, y):
        '''
        Handle `motion-notify-event` signal.
        
        This is IconView interface, you should implement it.
        '''
        if is_in_rect((x, y), (self.hover_response_rect.x,
                               self.hover_response_rect.y,
                               self.hover_response_rect.width,
                               self.hover_response_rect.height)):
            self.is_hover = True
            
        else:    
            self.is_hover = False
            
        self.emit_redraw_request()    
            
        
    def icon_item_lost_focus(self):
        '''
        Lost focus.
        
        This is IconView interface, you should implement it.
        '''
        
        self.is_hover = False
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
        self.toggle_tick()
        event_manager.emit("select-delete-wallpaper", self)
    
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
        if self.pixbuf:
            del self.pixbuf
        self.pixbuf = None    
        
        # Return True to tell IconView call gc.collect() to release memory resource.
        return True

class AddItem(gobject.GObject):
    '''
    Icon item.
    '''
	
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    
    def __init__(self):
        '''
        Initialize ItemIcon class.
        
        @param pixbuf: Icon pixbuf.
        '''
        gobject.GObject.__init__(self)
        self.hover_flag = False
        self.highlight_flag = False
        self.image_path = "invalid"
        self.is_add = True
        self.wallpaper_width = SMALL_SIZE["x"]
        self.wallpaper_height = SMALL_SIZE["y"]
        self.width = self.wallpaper_width + ITEM_PADDING_X * 2
        self.height = self.wallpaper_height + ITEM_PADDING_Y * 2
        
        self.is_hover = False
        self.is_tick = False
        self.hover_stroke_dcolor = app_theme.get_color("globalHoverStroke")
        self.hover_response_rect = gtk.gdk.Rectangle(
            ITEM_PADDING_X, ITEM_PADDING_Y ,
            self.wallpaper_width, self.wallpaper_height
            ) 
        self.theme = None

    def set_theme(self, theme):
        self.theme = theme

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
        return self.width
        
    def get_height(self):
        '''
        Get item height.
        
        This is IconView interface, you should implement it.
        '''
        return self.height
    
    def untick(self):
        pass
    
    def tick(self):
        pass
    
    def toggle_tick(self):
        pass
    
    def render(self, cr, rect):
        '''
        Render item.
        
        This is IconView interface, you should implement it.
        '''
        # Init.
        wallpaper_x = rect.x + (rect.width - self.wallpaper_width) / 2
        wallpaper_y = rect.y + (rect.height - self.wallpaper_height) / 2
        
        # Draw shadow.
        drop_shadow_padding = 7
        drop_shadow_radious = 7
        draw_shadow(
            cr,
            wallpaper_x,
            wallpaper_y,
            self.wallpaper_width + drop_shadow_padding,
            self.wallpaper_height + drop_shadow_padding,
            drop_shadow_radious,
            app_theme.get_shadow_color("window_shadow")
            )

        outside_shadow_padding = 4
        outside_shadow_radious = 5
        draw_shadow(
            cr,
            wallpaper_x - outside_shadow_padding,
            wallpaper_y - outside_shadow_padding,
            self.wallpaper_width + outside_shadow_padding * 2,
            self.wallpaper_height + outside_shadow_padding * 2,
            outside_shadow_radious,
            app_theme.get_shadow_color("window_shadow")
            )
        
        # Draw add button.
        cr.set_source_rgb(0.7, 0.7, 0.7)
        cr.rectangle(wallpaper_x, wallpaper_y, self.wallpaper_width, self.wallpaper_height)
        cr.fill()
        
        add_button_width = 8
        add_button_height = 40
        cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.rectangle(wallpaper_x + (self.wallpaper_width - add_button_height) / 2,
                     wallpaper_y + (self.wallpaper_height - add_button_width) / 2, 
                     add_button_height,
                     add_button_width)
        cr.fill()
        
        cr.rectangle(wallpaper_x + (self.wallpaper_width - add_button_width) / 2,
                     wallpaper_y + (self.wallpaper_height - add_button_height) / 2, 
                     add_button_width,
                     add_button_height)
        cr.fill()
        
        # Draw wallpaper frame.
        with cairo_disable_antialias(cr):
            cr.set_line_width(2)
            cr.set_source_rgba(1, 1, 1, 1)
            cr.rectangle(wallpaper_x, wallpaper_y, self.wallpaper_width, self.wallpaper_height)
            cr.stroke()
            
        if self.is_hover:    
            cr.rectangle(wallpaper_x, wallpaper_y, self.wallpaper_width, self.wallpaper_height)
            cr.set_source_rgb(*color_hex_to_cairo(self.hover_stroke_dcolor.get_color()))
            cr.stroke()
        
    def icon_item_motion_notify(self, x, y):
        '''
        Handle `motion-notify-event` signal.
        
        This is IconView interface, you should implement it.
        '''
        if is_in_rect((x, y), (self.hover_response_rect.x,
                               self.hover_response_rect.y,
                               self.hover_response_rect.width,
                               self.hover_response_rect.height)):
            self.is_hover = True
            
        else:    
            self.is_hover = False
            
        self.emit_redraw_request()    

        
    def icon_item_lost_focus(self):
        '''
        Lost focus.
        
        This is IconView interface, you should implement it.
        '''
        
        self.is_hover = False
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
        event_manager.emit("switch-to-addpage", self.theme)
    
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
        # Return True to tell IconView call gc.collect() to release memory resource.
        return True
    
    
class CacheItem(gobject.GObject, MissionThread):
    '''
    Icon item.
    '''
	
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    
    def __init__(self, image_object, download_dir=None):
        '''
        Initialize ItemIcon class.
        
        @param pixbuf: Icon pixbuf.
        '''
        gobject.GObject.__init__(self)
        MissionThread.__init__(self)
      
        self.image_path = None
        self.is_loaded = False
        self.is_downloaded = False
        self.hover_flag = False
        self.highlight_flag = False
        self.wallpaper_width = SMALL_SIZE["x"]
        self.wallpaper_height = SMALL_SIZE["y"]
        self.padding_x = 8
        self.width = self.wallpaper_width + self.padding_x * 2
        self.height = self.wallpaper_height + ITEM_PADDING_Y * 2
        self.image_object = image_object
        self.download_dir = download_dir
        self.pixbuf = None
        self.create_cache_pixbuf()
        
        self.is_hover = False
        self.hover_stroke_dcolor = app_theme.get_color("globalHoverStroke")
        self.hover_response_rect = gtk.gdk.Rectangle(
            self.padding_x, ITEM_PADDING_Y ,
            self.wallpaper_width, self.wallpaper_height
            ) 
        
        self.tick_normal_dpixbuf = app_theme.get_pixbuf("individuation/tick_normal.png")
        self.tick_gray_dpixbuf = app_theme.get_pixbuf("individuation/tick_gray.png")
        self.is_tick = False

        self.loop_dpixbuf = app_theme.get_pixbuf("individuation/loop.png")
        self.is_loop = False

        event_manager.add_callback("download-start", self.__on_download_start)
        event_manager.add_callback("download-finish", self.__on_download_finish)
        event_manager.add_callback("delete-downloaded-wallpaper", self.__on_delete_downloaded_wallpaper)

    def __on_delete_downloaded_wallpaper(self, name, obj, data):
        self.create_cache_pixbuf()
        self.emit_redraw_request()

    def __on_download_start(self, name, obj, data):
        if self.image_object.big_url != data.url:
            return

        self.is_loop = True
        self.degree = 0
        self.refresh_loading()

    @common.threaded
    def refresh_loading(self):
        while self.is_loop:
            self.degree += 10
            self.emit_redraw_request()
            time.sleep(0.1)

    def __on_download_finish(self, name, obj, data):                                
        if self.image_object.big_url != data.url:                               
            return                                                              
                                                                                
        self.is_loop = False
        self.is_downloaded = True
        self.emit_redraw_request()
        self.image_path = self.image_object.get_save_path()
        event_manager.emit("add-download-wallpapers", [self.image_object.get_save_path()])
        event_manager.emit("apply-download-wallpaper", self.image_object.get_save_path())

    @common.threaded
    def create_cache_pixbuf(self):
        image_path = cache_manager.get_image(self.image_object)
        
        if image_path != None:
            self.is_downloaded = os.path.exists(self.download_dir + "/" +  image_path.split("/")[-1])
            if self.is_downloaded:
                self.image_path = self.download_dir + "/" +  image_path.split("/")[-1]
        
        self.pixbuf, self.is_loaded = cache_manager.get_image_pixbuf(self.image_object)

    def start_mission(self):    
        image_path = cache_manager.get_image(self.image_object, try_web=True)
        if image_path:
            self.delay_render_image(image_path)
            
    def delay_render_image(self, image_path):        
        gobject.timeout_add(200 + random.randint(1, 10),  self.render_image, image_path)
            
    @post_gui    
    def render_image(self, image_path):
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(image_path)
        except:    
            pass
        else:
            self.pixbuf = pixbuf
            self.emit_redraw_request()
            
        return False
        
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
        return self.width
        
    def get_height(self):
        '''
        Get item height.
        
        This is IconView interface, you should implement it.
        '''
        return self.height
    
    def render(self, cr, rect):
        '''
        Render item.
        
        This is IconView interface, you should implement it.
        '''
        if self.pixbuf == None:
            self.create_cache_pixbuf()
            
        wallpaper_x = rect.x + (rect.width - self.wallpaper_width) / 2
        wallpaper_y = rect.y + (rect.height - self.wallpaper_height) / 2
        
        # Draw shadow.
        drop_shadow_padding = 7
        drop_shadow_radious = 7
        draw_shadow(
            cr,
            wallpaper_x,
            wallpaper_y,
            self.wallpaper_width + drop_shadow_padding,
            self.wallpaper_height + drop_shadow_padding,
            drop_shadow_radious,
            app_theme.get_shadow_color("window_shadow")
            )

        outside_shadow_padding = 4
        outside_shadow_radious = 5
        draw_shadow(
            cr,
            wallpaper_x - outside_shadow_padding,
            wallpaper_y - outside_shadow_padding,
            self.wallpaper_width + outside_shadow_padding * 2,
            self.wallpaper_height + outside_shadow_padding * 2,
            outside_shadow_radious,
            app_theme.get_shadow_color("window_shadow")
            )
        
        # Draw wallpaper.
        draw_pixbuf(cr, self.pixbuf, wallpaper_x, wallpaper_y)    
        
        # Draw wallpaper frame.
        with cairo_disable_antialias(cr):
            cr.set_line_width(2)
            cr.set_source_rgba(1, 1, 1, 1)
            cr.rectangle(wallpaper_x, wallpaper_y, self.wallpaper_width, self.wallpaper_height)
            cr.stroke()
            
        if self.is_hover:    
            cr.rectangle(wallpaper_x, wallpaper_y, self.wallpaper_width, self.wallpaper_height)
            cr.set_source_rgb(*color_hex_to_cairo(self.hover_stroke_dcolor.get_color()))
            cr.stroke()

        if self.is_downloaded:
            downloaded_str = _("downloaded")
            downloaded_padding = 4
            downloaded_str_width, downloaded_str_height = get_content_size(downloaded_str)
            cr.rectangle(wallpaper_x + 1, 
                         wallpaper_y + self.wallpaper_height - downloaded_str_height - downloaded_padding, 
                         self.wallpaper_width - 2, 
                         downloaded_str_height - 1 + downloaded_padding)
            cr.set_source_rgba(0, 0, 0, 0.4)
            cr.fill()
            draw_text(cr, 
                      downloaded_str, 
                      wallpaper_x + (self.wallpaper_width - downloaded_str_width) / 2, 
                      wallpaper_y + self.wallpaper_height - downloaded_str_height - downloaded_padding / 1.5, 
                      self.wallpaper_width, 
                      downloaded_str_height, 
                      text_color = "#FFFFFF")
            
        if self.is_tick:    
            tick_pixbuf = self.tick_normal_dpixbuf.get_pixbuf()
        else:    
            tick_pixbuf = self.tick_gray_dpixbuf.get_pixbuf()
            
        tick_x = wallpaper_x + self.wallpaper_width - tick_pixbuf.get_width() / 2 
        tick_y = wallpaper_y - tick_pixbuf.get_height() / 2
        #draw_pixbuf(cr, tick_pixbuf, tick_x, tick_y)    
        
        if self.is_tick:
            tick_pixbuf = self.tick_normal_dpixbuf.get_pixbuf()
        else:    
            tick_pixbuf = self.tick_gray_dpixbuf.get_pixbuf()
            
        tick_x = wallpaper_x + self.wallpaper_width - tick_pixbuf.get_width() / 2
        tick_y = wallpaper_y - tick_pixbuf.get_height() / 2
        #draw_pixbuf(cr, tick_pixbuf, tick_x, tick_y)

        if self.is_loop:
            loop_pixbuf = self.loop_dpixbuf.get_pixbuf()
            loop_x = wallpaper_x + (self.wallpaper_width - loop_pixbuf.get_width()) / 2
            loop_y = wallpaper_y + (self.wallpaper_height - loop_pixbuf.get_height()) / 2
            self.draw_loop_pixbuf(cr, loop_pixbuf, loop_x, loop_y)
    
    def draw_loop_pixbuf(self, cr, loop_pixbuf, loop_x, loop_y):
        width = loop_pixbuf.get_width()
        height = loop_pixbuf.get_height()
        ox = loop_x + width * 0.5
        oy = loop_y + height * 0.5 

        with cairo_state(cr):
            cr.translate(ox, oy)
            cr.rotate(radians(self.degree))                      
            cr.translate(-width * 0.5, -height * 0.5)
            draw_pixbuf(cr, loop_pixbuf, 0, 0)

    def icon_item_motion_notify(self, x, y):
        '''
        Handle `motion-notify-event` signal.
        
        This is IconView interface, you should implement it.
        '''
        
        if is_in_rect((x, y), (self.hover_response_rect.x,
                               self.hover_response_rect.y,
                               self.hover_response_rect.width,
                               self.hover_response_rect.height)):
            self.is_hover = True
            
        else:    
            self.is_hover = False
            
        self.emit_redraw_request()    
        
    def icon_item_lost_focus(self):
        '''
        Lost focus.
        
        This is IconView interface, you should implement it.
        '''
        
        self.is_hover = False
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
        self.emit_redraw_request()
        if self.is_downloaded:
            event_manager.emit("apply-wallpaper", self)
        event_manager.emit("download-images", [self.image_object])
    
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
        # Return True to tell IconView call gc.collect() to release memory resource.
        if self.pixbuf:
            del self.pixbuf
        self.pixbuf = None    
        return True

class SelectItem(gobject.GObject):
    '''
    Icon item.
    '''
	
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    
    def __init__(self, image_path):
        '''
        Initialize ItemIcon class.
        
        @param pixbuf: Icon pixbuf.
        '''
        gobject.GObject.__init__(self)
        
        self.hover_flag = False
        self.highlight_flag = False
        self.wallpaper_width = SMALL_SIZE["x"]
        self.wallpaper_height = SMALL_SIZE["y"]
        self.padding_x = 8
        self.width = self.wallpaper_width + self.padding_x * 2
        self.height = self.wallpaper_height + ITEM_PADDING_Y * 2
        self.image_path = image_path
        self.create_cache_pixbuf()
        
        self.is_hover = False
        self.hover_stroke_dcolor = app_theme.get_color("globalHoverStroke")
        self.hover_response_rect = gtk.gdk.Rectangle(
            self.padding_x, ITEM_PADDING_Y ,
            self.wallpaper_width, self.wallpaper_height
            ) 
        
        self.tick_normal_dpixbuf = app_theme.get_pixbuf("individuation/tick_normal.png")
        self.tick_gray_dpixbuf = app_theme.get_pixbuf("individuation/tick_gray.png")
        self.is_tick = False
        
    def create_cache_pixbuf(self):    
        self.pixbuf = get_optimum_pixbuf_from_file(self.image_path, self.wallpaper_width, self.wallpaper_height)
        
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
        return self.width
        
    def get_height(self):
        '''
        Get item height.
        
        This is IconView interface, you should implement it.
        '''
        return self.height
    
    def render(self, cr, rect):
        '''
        Render item.
        
        This is IconView interface, you should implement it.
        '''
        if self.pixbuf == None:
            self.create_cache_pixbuf()
        
        wallpaper_x = rect.x + (rect.width - self.wallpaper_width) / 2
        wallpaper_y = rect.y + (rect.height - self.wallpaper_height) / 2
        
        # Draw shadow.
        drop_shadow_padding = 7
        drop_shadow_radious = 7
        draw_shadow(
            cr,
            wallpaper_x,
            wallpaper_y,
            self.wallpaper_width + drop_shadow_padding,
            self.wallpaper_height + drop_shadow_padding,
            drop_shadow_radious,
            app_theme.get_shadow_color("window_shadow")
            )

        outside_shadow_padding = 4
        outside_shadow_radious = 5
        draw_shadow(
            cr,
            wallpaper_x - outside_shadow_padding,
            wallpaper_y - outside_shadow_padding,
            self.wallpaper_width + outside_shadow_padding * 2,
            self.wallpaper_height + outside_shadow_padding * 2,
            outside_shadow_radious,
            app_theme.get_shadow_color("window_shadow")
            )
        
        # Draw wallpaper.
        draw_pixbuf(cr, self.pixbuf, wallpaper_x, wallpaper_y)    
        
        # Draw wallpaper frame.
        with cairo_disable_antialias(cr):
            cr.set_line_width(2)
            cr.set_source_rgba(1, 1, 1, 1)
            cr.rectangle(wallpaper_x, wallpaper_y, self.wallpaper_width, self.wallpaper_height)
            cr.stroke()
            
        if self.is_hover:    
            cr.rectangle(wallpaper_x, wallpaper_y, self.wallpaper_width, self.wallpaper_height)
            cr.set_source_rgb(*color_hex_to_cairo(self.hover_stroke_dcolor.get_color()))
            cr.stroke()
        
        if self.is_tick:    
            tick_pixbuf = self.tick_normal_dpixbuf.get_pixbuf()
        else:    
            tick_pixbuf = self.tick_gray_dpixbuf.get_pixbuf()
            
        tick_x = wallpaper_x + self.wallpaper_width - tick_pixbuf.get_width() / 2 
        tick_y = wallpaper_y - tick_pixbuf.get_height() / 2
        draw_pixbuf(cr, tick_pixbuf, tick_x, tick_y)    
        
    def icon_item_motion_notify(self, x, y):
        '''
        Handle `motion-notify-event` signal.
        
        This is IconView interface, you should implement it.
        '''
        
        if is_in_rect((x, y), (self.hover_response_rect.x,
                               self.hover_response_rect.y,
                               self.hover_response_rect.width,
                               self.hover_response_rect.height)):
            self.is_hover = True
            
        else:    
            self.is_hover = False
            
        self.emit_redraw_request()    
        
    def icon_item_lost_focus(self):
        '''
        Lost focus.
        
        This is IconView interface, you should implement it.
        '''
        
        self.is_hover = False
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
    
    def tick(self):
        self.is_tick = True
        self.emit_redraw_request()

    def untick(self):
        self.is_tick = False
        self.emit_redraw_request()

    def icon_item_button_press(self, x, y):
        '''
        Handle button-press event.
        
        This is IconView interface, you should implement it.
        '''
        self.is_tick = not self.is_tick
        event_manager.emit("select-select-wallpaper", self)
        self.emit_redraw_request()
    
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
        # Return True to tell IconView call gc.collect() to release memory resource.
        if self.pixbuf:
            del self.pixbuf
        self.pixbuf = None    
        return True
