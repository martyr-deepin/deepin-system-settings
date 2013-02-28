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

from dtk.ui.tab_window import TabBox
from dtk.ui.label import Label
from dtk.ui.button import Button, CheckButton
from dtk.ui.scalebar import HScalebar
from dtk.ui.constant import ALIGN_END

from ui.wallpaper_item import ITEM_PADDING_Y
from ui.wallpaper_view import WallpaperView
from ui.utils import get_toggle_group, get_combo_group

from constant import STATUS_HEIGHT

TIME_COMBO_ITEM =  [
    # ("10秒", 10), ("30秒", 30), 
    ("1分钟", 60), ("3分钟", 180),
    ("5分钟", 300), ("10分钟", 600), 
    ("15分钟", 900),("20分钟", 1200), 
    ("30分钟", 30 * 60), ("1个小时", 60 * 60),
    ("2个小时", 120 * 60), ("3个小时", 180 * 60), 
    ("4个小时", 240 * 60), ("6个小时", 360 * 60), 
    ("12个小时", 12 * 60 * 60), ("24个小时", 24 * 60 * 60)
    ]

DRAW_COMBO_ITEM = [("拉伸", "Scaling"), ("平铺", "Tiling")]


class DetailPage(TabBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        TabBox.__init__(self)

        self.draw_title_background = self.draw_tab_title_background
        self.theme = None
        
        self.wallpaper_box = gtk.VBox()
        self.window_theme_box = gtk.VBox()
        self.wallpaper_view = WallpaperView(padding_x=30, padding_y=ITEM_PADDING_Y)
        self.wallpaper_view_sw = self.wallpaper_view.get_scrolled_window()

        position_group, self.position_combobox = get_combo_group("图片位置",
                                                                      DRAW_COMBO_ITEM,
                                                                      self.on_position_combox_selected)
        time_group, self.time_combobox = get_combo_group("图片时间间隔", 
                                                              TIME_COMBO_ITEM,
                                                              self.on_time_combox_selected)
        
        self.unorder_play = get_toggle_group("随机播放")
        self.delete_button = Button("删除")
                
        self.add_items([("桌面壁纸", self.wallpaper_box),
                        # ("窗口设置", self.window_theme_box)
                        ])
        

        self.action_bar = gtk.HBox(5)        
        self.action_bar.pack_start(position_group, False, False)
        self.action_bar.pack_start(time_group, False, False)
        self.action_bar.pack_start(self.unorder_play, False, False)
        self.action_bar.pack_end(self.delete_button, False, False)
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

