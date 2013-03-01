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
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.box import ResizableBox, ImageBox
from dtk.ui.label import Label
from dtk.ui.line import HSeparator
from dtk.ui.combo import ComboBox
from dtk.ui.hscalebar import HScalebar
from dtk.ui.button import ToggleButton
from dtk.ui.constant import ALIGN_START, ALIGN_END
from dtk.ui.utils import color_hex_to_cairo, set_clickable_cursor
from deepin_utils.ipc import is_dbus_name_exists
from dtk.ui.draw import (cairo_state, cairo_disable_antialias, draw_text, 
                         draw_pixbuf)
import gobject
import gtk
import pango
import dbus
from constant import *
from nls import _
from display_manager import DisplayManager

class MonitorResizableBox(ResizableBox):
    __gsignals__ = {                                                             
        "select-output" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),}
    
    def __init__(self, display_manager):
        ResizableBox.__init__(self)

        self.__display_manager = display_manager

        self.select_output_name = None

        self.output_width = 220
        self.output_height = 120
        self.output_padding = 3
        self.output_small_size = 20
        self.line_width = 1.0
        self.text_size = 10

        self.primary_pixbuf = app_theme.get_pixbuf("display/n01.png")
        self.other_pixbuf = app_theme.get_pixbuf("display/n00.png")

        self.__eventx = 0
        self.__eventy = 0

        self.connect("button-press-event", self.__button_press)

    def __button_press(self, widget, event):
        self.select_output_name = None
        self.__eventx = event.x
        self.__eventy = event.y
        self.invalidate()

    def select_output(self, output_name):
        output_names = self.__display_manager.get_output_names()
        i = 0

        while i < len(output_names):
            if output_names[i].find(output_name) != -1:
                self.select_output_name = output_name
                return

            i += 1
    
    def expose_override(self, cr, rect):
        x, y = rect.x, rect.y
        x = (self.width - self.output_width) / 2
        y += 10
        
        output_infos = self.__display_manager.get_output_info()
        output_count = len(output_infos)
        
        ''' 
        FIXME: ResizableBox logic issue
        if output_count < 2:
            self.set_resizeable(False)
        '''

        i = 0
        with cairo_disable_antialias(cr):
            while i < output_count:
                output_x = x + i * (self.output_width + self.output_padding)
                if output_count > 1:
                    output_x -= self.output_width / 3.0
                output_width = self.output_width - i * self.output_small_size
                output_height = self.output_height - i * self.output_small_size
                output_name = output_infos[i][0]
                is_primary = output_infos[i][5]
                output_display_name = self.__display_manager.get_output_display_name(output_name)
                '''
                background
                '''
                cr.set_source_rgb(*color_hex_to_cairo("#DFDFDF"))
                cr.set_line_width(self.line_width)
                cr.rectangle(output_x, 
                             y, 
                             output_width, 
                             output_height)
                cr.fill()
                '''
                output display name
                '''
                draw_text(cr = cr, 
                          markup = output_display_name, 
                          x = output_x, 
                          y = y + (output_height - self.text_size) / 2, 
                          w = output_width, 
                          h = self.text_size,
                          text_size = self.text_size, 
                          alignment = pango.ALIGN_CENTER)
                
                if output_count > 1:
                    if is_primary:
                        draw_pixbuf(cr, 
                                    self.primary_pixbuf.get_pixbuf(), 
                                    output_x + output_width - self.primary_pixbuf.get_pixbuf().get_width(), 
                                    y + output_height - self.primary_pixbuf.get_pixbuf().get_height())
                    else:
                        draw_pixbuf(cr,                                         
                                    self.other_pixbuf.get_pixbuf(),              
                                    output_x + output_width - self.other_pixbuf.get_pixbuf().get_width(), 
                                    y + output_height - self.other_pixbuf.get_pixbuf().get_height())
                    
                    draw_text(cr = cr, 
                              markup = str(i + 1), 
                              x = output_x + output_width - self.text_size - 5, 
                              y = y + output_height - self.text_size * 2, 
                              w = self.text_size, 
                              h = self.text_size, 
                              text_size = self.text_size, 
                              text_color = "#FFFFFF", 
                              alignment = pango.ALIGN_LEFT)

                '''
                stroke
                '''
                cr.set_source_rgb(*color_hex_to_cairo("#797979"))
                cr.set_line_width(self.line_width)
                cr.rectangle(output_x, 
                             y, 
                             output_width, 
                             output_height)
                cr.stroke()
                '''
                selected stroke
                '''
                if self.select_output_name == output_name:
                    cr.set_source_rgb(*color_hex_to_cairo("#FFCC34"))
                    cr.set_line_width(self.line_width)
                    cr.rectangle(output_x, y, output_width, output_height)
                    cr.stroke()
                
                if self.__eventx > output_x + output_width or self.__eventx < output_x:
                    i += 1
                    continue
                '''
                selected stroke && emit
                '''
                cr.set_source_rgb(*color_hex_to_cairo("#FFCC34"))
                cr.set_line_width(self.line_width)
                cr.rectangle(output_x, y, output_width, output_height)
                cr.stroke()
                self.emit("select-output", output_name)

                i += 1

gobject.type_register(MonitorResizableBox)

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
        self.__xrandr_settings = self.display_manager.get_xrandr_settings()
        self.__xrandr_settings.connect("changed", self.__xrandr_changed)

        self.resize_width = 790
        self.resize_height = 200
        self.monitor_items = []
        self.__output_names = []
        self.__current_output_name = self.display_manager.get_primary_output_name()
        self.__setup_monitor_items()
        self.sizes_items = []
        self.monitor_combo = None
        if len(self.monitor_items) > 1 and self.display_manager.is_copy_monitors():
            self.__set_same_sizes()
        else:
            self.__setup_sizes_items()
        self.multi_monitors_items = [(_("Copy Display"), 1), 
                                     (_("Extend Display"), 2), 
                                     (_("Only Monitor 1 shown"), 3), 
                                     (_("Only Monitor 2 shown"), 4)]
        self.rotation_items = [(_("Normal"), 1), 
                               (_("Right"), 2), 
                               (_("Left"), 3), 
                               (_("Inverted"), 4)]
        self.duration_items = [("1 %s" % _("Minute"), 1), 
                               ("2 %s" % _("Minutes"), 2), 
                               ("3 %s" % _("Minutes"), 3), 
                               ("5 %s" % _("Minutes"), 5), 
                               ("10 %s" % _("Minutes"), 10), 
                               ("30 %s" % _("Minutes"), 30), 
                               ("1 %s" % _("Hour"), 60), 
                               (_("Never"), DisplayManager.BIG_NUM / 60)]
        '''
        scrolled_window
        '''
        self.scrolled_window = ScrolledWindow()
        self.scrolled_window.set_size_request(800, 425)
        self.scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.main_box = gtk.VBox()
        self.body_box = gtk.HBox()
        '''
        left, right align
        '''
        self.left_align = self.__setup_align(padding_top = FRAME_TOP_PADDING, 
                                             padding_left = TEXT_WINDOW_LEFT_PADDING)
        self.right_align = self.__setup_align(padding_top = FRAME_TOP_PADDING, 
                                              padding_left = 0)
        '''
        left, right box
        '''
        self.left_box = gtk.VBox(spacing = WIDGET_SPACING)
        self.right_box = gtk.VBox(spacing = WIDGET_SPACING)
        '''
        monitor operation && detect
        '''
        self.monitor_resize_align = self.__setup_align(padding_top = 11, 
                                                       padding_left = int(TEXT_WINDOW_LEFT_PADDING / 2))
        self.monitor_resize_box = MonitorResizableBox(self.display_manager)
        self.monitor_resize_box.select_output(self.__current_output_name)
        self.monitor_resize_box.connect("select-output", self.__select_output)
        self.monitor_resize_box.connect("resize", self.__resize_box)
        self.monitor_resize_align.add(self.monitor_resize_box)
        '''
        monitor display
        '''
        self.monitor_display_align = self.__setup_title_align(
            app_theme.get_pixbuf("display/monitor_display.png"), 
            _("Monitor Display"), 
            0)
        '''
        monitor
        '''
        self.monitor_align = self.__setup_align()
        self.monitor_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.monitor_label = self.__setup_label(_("Monitor"))
        self.monitor_combo = self.__setup_combo(self.monitor_items)
        self.monitor_combo.set_select_index(self.display_manager.get_primary_output_name_index(self.monitor_items))
        self.monitor_combo.connect("item-selected", self.__combo_item_selected, "monitor_combo")
        self.__widget_pack_start(self.monitor_box, 
            [self.monitor_label, 
             self.monitor_combo])
        self.monitor_align.add(self.monitor_box)
        '''
        goto individuation or power setting
        '''
        self.goto_align = self.__setup_align()
        self.goto_box = gtk.VBox(spacing = WIDGET_SPACING)
        self.goto_label = self.__setup_label(_("Relative Settings"), 
                                             width = None, 
                                             align = ALIGN_START)
        goto_color = GOTO_FG_COLOR
        self.goto_individuation_label = self.__setup_label(
            text = _("<span foreground=\"%s\" underline=\"single\">Individuation</span>") % goto_color, 
            width = None, 
            align = ALIGN_START)
        self.goto_individuation_label.connect("button-press-event", 
                                              self.__button_press, 
                                              "individuation")
        set_clickable_cursor(self.goto_individuation_label)
        self.goto_power_label = self.__setup_label(
            text = _("<span foreground=\"%s\" underline=\"single\">Power</span>") % goto_color, 
            width = None, 
            align = ALIGN_START)
        self.goto_power_label.connect("button-press-event", 
                                      self.__button_press, 
                                      "power")
        set_clickable_cursor(self.goto_power_label)
        self.__widget_pack_start(self.goto_box, 
                                 [self.goto_label, 
                                  self.goto_individuation_label, 
                                  self.goto_power_label
                                 ])
        self.goto_align.add(self.goto_box)
        '''
        sizes
        '''
        self.sizes_align = self.__setup_align()
        self.sizes_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.sizes_label = self.__setup_label(_("Resolution"))
        self.sizes_combo = self.__setup_combo(self.sizes_items)
        if self.sizes_combo:
            self.sizes_combo.set_select_index(
                self.display_manager.get_screen_size_index(self.__current_output_name, 
                                                           self.sizes_items))
            self.sizes_combo.connect("item-selected", self.__combo_item_selected, "sizes_combo")
            self.__widget_pack_start(self.sizes_box, 
                                     [self.sizes_label, self.sizes_combo])
        self.sizes_align.add(self.sizes_box)
        '''
        rotation
        '''
        self.rotation_align = self.__setup_align()
        self.rotation_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.rotation_label = self.__setup_label(_("Rotation"))
        self.rotation_combo = self.__setup_combo(self.rotation_items)
        self.rotation_combo.set_select_index(self.display_manager.get_screen_rotation_index(self.__current_output_name))
        self.rotation_combo.connect("item-selected", self.__combo_item_selected, "rotation_combo")
        self.__widget_pack_start(self.rotation_box, 
            [self.rotation_label, 
             self.rotation_combo])
        self.rotation_align.add(self.rotation_box)
        '''
        multi-monitors
        '''
        self.multi_monitors_align = self.__setup_align()
        self.multi_monitors_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.multi_monitors_label = self.__setup_label(_("Multi-Monitors"))
        self.multi_monitors_combo = self.__setup_combo(self.multi_monitors_items)
        self.multi_monitors_combo.set_select_index(self.display_manager.get_multi_monitor_index())
        self.multi_monitors_combo.connect("item-selected", self.__combo_item_selected, "multi_monitors_combo")
        self.__widget_pack_start(self.multi_monitors_box, 
            [self.multi_monitors_label, self.multi_monitors_combo])
        self.multi_monitors_align.add(self.multi_monitors_box)
        if self.display_manager.get_output_count() < 2:
            self.multi_monitors_align.set_size_request(-1, 0)
            self.multi_monitors_align.set_child_visible(False)
        '''
        monitor brightness
        '''
        self.monitor_bright_align = self.__setup_title_align(
            app_theme.get_pixbuf("display/monitor_bright.png"), 
            _("Monitor Brightness"))
        '''
        brightness
        '''
        self.brightness_align = self.__setup_align()
        self.brightness_box = gtk.HBox(spacing = 2)
        self.brightness_label_align = self.__setup_align(padding_top = 8, 
                                                         padding_left = 0, 
                                                         padding_right = 5)
        self.brightness_label = self.__setup_label(_("Brightness"))
        self.brightness_label_align.add(self.brightness_label)
        
        self.brightness_scale = HScalebar(point_dpixbuf = app_theme.get_pixbuf("scalebar/point.png"), 
                                          value_min = 0.1, 
                                          value_max = 1.0)
        self.brightness_scale.set_size_request(HSCALEBAR_WIDTH, 33)
        self.brightness_scale.set_value(self.display_manager.get_screen_brightness())
        self.brightness_scale.connect("value-changed", self.__set_brightness)
        self.__widget_pack_start(self.brightness_box, 
            [self.brightness_label_align, 
             self.brightness_scale])
        self.brightness_align.add(self.brightness_box)
        '''
        auto adjust monitor brightness
        '''
        self.auto_adjust_align = self.__setup_align()
        self.auto_adjust_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.auto_adjust_label = self.__setup_label(_("Auto Adjust Brightness"))
        self.auto_adjust_toggle_align = self.__setup_align(padding_top = 4, padding_left = 158)
        self.auto_adjust_toggle = self.__setup_toggle()
        self.auto_adjust_toggle.set_active(self.display_manager.is_enable_close_monitor())
        self.auto_adjust_toggle.connect("toggled", self.__toggled, "auto_adjust_toggle")
        self.auto_adjust_toggle_align.add(self.auto_adjust_toggle)
        self.__widget_pack_start(self.auto_adjust_box, 
            [self.auto_adjust_label, self.auto_adjust_toggle_align])
        self.auto_adjust_align.add(self.auto_adjust_box)
        '''
        close monitor
        '''
        self.close_monitor_align = self.__setup_align()
        self.close_monitor_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.close_monitor_label = self.__setup_label(_("Close Monitor"))
        self.close_monitor_combo = self.__setup_combo(self.duration_items)
        self.close_monitor_combo.set_select_index(self.display_manager.get_close_monitor_index(self.duration_items))
        self.close_monitor_combo.connect("item-selected", self.__combo_item_selected, "close_monitor_combo")
        self.__widget_pack_start(self.close_monitor_box, 
            [self.close_monitor_label, 
             self.close_monitor_combo])
        self.close_monitor_align.add(self.close_monitor_box)
        '''
        monitor lock
        '''
        self.monitor_lock_align = self.__setup_title_align(
            app_theme.get_pixbuf("lock/lock.png"), 
            _("Monitor Screen Lock"))
        '''
        auto monitor lock
        '''
        self.auto_lock_align = self.__setup_align()
        self.auto_lock_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.auto_lock_label = self.__setup_label(_("Auto Lock User Screen"))
        self.auto_lock_toggle_align = self.__setup_align(padding_top = 4, padding_left = 158)
        self.auto_lock_toggle = self.__setup_toggle()
        is_enable_lock_display = self.display_manager.is_enable_lock_display()
        self.auto_lock_toggle.set_active(is_enable_lock_display)
        self.auto_lock_toggle.connect("toggled", self.__toggled, "auto_lock_toggle")
        self.auto_lock_toggle_align.add(self.auto_lock_toggle)
        self.__widget_pack_start(self.auto_lock_box, 
            [self.auto_lock_label, self.auto_lock_toggle_align])
        self.auto_lock_align.add(self.auto_lock_box)
        '''
        lock display
        '''
        self.lock_display_align = self.__setup_align(padding_bottom = 20)
        self.lock_display_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.lock_display_label = self.__setup_label(_("Lock Screen")) 
        self.lock_display_combo = self.__setup_combo(self.duration_items)
        self.lock_display_combo.set_select_index(self.display_manager.get_lock_display_index(self.duration_items))
        self.lock_display_combo.connect("item-selected", self.__combo_item_selected, "lock_display_combo")
        self.__widget_pack_start(self.lock_display_box, 
            [self.lock_display_label, 
             self.lock_display_combo])
        self.lock_display_align.add(self.lock_display_box)
        '''
        left_align pack_start
        '''
        self.__widget_pack_start(self.left_box, 
            [self.monitor_display_align, 
             self.monitor_align, 
             self.sizes_align, 
             self.rotation_align, 
             self.multi_monitors_align, 
             self.monitor_bright_align, 
             self.brightness_align, 
             self.auto_adjust_align, 
             self.close_monitor_align, 
             self.monitor_lock_align, 
             self.auto_lock_align, 
             self.lock_display_align])
        self.left_align.add(self.left_box)
        '''
        right_align pack_start
        '''
        self.__widget_pack_start(self.right_box, 
            [self.goto_align])
        self.right_box.set_size_request(280, -1)
        self.right_align.add(self.right_box)
        '''
        main && body box
        '''
        self.main_box.pack_start(self.monitor_resize_align, False, False)
        self.body_box.pack_start(self.left_align)
        self.body_box.pack_start(self.right_align, False, False)
        self.main_box.pack_start(self.body_box)
        '''
        this->HBox pack_start
        '''
        self.scrolled_window.add_child(self.main_box)
        self.pack_start(self.scrolled_window)

        self.__send_message("status", ("display", ""))

    def reset(self):
        self.__send_message("status", ("display", _("Reset to default value")))
        self.display_manager.reset()
        self.close_monitor_combo.set_select_index(self.display_manager.get_close_monitor_index(self.duration_items))
        self.lock_display_combo.set_select_index(self.display_manager.get_lock_display_index(self.duration_items))

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

    def __button_press(self, widget, event, module_id):
        self.__send_message("goto", (module_id, ""))

    def __expose(self, widget, event):
        cr = widget.window.cairo_create()                                        
        rect = widget.allocation                                                 
        
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                  
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)                    
        cr.fill()

    def __change_current_output(self, output_name, from_monitor_combo=True):
        self.__current_output_name = output_name

        if not from_monitor_combo:
            self.monitor_combo.set_select_index(self.display_manager.get_output_name_index(output_name, self.monitor_items))

        if not self.display_manager.is_copy_monitors():
            self.__setup_sizes_items()
        if len(self.sizes_items):
            self.sizes_combo.set_items(items = self.sizes_items, fixed_width = HSCALEBAR_WIDTH)
        self.sizes_combo.set_select_index(self.display_manager.get_screen_size_index(
            self.__current_output_name, self.sizes_items))
    
    def __select_output(self, widget, output_name):
        self.__change_current_output(output_name, False)
    
    def __set_same_sizes(self):
        same_sizes = self.display_manager.get_same_sizes(                      
            self.display_manager.get_screen_sizes(self.monitor_items[0][1]), 
            self.display_manager.get_screen_sizes(self.monitor_items[1][1]))
        i = 0
        
        del self.sizes_items[:]                                             
        while i < len(same_sizes):                                          
            self.sizes_items.append((same_sizes[i], i))                     
                                                                                
            i += 1                                                          
    
    def __xrandr_changed(self, key):
        if key != "output-names":
            return

        self.display_manager.init_xml()
        self.__setup_monitor_items()
        self.monitor_combo.set_items(items = self.monitor_items, fixed_width = HSCALEBAR_WIDTH)
        if len(self.monitor_items) > 1:
            if self.display_manager.is_copy_monitors():
                self.__set_same_sizes()
                self.sizes_combo.set_items(items = self.sizes_items,                    
                                           fixed_width = HSCALEBAR_WIDTH) 

            self.multi_monitors_align.set_size_request(-1, 30)
            self.multi_monitors_align.set_child_visible(True)

    def __set_brightness(self, widget, event):
        value = self.brightness_scale.get_value()
        self.__send_message("status", ("display", _("Changed brightness to %0.2f") % value))
        self.display_manager.set_screen_brightness(self.__current_output_name, 
                                                   value)
    
    def __setup_monitor_items(self):
        self.__output_names = self.display_manager.get_output_names()
        del self.monitor_items[:]
        i = 0

        while (i < len(self.__output_names)):
            self.monitor_items.append(self.display_manager.get_output_name(self.__output_names[i]))
            i += 1

    def __setup_sizes_items(self):
        screen_sizes = self.display_manager.get_screen_sizes(self.__current_output_name)
        del self.sizes_items[:]
        i = 0

        while i < len(screen_sizes):
            self.sizes_items.append((screen_sizes[i], i))
            i += 1

    def __toggled(self, widget, object=None):
        if object == "auto_adjust_toggle":
            if not widget.get_active():
                self.__send_message("status", ("display", _("Changed to manual adjustment")))
                self.display_manager.set_close_monitor(DisplayManager.BIG_NUM / 60)
            else:
                self.__send_message("status", ("display", _("Changed to automatic adjustment")))
            return

        if object == "auto_lock_toggle":
            if not widget.get_active():
                self.lock_display_combo.set_sensitive(False)
                self.__send_message("status", ("display", _("Changed to manual lock")))
            else:
                self.lock_display_combo.set_sensitive(True)
                self.__send_message("status", ("display", _("Changed to automatic lock")))
            return

    def __combo_item_selected(self, widget, item_text=None, item_value=None, item_index=None, object=None):
        if object == "monitor_combo":
            self.__send_message("status", ("display", _("Changed current output to %s") % item_value))
            self.__change_current_output(item_value)
            return

        if object == "sizes_combo":
            size = self.sizes_items[item_value][0]
            self.__send_message("status", ("display", _("Changed resolution to %s") % size))
            self.display_manager.set_screen_size(self.__current_output_name, size)
            return
        
        if object == "rotation_combo":
            self.__send_message("status", ("display", _("Changed rotation to %s") % item_text))
            self.display_manager.set_screen_rotation(self.__current_output_name, item_value)
            return

        if object == "multi_monitors_combo":
            self.__send_message("status", ("display", _("Changed multiply monitors mode to %s") % item_text))
            self.display_manager.set_multi_monitor(item_value)
            return
        
        if object == "close_monitor_combo":
            self.__send_message("status", ("display", _("Changed close monitor duration to %s") % item_text))
            self.display_manager.set_close_monitor(item_value)
            return

        if object == "lock_display_combo":
            self.__send_message("status", ("display", _("Changed lock display duration to %s") % item_text))
            if item_value == DisplayManager.BIG_NUM / 60:
                self.auto_lock_toggle.set_active(False)
            else:
                self.auto_lock_toggle.set_active(True)
            self.display_manager.set_lock_display(item_value)
            return

    def __resize_box(self, widget, height):
        self.monitor_resize_box.set_size_request(self.resize_width, height - FRAME_TOP_PADDING)

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
    
    def __setup_label(self, text="", text_size=CONTENT_FONT_SIZE, width=180, align=ALIGN_END, wrap_width=None):
        label = Label(text = text, 
                      text_color = None, 
                      text_size = text_size, 
                      text_x_align = align, 
                      label_width = width, 
                      wrap_width = wrap_width, 
                      enable_select = False, 
                      enable_double_click = False)
        return label

    def __setup_combo(self, items=[], width=HSCALEBAR_WIDTH):
        if len(items) == 0:
            return None

        combo = ComboBox(items = items, select_index = 0, max_width = width, fixed_width = width)
        combo.set_size_request(width, WIDGET_HEIGHT)
        return combo

    def __setup_toggle(self):
        toggle = ToggleButton(app_theme.get_pixbuf("toggle_button/inactive_normal.png"), 
            app_theme.get_pixbuf("toggle_button/active_normal.png"))
        return toggle

    def __setup_title_align(self, pixbuf, text, padding_top=FRAME_TOP_PADDING, padding_left=0):
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
    
    def __setup_align(self, 
                      xalign=0, 
                      yalign=0, 
                      xscale=0, 
                      yscale=0, 
                      padding_top=0, 
                      padding_bottom=0, 
                      padding_left=FRAME_LEFT_PADDING + int(WIDGET_SPACING / 2), 
                      padding_right=0):
        align = gtk.Alignment()
        align.set(xalign, yalign, xscale, yscale)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        align.connect("expose-event", self.__expose)
        return align

    def __widget_pack_start(self, parent_widget, widgets=[], expand=False, fill=False):
        if parent_widget == None:
            return
        for item in widgets:
            parent_widget.pack_start(item, expand, fill)

gobject.type_register(DisplayView)
