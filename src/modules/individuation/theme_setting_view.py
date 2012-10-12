#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
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
import gtk
import gobject
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.tab_window import TabBox
from dtk.ui.iconview import IconView
from dtk.ui.utils import get_optimum_pixbuf_from_file, cairo_disable_antialias
from dtk.ui.draw import draw_pixbuf, draw_shadow, draw_window_shadow

ITEM_PADDING_X = 19
ITEM_PADDING_Y = 15

class ThemeSettingView(TabBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        TabBox.__init__(self)
        self.theme = None
        
        self.wallpaper_box = gtk.VBox()
        self.window_theme_box = gtk.VBox()
        self.theme_icon_view = IconView(ITEM_PADDING_X, ITEM_PADDING_Y)
        self.theme_icon_view.draw_mask = self.draw_mask
        self.theme_scrolledwindow = ScrolledWindow()
        
        self.add_items([("壁纸", self.wallpaper_box),
                        ("窗口主题", self.window_theme_box)])
        
        self.theme_scrolledwindow.add_child(self.theme_icon_view)
        self.wallpaper_box.pack_start(self.theme_scrolledwindow, True, True)
        
    def set_theme(self, theme):
        self.theme = theme
        self.theme_icon_view.clear()
        
        items = []
        for wallpaper_path in self.theme.get_wallpaper_paths():
            items.append(WallpaperItem(wallpaper_path))
            
        self.theme_icon_view.add_items(items)    
        
    def draw_mask(self, cr, x, y, w, h):
        '''
        Draw mask interface.
        
        @param cr: Cairo context.
        @param x: X coordiante of draw area.
        @param y: Y coordiante of draw area.
        @param w: Width of draw area.
        @param h: Height of draw area.
        '''
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
        
gobject.type_register(ThemeSettingView)        

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
        self.wallpaper_width = 160
        self.wallpaper_height = 100
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
        self.hover_flag = True
        
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
        if self.pixbuf:
            del self.pixbuf
        self.pixbuf = None    
        
        # Return True to tell IconView call gc.collect() to release memory resource.
        return True
        
gobject.type_register(WallpaperItem)
