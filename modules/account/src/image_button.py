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
from dtk.ui.cache_pixbuf import CachePixbuf
from dtk.ui.draw import draw_pixbuf
from dtk.ui.utils import propagate_expose, color_hex_to_cairo
import gtk
import gobject


class ImageButton(gtk.Button):
    '''
    ImageButton class.
    '''
    def __init__(self, 
                 normal_dpixbuf, 
                 hover_dpixbuf, 
                 press_dpixbuf):
        '''
        Initialize ImageButton class.
        @param normal_dpixbuf: DynamicPixbuf for button normal status.
        @param hover_dpixbuf: DynamicPixbuf for button hover status.
        @param press_dpixbuf: DynamicPixbuf for button press status.
        '''
        gtk.Button.__init__(self)
        self.cache_pixbuf = CachePixbuf()

        self.request_width = normal_dpixbuf.get_pixbuf().get_width()
        self.request_height = normal_dpixbuf.get_pixbuf().get_height()
        self.set_size_request(self.request_width, self.request_height)

        # Expose button.
        self.connect("expose-event", self.expose_button,
                     self.cache_pixbuf, normal_dpixbuf, hover_dpixbuf, press_dpixbuf)
        
    def expose_button(self, widget, event,
                      cache_pixbuf, normal_dpixbuf, hover_dpixbuf, press_dpixbuf):
        
        # Get pixbuf along with button's sate.
        if widget.state == gtk.STATE_NORMAL or widget.state == gtk.STATE_INSENSITIVE:
            image = normal_dpixbuf.get_pixbuf()
        elif widget.state == gtk.STATE_PRELIGHT:
            image = hover_dpixbuf.get_pixbuf()
        elif widget.state == gtk.STATE_ACTIVE:
            image = press_dpixbuf.get_pixbuf()
        
        # Draw button.
        pixbuf = image
        image_width = self.request_width
        image_height = self.request_height
        if pixbuf.get_width() != image_width or pixbuf.get_height() != image_height:
            cache_pixbuf.scale(image, image_width, image_height)
            pixbuf = cache_pixbuf.get_cache()
        cr = widget.window.cairo_create()
        draw_pixbuf(cr, pixbuf, widget.allocation.x, widget.allocation.y)

        if widget.state == gtk.STATE_INSENSITIVE:
            color = "#A2A2A2"
            color = color_hex_to_cairo(color)
            cr.set_source_rgba(color[0], color[1], color[2], 0.7)
            cr.rectangle(*widget.allocation)
            cr.fill()
        
        # Propagate expose to children.
        propagate_expose(widget, event)
        
        return True

gobject.type_register(ImageButton)
