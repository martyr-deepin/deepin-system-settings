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
from dtk.ui.new_treeview import TreeItem, TreeView
from dtk.ui.draw import draw_text
from dtk.ui.utils import color_hex_to_cairo, cairo_disable_antialias
from nls import _
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
                 enable_hover=True,
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
    
    def set_select_rows(self, rows):
        super(MyTreeView, self).set_select_rows(rows)
        if rows:
            for select_row in self.select_rows:
                self.emit("select", self.visible_items[select_row], select_row)
    
    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))
        cr.rectangle(x, y, w, h)
        cr.fill()
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
            cr.set_line_width(1)
            cr.move_to(x+w-2, y)
            cr.line_to(x+w-2, y+h)
            cr.stroke()
    
gobject.type_register(MyTreeView)
        

class MyTreeItem(TreeItem):
    '''TreeItem class'''

    ACCOUNT_TYPE = ["Standard", "Administrator"]
    def __init__(self, icon, real_name, user_name, user_type, dbus_obj, is_myowner=False, is_head=False):
        '''
        initialization.
        @param icon: a gtk.gdk.Pixbuf type
        @param user_name: a string type
        @param user_type: a string type
        @param is_myowner: a bool type
        '''
        super(MyTreeItem, self).__init__()
        self.height = 55
        self.head_height = 35
        self.user_name_height = 25
        self.title_width = 250
        self.is_myowner = is_myowner
        self.is_head = is_head
        if is_myowner:
            self.title_height = 18
        else:
            self.title_height = 0
        self.padding_x = 5
        self.padding_y = 3
        self.icon = icon
        self.real_name = real_name
        self.user_name = user_name
        self.user_type = user_type
        self.dbus_obj = dbus_obj
        self.is_unique = True
    
    def get_height(self):
        if self.is_head:
            return self.height + 2 * self.title_height + self.head_height
        else:
            return self.height + 2 * self.title_height
    
    def get_column_widths(self):
        return [-1]
    
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

    def unhover(self, column, offset_x, offset_y):
        if not self.is_hover:
            return
        self.is_hover = False
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
        
    def hover(self, column, offset_x, offset_y):
        self.is_hover = True
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def get_column_renders(self):
        return [self.render_item]
    
    def render_item(self, cr, rect):
        #rect.x += 1
        #rect.width -=2
        #rect.height -= 2
        if self.is_head:
            rect.y += self.head_height
            rect.height -= self.head_height
        if self.is_hover and not self.is_select:
            text_color = "#000000"
            bg_color = app_theme.get_color("globalItemHover").get_color()
        elif self.is_select:
            text_color = "#FFFFFF"
            bg_color = app_theme.get_color("globalItemSelect").get_color()
        else:
            text_color = "#000000"
            bg_color = MODULE_BG_COLOR
        cr.set_source_rgb(*color_hex_to_cairo(bg_color))
        cr.rectangle(rect.x, rect.y+self.title_height, rect.width-4, rect.height-2*self.title_height-1)
        cr.fill()
        # draw account type text
        if self.is_myowner:
            text_color = "#000000"
            x1 = rect.x
            y1 = rect.y
            draw_text(cr, _("My Account"), x1+self.padding_x, y1, self.title_width, self.title_height, text_color=text_color)
            x2 = rect.x
            y2 = rect.y + self.height + self.title_height
            draw_text(cr, _("Other Accounts"), x2+self.padding_x, y2, self.title_width, self.title_height, text_color=text_color)
        self.render_icon(cr, gtk.gdk.Rectangle(rect.x+FRAME_LEFT_PADDING, rect.y, 55, rect.height))
        self.render_content(cr, gtk.gdk.Rectangle(rect.x+FRAME_LEFT_PADDING+55, rect.y, rect.width-55, rect.height), text_color)
    
    def render_content(self, cr, rect, text_color):
        # draw user name and account type
        x = rect.x+self.padding_x
        user_name_y = rect.y+self.title_height+self.padding_y
        if self.is_unique:
            if self.real_name:
                show_name = "<b>%s</b>" % self.real_name
            else:
                show_name = "<b>(%s)</b>" % self.user_name
        else:
            show_name = "<b>%s (%s)</b>" % (self.real_name, self.user_name)
        draw_text(cr, show_name,
                  x, user_name_y,
                  rect.width-self.padding_x,
                  self.user_name_height,
                  text_color=text_color)
        draw_text(cr, self.ACCOUNT_TYPE[self.user_type],
                  x, user_name_y+self.user_name_height,
                  rect.width-self.padding_x,
                  self.user_name_height,
                  text_color=text_color)
    
    def render_icon(self, cr, rect):
        if self.icon:
            cr.set_source_pixbuf(self.icon, rect.x+self.padding_x, rect.y+self.title_height+self.padding_y)
            cr.paint()
    
gobject.type_register(MyTreeItem)
