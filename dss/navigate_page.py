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

from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.iconview import IconView
from dtk.ui.utils import color_hex_to_cairo, cairo_disable_antialias, is_in_rect
from dtk.ui.draw import draw_pixbuf, draw_text
from dtk.ui.constant import DEFAULT_FONT_SIZE
import pango
import gtk
import gobject
import os
import locale

from theme import app_theme

ICON_SIZE = 106

class NavigatePage(gtk.Alignment):
    '''
    class docs
    '''
	
    def __init__(self, module_infos, start_callback):
        '''
        init docs
        '''
        # Init.
        gtk.Alignment.__init__(self)
        (self.first_module_infos, self.second_module_infos, self.third_module_infos, self.extend_module_infos) = module_infos
        self.start_callback = start_callback
        self.module_dir = os.path.join(os.path.dirname(__file__), "modules")        
        
        # Init widgets.
        self.set(0.5, 0.5, 1, 1)
        self.set_padding(50, 0, 0, 0)
        self.layout = gtk.VBox()        
        self.first_iconview = IconView(18)
        self.second_iconview = IconView(18)
        self.third_iconview = IconView(18)
        self.extend_iconview = IconView(18)
        self.first_iconview_scrolledwindow = ScrolledWindow()
        self.second_iconview_scrolledwindow = ScrolledWindow()
        self.third_iconview_scrolledwindow = ScrolledWindow()
        self.extend_iconview_scrolledwindow = ScrolledWindow()
        
        # Connect widgets.
        self.add(self.layout)
        
        # Add icons.
        self.add_modules(self.first_module_infos, self.first_iconview, self.first_iconview_scrolledwindow)
        self.add_modules(self.second_module_infos, self.second_iconview, self.second_iconview_scrolledwindow)
        self.add_modules(self.third_module_infos, self.third_iconview, self.third_iconview_scrolledwindow)
        self.add_modules(self.extend_module_infos, self.extend_iconview, self.extend_iconview_scrolledwindow)
        
        self.first_iconview.draw_mask = self.draw_mask
        self.second_iconview.draw_mask = self.draw_mask
        self.third_iconview.draw_mask = self.draw_mask
        self.extend_iconview.draw_mask = self.draw_mask
        self.connect("expose-event", self.expose_navigate_page)
            
    def add_modules(self, module_infos, icon_view, scrolled_window):
        if len(module_infos) > 0:    
            items = []
            for module_info in module_infos:
                items.append(IconItem(module_info, self.start_callback))
            
            icon_view.add_items(items)    
            scrolled_window.add_child(icon_view)
            scrolled_window.set_size_request(-1, ICON_SIZE)
            self.layout.pack_start(scrolled_window, False, False)
            
    def expose_navigate_page(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation

        self.draw_mask(cr, rect.x, rect.y, rect.width, rect.height)
            
    def draw_mask(self, cr, x, y, w, h):
        '''
        Draw mask interface.
        
        @param cr: Cairo context.
        @param x: X coordiante of draw area.
        @param y: Y coordiante of draw area.
        @param w: Width of draw area.
        @param h: Height of draw area.
        '''
        cr.set_source_rgba(1, 1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
        
gobject.type_register(NavigatePage)


class IconItem(gobject.GObject):
    '''
    Icon item.
    '''
	
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    
    def __init__(self, module_info, start_callback):
        '''
        Initialize ItemIcon class.
        
        @param pixbuf: Icon pixbuf.
        '''
        gobject.GObject.__init__(self)
        self.start_callback = start_callback
        self.module_info = module_info
        self.icon_padding_y = 21
        self.name_padding_y = 8
        self.hover_flag = False
        self.highlight_flag = False
        self.hover_offset = 5
        self.hover_stroke_dcolor = app_theme.get_color("globalHoverStroke")
        self.hover_fill_dcolor = app_theme.get_color("globalHoverFill")
        self.hover_response_rect = gtk.gdk.Rectangle(
            self.hover_offset, self.hover_offset, 
            ICON_SIZE - self.hover_offset * 2, 
            ICON_SIZE - self.hover_offset * 2) 
        
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
        return ICON_SIZE
        
    def get_height(self):
        '''
        Get item height.
        
        This is IconView interface, you should implement it.
        '''
        return ICON_SIZE
    
    def render(self, cr, rect):
        '''
        Render item.
        
        This is IconView interface, you should implement it.
        '''
        # Init size.
        icon_width = self.module_info.icon_pixbuf.get_width()
        icon_height = self.module_info.icon_pixbuf.get_height()
        
        # Draw background.
        if self.hover_flag:
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
        
        # Draw icon.
        draw_pixbuf(
            cr, 
            self.module_info.icon_pixbuf,
            rect.x + (rect.width - icon_width) / 2,
            rect.y + self.icon_padding_y)
        
        # Draw icon name.
        # TODO: lihongwu req to support i18n
        name = self.module_info.name
        if len(locale.getdefaultlocale()):
            if locale.getdefaultlocale()[0].find("zh_") != 0:
                name = self.module_info.default_name
        else:
            name = self.module_info.default_name
        
        draw_text(cr, name, 
                  rect.x, 
                  rect.y + self.icon_padding_y + icon_height + self.name_padding_y,
                  rect.width, 
                  DEFAULT_FONT_SIZE, 
                  alignment=pango.ALIGN_CENTER)
        
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
        self.start_callback(self.module_info.path, self.module_info.config)

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
        return False
        
gobject.type_register(IconItem)
