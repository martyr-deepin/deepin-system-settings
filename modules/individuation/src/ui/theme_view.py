#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hou Shaohui
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
from dtk.ui.menu import Menu
from dtk.ui.iconview import IconView
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.dialog import InputDialog, ConfirmDialog
from ui.theme_item import ThemeItem
from helper import event_manager
from theme_manager import theme_manager
from nls import _
from common import threaded
from constant import CONTENT_FONT_SIZE

class UserThemeView(IconView):

    def __init__(self, padding_x=0, padding_y=0, status_box=None):
        IconView.__init__(self, padding_x=padding_x, padding_y=padding_y)
        self.untitled_theme = theme_manager.get_untitled_theme()
        self.status_box = status_box

        self.__is_double_click = False
        self.__single_click_item = None
        self.connect("double-click-item", self.__on_double_click_item)
        self.connect("single-click-item", self.__on_single_click_item)
        self.connect("right-click-item", self.__on_right_click_item)

        event_manager.add_callback("create-new-theme", self.on_create_new_theme)
        event_manager.add_callback("update-theme", self.__on_update_theme)
        event_manager.add_callback("clear-userview-highlight", self.clear_highlight_status)
        gobject.timeout_add(500, lambda : self.__init_themes())
        
    def __init_themes(self):
        print "user start"
        user_themes = theme_manager.get_user_themes()
        if user_themes:
            self.add_themes(user_themes)

        for item in self.items:
            if theme_manager.is_current_theme(item.theme):
                self.__single_click_item = item
                self.set_highlight(self.__single_click_item)
                break
        print "user end"

    def clear_highlight_status(self, name, obj, data):
        self.clear_highlight()
        self.__single_click_item = None

    def get_scrolled_window(self):
        scrolled_window = ScrolledWindow()
        scrolled_window.add_child(self)
        return scrolled_window

    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()

    def __on_double_click_item(self, widget, item, x, y):
        self.__is_double_click = True
        event_manager.emit("theme-detail", item.theme)

    def __is_single_click(self, item):
        if self.__is_double_click:
            item.do_double_click()
            
            if self.__single_click_item:
                self.set_highlight(self.__single_click_item)
        else:
            self.__single_click_item = item
            event_manager.emit("clear-systemview-highlight", item.theme)            
            theme_manager.apply_theme(item.theme)
            self.__sync_untitle_theme(item.theme)
            self.status_box.set_status(_("Changed User Theme to %s") % item.theme.get_name())
        
        self.__is_double_click = False

    def __sync_untitle_theme(self, theme):
        self.untitled_theme.clear_system_wallpapers()
        self.untitled_theme.add_system_wallpapers(theme.get_system_wallpapers())
        self.untitled_theme.clear_user_wallpapers()
        self.untitled_theme.add_user_wallpapers(theme.get_user_wallpapers())
        self.untitled_theme.save()
        event_manager.emit("update-theme", self.untitled_theme)

    def __on_single_click_item(self, widget, item, x, y):
        self.set_highlight(item)
        event_manager.emit("clear-systemview-highlight", item.theme)
        theme_manager.apply_theme(item.theme)
        self.__sync_untitle_theme(item.theme)
        self.status_box.set_status(_("Changed User Theme to %s") % item.theme.get_name())
        #gobject.timeout_add(300, self.__is_single_click, item)

    def on_create_new_theme(self, name, obj, new_theme):
        self.add_themes([new_theme])

    def create_new_theme(self, name, item):
        new_theme = theme_manager.create_new_theme(name, item.theme)
        self.add_themes([new_theme])

    def rename_theme(self, name, item):
        theme = theme_manager.rename_theme(item.theme.get_default_name(), name)
        item.rename_theme(name)

    def delete_theme(self, item):
        theme = theme_manager.delete_theme(item.theme.get_default_name())
        self.items.remove(item)

    def on_theme_sava_as(self, item):
        input_dialog = InputDialog(_("Save Theme As"), "", 300, 100, lambda name: self.create_new_theme(name, item), None, True)
        input_dialog.show_all()

    def on_theme_rename(self, item):
        input_dialog = InputDialog(_("Rename Theme"), "", 300, 100, lambda name: self.rename_theme(name, item), None, True)
        input_dialog.show_all()

    def on_theme_delete(self, item):
        dlg = ConfirmDialog(_("Delete Theme"), 
                            _("Are you sure you want to delete the theme %s?") % item.theme.get_name(), 
                            300, 
                            100, 
                            lambda : self.delete_theme(item), 
                            None, 
                            True, 
                            CONTENT_FONT_SIZE)
        dlg.show_all()

    def __on_right_click_item(self, widget, item, x, y):
        menu_items = [(None, _("Save As"), lambda : self.on_theme_sava_as(item))]
        # TODO: the first item do not show delete
        if self.items.index(item) != 0:
            menu_items = [(None, _("Rename"), lambda : self.on_theme_rename(item)), 
                          (None, _("Save As"), lambda : self.on_theme_sava_as(item)), 
                          None, 
                          (None, _("Delete Theme"), lambda : self.on_theme_delete(item))]
        Menu(menu_items, True).show((int(x), int(y)))

    def __on_update_theme(self, name, obj, new_theme):
        for item in self.items:
            if item.theme == new_theme:
                item.update_theme()
                return

    def add_themes(self, themes):
        for theme_file in themes:
            @threaded
            def add_theme_intern(f):
                self.add_items([ThemeItem(f)])
                
            add_theme_intern(theme_file)

class SystemThemeView(IconView):

    def __init__(self, padding_x=0, padding_y=0, status_box=None):
        IconView.__init__(self, padding_x=padding_x, padding_y=padding_y)
        self.untitled_theme = theme_manager.get_untitled_theme()
        self.status_box = status_box
        
        self.__is_double_click = False
        self.__single_click_item = None
        self.connect("double-click-item", self.__on_double_click_item)
        self.connect("single-click-item", self.__on_single_click_item)
        self.connect("right-click-item", self.__on_right_click_item)
        event_manager.add_callback("clear-systemview-highlight", self.clear_highlight_status)
        gobject.timeout_add(500, lambda : self.__init_themes())
        
    def __init_themes(self):
        print "system start"
        system_themes = theme_manager.get_system_themes()
        if system_themes:
            self.add_themes(system_themes)

        for item in self.items:
            if theme_manager.is_current_theme(item.theme):
                self.__single_click_item = item
                self.set_highlight(self.__single_click_item)
                break
        print "system end"

    def clear_highlight_status(self, name, obj, data):
        self.clear_highlight()
        self.__single_click_item = None

    def get_scrolled_window(self):
        scrolled_window = ScrolledWindow()
        scrolled_window.add_child(self)
        return scrolled_window

    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()

    def __on_double_click_item(self, widget, item, x, y):
        self.__is_double_click = True
        event_manager.emit("theme-detail", item.theme)

    def __sync_untitle_theme(self, theme):                                      
        self.untitled_theme.clear_system_wallpapers()                           
        self.untitled_theme.add_system_wallpapers(theme.get_system_wallpapers())
        self.untitled_theme.clear_user_wallpapers()                             
        self.untitled_theme.add_user_wallpapers(theme.get_user_wallpapers())       
        self.untitled_theme.save()
        event_manager.emit("update-theme", self.untitled_theme)

    def __is_single_click(self, item):                                          
        if self.__is_double_click:                                              
            item.do_double_click()

            if self.__single_click_item:
                self.set_highlight(self.__single_click_item)
        else:                                                                   
            self.__single_click_item = item                                                
            event_manager.emit("clear-userview-highlight", item.theme)            
            theme_manager.apply_theme(item.theme)                                   
            self.__sync_untitle_theme(item.theme)
            self.status_box.set_status(_("Changed System Theme to %s") % item.theme.get_name())
                                                                                
        self.__is_double_click = False

    def __on_single_click_item(self, widget, item, x, y):
        self.set_highlight(item)
        event_manager.emit("clear-userview-highlight", item.theme)
        theme_manager.apply_theme(item.theme)
        self.__sync_untitle_theme(item.theme)
        self.status_box.set_status(_("Changed System Theme to %s") % item.theme.get_name())
        #gobject.timeout_add(300, self.__is_single_click, item)

    def create_new_theme(self, name, item):
        if name == "":
            return
        
        if theme_manager.is_theme_exist(name):
            return

        new_theme = theme_manager.create_new_theme(name, item.theme)
        new_theme.set_editable(True)
        event_manager.emit("create-new-theme", new_theme)

    def on_theme_sava_as(self, item):
        input_dialog = InputDialog(_("Save Theme As"), "", 300, 100, lambda name: self.create_new_theme(name, item))
        input_dialog.show_all()

    def __on_right_click_item(self, widget, item, x, y):
        menu_items = [(None, _("Save As"), lambda : self.on_theme_sava_as(item))]
        Menu(menu_items, True).show((int(x), int(y)))

    def add_themes(self, themes):
        for theme_file in themes:
            @threaded
            def add_theme_intern(f):
                self.add_items([ThemeItem(f)])
                
            add_theme_intern(theme_file)
