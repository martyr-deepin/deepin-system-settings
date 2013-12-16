#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Zhai Xiang
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

from dtk.ui.constant import ALIGN_MIDDLE
from dtk.ui.utils import color_hex_to_cairo, container_remove_all
from deepin_utils.ipc import is_dbus_name_exists
from dtk.ui.draw import draw_line
from dtk.ui.label import Label
from dtk.ui.button import Button
import gobject
import gtk
import dbus
from nls import _
from constant import *
    
class FootBox(gtk.HBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        gtk.HBox.__init__(self)

        self.button_width = 80

        self.module_id = None

        self.buttons_list = []
        self.__setup_reset_button()
        self.buttons_list.append(self.reset_button)

        self.__is_init_ui = False
   
    def __setup_reset_button(self):
        self.reset_button = Button(_("Reset"))
        self.reset_button.set_size_request(self.button_width, WIDGET_HEIGHT)
        self.reset_button.connect("clicked", self.__reset_button_clicked)

    def __setup_buttons_align(self, list):
        buttons_align = self.__setup_align(padding_top = 7,                   
            padding_left = 80 - (len(list) - 1) * 10,                
            padding_right = TEXT_WINDOW_RIGHT_WIDGET_PADDING / 5)
        buttons_box = gtk.HBox(spacing = 5)                  
        i = 0
        while i < len(list):
            buttons_box.pack_start(list[i]) 
            i += 1

        buttons_align.add(buttons_box)

        return buttons_align

    def __init_ui(self):
        self.status_label = self.__setup_label("")
        self.right_box = gtk.VBox()
        self.buttons_align = self.__setup_buttons_align(self.buttons_list)
        self.right_box.pack_start(self.buttons_align)
        
        self.pack_start(self.status_label)
        self.pack_start(self.right_box)
        self.set_size_request(-1, STATUS_HEIGHT)
        
        self.connect("expose-event", self.__expose)
        
        self.__is_init_ui = True

    def __handle_dbus_reply(*reply):                                                  
        pass

    def __handle_dbus_error(*error):                                                  
        pass

    def __add_button_clicked(self, widget, argv):                                      
        bus = dbus.SessionBus()                                                              
        module_dbus_name = "com.deepin.%s_settings" % (self.module_id)                  
        module_object_name = "/com/deepin/%s_settings" % (self.module_id)                  
        if is_dbus_name_exists(module_dbus_name):                                       
            bus_object = bus.get_object(module_dbus_name, module_object_name)       
            method = bus_object.get_dbus_method("message_receiver")                 
            method("add_button_cb",                                                        
                   argv,                                                             
                   reply_handler=self.__handle_dbus_reply,                          
                   error_handler=self.__handle_dbus_error                          
                  )                    

    def __reset_button_clicked(self, widget):
        bus = dbus.SessionBus()                                                     
        module_dbus_name = "com.deepin.%s_settings" % (self.module_id)                   
        module_object_name = "/com/deepin/%s_settings" % (self.module_id)                
        if is_dbus_name_exists(module_dbus_name):                                   
            bus_object = bus.get_object(module_dbus_name, module_object_name)          
            method = bus_object.get_dbus_method("message_receiver")                 
            method("reset",                                                    
                   "",                      
                   reply_handler=self.__handle_dbus_reply,                                 
                   error_handler=self.__handle_dbus_error                  
                  )         
    
    def hide(self):
        self.hide_all()

    def show(self, module_id):
        self.module_id = module_id

        if not self.__is_init_ui:
            self.__init_ui()
       
        self.show_all()

    def hide_reset(self):
        self.reset_button.set_child_visible(False)
   
    def show_reset(self):
        self.reset_button.set_child_visible(True)

    def add_button(self, add_button):
        container_remove_all(self.buttons_align.get_children()[0])

        self.__setup_reset_button()
        button = Button(add_button)
        button.set_size_request(self.button_width, WIDGET_HEIGHT)
        button.connect("clicked", self.__add_button_clicked, add_button)
        self.buttons_list = []
        self.buttons_list.append(button)
        self.buttons_list.append(self.reset_button)
        self.buttons_align = self.__setup_buttons_align(self.buttons_list)        
        self.right_box.pack_start(self.buttons_align)

    def hide_status(self):
        self.status_label.set_text("")

    def set_status(self, status):
        self.status_label.set_text(status)
        gobject.timeout_add(3000, self.hide_status)
    
    def __expose(self, widget, event):
        cr = widget.window.cairo_create()                                       
        rect = widget.allocation                                                
        
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                     
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)                       
        cr.fill()

        cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
        draw_line(cr, rect.x, rect.y + 1, rect.x + rect.width, rect.y + 1)
    
    def __setup_align(self, 
                      xalign=0, 
                      yalign=0, 
                      xscale=0, 
                      yscale=0, 
                      padding_top=0, 
                      padding_bottom=0, 
                      padding_left=FRAME_LEFT_PADDING,
                      padding_right=0):
        align = gtk.Alignment()
        align.set(xalign, yalign, xscale, yscale)
        align.set_padding(padding_top, 
                          padding_bottom, 
                          padding_left, 
                          padding_right)
        return align

    def __setup_label(self, 
                      text="", 
                      text_size=CONTENT_FONT_SIZE, 
                      label_width=600):
        label = Label(text = text, 
                      text_size = text_size, 
                      text_x_align = ALIGN_MIDDLE, 
                      label_width = label_width, 
                      enable_select = False, 
                      )
        return label

gobject.type_register(FootBox)
