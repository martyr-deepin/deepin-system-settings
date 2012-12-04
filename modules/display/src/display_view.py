#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2012 Zhai Xiang
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

from dtk.ui.init_skin import init_skin
from dtk.ui.utils import get_parent_dir
import os

app_theme = init_skin(
    "deepin-display-settings", 
    "1.0",
    "01",
    os.path.join(get_parent_dir(__file__, 2), "skin"),
    os.path.join(get_parent_dir(__file__, 2), "app_theme"),
    )

from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.box import ResizableBox
from dtk.ui.button import Button
from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
from dtk.ui.scalebar import HScalebar
from dtk.ui.button import ToggleButton
from dtk.ui.constant import DEFAULT_FONT_SIZE, ALIGN_START, ALIGN_END
from dtk.ui.utils import get_optimum_pixbuf_from_file
from dtk.ui.draw import cairo_state
import gobject
import gtk
from display_manager import DisplayManager

class MonitorResizableBox(ResizableBox):
    def __init__(self):
        ResizableBox.__init__(self)
        self.screen_width = 200

    def expose_override(self, cr, rect):
        x, y = rect.x, rect.y
        x = (self.width - self.screen_width) / 2
        y += 10
        
        with cairo_state(cr):
            cr.rectangle(x, y, self.screen_width, self.height - y * 3)
            cr.stroke()

class DisplayView(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)

        self.display_manager = DisplayManager()

        self.padding_x = 10
        self.padding_y = 5
        self.box_spacing = 10
        self.resize_width = 790
        self.resize_height = 200
        self.monitor_items = []
        self.__setup_monitor_items()
        self.sizes_items = []
        self.__setup_sizes_items()
        self.direction_items = [("DEBUG", 0)]
        self.duration_items = [("1分钟", 1), 
                               ("2分钟", 2), 
                               ("3分钟", 3), 
                               ("5分钟", 5), 
                               ("10分钟", 10), 
                               ("30分钟", 30), 
                               ("60分钟", 60), 
                               ("从不", -1)]
        '''
        scrolled_window
        '''
        self.scrolled_window = ScrolledWindow()
        self.scrolled_window.set_size_request(825, 425)
        '''
        left, right align
        '''
        self.left_align = self.__setup_align()
        self.right_align = self.__setup_align()
        '''
        left, right box
        '''
        self.left_box = gtk.VBox(spacing = self.box_spacing)
        self.right_box = gtk.VBox(spacing = self.box_spacing)
        '''
        monitor operation && detect
        '''
        self.monitor_resize_box = MonitorResizableBox()
        self.monitor_resize_box.set_size_request(self.resize_width, self.resize_height)
        self.monitor_resize_box.connect("resize", self.__resize_box)
        '''
        monitor display
        '''
        self.monitor_display_align = self.__setup_align()
        self.monitor_display_label = self.__setup_label("屏幕显示", align = ALIGN_START)
        self.monitor_display_align.add(self.monitor_display_label)
        '''
        monitor
        '''
        self.monitor_align = self.__setup_align()
        self.monitor_box = gtk.HBox(spacing = self.box_spacing)
        self.monitor_label = self.__setup_label("显示器")
        self.monitor_combo = self.__setup_combo(self.monitor_items, 350)
        self.monitor_combo.set_select_index(self.display_manager.get_current_screen())
        self.monitor_combo.connect("item-selected", self.__combo_item_selected, "monitor_combo")
        self.__widget_pack_start(self.monitor_box, 
            [self.monitor_label, 
             self.monitor_combo])
        self.monitor_align.add(self.monitor_box)
        '''
        goto individuation or power setting
        '''
        self.goto_align = self.__setup_align(0.0, 0.0, 0.0, 0.0)
        self.goto_box = gtk.VBox(spacing = self.box_spacing)
        self.goto_label = self.__setup_label("DEBUG")
        self.__widget_pack_start(self.goto_box, 
            [self.goto_label])
        self.goto_align.add(self.goto_box)
        '''
        sizes && direction
        '''
        self.sizes_align = self.__setup_align()
        self.sizes_box = gtk.HBox(spacing = self.box_spacing)
        self.sizes_label = self.__setup_label("分辨率")
        self.sizes_combo = self.__setup_combo(self.sizes_items, 160)
        self.direction_label = self.__setup_label("方向")
        self.direction_combo = self.__setup_combo(self.direction_items)
        self.__widget_pack_start(self.sizes_box, 
            [self.sizes_label, 
             self.sizes_combo, 
             self.direction_label, 
             self.direction_combo])
        self.sizes_align.add(self.sizes_box)
        '''
        monitor brightness
        '''
        self.monitor_bright_align = self.__setup_align()
        self.monitor_bright_label = self.__setup_label("屏幕亮度", align = ALIGN_START)
        self.monitor_bright_align.add(self.monitor_bright_label)
        '''
        brightness
        '''
        self.brightness_align = self.__setup_align()
        self.brightness_box = gtk.HBox(spacing = self.box_spacing)
        self.brightness_label = self.__setup_label("亮度")
        self.brightness_scale = HScalebar(
            app_theme.get_pixbuf("scalebar/l_fg.png"), 
            app_theme.get_pixbuf("scalebar/l_bg.png"), 
            app_theme.get_pixbuf("scalebar/m_fg.png"), 
            app_theme.get_pixbuf("scalebar/m_bg.png"), 
            app_theme.get_pixbuf("scalebar/r_fg.png"), 
            app_theme.get_pixbuf("scalebar/r_bg.png"), 
            app_theme.get_pixbuf("scalebar/point.png"), 
            True)
        self.brightness_adjust = gtk.Adjustment(0, 0, 100)
        self.brightness_scale.set_adjustment(self.brightness_adjust)
        self.brightness_scale.set_size_request(355, DEFAULT_FONT_SIZE * 4)
        self.__widget_pack_start(self.brightness_box, 
            [self.brightness_label, 
             self.brightness_scale])
        self.brightness_align.add(self.brightness_box)
        '''
        auto adjust monitor brightness
        '''
        self.auto_adjust_align = self.__setup_align()
        self.auto_adjust_box = gtk.HBox(spacing = self.box_spacing)
        self.auto_adjust_label = self.__setup_label("自动调节屏幕亮度", 120)
        self.auto_adjust_toggle = self.__setup_toggle()
        self.close_monitor_label = self.__setup_label("关闭屏幕", 90)
        self.close_monitor_combo = self.__setup_combo(self.duration_items)
        self.__widget_pack_start(self.auto_adjust_box, 
            [self.auto_adjust_label, 
             self.auto_adjust_toggle, 
             self.close_monitor_label, 
             self.close_monitor_combo])
        self.auto_adjust_align.add(self.auto_adjust_box)
        '''
        monitor lock
        '''
        self.monitor_lock_align = self.__setup_align()
        self.monitor_lock_label = self.__setup_label("屏幕锁定", align = ALIGN_START)
        self.monitor_lock_align.add(self.monitor_lock_label)
        '''
        auto monitor lock
        '''
        self.auto_lock_align = self.__setup_align()
        self.auto_lock_box = gtk.HBox(spacing = self.box_spacing)
        self.auto_lock_label = self.__setup_label("自动锁定用户屏幕", 120)
        self.auto_lock_toggle = self.__setup_toggle()
        self.lock_display_label = self.__setup_label("锁定屏幕", 90)
        self.lock_display_combo = self.__setup_combo(self.duration_items)
        self.__widget_pack_start(self.auto_lock_box, 
            [self.auto_lock_label, 
             self.auto_lock_toggle, 
             self.lock_display_label, 
             self.lock_display_combo])
        self.auto_lock_align.add(self.auto_lock_box)
        '''
        left_align pack_start
        '''
        self.__widget_pack_start(self.left_box, 
            [self.monitor_resize_box, 
             self.monitor_display_align, 
             self.monitor_align, 
             self.sizes_align, 
             self.monitor_bright_align, 
             self.brightness_align, 
             self.auto_adjust_align, 
             self.monitor_lock_align, 
             self.auto_lock_align])
        self.left_align.add(self.left_box)
        '''
        right_align pack_start
        '''
        self.__widget_pack_start(self.right_box, 
            [self.goto_align])
        self.right_align.add(self.right_box)
        '''
        this->HBox pack_start
        '''
        self.scrolled_window.add_child(self.left_align)
        self.pack_start(self.scrolled_window)

    def __setup_monitor_items(self):
        count = self.display_manager.get_screen_count()
        i = 0

        while (i < count):
            self.monitor_items.append(("显示器%d" % (i + 1), i))
            i += 1

    def __setup_sizes_items(self):
        i = 0
        
        self.sizes_items = []
        for size in self.display_manager.get_screen_sizes():
            self.sizes_items.append(("%s x %s" % (size.width, size.height), i))
            i += 1

    def __combo_item_selected(self, widget, item_text=None, item_value=None, item_index=None, object=None):
        if object == "monitor_combo":
            self.display_manager.set_current_screen(item_value)
            self.__setup_sizes_items()
            return

    def __resize_box(self, widget, height):
        self.monitor_resize_box.set_size_request(self.resize_width, height - self.padding_y)

    def __setup_label(self, text="", width=50, align=ALIGN_END):
        label = Label(text, None, DEFAULT_FONT_SIZE, align, width)
        return label

    def __setup_combo(self, items=[], width=120):
        combo = ComboBox(items, None, 0, width)
        return combo

    def __setup_toggle(self):
        toggle = ToggleButton(app_theme.get_pixbuf("inactive_normal.png"), 
            app_theme.get_pixbuf("active_normal.png"))
        return toggle

    def __setup_align(self, xalign=0.5, yalign=0.5, xscale=1.0, yscale=1.0):
        align = gtk.Alignment()
        align.set(xalign, yalign, xscale, yscale)
        align.set_padding(self.padding_y, self.padding_y, self.padding_x, 0)
        return align

    def __widget_pack_start(self, parent_widget, widgets=[], expand=False, fill=False):
        if parent_widget == None:
            return
        for item in widgets:
            parent_widget.pack_start(item, expand, fill)

gobject.type_register(DisplayView)
