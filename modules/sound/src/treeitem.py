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
from dtk.ui.utils import (color_hex_to_cairo, is_left_button, 
                          is_double_click, is_single_click)
#from gtk import gdk
#from gtk import accelerator_name, accelerator_parse, accelerator_get_label
#from nls import _
import gobject
import copy


class MyTreeView(TreeView):
    ''' my TreeView'''
    __gsignals__ = {
        "select"  : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.GObject, int)),
        "unselect": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "clicked" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.GObject, int))}

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
        with self.keep_select_status():
            if clear_first:
                self.visible_items = []
            
            if insert_pos == None:
                self.visible_items += items
            else:
                self.visible_items = self.visible_items[0:insert_pos] + items + self.visible_items[insert_pos::]
            
            # Update redraw callback.
            # Callback is better way to avoid perfermance problem than gobject signal.
            for item in items:
                item.redraw_request_callback = self.redraw_request
                item.add_items_callback = self.add_items
                item.delete_items_callback = self.delete_items
                item.treeview = self
            
            self.update_item_index()    
            
            self.update_item_widths()
                
            self.update_vadjustment()
        
    def click_item(self, event):
        cell = self.get_cell_with_event(event)
        if cell != None:
            (click_row, click_column, offset_x, offset_y) = cell
            
            if self.left_button_press:
                if click_row == None:
                    self.unselect_all()
                else:
                    if self.enable_drag_drop and click_row in self.select_rows:
                        self.start_drag = True
                        # Record press_in_select_rows, disable select rows if mouse not move after release button.
                        self.press_in_select_rows = click_row
                    else:
                        self.start_drag = False
                        self.start_select_row = click_row
                        self.set_select_rows([click_row])
                        
                        self.visible_items[click_row].button_press(click_column, offset_x, offset_y)
                            
                if is_double_click(event):
                    self.double_click_row = copy.deepcopy(click_row)
                elif is_single_click(event):
                    self.single_click_row = copy.deepcopy(click_row)                
    
    def set_select_rows(self, rows):
        for select_row in self.select_rows:
            self.visible_items[select_row].unselect()
            
        self.select_rows = rows
        
        if rows == []:
            self.start_select_row = None
        else:
            for select_row in self.select_rows:
                self.visible_items[select_row].select()
                self.emit("select", self.visible_items[select_row], select_row)
    
    def release_item(self, event):
        if is_left_button(event):
            cell = self.get_cell_with_event(event)
            if cell is not None:
                (release_row, release_column, offset_x, offset_y) = cell
                
                if release_row is not None:
                    if self.double_click_row == release_row:
                        self.visible_items[release_row].double_click(release_column, offset_x, offset_y)
                    elif self.single_click_row == release_row:
                        self.emit("clicked", self.visible_items[release_row], release_column)
                        self.visible_items[release_row].single_click(release_column, offset_x, offset_y)
                
                if self.start_drag and self.is_in_visible_area(event):
                    self.drag_select_items_at_cursor()
                    
                self.double_click_row = None    
                self.single_click_row = None    
                self.start_drag = False
                
                # Disable select rows when press_in_select_rows valid after button release.
                if self.press_in_select_rows:
                    self.set_select_rows([self.press_in_select_rows])
                    self.start_select_row = self.press_in_select_rows
                    self.press_in_select_rows = None
                
                self.set_drag_row(None)
gobject.type_register(MyTreeView)
        

class MyTreeItem(TreeItem):
    '''TreeItem class'''
    __gsignals__ = {"select": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (int,))}

    def __init__(self, icon, content):
        '''
        initialization.
        @param icon: a gtk.gdk.Pixbuf type
        @param content: a string type
        '''
        super(MyTreeItem, self).__init__()
        self.treeview = None
        self.height = 30
        self.padding_x = 5
        self.icon = icon
        self.content = content
    
    def get_height(self):
        return self.height
    
    def get_column_widths(self):
        return [30, -1]
    
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
        #self.emit("select", self.row_index)
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def get_column_renders(self):
        return [self.render_icon, self.render_content]
    
    def render_content(self, cr, rect):
        if self.is_select:
            text_color = "#FFFFFF"
            bg_color = "#3399FF"
            cr.set_source_rgb(*color_hex_to_cairo(bg_color))
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.paint()
        else:
            text_color = "#000000"
        draw_text(cr, self.content, rect.x+self.padding_x, rect.y, rect.width-self.padding_x, rect.height, text_color=text_color)
    
    def render_icon(self, cr, rect):
        if self.is_select:
            bg_color = "#3399FF"
            cr.set_source_rgb(*color_hex_to_cairo(bg_color))
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.paint()
        cr.set_source_pixbuf(self.icon, rect.x+self.padding_x, rect.y)
        cr.paint()
    
gobject.type_register(MyTreeItem)
