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
print os.path.join(get_parent_dir(__file__, 2), "skin")
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
from power_manager import PowerManager
import gobject
import gtk

class PowerView(gtk.VBox):
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
        self.wait_duration_items = [("5分钟", 1), ("10分钟", 2), ("30分钟", 3), ("1小时", 4)]
        self.power_manager = PowerManager()
        '''
        power button config
        '''
        self.power_button_config_align = self.m_setup_align()
        self.power_button_config_label = self.m_setup_label("电源按钮设置", ALIGN_START)
        self.power_button_config_align.add(self.power_button_config_label)
        '''
        press power button
        '''
        self.press_power_button_align = self.m_setup_align()
        self.press_power_button_box = gtk.HBox(spacing=self.hbox_spacing)
        self.press_power_button_label = self.m_setup_label("按电源按钮时")
        items = [("关机", 0), ("休眠", 1), ("不采取任何措施", 2)]
        self.press_power_button_combo = self.m_setup_combo(items)
        self.press_power_button_combo.set_select_index(self.power_manager.get_press_power_button(items))
        self.press_power_button_combo.connect("item-selected", self.m_combo_item_selected, "press_power_button")
        self.m_widget_pack_start(self.press_power_button_box, 
            [self.press_power_button_label, self.press_power_button_combo])
        self.press_power_button_align.add(self.press_power_button_box)
        '''
        close notebook cover
        '''
        self.close_notebook_cover_align = self.m_setup_align()
        self.close_notebook_cover_box = gtk.HBox(spacing=self.hbox_spacing)
        self.close_notebook_cover_label = self.m_setup_label("合上笔记本盖子")
        items = [("不采取任何措施", 0), ("关机", 1), ("休眠", 2)]
        self.close_notebook_cover_combo = self.m_setup_combo(items)
        self.close_notebook_cover_combo.set_select_index(self.power_manager.get_close_notebook_cover(items))
        self.close_notebook_cover_combo.connect("item-selected", self.m_combo_item_selected, "close_notebook_cover")
        self.m_widget_pack_start(self.close_notebook_cover_box, 
            [self.close_notebook_cover_label, self.close_notebook_cover_combo])
        self.close_notebook_cover_align.add(self.close_notebook_cover_box)
        '''
        press hibernate button
        '''
        self.press_hibernate_button_align = self.m_setup_align()
        self.press_hibernate_button_box = gtk.HBox(spacing=self.hbox_spacing)
        self.press_hibernate_button_label = self.m_setup_label("按休眠按钮时")
        self.press_hibernate_button_combo = self.m_setup_combo(
            [("休眠", 1), ("不采取任何措施", 2), ("关机", 3)])
        self.press_hibernate_button_combo.connect("item-selected", self.m_combo_item_selected, "press_hibernate_button")
        self.m_widget_pack_start(self.press_hibernate_button_box, 
            [self.press_hibernate_button_label, self.press_hibernate_button_combo])
        self.press_hibernate_button_align.add(self.press_hibernate_button_box)
        '''
        power save config
        '''
        self.power_save_config_align = self.m_setup_align()
        self.power_save_config_label = self.m_setup_label("电源节能设置", ALIGN_START)
        self.power_save_config_align.add(self.power_save_config_label)
        '''
        hibernate status
        '''
        self.hibernate_status_align = self.m_setup_align()
        self.hibernate_status_box = gtk.HBox(spacing=self.hbox_spacing)
        self.hibernate_status_label = self.m_setup_label("进入休眠状态")
        self.hibernate_status_combo = self.m_setup_combo(self.wait_duration_items)
        self.hibernate_status_combo.connect("item-selected", self.m_combo_item_selected, "hibernate_status")
        self.m_widget_pack_start(self.hibernate_status_box, 
            [self.hibernate_status_label, self.hibernate_status_combo])
        self.hibernate_status_align.add(self.hibernate_status_box)
        '''
        close harddisk
        '''
        self.close_hardisk_align = self.m_setup_align()
        self.close_hardisk_box = gtk.HBox(spacing=self.hbox_spacing)
        self.close_hardisk_label = self.m_setup_label("关闭硬盘")
        self.close_hardisk_combo = self.m_setup_combo(self.wait_duration_items)
        self.close_hardisk_combo.connect("item-selected", self.m_combo_item_selected, "close_hardisk")
        self.m_widget_pack_start(self.close_hardisk_box, 
            [self.close_hardisk_label, self.close_hardisk_combo])
        self.close_hardisk_align.add(self.close_hardisk_box)
        '''
        close monitor
        '''
        self.close_monitor_align = self.m_setup_align()
        self.close_monitor_box = gtk.HBox(spacing=self.hbox_spacing)
        self.close_monitor_label = self.m_setup_label("关闭显示器")
        self.close_monitor_combo = self.m_setup_combo(self.wait_duration_items)
        self.close_monitor_combo.connect("item-selected", self.m_combo_item_selected, "close_monitor")
        self.m_widget_pack_start(self.close_monitor_box, 
            [self.close_monitor_label, self.close_monitor_combo])
        self.close_monitor_align.add(self.close_monitor_box)
        '''
        wakeup password
        '''
        self.wakeup_password_align = self.m_setup_align()
        self.wakeup_password_box = gtk.HBox(spacing=self.hbox_spacing)
        self.wakeup_password_label = self.m_setup_label("唤醒时的密码保护")
        self.wakeup_password_toggle = self.m_setup_toggle()
        self.wakeup_password_toggle.connect("toggled", self.m_toggled, "wakeup_password")
        self.m_widget_pack_start(self.wakeup_password_box, 
            [self.wakeup_password_label, self.wakeup_password_toggle])
        self.wakeup_password_align.add(self.wakeup_password_box)
        '''
        tray battery status
        '''
        self.tray_battery_status_align = self.m_setup_align()
        self.tray_battery_status_box = gtk.HBox(spacing=self.hbox_spacing)
        self.tray_battery_status_label = self.m_setup_label("在系统托盘显示电池状态")
        self.tray_battery_status_toggle = self.m_setup_toggle()
        self.tray_battery_status_toggle.connect("toggled", self.m_toggled, "tray_battery_status")
        self.m_widget_pack_start(self.tray_battery_status_box, 
            [self.tray_battery_status_label, self.tray_battery_status_toggle])
        self.tray_battery_status_align.add(self.tray_battery_status_box)
        '''
        this->gtk.VBox pack_start
        '''
        self.m_widget_pack_start(self, 
            [self.power_button_config_align, 
             self.press_power_button_align, 
             self.close_notebook_cover_align, 
             self.press_hibernate_button_align, 
             self.power_save_config_align, 
             self.hibernate_status_align, 
             self.close_hardisk_align, 
             self.close_monitor_align, 
             self.wakeup_password_align, 
             self.tray_battery_status_align])

    def m_setup_label(self, text="", align=ALIGN_END):
        label = Label(text, None, DEFAULT_FONT_SIZE, align, 140)
        return label

    def m_setup_combo(self, items=[]):
        combo = ComboBox(items, None, 0, 120)
        return combo

    '''
    temperary pixbuf I am not a designer :)
    '''
    def m_setup_toggle(self):
        toggle = ToggleButton(app_theme.get_pixbuf("inactive_normal.png"), 
            app_theme.get_pixbuf("active_normal.png"))
        return toggle

    def m_setup_align(self):
        align = gtk.Alignment()
        align.set(0.0, 0.5, 0, 0)
        align.set_padding(self.label_padding_y, self.label_padding_y, self.label_padding_x, 0)
        return align

    def m_widget_pack_start(self, parent_widget, widgets=[]):
        if parent_widget == None:
            return
        for item in widgets:
            parent_widget.pack_start(item, False, False)

    def m_combo_item_selected(self, widget, item_text=None, item_value=None, item_index=None, object=None):
        if object == "press_power_button":
            '''
            There is no org.gnome.power-manager suspend or hibernate keys in gnome 3 any more
            so could not use gsettings set/get way.
            I want to use /etc/acpi/* script at first, if /var/run/acpid.socket is available to 
            control acpid daemon, then changed the script way.
            '''
            pass
        if object == "close_notebook_cover":
            return

    def m_toggled(self, widget, data=None):
        #print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
        '''
        Same situation as m_combo_item_selected callback
        '''
        pass

gobject.type_register(PowerView)        
