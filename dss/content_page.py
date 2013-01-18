#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
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

import gtk
import gobject

class ContentPage(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self, module_id):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)
        rc_str = "style 'my_style' {\n  bg[NORMAL] = \"%s\"\n }\nwidget '*' style 'my_style'" % "#FFFFFF"
        gtk.rc_parse_string(rc_str)          
        self.module_id = module_id
        self.socket = None
        self.connect("realize", self._add_socket)
        
    def _add_socket(self, w):
        #must create an new socket, because socket will be destroyed when it reparent!!!
        if self.socket:
            self.socket.destroy()
        self.socket = gtk.Socket()
        self.pack_start(self.socket, True, True)
        self.socket.realize()

    def add_plug_id(self, plug_id):
        self._add_socket(None)
        self.socket.add_id(plug_id)
        self.show_all()
                
gobject.type_register(ContentPage)

class ContentPageInfo(object):
    '''
    class docs
    '''
	
    def __init__(self, slider):
        '''
        init docs
        '''
        self.slider = slider
        self.page_dict = {}
        self.active_module_id = 0
        
    def set_active_module_id(self, module_id):
        self.active_module_id = module_id
        
    def get_active_module_id(self):
        return self.active_module_id
        
    def create_content_page(self, module_id):
        content_page = ContentPage(module_id)
        self.page_dict[module_id] = content_page
        self.slider.append_page(content_page)
    
    def get_content_page(self, module_id):
        if not self.page_dict.has_key(module_id):
            self.create_content_page(module_id)
            
        return self.page_dict[module_id]
