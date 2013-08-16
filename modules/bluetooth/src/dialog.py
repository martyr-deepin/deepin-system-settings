#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang YaoHua
#
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
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


# This file is _not_ in use anymore, if you want the source bundle to be more cleaner,
# delete this file for me :(

import gtk
import cairo

from dtk.ui.theme import ui_theme
from dtk_cairo_blur import gaussian_blur
from dtk.ui.skin_config import skin_config
from dtk.ui.titlebar import Titlebar
from dtk.ui.draw import draw_vlinear, draw_round_rectangle
from dtk.ui.utils import move_window, propagate_expose
from dtk.ui.button import Button
from dtk.ui.entry import InputEntry
from nls import _

BORDER_RADIOUS = 3

class BluetoothDialog(gtk.Dialog):
    def __init__(self, title):
        gtk.Dialog.__init__(self)

        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_colormap(gtk.gdk.Screen().get_rgba_colormap() or gtk.gdk.Screen().get_rgb_colormap())
        self.set_size_request(350, 140)

        self.titlebar = Titlebar(
            ["close"],
            None,
            title)

        self.titlebar.close_button.connect("clicked", lambda w: self.destroy())

        self.add_move_event(self.titlebar)
        self.vbox.pack_start(self.titlebar, False, False, 0)
        
        self.connect("expose-event", self.__render)
        
    def __render_blur(self, cr, rect):
        x, y, w, h = rect
        
        img_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        img_surf_cr = cairo.Context(img_surf)
        draw_round_rectangle(img_surf_cr, x + 3, y + 3, w - 6, h - 6, BORDER_RADIOUS)
        
        img_surf_cr.set_source_rgb(0, 0, 0)
        img_surf_cr.set_line_width(1)
        img_surf_cr.stroke()
        gaussian_blur(img_surf, 2)
        
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_surface(img_surf, 0, 0)
        cr.rectangle(*rect)
        cr.fill()
        
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        draw_round_rectangle(cr, x + 3, y + 3, w - 6, h - 6, BORDER_RADIOUS)
        cr.stroke_preserve()
        
        cr.clip()

    def __render(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y, w, h = rect

        cr.rectangle(*rect)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.fill()

        cr.set_operator(cairo.OPERATOR_OVER)

        # Draw border
        self.__render_blur(cr, rect)
        
        # Render background
        skin_config.render_background(cr, self, rect.x, rect.y)

        # Draw mask
        self.draw_mask_single_page(cr, rect.x, rect.y, rect.width, rect.height)

        propagate_expose(widget, event)

        return True
    
    def add_dtk_button(self, btn, response_id):
        def btn_clicked(w):
            self.response(response_id)
            self.destroy()
            
        btn.set_size(70, 20)
        btn.connect_after("clicked", btn_clicked)
        self.get_action_area().pack_start(btn, False, False)

    def add_move_event(self, widget):
        '''
        Add move event callback.

        @param widget: A widget of type gtk.Widget.
        '''
        widget.connect("button-press-event", lambda w, e: move_window(w, e, self))

    def draw_mask_single_page(self, cr, x, y, w, h):
        '''
        Internal render function for DIALOG_MASK_SINGLE_PAGE type.

        @param cr: Cairo context.
        @param x: X coordinate of draw area.
        @param y: Y coordinate of draw area.
        @param w: Width of draw area.
        @param h: Height of draw area.
        '''
        top_height = 70

        draw_vlinear(
            cr, x, y, w, top_height,
            ui_theme.get_shadow_color("mask_single_page_top").get_color_info(),
            )

        draw_vlinear(
            cr, x, y + top_height, w, h - top_height,
            ui_theme.get_shadow_color("mask_single_page_bottom").get_color_info(),
            )

class BluetoothInputDialog(BluetoothDialog):
    
    def __init__(self, title, ok_cb=None, cancel_cb=None):
        BluetoothDialog.__init__(self, title)
        
        self.ok_cb = ok_cb
        self.cancel_cb = cancel_cb
        
        self.input_entry_align = gtk.Alignment()
        self.input_entry_align.set_padding(20, 20, 5, 5)
        
        self.input_entry = InputEntry("")
        self.input_entry.set_size(500, 25)
        
        self.ok_button = Button(_("OK"))
        self.ok_button.connect("clicked", self.__ok_callback)
        self.cancel_button = Button(_("Cancel"))
        self.cancel_button.connect("clicked", self.__cancel_callback)
        
        self.input_entry_align.add(self.input_entry)
        self.vbox.pack_end(self.input_entry_align)
        self.add_dtk_button(self.ok_button, gtk.RESPONSE_OK)
        self.add_dtk_button(self.cancel_button, gtk.RESPONSE_CANCEL)
        
        self.input_entry.entry.connect("press-return", ok_cb, self.input_entry.get_text())
        
    def __ok_callback(self, widget):
        if self.ok_cb:
            apply(self.ok_cb, [self.input_entry.get_text()])
            
    def __cancel_callback(self, widget):
        if self.cancel_cb:
            self.cancel_cb()
