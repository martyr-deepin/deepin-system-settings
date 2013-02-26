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

from theme import app_theme
from deepin_utils.ipc import is_dbus_name_exists
from dtk.ui.utils import color_hex_to_cairo
from dtk.ui.line import HSeparator
from dtk.ui.box import ImageBox
from dtk.ui.label import Label
from dtk.ui.button import CheckButton, Button
from dtk.ui.combo import ComboBox
from dtk.ui.entry import InputEntry
from dtk.ui.constant import ALIGN_START, ALIGN_END
from constant import *
from nls import _
import gobject
import gtk
import dbus

class DesktopView(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)
        self.display_style_items = [(_("Default"), 0), 
                                    (_("Auto Hide"), 1), 
                                    (_("Invisible"), 2)]
        self.place_style_items = [(_("Buttom"), 0), 
                                  (_("Top"), 1)]
        self.icon_size_items = [(_("Default"), 0), 
                                (_("Small"), 1)]
        '''
        icon title
        '''
        self.icon_title_align = self.__setup_title_align(
            app_theme.get_pixbuf("desktop/icon.png"), 
            _("Desktop Icon"), 
            TEXT_WINDOW_TOP_PADDING, 
            TEXT_WINDOW_LEFT_PADDING)
        '''
        icon
        '''
        self.icon_align = self.__setup_align(padding_left = 225)
        self.icon_box = gtk.HBox(spacing = WIDGET_SPACING * 3)
        self.computer_checkbutton = self.__setup_checkbutton(_("Computer"))
        self.home_checkbutton = self.__setup_checkbutton(_("Home"))
        self.trash_checkbutton = self.__setup_checkbutton(_("Trash"))
        self.dsc_checkbutton = self.__setup_checkbutton(_("Software Center"))
        self.__widget_pack_start(self.icon_box, 
                                 [self.computer_checkbutton, 
                                  self.home_checkbutton, 
                                  self.trash_checkbutton, 
                                  self.dsc_checkbutton])
        self.icon_align.add(self.icon_box)
        '''
        dock title
        '''
        self.dock_title_align = self.__setup_title_align(
            app_theme.get_pixbuf("desktop/dock.png"), 
            _("Dock")) 
        '''
        display style
        '''
        self.display_style_align = self.__setup_align()
        self.display_style_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.display_style_label = self.__setup_label(_("Display Style"))
        self.display_style_combo = self.__setup_combo(self.display_style_items)
        self.display_style_combo.set_select_index(0)
        self.display_style_combo.connect("item-selected", self.__combo_item_selected, "display_style")
        self.__widget_pack_start(self.display_style_box, 
            [self.display_style_label, self.display_style_combo])
        self.display_style_align.add(self.display_style_box)
        '''
        place style
        '''
        self.place_style_align = self.__setup_align()
        self.place_style_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.place_style_label = self.__setup_label(_("Place Style"))
        self.place_style_combo = self.__setup_combo(self.place_style_items)
        self.place_style_combo.set_select_index(0)
        self.place_style_combo.connect("item-selected", self.__combo_item_selected, "place_style")
        self.__widget_pack_start(self.place_style_box, 
            [self.place_style_label, self.place_style_combo])
        self.place_style_align.add(self.place_style_box)
        '''
        icon size
        '''
        self.icon_size_align = self.__setup_align()
        self.icon_size_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.icon_size_label = self.__setup_label(_("Icon Size"))
        self.icon_size_combo = self.__setup_combo(self.icon_size_items)
        self.icon_size_combo.set_select_index(0)
        self.icon_size_combo.connect("item-selected", self.__combo_item_selected, "icon_size")
        self.__widget_pack_start(self.icon_size_box, 
            [self.icon_size_label, self.icon_size_combo])
        self.icon_size_align.add(self.icon_size_box)
        '''
        greeter
        '''
        self.greeter_title_align = self.__setup_title_align(                       
            app_theme.get_pixbuf("desktop/lock.png"),                     
            _("Login &amp;&amp; Lock"),                                                  
            TEXT_WINDOW_TOP_PADDING,                                            
            TEXT_WINDOW_LEFT_PADDING)
        '''
        greeter
        '''
        self.greeter_align = self.__setup_align()
        self.greeter_box = gtk.HBox()
        self.greeter_label = self.__setup_label(_("Login Page"))
        self.greeter_entry_align = self.__setup_align(
            padding_left = WIDGET_SPACING, padding_top = 3)
        self.greeter_entry = self.__setup_entry()
        self.greeter_entry_align.add(self.greeter_entry)
        self.greeter_button = self.__setup_button(_("Select"))
        self.__widget_pack_start(self.greeter_box, 
                                 [self.greeter_label, 
                                  self.greeter_entry_align, 
                                  self.greeter_button])
        self.greeter_align.add(self.greeter_box)
        '''
        lock
        '''
        self.lock_align = self.__setup_align()
        self.lock_box = gtk.HBox()
        self.lock_label = self.__setup_label(_("Lock Page"))
        self.lock_entry_align = self.__setup_align(
            padding_left = WIDGET_SPACING, padding_top = 3)
        self.lock_entry = self.__setup_entry()
        self.lock_entry_align.add(self.lock_entry)
        self.lock_button = self.__setup_button(_("Select"))
        self.__widget_pack_start(self.lock_box, 
                                 [self.lock_label, 
                                  self.lock_entry_align, 
                                  self.lock_button])
        self.lock_align.add(self.lock_box)
        '''
        this->gtk.VBox pack_start
        '''
        self.__widget_pack_start(self, 
                                 [self.icon_title_align, 
                                  self.icon_align, 
                                  self.dock_title_align, 
                                  self.display_style_align, 
                                  self.place_style_align, 
                                  self.icon_size_align, 
                                  self.greeter_title_align, 
                                  self.greeter_align, 
                                  self.lock_align])

        self.connect("expose-event", self.__expose)

        self.__send_message("status", ("desktop", ""))

    def __handle_dbus_replay(self, *reply):                                     
        pass                                                                    
                                                                                
    def __handle_dbus_error(self, *error):                                      
        pass                                                                    
                                                                                
    def __send_message(self, message_type, message_content):                    
        if is_dbus_name_exists(APP_DBUS_NAME):                                  
            bus_object = dbus.SessionBus().get_object(APP_DBUS_NAME, APP_OBJECT_NAME)
            method = bus_object.get_dbus_method("message_receiver")             
            method(message_type,                                                
                   message_content,                                             
                   reply_handler=self.__handle_dbus_replay,                     
                   error_handler=self.__handle_dbus_error)       

    def __setup_separator(self):                                                
        hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        hseparator.set_size_request(500, 10)                                    
        return hseparator                                                       
                                                                                
    def __setup_title_label(self,                                               
                            text="",                                            
                            text_color=app_theme.get_color("globalTitleForeground"),
                            text_size=TITLE_FONT_SIZE,                          
                            text_x_align=ALIGN_START,                           
                            label_width=180):                                   
        return Label(text = text,                                               
                     text_color = text_color,                                   
                     text_size = text_size,                                     
                     text_x_align = text_x_align,                               
                     label_width = label_width, 
                     enable_select = False, 
                     enable_double_click = False)     

    def __setup_title_align(self, 
                            pixbuf, 
                            text, 
                            padding_top=FRAME_TOP_PADDING, 
                            padding_left=TEXT_WINDOW_LEFT_PADDING):
        align = self.__setup_align(padding_top = padding_top, padding_left = padding_left)              
        align_box = gtk.VBox(spacing = WIDGET_SPACING)                             
        title_box = gtk.HBox(spacing = WIDGET_SPACING)                             
        image = ImageBox(pixbuf)                                                   
        label = self.__setup_title_label(text)                                     
        separator = self.__setup_separator()                                       
        self.__widget_pack_start(title_box, [image, label])                        
        self.__widget_pack_start(align_box, [title_box, separator])                
        align.add(align_box)                                                       
        return align        

    def reset(self):
        self.__send_message("status", ("desktop", _("Reset to default value")))

    def __expose(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation

        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                                               
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)                                                 
        cr.fill()

    def __setup_checkbutton(self, label_text, padding_x=0):
        return CheckButton(label_text, padding_x)

    def __setup_button(self, label):
        return Button(label)

    def __setup_label(self, text="", text_size=CONTENT_FONT_SIZE, align=ALIGN_END):
        return Label(text, None, text_size, align, 200, False, False, False)

    def __setup_combo(self, items=[]):
        combo = ComboBox(items, None, 0, 285)
        combo.set_size_request(-1, WIDGET_HEIGHT)
        return combo

    def __setup_entry(self, content=""):
        entry = InputEntry(content)
        entry.set_size(215, WIDGET_HEIGHT)
        return entry

    def __setup_align(self, 
                      padding_top=8, 
                      padding_bottom=0, 
                      padding_left=TEXT_WINDOW_LEFT_PADDING + IMG_WIDTH + WIDGET_SPACING, 
                      padding_right=0):
        align = gtk.Alignment()
        align.set(0.0, 0.5, 0, 0)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        return align

    def __widget_pack_start(self, parent_widget, widgets=[]):
        if parent_widget == None:
            return
        for item in widgets:
            parent_widget.pack_start(item, False, False)

    def __combo_item_selected(self, widget, item_text=None, item_value=None, item_index=None, object=None):
        return

gobject.type_register(DesktopView)        
