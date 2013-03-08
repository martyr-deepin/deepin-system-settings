#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
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
import os
import copy
from dtk.ui.label import Label
from dtk.ui.button import Button
from dtk.ui.iconview import IconView
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.dialog import ConfirmDialog
from ui.wallpaper_item import SelectItem
from helper import event_manager
from monitor import LibraryMonitor
from xdg_support import get_images_dir
import common
from nls import _
from constant import CONTENT_FONT_SIZE

class SelectView(IconView):
    SHOW_ITEM_COUNT = 16
    
    __gsignals__ = {                                                            
        "loaded" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),}

    def __init__(self, monitor_dir, padding_x=8, padding_y=10, filter_dir=None):
        IconView.__init__(self, padding_x=padding_x, padding_y=padding_y)
        
        self.monitor_dir = monitor_dir
        self.filter_dir = filter_dir
        self.library_monitor = LibraryMonitor(monitor_dir)
        self.library_monitor.set_property("monitored", True)
        self.library_monitor.connect("file-added", self.on_library_file_added)
        self.library_monitor.connect("folder-added", self.on_library_folder_added)
        self.library_monitor.connect("location-removed", self.on_library_location_removed)
        self.__image_index = 0
        self.__init_monitor_images()

    def on_library_file_added(self, obj, gfile):    
        is_image_type = common.gfile_is_image(gfile)
        if is_image_type:
            image_path = gfile.get_path()
            if not self.is_exists(image_path):
                self.add_items([SelectItem(image_path)])
                
    def on_library_folder_added(self, obj, gfile):            
        items = []
        for image_path in common.walk_images(gfile.get_path(), filter_dir = self.filter_dir):
            if not self.is_exists(image_path):
                items.append(SelectItem(image_path))
        if items:        
            self.add_items(items)
            
    def on_library_location_removed(self, obj, gfile):        
        file_path = gfile.get_path()
        items = filter(lambda item: item.image_path.startswith(file_path), self.items)
        if items:
            event_manager.emit("wallpapers-deleted", map(lambda item: item.image_path, items))            
            self.delete_items(items)
            
    def is_exists(self, image_path):        
        for item in self.items:
            if image_path == item.image_path:
                return True
        return False    
    
    '''
    divide BIG images count into several small sections
    '''
    @common.threaded
    def __init_monitor_images(self):    
        items = []
        image_paths = []
        i = 0
        
        self.set_loading(True)
        for image_path in common.walk_images(self.monitor_dir, filter_dir = self.filter_dir):
            image_paths.append(image_path)
        
        while self.__image_index < len(image_paths) and i < self.SHOW_ITEM_COUNT:
            items.append(SelectItem(image_paths[self.__image_index]))
            self.__image_index += 1
            i += 1

        if items:    
            self.add_items(items)
        self.set_loading(False)

    @common.threaded
    def __more_monitor_images(self):
        items = []
        i = 0
        
        self.set_loading(True)
        while self.__image_index < len(image_paths) and i < self.SHOW_ITEM_COUNT:
            items.append(SelectItem(image_paths[self.__image_index]))              
            self.__image_index += 1
            i += 1
                                                                                   
        if items:                                                                  
            self.add_items(items)
        self.set_loading(False)

    def add_images(self, images):        
        items = map(lambda image: SelectItem(image), images)
        self.add_items(items)
        
    def get_scrolled_window(self):    
        scrolled_window = ScrolledWindow()
        scrolled_window.connect("vscrollbar-state-changed", self.__on_vscrollbar_state_changed)
        scrolled_window.add_child(self)
        return scrolled_window

    def __on_vscrollbar_state_changed(self, widget, argv):                      
        if argv != "bottom":
            return

        self.__init_monitor_images()

    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()

    def delete(self):
        for item in self.items:
            if item.is_tick:
                os.remove(item.image_path)
                event_manager.emit("delete-downloaded-wallpaper", item)

        self.queue_draw()

    def is_select_all(self):
        for item in self.items:
            if not item.is_tick:
                return False

        return True

    def select_all(self):
        is_select_all = self.is_select_all()                                    
                                                                                
        for item in self.items:                                                 
            if is_select_all:
                item.untick()
            else:
                item.tick()

    def emit_add_wallpapers(self):    
        tick_items = filter(lambda item : item.is_tick, self.items)
        if tick_items:
            image_paths = map(lambda item: item.image_path, tick_items)
            event_manager.emit("add-wallpapers", image_paths)
        
class SystemPage(gtk.VBox):        
    def __init__(self, monitor_dir):
        
        gtk.VBox.__init__(self)

        self.theme = None

        self.set_spacing(10)
        
        self.select_view = SelectView(monitor_dir)
        self.select_view_sw = self.select_view.get_scrolled_window()
        
        self.back_button = Button(_("Back"))                                    
        self.back_button.connect("clicked", self.__on_back)
        self.select_all_button = Button(_("Select All"))
        self.select_all_button.connect("clicked", self.on_select_all)
        add_button = Button(_("Add"))
        add_button.connect("clicked", self.on_add_wallpapers)
        
        control_box = gtk.HBox(spacing = 10)
        control_box.pack_start(self.back_button, False, False)
        control_box.pack_start(self.select_all_button, False, False)
        control_box.pack_start(add_button, False, False)
        
        control_align = gtk.Alignment()
        control_align.set(1.0, 0.5, 0, 0)
        control_align.set_padding(0, 5, 0, 10)
        control_align.add(control_box)
        self.pack_start(self.select_view_sw, True, True)
        self.pack_start(control_align, False, True)

        event_manager.add_callback("select-select-wallpaper", self.__on_select_select_wallpaper)
  
    def __on_back(self, widget):
        event_manager.emit("back-to-detailpage", self.theme)

    def set_theme(self, theme):
        self.theme = theme

    def __on_select_select_wallpaper(self, name, obj, select_item):
        if self.select_view.is_select_all():                                    
            self.select_all_button.set_label(_("UnSelect All"))                 
        else:                                                                   
            self.select_all_button.set_label(_("Select All"))

    def on_select_all(self, widget):
        self.select_view.select_all()

        if self.select_view.is_select_all():
            self.select_all_button.set_label(_("UnSelect All"))
        else:
            self.select_all_button.set_label(_("Select All"))

    def on_add_wallpapers(self, widget):    
        self.select_view.emit_add_wallpapers()

class PicturePage(gtk.VBox):                                                     
    def __init__(self, monitor_dir):                                            
                                                                                
        gtk.VBox.__init__(self)                                                 
        self.set_spacing(10)                                                    
                                                                                
        self.select_view = SelectView(monitor_dir, filter_dir=["deepin-wallpapers"])
        self.select_view_sw = self.select_view.get_scrolled_window()               

        self.notice_label = Label("")
        self.notice_label.set_size_request(400, -1)

        self.back_button = Button(_("Back"))                                    
        self.back_button.connect("clicked", self.__on_back)
        self.select_all_button = Button(_("Select All"))                        
        self.select_all_button.connect("clicked", self.on_select_all)
        add_button = Button(_("Add"))                                              
        add_button.connect("clicked", self.on_add_wallpapers)                      
                                                                                   
        control_box = gtk.HBox(spacing = 10)
        control_box.pack_start(self.notice_label, False, False)
        control_box.pack_start(self.back_button, False, False)
        control_box.pack_start(self.select_all_button, False, False)
        control_box.pack_start(add_button, False, False)                           
                                                                                
        control_align = gtk.Alignment()                                         
        control_align.set(1.0, 0.5, 0, 0)                                       
        control_align.set_padding(0, 5, 0, 10)                                  
        control_align.add(control_box)                                          
        self.pack_start(self.select_view_sw, True, True)                        
        self.pack_start(control_align, False, True)
  
        event_manager.add_callback("select-select-wallpaper", self.__on_select_select_wallpaper)

    def __on_select_select_wallpaper(self, name, obj, select_item):             
        if self.select_view.is_select_all():                                    
            self.select_all_button.set_label(_("UnSelect All"))                 
        else:                                                                   
            self.select_all_button.set_label(_("Select All"))

    def __on_back(self, widget):                                                
        event_manager.emit("back-to-detailpage", self.theme)                           
                                                                                
    def set_theme(self, theme):                                                 
        self.theme = theme
        if len(self.select_view.items) == 0:                                    
            self.notice_label.set_text(_("Please copy some pictures under %s") % get_images_dir())
 
    def on_select_all(self, widget):                                            
        self.select_view.select_all()                                           
                                                                                
        if self.select_view.is_select_all():                                    
            self.select_all_button.set_label(_("UnSelect All"))                 
        else:                                                                   
            self.select_all_button.set_label(_("Select All"))
                                                                            
    def on_add_wallpapers(self, widget):                                        
        self.select_view.emit_add_wallpapers()
        
class UserPage(gtk.VBox):        
    
    def __init__(self, monitor_dir):
        
        gtk.VBox.__init__(self)
        self.set_spacing(10)
        
        self.select_view = SelectView(monitor_dir)
        self.select_view_sw = self.select_view.get_scrolled_window()
        
        self.back_button = Button(_("Back"))                                    
        self.back_button.connect("clicked", self.__on_back)
        self.select_all_button = Button(_("Select All"))                        
        self.select_all_button.connect("clicked", self.on_select_all)           
        delete_button = Button(_("Delete"))
        delete_button.connect("clicked", self.__on_delete)
        add_button = Button(_("Add"))
        add_button.connect("clicked", self.on_add_wallpapers)
        
        control_box = gtk.HBox(spacing = 10)
        control_box.pack_start(self.back_button, False, False)
        control_box.pack_start(self.select_all_button, False, False)
        control_box.pack_start(delete_button, False, False)
        control_box.pack_start(add_button, False, False)
        
        control_align = gtk.Alignment()
        control_align.set(1.0, 0.5, 0, 0)
        control_align.set_padding(0, 5, 0, 10)
        control_align.add(control_box)
        
        self.pack_start(self.select_view_sw, True, True)
        self.pack_start(control_align, False, True)
 
        event_manager.add_callback("select-select-wallpaper", self.__on_select_select_wallpaper)
 
    def __on_select_select_wallpaper(self, name, obj, select_item):             
        if self.select_view.is_select_all():                                    
            self.select_all_button.set_label(_("UnSelect All"))                 
        else:                                                                   
            self.select_all_button.set_label(_("Select All"))
 
    def __on_back(self, widget):                                                
        event_manager.emit("back-to-detailpage", self.theme)                           
                                                                                
    def set_theme(self, theme):                                                 
        self.theme = theme
 
    def on_select_all(self, widget):                                            
        self.select_view.select_all()                                           
                                                                                
        if self.select_view.is_select_all():                                    
            self.select_all_button.set_label(_("UnSelect All"))                 
        else:                                                                   
            self.select_all_button.set_label(_("Select All"))
  
    def __delete_confirm(self):
        self.select_view.delete()
        self.select_all_button.set_label(_("Select All"))

    def __on_delete(self, widget):
        dlg = ConfirmDialog(_("Delete Wallpaper"),                                  
                            _("Are you sure delete wallpaper?"), 
                            300,                                                
                            100,                                                
                            lambda : self.__delete_confirm(),                   
                            None,                                               
                            True, 
                            CONTENT_FONT_SIZE)                                               
        dlg.show_all()

    def on_add_wallpapers(self, widget):    
        self.select_view.emit_add_wallpapers()
