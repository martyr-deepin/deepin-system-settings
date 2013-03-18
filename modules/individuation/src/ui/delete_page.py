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
import gtk
import gobject
from dtk.ui.dialog import ConfirmDialog
from dtk.ui.tab_window import TabBox
from dtk.ui.label import Label
from dtk.ui.button import Button, CheckButton
from dtk.ui.scalebar import HScalebar
from dtk.ui.constant import ALIGN_END
from ui.wallpaper_item import ITEM_PADDING_Y
from ui.delete_view import DeleteView
from constant import STATUS_HEIGHT, WIDGET_HEIGHT
from helper import event_manager
from nls import _
from constant import CONTENT_FONT_SIZE

class DeletePage(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)

        self.draw_title_background = self.draw_tab_title_background
        self.theme = None
        
        self.delete_view = DeleteView(padding_x=30, padding_y=ITEM_PADDING_Y)
        self.delete_view_sw = self.delete_view.get_scrolled_window()
        
        self.action_align = gtk.Alignment()
        self.action_align.set_padding(5, 5, 500, 5)
        self.action_box = gtk.HBox(spacing = 10)
        self.back_button = Button(_("Back"))
        self.back_button.set_size_request(80, WIDGET_HEIGHT)
        self.back_button.connect("clicked", self.__on_back)
        self.select_all_button = Button(_("Select All"))
        self.select_all_button.set_size_request(80, WIDGET_HEIGHT)
        self.select_all_button.connect("clicked", self.__on_select_all)
        self.delete_button = Button(_("Delete"))
        self.delete_button.set_size_request(80, WIDGET_HEIGHT)
        self.delete_button.connect("clicked", self.__on_delete)
        self.action_box.pack_start(self.back_button, False, False)
        self.action_box.pack_start(self.select_all_button, False, False)
        self.action_box.pack_start(self.delete_button, False, False)
        self.action_align.add(self.action_box)
        
        self.pack_start(self.delete_view_sw, True, True)
        self.pack_start(self.action_align, False, False)

        event_manager.add_callback("select-delete-wallpaper", self.__on_select_delete_wallpaper)

    def __on_back(self, widget):
        event_manager.emit("back-to-detailpage", self.theme)

    def __on_select_delete_wallpaper(self, name, obj, select_item):
        if self.delete_view.is_select_all():                                    
            self.select_all_button.set_label(_("UnSelect All"))                 
        else:                                                                   
            self.select_all_button.set_label(_("Select All"))

    def __on_select_all(self, widget):
        self.delete_view.select_all()
        if self.delete_view.is_select_all():
            self.select_all_button.set_label(_("UnSelect All"))
        else:
            self.select_all_button.set_label(_("Select All"))

    def __delete_confirm(self):
        self.delete_view.delete_wallpaper()
        event_manager.emit("update-theme", None)

    def __on_delete(self, widget):
        if self.delete_view.is_deletable():
            dlg = ConfirmDialog(_("Delete Wallpaper"),                                  
                                _("Are you sure delete wallpaper?"), 
                                300,                                                
                                100,                                                
                                lambda : self.__delete_confirm(),                   
                                None,                                               
                                True, 
                                CONTENT_FONT_SIZE)                                               
            dlg.show_all()

    def draw_tab_title_background(self, cr, widget):
        rect = widget.allocation
        cr.set_source_rgb(1, 1, 1)    
        cr.rectangle(0, 0, rect.width, rect.height - 1)
        cr.fill()

    def set_theme(self, theme):
        self.theme = theme
        self.delete_view.set_theme(theme)
        self.select_all_button.set_label(_("Select All"))
        
    def draw_mask(self, cr, x, y, w, h):
        '''
        Draw mask interface.
        
        @param cr: Cairo context.
        @param x: X coordiante of draw area.
        @param y: Y coordiante of draw area.
        @param w: Width of draw area.
        @param h: Height of draw area.
        '''
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
        
gobject.type_register(DeletePage)        
