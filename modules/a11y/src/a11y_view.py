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
    "deepin-power-settings", 
    "1.0",
    "01",
    os.path.join(get_parent_dir(__file__, 2), "skin"),
    os.path.join(get_parent_dir(__file__, 2), "app_theme"),
    )

from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
from dtk.ui.button import ToggleButton
from dtk.ui.constant import DEFAULT_FONT_SIZE, ALIGN_START, ALIGN_END
from dtk.ui.utils import get_optimum_pixbuf_from_file
from a11y_manager import A11yManager
import gobject
import gtk

class A11yView(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)
        self.label_padding_x = 10
        self.label_padding_y = 10
        self.hbox_spacing = 10
        self.wait_duration_items = [("5分钟", 5), ("10分钟", 10), ("30分钟", 30), ("1小时", 60)]
        self.a11y_manager = A11yManager()
        self.high_contrast_theme_items = [("高对比度主题1", 0), 
                                          ("高对比度主题2", 1), 
                                          ("高对比度主题3", 2)
                                         ]
        '''
        high contrast
        '''
        self.high_contrast_align = self.__setup_align()
        self.high_contrast_label = self.__setup_label("高对比度", ALIGN_START)
        self.high_contrast_align.add(self.high_contrast_label)
        '''
        high contrast theme
        '''
        self.high_contrast_theme_align = self.__setup_align()
        self.high_contrast_theme_box = gtk.HBox(spacing=self.hbox_spacing)
        self.high_contrast_theme_label = self.__setup_label("请选择一个高对比度主题")
        self.high_contrast_theme_combo = self.__setup_combo(self.high_contrast_theme_items)
        #self.high_contrast_theme_combo.set_select_index(self.a11y_manager.get_press_button_power(self.power_manage_items))
        self.high_contrast_theme_combo.connect("item-selected", self.__combo_item_selected, "high_contrast_theme")
        self.__widget_pack_start(self.press_button_power_box, 
            [self.press_button_power_label, self.press_button_power_combo])
        self.press_button_power_align.add(self.press_button_power_box)
        '''
        close notebook cover
        '''
        self.close_notebook_cover_align = self.__setup_align()
        self.close_notebook_cover_box = gtk.HBox(spacing=self.hbox_spacing)
        self.close_notebook_cover_label = self.__setup_label("合上笔记本盖子")
        self.close_notebook_cover_combo = self.__setup_combo(self.power_manage_items)
        self.close_notebook_cover_combo.set_select_index(self.a11y_manager.get_close_notebook_cover(self.power_manage_items))
        self.close_notebook_cover_combo.connect("item-selected", self.__combo_item_selected, "close_notebook_cover")
        self.__widget_pack_start(self.close_notebook_cover_box, 
            [self.close_notebook_cover_label, self.close_notebook_cover_combo])
        self.close_notebook_cover_align.add(self.close_notebook_cover_box)
        '''
        press button hibernate
        '''
        self.press_button_hibernate_align = self.__setup_align()
        self.press_button_hibernate_box = gtk.HBox(spacing=self.hbox_spacing)
        self.press_button_hibernate_label = self.__setup_label("按休眠按钮时")
        self.press_button_hibernate_combo = self.__setup_combo(self.power_manage_items)
        self.press_button_hibernate_combo.set_select_index(self.a11y_manager.get_press_button_hibernate(self.power_manage_items))
        self.press_button_hibernate_combo.connect("item-selected", self.__combo_item_selected, "press_button_hibernate")
        self.__widget_pack_start(self.press_button_hibernate_box, 
            [self.press_button_hibernate_label, self.press_button_hibernate_combo])
        self.press_button_hibernate_align.add(self.press_button_hibernate_box)
        '''
        power save config
        '''
        self.power_save_config_align = self.__setup_align()
        self.power_save_config_label = self.__setup_label("电源节能设置", ALIGN_START)
        self.power_save_config_align.add(self.power_save_config_label)
        '''
        hibernate status
        '''
        self.hibernate_status_align = self.__setup_align()
        self.hibernate_status_box = gtk.HBox(spacing=self.hbox_spacing)
        self.hibernate_status_label = self.__setup_label("进入休眠状态")
        self.hibernate_status_combo = self.__setup_combo(self.wait_duration_items)
        self.hibernate_status_combo.set_select_index(self.a11y_manager.get_hibernate_status(self.wait_duration_items))
        self.hibernate_status_combo.connect("item-selected", self.__combo_item_selected, "hibernate_status")
        self.__widget_pack_start(self.hibernate_status_box, 
            [self.hibernate_status_label, self.hibernate_status_combo])
        self.hibernate_status_align.add(self.hibernate_status_box)
        '''
        close harddisk
        '''
        self.close_harddisk_align = self.__setup_align()
        self.close_harddisk_box = gtk.HBox(spacing=self.hbox_spacing)
        self.close_harddisk_label = self.__setup_label("关闭硬盘")
        self.close_harddisk_combo = self.__setup_combo(self.wait_duration_items)
        self.close_harddisk_combo.set_select_index(self.a11y_manager.get_close_harddisk(self.wait_duration_items))
        self.close_harddisk_combo.connect("item-selected", self.__combo_item_selected, "close_harddisk")
        self.__widget_pack_start(self.close_harddisk_box, 
            [self.close_harddisk_label, self.close_harddisk_combo])
        self.close_harddisk_align.add(self.close_harddisk_box)
        '''
        close monitor
        '''
        self.close_monitor_align = self.__setup_align()
        self.close_monitor_box = gtk.HBox(spacing=self.hbox_spacing)
        self.close_monitor_label = self.__setup_label("关闭显示器")
        self.close_monitor_combo = self.__setup_combo(self.wait_duration_items)
        self.close_monitor_combo.set_select_index(self.a11y_manager.get_close_monitor(self.wait_duration_items))
        self.close_monitor_combo.connect("item-selected", self.__combo_item_selected, "close_monitor")
        self.__widget_pack_start(self.close_monitor_box, 
            [self.close_monitor_label, self.close_monitor_combo])
        self.close_monitor_align.add(self.close_monitor_box)
        '''
        wakeup password
        '''
        self.wakeup_password_align = self.__setup_align()
        self.wakeup_password_box = gtk.HBox(spacing=self.hbox_spacing)
        self.wakeup_password_label = self.__setup_label("唤醒时的密码保护")
        self.wakeup_password_toggle = self.__setup_toggle()
        self.wakeup_password_toggle.set_active(self.a11y_manager.get_wakeup_password())
        self.wakeup_password_toggle.connect("toggled", self.__toggled, "wakeup_password")
        self.__widget_pack_start(self.wakeup_password_box, 
            [self.wakeup_password_label, self.wakeup_password_toggle])
        self.wakeup_password_align.add(self.wakeup_password_box)
        '''
        tray battery status
        '''
        self.tray_battery_status_align = self.__setup_align()
        self.tray_battery_status_box = gtk.HBox(spacing=self.hbox_spacing)
        self.tray_battery_status_label = self.__setup_label("在系统托盘显示电池状态")
        self.tray_battery_status_toggle = self.__setup_toggle()
        self.tray_battery_status_toggle.set_active(self.a11y_manager.get_tray_battery_status())
        self.tray_battery_status_toggle.connect("toggled", self.__toggled, "tray_battery_status")
        self.__widget_pack_start(self.tray_battery_status_box, 
            [self.tray_battery_status_label, self.tray_battery_status_toggle])
        self.tray_battery_status_align.add(self.tray_battery_status_box)
        '''
        this->gtk.VBox pack_start
        '''
        self.__widget_pack_start(self, 
            [self.high_contrast_align, 
             self.press_button_power_align, 
             self.close_notebook_cover_align, 
             self.press_button_hibernate_align, 
             self.power_save_config_align, 
             self.hibernate_status_align, 
             self.close_harddisk_align, 
             self.close_monitor_align, 
             self.wakeup_password_align, 
             self.tray_battery_status_align])

    def __setup_label(self, text="", align=ALIGN_END):
        label = Label(text, None, DEFAULT_FONT_SIZE, align, 140)
        return label

    def __setup_combo(self, items=[]):
        combo = ComboBox(items, None, 0, 120)
        return combo

    '''
    temperary pixbuf I am not a designer :)
    '''
    def __setup_toggle(self):
        toggle = ToggleButton(app_theme.get_pixbuf("inactive_normal.png"), 
            app_theme.get_pixbuf("active_normal.png"))
        return toggle

    def __setup_align(self):
        align = gtk.Alignment()
        align.set(0.0, 0.5, 0, 0)
        align.set_padding(self.label_padding_y, self.label_padding_y, self.label_padding_x, 0)
        return align

    def __widget_pack_start(self, parent_widget, widgets=[]):
        if parent_widget == None:
            return
        for item in widgets:
            parent_widget.pack_start(item, False, False)

    def __combo_item_selected(self, widget, item_text=None, item_value=None, item_index=None, object=None):
        if object == "press_button_power":
            self.a11y_manager.set_press_button_power(item_value)
            return

        if object == "close_notebook_cover":
            self.a11y_manager.set_close_notebook_cover(item_value)
            return

        if object == "press_button_hibernate":
            self.a11y_manager.set_press_button_hibernate(item_value)
            return

        if object == "hibernate_status":
            self.a11y_manager.set_hibernate_status(item_value)
            return

        if object == "close_harddisk":
            self.a11y_manager.set_close_harddisk(item_value)
            return

        if object == "close_monitor":
            self.a11y_manager.set_close_monitor(item_value)
            return

    def __toggled(self, widget, object=None):
        if object == "wakeup_password":
            self.a11y_manager.set_wakeup_password(widget.get_active())
            return

        if object == "tray_battery_status":
            self.a11y_manager.set_tray_battery_status(widget.get_active())
            return

gobject.type_register(A11yView)        
