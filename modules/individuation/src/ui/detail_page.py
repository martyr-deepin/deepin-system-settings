#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
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

from theme import app_theme
import gtk
import gobject
import deepin_gsettings
from dtk.ui.tab_window import TabBox
from dtk.ui.label import Label
from dtk.ui.button import Button, CheckButton
from dtk.ui.scalebar import HScalebar
from dtk.ui.constant import ALIGN_END
from ui.wallpaper_item import ITEM_PADDING_Y
from ui.wallpaper_view import WallpaperView
from ui.utils import get_toggle_group, get_combo_group
from constant import STATUS_HEIGHT, WIDGET_HEIGHT
from helper import event_manager
from nls import _
import threading as td

TIME_COMBO_ITEM =  [
    ("10 %s" % _("Seconds"), 10), ("30 %s" % _("Seconds"), 30), 
    ("1 %s" % _("Minute"), 60), ("3 %s" % _("Minutes"), 180),
    ("5 %s" % _("Minutes"), 300), ("10 %s" % _("Minutes"), 600), 
    ("15 %s" % _("Minutes"), 900),("20 %s" % _("Minutes"), 1200), 
    ("30 %s" % _("Minutes"), 30 * 60), ("1 %s" % _("Hour"), 60 * 60),
    ("2 %s" % _("Hours"), 120 * 60), ("3 %s" % _("Hours"), 180 * 60), 
    ("4 %s" % _("Hours"), 240 * 60), ("6 %s" % _("Hours"), 360 * 60), 
    ("12 %s" % _("Hours"), 12 * 60 * 60), ("24 %s" % _("Hours"), 24 * 60 * 60)
    ]

DRAW_COMBO_ITEM = [(_("Scaling"), "Scaling"), (_("Tiling"), "Tiling")]
                                                                                
class SelectAllThread(td.Thread):                                                  
    def __init__(self, ThisPtr):                                                
        td.Thread.__init__(self)                                                
        self.setDaemon(True)                                                    
        self.ThisPtr = ThisPtr                                                  
                                                                                
    def run(self):                                                              
        try:                                                                    
            self.ThisPtr.wallpaper_view.select_all()                                       
        except Exception, e:                                                    
            print "class SecondThread got error %s" % e

class DetailPage(TabBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        TabBox.__init__(self)

        self.__background_settings = deepin_gsettings.new("com.deepin.dde.background")

        self.draw_title_background = self.draw_tab_title_background
        self.theme = None
        
        self.wallpaper_box = gtk.VBox()
        self.window_theme_box = gtk.VBox()
        self.wallpaper_view = WallpaperView(padding_x=30, padding_y=ITEM_PADDING_Y)
        self.wallpaper_view_sw = self.wallpaper_view.get_scrolled_window()

        position_group, self.position_combobox = get_combo_group(_("Position"),
                                                                 DRAW_COMBO_ITEM,
                                                                 self.on_position_combox_selected)
        time_group, self.time_combobox = get_combo_group(_("Duration"), 
                                                         TIME_COMBO_ITEM,
                                                         self.on_time_combox_selected)
        
        self.__is_random = True
        if self.__background_settings.get_int("background-duration") == 0:
            self.time_combobox.set_sensitive(False)
            self.__is_random = False
        self.unorder_play = get_toggle_group(_("Random"), 
                                             self.__on_random_toggled, 
                                             self.__is_random)
        self.button_align = gtk.Alignment()
        self.button_align.set_padding(0, 0, 35, 5)
        self.button_box = gtk.HBox(spacing = 10)
        self.select_all_button = Button(_("Select All"))
        self.select_all_button.set_size_request(80, WIDGET_HEIGHT)
        self.select_all_button.connect("clicked", self.__on_select_all)
        self.delete_button = Button(_("Delete"))
        self.delete_button.set_size_request(80, WIDGET_HEIGHT)
        self.delete_button.connect("clicked", self.__on_delete)
        self.button_box.pack_start(self.select_all_button, False, False)
        self.button_box.pack_start(self.delete_button, False, False)
        self.button_align.add(self.button_box)

        self.action_bar = gtk.HBox(5)        
        self.action_bar.pack_start(position_group, False, False)
        self.action_bar.pack_start(time_group, False, False)
        self.action_bar.pack_start(self.unorder_play, False, False)
        self.action_bar.pack_start(self.button_align)
        action_bar_align = gtk.Alignment()
        action_bar_align.set_size_request(-1, STATUS_HEIGHT)
        action_bar_align.set_padding(5, 5, 15, 50)
        action_bar_align.add(self.action_bar)
        
        self.wallpaper_box.pack_start(self.wallpaper_view_sw, True, True)
        self.wallpaper_box.pack_start(action_bar_align, False, False)

        '''
        Window Effect
        '''
        self.window_effect_align = gtk.Alignment()
        self.window_effect_align.set(0.0, 0.5, 0, 0)
        self.window_effect_align.set_padding(10, 10, 10, 0)
        self.window_effect_box = gtk.HBox()
        self.window_effect_button = CheckButton("开启毛玻璃效果")
        self.window_effect_box.pack_start(self.window_effect_button, False, False, 4)
        self.window_effect_align.add(self.window_effect_box)
        '''
        Color Deepth
        '''
        self.color_deepth_align = gtk.Alignment()
        self.color_deepth_align.set(0.0, 0.5, 0, 0)
        self.color_deepth_align.set_padding(10, 10, 10, 0)
        self.color_deepth_box = gtk.HBox(spacing=10)
        self.color_deepth_label = Label("颜色浓度", text_x_align=ALIGN_END, label_width=60)
        self.color_deepth_scalbar = HScalebar(                                                      
            None, None, None, None, None, None,
            app_theme.get_pixbuf("scalebar/point.png"), 
            True, 
            "%")
        self.color_deepth_adjust = gtk.Adjustment(0, 0, 100)
        self.color_deepth_scalbar.set_adjustment(self.color_deepth_adjust)
        self.color_deepth_scalbar.set_size_request(355, 40)
        self.color_deepth_box.pack_start(self.color_deepth_label)
        self.color_deepth_box.pack_start(self.color_deepth_scalbar)
        self.color_deepth_align.add(self.color_deepth_box)
        self.window_theme_box.pack_start(self.window_effect_align, False, False)
        self.window_theme_box.pack_start(self.color_deepth_align, False, False)

    def __on_select_all(self, widget):
        SelectAllThread(self).start()

        if self.wallpaper_view.is_select_all():
            self.select_all_button.set_label(_("UnSelect All"))
        else:
            self.select_all_button.set_label(_("Select All"))

    def __on_delete(self, widget):
        event_manager.emit("switch-to-deletepage", self.theme)

    def __on_random_toggled(self, widget):
        is_random = widget.get_active()
        if is_random:
            self.time_combobox.set_sensitive(True)
            item = self.time_combobox.get_current_item()
            if item == None:
                return
            self.__background_settings.set_int("background-duration", item[1])
        else:
            self.time_combobox.set_sensitive(False)
            self.__background_settings.set_int("background-duration", 0)
        
    def draw_tab_title_background(self, cr, widget):
        rect = widget.allocation
        cr.set_source_rgb(1, 1, 1)    
        cr.rectangle(0, 0, rect.width, rect.height - 1)
        cr.fill()
        
    def on_position_combox_selected(self, widget, label, data, index):    
        self.theme.set_background_draw_mode(data)
        self.theme.save()
        
    def on_time_combox_selected(self, widget, label, data, index):    
        self.theme.set_background_duration(data)
        self.theme.save()

    def set_theme(self, theme):
        self.theme = theme
        
        '''
        TODO: self.theme.name
        '''
        self.delete_items(self.tab_items)
        self.add_items([(self.theme.get_name(), self.wallpaper_box),                   
                       ])
        
        draw_mode = self.theme.get_background_draw_mode()
        item_index = 0
        for index, item in enumerate(DRAW_COMBO_ITEM):
            if draw_mode == item[-1]:
                item_index = index
                
        self.position_combobox.set_select_index(item_index)        
        
        duration = self.theme.get_background_duration()
        item_index = 0
        for index, item in enumerate(TIME_COMBO_ITEM):
            if duration == item[-1]:
                item_index = index
                
        self.time_combobox.set_select_index(item_index)        
        self.wallpaper_view.set_theme(theme)
        if self.wallpaper_view.is_select_all():
            self.select_all_button.set_label(_("UnSelect All"))
        
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
        
gobject.type_register(DetailPage)        

