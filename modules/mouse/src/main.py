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

import sys
import os
from deepin_utils.file import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from theme import app_theme

import settings

from dtk.ui.theme import ui_theme
from dtk.ui.label import Label
from dtk.ui.button import RadioButton, Button
from dtk.ui.hscalebar import HScalebar
from dtk.ui.line import HSeparator
from dtk.ui.box import ImageBox
from dtk.ui.utils import propagate_expose, color_hex_to_cairo, set_clickable_cursor
import gtk
from statusbar import StatusBar
from nls import _
from module_frame import ModuleFrame
from constant import *

MODULE_NAME = "mouse"

class MouseSetting(object):
    '''mouse setting class'''
    def __init__(self, module_frame):
        self.settings = settings.MOUSE_SETTINGS
        self.module_frame = module_frame
        self.scale_set= {
            "motion-acceleration" : settings.mouse_set_motion_acceleration,
            "motion-threshold"    : settings.mouse_set_motion_threshold,
            "double-click"        : settings.mouse_set_double_click}
        self.scale_get= {
            "motion-acceleration" : settings.mouse_get_motion_acceleration,
            "motion-threshold"    : settings.mouse_get_motion_threshold,
            "double-click"        : settings.mouse_get_double_click}

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
        option_item_font_size = CONTENT_FONT_SIZE
        # image init
        self.image_widgets["custom"] = ImageBox(app_theme.get_pixbuf("%s/mouse_l.png" % MODULE_NAME))
        self.image_widgets["speed"] = ImageBox(app_theme.get_pixbuf("%s/pointer.png" % MODULE_NAME))
        self.image_widgets["double"] = ImageBox(app_theme.get_pixbuf("%s/double-click.png" % MODULE_NAME))
        self.image_widgets["double_test_1"] = app_theme.get_pixbuf("%s/smiley00.png" % MODULE_NAME)
        self.image_widgets["double_test_2"] = app_theme.get_pixbuf("%s/smiley01.png" % MODULE_NAME)
        # label init
        self.label_widgets["custom"] = Label(_("Custom"), app_theme.get_color("globalTitleForeground"), text_size=title_item_font_size, enable_select=False, enable_double_click=False)
        self.label_widgets["pointer_speed"] = Label(_("Pointer Speed"), app_theme.get_color("globalTitleForeground"), text_size=title_item_font_size, enable_select=False, enable_double_click=False)
        self.label_widgets["acceleration"] = Label(_("Acceleration"),
            text_size=option_item_font_size, enable_select=False, enable_double_click=False)
        self.label_widgets["accel_fast"] = Label(_("Fast"), enable_select=False, enable_double_click=False)
        self.label_widgets["accel_slow"] = Label(_("Slow"), enable_select=False, enable_double_click=False)
        self.label_widgets["sensitivity"] = Label(_("Sensitivity"),
            text_size=option_item_font_size, enable_select=False, enable_double_click=False)
        self.label_widgets["sensitiv_low"] = Label(_("Low"), enable_select=False, enable_double_click=False)
        self.label_widgets["sensitiv_high"] = Label(_("High"), enable_select=False, enable_double_click=False)
        self.label_widgets["double_click"] = Label(_("Double-click"), app_theme.get_color("globalTitleForeground"), text_size=title_item_font_size, enable_select=False, enable_double_click=False)
        self.label_widgets["click_rate"] = Label(_("Frequency"),
            text_size=option_item_font_size, enable_select=False, enable_double_click=False)
        self.label_widgets["click_fast"] = Label(_("Fast"), enable_select=False, enable_double_click=False)
        self.label_widgets["click_slow"] = Label(_("Slow"), enable_select=False, enable_double_click=False)
        self.label_widgets["double_test"] = Label(_("Double-click on the smiley face to test your settings."),
            label_width=HSCALEBAR_WIDTH, wrap_width=HSCALEBAR_WIDTH, enable_select=False, enable_double_click=False)
        self.label_widgets["relevant"] = Label(_("Relevant Settings"), text_size=option_item_font_size, enable_select=False, enable_double_click=False)
        # button init
        self.button_widgets["right_hand_radio"] = RadioButton( _("Right-handed"), padding_x=10)
        self.button_widgets["left_hand_radio"] = RadioButton(_("Left-handed"), padding_x=10)
        self.button_widgets["double_test"] = gtk.EventBox()
        # relevant settings button
        self.button_widgets["keyboard_setting"] = Label("<u>%s</u>" % _("Keyboard Settings"),
            app_theme.get_color("globalTitleForeground"), text_size=option_item_font_size,
            enable_select=False, enable_double_click=False)
        self.button_widgets["touchpad_setting"] = Label("<u>%s</u>" % _("TouchPad Settings"),
            app_theme.get_color("globalTitleForeground"), text_size=option_item_font_size,
            enable_select=False, enable_double_click=False)
        self.button_widgets["set_to_default"] = Button(_("Reset to Defaults"))
        # container init
        self.container_widgets["main_vbox"] = gtk.VBox(False)
        self.container_widgets["statusbar"] = StatusBar()
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
        # alignment init
        self.alignment_widgets["main_hbox"] = gtk.Alignment()
        self.alignment_widgets["left"] = gtk.Alignment()
        self.alignment_widgets["right"] = gtk.Alignment()
        self.alignment_widgets["custom_label"] = gtk.Alignment()            # custom
        self.alignment_widgets["custom_button"] = gtk.Alignment()
        self.alignment_widgets["pointer_speed_label"] = gtk.Alignment()     # pointer speed
        self.alignment_widgets["pointer_speed_table"] = gtk.Alignment()
        self.alignment_widgets["double_click_label"] = gtk.Alignment()      # double click
        self.alignment_widgets["double_click_table"] = gtk.Alignment()
        self.alignment_widgets["keyboard_setting"] = gtk.Alignment()
        self.alignment_widgets["touchpad_setting"] = gtk.Alignment()
        # adjust init
        self.adjust_widgets["pointer_speed_accel"] = gtk.Adjustment(1.0, 1.0, 10.0, 1, 2)
        self.adjust_widgets["pointer_speed_sensitiv"] = gtk.Adjustment(1, 1, 10, 1, 2)
        self.adjust_widgets["double_click_rate"] = gtk.Adjustment(100, 100, 1000, 100, 200)
        # scale init
        self.scale_widgets["pointer_speed_accel"] = HScalebar(value_min=1, value_max=10)
        #self.scale_widgets["pointer_speed_accel"] = HScalebar(
            #None, None, None, None, None, None,
            #app_theme.get_pixbuf("scalebar/point.png"))
        #self.scale_widgets["pointer_speed_accel"].set_adjustment( self.adjust_widgets["pointer_speed_accel"])
        self.scale_widgets["pointer_speed_sensitiv"] = HScalebar(value_min=1, value_max=10)
        #self.scale_widgets["pointer_speed_sensitiv"] = HScalebar(
            #None, None, None, None, None, None,
            #app_theme.get_pixbuf("scalebar/point.png"))
        #self.scale_widgets["pointer_speed_sensitiv"].set_adjustment( self.adjust_widgets["pointer_speed_sensitiv"])
        self.scale_widgets["double_click_rate"] = HScalebar(value_min=100, value_max=1000)
        #self.scale_widgets["double_click_rate"] = HScalebar(
            #None, None, None, None, None, None,
            #app_theme.get_pixbuf("scalebar/point.png"))
        #self.scale_widgets["double_click_rate"].set_adjustment( self.adjust_widgets["double_click_rate"])
     
    def __adjust_widget(self):
        ''' adjust widget '''
        MID_SPACING = 10
        RIGHT_BOX_WIDTH = TIP_BOX_WIDTH - 20
        MAIN_AREA_WIDTH = 480
        LABEL_WIDTH = 180
        OPTION_LEFT_PADDING = WIDGET_SPACING + 16
        TABLE_ROW_SPACING = 15
        self.container_widgets["main_vbox"].pack_start(self.alignment_widgets["main_hbox"])
        self.container_widgets["main_vbox"].pack_start(self.container_widgets["statusbar"], False, False)
        self.container_widgets["statusbar"].set_buttons([self.button_widgets["set_to_default"]])
        self.alignment_widgets["main_hbox"].add(self.container_widgets["main_hbox"])
        self.alignment_widgets["main_hbox"].set(0.0, 0.0, 1.0, 1.0)
        self.alignment_widgets["main_hbox"].set_padding(
            TEXT_WINDOW_TOP_PADDING, 0, 0, 0)
        
        self.container_widgets["main_hbox"].set_spacing(MID_SPACING)
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["left"])
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["right"], False, False)
        self.alignment_widgets["left"].add(self.container_widgets["left_vbox"])
        self.alignment_widgets["right"].add(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].set_size_request(RIGHT_BOX_WIDTH, -1)
        # set left padding
        self.alignment_widgets["left"].set(0.0, 0.5, 1.0, 1.0)
        # set right padding
        self.alignment_widgets["right"].set(0.0, 0.0, 1.0, 1.0)
        self.alignment_widgets["right"].set_padding(0, 0, 0, 60)
        
        self.container_widgets["left_vbox"].set_spacing(BETWEEN_SPACING)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["custom_main_vbox"], False, False)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["pointer_speed_main_vbox"], False, False)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["double_click_main_vbox"], False, False)
        # set option label width
        label_widgets = self.label_widgets
        label_width = max(label_widgets["acceleration"].size_request()[0],
                          label_widgets["sensitivity"].size_request()[0],
                          label_widgets["click_rate"].size_request()[0]) + 2
        #label_widgets["acceleration"].set_size_request(label_width, WIDGET_HEIGHT)
        #label_widgets["sensitivity"].set_size_request(label_width, WIDGET_HEIGHT)
        #label_widgets["click_rate"].set_size_request(label_width, WIDGET_HEIGHT)
        # custom
        self.alignment_widgets["custom_label"].add(self.container_widgets["custom_label_hbox"])
        self.alignment_widgets["custom_button"].add(self.container_widgets["custom_button_hbox"])
        # alignment set
        self.alignment_widgets["custom_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["custom_button"].set(0.0, 0.5, 0.0, 0.0)
        self.alignment_widgets["custom_button"].set_padding(0, 0, TEXT_WINDOW_LEFT_PADDING+OPTION_LEFT_PADDING-10, 0)
        self.alignment_widgets["custom_label"].set_padding(0, 0, TEXT_WINDOW_LEFT_PADDING, 0)
        #self.alignment_widgets["custom_label"].set_size_request(-1, CONTAINNER_HEIGHT)
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
        if settings.mouse_get_left_handed():
            self.button_widgets["left_hand_radio"].set_active(True)
            self.image_widgets["custom"].image_dpixbuf = app_theme.get_pixbuf("%s/mouse_r.png" % MODULE_NAME)
        else:
            self.button_widgets["right_hand_radio"].set_active(True)
            self.image_widgets["custom"].image_dpixbuf = app_theme.get_pixbuf("%s/mouse_l.png" % MODULE_NAME)
        self.container_widgets["custom_button_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["custom_button_hbox0"] = gtk.HBox(False)
        self.container_widgets["custom_button_hbox0"].set_spacing(WIDGET_SPACING)
        self.container_widgets["custom_button_hbox0"].pack_start(
            self.button_widgets["right_hand_radio"], False, False)
        self.container_widgets["custom_button_hbox0"].pack_start(
            self.button_widgets["left_hand_radio"], False, False)
        button_align = self.__make_align(self.container_widgets["custom_button_hbox0"], xalign=0.0)
        button_align.set_size_request(HSCALEBAR_WIDTH+WIDGET_SPACING+label_width, CONTAINNER_HEIGHT)
        self.container_widgets["custom_button_hbox"].pack_start(button_align, False, False)
        self.container_widgets["custom_button_hbox"].pack_start(self.__make_align())

        # pointer speed
        self.alignment_widgets["pointer_speed_label"].add(self.container_widgets["pointer_speed_label_hbox"])
        self.alignment_widgets["pointer_speed_table"].add(self.container_widgets["pointer_speed_table"])
        # alignment set
        self.alignment_widgets["pointer_speed_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["pointer_speed_table"].set(0.0, 0.5, 1.0, 1.0)
        #self.alignment_widgets["pointer_speed_table"].set_padding(0, 0, OPTION_LEFT_PADDING+TEXT_WINDOW_LEFT_PADDING, 0)
        #self.alignment_widgets["pointer_speed_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["pointer_speed_label"].set_padding(0, 0, TEXT_WINDOW_LEFT_PADDING, 0)
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
        self.scale_widgets["pointer_speed_accel"].set_value(settings.mouse_get_motion_acceleration())
        self.scale_widgets["pointer_speed_accel"].add_mark(self.adjust_widgets["pointer_speed_accel"].get_lower(), gtk.POS_BOTTOM, _("Slow"))
        self.scale_widgets["pointer_speed_accel"].add_mark(self.adjust_widgets["pointer_speed_accel"].get_upper(), gtk.POS_BOTTOM, _("Fast"))
        self.scale_widgets["pointer_speed_accel"].set_size_request(HSCALEBAR_WIDTH, -1)
        # table attach
        self.container_widgets["pointer_speed_table"].set_size_request(MAIN_AREA_WIDTH, -1)
        self.container_widgets["pointer_speed_table"].set_col_spacings(WIDGET_SPACING)
        #self.container_widgets["pointer_speed_table"].set_row_spacing(0, TABLE_ROW_SPACING)
        acceleration_align = self.__make_align(self.label_widgets["acceleration"], xalign=1.0)
        acceleration_align.set_size_request(STANDARD_LINE, CONTAINNER_HEIGHT)
        self.container_widgets["pointer_speed_table"].attach(
            acceleration_align, 0, 1, 0, 1, 4)
        self.container_widgets["pointer_speed_table"].attach(
            self.__make_align(self.scale_widgets["pointer_speed_accel"], yalign=0.0, yscale=1.0, height=43), 1, 3, 0, 1, 4)
        # motion threshold
        self.scale_widgets["pointer_speed_sensitiv"].set_value(settings.mouse_get_motion_threshold())
        self.scale_widgets["pointer_speed_sensitiv"].add_mark(self.adjust_widgets["pointer_speed_sensitiv"].get_lower(), gtk.POS_BOTTOM, _("Low"))
        self.scale_widgets["pointer_speed_sensitiv"].add_mark(self.adjust_widgets["pointer_speed_sensitiv"].get_upper(), gtk.POS_BOTTOM, _("High"))
        self.scale_widgets["pointer_speed_sensitiv"].set_size_request(HSCALEBAR_WIDTH, -1)
        # table attach
        sensitivity_align = self.__make_align(self.label_widgets["sensitivity"], xalign=1.0)
        sensitivity_align.set_size_request(STANDARD_LINE, CONTAINNER_HEIGHT)
        self.container_widgets["pointer_speed_table"].attach(
            sensitivity_align, 0, 1, 1, 2, 4)
        self.container_widgets["pointer_speed_table"].attach(
            self.__make_align(self.scale_widgets["pointer_speed_sensitiv"], yalign=0.0, yscale=1.0, height=43), 1, 3, 1, 2, 4)

        # double click
        self.alignment_widgets["double_click_label"].add(self.container_widgets["double_click_label_hbox"])
        self.alignment_widgets["double_click_table"].add(self.container_widgets["double_click_table"])
        self.alignment_widgets["double_click_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["double_click_table"].set(0.0, 0.5, 1.0, 1.0)
        #self.alignment_widgets["double_click_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["double_click_label"].set_padding(0, 0, TEXT_WINDOW_LEFT_PADDING, 0)
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
        self.scale_widgets["double_click_rate"].set_value(settings.mouse_get_double_click())
        self.scale_widgets["double_click_rate"].add_mark(self.adjust_widgets["double_click_rate"].get_lower(), gtk.POS_BOTTOM, _("Slow"))
        self.scale_widgets["double_click_rate"].add_mark(self.adjust_widgets["double_click_rate"].get_upper(), gtk.POS_BOTTOM, _("Fast"))
        self.scale_widgets["double_click_rate"].set_size_request(HSCALEBAR_WIDTH, -1)
        # table attach
        self.container_widgets["double_click_table"].set_size_request(MAIN_AREA_WIDTH, -1)
        self.container_widgets["double_click_table"].set_col_spacings(WIDGET_SPACING)
        click_rate_align = self.__make_align(self.label_widgets["click_rate"], xalign=1.0)
        click_rate_align.set_size_request(STANDARD_LINE, CONTAINNER_HEIGHT)
        self.container_widgets["double_click_table"].attach(
            click_rate_align, 0, 1, 0, 1, 4)
        self.container_widgets["double_click_table"].attach(
            self.__make_align(self.scale_widgets["double_click_rate"], xalign=0.0, yalign=0.0, yscale=1.0, height=43), 1, 3, 0, 1, 4)
        self.container_widgets["double_click_table"].attach(
            self.__make_align(self.label_widgets["double_test"], xalign=0.0), 1, 3, 1, 2, 4)
        self.container_widgets["double_click_table"].attach(
            self.__make_align(self.button_widgets["double_test"], xalign=0.0, xscale=1.0, height=-1), 3, 4, 0, 2)
        self.button_widgets["double_test"].set_size_request(
            self.image_widgets["double_test_1"].get_pixbuf().get_width(),
            self.image_widgets["double_test_1"].get_pixbuf().get_height())

        # relevant setting
        self.container_widgets["right_vbox"].pack_start(
            self.__make_align(self.label_widgets["relevant"], height=-1), False, False)
        self.container_widgets["right_vbox"].pack_start(
            self.alignment_widgets["keyboard_setting"], False, False)
        self.container_widgets["right_vbox"].pack_start(
            self.alignment_widgets["touchpad_setting"], False, False)
        self.alignment_widgets["keyboard_setting"].add(self.button_widgets["keyboard_setting"])
        self.alignment_widgets["touchpad_setting"].add(self.button_widgets["touchpad_setting"])
        self.alignment_widgets["keyboard_setting"].set(0.0, 0.5, 0.0, 0.0)
        self.alignment_widgets["touchpad_setting"].set(0.0, 0.5, 0.0, 0.0)
        self.alignment_widgets["keyboard_setting"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["touchpad_setting"].set_size_request(-1, CONTAINNER_HEIGHT)
        #self.alignment_widgets["keyboard_setting"].set_padding(0, 0, 10, 0)
        #self.alignment_widgets["touchpad_setting"].set_padding(0, 0, 10, 0)

    def __signals_connect(self):
        ''' widget signals connect'''
        self.alignment_widgets["main_hbox"].connect("expose-event", self.container_expose_cb)
        # left-handed operation
        self.settings.connect("changed", self.settings_changed_cb)
        self.button_widgets["right_hand_radio"].connect("toggled", self.left_or_right_set, False)
        self.button_widgets["left_hand_radio"].connect("toggled", self.left_or_right_set, True)
        # acceleration operation
        self.scale_widgets["pointer_speed_accel"].connect(
            "button-release-event", self.scalebar_value_changed, "motion-acceleration")
        # sensitivity operation
        self.scale_widgets["pointer_speed_sensitiv"].connect(
            "button-release-event", self.scalebar_value_changed, "motion-threshold")
        # double-click operation
        self.scale_widgets["double_click_rate"].connect(
            "button-release-event", self.scalebar_value_changed, "double-click")
        # adjustment widget
        self.adjust_widgets["pointer_speed_accel"].connect("value-changed",
            lambda w: self.scale_widgets["pointer_speed_accel"].set_value(
                self.adjust_widgets["pointer_speed_accel"].get_value()))
        self.adjust_widgets["pointer_speed_sensitiv"].connect("value-changed",
            lambda w: self.scale_widgets["pointer_speed_sensitiv"].set_value(
                self.adjust_widgets["pointer_speed_sensitiv"].get_value()))
        self.adjust_widgets["double_click_rate"].connect("value-changed",
            lambda w: self.scale_widgets["double_click_rate"].set_value(
                self.adjust_widgets["double_click_rate"].get_value()))
        self.button_widgets["double_test"].set_data("has_double_clicked", False)
        self.button_widgets["double_test"].connect("button-press-event", self.double_click_test)
        self.button_widgets["double_test"].connect("expose-event", self.double_click_test_expose)
        
        # relevant setting
        self.button_widgets["keyboard_setting"].connect("button-press-event", self.relevant_press, "keyboard")
        self.button_widgets["touchpad_setting"].connect("button-press-event", self.relevant_press, "touchpad")
        set_clickable_cursor(self.button_widgets["keyboard_setting"])
        set_clickable_cursor(self.button_widgets["touchpad_setting"])

        self.button_widgets["set_to_default"].connect("clicked", self.set_to_default)
    
    #############################
    def container_expose_cb(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))
        cr.rectangle(x, y, w, h)
        cr.fill()
    
    def settings_changed_cb(self, key):
        args = [self.settings, key]
        if key == 'left-handed':
            callback = self.left_or_right_setting_changed
        elif key == 'motion-acceleration':
            callback = self.settings_value_changed
            #args.append(self.adjust_widgets["pointer_speed_accel"])
            args.append(self.scale_widgets["pointer_speed_accel"])
        elif key == 'motion-threshold':
            callback = self.settings_value_changed
            #args.append(self.adjust_widgets["pointer_speed_sensitiv"])
            args.append(self.scale_widgets["pointer_speed_sensitiv"])
        elif key == 'double-click':
            callback = self.settings_value_changed
            #args.append(self.adjust_widgets["double_click_rate"])
            args.append(self.scale_widgets["double_click_rate"])
        else:
            return
        callback(*args)
    
    def left_or_right_set(self, button, active):
        ''' set left-handed '''
        if button.get_data("changed-by-other-app"):
            button.set_data("changed-by-other-app", False)
            return
        if button.get_active():
            settings.mouse_set_left_handed(active)
    
    def left_or_right_setting_changed(self, setting, key):
        ''' set left or right radio button active '''
        if setting.get_boolean(key):
            self.button_widgets["left_hand_radio"].set_active(True)
            self.image_widgets["custom"].image_dpixbuf = app_theme.get_pixbuf("%s/mouse_r.png" % MODULE_NAME)
            self.button_widgets["left_hand_radio"].set_data("changed-by-other-app", True)
        else:
            self.button_widgets["right_hand_radio"].set_active(True)
            self.image_widgets["custom"].image_dpixbuf = app_theme.get_pixbuf("%s/mouse_l.png" % MODULE_NAME)
            self.button_widgets["right_hand_radio"].set_data("changed-by-other-app", True)
        self.image_widgets["custom"].queue_draw()
    
    def scalebar_value_changed(self, widget, event, key):
        '''adjustment value changed, and settings set the value'''
        value = widget.value + widget.value_min
        if key == "motion-threshold":   # motion-threshold is an int type
            new_value = value
            old_value = self.settings.get_int(key)
            if abs(new_value - old_value) < 0.9:
                return
            if new_value > old_value:
                value = int(new_value + 0.2)
            else:
                value = int(new_value)
        self.scale_set[key](value)
    
    def settings_value_changed(self, settings, key, adjustment):
        '''settings value changed, and adjustment set the value'''
        adjustment.set_value(self.scale_get[key]())
        adjustment.set_data("changed-by-other-app", True)

    def double_click_test(self, widget, event):
        '''double clicked callback, to test the double-click time'''
        if event.type == gtk.gdk._2BUTTON_PRESS or event.type == gtk.gdk._3BUTTON_PRESS:
            widget.set_data("has_double_clicked", not widget.get_data("has_double_clicked"))
            widget.queue_draw()
    
    def double_click_test_expose(self, widget, event):
        '''double_test button expsoe'''
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
        hseparator.set_size_request(450, 10)
        return hseparator
    
    def __setup_separator(self):
        return self.__make_align(self.__make_separator(), xalign=0.0, xscale=0.0, padding_left=TEXT_WINDOW_LEFT_PADDING, height=10)
    
    def set_to_default(self, button):
        '''set to the default'''
        settings.mouse_set_to_default()
    
if __name__ == '__main__':
    gtk.gdk.threads_init()
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    mouse_settings = MouseSetting(module_frame)
    
    module_frame.add(mouse_settings.container_widgets["main_vbox"])
    
    if len(sys.argv) > 1:
        print "module_uid:", sys.argv[1]
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            print "DEBUG show_again module_uid", message_content
            module_frame.send_module_info()

    module_frame.module_message_handler = message_handler        
    
    module_frame.run()
