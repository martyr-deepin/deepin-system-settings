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
import shutil
from dtk.ui.label import Label
from dtk.ui.button import Button
from dtk.ui.iconview import IconView
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.dialog import ConfirmDialog
from dtk.ui.utils import container_remove_all
from dtk.ui.utils import set_clickable_cursor
from dtk.ui.theme import ui_theme

from ui.wallpaper_item import SelectItem, AddItem
from xdg_support import get_system_wallpaper_dirs, get_favorite_dir
from settings import get_system_deletes, add_system_deletes
from helper import event_manager
from monitor import LibraryMonitor
from theme_manager import background_gsettings
import common
from nls import _
from constant import CONTENT_FONT_SIZE

class ActionButton(Label):
    def __init__(self, 
                 text, 
                 callback_action=None,
                 enable_gaussian=False, 
                 text_color=ui_theme.get_color("link_text"),
                 ):
        Label.__init__(self, text, text_color, enable_gaussian=enable_gaussian, text_size=9,
                       gaussian_radious=1, border_radious=0, underline=False)
        self.callback_action = callback_action

        set_clickable_cursor(self)
        self.connect('button-press-event', self.button_press_action)

    def button_press_action(self, widget, e):
        if self.callback_action:
            self.callback_action()

class LocalPicturePage(gtk.VBox):
    def __init__(self, monitor_dir):

        gtk.VBox.__init__(self)
        self.set_spacing(10)
        self.select_view = SelectView(monitor_dir, filter_dir=["deepin-wallpapers"], add_system=True)
        self.select_view.connect("items-change", self.select_view_item_changed)
        self.select_view.connect("double-click-item", self.select_view_double_clicked)
        self.select_view_sw = self.select_view.get_scrolled_window()               

        no_favorites_label = Label(_("Your Local Pictures folder is empty"))
        self.no_favorites_align = gtk.Alignment(0.5, 0.5, 0, 0)
        self.no_favorites_align.add(no_favorites_label)

        self.notice_label = Label("")

        set_wallpapper_button = Button(_("Set as wallpaper"))
        set_wallpapper_button.connect("clicked", self.__on_set_as_wallpapper)

        favorite_button = Button(_("Add to Favorites"))
        favorite_button.connect("clicked", self.__on_add_favorites)

        delete_button = Button(_("Delete"))
        delete_button.connect("clicked", self.__on_delete)

        self.button_box = gtk.HBox(spacing=10)
        self.button_box.pack_start(set_wallpapper_button, False, False)
        self.button_box.pack_start(favorite_button, False, False)
        self.button_box.pack_start(delete_button, False, False)
                                                                                   
        self.control_box = gtk.HBox()
        self.control_box.set_size_request(-1, 20)
        self.control_box.pack_start(self.notice_label, False, False)
                                                                                
        self.control_align = gtk.Alignment()                                         
        self.control_align.set(0.5, 0.5, 1, 1)
        self.control_align.set_padding(0, 5, 20, 10)
        self.control_align.add(self.control_box)

        if len(self.select_view.items) == 0:
            self.pack_start(self.no_favorites_align, True, True)
        else:
            self.pack_start(self.select_view_sw, True, True)
        self.pack_start(self.control_align, False, True)
  
        event_manager.add_callback("select-select-wallpaper", self.__on_select_select_wallpaper)

        self.timeout_notice_hide_id = None

    def __on_set_as_wallpapper(self, widget, data=None):
        self.select_view.set_multi_wallpapper()
        n = self.select_view.get_select_number()
        if n > 1:
            notice_text = _("%s pictures are set as wallpaper") % n
        else:
            notice_text = _("%s picture is set as wallpaper") % n
        self.notice_label.set_text(notice_text)
        self.timeout_notice_hide()

    def select_view_double_clicked(self, widget, item, x, y):
        image_path_string = "file://%s;" % item.image_path
        background_gsettings.set_string("picture-uris", image_path_string)        

    def select_view_item_changed(self, widget):
        if len(self.select_view.items) == 0:
            container_remove_all(self)
            self.pack_start(self.no_favorites_align, True, True)
            self.pack_end(self.control_align, False, True)
        else:
            container_remove_all(self)
            self.pack_start(self.select_view_sw, True, True)
            self.pack_end(self.control_align, False, True)

    def timeout_notice_hide(self, time=3000):
        if self.timeout_notice_hide_id:
            gtk.timeout_remove(self.timeout_notice_hide_id)
        gtk.timeout_add(time, lambda: self.notice_label.set_text(""))

    def __on_add_favorites(self, widget, data=None):
        self.select_view.add_favorites()
        n = self.select_view.get_select_number()
        if n > 1:
            notice_text = _("add %s pictures to Favorites") % n
        else:
            notice_text = _("add %s picture to Favorites") % n
        self.notice_label.set_text(notice_text)
        self.timeout_notice_hide()

    def __delete_confirm(self):
        self.select_view.delete()
        n = self.select_view.get_select_number()
        if n > 1:
            notice_text = _("delete %s pictures") % n
        else:
            notice_text = _("delete %s picture") % n
        self.notice_label.set_text(notice_text)
        self.timeout_notice_hide()
        if self.button_box in self.control_box.get_children():
            self.control_box.remove(self.button_box)

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

    def __on_select_select_wallpaper(self, name, obj, select_item):             
        select_number = self.select_view.get_select_number()
        if select_number > 0:
            if select_number > 1:
                notice_text = _("choose %s pictures") % select_number
            else:
                notice_text = _("choose %s picture") % select_number
            self.notice_label.set_text(notice_text)
            if self.button_box not in self.control_box.get_children():
                self.control_box.pack_end(self.button_box, False, False)
        else:
            self.notice_label.set_text("")
            if self.button_box in self.control_box.get_children():
                self.control_box.remove(self.button_box)
        self.show_all()

    def on_add_wallpapers(self, widget):                                        
        event_manager.emit("add-local-wallpapers", None)

def get_align(align=(0.5, 0.5, 0, 0), padding=(0, 0, 0, 0)):
    new_align = gtk.Alignment(*align)
    new_align.set_padding(*padding)
    return new_align

class FavoritePage(gtk.VBox):
    def __init__(self, monitor_dir):

        gtk.VBox.__init__(self)
        self.set_spacing(10)
        self.select_view = SelectView(monitor_dir, filter_dir=["deepin-wallpapers"], add_system=False)
        self.select_view.connect("items-change", self.select_view_item_changed)
        self.select_view.connect("double-click-item", self.select_view_double_clicked)
        self.select_view_sw = self.select_view.get_scrolled_window()

        label_box = gtk.VBox()
        no_favorites_label = Label(_("Your Favorites folder is empty."))
        align_up = get_align(align=(0.5, 0.5, 0, 0))
        align_up.add(no_favorites_label)
        go_to_local_action = ActionButton(_("Add from Local Pictures"), lambda: event_manager.emit("switch-to-local-pictures", self))
        align_down = get_align(align=(0.5, 0.5, 0, 0))
        align_down.add(go_to_local_action)

        label_box.pack_start(align_up, False, False)
        label_box.pack_start(align_down, False, False)
        self.no_favorites_align = gtk.Alignment(0.5, 0.5, 0, 0)
        self.no_favorites_align.add(label_box)

        self.notice_label = Label("")

        set_wallpapper_button = Button(_("Set as wallpaper"))
        set_wallpapper_button.connect("clicked", self.__on_set_as_wallpapper)

        delete_button = Button(_("Delete"))
        delete_button.connect("clicked", self.__on_delete)

        self.button_box = gtk.HBox(spacing=10)
        self.button_box.pack_start(set_wallpapper_button, False, False)
        self.button_box.pack_start(delete_button, False, False)
                                                                                   
        self.control_box = gtk.HBox()
        self.control_box.set_size_request(-1, 20)
        self.control_box.pack_start(self.notice_label, False, False)
                                                                                
        self.control_align = gtk.Alignment()
        self.control_align.set(0.5, 0.5, 1, 1)
        self.control_align.set_padding(0, 5, 20, 10)
        self.control_align.add(self.control_box)

        if len(self.select_view.items) == 0:
            self.pack_start(self.no_favorites_align, True, True)
        else:
            self.pack_start(self.select_view_sw, True, True)
        self.pack_end(self.control_align, False, True)
  
        event_manager.add_callback("select-select-wallpaper", self.__on_select_select_wallpaper)

        self.timeout_notice_hide_id = None

    def __on_set_as_wallpapper(self, widget, data=None):
        self.select_view.set_multi_wallpapper()
        n = self.select_view.get_select_number()
        if n > 1:
            notice_text = _("%s pictures are set as wallpaper") % n
        else:
            notice_text = _("%s picture is set as wallpaper") % n
        self.notice_label.set_text(notice_text)
        self.timeout_notice_hide()

    def select_view_double_clicked(self, widget, item, x, y):
        image_path_string = "file://%s;" % item.image_path
        background_gsettings.set_string("picture-uris", image_path_string)        

    def select_view_item_changed(self, widget):
        if len(self.select_view.items) == 0:
            container_remove_all(self)
            self.pack_start(self.no_favorites_align, True, True)
            self.pack_end(self.control_align, False, True)
        else:
            container_remove_all(self)
            self.pack_start(self.select_view_sw, True, True)
            self.pack_end(self.control_align, False, True)

    def timeout_notice_hide(self, time=3000):
        if self.timeout_notice_hide_id:
            gtk.timeout_remove(self.timeout_notice_hide_id)
        gtk.timeout_add(time, lambda: self.notice_label.set_text(""))

    def __delete_confirm(self):
        self.select_view.delete()
        n = self.select_view.get_select_number()
        if n > 1:
            notice_text = _("delete %s pictures") % n
        else:
            notice_text = _("delete %s picture") % n
        self.notice_label.set_text(notice_text)
        self.timeout_notice_hide()
        if self.button_box in self.control_box.get_children():
            self.control_box.remove(self.button_box)

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

    def __on_select_select_wallpaper(self, name, obj, select_item):
        select_number = self.select_view.get_select_number()
        if select_number > 0:
            if select_number > 1:
                notice_text = _("choose %s pictures") % select_number
            else:
                notice_text = _("choose %s picture") % select_number
            self.notice_label.set_text(notice_text)
            if self.button_box not in self.control_box.get_children():
                self.control_box.pack_end(self.button_box, False, False)
        else:
            self.notice_label.set_text("")
            if self.button_box in self.control_box.get_children():
                self.control_box.remove(self.button_box)
        self.show_all()

    def on_add_wallpapers(self, widget):                                        
        event_manager.emit("add-local-wallpapers", None)

class SelectView(IconView):
    SHOW_ITEM_COUNT = 16
    
    __gsignals__ = {                                                            
        "loaded" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),}

    def __init__(self, monitor_dir, padding_x=8, padding_y=10, filter_dir=None, add_system=False):
        IconView.__init__(self, padding_x=padding_x, padding_y=padding_y)
        
        self.system_wallpapper_dir = get_system_wallpaper_dirs()[1]
        self.is_file_added = False
        self.monitor_dir = monitor_dir
        self.filter_dir = filter_dir
        self.library_monitor = LibraryMonitor(monitor_dir)
        self.library_monitor.set_property("monitored", True)
        self.library_monitor.connect("file-added", self.on_library_file_added)
        self.library_monitor.connect("folder-added", self.on_library_folder_added)
        self.library_monitor.connect("location-removed", self.on_library_location_removed)
        self.__image_index = 0
        self.__init_monitor_images(add_system)

    def on_library_file_added(self, obj, gfile):    
        is_image_type = common.gfile_is_image(gfile)
        if is_image_type:
            image_path = gfile.get_path()
            if not self.is_exists(image_path):
                self.is_file_added = True
                self.add_items([SelectItem(image_path)], 1)
                
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
    def __init_monitor_images(self, add_system=False):
        if self.is_file_added:
            return
        
        items = []
        image_paths = []
        i = 0
        
        self.set_loading(True)
        for image_path in common.walk_images(self.monitor_dir, filter_dir = self.filter_dir):
            image_paths.append(image_path)

        if add_system:
            system_deletes = get_system_deletes()
            for image_path in common.walk_images(self.system_wallpapper_dir):
                if not image_path in system_deletes:
                    image_paths.append(image_path)
        
        while self.__image_index < len(image_paths) and i < self.SHOW_ITEM_COUNT:
            items.append(SelectItem(image_paths[self.__image_index]))
            self.__image_index += 1
            i += 1

        if items and items not in self.items:    
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

    def add_favorites(self):
        favorites_dir = get_favorite_dir()
        for item in self.items:
            if item.is_tick:
                new_path = os.path.join(favorites_dir, os.path.split(item.image_path)[1])
                shutil.copy2(item.image_path, new_path)

    def delete(self):
        for item in self.items:
            if item.is_tick:
                if item.image_path.startswith(self.system_wallpapper_dir):
                    self.delete_items([item])
                    add_system_deletes([item.image_path])
                else:
                    os.remove(item.image_path)
                event_manager.emit("delete-downloaded-wallpaper", item)

        self.queue_draw()

    def set_multi_wallpapper(self):
        uris = []
        for item in self.items:
            if item.is_tick:
                url = "file://%s" % item.image_path
                uris.append(url)
        image_path_string = ";".join(uris)
        background_gsettings.set_string("picture-uris", image_path_string)        
        background_gsettings.set_int("background-duration", 600)

    def get_select_number(self):
        n = 0
        for item in self.items:
            if item.is_tick:
                n += 1
        return n

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
        
