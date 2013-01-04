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
from dtk.ui.constant import ALIGN_START
from dtk.ui.utils import (color_hex_to_cairo, set_clickable_cursor, 
                          is_dbus_name_exists)
from dtk.ui.draw import cairo_state, draw_text
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
        self.text_size = 10

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
        i = 0

        with cairo_state(cr):
            while i < len(output_infos):
                output_x = x + i * (self.output_width + self.output_padding)
                output_width = self.output_width - i * self.output_small_size
                output_height = self.output_height - i * self.output_small_size
                output_name = output_infos[i][0]
                output_display_name = self.__display_manager.get_output_display_name(output_name)
                '''
                background
                '''
                cr.set_source_rgb(*color_hex_to_cairo("#DFDFDF"))
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
                draw_text(cr = cr, 
                          markup = str(i + 1), 
                          x = output_x + output_width - self.text_size, 
                          y = y + output_height - self.text_size * 2, 
                          w = self.text_size, 
                          h = self.text_size, 
                          text_size = self.text_size, 
                          alignment = pango.ALIGN_LEFT)
                '''
                stroke
                '''
                cr.set_source_rgb(*color_hex_to_cairo("#797979"))
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
                    cr.rectangle(output_x, y, output_width, output_height)
                    cr.stroke()
                
                if self.__eventx > output_x + output_width or self.__eventx < output_x:
                    i += 1
                    continue
                '''
                selected stroke && emit
                '''
                cr.set_source_rgb(*color_hex_to_cairo("#FFCC34"))
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
        self.__setup_sizes_items()
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
                               (_("Never"), -1)]
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
        self.monitor_display_align = self.__setup_align(padding_left = 0)
        self.monitor_display_box = gtk.VBox(spacing = WIDGET_SPACING)
        self.monitor_display_title_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.monitor_display_image = ImageBox(app_theme.get_pixbuf("display/monitor_display.png"))
        self.monitor_display_label = self.__setup_title_label(_("Monitor Display"))
        self.monitor_display_separator = self.__setup_separator()
        self.__widget_pack_start(self.monitor_display_title_box, 
                                 [self.monitor_display_image, 
                                  self.monitor_display_label])
        self.__widget_pack_start(self.monitor_display_box, 
                                 [self.monitor_display_title_box, self.monitor_display_separator])
        self.monitor_display_align.add(self.monitor_display_box)
        '''
        monitor
        '''
        self.monitor_align = self.__setup_align()
        self.monitor_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.monitor_label = self.__setup_label(_("Monitor"))
        self.monitor_combo = self.__setup_combo(self.monitor_items, 370)
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
        self.goto_label = self.__setup_label(_("Relative Settings"))
        self.goto_individuation_label = self.__setup_label(text = _("<span foreground=\"blue\" underline=\"single\">Individuation</span>"), width = 180)
        self.goto_individuation_label.connect("button-press-event", 
                                              self.__button_press, 
                                              "individuation")
        set_clickable_cursor(self.goto_individuation_label)
        self.goto_power_label = self.__setup_label(text = _("<span foreground=\"blue\" underline=\"single\">Power</span>"), width = 180)
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
        sizes && rotation
        '''
        self.sizes_align = self.__setup_align()
        self.sizes_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.sizes_label = self.__setup_label(_("Resolution"))
        self.sizes_combo = self.__setup_combo(self.sizes_items, 150)
        self.sizes_combo.set_select_index(self.display_manager.get_screen_size_index(self.__current_output_name, 
                                                                                     self.sizes_items))
        self.sizes_combo.connect("item-selected", self.__combo_item_selected, "sizes_combo")
        self.rotation_label = self.__setup_label(_("Rotation"))
        self.rotation_combo = self.__setup_combo(self.rotation_items)
        self.rotation_combo.set_select_index(self.display_manager.get_screen_rotation_index(self.__current_output_name))
        self.rotation_combo.connect("item-selected", self.__combo_item_selected, "rotation_combo")
        self.__widget_pack_start(self.sizes_box, 
            [self.sizes_label, 
             self.sizes_combo, 
             self.rotation_label, 
             self.rotation_combo])
        self.sizes_align.add(self.sizes_box)
        '''
        monitor brightness
        '''
        self.monitor_bright_align = self.__setup_align(padding_left = 0)
        self.monitor_bright_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.monitor_bright_image = ImageBox(app_theme.get_pixbuf("display/monitor_bright.png")) 
        self.monitor_bright_label = self.__setup_label(_("Monitor Brightness"), text_size = TITLE_FONT_SIZE, width = 180)
        self.__widget_pack_start(self.monitor_bright_box, 
                                 [self.monitor_bright_image, self.monitor_bright_label])
        self.monitor_bright_align.add(self.monitor_bright_box)
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
                                          value_min = 5, 
                                          value_max = 100)
        self.brightness_scale.set_size_request(370, 33)
        self.brightness_scale.value = self.display_manager.get_screen_brightness()
        self.brightness_scale.connect("button-release-event", self.__set_brightness)
        self.__widget_pack_start(self.brightness_box, 
            [self.brightness_label_align, 
             self.brightness_scale])
        self.brightness_align.add(self.brightness_box)
        '''
        auto adjust monitor brightness
        '''
        self.auto_adjust_align = self.__setup_align()
        self.auto_adjust_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.auto_adjust_label = self.__setup_label(_("Auto Adjust Monitor Brightness"), width = 190)
        self.auto_adjust_toggle_align = self.__setup_align(padding_top = 4, padding_left = 0)
        self.auto_adjust_toggle = self.__setup_toggle()
        self.auto_adjust_toggle.set_active(self.display_manager.is_enable_close_monitor())
        self.auto_adjust_toggle.connect("toggled", self.__toggled, "auto_adjust_toggle")
        self.auto_adjust_toggle_align.add(self.auto_adjust_toggle)
        self.close_monitor_label = self.__setup_label(_("Close Monitor"))
        self.close_monitor_combo = self.__setup_combo(self.duration_items)
        self.close_monitor_combo.set_select_index(self.display_manager.get_close_monitor_index(self.duration_items))
        self.close_monitor_combo.connect("item-selected", self.__combo_item_selected, "close_monitor_combo")
        self.__widget_pack_start(self.auto_adjust_box, 
            [self.auto_adjust_label, 
             self.auto_adjust_toggle_align, 
             self.close_monitor_label, 
             self.close_monitor_combo])
        self.auto_adjust_align.add(self.auto_adjust_box)
        '''
        monitor lock
        '''
        self.monitor_lock_align = self.__setup_align(padding_left = 0)
        self.monitor_lock_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.monitor_lock_image = ImageBox(app_theme.get_pixbuf("lock/lock.png"))
        self.monitor_lock_label = self.__setup_label(text = _("Monitor Screen Lock"), text_size = TITLE_FONT_SIZE, width = 180)
        self.__widget_pack_start(self.monitor_lock_box, 
                                 [self.monitor_lock_image, self.monitor_lock_label])
        self.monitor_lock_align.add(self.monitor_lock_box)
        '''
        auto monitor lock
        '''
        self.auto_lock_align = self.__setup_align()
        self.auto_lock_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.auto_lock_label = self.__setup_label(_("Auto Lock User Monitor Screen"), width = 190)
        self.auto_lock_toggle_align = self.__setup_align(padding_top = 4, padding_left = 0)
        self.auto_lock_toggle = self.__setup_toggle()
        self.auto_lock_toggle.set_active(self.display_manager.is_enable_lock_display())
        self.auto_lock_toggle.connect("toggled", self.__toggled, "auto_lock_toggle")
        self.auto_lock_toggle_align.add(self.auto_lock_toggle)
        self.lock_display_label = self.__setup_label(_("Lock Screen")) 
        self.lock_display_combo = self.__setup_combo(self.duration_items)
        self.lock_display_combo.set_select_index(self.display_manager.get_lock_display_index(self.duration_items))
        self.lock_display_combo.connect("item-selected", self.__combo_item_selected, "lock_display_combo")
        self.__widget_pack_start(self.auto_lock_box, 
            [self.auto_lock_label, 
             self.auto_lock_toggle_align, 
             self.lock_display_label, 
             self.lock_display_combo])
        self.auto_lock_align.add(self.auto_lock_box)
        '''
        left_align pack_start
        '''
        self.__widget_pack_start(self.left_box, 
            [self.monitor_display_align, 
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

        self.__setup_sizes_items()
        if len(self.sizes_items):
            self.sizes_combo.set_items(items = self.sizes_items, max_width = 150)
        self.sizes_combo.set_select_index(self.display_manager.get_screen_size_index(
            self.__current_output_name, self.sizes_items))
    
    def __select_output(self, widget, output_name):
        self.__change_current_output(output_name, False)
    
    def __xrandr_changed(self, key):
        if key != "output-names":
            return

        self.display_manager.init_xml()
        self.__setup_monitor_items()
        self.monitor_combo.set_items(items = self.monitor_items, max_width = 370)

    def __set_brightness(self, widget, event):
        self.display_manager.set_screen_brightness(self.__current_output_name, 
                                                   self.brightness_scale.value / 100.0)
    
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
                self.display_manager.set_close_monitor(DisplayManager.BIG_NUM / 60)
            return

        if object == "auto_lock_toggle":
            if not widget.get_active():
                self.display_manager.set_lock_display(DisplayManager.BIG_NUM / 60)
            return

    def __combo_item_selected(self, widget, item_text=None, item_value=None, item_index=None, object=None):
        if object == "monitor_combo":
            self.__change_current_output(item_value)
            return

        if object == "sizes_combo":
            self.__send_message("status", ("display", _("Changed Resolution")))
            self.display_manager.set_screen_size(self.__current_output_name, self.sizes_items[item_value][0])
            return
        
        if object == "rotation_combo":
            self.display_manager.set_screen_rotation(self.__current_output_name, item_value)
            return

        if object == "close_monitor_combo":
            self.display_manager.set_close_monitor(item_value)
            return

        if object == "lock_display_combo":
            self.display_manager.set_lock_display(item_value)
            return

    def __resize_box(self, widget, height):
        self.monitor_resize_box.set_size_request(self.resize_width, height - FRAME_TOP_PADDING)

    def __setup_separator(self):
        hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        hseparator.set_size_request(380, 10)
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
                     label_width = label_width)
    
    def __setup_label(self, text="", text_size=CONTENT_FONT_SIZE, width=80, align=ALIGN_START, wrap_width=None):
        label = Label(text = text, 
                      text_color = None, 
                      text_size = text_size, 
                      text_x_align = align, 
                      label_width = width, 
                      wrap_width = wrap_width)
        return label

    def __setup_combo(self, items=[], width=120):
        combo = ComboBox(items, None, 0, width)
        combo.set_size_request(width, WIDGET_HEIGHT)
        return combo

    def __setup_toggle(self):
        toggle = ToggleButton(app_theme.get_pixbuf("toggle_button/inactive_normal.png"), 
            app_theme.get_pixbuf("toggle_button/active_normal.png"))
        return toggle

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
