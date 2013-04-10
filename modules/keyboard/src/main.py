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
from dtk.ui.theme import DynamicColor
from dtk.ui.dialog import DialogBox, DIALOG_MASK_SINGLE_PAGE
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.label import Label
from dtk.ui.button import Button, OffButton
from dtk.ui.entry import InputEntry, EntryBuffer
from dtk.ui.tab_window import TabBox
from dtk.ui.scalebar import HScalebar
from dtk.ui.line import HSeparator
from dtk.ui.box import ImageBox
from dtk.ui.utils import cairo_disable_antialias, color_hex_to_cairo, set_clickable_cursor, container_remove_all
from treeitem import (SelectItem, LayoutItem,
                      AccelBuffer, ShortcutItem)
from treeitem import MyTreeView as TreeView
from accel_entry import AccelEntry
from blink import BlinkButton
from statusbar import StatusBar
from nls import _
from glib import markup_escape_text
import xkb
import gtk
import keybind_mk
import pangocairo
import pango
import threading
from time import sleep
from module_frame import ModuleFrame
from constant import *

MODULE_NAME = "keyboard"

class KeySetting(object):
    '''keyboard setting class'''
    def __init__(self, module_frame):
        self.settings = settings.KEYBOARD_SETTINGS
        self.settings1 = settings.DESKTOP_SETTINGS
        self.settings2 = settings.TOUCHPAD_SETTINGS
        self.module_frame = module_frame
        self.xkb = xkb.XKeyBoard()
        self.__layout_items = self.xkb.get_layout_treeitems()

        self.__shortcuts_entries = keybind_mk.get_all_shortcuts_entry(
            [settings.WM_SHORTCUTS_SETTINGS, settings.SHORTCUTS_SETTINGS,
             settings.DP_SHORTCUTS_SETTINGS, settings.COMPIZ_SHORTCUTS_SETTINGS])
        self.__shortcuts_entries[_('Custom Shortcuts')] = keybind_mk.get_shortcuts_custom_shortcut_entry(settings.GCONF_CLIENT, self.__remove_shortcuts_item)
        self.__shortcuts_entries_page_widgets = {}
        self.scale_set= {
            "delay"               : settings.keyboard_set_repeat_delay,
            "repeat-interval"     : settings.keyboard_set_repeat_interval,
            "cursor-blink-time"   : settings.keyboard_set_cursor_blink_time}
        self.scale_get= {
            "delay"               : settings.keyboard_get_repeat_delay,
            "repeat-interval"     : settings.keyboard_get_repeat_interval,
            "cursor-blink-time"   : settings.keyboard_get_cursor_blink_time}

        self.image_widgets = {}
        self.label_widgets = {}
        self.button_widgets = {}
        self.adjust_widgets = {}
        self.scale_widgets = {}
        self.alignment_widgets = {}
        self.container_widgets = {}
        self.view_widgets = {}
        self.dialog_widget = {}

        self.__create_widget()
        self.__adjust_widget()
        self.__signals_connect()

    def __create_widget(self):
        '''create gtk widget'''
        title_item_font_size = TITLE_FONT_SIZE
        option_item_font_size = CONTENT_FONT_SIZE

        #####################################
        # Typing widgets create
        # image init
        self.image_widgets["repeat"] = ImageBox(app_theme.get_pixbuf("%s/repeat.png" % MODULE_NAME))
        self.image_widgets["blink"] = ImageBox(app_theme.get_pixbuf("%s/blink.png" % MODULE_NAME))
        self.image_widgets["touchpad"] = ImageBox(app_theme.get_pixbuf("%s/typing.png" % MODULE_NAME))
        self.image_widgets["layout"] = ImageBox(app_theme.get_pixbuf("%s/layout.png" % MODULE_NAME))
        # label init
        self.label_widgets["repeat"] = Label(_("Repeat"),
            app_theme.get_color("globalTitleForeground"),
            text_size=title_item_font_size, enable_select=False, enable_double_click=False)
        self.label_widgets["repeat_delay"] = Label(_("Repeat Delay"), text_size=option_item_font_size, enable_select=False, enable_double_click=False)
        self.label_widgets["repeat_interval"] = Label(_("Repeat Interval"), text_size=option_item_font_size, enable_select=False, enable_double_click=False)
        self.label_widgets["repeat_fast"] = Label(_("Fast"), enable_select=False, enable_double_click=False)
        self.label_widgets["repeat_slow"] = Label(_("Slow"), enable_select=False, enable_double_click=False)
        self.label_widgets["repeat_long"] = Label(_("Long"), enable_select=False, enable_double_click=False)
        self.label_widgets["repeat_short"] = Label(_("Short"), enable_select=False, enable_double_click=False)
        self.label_widgets["blink"] = Label(_("Cursor Blink"),
            app_theme.get_color("globalTitleForeground"),
            text_size=title_item_font_size, enable_select=False, enable_double_click=False)
        self.label_widgets["blink_fast"] = Label(_("Fast"), enable_select=False, enable_double_click=False)
        self.label_widgets["blink_slow"] = Label(_("Slow"), enable_select=False, enable_double_click=False)
        self.label_widgets["touchpad"] = Label(_("Disable touchpad while typing"),
            app_theme.get_color("globalTitleForeground"),
            text_size=title_item_font_size, enable_select=False, enable_double_click=False)
        self.label_widgets["layout"] = Label(_("Keyboard Layout"),
            app_theme.get_color("globalTitleForeground"),
            text_size=title_item_font_size, enable_select=False, enable_double_click=False)

        self.label_widgets["relevant"] = Label(_("Relevant Settings"), text_size=title_item_font_size, enable_select=False, enable_double_click=False)
        # button init
        self.button_widgets["repeat_test_entry"] = InputEntry()
        self.button_widgets["repeat_entry_buffer"] = self.button_widgets["repeat_test_entry"].entry.get_buffer()
        self.button_widgets["repeat_entry_buffer2"] = EntryBuffer(_("Test Repeat Interval"))
        self.button_widgets["repeat_test_entry"].entry.set_buffer(self.button_widgets["repeat_entry_buffer2"])
        self.button_widgets["blink_test_entry"] = BlinkButton(settings.keyboard_get_cursor_blink_time())
        #self.button_widgets["repeat_test_entry"] = gtk.Entry()
        #self.button_widgets["blink_test_entry"] = gtk.Entry()
        self.button_widgets["touchpad_disable"] = OffButton()
        # relevant settings button
        self.button_widgets["mouse_setting"] = Label("<u>%s</u>" % _("Mouse Settings"),
            DynamicColor(GOTO_FG_COLOR), text_size=option_item_font_size,
            enable_select=False, enable_double_click=False)
        self.button_widgets["touchpad_setting"] = Label("<u>%s</u>" % _("TouchPad Settings"),
            DynamicColor(GOTO_FG_COLOR), text_size=option_item_font_size,
            enable_select=False, enable_double_click=False)
        self.button_widgets["set_to_default"] = Button(_("Reset"))
        # container init
        self.container_widgets["main_vbox"] = gtk.VBox(False)
        self.container_widgets["statusbar"] = StatusBar()
        self.container_widgets["tab_box"] = TabBox()
        self.container_widgets["tab_box"].draw_title_background = self.draw_tab_title_background
        self.container_widgets["type_swindow"] = ScrolledWindow()
        self.container_widgets["type_main_hbox"] = gtk.HBox(False)
        self.container_widgets["layout_main_hbox"] = gtk.HBox(False)
        self.container_widgets["shortcuts_main_hbox"] = gtk.HBox(False)
        self.container_widgets["left_vbox"] = gtk.VBox(False)
        self.container_widgets["right_vbox"] = gtk.VBox(False)
        self.container_widgets["repeat_main_vbox"] = gtk.VBox(False)     # repeat
        self.container_widgets["repeat_label_hbox"] = gtk.HBox(False)
        self.container_widgets["repeat_table"] = gtk.Table(3, 2, False)
        self.container_widgets["repeat_delay_hbox"] = gtk.HBox(False)
        self.container_widgets["repeat_interval_hbox"] = gtk.HBox(False)
        self.container_widgets["blink_main_vbox"] = gtk.VBox(False)      # blink
        self.container_widgets["blink_label_hbox"] = gtk.HBox(False)
        self.container_widgets["blink_table"] = gtk.Table(2, 2, False)
        self.container_widgets["blink_cursor_hbox"] = gtk.HBox(False)
        self.container_widgets["touchpad_main_vbox"] = gtk.VBox(False)      # touchpad
        self.container_widgets["touchpad_label_hbox"] = gtk.HBox(False)
        # alignment init
        self.alignment_widgets["notebook"] = gtk.Alignment()
        self.alignment_widgets["left"] = gtk.Alignment()
        self.alignment_widgets["right"] = gtk.Alignment()
        self.alignment_widgets["type_label"] = gtk.Alignment()            # type
        self.alignment_widgets["type_table"] = gtk.Alignment()
        self.alignment_widgets["blink_label"] = gtk.Alignment()      # blink
        self.alignment_widgets["blink_table"] = gtk.Alignment()
        self.alignment_widgets["touchpad_label"] = gtk.Alignment()      # touchpad
        self.alignment_widgets["mouse_setting"] = gtk.Alignment()
        self.alignment_widgets["touchpad_setting"] = gtk.Alignment()
        # adjust init
        self.adjust_widgets["repeat_delay"] = gtk.Adjustment(100, 100, 2000, 100, 500)
        self.adjust_widgets["repeat_interval"] = gtk.Adjustment(20, 20, 2000, 100, 500)
        self.adjust_widgets["blink_cursor"] = gtk.Adjustment(100, 100, 2500, 100, 501)
        # scale init
        self.scale_widgets["repeat_delay"] = HScalebar(value_min=100, value_max=2000)
        self.scale_widgets["repeat_interval"] = HScalebar(value_min=20, value_max=2000)
        self.scale_widgets["blink_cursor"] = HScalebar(value_min=100, value_max=2500)
        #####################################
        # Layout widgets create
        # label
        self.label_widgets["layout_current_layout"] = Label("", enable_select=False, enable_double_click=False)
        # button init
        self.button_widgets["layout_add"] = Button(_("Replace"))
        self.button_widgets["layout_remove"] = Button(_("Remove"))
        # view init
        self.view_widgets["layout_selected"] = TreeView(enable_hover=False)
        # container init
        self.container_widgets["layout_vbox"] = gtk.VBox(False)
        self.container_widgets["layout_button_hbox"] = gtk.HBox(False)
        self.container_widgets["layout_label_hbox"] = gtk.HBox(False)
        self.container_widgets["layout_table"] = gtk.Table(1, 2)
        # alignment init
        self.alignment_widgets["layout_vbox"] = gtk.Alignment()
        self.alignment_widgets["layout_button_hbox"] = gtk.Alignment()
        self.alignment_widgets["layout_label"] = gtk.Alignment()
        self.alignment_widgets["layout_table"] = gtk.Alignment()
        #####################################
        # Shortcuts widgets create
        # label init
        # button init
        self.button_widgets["shortcuts_add"] = Button(_("Add"))
        self.button_widgets["shortcuts_remove"] = Button(_("Remove"))
        # view init
        self.view_widgets["shortcuts_selected"] = TreeView(enable_hover=True)
        #self.view_widgets["shortcuts_shortcut"] = TreeView(enable_hover=False)
        # container init
        self.container_widgets["shortcuts_table"] = gtk.Table(2, 3, False)
        self.container_widgets["shortcuts_toolbar_hbox"] = gtk.HBox(False)
        #self.container_widgets["shortcuts_swin"] = ScrolledWindow()
        self.container_widgets["shortcuts_swin"] = gtk.VBox(False)
        # alignment init
        self.alignment_widgets["shortcuts_table"] = gtk.Alignment()
     
    def draw_tab_title_background(self, cr, widget):
        rect = widget.allocation
        cr.set_source_rgb(1, 1, 1)    
        cr.rectangle(0, 0, rect.width, rect.height - 1)
        cr.fill()
        
    def __adjust_widget(self):
        ''' adjust widget '''
        MID_SPACING = 10
        RIGHT_BOX_WIDTH = TIP_BOX_WIDTH - 20
        MAIN_AREA_WIDTH = 480
        LABEL_WIDTH = 180
        OPTION_LEFT_PADDING = WIDGET_SPACING + 16
        TABLE_ROW_SPACING = 15
        self.container_widgets["main_vbox"].pack_start(self.alignment_widgets["notebook"])
        self.container_widgets["main_vbox"].pack_start(self.container_widgets["statusbar"], False, False)
        self.container_widgets["statusbar"].set_buttons([self.button_widgets["set_to_default"]])
        self.alignment_widgets["notebook"].set(0.0, 0.0, 1, 1)
        #self.alignment_widgets["notebook"].set_padding(FRAME_TOP_PADDING, 0, FRAME_LEFT_PADDING, FRAME_LEFT_PADDING)
        self.alignment_widgets["notebook"].set_padding(FRAME_TOP_PADDING, 0, 0, 0)
        self.alignment_widgets["notebook"].add(self.container_widgets["tab_box"])
        tab_box_item = [
            (_("Typing"), self.container_widgets["type_swindow"]),
            (_("Shortcuts"), self.container_widgets["shortcuts_main_hbox"])]
            #(_("Layout"), self.container_widgets["layout_main_hbox"])]
        self.container_widgets["tab_box"].add_items(tab_box_item)
        ###########################
        # typing set
        self.container_widgets["type_swindow"].add_child(self.container_widgets["type_main_hbox"])
        self.container_widgets["type_main_hbox"].set_spacing(MID_SPACING)
        self.container_widgets["type_main_hbox"].pack_start(self.alignment_widgets["left"])
        self.container_widgets["type_main_hbox"].pack_start(self.alignment_widgets["right"], False, False)
        self.alignment_widgets["left"].add(self.container_widgets["left_vbox"])
        self.alignment_widgets["right"].add(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].set_size_request(RIGHT_BOX_WIDTH, -1)
        # set left padding
        self.alignment_widgets["left"].set(0.0, 0.0, 1.0, 1.0)
        self.alignment_widgets["left"].set_padding(TEXT_WINDOW_TOP_PADDING, 20, 0, 0)
        # set right padding
        self.alignment_widgets["right"].set(0.0, 0.0, 0.0, 1.0)
        self.alignment_widgets["right"].set_padding(TEXT_WINDOW_TOP_PADDING, 0, 0, 60)
        
        self.container_widgets["left_vbox"].set_spacing(BETWEEN_SPACING)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["repeat_main_vbox"], False, False)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["blink_main_vbox"], False, False)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["touchpad_main_vbox"], False, False)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["layout_vbox"], False, False)
        # set option label width
        label_widgets = self.label_widgets
        label_width = max(
            label_widgets["repeat_delay"].size_request()[0],
            label_widgets["repeat_interval"].size_request()[0]) + 2
        #self.button_widgets["blink_test_entry"].set_size(label_width, WIDGET_HEIGHT)
        self.button_widgets["blink_test_entry"].set_size_request(label_width, 16)

        # repeat
        self.alignment_widgets["type_label"].add(self.container_widgets["repeat_label_hbox"])
        self.alignment_widgets["type_table"].add(self.container_widgets["repeat_table"])
        # alignment set
        self.alignment_widgets["type_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["type_label"].set_padding(0, 0, TEXT_WINDOW_LEFT_PADDING, 0)
        #self.alignment_widgets["type_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["type_table"].set(0.0, 0.5, 0.0, 1.0)
        #self.alignment_widgets["type_table"].set_padding(0, 0, OPTION_LEFT_PADDING, 0)
        self.container_widgets["repeat_main_vbox"].pack_start(
            self.alignment_widgets["type_label"], False, False)
        self.container_widgets["repeat_main_vbox"].pack_start(
            self.__setup_separator(), False, False)
        self.container_widgets["repeat_main_vbox"].pack_start(
            self.alignment_widgets["type_table"])
        # tips lable
        self.container_widgets["repeat_label_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["repeat_label_hbox"].pack_start(
            self.__make_align(self.image_widgets["repeat"], xalign=0.0, height=-1), False, False)
        self.container_widgets["repeat_label_hbox"].pack_start(
            self.label_widgets["repeat"], False, False)
        # repeat delay
        value = self.adjust_widgets["repeat_delay"].get_upper() + self.adjust_widgets["repeat_delay"].get_lower() - settings.keyboard_get_repeat_delay()
        self.scale_widgets["repeat_delay"].set_value(value)
        self.scale_widgets["repeat_delay"].add_mark(
            self.adjust_widgets["repeat_delay"].get_lower(), gtk.POS_BOTTOM, _("Long"))
        self.scale_widgets["repeat_delay"].add_mark(
            self.adjust_widgets["repeat_delay"].get_upper(), gtk.POS_BOTTOM, _("Short"))
        self.scale_widgets["repeat_delay"].set_size_request(HSCALEBAR_WIDTH, -1)
        # table attach
        self.container_widgets["repeat_table"].set_col_spacings(WIDGET_SPACING)
        #self.container_widgets["repeat_table"].set_row_spacing(0, TABLE_ROW_SPACING)
        self.container_widgets["repeat_table"].attach(
            self.__make_align(self.label_widgets["repeat_delay"], yalign=0.5, yscale=0.0, width=STANDARD_LINE), 0, 1, 0, 1, 4)
        self.container_widgets["repeat_table"].attach(
            self.__make_align(self.scale_widgets["repeat_delay"], yalign=0.0, yscale=1.0, height=43), 1, 2, 0, 1, 4)
        # repeat interval
        value = self.adjust_widgets["repeat_interval"].get_upper() + self.adjust_widgets["repeat_interval"].get_lower() - settings.keyboard_get_repeat_interval()
        self.scale_widgets["repeat_interval"].set_value(value)
        self.scale_widgets["repeat_interval"].add_mark(
            self.adjust_widgets["repeat_interval"].get_lower(), gtk.POS_BOTTOM, _("Slow"))
        self.scale_widgets["repeat_interval"].add_mark(
            self.adjust_widgets["repeat_interval"].get_upper(), gtk.POS_BOTTOM, _("Fast"))
        self.scale_widgets["repeat_interval"].set_size_request(HSCALEBAR_WIDTH, -1)
        # table attach
        self.container_widgets["repeat_table"].attach(
            self.__make_align(self.label_widgets["repeat_interval"], yalign=0.5, yscale=0.0, width=STANDARD_LINE), 0, 1, 1, 2, 4)
        self.container_widgets["repeat_table"].attach(
            self.__make_align(self.scale_widgets["repeat_interval"], yalign=0.0, yscale=1.0, height=43), 1, 2, 1, 2, 4)
        self.container_widgets["repeat_table"].attach(
            self.__make_align(self.button_widgets["repeat_test_entry"], xscale=1.0, padding_top=10), 1, 2, 2, 3, 4)
        self.container_widgets["repeat_table"].set_size_request(MAIN_AREA_WIDTH, -1)
        self.button_widgets["repeat_test_entry"].set_size(HSCALEBAR_WIDTH, WIDGET_HEIGHT)

        # blink
        self.alignment_widgets["blink_label"].add(self.container_widgets["blink_label_hbox"])
        self.alignment_widgets["blink_table"].add(self.container_widgets["blink_table"])
        self.alignment_widgets["blink_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["blink_label"].set_padding(0, 0, TEXT_WINDOW_LEFT_PADDING, 0)
        #self.alignment_widgets["blink_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["blink_table"].set(0.0, 0.5, 0.0, 1.0)
        #self.alignment_widgets["blink_table"].set_padding(0, 0, OPTION_LEFT_PADDING, 0)
        self.container_widgets["blink_main_vbox"].pack_start(
            self.alignment_widgets["blink_label"], False, False)
        self.container_widgets["blink_main_vbox"].pack_start(
            self.__setup_separator(), False, False)
        self.container_widgets["blink_main_vbox"].pack_start(
            self.alignment_widgets["blink_table"])
        # tips lable
        self.container_widgets["blink_label_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["blink_label_hbox"].pack_start(
            self.__make_align(self.image_widgets["blink"], xalign=0.0, height=-1), False, False)
        self.container_widgets["blink_label_hbox"].pack_start(
            self.label_widgets["blink"], False, False)
        # blink time

        value = self.adjust_widgets["blink_cursor"].get_upper() + self.adjust_widgets["blink_cursor"].get_lower() - settings.keyboard_get_cursor_blink_time()
        self.scale_widgets["blink_cursor"].set_value(value)
        self.scale_widgets["blink_cursor"].add_mark(
            self.adjust_widgets["blink_cursor"].get_lower(), gtk.POS_BOTTOM, _("Slow"))
        self.scale_widgets["blink_cursor"].add_mark(
            self.adjust_widgets["blink_cursor"].get_upper(), gtk.POS_BOTTOM, _("Fast"))
        self.scale_widgets["blink_cursor"].set_size_request(HSCALEBAR_WIDTH, -1)
        # table attach
        self.container_widgets["blink_table"].set_col_spacings(WIDGET_SPACING)
        self.container_widgets["blink_table"].attach(
            self.__make_align(self.button_widgets["blink_test_entry"], yalign=0.5, yscale=0.0, width=STANDARD_LINE), 0, 1, 0, 1, 4)
        self.container_widgets["blink_table"].attach(
            self.__make_align(self.scale_widgets["blink_cursor"], yalign=0.0, yscale=1.0, height=43), 1, 2, 0, 1, 4)
        self.container_widgets["blink_table"].set_size_request(MAIN_AREA_WIDTH, -1)

        # touchpad
        self.container_widgets["touchpad_label_hbox0"] = gtk.HBox(False)
        self.alignment_widgets["touchpad_label"].add(self.container_widgets["touchpad_label_hbox0"])
        self.alignment_widgets["touchpad_label"].set(0.0, 0.5, 0.0, 0.0)
        self.alignment_widgets["touchpad_label"].set_padding(0, 0, TEXT_WINDOW_LEFT_PADDING, 0)
        #self.alignment_widgets["touchpad_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["touchpad_label"].set_size_request(
            STANDARD_LINE+WIDGET_SPACING+HSCALEBAR_WIDTH-TEXT_WINDOW_LEFT_PADDING, -1)
        if settings.is_has_touchpad():
            self.container_widgets["touchpad_main_vbox"].pack_start(
                self.alignment_widgets["touchpad_label"])
        # tips lable
        tmp_align = self.__make_align()
        tmp_align.set(0.0, 0.0, 1.0, 0.0)
        self.container_widgets["touchpad_label_hbox0"].pack_start(self.container_widgets["touchpad_label_hbox"], False, False)
        self.container_widgets["touchpad_label_hbox0"].pack_start(tmp_align)
        self.container_widgets["touchpad_label_hbox"].set_size_request(
            STANDARD_LINE+WIDGET_SPACING+HSCALEBAR_WIDTH-TEXT_WINDOW_LEFT_PADDING, -1)
        self.container_widgets["touchpad_label_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["touchpad_label_hbox"].pack_start(
            self.__make_align(self.image_widgets["touchpad"]), False, False)
        self.container_widgets["touchpad_label_hbox"].pack_start(
            self.label_widgets["touchpad"], False, False)
        self.container_widgets["touchpad_label_hbox"].pack_start(
            self.__make_align(self.button_widgets["touchpad_disable"], xalign=1.0, xscale=0.0), True, True)
        self.button_widgets["touchpad_disable"].set_active(
            settings.keyboard_get_disable_touchpad_while_typing())
        
        # relevant setting
        self.container_widgets["right_vbox"].pack_start(
            self.__make_align(self.label_widgets["relevant"], xalign=0.0, yalign=0.0,
                              yscale=1.0, height=-1), False, False)
        self.container_widgets["right_vbox"].pack_start(
            self.alignment_widgets["mouse_setting"], False, False)
        self.container_widgets["right_vbox"].pack_start(
            self.alignment_widgets["touchpad_setting"], False, False)
        self.container_widgets["right_vbox"].pack_start(self.__make_align())
        self.alignment_widgets["mouse_setting"].add(self.button_widgets["mouse_setting"])
        self.alignment_widgets["touchpad_setting"].add(self.button_widgets["touchpad_setting"])
        self.alignment_widgets["mouse_setting"].set(0.0, 0.5, 0.0, 0.0)
        self.alignment_widgets["touchpad_setting"].set(0.0, 0.5, 0.0, 0.0)
        self.alignment_widgets["mouse_setting"].set_padding(15, 15, 0, 0)
        self.alignment_widgets["mouse_setting"].set_size_request(-1, -1)
        self.alignment_widgets["touchpad_setting"].set_size_request(-1, -1)
        #self.alignment_widgets["mouse_setting"].set_padding(0, 0, 10, 0)
        #self.alignment_widgets["touchpad_setting"].set_padding(0, 0, 10, 0)

        ###################################
        # layout set
        self.container_widgets["layout_vbox"].pack_start(
            self.alignment_widgets["layout_label"], False, False)
        self.container_widgets["layout_vbox"].pack_start(
            self.__setup_separator(), False, False)
        self.container_widgets["layout_vbox"].pack_start(
            self.alignment_widgets["layout_table"])

        self.alignment_widgets["layout_label"].add(self.container_widgets["layout_label_hbox"])
        self.alignment_widgets["layout_table"].add(self.container_widgets["layout_table"])
        self.alignment_widgets["layout_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["layout_label"].set_padding(0, 0, TEXT_WINDOW_LEFT_PADDING, 0)
        #self.alignment_widgets["layout_table"].set_padding(0, 0, TEXT_WINDOW_LEFT_PADDING+OPTION_LEFT_PADDING, 0)

        self.container_widgets["layout_label_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["layout_label_hbox"].pack_start(
            self.image_widgets["layout"], False, False)
        self.container_widgets["layout_label_hbox"].pack_start(
            self.label_widgets["layout"], False, False)
        # table attach
        #self.container_widgets["layout_table"].set_size_request(STANDARD_LINE+HSCALEBAR_WIDTH-TEXT_WINDOW_LEFT_PADDING-OPTION_LEFT_PADDING, -1)
        self.container_widgets["layout_table"].set_col_spacings(WIDGET_SPACING)
        layout_align = self.__make_align(self.label_widgets["layout_current_layout"],
            width=STANDARD_LINE+HSCALEBAR_WIDTH-self.button_widgets["layout_add"].get_size_request()[0])
        self.container_widgets["layout_table"].attach(
            layout_align, 0, 1, 0, 1, 4)
        self.container_widgets["layout_table"].attach(
            self.__make_align(self.button_widgets["layout_add"]), 1, 2, 0, 1, 4)
        # layout toolbar
        # init layout selected treeview
        current_variants = self.xkb.get_current_variants_description()
        for name in current_variants:
            if name and name[0]:
                try:
                    layout_name = markup_escape_text(name[0])
                except:
                    layout_name = " "
                self.label_widgets['layout_current_layout'].set_text(_("Current Layout: %s") % layout_name)
                break

        #############################
        # shortcuts set
        self.container_widgets["shortcuts_main_hbox"].pack_start(
            self.alignment_widgets["shortcuts_table"])
        self.alignment_widgets["shortcuts_table"].add(
            self.container_widgets["shortcuts_table"])
        self.view_widgets["shortcuts_selected"].set_size_request(190, -1)
        self.container_widgets["shortcuts_swin"].set_size_request(590, -1)
        self.alignment_widgets["shortcuts_table"].set(0.0, 0.0, 1, 1)
        self.alignment_widgets["shortcuts_table"].set_padding(10, 0, 0, 0)
        # shortcut toolbar
        self.container_widgets["shortcuts_toolbar_hbox"].set_spacing(WIDGET_SPACING)
        #self.container_widgets["shortcuts_toolbar_hbox"].pack_start(self.button_widgets["shortcuts_add"])
        #self.container_widgets["shortcuts_toolbar_hbox"].pack_start(self.button_widgets["shortcuts_remove"])

        # table attach
        self.container_widgets["shortcuts_table"].attach(
            self.__make_align(self.view_widgets["shortcuts_selected"], yalign=1.0, yscale=1.0,
            padding_top=2, padding_bottom=2, padding_right=2), 0, 1, 0, 2)
        self.container_widgets["shortcuts_table"].attach(
            self.__make_align(self.container_widgets["shortcuts_swin"], yalign=0.0, yscale=1.0,
            padding_top=2, padding_bottom=2, padding_left=2, padding_right=7), 1, 2, 0, 2, xpadding=4)
        #self.container_widgets["shortcuts_table"].attach(
            #self.__make_align(self.container_widgets["shortcuts_toolbar_hbox"], xalign=1.0, xscale=0.0,
            #padding_right=15), 1, 2, 1, 2, 5, 0)
        # init shortcuts selected treeview
        self.view_widgets["shortcuts_selected"].add_items([SelectItem(_('System'))])
        self.view_widgets["shortcuts_selected"].add_items([SelectItem(_('Sound and Media'))])
        self.view_widgets["shortcuts_selected"].add_items([SelectItem(_('Windows'))])
        self.view_widgets["shortcuts_selected"].add_items([SelectItem(_('Workspace'))])
        self.view_widgets["shortcuts_selected"].add_items([SelectItem(_('Custom Shortcuts'))])
        self.view_widgets["shortcuts_selected"].set_data("is_custom", False)
        self.view_widgets["shortcuts_selected"].set_expand_column(0)
        self.button_widgets["shortcuts_remove"].set_sensitive(False)
        self.__make_accel_page()

    def __signals_connect(self):
        ''' widget signals connect'''
        ##################################
        # redraw container background white
        self.alignment_widgets["notebook"].connect("expose-event", self.draw_background)
        self.container_widgets["type_main_hbox"].connect("expose-event", self.draw_background)
        self.container_widgets["layout_main_hbox"].connect("expose-event", self.draw_background)
        self.container_widgets["shortcuts_main_hbox"].connect("expose-event", self.draw_background)
        self.container_widgets["tab_box"].connect("switch-tab", self.on_tab_box_switch_tab_cb)
        # typing widget signal
        # repeat delay
        self.settings.connect("changed", self.keyboard_setting_changed_cb)
        self.settings1.connect("changed", self.desktop_setting_changed_cb)
        self.settings2.connect("changed", self.touchpad_setting_changed_cb)
        self.scale_widgets["repeat_delay"].connect(
            "button-release-event", self.scalebar_value_changed, "delay")
        # repeat interval
        self.scale_widgets["repeat_interval"].connect(
            "button-release-event", self.scalebar_value_changed, "repeat-interval")
        #self.button_widgets["repeat_test_entry"].get_parent().connect("expose-event", self.repeat_entry_expose)
        #self.button_widgets["repeat_test_entry"].connect("expose-event", self.repeat_entry_expose)
        self.button_widgets["repeat_test_entry"].entry.connect("focus-in-event", self.repeat_entry_focus_in_entry)
        self.button_widgets["repeat_test_entry"].entry.connect("focus-out-event", self.repeat_entry_focus_out_entry)
        # blink
        self.scale_widgets["blink_cursor"].connect(
            "button-release-event", self.scalebar_value_changed, "cursor-blink-time")
        # touchpad disable 
        self.button_widgets["touchpad_disable"].connect("toggled", self.disable_while_typing_set)
        # adjustment widget
        self.adjust_widgets["repeat_delay"].connect("value-changed",
            lambda w: self.scale_widgets["repeat_delay"].set_value(
                self.adjust_widgets["repeat_delay"].get_value()))
        self.adjust_widgets["repeat_interval"].connect("value-changed",
            lambda w: self.scale_widgets["repeat_interval"].set_value(
                self.adjust_widgets["repeat_interval"].get_value()))
        self.adjust_widgets["blink_cursor"].connect("value-changed",
            lambda w: self.scale_widgets["blink_cursor"].set_value(
                self.adjust_widgets["blink_cursor"].get_value()))
        
        # relevant setting
        self.button_widgets["mouse_setting"].connect("button-press-event", self.relevant_press, "mouse")
        self.button_widgets["touchpad_setting"].connect("button-press-event", self.relevant_press, "touchpad")
        set_clickable_cursor(self.button_widgets["mouse_setting"])
        set_clickable_cursor(self.button_widgets["touchpad_setting"])
        ########################
        # layout widget signal
        # toolbutton
        self.button_widgets["layout_add"].connect("clicked",
            lambda b: self.__create_add_layout_dialog())
        settings.XKB_KEYBOARS_SETTINGS.connect("changed", self.xkb_keyboard_setting_changed_cd)
        ########################
        # shortcuts widget signal
        self.container_widgets["shortcuts_table"].connect("expose-event", self.shortcuts_table_expose)
        self.view_widgets["shortcuts_selected"].connect("select", self.shortcuts_treeview_selecte)
        self.view_widgets["shortcuts_selected"].set_select_rows([0])
        self.button_widgets["shortcuts_remove"].connect("clicked", self.__remove_shortcuts_item)
        self.button_widgets["shortcuts_add"].connect("clicked", lambda b: self.__add_shortcuts_item())

        self.button_widgets["set_to_default"].connect("clicked", self.set_to_default)
    
    ######################################
    def draw_background(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))
        cr.rectangle(x, y, w, h)
        cr.fill()
    
    def on_tab_box_switch_tab_cb(self, widget, index):
        if index == 0:
            self.container_widgets["statusbar"].set_buttons([self.button_widgets["set_to_default"]])
        elif index == 1:
            self.container_widgets["statusbar"].set_buttons(
                [self.button_widgets["shortcuts_add"]])

    def keyboard_setting_changed_cb(self, key):
        args = [self.settings, key]
        if key == 'delay':
            callback = self.settings_value_changed
            args.append(self.adjust_widgets["repeat_delay"])
        elif key == 'repeat-interval':
            callback = self.settings_value_changed
            args.append(self.adjust_widgets["repeat_interval"])
        else:
            return
        callback(*args)
    
    def desktop_setting_changed_cb(self, key):
        args = [self.settings1, key]
        if key == 'cursor-blink-time':
            self.button_widgets["blink_test_entry"].update_time(self.scale_get[key]())
            callback = self.settings_value_changed
            args.append(self.adjust_widgets["blink_cursor"])
        else:
            return
        callback(*args)

    def touchpad_setting_changed_cb(self, key):
        args = [key]
        if key == 'disable-while-typing':
            callback = self.disable_while_typing_change
        else:
            return
        callback(*args)

    # typing widget callback
    def disable_while_typing_set(self, button):
        ''' set left-handed '''
        print "disable while typing:", button.get_active(), button.get_data("changed-by-other-app")
        #if button.get_data("changed-by-other-app"):
            #button.set_data("changed-by-other-app", False)
            #return
        settings.keyboard_set_disable_touchpad_while_typing(
            button.get_active())
        if button.get_active():
            self.set_status_text(_("Disabled touchpad while typing"))
        else:
            self.set_status_text(_("Enabled touchpad while typing"))
    
    def disable_while_typing_change(self, key):
        ''' set left or right radio button active '''
        self.button_widgets["touchpad_disable"].set_data("changed-by-other-app", True)
        self.button_widgets["touchpad_disable"].set_active(
            settings.keyboard_get_disable_touchpad_while_typing())
    
    def scalebar_value_changed(self, widget, event, key):
        '''adjustment value changed, and settings set the value'''
        if widget.get_data("changed-by-other-app"):
            widget.set_data("changed-by-other-app", False)
            return
        value = widget.value_max - widget.value + widget.value_min
        self.scale_set[key](value)
    
    def settings_value_changed(self, settings, key, adjustment):
        '''settings value changed, and adjustment set the value'''
        value = adjustment.get_upper() + adjustment.get_lower() - self.scale_get[key]()
        adjustment.set_value(value)
        adjustment.set_data("changed-by-other-app", True)

    def repeat_entry_focus_in_entry(self, widget, event):
        self.button_widgets["repeat_test_entry"].entry.set_buffer(self.button_widgets["repeat_entry_buffer"])

    def repeat_entry_focus_out_entry(self, widget, event):
        if not self.button_widgets["repeat_entry_buffer"].get_text():
            self.button_widgets["repeat_test_entry"].entry.set_buffer(self.button_widgets["repeat_entry_buffer2"])

    def repeat_entry_expose(self, widget, event):
        text = widget.get_text()
        layout = widget.get_layout()
        if text == "" and not widget.is_focus():
            layout.set_text(_("Test Repeat Interval"))
        elif layout.get_text() != text:
            layout.set_text("")
    
    def relevant_press(self, widget, event, action):
        '''relevant button pressed'''
        self.module_frame.send_message("goto", (action, ""))

    ######################################
    # layout widget callback
    def layout_table_expose(self, table, event):
        ''' layout table expose '''
        cr = table.window.cairo_create()
        x, y, w, h = table.allocation
        x1, y1, w1, h1 = self.container_widgets["layout_swindow"].allocation
        x2, y2, w2, h2 = self.alignment_widgets["layout_button_hbox"].allocation
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
            cr.set_line_width(1)
            cr.rectangle(x, y, w1+1, h)
            cr.move_to(x2, y2-2)
            cr.line_to(x2+w2, y2-2)
            cr.stroke()
    
    ######
    # layout create dailog
    def __create_add_layout_dialog(self):
        def entry_changed(entry, value, treeview):
            treeview.add_items(xkb.search_layout_treeitems(
                layout_treetimes, value), None, True)
        
        def treeview_select(tv, item, row, button):
            layouts, variants = xkb.get_treeview_layout_variants(
                self.view_widgets["layout_selected"])
            #layouts = self.xkb.get_current_layouts()
            #variants = self.xkb.get_current_variants()
            if not variants:
                variants = [''] * len(layouts)
            if item.layout in layouts and item.variants in variants:
                if button.get_sensitive():
                    button.set_sensitive(False)
            elif not button.get_sensitive():
                button.set_sensitive(True)

        def add_layout(treeview, dialog):
            if not treeview.select_rows:
                return
            select_row = treeview.select_rows[0]
            item = treeview.visible_items[select_row]
            layout = item.layout
            variants = item.variants
            if variants:
                l_str = "%s\t%s" % (layout, variants)
            else:
                l_str = "%s" % (layout)
            layout_list = []
            layout_list.append(l_str)
            settings.xkb_set_layouts(layout_list)
            dialog.destroy()
            self.set_status_text(_("Current Layout is: %s") % item.name)
        self.button_widgets["layout_add"].set_sensitive(False)
        dialog_width = 400
        dialog_heigth = 380
        dialog = DialogBox(_("Select an input source to add"), dialog_width, dialog_heigth, DIALOG_MASK_SINGLE_PAGE)
        dialog.connect("destroy", lambda w: self.button_widgets["layout_add"].set_sensitive(True))
        dialog.set_keep_above(True)
        #dialog.set_modal(True)
        dialog.body_align.set_padding(0, 0, 10, 10)
        layout_treetimes = map(lambda item: LayoutItem(*item), self.__layout_items)
        layout_add_treeview = TreeView(layout_treetimes, enable_hover=False)
        layout_add_treeview.set_expand_column(0)
        # search input
        entry = InputEntry()
        entry.set_size(dialog_width-30, 25)
        
        dialog.body_box.pack_start(layout_add_treeview)
        dialog.body_box.pack_start(entry, False, False, 5)
        
        add_button = Button(_("Replace"))
        #add_button.set_sensitive(False)
        cancel_button = Button(_("Cancel"))
        dialog.right_button_box.set_buttons([cancel_button, add_button])
        # signal 
        entry.entry.connect("changed", entry_changed, layout_add_treeview)
        cancel_button.connect("clicked", lambda w: dialog.destroy())
        add_button.connect("clicked", lambda w: add_layout(layout_add_treeview, dialog))
        #layout_add_treeview.connect("select", treeview_select, add_button)
        dialog.show_all()
    
    def xkb_keyboard_setting_changed_cd(self, key):
        if key == 'layouts':
            layouts = settings.xkb_get_layouts()
            if layouts:
                variants = layouts[0].split('\t')
                if len(variants) > 1:
                    descript = self.xkb.get_variants_description(variants[1], variants[0])
                else:
                    descript = self.xkb.get_variants_description('', variants[0])
                self.label_widgets['layout_current_layout'].set_text(_("Current Layout: %s") % markup_escape_text(descript))
            else:
                mutex = threading.Lock()
                t = threading.Thread(target=self.xkb_keyboard_setting_changed_thread, args=(mutex,))
                t.setDaemon(True)
                t.start()

    def xkb_keyboard_setting_changed_thread(self, mutex):
        mutex.acquire()
        sleep(2)
        self.xkb.update_current_config()
        current_variants = self.xkb.get_current_variants_description()
        for name in current_variants:
            if name and name[0]:
                try:
                    layout_name = markup_escape_text(name[0])
                except:
                    layout_name = " "
                gtk.gdk.threads_enter()
                self.label_widgets['layout_current_layout'].set_text(_("Current Layout: %s") % layout_name)
                gtk.gdk.threads_leave()
                break
        mutex.release()
    
    ######################################
    # shortcuts widget callback
    def shortcuts_table_expose(self, table, event):
        cr = table.window.cairo_create()
        x, y, w, h = table.allocation
        left_rect = self.view_widgets["shortcuts_selected"].allocation
        x1 = left_rect.x - 1
        y1 = left_rect.y - 1
        w1 = left_rect.width + 2
        h1 = left_rect.height + 2
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
            cr.set_line_width(1)
            cr.move_to(x1+w1, y1)
            cr.line_to(x1+w1, y1+h1)
            cr.stroke()
    
    def shortcuts_treeview_selecte(self, tree_view, item, row_index):
        self.button_widgets["shortcuts_remove"].set_sensitive(False)
        container_remove_all(self.container_widgets["shortcuts_swin"])
        self.container_widgets["shortcuts_swin"].add(self.__shortcuts_entries_page_widgets[item.text])
        if row_index == len(tree_view.visible_items)-1:
            tree_view.set_data('is_custom', True)
        else:
            tree_view.set_data('is_custom', False)
        self.container_widgets["shortcuts_swin"].show_all()
    
    def __remove_shortcuts_item(self, button):
        gconf_dir = button.settings_key
        settings.GCONF_CLIENT.unset('%s/action' % gconf_dir)
        settings.GCONF_CLIENT.unset('%s/binding' % gconf_dir)
        settings.GCONF_CLIENT.unset('%s/name' % gconf_dir)
        button.get_parent().get_parent().destroy()
        self.set_status_text(_("Deleted custom hotkey"))
    
    def __add_shortcuts_item(self):
        last_row = len(self.view_widgets["shortcuts_selected"].visible_items) - 1
        self.view_widgets["shortcuts_selected"].set_select_rows([last_row])
        self.button_widgets["shortcuts_add"].set_sensitive(False)
        self.__edit_custom_shortcuts_dilaog()
    
    def on_accel_entry_changed_cb(self, widget, key_name):
        accel_str = widget.accel_buffer.get_accel_label()
        if not accel_str:
            text = _("Disabled hotkey for %s") % widget.settings_description
        else:
            text = _("The hotkey for %s is set to %s") % (widget.settings_description, accel_str)
        self.set_status_text(text)

    def on_accel_entry_wait_key_cb(self, widget, s):
        self.set_status_text("%s" % (_("Please input new shortcuts. Press Esc to cancle or press Backspace to clear.")))

    def __edit_custom_shortcuts_dilaog(self, is_edit=False):
        '''
        create a dialog to edit custom shortcuts
        @param is_edit: if True it will edit an exist item, else it will create an item.
        '''
        def dialog_respone(button, name_entry, action_entry, dialog):
            name = name_entry.entry.get_text()
            action = action_entry.entry.get_text()
            if not name and not action:
                dialog.destroy()
                return
            base_dir = '/desktop/gnome/keybindings'
            i = 0
            while True:
                key_dir = "%s%d" % ('custom', i)
                if not settings.GCONF_CLIENT.dir_exists('%s/%s' % (base_dir, key_dir)):
                    break
                i += 1
            settings.shortcuts_custom_set(key_dir, (action, '', name))
            entry = AccelEntry("", keybind_mk.check_shortcut_conflict, can_del=True)
            entry.connect("accel-key-change", self.on_accel_entry_changed_cb)
            entry.connect("wait-key-input", self.on_accel_entry_wait_key_cb)
            entry.connect("accel-del", self.__remove_shortcuts_item)
            entry.settings_description = name
            entry.settings_key = '%s/%s' % (base_dir, key_dir)
            entry.settings_obj = settings.GCONF_CLIENT
            entry.settings_type = entry.TYPE_GCONF
            entry.settings_value_type = entry.TYPE_STRING
            keybind_mk.ACCEL_ENTRY_LIST.append(entry)
            shortcut_vbox = self.container_widgets["shortcuts_swin"].get_children()[0].get_children()[0].get_children()[0]
            hbox = gtk.HBox(False)
            hbox.set_spacing(TEXT_WINDOW_RIGHT_WIDGET_PADDING)
            description_label = Label(entry.settings_description, text_x_align=pango.ALIGN_RIGHT,
                                      enable_select=False, enable_double_click=False)
            description_label.set_size_request(self.max_label_width+30, description_label.get_size_request()[1])
            label_align = self.__make_align(description_label)
            label_align.set_size_request(self.max_label_width+30, CONTAINNER_HEIGHT)
            hbox.pack_start(label_align, False, False)
            hbox.pack_start(self.__make_align(entry), False, False)
            hbox.pack_start(self.__make_align())
            shortcut_vbox.pack_start(hbox, False, False)
            shortcut_vbox.show_all()
            dialog.destroy()
            self.set_status_text(_("Add custom hotkey"))
        self.container_widgets["shortcuts_toolbar_hbox"].set_sensitive(False)
        dialog = DialogBox(_("Custom Shortcuts"), 250, 150, DIALOG_MASK_SINGLE_PAGE)
        dialog.connect("destroy", lambda w: self.button_widgets["shortcuts_add"].set_sensitive(True))
        dialog.set_keep_above(True)
        #dialog.set_modal(True)
        dialog.body_align.set_padding(15, 10, 10, 10)
        
        table = gtk.Table(2, 2, False)
        name_lable = Label(_("name"), enable_select=False, enable_double_click=False)
        name_lable.set_can_focus(False)
        action_lable = Label(_("action"), enable_select=False, enable_double_click=False)
        action_lable.set_can_focus(False)
        name_entry = InputEntry()
        action_entry = InputEntry()

        name_entry.set_size(150, 25)
        action_entry.set_size(150, 25)
        table.attach(name_lable, 0, 1, 0, 1, 5, 0)
        table.attach(name_entry, 1, 2, 0, 1, 5, 0)
        table.attach(action_lable, 0, 1, 1, 2, 5, 0)
        table.attach(action_entry, 1, 2, 1, 2, 5, 0)
        table.set_row_spacing(0, 10)
        table.set_row_spacing(1, 10)
        button = Button(_("Ok"))
        dialog.body_box.pack_start(table)
        dialog.right_button_box.set_buttons([button])
        # signal
        button.connect("clicked", dialog_respone, name_entry, action_entry, dialog)
        dialog.show_all()
    
    def __make_align(self, widget=None, xalign=1.0, yalign=0.5, xscale=0.0,
                     yscale=0.0, padding_top=0, padding_bottom=0, padding_left=0,
                     padding_right=0, width=-1, height=CONTAINNER_HEIGHT):
        align = gtk.Alignment()
        align.set_size_request(width, height)
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
        return self.__make_align(self.__make_separator(), xalign=0.0, xscale=0.0,
                                 padding_top=10,# padding_bottom=10,
                                 padding_left=TEXT_WINDOW_LEFT_PADDING, height=-1)
    
    def __make_accel_page(self):
        self.max_label_width = 0
        label_align_list = []
        for category in self.__shortcuts_entries:
            vbox = gtk.VBox(False)
            self.__shortcuts_entries_page_widgets[category] = ScrolledWindow()
            self.__shortcuts_entries_page_widgets[category].add_child(vbox)
            vbox.set_size_request(570, -1)
            vbox.connect("expose-event", self.draw_background)
            for entry in self.__shortcuts_entries[category]:
                hbox = gtk.HBox(False)
                hbox.set_spacing(TEXT_WINDOW_RIGHT_WIDGET_PADDING)
                description_label = Label(entry.settings_description, text_x_align=pango.ALIGN_RIGHT,
                                          enable_select=False, enable_double_click=False)
                #description_label.set_size_request(description_label.get_size_request()[0]+10, description_label.get_size_request()[1])
                self.max_label_width = max(self.max_label_width, description_label.get_size_request()[0])
                label_align = self.__make_align(description_label)
                label_align_list.append(label_align)
                hbox.pack_start(label_align, False, False)
                hbox.pack_start(self.__make_align(entry), False, False)
                hbox.pack_start(self.__make_align())
                vbox.pack_start(hbox, False, False)
                entry.connect("accel-key-change", self.on_accel_entry_changed_cb)
                entry.connect("wait-key-input", self.on_accel_entry_wait_key_cb)
        for label_align in label_align_list:
            label_align.set_size_request(self.max_label_width+30, CONTAINNER_HEIGHT)
            l = label_align.get_child()
            l.set_size_request(self.max_label_width+30, l.get_size_request()[1])

    def get_accel_page(self):
        return self.__shortcuts_entries_page_widgets
    
    def show_again(self):
        if self.container_widgets["tab_box"].tab_index != 0:
            self.container_widgets["tab_box"].switch_content(0)
            self.on_tab_box_switch_tab_cb(self.container_widgets["tab_box"], 0)

    def set_status_text(self, text):
        self.container_widgets["statusbar"].set_text(text)

    def set_to_default(self, button):
        '''set to the default'''
        if self.container_widgets["tab_box"].tab_index == 0:
            settings.keyboard_set_to_default()
            settings.xkb_set_to_default()
            self.set_status_text(_("Reset to default"))
        elif self.container_widgets["tab_box"].tab_index == 1:
            pass
    
if __name__ == '__main__':
    gtk.gdk.threads_init()
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    key_settings = KeySetting(module_frame)
    
    #module_frame.add(key_settings.alignment_widgets["notebook"])
    module_frame.add(key_settings.container_widgets["main_vbox"])
    
    if len(sys.argv) > 1:
        print "module_uid:", sys.argv[1]
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            print "DEBUG show_again module_uid", message_content
            module_frame.send_module_info()
            key_settings.show_again()
        elif message_type == "exit":
            module_frame.exit()

    module_frame.module_message_handler = message_handler        
    
    module_frame.run()
