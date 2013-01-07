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

import pango
from dtk.ui.new_treeview import TreeItem
from dtk.ui.draw import draw_text


from ui.utils import (draw_single_mask)


class ExpandItem(TreeItem):
    
    def __init__(self, title, column_index=0):
        TreeItem.__init__(self)
        self.column_index = column_index
        self.side_padding = 5
        self.item_height = 37
        self.title = title
        self.item_width = -1
        self.child_items = []
        self.title_padding_x = 10
        self.widget = None
        
    def get_height(self):    
        return self.item_height
    
    def get_column_widths(self):
        return (self.item_width,)
    
    def get_column_renders(self):
        return (self.render_title,)
    
    def unselect(self):
        self.is_select = False
        self.emit_redraw_request()
        
    def emit_redraw_request(self):    
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
            
    def select(self):        
        self.is_select = True
        self.emit_redraw_request()
        
    def render_title(self, cr, rect):        
        # Draw select background.
            
        # if self.is_select:    
        #     draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemHighlight")
        # elif self.is_hover:
        #     draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemHover")
        
        # if self.is_select:
        #     text_color = "#FFFFFF"
        # else:    
        #     text_color = "#000000"
        text_color = "#000000"
                
        draw_text(cr, "<b>%s</b>" % self.title, rect.x + self.title_padding_x, rect.y, 
                  rect.width - self.title_padding_x, rect.height, text_size=10, 
                  text_color = text_color,
                  alignment=pango.ALIGN_LEFT)    
        
    def unhover(self, column, offset_x, offset_y):
        self.is_hover = False
        self.emit_redraw_request()
    
    def hover(self, column, offset_x, offset_y):
        self.is_hover = True
        self.emit_redraw_request()
        
    def button_press(self, column, offset_x, offset_y):
        pass
    
    def single_click(self, column, offset_x, offset_y):
        pass

    def double_click(self, column, offset_x, offset_y):
        if self.is_expand:
            self.unexpand()
        else:
            self.expand()
    
    def add_child_item(self):        
        self.add_items_callback(self.child_items, self.row_index + 1)
    
    def delete_child_item(self):
        self.delete_items_callback(self.child_items)
        
    def expand(self):
        self.is_expand = True
        self.add_child_item()
        self.emit_redraw_request()
    
    def unexpand(self):
        self.is_expand = False
        self.delete_child_item()
        self.emit_redraw_request()
        
    def try_to_expand(self):    
        if not self.is_expand:
            self.expand()
            
    def add_childs(self, child_items, pos=None, expand=False):    
        items = []
        for child_item in child_items:
            items.append(NormalItem(child_item[0], child_item[1], self.column_index + 1))
            
        for item in items:    
            item.parent_item = self
            
        if pos is not None:    
            for item in items:
                self.child_items.insert(pos, item)
                pos += 1
        else:            
            self.child_items.extend(items)
            
        if expand:    
            self.expand()
            
        return items    
            
    def __repr__(self):        
        return "<ExpandItem %s>" % self.title
        
class NormalItem(TreeItem):        
    def __init__(self, title, widget, column_index=0):
        TreeItem.__init__(self)
        self.column_index = column_index
        self.side_padding = 5
        if column_index > 0:
            self.item_height = 30
        else:    
            self.item_height = 37
            
        self.title = title
        self.item_width = -1
        self.title_padding_x = 12
        self.column_offset = 15
        self.widget = widget
        
    def get_height(self):    
        return self.item_height
    
    def get_column_widths(self):
        return (self.item_width,)
    
    def get_column_renders(self):
        return (self.render_title,)
    
    def unselect(self):
        self.is_select = False
        self.emit_redraw_request()
        
    def emit_redraw_request(self):    
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
            
    def select(self):        
        self.is_select = True
        self.emit_redraw_request()
        
    def render_title(self, cr, rect):        
        # Draw select background.
            
        if self.is_select:    
            draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemHighlight")
        elif self.is_hover:
            draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemHover")
        
        if self.is_select:
            text_color = "#FFFFFF"
        else:    
            text_color = "#000000"
            
            
        column_offset = self.column_offset * self.column_index    
        draw_text(cr, self.title, rect.x + self.title_padding_x + column_offset,
                  rect.y, rect.width - self.title_padding_x - column_offset ,
                  rect.height, text_size=10, 
                  text_color = text_color,
                  alignment=pango.ALIGN_LEFT)    
        
    def unhover(self, column, offset_x, offset_y):
        self.is_hover = False
        self.emit_redraw_request()
    
    def hover(self, column, offset_x, offset_y):
        self.is_hover = True
        self.emit_redraw_request()
        
    def button_press(self, column, offset_x, offset_y):
        pass
    
    def single_click(self, column, offset_x, offset_y):
        pass
    
    def set_title(self, title):
        self.title = title
        self.emit_redraw_request()

    def __repr__(self):        
        return "<NormalItem %s>" % self.title
    
    
    
