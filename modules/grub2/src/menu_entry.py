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

import pango
from theme import app_theme
from dtk.ui.treeview import TreeItem
from dtk.ui.draw import draw_text
from dtk.ui.utils import color_hex_to_cairo

def draw_single_mask(cr, x, y, width, height, color_name):
    if color_name.startswith("#"):
        color = color_name
    else:
        color = app_theme.get_color(color_name).get_color()
    cairo_color = color_hex_to_cairo(color)
    cr.set_source_rgb(*cairo_color)
    cr.rectangle(x, y, width, height)
    cr.fill()

class MenuEntry(TreeItem):

    def __init__(self, title, is_parent=False):
        '''
        init docs
        '''
        TreeItem.__init__(self)

        self._title = title

        self.item_height = 26
        self.item_width = 200

        self.column_index = 0

        self.is_hover = False
        self.is_select = False
        self.is_highlight = False

        self.is_parent = is_parent

        if is_parent:
            self.row_index = 0
        else:
            self.row_index = 1

        self.child_offset = 10

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    def add_child_items(self, items):
        self.child_items = items
        self.expand()

    def get_height(self):
        return self.item_height

    def get_column_widths(self):
        return [self.item_width,]

    def get_column_renders(self):
        return (self.render_title,)

    def unselect(self):
        self.is_select = False
        self.emit_redraw_request()

    def emit_redraw_request(self):
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def expand(self):
        self.is_expand = True

        if self.child_items:
            self.add_items_callback(self.child_items, self.row_index + 1)

        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def unexpand(self):
        self.is_expand = False

        if self.child_items:
            self.delete_items_callback(self.child_items)

        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def select(self):
        self.is_select = True
        self.emit_redraw_request()

    def render_title(self, cr, rect):
        # Draw select background.
        rect.width -= 2

        if not self.is_parent:
            if self.is_highlight:
                draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemSelect")
            elif self.is_hover:
                draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemHover")

            if self.is_highlight:
                text_color = "#FFFFFF"
            else:
                text_color = "#000000"
        else:
            text_color = "#000000"

        draw_text(cr, " " + self.title,
                  rect.x,
                  rect.y,
                  rect.width,
                  rect.height,
                  text_color = text_color,
                  alignment=pango.ALIGN_LEFT)


    def hover(self, column, offset_x, offset_y):
        self.is_hover = True
        self.emit_redraw_request()

    def unhover(self, column, offset_x, offset_y):
        self.is_hover = False
        self.emit_redraw_request()

    def highlight(self):
        self.is_highlight = True
        self.emit_redraw_request()

    def unhighlight(self):
        self.is_highlight = False
        self.emit_redraw_request()
