#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
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

# The way to mix PyGTK+ and PyGObject code, 
# run code `gi.repository` before any `import gobject`.
import settings

import sys
import os
from dtk.ui.utils import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))

from nls import _
from theme import app_theme
from dtk.ui.label import Label
from dtk.ui.button import RadioButton
from dtk.ui.scalebar import HScalebar
from dtk.ui.utils import propagate_expose, cairo_disable_antialias
import gtk
from module_frame import ModuleFrame

class TouchpadSetting(object):
    '''touchpad setting class'''
    def __init__(self, module_frame):
        self.settings = settings.TOUCHPAD_SETTINGS
        self.settings1 = settings.MOUSE_SETTINGS
        self.module_frame = module_frame
        self.scale_set= {
            "motion-acceleration" : settings.touchpad_set_motion_acceleration,
            "motion-threshold"    : settings.touchpad_set_motion_threshold,
            "double-click"        : settings.touchpad_set_double_click,
            "drag-threshold"      : settings.touchpad_set_drag_threshold}
        self.scale_get= {
            "motion-acceleration" : settings.touchpad_get_motion_acceleration,
            "motion-threshold"    : settings.touchpad_get_motion_threshold,
            "double-click"        : settings.touchpad_get_double_click,
            "drag-threshold"      : settings.touchpad_get_drag_threshold}

        self.image_widgets = {}
        self.label_widgets = {}
        self.button_widgets = {}
        self.adjust_widgets = {}
        self.scale_widgets = {}
        self.alignment_widgets = {}
        self.container_widgets = {}

        self.__create_widget()
        self.__adjust_widget()
        self.__signals_connect()

    def __create_widget(self):
        '''create gtk widget'''
        title_item_font_size = 12
        option_item_font_szie = 9
        # image init
        self.image_widgets["custom"] = gtk.image_new_from_file(
            app_theme.get_theme_file_path("image/set/custom.png"))
        self.image_widgets["speed"] = gtk.image_new_from_file(
            app_theme.get_theme_file_path("image/set/pointer.png"))
        self.image_widgets["double"] = gtk.image_new_from_file(
            app_theme.get_theme_file_path("image/set/double-click.png"))
        self.image_widgets["drag"] = gtk.image_new_from_file(
            app_theme.get_theme_file_path("image/set/drag.png"))
        self.image_widgets["double_test"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/double-test.png"))
        # label init
        self.label_widgets["custom"] = Label(_("Custom"), text_size=title_item_font_size)
        self.label_widgets["pointer_speed"] = Label(_("Pointer speed"), text_size=title_item_font_size)
        self.label_widgets["acceleration"] = Label(_("Acceleration"),
            text_size=option_item_font_szie)
        self.label_widgets["accel_fast"] = Label(_("Fast"))
        self.label_widgets["accel_slow"] = Label(_("Slow"))
        self.label_widgets["sensitivity"] = Label(_("Sensitivity"),
            text_size=option_item_font_szie)
        self.label_widgets["sensitiv_low"] = Label(_("Low"))
        self.label_widgets["sensitiv_high"] = Label(_("High"))
        self.label_widgets["double_click"] = Label(_("Double-click"), text_size=title_item_font_size)
        self.label_widgets["click_rate"] = Label(_("Frequency"),
            text_size=option_item_font_szie)
        self.label_widgets["click_fast"] = Label(_("Fast"))
        self.label_widgets["click_slow"] = Label(_("Slow"))
        self.label_widgets["double_test"] = Label(_("Double-click on the folder to test your settings."), text_size=option_item_font_szie)
        self.label_widgets["drag_drop"] = Label(_("Drag and Drop"), text_size=title_item_font_size)
        self.label_widgets["drag_threshold"] = Label(_("Drag threshold"),
            text_size=option_item_font_szie)
        self.label_widgets["drag_time_short"] = Label(_("Short"))
        self.label_widgets["drag_time_long"] = Label(_("Long"))
        self.label_widgets["relevant"] = Label(_("Relevant input device Settings "), text_size=10)
        # button init
        self.button_widgets["right_hand_radio"] = RadioButton( _("Right-handed"))
        self.button_widgets["left_hand_radio"] = RadioButton(_("Left-handed"))
        self.button_widgets["double_test"] = gtk.EventBox()
        # relevant settings button
        self.button_widgets["keyboard_setting"] = Label("<u>%s</u>" % _("Keyboard Setting"),
            text_size=10, text_color=app_theme.get_color("link_text"), enable_select=False)
        self.button_widgets["mouse_setting"] = Label("<u>%s</u>" % _("Mouse Setting"),
            text_size=10, text_color=app_theme.get_color("link_text"), enable_select=False)
        # container init
        self.container_widgets["main_hbox"] = gtk.HBox(False)
        self.container_widgets["left_vbox"] = gtk.VBox(False)
        self.container_widgets["right_vbox"] = gtk.VBox(False)
        self.container_widgets["custom_main_vbox"] = gtk.VBox(False)            # custom
        self.container_widgets["custom_label_hbox"] = gtk.HBox(False)
        self.container_widgets["custom_button_hbox"] = gtk.HBox(False)
        self.container_widgets["pointer_speed_main_vbox"] = gtk.VBox(False)     # pointer speed
        self.container_widgets["pointer_speed_label_hbox"] = gtk.HBox(False)
        self.container_widgets["pointer_speed_table"] = gtk.Table(2, 4, False)
        self.container_widgets["pointer_speed_accel_hbox"] = gtk.HBox(False)
        self.container_widgets["pointer_speed_sensitiv_hbox"] = gtk.HBox(False)
        self.container_widgets["double_click_main_vbox"] = gtk.VBox(False)      # double click
        self.container_widgets["double_click_label_hbox"] = gtk.HBox(False)
        self.container_widgets["double_click_table"] = gtk.Table(2, 4, False)
        self.container_widgets["double_click_rate_hbox"] = gtk.HBox(False)
        self.container_widgets["drag_threshold_main_vbox"] = gtk.VBox(False)       # mouse wheel
        self.container_widgets["drag_threshold_label_hbox"] = gtk.HBox(False)
        self.container_widgets["drag_threshold_table"] = gtk.Table(1, 4, False)
        self.container_widgets["drag_threshold_time_hbox"] = gtk.HBox(False)
        # alignment init
        self.alignment_widgets["left"] = gtk.Alignment()
        self.alignment_widgets["right"] = gtk.Alignment()
        self.alignment_widgets["custom_label"] = gtk.Alignment()            # custom
        self.alignment_widgets["custom_button"] = gtk.Alignment()
        self.alignment_widgets["pointer_speed_label"] = gtk.Alignment()     # pointer speed
        self.alignment_widgets["pointer_speed_table"] = gtk.Alignment()
        self.alignment_widgets["double_click_label"] = gtk.Alignment()      # double click
        self.alignment_widgets["double_click_table"] = gtk.Alignment()
        self.alignment_widgets["drag_threshold_label"] = gtk.Alignment()       # mouse wheel
        self.alignment_widgets["drag_threshold_table"] = gtk.Alignment()
        self.alignment_widgets["keyboard_setting"] = gtk.Alignment()
        self.alignment_widgets["mouse_setting"] = gtk.Alignment()
        # adjust init
        self.adjust_widgets["pointer_speed_accel"] = gtk.Adjustment(0.0, 1.0, 10.0)
        self.adjust_widgets["pointer_speed_sensitiv"] = gtk.Adjustment(0, 1, 10)
        self.adjust_widgets["double_click_rate"] = gtk.Adjustment(0, 100, 1000)
        self.adjust_widgets["drag_threshold_time"] = gtk.Adjustment(0, 1, 10)
        # scale init
        #self.scale_widgets["pointer_speed_accel"] = gtk.HScale()
        #self.scale_widgets["pointer_speed_accel"].set_draw_value(False)
        self.scale_widgets["pointer_speed_accel"] = HScalebar(
            app_theme.get_pixbuf("scalebar/l_fg.png"),
            app_theme.get_pixbuf("scalebar/l_bg.png"),
            app_theme.get_pixbuf("scalebar/m_fg.png"),
            app_theme.get_pixbuf("scalebar/m_bg.png"),
            app_theme.get_pixbuf("scalebar/r_fg.png"),
            app_theme.get_pixbuf("scalebar/r_bg.png"),
            app_theme.get_pixbuf("scalebar/point.png"))
        self.scale_widgets["pointer_speed_accel"].set_adjustment( self.adjust_widgets["pointer_speed_accel"])
        #self.scale_widgets["pointer_speed_sensitiv"] = gtk.HScale()
        #self.scale_widgets["pointer_speed_sensitiv"].set_draw_value(False)
        self.scale_widgets["pointer_speed_sensitiv"] = HScalebar(
            app_theme.get_pixbuf("scalebar/l_fg.png"),
            app_theme.get_pixbuf("scalebar/l_bg.png"),
            app_theme.get_pixbuf("scalebar/m_fg.png"),
            app_theme.get_pixbuf("scalebar/m_bg.png"),
            app_theme.get_pixbuf("scalebar/r_fg.png"),
            app_theme.get_pixbuf("scalebar/r_bg.png"),
            app_theme.get_pixbuf("scalebar/point.png"))
        self.scale_widgets["pointer_speed_sensitiv"].set_adjustment( self.adjust_widgets["pointer_speed_sensitiv"])
        #self.scale_widgets["double_click_rate"] = gtk.HScale()
        #self.scale_widgets["double_click_rate"].set_draw_value(False)
        self.scale_widgets["double_click_rate"] = HScalebar(
            app_theme.get_pixbuf("scalebar/l_fg.png"),
            app_theme.get_pixbuf("scalebar/l_bg.png"),
            app_theme.get_pixbuf("scalebar/m_fg.png"),
            app_theme.get_pixbuf("scalebar/m_bg.png"),
            app_theme.get_pixbuf("scalebar/r_fg.png"),
            app_theme.get_pixbuf("scalebar/r_bg.png"),
            app_theme.get_pixbuf("scalebar/point.png"))
        self.scale_widgets["double_click_rate"].set_adjustment( self.adjust_widgets["double_click_rate"])
        #self.scale_widgets["drag_threshold_time"] = gtk.HScale()
        #self.scale_widgets["drag_threshold_time"].set_draw_value(False)
        self.scale_widgets["drag_threshold_time"] = HScalebar(
            app_theme.get_pixbuf("scalebar/l_fg.png"),
            app_theme.get_pixbuf("scalebar/l_bg.png"),
            app_theme.get_pixbuf("scalebar/m_fg.png"),
            app_theme.get_pixbuf("scalebar/m_bg.png"),
            app_theme.get_pixbuf("scalebar/r_fg.png"),
            app_theme.get_pixbuf("scalebar/r_bg.png"),
            app_theme.get_pixbuf("scalebar/point.png"))
        self.scale_widgets["drag_threshold_time"].set_adjustment( self.adjust_widgets["drag_threshold_time"])
     
    def __adjust_widget(self):
        ''' adjust widget '''
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["left"])
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["right"], False, False)
        self.alignment_widgets["left"].add(self.container_widgets["left_vbox"])
        self.alignment_widgets["right"].add(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].set_size_request(200, -1)
        # set left padding
        self.alignment_widgets["left"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["left"].set_padding(15, 0, 20, 0)
        # set right padding
        self.alignment_widgets["right"].set(0.0, 0.0, 0.0, 0.0)
        self.alignment_widgets["right"].set_padding(15, 0, 0, 0)
        
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["custom_main_vbox"], False, False)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["pointer_speed_main_vbox"], False, False, 10)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["double_click_main_vbox"], False, False, 10)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["drag_threshold_main_vbox"], False, False, 10)
        # set option label width
        label_widgets = self.label_widgets
        label_width = max(label_widgets["acceleration"].size_request()[0],
            label_widgets["sensitivity"].size_request()[0],
            label_widgets["click_rate"].size_request()[0],
            label_widgets["drag_threshold"].size_request()[0])
        label_widgets["acceleration"].set_size_request(label_width, -1)
        label_widgets["sensitivity"].set_size_request(label_width, -1)
        label_widgets["click_rate"].set_size_request(label_width, -1)
        label_widgets["drag_threshold"].set_size_request(label_width, -1)
        # set scale label width
        label_width = max(label_widgets["accel_fast"].size_request()[0],
            label_widgets["accel_slow"].size_request()[0],
            label_widgets["sensitiv_low"].size_request()[0],
            label_widgets["sensitiv_high"].size_request()[0],
            label_widgets["click_fast"].size_request()[0],
            label_widgets["click_slow"].size_request()[0],
            label_widgets["drag_time_short"].size_request()[0],
            label_widgets["drag_time_long"].size_request()[0])
        label_widgets["accel_slow"].set_size_request(label_width, -1)
        label_widgets["accel_fast"].set_size_request(label_width, -1)
        label_widgets["sensitiv_low"].set_size_request(label_width, -1)
        label_widgets["sensitiv_high"].set_size_request(label_width, -1)
        label_widgets["click_fast"].set_size_request(label_width, -1)
        label_widgets["click_slow"].set_size_request(label_width, -1)
        label_widgets["drag_time_short"].set_size_request(label_width, -1)
        label_widgets["drag_time_long"].set_size_request(label_width, -1)
        # custom
        self.alignment_widgets["custom_label"].add(self.container_widgets["custom_label_hbox"])
        self.alignment_widgets["custom_button"].add(self.container_widgets["custom_button_hbox"])
        # alignment set
        self.alignment_widgets["custom_label"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["custom_button"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["custom_label"].set_padding(0, 0, 5, 5)
        self.alignment_widgets["custom_button"].set_padding(0, 0, 0, 5)
        self.container_widgets["custom_main_vbox"].pack_start(
            self.alignment_widgets["custom_label"])
        self.container_widgets["custom_main_vbox"].pack_start(
            self.alignment_widgets["custom_button"], True, True, 10)
        # tips label
        self.container_widgets["custom_label_hbox"].pack_start(
            self.image_widgets["custom"], False, False)
        self.container_widgets["custom_label_hbox"].pack_start(
            self.label_widgets["custom"], False, False, 15)
        # radio button set
        is_left = settings.touchpad_get_left_handed()
        if is_left == "mouse":
            if settings.mouse_get_left_handed():
                self.button_widgets["left_hand_radio"].set_active(True)
            else:
                self.button_widgets["right_hand_radio"].set_active(True)
        else:
            self.button_widgets["%s_hand_radio" % is_left].set_active(True)
        self.container_widgets["custom_button_hbox"].pack_start(
            self.button_widgets["left_hand_radio"], False, False, 40)
        self.container_widgets["custom_button_hbox"].pack_start(
            self.button_widgets["right_hand_radio"], False, False, 60)

        # pointer speed
        self.alignment_widgets["pointer_speed_label"].add(self.container_widgets["pointer_speed_label_hbox"])
        self.alignment_widgets["pointer_speed_table"].add(self.container_widgets["pointer_speed_table"])
        # alignment set
        self.alignment_widgets["pointer_speed_label"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["pointer_speed_table"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["pointer_speed_label"].set_padding(0, 0, 5, 5)
        self.alignment_widgets["pointer_speed_table"].set_padding(0, 0, 35, 71)
        self.container_widgets["pointer_speed_main_vbox"].pack_start(
            self.alignment_widgets["pointer_speed_label"])
        self.container_widgets["pointer_speed_main_vbox"].pack_start(
            self.alignment_widgets["pointer_speed_table"], True, True, 10)
        # tips lable
        self.container_widgets["pointer_speed_label_hbox"].pack_start(
            self.image_widgets["speed"], False, False)
        self.container_widgets["pointer_speed_label_hbox"].pack_start(
            self.label_widgets["pointer_speed"], False, False, 15)
        # motion acceleration
        # set original value
        self.adjust_widgets["pointer_speed_accel"].set_value(settings.touchpad_get_motion_acceleration())
        self.container_widgets["pointer_speed_accel_hbox"].pack_start(
            self.label_widgets["accel_slow"], False, False)
        self.container_widgets["pointer_speed_accel_hbox"].pack_start(
            self.scale_widgets["pointer_speed_accel"], True, True, 2)
        self.container_widgets["pointer_speed_accel_hbox"].pack_start(
            self.label_widgets["accel_fast"], False, False)
        # table attach
        self.container_widgets["pointer_speed_table"].attach(
            self.label_widgets["acceleration"], 0, 1, 0, 1, 0, 0, 15, 10)
        self.container_widgets["pointer_speed_table"].attach(
            self.container_widgets["pointer_speed_accel_hbox"], 1, 3, 0, 1, 5, 0)
        # motion threshold
        # set original value
        self.adjust_widgets["pointer_speed_sensitiv"].set_value(settings.touchpad_get_motion_threshold())
        self.container_widgets["pointer_speed_sensitiv_hbox"].pack_start(
            self.label_widgets["sensitiv_low"], False, False)
        self.container_widgets["pointer_speed_sensitiv_hbox"].pack_start(
            self.scale_widgets["pointer_speed_sensitiv"], True, True, 2)
        self.container_widgets["pointer_speed_sensitiv_hbox"].pack_start(
            self.label_widgets["sensitiv_high"], False, False)
        # table attach
        self.container_widgets["pointer_speed_table"].attach(
            self.label_widgets["sensitivity"], 0, 1, 1, 2, 0, 0, 15, 10)
        self.container_widgets["pointer_speed_table"].attach(
            self.container_widgets["pointer_speed_sensitiv_hbox"], 1, 3, 1, 2, 5, 0)

        # double click
        self.alignment_widgets["double_click_label"].add(self.container_widgets["double_click_label_hbox"])
        self.alignment_widgets["double_click_table"].add(self.container_widgets["double_click_table"])
        self.alignment_widgets["double_click_label"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["double_click_table"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["double_click_label"].set_padding(0, 0, 5, 5)
        self.alignment_widgets["double_click_table"].set_padding(0, 0, 35, 5)
        self.container_widgets["double_click_main_vbox"].pack_start(
            self.alignment_widgets["double_click_label"])
        self.container_widgets["double_click_main_vbox"].pack_start(
            self.alignment_widgets["double_click_table"])
        # tips lable
        self.container_widgets["double_click_label_hbox"].pack_start(
            self.image_widgets["double"], False, False)
        self.container_widgets["double_click_label_hbox"].pack_start(
            self.label_widgets["double_click"], False, False, 15)
        # double click rate
        # set original value
        self.adjust_widgets["double_click_rate"].set_value(settings.touchpad_get_double_click())
        self.container_widgets["double_click_rate_hbox"].pack_start(
            self.label_widgets["click_slow"], False, False)
        self.container_widgets["double_click_rate_hbox"].pack_start(
            self.scale_widgets["double_click_rate"], True, True, 2)
        self.container_widgets["double_click_rate_hbox"].pack_start(
            self.label_widgets["click_fast"], False, False)
        # table attach
        self.container_widgets["double_click_table"].attach(
            self.label_widgets["click_rate"], 0, 1, 0, 1, 0, 0, 15, 5)
        self.container_widgets["double_click_table"].attach(
            self.container_widgets["double_click_rate_hbox"], 1, 3, 0, 1, 5, 0)
        self.container_widgets["double_click_table"].attach(
            self.label_widgets["double_test"], 1, 3, 1, 2, 5, 0, 0, 5)
        self.container_widgets["double_click_table"].attach(
            self.button_widgets["double_test"], 3, 4, 0, 2, 0, 0, 0)
        self.button_widgets["double_test"].set_size_request(66, 66)

        # drag threshold
        self.alignment_widgets["drag_threshold_label"].add(self.container_widgets["drag_threshold_label_hbox"])
        self.alignment_widgets["drag_threshold_table"].add(self.container_widgets["drag_threshold_table"])
        self.alignment_widgets["drag_threshold_label"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["drag_threshold_table"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["drag_threshold_label"].set_padding(0, 0, 5, 5)
        self.alignment_widgets["drag_threshold_table"].set_padding(0, 0, 35, 71)
        self.container_widgets["drag_threshold_main_vbox"].pack_start(
            self.alignment_widgets["drag_threshold_label"])
        self.container_widgets["drag_threshold_main_vbox"].pack_start(
            self.alignment_widgets["drag_threshold_table"])
        # tips lable
        self.container_widgets["drag_threshold_label_hbox"].pack_start(
            self.image_widgets["drag"], False, False)
        self.container_widgets["drag_threshold_label_hbox"].pack_start(
            self.label_widgets["drag_drop"], False, False, 15)
        # drag threshold time
        # set original value
        self.adjust_widgets["drag_threshold_time"].set_value(settings.touchpad_get_drag_threshold())
        self.container_widgets["drag_threshold_time_hbox"].pack_start(
            self.label_widgets["drag_time_short"], False, False)
        self.container_widgets["drag_threshold_time_hbox"].pack_start(
            self.scale_widgets["drag_threshold_time"], True, True, 2)
        self.container_widgets["drag_threshold_time_hbox"].pack_start(
            self.label_widgets["drag_time_long"], False, False)
        # table attach
        self.container_widgets["drag_threshold_table"].attach(
            self.label_widgets["drag_threshold"], 0, 1, 0, 1, 0, 0, 15, 10)
        self.container_widgets["drag_threshold_table"].attach(
            self.container_widgets["drag_threshold_time_hbox"], 1, 3, 0, 1, 5, 0)
        
        # relevant setting
        self.container_widgets["right_vbox"].pack_start(
            self.label_widgets["relevant"])
        self.container_widgets["right_vbox"].pack_start(
            self.alignment_widgets["keyboard_setting"])
        self.container_widgets["right_vbox"].pack_start(
            self.alignment_widgets["mouse_setting"])
        self.alignment_widgets["keyboard_setting"].add(self.button_widgets["keyboard_setting"])
        self.alignment_widgets["mouse_setting"].add(self.button_widgets["mouse_setting"])
        self.alignment_widgets["keyboard_setting"].set_padding(15, 0, 9, 0)
        self.alignment_widgets["mouse_setting"].set_padding(10, 0, 9, 0)

    def __signals_connect(self):
        ''' widget signals connect'''
        # window signals
        self.button_widgets["right_hand_radio"].connect("toggled", self.left_or_right_set, "right")
        self.button_widgets["left_hand_radio"].connect("toggled", self.left_or_right_set, "left")
        self.settings.connect("changed", self.touchpad_setting_changed_cb)
        self.settings1.connect("changed", self.mouse_setting_changed_cb)
        # acceleration operation
        self.scale_widgets["pointer_speed_accel"].connect(
            "button-release-event", self.adjustment_value_changed, "motion-acceleration")
        # sensitivity operation
        self.scale_widgets["pointer_speed_sensitiv"].connect(
            "button-release-event", self.adjustment_value_changed, "motion-threshold")
        # double-click operation
        self.scale_widgets["double_click_rate"].connect(
            "button-release-event", self.adjustment_value_changed, "double-click")
        
        self.button_widgets["double_test"].connect("button-press-event", self.double_click_test)
        self.button_widgets["double_test"].connect("expose-event", self.double_click_test_expose)
        self.scale_widgets["drag_threshold_time"].connect(
            "button-release-event", self.adjustment_value_changed, "drag-threshold")
        
        # relevant setting
        self.button_widgets["keyboard_setting"].connect("button-press-event", self.relevant_press, "keyboard")
        self.button_widgets["mouse_setting"].connect("button-press-event", self.relevant_press, "mouse")
    
    def touchpad_setting_changed_cb(self, key):
        args = [key]
        if key == "left-handed":
            callback = self.left_or_right_setting_changed
        elif key == "motion-acceleration":
            callback = self.settings_value_changed
            args.append(self.adjust_widgets["pointer_speed_accel"])
        elif key == "motion-threshold":
            callback = self.settings_value_changed
            args.append(self.adjust_widgets["pointer_speed_sensitiv"])
        else:
            return
        callback(*args)
    
    def mouse_setting_changed_cb(self, key):
        args = [key]
        if key == "double-click":
            callback = self.settings_value_changed
            args.append(self.adjust_widgets["double_click_rate"])
        elif key == "drag-threshold":
            callback = self.settings_value_changed
            args.append(self.adjust_widgets["drag_threshold_time"])
        else:
            return
        callback(*args)
    
    def left_or_right_set(self, button, active):
        ''' set left-handed '''
        if button.get_data("changed-by-other-app"):
            button.set_data("changed-by-other-app", False)
            return
        if button.get_active():
            settings.touchpad_set_left_handed(active)
    
    def left_or_right_setting_changed(self, *args):
        ''' set left or right radio button active '''
        is_left = settings.touchpad_get_left_handed()
        if is_left == "mouse":
            if settings.mouse_get_left_handed():
                self.button_widgets["left_hand_radio"].set_active(True)
                self.button_widgets["left_hand_radio"].set_data("changed-by-other-app", True)
            else:
                self.button_widgets["right_hand_radio"].set_active(True)
                self.button_widgets["right_hand_radio"].set_data("changed-by-other-app", True)
        else:
            self.button_widgets["%s_hand_radio" % is_left].set_active(True)
            self.button_widgets["%s_hand_radio" % is_left].set_data("changed-by-other-app", True)
    
    def adjustment_value_changed(self, widget, event, key):
        '''adjustment value changed, and settings set the value'''
        adjustment = widget.get_adjustment()
        value = adjustment.get_value()
        if key == "motion-threshold" or key == "drag-threshold":   # motion-threshold or drag-threshold is an int type
            new_value = value
            old_value = self.scale_get[key]()
            if abs(new_value - old_value) < 0.9:
                return
            if new_value > old_value:
                value = int(new_value + 0.2)
            else:
                value = int(new_value)
        self.scale_set[key](value)
    
    def settings_value_changed(self, key, adjustment):
        '''settings value changed, and adjustment set the value'''
        adjustment.set_value(self.scale_get[key]())

    def double_click_test(self, widget, event):
        '''double clicked callback, to test the double-click time'''
        if event.type == gtk.gdk._2BUTTON_PRESS:
            print "double-clicked:" 
            print "-"*20
    
    def double_click_test_expose(self, widget, event):
        '''double_test button expsoe'''
        cr = widget.window.cairo_create()
        cr.set_source_pixbuf(self.image_widgets["double_test"], 0, 0)
        cr.paint()
        propagate_expose(widget, event)
        return True
    
    # TODO 相关设置按钮
    def relevant_press(self, widget, event, action):
        '''relevant button pressed'''
        if action == 'keyboard':
            print "goto keyboard"
        elif action == 'mouse':
            print "goto mouse"

    def set_to_default(self):
        '''set to the default'''
        settings.mouse_set_to_default()
    
if __name__ == '__main__':
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    mouse_settings = TouchpadSetting(module_frame)
    
    module_frame.add(mouse_settings.container_widgets["main_hbox"])
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            module_frame.send_module_info()

    module_frame.module_message_handler = message_handler        
    
    module_frame.run()
