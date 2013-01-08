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

import sys
import os
from deepin_utils.file import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from theme import app_theme

import settings

from nls import _
from dtk.ui.theme import ui_theme
from dtk.ui.label import Label
from dtk.ui.button import RadioButton
from dtk.ui.hscalebar import HScalebar
from dtk.ui.line import HSeparator
from dtk.ui.box import ImageBox
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.utils import propagate_expose, color_hex_to_cairo, set_clickable_cursor
import gtk
from module_frame import ModuleFrame
from constant import *

MODULE_NAME = "touchpad"

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
        title_item_font_size = TITLE_FONT_SIZE
        option_item_font_szie = CONTENT_FONT_SIZE
        # image init
        self.image_widgets["custom"] = ImageBox(app_theme.get_pixbuf("%s/pad_l.png" % MODULE_NAME))
        self.image_widgets["speed"] = ImageBox(app_theme.get_pixbuf("%s/pointer.png" % MODULE_NAME))
        self.image_widgets["double"] = ImageBox(app_theme.get_pixbuf("%s/double-click.png" % MODULE_NAME))
        self.image_widgets["drag"] = ImageBox(app_theme.get_pixbuf("%s/drag.png" % MODULE_NAME))
        self.image_widgets["double_test_1"] = app_theme.get_pixbuf("%s/smiley00.png" % MODULE_NAME)
        self.image_widgets["double_test_2"] = app_theme.get_pixbuf("%s/smiley01.png" % MODULE_NAME)
        # label init
        self.label_widgets["custom"] = Label(_("Custom"), text_size=title_item_font_size)
        self.label_widgets["pointer_speed"] = Label(_("Pointer speed"), text_size=title_item_font_size)
        self.label_widgets["acceleration"] = Label(_("Acceleration"),
            text_size=option_item_font_szie)
        self.label_widgets["sensitivity"] = Label(_("Sensitivity"),
            text_size=option_item_font_szie)
        self.label_widgets["double_click"] = Label(_("Double-click"), text_size=title_item_font_size)
        self.label_widgets["click_rate"] = Label(_("Frequency"),
            text_size=option_item_font_szie)
        self.label_widgets["double_test"] = Label(_("Double-click on the folder to test your settings."),
            label_width=HSCALEBAR_WIDTH, wrap_width=HSCALEBAR_WIDTH, enable_select=False)
        self.label_widgets["drag_drop"] = Label(_("Drag and Drop"), text_size=title_item_font_size)
        self.label_widgets["drag_threshold"] = Label(_("Drag threshold"),
            text_size=option_item_font_szie)
        self.label_widgets["relevant"] = Label(_("Relevant Settings"), text_size=title_item_font_size)
        # button init
        self.button_widgets["right_hand_radio"] = RadioButton( _("Right-handed"), padding_x=0)
        self.button_widgets["left_hand_radio"] = RadioButton(_("Left-handed"), padding_x=0)
        self.button_widgets["double_test"] = gtk.EventBox()
        # relevant settings button
        self.button_widgets["keyboard_setting"] = Label("<u>%s</u>" % _("Keyboard Setting"),
            text_size=option_item_font_szie, text_color=ui_theme.get_color("link_text"), enable_select=False)
        self.button_widgets["mouse_setting"] = Label("<u>%s</u>" % _("Mouse Setting"),
            text_size=option_item_font_szie, text_color=ui_theme.get_color("link_text"), enable_select=False)
        # container init
        self.container_widgets["main_swindow"] = ScrolledWindow()
        self.container_widgets["main_hbox"] = gtk.HBox(False)
        self.container_widgets["left_vbox"] = gtk.VBox(False)
        self.container_widgets["right_vbox"] = gtk.VBox(False)
        self.container_widgets["custom_main_vbox"] = gtk.VBox(False)            # custom
        self.container_widgets["custom_label_hbox"] = gtk.HBox(False)
        self.container_widgets["custom_button_hbox"] = gtk.HBox(False)
        self.container_widgets["pointer_speed_main_vbox"] = gtk.VBox(False)     # pointer speed
        self.container_widgets["pointer_speed_label_hbox"] = gtk.HBox(False)
        self.container_widgets["pointer_speed_table"] = gtk.Table(2, 4, False)
        self.container_widgets["double_click_main_vbox"] = gtk.VBox(False)      # double click
        self.container_widgets["double_click_label_hbox"] = gtk.HBox(False)
        self.container_widgets["double_click_table"] = gtk.Table(2, 4, False)
        self.container_widgets["drag_threshold_main_vbox"] = gtk.VBox(False)       # mouse wheel
        self.container_widgets["drag_threshold_label_hbox"] = gtk.HBox(False)
        self.container_widgets["drag_threshold_table"] = gtk.Table(1, 4, False)
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
        self.adjust_widgets["pointer_speed_accel"] = gtk.Adjustment(1.0, 1.0, 10.0, 1, 2)
        self.adjust_widgets["pointer_speed_sensitiv"] = gtk.Adjustment(1, 1, 10, 1, 2)
        self.adjust_widgets["double_click_rate"] = gtk.Adjustment(100, 100, 1000, 100, 200)
        self.adjust_widgets["drag_threshold_time"] = gtk.Adjustment(1, 1, 10, 1, 2)
        # scale init
        self.scale_widgets["pointer_speed_accel"] = HScalebar(value_min=1.0, value_max=10.0)
        self.scale_widgets["pointer_speed_sensitiv"] = HScalebar(value_min=1, value_max=10)
        self.scale_widgets["double_click_rate"] = HScalebar(value_min=100, value_max=1000)
        self.scale_widgets["drag_threshold_time"] = HScalebar(value_min=1, value_max=10)
     
    def __adjust_widget(self):
        ''' adjust widget '''
        MID_SPACING = 10
        RIGHT_BOX_WIDTH = TIP_BOX_WIDTH - 20
        MAIN_AREA_WIDTH = 480
        LABEL_WIDTH = 180
        OPTION_LEFT_PADDING = WIDGET_SPACING + 16
        TABLE_ROW_SPACING = 15
        self.container_widgets["main_swindow"].add_child(self.container_widgets["main_hbox"])
        self.container_widgets["main_hbox"].set_spacing(MID_SPACING)
        self.container_widgets["main_hbox"].set_size_request(WINDOW_WIDTH-20, -1)
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["left"])
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["right"], False, False)
        self.alignment_widgets["left"].add(self.container_widgets["left_vbox"])
        self.alignment_widgets["right"].add(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].set_size_request(RIGHT_BOX_WIDTH, -1)
        # set left padding
        self.alignment_widgets["left"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["left"].set_padding(
            TEXT_WINDOW_TOP_PADDING, 15, TEXT_WINDOW_LEFT_PADDING, TEXT_WINDOW_RIGHT_WIDGET_PADDING)
        # set right padding
        self.alignment_widgets["right"].set(0.0, 0.0, 1.0, 0.0)
        self.alignment_widgets["right"].set_padding(TEXT_WINDOW_TOP_PADDING, 0, 0, 60)
        
        self.container_widgets["left_vbox"].set_spacing(BETWEEN_SPACING)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["custom_main_vbox"], False, False)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["pointer_speed_main_vbox"], False, False)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["double_click_main_vbox"], False, False)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["drag_threshold_main_vbox"], False, False)
        # set option label width
        label_widgets = self.label_widgets
        label_width = max(label_widgets["acceleration"].size_request()[0],
                          label_widgets["sensitivity"].size_request()[0],
                          label_widgets["click_rate"].size_request()[0],
                          label_widgets["drag_threshold"].size_request()[0]) + 2
        #label_widgets["acceleration"].set_size_request(label_width, WIDGET_HEIGHT)
        #label_widgets["sensitivity"].set_size_request(label_width, WIDGET_HEIGHT)
        #label_widgets["click_rate"].set_size_request(label_width, WIDGET_HEIGHT)
        #label_widgets["drag_threshold"].set_size_request(label_width, WIDGET_HEIGHT)
        # custom
        self.alignment_widgets["custom_label"].add(self.container_widgets["custom_label_hbox"])
        self.alignment_widgets["custom_button"].add(self.container_widgets["custom_button_hbox"])
        # alignment set
        self.alignment_widgets["custom_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["custom_button"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["custom_button"].set_padding(0, 0, OPTION_LEFT_PADDING, 0)
        self.alignment_widgets["custom_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["custom_button"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.container_widgets["custom_main_vbox"].pack_start(
            self.alignment_widgets["custom_label"])
        self.container_widgets["custom_main_vbox"].pack_start(
            self.__setup_separator())
        self.container_widgets["custom_main_vbox"].pack_start(
            self.alignment_widgets["custom_button"])
        # tips label
        self.container_widgets["custom_label_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["custom_label_hbox"].pack_start(
            self.image_widgets["custom"], False, False)
        self.container_widgets["custom_label_hbox"].pack_start(
            self.label_widgets["custom"], False, False)
        # radio button set
        is_left = settings.touchpad_get_left_handed()
        if is_left == "mouse":
            if settings.mouse_get_left_handed():
                self.button_widgets["left_hand_radio"].set_active(True)
                self.image_widgets["custom"].image_dpixbuf = app_theme.get_pixbuf("%s/pad_r.png" % MODULE_NAME)
            else:
                self.button_widgets["right_hand_radio"].set_active(True)
                self.image_widgets["custom"].image_dpixbuf = app_theme.get_pixbuf("%s/pad_l.png" % MODULE_NAME)
        else:
            if is_left == "left":
                self.image_widgets["custom"].image_dpixbuf = app_theme.get_pixbuf("%s/pad_r.png" % MODULE_NAME)
            else:
                self.image_widgets["custom"].image_dpixbuf = app_theme.get_pixbuf("%s/pad_l.png" % MODULE_NAME)
            self.button_widgets["%s_hand_radio" % is_left].set_active(True)
        self.container_widgets["custom_button_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["custom_button_hbox0"] = gtk.HBox(False)
        self.container_widgets["custom_button_hbox0"].set_spacing(WIDGET_SPACING)
        self.container_widgets["custom_button_hbox0"].pack_start(
            self.button_widgets["right_hand_radio"], False, False)
        self.container_widgets["custom_button_hbox0"].pack_start(
            self.button_widgets["left_hand_radio"], False, False)
        button_align = self.__make_align(self.container_widgets["custom_button_hbox0"], xalign=1.0)
        button_align.set_size_request(HSCALEBAR_WIDTH+WIDGET_SPACING+label_width, CONTAINNER_HEIGHT)
        self.container_widgets["custom_button_hbox"].pack_start(button_align, False, False)
        self.container_widgets["custom_button_hbox"].pack_start(self.__make_align())

        # pointer speed
        self.alignment_widgets["pointer_speed_label"].add(self.container_widgets["pointer_speed_label_hbox"])
        self.alignment_widgets["pointer_speed_table"].add(self.container_widgets["pointer_speed_table"])
        # alignment set
        self.alignment_widgets["pointer_speed_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["pointer_speed_table"].set(0.0, 0.5, 1.0, 1.0)
        self.alignment_widgets["pointer_speed_table"].set_padding(0, 0, OPTION_LEFT_PADDING, 0)
        self.alignment_widgets["pointer_speed_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.container_widgets["pointer_speed_main_vbox"].pack_start(
            self.alignment_widgets["pointer_speed_label"])
        self.container_widgets["pointer_speed_main_vbox"].pack_start(
            self.__setup_separator())
        self.container_widgets["pointer_speed_main_vbox"].pack_start(
            self.alignment_widgets["pointer_speed_table"])
        # tips lable
        self.container_widgets["pointer_speed_label_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["pointer_speed_label_hbox"].pack_start(
            self.image_widgets["speed"], False, False)
        self.container_widgets["pointer_speed_label_hbox"].pack_start(
            self.label_widgets["pointer_speed"], False, False)
        # motion acceleration
        # set original value
        self.scale_widgets["pointer_speed_accel"].set_value(settings.touchpad_get_motion_acceleration() - self.scale_widgets["pointer_speed_accel"].value_min)
        self.scale_widgets["pointer_speed_accel"].add_mark(self.adjust_widgets["pointer_speed_accel"].get_lower(), gtk.POS_BOTTOM, _("Slow"))
        self.scale_widgets["pointer_speed_accel"].add_mark(self.adjust_widgets["pointer_speed_accel"].get_upper(), gtk.POS_BOTTOM, _("Fast"))
        self.scale_widgets["pointer_speed_accel"].set_size_request(HSCALEBAR_WIDTH, -1)
        # table attach
        self.container_widgets["pointer_speed_table"].set_size_request(MAIN_AREA_WIDTH, -1)
        self.container_widgets["pointer_speed_table"].set_col_spacings(WIDGET_SPACING)
        #self.container_widgets["pointer_speed_table"].set_row_spacing(0, TABLE_ROW_SPACING)
        acceleration_align = self.__make_align(self.label_widgets["acceleration"], xalign=1.0)
        acceleration_align.set_size_request(label_width, CONTAINNER_HEIGHT)
        self.container_widgets["pointer_speed_table"].attach(
            acceleration_align, 0, 1, 0, 1, 4)
        self.container_widgets["pointer_speed_table"].attach(
            self.__make_align(self.scale_widgets["pointer_speed_accel"], yalign=0.0, yscale=1.0, padding_top=1, height=43), 1, 3, 0, 1, 4)
        # motion threshold
        # set original value
        self.scale_widgets["pointer_speed_sensitiv"].set_value(settings.touchpad_get_motion_threshold() - self.scale_widgets["pointer_speed_sensitiv"].value_min)
        self.scale_widgets["pointer_speed_sensitiv"].add_mark(self.adjust_widgets["pointer_speed_sensitiv"].get_lower(), gtk.POS_BOTTOM, _("Low"))
        self.scale_widgets["pointer_speed_sensitiv"].add_mark(self.adjust_widgets["pointer_speed_sensitiv"].get_upper(), gtk.POS_BOTTOM, _("High"))
        self.scale_widgets["pointer_speed_sensitiv"].set_size_request(HSCALEBAR_WIDTH, -1)
        # table attach
        sensitivity_align = self.__make_align(self.label_widgets["sensitivity"], xalign=1.0)
        sensitivity_align.set_size_request(label_width, CONTAINNER_HEIGHT)
        self.container_widgets["pointer_speed_table"].attach(
            sensitivity_align, 0, 1, 1, 2, 4)
        self.container_widgets["pointer_speed_table"].attach(
            self.__make_align(self.scale_widgets["pointer_speed_sensitiv"], yalign=0.0, yscale=1.0, padding_top=1, height=43), 1, 3, 1, 2, 4)

        # double click
        self.alignment_widgets["double_click_label"].add(self.container_widgets["double_click_label_hbox"])
        self.alignment_widgets["double_click_table"].add(self.container_widgets["double_click_table"])
        self.alignment_widgets["double_click_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["double_click_table"].set(0.0, 0.5, 1.0, 1.0)
        self.alignment_widgets["double_click_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["double_click_table"].set_padding(0, 0, OPTION_LEFT_PADDING, 0)
        self.container_widgets["double_click_main_vbox"].pack_start(
            self.alignment_widgets["double_click_label"])
        self.container_widgets["double_click_main_vbox"].pack_start(
            self.__setup_separator())
        self.container_widgets["double_click_main_vbox"].pack_start(
            self.alignment_widgets["double_click_table"])
        # tips lable
        self.container_widgets["double_click_label_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["double_click_label_hbox"].pack_start(
            self.image_widgets["double"], False, False)
        self.container_widgets["double_click_label_hbox"].pack_start(
            self.label_widgets["double_click"], False, False)
        # double click rate
        # set original value
        self.scale_widgets["double_click_rate"].set_value(settings.touchpad_get_double_click() - self.scale_widgets["double_click_rate"].value_min)
        self.scale_widgets["double_click_rate"].add_mark(self.adjust_widgets["double_click_rate"].get_lower(), gtk.POS_BOTTOM, _("Slow"))
        self.scale_widgets["double_click_rate"].add_mark(self.adjust_widgets["double_click_rate"].get_upper(), gtk.POS_BOTTOM, _("Fast"))
        self.scale_widgets["double_click_rate"].set_size_request(HSCALEBAR_WIDTH, -1)
        # table attach
        self.container_widgets["double_click_table"].set_size_request(MAIN_AREA_WIDTH, -1)
        self.container_widgets["double_click_table"].set_col_spacings(WIDGET_SPACING)
        click_rate_align = self.__make_align(self.label_widgets["click_rate"], xalign=1.0)
        click_rate_align.set_size_request(label_width, CONTAINNER_HEIGHT)
        self.container_widgets["double_click_table"].attach(
            click_rate_align, 0, 1, 0, 1, 4)
        self.container_widgets["double_click_table"].attach(
            self.__make_align(self.scale_widgets["double_click_rate"], yalign=0.0, yscale=1.0, padding_top=1, height=43), 1, 3, 0, 1, 4)
        self.container_widgets["double_click_table"].attach(
            self.__make_align(self.label_widgets["double_test"]), 1, 3, 1, 2, 4)
        self.container_widgets["double_click_table"].attach(
            self.__make_align(self.button_widgets["double_test"], height=-1), 3, 4, 0, 2, 0, 0, 0)
        self.button_widgets["double_test"].set_size_request(
            self.image_widgets["double_test_1"].get_pixbuf().get_width(),
            self.image_widgets["double_test_1"].get_pixbuf().get_height())

        # drag threshold
        self.alignment_widgets["drag_threshold_label"].add(self.container_widgets["drag_threshold_label_hbox"])
        self.alignment_widgets["drag_threshold_table"].add(self.container_widgets["drag_threshold_table"])
        self.alignment_widgets["drag_threshold_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["drag_threshold_table"].set(0.0, 0.5, 1.0, 1.0)
        self.alignment_widgets["drag_threshold_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["drag_threshold_table"].set_padding(0, 0, OPTION_LEFT_PADDING, 0)
        self.container_widgets["drag_threshold_main_vbox"].pack_start(
            self.alignment_widgets["drag_threshold_label"])
        self.container_widgets["drag_threshold_main_vbox"].pack_start(
            self.__setup_separator())
        self.container_widgets["drag_threshold_main_vbox"].pack_start(
            self.alignment_widgets["drag_threshold_table"])
        # tips lable
        self.container_widgets["drag_threshold_label_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["drag_threshold_label_hbox"].pack_start(
            self.image_widgets["drag"], False, False)
        self.container_widgets["drag_threshold_label_hbox"].pack_start(
            self.label_widgets["drag_drop"], False, False)
        # drag threshold time
        # set original value
        self.scale_widgets["drag_threshold_time"].set_value(settings.touchpad_get_drag_threshold() - self.scale_widgets["drag_threshold_time"].value_min)
        self.scale_widgets["drag_threshold_time"].add_mark(self.adjust_widgets["drag_threshold_time"].get_lower(), gtk.POS_BOTTOM, _("Short"))
        self.scale_widgets["drag_threshold_time"].add_mark(self.adjust_widgets["drag_threshold_time"].get_upper(), gtk.POS_BOTTOM, _("Long"))
        self.scale_widgets["drag_threshold_time"].set_size_request(HSCALEBAR_WIDTH, -1)
        # table attach
        self.container_widgets["drag_threshold_table"].set_size_request(MAIN_AREA_WIDTH, -1)
        self.container_widgets["drag_threshold_table"].set_col_spacings(WIDGET_SPACING)
        drag_threshold_align = self.__make_align(self.label_widgets["drag_threshold"], xalign=1.0)
        self.container_widgets["drag_threshold_table"].attach(
            drag_threshold_align, 0, 1, 0, 1, 4)
        self.container_widgets["drag_threshold_table"].attach(
            self.__make_align(self.scale_widgets["drag_threshold_time"], yalign=0.0, yscale=1.0, padding_top=1, height=43), 1, 3, 0, 1, 4)
        
        # relevant setting
        self.container_widgets["right_vbox"].pack_start(
            self.__make_align(self.label_widgets["relevant"]), False, False)
        self.container_widgets["right_vbox"].pack_start(
            self.alignment_widgets["keyboard_setting"], False, False)
        self.container_widgets["right_vbox"].pack_start(
            self.alignment_widgets["mouse_setting"], False, False)
        self.alignment_widgets["keyboard_setting"].add(self.button_widgets["keyboard_setting"])
        self.alignment_widgets["mouse_setting"].add(self.button_widgets["mouse_setting"])
        self.alignment_widgets["keyboard_setting"].set(0.0, 0.5, 0.0, 0.0)
        self.alignment_widgets["mouse_setting"].set(0.0, 0.5, 0.0, 0.0)
        self.alignment_widgets["keyboard_setting"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["mouse_setting"].set_size_request(-1, CONTAINNER_HEIGHT)

    def __signals_connect(self):
        ''' widget signals connect'''
        self.container_widgets["main_hbox"].connect("expose-event", self.container_expose_cb)
        # window signals
        self.button_widgets["right_hand_radio"].connect("toggled", self.left_or_right_set, "right")
        self.button_widgets["left_hand_radio"].connect("toggled", self.left_or_right_set, "left")
        self.settings.connect("changed", self.touchpad_setting_changed_cb)
        self.settings1.connect("changed", self.mouse_setting_changed_cb)
        # acceleration operation
        self.scale_widgets["pointer_speed_accel"].connect(
            "button-release-event", self.scalebar_value_changed, "motion-acceleration")
        # sensitivity operation
        self.scale_widgets["pointer_speed_sensitiv"].connect(
            "button-release-event", self.scalebar_value_changed, "motion-threshold")
        # double-click operation
        self.scale_widgets["double_click_rate"].connect(
            "button-release-event", self.scalebar_value_changed, "double-click")
        
        self.button_widgets["double_test"].connect("button-press-event", self.double_click_test)
        self.button_widgets["double_test"].connect("expose-event", self.double_click_test_expose)
        self.scale_widgets["drag_threshold_time"].connect(
            "button-release-event", self.scalebar_value_changed, "drag-threshold")
        
        # relevant setting
        self.button_widgets["keyboard_setting"].connect("button-press-event", self.relevant_press, "keyboard")
        self.button_widgets["mouse_setting"].connect("button-press-event", self.relevant_press, "mouse")
        set_clickable_cursor(self.button_widgets["keyboard_setting"])
        set_clickable_cursor(self.button_widgets["mouse_setting"])
    
    ############################
    def container_expose_cb(self, widget, event):
        cr = widget.window.cairo_create()
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                                               
        cr.rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)                                                 
        cr.fill()
    
    def touchpad_setting_changed_cb(self, key):
        args = [key]
        if key == "left-handed":
            callback = self.left_or_right_setting_changed
        elif key == "motion-acceleration":
            callback = self.settings_value_changed
            #args.append(self.adjust_widgets["pointer_speed_accel"])
            args.append(self.scale_widgets["pointer_speed_accel"])
        elif key == "motion-threshold":
            callback = self.settings_value_changed
            #args.append(self.adjust_widgets["pointer_speed_sensitiv"])
            args.append(self.scale_widgets["pointer_speed_sensitiv"])
        else:
            return
        callback(*args)
    
    def mouse_setting_changed_cb(self, key):
        args = [key]
        if key == "double-click":
            callback = self.settings_value_changed
            #args.append(self.adjust_widgets["double_click_rate"])
            args.append(self.scale_widgets["double_click_rate"])
        elif key == "drag-threshold":
            callback = self.settings_value_changed
            #args.append(self.adjust_widgets["drag_threshold_time"])
            args.append(self.scale_widgets["drag_threshold_time"])
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
                self.image_widgets["custom"].image_dpixbuf = app_theme.get_pixbuf("%s/pad_r.png" % MODULE_NAME)
            else:
                self.button_widgets["right_hand_radio"].set_active(True)
                self.button_widgets["right_hand_radio"].set_data("changed-by-other-app", True)
                self.image_widgets["custom"].image_dpixbuf = app_theme.get_pixbuf("%s/pad_l.png" % MODULE_NAME)
        else:
            if is_left == "left":
                self.image_widgets["custom"].image_dpixbuf = app_theme.get_pixbuf("%s/pad_r.png" % MODULE_NAME)
            else:
                self.image_widgets["custom"].image_dpixbuf = app_theme.get_pixbuf("%s/pad_l.png" % MODULE_NAME)
            self.button_widgets["%s_hand_radio" % is_left].set_active(True)
            self.button_widgets["%s_hand_radio" % is_left].set_data("changed-by-other-app", True)
        self.image_widgets["custom"].queue_draw()
    
    def scalebar_value_changed(self, widget, event, key):
        '''adjustment value changed, and settings set the value'''
        value = widget.value + widget.value_min
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
        adjustment.set_value(self.scale_get[key]()-adjustment.value_min)
        adjustment.set_data("changed-by-other-app", True)

    def double_click_test(self, widget, event):
        '''double clicked callback, to test the double-click time'''
        if event.type == gtk.gdk._2BUTTON_PRESS:
            widget.set_data("has_double_clicked", not widget.get_data("has_double_clicked"))
            widget.queue_draw()
    
    def double_click_test_expose(self, widget, event):
        '''double_test button expsoe'''
        cr = widget.window.cairo_create()
        cr = widget.window.cairo_create()
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                                               
        cr.rectangle(*widget.allocation)                                                 
        cr.paint()
        if widget.get_data("has_double_clicked"):
            cr.set_source_pixbuf(self.image_widgets["double_test_2"].get_pixbuf(), 0, 0)
        else:
            cr.set_source_pixbuf(self.image_widgets["double_test_1"].get_pixbuf(), 0, 0)
        cr.paint()
        propagate_expose(widget, event)
        return True
    
    def relevant_press(self, widget, event, action):
        '''relevant button pressed'''
        self.module_frame.send_message("goto", (action, ""))
    
    def __make_align(self, widget=None, xalign=0.0, yalign=0.5, xscale=0.0,
                     yscale=0.0, padding_top=0, padding_bottom=0, padding_left=0,
                     padding_right=0, height=CONTAINNER_HEIGHT):
        align = gtk.Alignment()
        align.set_size_request(-1, height)
        align.set(xalign, yalign, xscale, yscale)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        if widget:
            align.add(widget)
        return align

    def __make_separator(self):
        hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        hseparator.set_size_request(350, 10)
        return hseparator
    
    def __setup_separator(self):
        return self.__make_align(self.__make_separator(), xalign=0.0, xscale=0.0, height=10)

    def set_to_default(self):
        '''set to the default'''
        settings.touchpad_set_to_default()
    
if __name__ == '__main__':
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    mouse_settings = TouchpadSetting(module_frame)
    
    module_frame.add(mouse_settings.container_widgets["main_swindow"])
    
    if len(sys.argv) > 1:
        print "module_uid:", sys.argv[1]
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            print "DEBUG show_again module_uid", message_content
            module_frame.send_module_info()
        if message_type == "reset":
            mouse_settings.set_to_default()

    module_frame.module_message_handler = message_handler        
    
    module_frame.run()
