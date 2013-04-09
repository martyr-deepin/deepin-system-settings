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
from dtk.ui.treeview import TreeItem, TreeView
from dtk.ui.draw import draw_text, draw_line
from dtk.ui.utils import color_hex_to_cairo, cairo_disable_antialias
from accel_entry import AccelBuffer
from nls import _
from glib import markup_escape_text
from gtk import gdk
import gobject
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
                #print self.visible_items[select_row]
                self.emit("select", self.visible_items[select_row], select_row)
    
    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))
        cr.rectangle(x, y, w, h)
        cr.fill()
    
gobject.type_register(MyTreeView)

class BaseItem(TreeItem):
    '''the base TreeItem class'''

    def __init__(self):
        super(BaseItem, self).__init__()
        self.treeview = None
        self.height = 30
    
    def get_height(self):
        '''
        get height
        @return: the item height, a int type
        '''
        return self.height
    
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

gobject.type_register(BaseItem)

class SelectItem(BaseItem):
    '''a selection item in TreeView'''
    def __init__(self, text):
        super(SelectItem, self).__init__()
        self.text = text
        self.padding_x = 5
    
    def get_column_widths(self):
        return [-1]
    
    def get_column_renders(self):
        return [self.render_text]
        
    def render_text(self, cr, rect):
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
        cr.rectangle(rect.x+1, rect.y, rect.width-2, rect.height-1)
        cr.paint()
        draw_text(cr, self.text, rect.x+50+self.padding_x, rect.y, rect.width, rect.height, text_color=text_color)

gobject.type_register(SelectItem)

class LayoutItem(BaseItem):
    '''a selection item in TreeView'''
    def __init__(self, name, layout, variants=''):
        '''
        initialization function.
        @param name: the name to show, a string type.
        @param layout: the layout name, a string type.
        @param variants: the variants name, a string type.
        '''
        super(LayoutItem, self).__init__()
        try:
            self.name = markup_escape_text(name)
        except:
            self.name = " "
        self.layout = layout
        self.variants = variants
        self.padding_x = 5
    
    def get_layout(self):
        '''
        get layout name
        @return: the layout name, a string type
        '''
        return self.layout
    
    def get_column_widths(self):
        '''
        @return: all column width, a list type
        '''
        return [-1]
    
    def get_column_renders(self):
        return [self.render_text]
        
    def render_text(self, cr, rect):
        if self.is_select:
            text_color = "#FFFFFF"
            bg_color = "#3399FF"
        else:
            text_color = "#000000"
            bg_color = MODULE_BG_COLOR
        cr.set_source_rgb(*color_hex_to_cairo(bg_color))
        cr.rectangle(rect.x+1, rect.y, rect.width-2, rect.height-1)
        cr.paint()
        draw_text(cr, self.name, rect.x+self.padding_x, rect.y, rect.width, rect.height, text_color=text_color)

gobject.type_register(LayoutItem)


class ShortcutItem(BaseItem):
    '''a shortcut item in TreeView'''
    def __init__(self, description, keyname, name): 
        super(ShortcutItem, self).__init__()
        try:
            self.description = markup_escape_text(description)
        except:
            self.description = " "
        self.keyname = keyname
        self.name = name
        self.padding_x = 5
        self.accel_buffer = AccelBuffer()
        self.COLUMN_ACCEL = 1
    
    def get_column_widths(self):
        return [380, -1]
    
    def get_column_renders(self):
        return [self.render_description, self.render_keyname]
        
    def render_description(self, cr, rect):
        if self.is_select:
            text_color = "#FFFFFF"
            bg_color = "#3399FF"
        else:
            text_color = "#000000"
            bg_color = MODULE_BG_COLOR
        cr.set_source_rgb(*color_hex_to_cairo(bg_color))
        cr.rectangle(rect.x, rect.y, rect.width, rect.height-1)
        cr.paint()
        draw_text(cr, self.description, rect.x+self.padding_x, rect.y, rect.width, rect.height, text_color=text_color)
        #cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
        #draw_line(cr, rect.x, rect.y-1+rect.height, rect.x+rect.width, rect.y-1+rect.height)
    
    def render_keyname(self, cr, rect):
        if self.is_select:
            text_color = "#FFFFFF"
            bg_color = "#3399FF"
        else:
            text_color = "#000000"
            bg_color = MODULE_BG_COLOR
        cr.set_source_rgb(*color_hex_to_cairo(bg_color))
        cr.rectangle(rect.x, rect.y, rect.width, rect.height-1)
        cr.paint()
        draw_text(cr, self.keyname, rect.x+self.padding_x, rect.y, rect.width, rect.height, text_color=text_color)
        #cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
        #draw_line(cr, rect.x, rect.y-1+rect.height, rect.x+rect.width, rect.y-1+rect.height)
    
    def set_accel_buffer_from_event(self, event):
        '''
        set accel buffer value from an Event
        @param event: a gtk.gdk.KEY_PRESS
        '''
        if event.type != gdk.KEY_PRESS:
            return
        self.accel_buffer.set_state(event.state)
        self.accel_buffer.set_keyval(event.keyval)
    
    def set_accel_buffer_from_accel(self, accelerator):
        '''
        ser accel buffer value from an accelerator string
        @parse accelerator: a accelerator string
        '''
        self.accel_buffer.set_from_accel(accelerator)
    
    def update_accel_setting(self):
        ''' update the system setting '''
        setting_type = self.get_data("setting-type")
        if setting_type is None:
            return False
        settings = self.get_data("settings")
        if settings is None:
            return False
        accel_data = self.accel_buffer.get_accel_name()
        if setting_type == "gsettings":
            data_type = self.get_data('setting-data-type')
            if data_type == 'string':
                settings.set_string(self.name, accel_data)
            elif data_type == 'strv':
                if accel_data:
                    settings.set_strv(self.name, [accel_data])
                else:
                    settings.set_strv(self.name, [])
        else:
            gconf_dir = self.get_data("gconf-dir")
            settings.set_string("%s/binding" % (gconf_dir), accel_data)
        self.keyname = self.accel_buffer.get_accel_label()
        if self.keyname == '':
            self.keyname = _('disable')
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
        return True
gobject.type_register(ShortcutItem)
