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
from dtk.ui.utils import (color_hex_to_cairo, is_left_button)
from gtk import gdk
from gtk import accelerator_name, accelerator_parse, accelerator_get_label
from nls import _
import gobject


class MyTreeView(TreeView):
    ''' my TreeView'''
    __gsignals__ = {
        "select"  : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT, int)),
        "unselect": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "clicked" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT, int))}

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
        
    #def click_item(self, event):
        #cell = self.get_cell_with_event(event)
        #if cell != None:
            #(click_row, click_column, offset_x, offset_y) = cell
            
            #if self.left_button_press:
                #if click_row == None:
                    #self.unselect_all()
                #else:
                    #if self.enable_drag_drop and click_row in self.select_rows:
                        #self.start_drag = True
                        ## Record press_in_select_rows, disable select rows if mouse not move after release button.
                        #self.press_in_select_rows = click_row
                    #else:
                        #self.start_drag = False
                        #self.start_select_row = click_row
                        #self.set_select_rows([click_row])
                        
                        #self.visible_items[click_row].button_press(click_column, offset_x, offset_y)
                            
                #if is_double_click(event):
                    #self.double_click_row = copy.deepcopy(click_row)
                #elif is_single_click(event):
                    #self.single_click_row = copy.deepcopy(click_row)                
    
    def set_select_rows(self, rows):
        super(MyTreeView, self).set_select_rows(rows)
        if rows:
            for select_row in self.select_rows:
                self.emit("select", self.visible_items[select_row], select_row)
    
    #def release_item(self, event):
        #super(MyTreeView, self).release_item(event)
        #if is_left_button(event):
            #cell = self.get_cell_with_event(event)
            #if cell is not None:
                #(release_row, release_column, offset_x, offset_y) = cell
                #if release_row is not None:
                    #if self.single_click_row == release_row:
                        #self.emit("clicked", self.visible_items[release_row], release_column)

gobject.type_register(MyTreeView)
        

class BaseItem(TreeItem):
    '''the base TreeItem class'''

    def __init__(self):
        super(BaseItem, self).__init__()
        self.treeview = None
    
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
gobject.type_register(BaseItem)

class SelectItem(BaseItem):
    '''a selection item in TreeView'''
    def __init__(self, text):
        super(SelectItem, self).__init__()
        self.text = text
        self.height = 24
        self.padding_x = 5
    
    def get_height(self):
        return self.height
    
    def get_column_widths(self):
        return [-1]
    
    def get_column_renders(self):
        return [self.render_text]
        
    def render_text(self, cr, rect):
        if self.is_select:
            text_color = "#FFFFFF"
            bg_color = "#3399FF"
            cr.set_source_rgb(*color_hex_to_cairo(bg_color))
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.paint()
        else:
            text_color = "#000000"
        draw_text(cr, self.text, rect.x+self.padding_x, rect.y, rect.width, rect.height, text_color=text_color)
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
        self.name = name
        self.layout = layout
        self.variants = variants
        self.height = 35
        self.padding_x = 5
    
    def get_layout(self):
        '''
        get layout name
        @return: the layout name, a string type
        '''
        return self.layout
    
    def get_height(self):
        '''
        get height
        @return: the item height, a int type
        '''
        return self.height
    
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
            cr.set_source_rgb(*color_hex_to_cairo(bg_color))
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.paint()
        else:
            text_color = "#000000"
        draw_text(cr, self.name, rect.x+self.padding_x, rect.y, rect.width, rect.height, text_size=12, text_color=text_color)
gobject.type_register(LayoutItem)

class AccelBuffer(object):
    '''a buffer which store accelerator'''
    def __init__(self):
        super(AccelBuffer, self).__init__()
        self.state = None
        self.keyval = None
    
    def set_state(self, state):
        '''
        set state
        @param state: the state of the modifier keys, a GdkModifierType
        '''
        self.state = state & (~gdk.MOD2_MASK)
    
    def get_state(self):
        '''
        get state
        @return: the state of the modifier keys, a GdkModifierType or None
        '''
        return self.state
    
    def set_keyval(self, keyval):
        '''
        set keyval
        @param keyval: a keyval, an int type
        '''
        self.keyval = keyval
    
    def get_keyval(self):
        '''
        get keyval
        @return: a keyval, an int type or None
        '''
        return self.keyval
    
    def get_accel_name(self):
        '''
        converts the accelerator keyval and modifier mask into a string
        @return: a acceleratot string
        '''
        if self.state is None or self.keyval is None:
            return ''
        return accelerator_name(self.keyval, self.state)
    
    def get_accel_label(self):
        '''
        converts the accelerator keyval and modifier mask into a string
        @return: a accelerator string
        '''
        if self.state is None or self.keyval is None:
            return ''
        return accelerator_get_label(self.keyval, self.state)
    
    def set_from_accel(self, accelerator):
        '''
        parses the accelerator string and update keyval and state
        @parse accelerator: a accelerator string
        '''
        (self.keyval, self.state) = accelerator_parse(accelerator)
    
    def is_equal(self, accel_buffer):
        '''
        check an other AccelBuffer object is equal
        @param accel_buffer: a AccelBuffer object
        @return: True if their values are equal, otherwise False'''
        if self.get_state() == accel_buffer.get_state()\
                and self.get_keyval() == accel_buffer.get_keyval():
                return True
        else:
            return False

    def __eq__(self, accel_buffer):
        ''' '''
        return self.is_equal(accel_buffer)

class ShortcutItem(BaseItem):
    '''a shortcut item in TreeView'''
    def __init__(self, description, keyname, name): 
        super(ShortcutItem, self).__init__()
        self.description = description
        self.keyname = keyname
        self.name = name
        self.height = 24
        self.padding_x = 5
        self.accel_buffer = AccelBuffer()
        self.COLUMN_ACCEL = 1
    
    def get_height(self):
        return self.height
    
    def get_column_widths(self):
        return [400, 270]
    
    def get_column_renders(self):
        return [self.render_description, self.render_keyname]
        
    def render_description(self, cr, rect):
        if self.is_select:
            text_color = "#FFFFFF"
            bg_color = "#3399FF"
            cr.set_source_rgb(*color_hex_to_cairo(bg_color))
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.paint()
        else:
            text_color = "#000000"
        draw_text(cr, self.description, rect.x+self.padding_x, rect.y, rect.width, rect.height, text_color=text_color)
    
    def render_keyname(self, cr, rect):
        if self.is_select:
            text_color = "#FFFFFF"
            bg_color = "#3399FF"
            cr.set_source_rgb(*color_hex_to_cairo(bg_color))
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.paint()
        else:
            text_color = "#000000"
        draw_text(cr, self.keyname, rect.x+self.padding_x, rect.y, rect.width, rect.height, text_color=text_color)
    
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
            value = settings.get("%s/binding" % (gconf_dir))
            value.set_string(accel_data)
            settings.set("%s/binding" % (gconf_dir), value)
        self.keyname = self.accel_buffer.get_accel_label()
        if self.keyname == '':
            self.keyname = _('disable')
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
        return True
gobject.type_register(ShortcutItem)
