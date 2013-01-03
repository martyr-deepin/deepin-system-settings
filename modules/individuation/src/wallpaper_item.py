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

import gtk
import random
import gobject

from dtk.ui.utils import get_optimum_pixbuf_from_file, cairo_disable_antialias, run_command
from dtk.ui.draw import draw_pixbuf, draw_shadow
from dtk.ui.threads import post_gui
from dtk.ui.thread_pool import MissionThread

from theme import app_theme
from helper import event_manager
from cache_manager import SMALL_SIZE, cache_manager


ITEM_PADDING_X = 20
ITEM_PADDING_Y = 10

class WallpaperItem(gobject.GObject):
    '''
    Icon item.
    '''
	
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    
    def __init__(self, path):
        '''
        Initialize ItemIcon class.
        
        @param pixbuf: Icon pixbuf.
        '''
        gobject.GObject.__init__(self)
        self.path = path
        self.pixbuf = None
        self.hover_flag = False
        self.highlight_flag = False
        self.wallpaper_width = SMALL_SIZE["x"]
        self.wallpaper_height = SMALL_SIZE["y"]
        self.width = self.wallpaper_width + ITEM_PADDING_X * 2
        self.height = self.wallpaper_height + ITEM_PADDING_Y * 2
        
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
        
        # cr.rectangle(*rect)
        # cr.set_source_rgb(0, 0, 0)
        # cr.stroke()
        
        # Init.
        if self.pixbuf == None:
            self.pixbuf = get_optimum_pixbuf_from_file(self.path, self.wallpaper_width, self.wallpaper_height)
            
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
        
    def icon_item_motion_notify(self, x, y):
        '''
        Handle `motion-notify-event` signal.
        
        This is IconView interface, you should implement it.
        '''
        pass
        
    def icon_item_lost_focus(self):
        '''
        Lost focus.
        
        This is IconView interface, you should implement it.
        '''
        pass
        
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
        run_command("gsettings set com.deepin.dde.background picture-uris 'file://%s'" % self.path)
    
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
        self.wallpaper_width = SMALL_SIZE["x"]
        self.wallpaper_height = SMALL_SIZE["y"]
        self.width = self.wallpaper_width + ITEM_PADDING_X * 2
        self.height = self.wallpaper_height + ITEM_PADDING_Y * 2
        
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
        
    def icon_item_motion_notify(self, x, y):
        '''
        Handle `motion-notify-event` signal.
        
        This is IconView interface, you should implement it.
        '''
        pass
        
    def icon_item_lost_focus(self):
        '''
        Lost focus.
        
        This is IconView interface, you should implement it.
        '''
        pass
        
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
        event_manager.emit("add-wallpapers", None)
    
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
    
    def __init__(self, image_object):
        '''
        Initialize ItemIcon class.
        
        @param pixbuf: Icon pixbuf.
        '''
        gobject.GObject.__init__(self)
        MissionThread.__init__(self)
        
        self.hover_flag = False
        self.highlight_flag = False
        self.wallpaper_width = SMALL_SIZE["x"]
        self.wallpaper_height = SMALL_SIZE["y"]
        self.width = self.wallpaper_width + 8 * 2
        self.height = self.wallpaper_height + ITEM_PADDING_Y * 2
        self.image_object = image_object
        self.create_cache_pixbuf()
        
    def create_cache_pixbuf(self):    
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
        
    def icon_item_motion_notify(self, x, y):
        '''
        Handle `motion-notify-event` signal.
        
        This is IconView interface, you should implement it.
        '''
        pass
        
    def icon_item_lost_focus(self):
        '''
        Lost focus.
        
        This is IconView interface, you should implement it.
        '''
        pass
        
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
        # Return True to tell IconView call gc.collect() to release memory resource.
        return True
    
