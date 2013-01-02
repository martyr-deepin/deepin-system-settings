#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
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
from dtk.ui.utils import color_hex_to_cairo, is_dbus_name_exists
from dtk.ui.label import Label
from dtk.ui.button import Button
import gobject
import gtk
import dbus
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

        self.module_id = None

        self.__is_init_ui = False
        

    def __init_ui(self):
        self.status_label = self.__setup_label("")
        self.buttons_align = self.__setup_align(padding_top = 7, 
                                                padding_left = 100, 
                                                padding_right = TEXT_WINDOW_RIGHT_WIDGET_PADDING)
        self.buttons_box = gtk.HBox()
        self.reset_button = Button("恢复默认")
        self.reset_button.connect("clicked", self.__reset_button_clicked)
        '''
        TODO: it need to consider about other module pack_start button into buttons_box
        '''
        self.buttons_box.pack_start(self.reset_button)
        self.buttons_align.add(self.buttons_box)
        self.pack_start(self.status_label)
        self.pack_start(self.buttons_align)
        self.set_size_request(-1, STATUS_HEIGHT)
        self.connect("expose-event", self.__expose)

        self.__is_init_ui = True

    def __handle_dbus_reply(*reply):                                                  
        pass

    def __handle_dbus_error(*error):                                                  
        pass

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
    
    def set_status(self, status):
        self.status_label.set_text(status)
    
    def __expose(self, widget, event):
        cr = widget.window.cairo_create()                                       
        rect = widget.allocation                                                
        
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                     
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)                       
        cr.fill()
    
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
                      label_width = label_width)
        return label

gobject.type_register(FootBox)
