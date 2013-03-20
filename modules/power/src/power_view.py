#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Zhai Xiang
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
from deepin_utils.ipc import is_dbus_name_exists
from dtk.ui.utils import color_hex_to_cairo
from dtk.ui.box import ImageBox
from dtk.ui.label import Label
from dtk.ui.line import HSeparator
from dtk.ui.combo import ComboBox
from dtk.ui.button import ToggleButton
from power_progressbar import PowerProgressBar
from dtk.ui.constant import ALIGN_START, ALIGN_END
from constant import *
from nls import _
from power_manager import PowerManager
import gobject
import gtk
import dbus

class PowerView(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)
        self.wait_duration_items = [("5 %s" % _("Minutes"), 300), 
                                    ("10 %s" % _("Minutes"), 600), 
                                    ("30 %s" % _("Minutes"), 1800), 
                                    ("1 %s" % _("Hour"), 3600), 
                                    (_("Never"), PowerManager.BIG_NUM)
                                   ]
        self.power_manager = PowerManager()
        self.power_manager.power_settings.connect("changed", self.__power_settings_changed)
        self.power_manage_items = [(_("Nothing"), self.power_manager.nothing), 
                                   (_("Suspend"), self.power_manager.suspend), 
                                   (_("Shutdown"), self.power_manager.shutdown)
                                  ]
        '''
        button power config
        '''
        self.button_power_config_align = self.__setup_title_align(
            app_theme.get_pixbuf("power/button_power.png"), 
            _("Power Button Configuration"), 
            TEXT_WINDOW_TOP_PADDING, 
            TEXT_WINDOW_LEFT_PADDING)
        '''
        press button power
        '''
        self.press_button_power_align = self.__setup_align()
        self.press_button_power_box = gtk.HBox(spacing=WIDGET_SPACING)
        self.press_button_power_label = self.__setup_label(_("Press Power Button"))
        self.press_button_power_combo = self.__setup_combo(self.power_manage_items)
        self.press_button_power_combo.set_select_index(self.power_manager.get_press_button_power(self.power_manage_items))
        self.press_button_power_combo.connect("item-selected", self.__combo_item_selected, "press_button_power")
        self.__widget_pack_start(self.press_button_power_box, 
            [self.press_button_power_label, self.press_button_power_combo])
        self.press_button_power_align.add(self.press_button_power_box)
        '''
        close notebook cover
        '''
        self.close_notebook_cover_align = self.__setup_align()
        self.close_notebook_cover_box = gtk.HBox(spacing=WIDGET_SPACING)
        self.close_notebook_cover_label = self.__setup_label(_("Close Notebook Cover"))
        self.close_notebook_cover_combo = self.__setup_combo(self.power_manage_items)
        self.close_notebook_cover_combo.set_select_index(self.power_manager.get_close_notebook_cover(self.power_manage_items))
        self.close_notebook_cover_combo.connect("item-selected", self.__combo_item_selected, "close_notebook_cover")
        self.__widget_pack_start(self.close_notebook_cover_box, 
            [self.close_notebook_cover_label, self.close_notebook_cover_combo])
        self.close_notebook_cover_align.add(self.close_notebook_cover_box)
        self.close_notebook_cover_align.set_child_visible(is_laptop())
        '''
        press button hibernate
        '''
        self.press_button_hibernate_align = self.__setup_align()
        self.press_button_hibernate_box = gtk.HBox(spacing=WIDGET_SPACING)
        self.press_button_hibernate_label = self.__setup_label(_("Press Hibernate Button"))
        self.press_button_hibernate_combo = self.__setup_combo(self.power_manage_items)
        self.press_button_hibernate_combo.set_select_index(self.power_manager.get_press_button_hibernate(self.power_manage_items))
        self.press_button_hibernate_combo.connect("item-selected", self.__combo_item_selected, "press_button_hibernate")
        self.__widget_pack_start(self.press_button_hibernate_box, 
            [self.press_button_hibernate_label, self.press_button_hibernate_combo])
        self.press_button_hibernate_align.add(self.press_button_hibernate_box)
        '''
        power save config
        '''
        self.power_save_config_align = self.__setup_title_align(
            app_theme.get_pixbuf("power/power_save.png"), 
            _("Saving Power Configuration")) 
        '''
        hibernate status
        '''
        self.suspend_status_align = self.__setup_align()
        self.suspend_status_box = gtk.HBox(spacing=WIDGET_SPACING)
        self.suspend_status_label = self.__setup_label(_("Being Suspend"))
        self.suspend_status_combo = self.__setup_combo(self.wait_duration_items)
        self.suspend_status_combo.set_select_index(self.power_manager.get_suspend_status(self.wait_duration_items))
        self.suspend_status_combo.connect("item-selected", self.__combo_item_selected, "suspend_status")
        self.__widget_pack_start(self.suspend_status_box, 
            [self.suspend_status_label, self.suspend_status_combo])
        self.suspend_status_align.add(self.suspend_status_box)
        '''
        close harddisk
        '''
        self.close_harddisk_align = self.__setup_align()
        self.close_harddisk_box = gtk.HBox(spacing=WIDGET_SPACING)
        self.close_harddisk_label = self.__setup_label(_("Close Harddisk"))
        self.close_harddisk_combo = self.__setup_combo(self.wait_duration_items)
        self.close_harddisk_combo.set_select_index(self.power_manager.get_close_harddisk(self.wait_duration_items))
        self.close_harddisk_combo.connect("item-selected", self.__combo_item_selected, "close_harddisk")
        self.__widget_pack_start(self.close_harddisk_box, 
            [self.close_harddisk_label, self.close_harddisk_combo])
        self.close_harddisk_align.add(self.close_harddisk_box)
        '''
        close monitor
        '''
        self.close_monitor_align = self.__setup_align()
        self.close_monitor_box = gtk.HBox(spacing=WIDGET_SPACING)
        self.close_monitor_label = self.__setup_label(_("Close Monitor"))
        self.close_monitor_combo = self.__setup_combo(self.wait_duration_items)
        self.close_monitor_combo.set_select_index(self.power_manager.get_close_monitor(self.wait_duration_items))
        self.close_monitor_combo.connect("item-selected", self.__combo_item_selected, "close_monitor")
        self.__widget_pack_start(self.close_monitor_box, 
            [self.close_monitor_label, self.close_monitor_combo])
        self.close_monitor_align.add(self.close_monitor_box)
        '''
        percentage
        '''
        self.percentage_align = self.__setup_align()
        self.percentage_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.percentage_label = self.__setup_label(_("Current Battery"))
        self.percentage_progressbar_align = self.__setup_align(padding_left = 0, padding_top = 0)
        self.percentage_progressbar = self.__setup_progressbar(
            self.power_manager.power_settings.get_double("percentage"))
        self.percentage_progressbar_align.add(self.percentage_progressbar)
        self.__widget_pack_start(self.percentage_box, 
                                 [self.percentage_label, self.percentage_progressbar_align])
        self.percentage_align.add(self.percentage_box)
        self.percentage_align.set_child_visible(is_laptop())
        '''
        wakeup password
        '''
        self.wakeup_password_align = self.__setup_align(padding_top = BETWEEN_SPACING, 
                                                        padding_left = TEXT_WINDOW_LEFT_PADDING)
        self.wakeup_password_box = gtk.HBox(spacing=WIDGET_SPACING)
        self.wakeup_password_image = ImageBox(app_theme.get_pixbuf("lock/lock.png"))
        self.wakeup_password_label = self.__setup_label(_("Password Protection Wakeup"), 
                                                        TITLE_FONT_SIZE, 
                                                        ALIGN_START)
        self.wakeup_password_label.set_sensitive(self.power_manager.get_wakeup_password())
        self.wakeup_password_toggle_align = self.__setup_align(padding_top = 2,
                                                               padding_left = 80)
        self.wakeup_password_toggle = self.__setup_toggle()
        self.wakeup_password_toggle.set_active(self.power_manager.get_wakeup_password())
        self.wakeup_password_toggle.connect("toggled", self.__toggled, "wakeup_password")
        self.wakeup_password_toggle_align.add(self.wakeup_password_toggle)
        self.__widget_pack_start(self.wakeup_password_box, 
            [self.wakeup_password_image, 
             self.wakeup_password_label, 
             self.wakeup_password_toggle_align])
        self.wakeup_password_align.add(self.wakeup_password_box)
        '''
        tray battery status
        '''
        self.tray_battery_status_align = self.__setup_align(padding_top = BETWEEN_SPACING, 
                                                            padding_left = TEXT_WINDOW_LEFT_PADDING)
        self.tray_battery_status_box = gtk.HBox(spacing=WIDGET_SPACING)
        self.tray_battery_image = ImageBox(app_theme.get_pixbuf("power/tray_battery.png"))
        self.tray_battery_status_label = self.__setup_label(_("Show Battery Status In Tray"), 
                                                            TITLE_FONT_SIZE, 
                                                            ALIGN_START)
        self.tray_battery_status_label.set_sensitive(self.power_manager.get_tray_battery_status())
        self.tray_battery_status_toggle_align = self.__setup_align(padding_top = 2, 
                                                                   padding_left = 80)
        self.tray_battery_status_toggle = self.__setup_toggle()
        self.tray_battery_status_toggle.set_active(self.power_manager.get_tray_battery_status())
        self.tray_battery_status_toggle.connect("toggled", self.__toggled, "tray_battery_status")
        self.tray_battery_status_toggle_align.add(self.tray_battery_status_toggle)
        self.__widget_pack_start(self.tray_battery_status_box, 
            [self.tray_battery_image, 
             self.tray_battery_status_label, 
             self.tray_battery_status_toggle_align])
        self.tray_battery_status_align.add(self.tray_battery_status_box)
        self.tray_battery_status_align.set_child_visible(is_laptop())
        '''
        this->gtk.VBox pack_start
        '''
        self.__widget_pack_start(self, 
            [self.button_power_config_align, 
             self.press_button_power_align, 
             self.close_notebook_cover_align, 
             #self.press_button_hibernate_align, 
             self.power_save_config_align, 
             self.suspend_status_align, 
             #self.close_harddisk_align, 
             self.close_monitor_align, 
             self.percentage_align, 
             self.wakeup_password_align, 
             self.tray_battery_status_align, 
            ])

        self.connect("expose-event", self.__expose)

        self.__send_message("status", ("power", ""))
        self.__send_message("status", ("power", "show_reset"))

    def show_again(self):                                                       
        self.__send_message("status", ("power", ""))

    def __power_settings_changed(self, key):
        if key != "percentage":
            return
        
        self.percentage_progressbar.progress_buffer.progress = self.power_manager.power_settings.get_double("percentage")

    def __handle_dbus_replay(self, *reply):                                     
        pass                                                                    
                                                                                
    def __handle_dbus_error(self, *error):                                      
        pass                                                                    
                                                                                
    def __send_message(self, message_type, message_content):                    
        if is_dbus_name_exists(APP_DBUS_NAME):                                  
            bus_object = dbus.SessionBus().get_object(APP_DBUS_NAME, APP_OBJECT_NAME)
            method = bus_object.get_dbus_method("message_receiver")             
            method(message_type,                                                
                   message_content,                                             
                   reply_handler=self.__handle_dbus_replay,                     
                   error_handler=self.__handle_dbus_error)       

    def __setup_separator(self):                                                
        hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        hseparator.set_size_request(500, HSEPARATOR_HEIGHT)                                    
        return hseparator                                                       
                                                                                
    def __setup_title_label(self,                                               
                            text="",                                            
                            text_color=app_theme.get_color("globalTitleForeground"),
                            text_size=TITLE_FONT_SIZE,                          
                            text_x_align=ALIGN_START,                           
                            label_width=180):                                   
        return Label(text = text,                                               
                     text_color = text_color,                                   
                     text_size = text_size,                                     
                     text_x_align = text_x_align,                               
                     label_width = label_width, 
                     enable_select = False, 
                     enable_double_click = False)     

    def __setup_title_align(self, 
                            pixbuf, 
                            text, 
                            padding_top=FRAME_TOP_PADDING, 
                            padding_left=TEXT_WINDOW_LEFT_PADDING):
        align = self.__setup_align(padding_top = padding_top, padding_left = padding_left)              
        align_box = gtk.VBox(spacing = WIDGET_SPACING)                             
        title_box = gtk.HBox(spacing = WIDGET_SPACING)                             
        image = ImageBox(pixbuf)                                                   
        label = self.__setup_title_label(text)                                     
        separator = self.__setup_separator()                                       
        self.__widget_pack_start(title_box, [image, label])                        
        self.__widget_pack_start(align_box, [title_box, separator])                
        align.add(align_box)                                                       
        return align        

    def reset(self):
        self.__send_message("status", ("power", _("Reset to default value")))
        self.power_manager.reset()
        self.press_button_power_combo.set_select_index(self.power_manager.get_press_button_power(self.power_manage_items))
        self.close_notebook_cover_combo.set_select_index(self.power_manager.get_close_notebook_cover(self.power_manage_items))
        self.press_button_hibernate_combo.set_select_index(self.power_manager.get_press_button_hibernate(self.power_manage_items))
        self.suspend_status_combo.set_select_index(self.power_manager.get_suspend_status(self.wait_duration_items))
        self.close_monitor_combo.set_select_index(self.power_manager.get_close_monitor(self.wait_duration_items))
        self.wakeup_password_toggle.set_active(self.power_manager.get_wakeup_password())
        self.tray_battery_status_toggle.set_active(self.power_manager.get_tray_battery_status())

    def __expose(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation

        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                                               
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)                                                 
        cr.fill()

    def __setup_progressbar(self, progress):
        progressbar = PowerProgressBar()
        progressbar.progress_buffer.progress = progress
        progressbar.set_size_request(121, WIDGET_HEIGHT)
        return progressbar

    def __setup_label(self, text="", text_size=CONTENT_FONT_SIZE, align=ALIGN_END):
        label = Label(text, None, text_size, align, 200, False, False, False)
        return label

    def __setup_combo(self, items=[]):
        combo = ComboBox(items, None, 0, 120)
        combo.set_size_request(-1, WIDGET_HEIGHT)
        return combo

    def __setup_toggle(self):
        toggle = ToggleButton(app_theme.get_pixbuf("toggle_button/inactive_normal.png"), 
            app_theme.get_pixbuf("toggle_button/active_normal.png"))
        return toggle

    def __setup_align(self, 
                      padding_top=8, 
                      padding_bottom=0, 
                      padding_left=TEXT_WINDOW_LEFT_PADDING + IMG_WIDTH + WIDGET_SPACING, 
                      padding_right=0):
        align = gtk.Alignment()
        align.set(0.0, 0.5, 0, 0)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        return align

    def __widget_pack_start(self, parent_widget, widgets=[]):
        if parent_widget == None:
            return
        for item in widgets:
            parent_widget.pack_start(item, False, False)

    def __combo_item_selected(self, widget, item_text=None, item_value=None, item_index=None, object=None):
        if object == "press_button_power":
            self.__send_message("status", ("power", _("Changed Press Power Button to %s") % item_text))
            self.power_manager.set_press_button_power(item_value)
            return

        if object == "close_notebook_cover":
            self.__send_message("status", ("power", _("Changed Close Notebook Cover to %s") % item_text))
            self.power_manager.set_close_notebook_cover(item_value)
            return

        if object == "press_button_hibernate":
            self.__send_message("status", ("power", _("Changed Press Hibernate Button to %s") % item_text))
            self.power_manager.set_press_button_hibernate(item_value)
            return

        if object == "suspend_status":
            self.__send_message("status", ("power", _("Changed Suspend Status to %s") % item_text))
            self.power_manager.set_suspend_status(item_value)
            return

        if object == "close_harddisk":
            self.__send_message("status", ("power", _("Changed Close Harddisk to %s") % item_text))
            self.power_manager.set_close_harddisk(item_value)
            return

        if object == "close_monitor":
            self.__send_message("status", ("power", _("Changed Close Monitor to %s") % item_text))
            self.power_manager.set_close_monitor(item_value)
            return

    def __toggled(self, widget, object=None):
        if object == "wakeup_password":
            if widget.get_active():
                self.__send_message("status", ("power", _("Changed to Password Protection Wakeup")))
            else:
                self.__send_message("status", ("power", _("Changed to NO Password Protection Wakeup")))
            self.power_manager.set_wakeup_password(widget.get_active())
            self.wakeup_password_label.set_sensitive(widget.get_active())
            return

        if object == "tray_battery_status":
            if widget.get_active():
                self.__send_message("status", ("power", _("Changed to Show Battery Status In Tray")))
            else:
                self.__send_message("status", ("power", _("Changed to Hide Battery Status In Tray")))
            self.power_manager.set_tray_battery_status(widget.get_active())
            return

gobject.type_register(PowerView)        
