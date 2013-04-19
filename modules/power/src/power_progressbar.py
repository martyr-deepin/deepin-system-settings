#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Deepin, Inc.
#               2013 Zhai Xiang
# 
# Author:     Zhai Xiang <zhaixiang@linuxdeepin.com>
# Maintainer: Zhai Xiang <zhaixiang@linuxdeepin.com>
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

from dtk.ui.cache_pixbuf import CachePixbuf
from dtk.ui.draw import draw_vlinear, draw_pixbuf
from dtk.ui.theme import ui_theme
from dtk.ui.utils import cairo_state, propagate_expose, color_hex_to_cairo, cairo_disable_antialias
import gobject
import gtk
from theme import app_theme

class PowerProgressBuffer(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        
        self.progress = 0

        self.percentage_dpixbuf = [app_theme.get_pixbuf("power/10.png"), 
                                   app_theme.get_pixbuf("power/20.png"), 
                                   app_theme.get_pixbuf("power/30.png"), 
                                   app_theme.get_pixbuf("power/40.png"), 
                                   app_theme.get_pixbuf("power/50.png"), 
                                   app_theme.get_pixbuf("power/60.png"), 
                                   app_theme.get_pixbuf("power/70.png"), 
                                   app_theme.get_pixbuf("power/80.png"), 
                                   app_theme.get_pixbuf("power/90.png"), 
                                   app_theme.get_pixbuf("power/100.png")]
        
    def render(self, cr, rect):
        # Init.
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        
        # Draw background frame.
        with cairo_state(cr):
            cr.rectangle(x, y + 1, w, h - 2)
            cr.rectangle(x + 1, y, w - 2, h)
            cr.clip()
            
            cr.set_source_rgb(*color_hex_to_cairo(ui_theme.get_color("progressbar_background_frame").get_color()))
            cr.rectangle(x, y, w, h)
            cr.set_line_width(1)
            cr.stroke()
            
        # Draw background.
        with cairo_state(cr):
            cr.rectangle(x + 1, y + 1, w - 2, h - 2)
            cr.clip()
            
            draw_vlinear(cr, x + 1, y + 1, w - 2, h - 2,
                         ui_theme.get_shadow_color("progressbar_background").get_color_info(), 
                         )
            cache_pixbuf_object = CachePixbuf()
            if self.progress > 0 and self.progress < 100:
                cache_pixbuf_object.scale(self.percentage_dpixbuf[int(self.progress / 10)].get_pixbuf(), 
                                          w, 
                                          h)
            if self.progress == 100:
                cache_pixbuf_object.scale(self.percentage_dpixbuf[9].get_pixbuf(), 
                                          w, 
                                          h)
            draw_pixbuf(cr, cache_pixbuf_object.get_cache(), x, y)
        
        # Draw light.
        with cairo_disable_antialias(cr):
            cr.set_source_rgba(1, 1, 1, 0.5)
            cr.rectangle(x + 1, y + 1, w - 2, 1)
            cr.fill()

gobject.type_register(PowerProgressBuffer)

class PowerProgressBar(gtk.Button):
    '''
    Progress bar.
    
    @undocumented: expose_progressbar
    @undocumented: update_light_ticker
    '''
	
    def __init__(self):
        '''
        Initialize progress bar.
        '''
        # Init.
        gtk.Button.__init__(self)
        self.test_ticker = 0
        self.progress_buffer = PowerProgressBuffer()
        
        # Expose callback.
        self.connect("expose-event", self.expose_progressbar)
        
    def expose_progressbar(self, widget, event):
        '''
        Internal callback for `expose` signal.
        '''
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        self.progress_buffer.render(cr, rect)
               
        # Propagate expose.
        propagate_expose(widget, event)
        
        return True        
    
gobject.type_register(PowerProgressBar)
