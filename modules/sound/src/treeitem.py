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

#from theme import app_theme
from dtk.ui.new_treeview import TreeItem, TreeView
from dtk.ui.draw import draw_text
from dtk.ui.utils import color_hex_to_cairo, cairo_disable_antialias
import gobject
import gtk
from constant import *


class MyTreeView(TreeView):
    ''' my TreeView'''
    __gsignals__ = {
        "select"  : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, int)),
        "unselect": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())}

    def __init__(self,
                 items=[],
                 drag_data=None,
                 enable_hover=False,
                 enable_highlight=False,
                 enable_multiple_select=False,
                 enable_drag_drop=False,
                 drag_icon_pixbuf=None,
                 start_drag_offset=50,
                 mask_bound_height=24,
                 right_space=0,
                 top_bottom_space=3
                 ):
        super(MyTreeView, self).__init__(
                items, drag_data, enable_hover, enable_highlight,
                enable_multiple_select, enable_drag_drop, drag_icon_pixbuf,
                start_drag_offset, mask_bound_height, right_space, top_bottom_space)
        self.keymap["Shift + Up"] = self.keymap["Up"]
        self.keymap["Shift + Down"] = self.keymap["Down"]
        self.keymap["Shift + Home"] = self.keymap["Home"]
        self.keymap["Shift + End"] = self.keymap["End"]
        self.keymap["Ctrl + Up"] = self.keymap["Up"]
        self.keymap["Ctrl + Down"] = self.keymap["Down"]
        del self.keymap["Ctrl + a"]
        del self.keymap["Delete"]
    
    def add_items(self, items, insert_pos=None, clear_first=False):
        '''
        Add items.
        '''
        super(MyTreeView, self).add_items(items, insert_pos, clear_first)
        with self.keep_select_status():
            for item in items:
                item.treeview = self
        
    def set_select_rows(self, rows):
        super(MyTreeView, self).set_select_rows(rows)
        if rows:
            for select_row in self.select_rows:
                self.emit("select", self.visible_items[select_row], select_row)
    
    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BG_COLOR))
        cr.rectangle(x, y, w, h)
        cr.fill()
    
gobject.type_register(MyTreeView)
        

class MyTreeItem(TreeItem):
    '''TreeItem class'''

    def __init__(self, icon, content, obj_path=None):
        '''
        initialization.
        @param icon: a DynamicPixbuf object
        @param content: a string object
        '''
        super(MyTreeItem, self).__init__()
        self.treeview = None
        self.height = 30
        self.padding_x = 5
        self.icon = icon
        self.content = content
        self.obj_path = obj_path
    
    def get_height(self):
        return self.height
    
    def get_column_widths(self):
        return [-1]
    
    def get_treeview(self):
        '''
        get treeview
        @return: a TreeView type
        '''
        return self.treeview
    
    def unselect(self):
        if not self.is_select:
            return
        self.is_select = False
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
        
    def select(self):
        self.is_select = True
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def get_column_renders(self):
        return [self.render_item]

    def render_item(self, cr, rect):
        if self.is_select:
            text_color = "#FFFFFF"
            bg_color = "#3399FF"
        else:
            text_color = "#000000"
            bg_color = MODULE_BG_COLOR
        cr.set_source_rgb(*color_hex_to_cairo(bg_color))
        cr.rectangle(rect.x, rect.y, rect.width, rect.height-1)
        cr.paint()
        self.render_icon(cr, rect)
        width = self.icon.get_pixbuf().get_width()
        self.render_content(cr, gtk.gdk.Rectangle(rect.x+width+self.padding_x, rect.y, rect.width-width-self.padding_x, rect.height), text_color)
        cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
        # draw line
        with cairo_disable_antialias(cr):    
            cr.set_line_width(1)
            cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
            cr.move_to(rect.x, rect.y-1+rect.height)
            cr.line_to(rect.x+rect.width, rect.y-1+rect.height)
            cr.stroke()
    
    def render_content(self, cr, rect, text_color):
        draw_text(cr, self.content, rect.x+self.padding_x, rect.y, rect.width-self.padding_x, rect.height-1, text_color=text_color)
    
    def render_icon(self, cr, rect):
        cr.set_source_pixbuf(self.icon.get_pixbuf(), rect.x+self.padding_x, rect.y)
        cr.paint()
    
gobject.type_register(MyTreeItem)
