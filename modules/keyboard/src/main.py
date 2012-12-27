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
from dtk.ui.utils import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from theme import app_theme

import settings

from dtk.ui.theme import ui_theme
from dtk.ui.dialog import DialogBox
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.label import Label
from dtk.ui.button import Button, OffButton
from dtk.ui.new_entry import InputEntry
from dtk.ui.tab_window import TabBox
from dtk.ui.scalebar import HScalebar
from dtk.ui.box import ImageBox
from dtk.ui.utils import cairo_disable_antialias, color_hex_to_cairo, set_clickable_cursor
from treeitem import (SelectItem, LayoutItem,
                      AccelBuffer, ShortcutItem)
from treeitem import MyTreeView as TreeView
from nls import _
import xkb
import gtk
import shortcuts
import pangocairo
import pango
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
        self.__shortcuts_items = shortcuts.get_shortcuts_wm_shortcut_item(settings.WM_SHORTCUTS_SETTINGS)
        media_shortcuts = shortcuts.get_shortcuts_media_shortcut_item(settings.SHORTCUTS_SETTINGS)
        for shortcut in media_shortcuts:
            self.__shortcuts_items[shortcut] = media_shortcuts[shortcut]
        self.__shortcuts_items[_('Custom Shortcuts')] = shortcuts.get_shortcuts_custom_shortcut_item(settings.GCONF_CLIENT)
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
        option_item_font_szie = CONTENT_FONT_SIZE

        #####################################
        # Typing widgets create
        # image init
        self.image_widgets["repeat"] = ImageBox(app_theme.get_pixbuf("%s/repeat.png" % MODULE_NAME))
        self.image_widgets["blink"] = ImageBox(app_theme.get_pixbuf("%s/blink.png" % MODULE_NAME))
        self.image_widgets["touchpad"] = ImageBox(app_theme.get_pixbuf("%s/typing.png" % MODULE_NAME))
        # label init
        self.label_widgets["repeat"] = Label(_("Repeat"), text_size=title_item_font_size)
        self.label_widgets["repeat_delay"] = Label(_("Repeat Delay"), text_size=option_item_font_szie)
        self.label_widgets["repeat_interval"] = Label(_("Repeat Interval"), text_size=option_item_font_szie)
        self.label_widgets["repeat_fast"] = Label(_("Fast"))
        self.label_widgets["repeat_slow"] = Label(_("Slow"))
        self.label_widgets["repeat_long"] = Label(_("Long"))
        self.label_widgets["repeat_short"] = Label(_("Short"))
        self.label_widgets["blink"] = Label(_("Cursor Blink"),
            text_size=title_item_font_size)
        self.label_widgets["blink_fast"] = Label(_("Fast"))
        self.label_widgets["blink_slow"] = Label(_("Slow"))
        self.label_widgets["touchpad"] = Label(_("Disable touchpad while typing"),
            text_size=title_item_font_size)

        self.label_widgets["relevant"] = Label(_("Relevant Settings"), text_size=title_item_font_size)
        # button init
        self.button_widgets["repeat_test_entry"] = gtk.Entry()
        self.button_widgets["blink_test_entry"] = gtk.Entry()
        self.button_widgets["touchpad_disable"] = OffButton()
        # relevant settings button
        self.button_widgets["mouse_setting"] = Label("<u>%s</u>" % _("Mouse Setting"),
            text_size=option_item_font_szie, text_color=ui_theme.get_color("link_text"), enable_select=False)
        self.button_widgets["touchpad_setting"] = Label("<u>%s</u>" % _("TouchPad Setting"),
            text_size=option_item_font_szie, text_color=ui_theme.get_color("link_text"), enable_select=False)
        # container init
        self.container_widgets["tab_box"] = TabBox()
        self.container_widgets["tab_box"].draw_title_background = self.draw_tab_title_background
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
        self.scale_widgets["repeat_delay"] = HScalebar(
            None, None, None, None, None, None,
            app_theme.get_pixbuf("scalebar/point.png"))
        self.scale_widgets["repeat_delay"].set_adjustment(self.adjust_widgets["repeat_delay"])
        self.scale_widgets["repeat_interval"] = HScalebar(
            None, None, None, None, None, None,
            app_theme.get_pixbuf("scalebar/point.png"))
        self.scale_widgets["repeat_interval"].set_adjustment(self.adjust_widgets["repeat_interval"])
        self.scale_widgets["blink_cursor"] = HScalebar(
            None, None, None, None, None, None,
            app_theme.get_pixbuf("scalebar/point.png"))
        self.scale_widgets["blink_cursor"].set_adjustment(self.adjust_widgets["blink_cursor"])
        #####################################
        # Layout widgets create
        # button init
        self.button_widgets["layout_add"] = Button(_("Add"))
        self.button_widgets["layout_remove"] = Button(_("Remove"))
        # view init
        self.view_widgets["layout_selected"] = TreeView(enable_hover=False)
        # container init
        self.container_widgets["layout_table"] = gtk.Table(2, 3, False)
        self.container_widgets["layout_swindow"] = ScrolledWindow()
        self.container_widgets["layout_button_hbox"] = gtk.HBox(False)
        # alignment init
        self.alignment_widgets["layout_table"] = gtk.Alignment()
        self.alignment_widgets["layout_button_hbox"] = gtk.Alignment()
        #####################################
        # Shortcuts widgets create
        # label init
        self.label_widgets["shortcuts_tips"] = Label(_("To edit a shortcut, click the row and hold down the new keys or press Backspace to clear."))
        # button init
        self.button_widgets["shortcuts_add"] = Button(_("Add"))
        self.button_widgets["shortcuts_remove"] = Button(_("Remove"))
        # view init
        self.view_widgets["shortcuts_selected"] = TreeView(enable_hover=False)
        self.view_widgets["shortcuts_shortcut"] = TreeView(enable_hover=False)
        # container init
        self.container_widgets["shortcuts_table"] = gtk.Table(2, 3, False)
        self.container_widgets["shortcuts_toolbar_hbox"] = gtk.HBox(False)
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
        self.alignment_widgets["notebook"].set(0.0, 0.0, 1, 1)
        #self.alignment_widgets["notebook"].set_padding(FRAME_TOP_PADDING, 0, FRAME_LEFT_PADDING, FRAME_LEFT_PADDING)
        self.alignment_widgets["notebook"].set_padding(FRAME_TOP_PADDING, 0, 0, 0)
        self.alignment_widgets["notebook"].add(self.container_widgets["tab_box"])
        tab_box_item = [
            (_("Typing"), self.container_widgets["type_main_hbox"]),
            (_("Layout"), self.container_widgets["layout_main_hbox"]),
            (_("Shortcuts"), self.container_widgets["shortcuts_main_hbox"])]
        self.container_widgets["tab_box"].add_items(tab_box_item)
        ###########################
        # typing set
        self.container_widgets["type_main_hbox"].set_spacing(MID_SPACING)
        self.container_widgets["type_main_hbox"].pack_start(self.alignment_widgets["left"])
        self.container_widgets["type_main_hbox"].pack_start(self.alignment_widgets["right"], False, False)
        self.alignment_widgets["left"].add(self.container_widgets["left_vbox"])
        self.alignment_widgets["right"].add(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].set_size_request(RIGHT_BOX_WIDTH, -1)
        # set left padding
        self.alignment_widgets["left"].set(0.0, 0.0, 1.0, 1.0)
        self.alignment_widgets["left"].set_padding(35, 0, 50, 0)
        # set right padding
        self.alignment_widgets["right"].set(0.0, 0.0, 0.0, 0.0)
        self.alignment_widgets["right"].set_padding(35, 0, 0, 20)
        
        self.container_widgets["left_vbox"].set_spacing(BETWEEN_SPACING)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["repeat_main_vbox"], False, False)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["blink_main_vbox"], False, False)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["touchpad_main_vbox"], False, False)
        # set option label width
        label_widgets = self.label_widgets
        label_width = max(
            label_widgets["repeat_delay"].size_request()[0],
            label_widgets["repeat_interval"].size_request()[0]) + 2
        label_widgets["repeat_delay"].set_size_request(label_width, WIDGET_HEIGHT)
        label_widgets["repeat_interval"].set_size_request(label_width, WIDGET_HEIGHT)
        self.button_widgets["blink_test_entry"].set_size_request(label_width, WIDGET_HEIGHT)

        # repeat
        self.alignment_widgets["type_label"].add(self.container_widgets["repeat_label_hbox"])
        self.alignment_widgets["type_table"].add(self.container_widgets["repeat_table"])
        # alignment set
        self.alignment_widgets["type_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["type_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["type_table"].set(0.0, 0.5, 1.0, 1.0)
        self.alignment_widgets["type_table"].set_padding(0, 0, OPTION_LEFT_PADDING, 0)
        self.container_widgets["repeat_main_vbox"].pack_start(
            self.alignment_widgets["type_label"])
        self.container_widgets["repeat_main_vbox"].pack_start(
            self.alignment_widgets["type_table"])
        # tips lable
        self.container_widgets["repeat_label_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["repeat_label_hbox"].pack_start(
            self.__make_align(self.image_widgets["repeat"]), False, False)
        self.container_widgets["repeat_label_hbox"].pack_start(
            self.label_widgets["repeat"], False, False)
        # repeat delay
        value = self.adjust_widgets["repeat_delay"].get_upper() + self.adjust_widgets["repeat_delay"].get_lower() - settings.keyboard_get_repeat_delay()
        self.adjust_widgets["repeat_delay"].set_value(value)
        self.scale_widgets["repeat_delay"].add_mark(self.adjust_widgets["repeat_delay"].get_lower(), gtk.POS_BOTTOM, _("Long"))
        self.scale_widgets["repeat_delay"].add_mark(self.adjust_widgets["repeat_delay"].get_upper(), gtk.POS_BOTTOM, _("Short"))
        self.scale_widgets["repeat_delay"].set_size_request(MAIN_AREA_WIDTH-LABEL_WIDTH, -1)
        # table attach
        self.container_widgets["repeat_table"].set_col_spacings(WIDGET_SPACING)
        self.container_widgets["repeat_table"].set_row_spacing(0, TABLE_ROW_SPACING)
        self.container_widgets["repeat_table"].attach(
            self.__make_align(self.label_widgets["repeat_delay"], yalign=0.0, yscale=0.0), 0, 1, 0, 1, 4)
        self.container_widgets["repeat_table"].attach(
            self.__make_align(self.scale_widgets["repeat_delay"], yalign=0.0, yscale=1.0, padding_top=4, height=43), 1, 2, 0, 1, 4)
        # repeat interval
        value = self.adjust_widgets["repeat_interval"].get_upper() + self.adjust_widgets["repeat_interval"].get_lower() - settings.keyboard_get_repeat_interval()
        self.adjust_widgets["repeat_interval"].set_value(value)
        self.scale_widgets["repeat_interval"].add_mark(self.adjust_widgets["repeat_interval"].get_lower(), gtk.POS_BOTTOM, _("Slow"))
        self.scale_widgets["repeat_interval"].add_mark(self.adjust_widgets["repeat_interval"].get_upper(), gtk.POS_BOTTOM, _("Fast"))
        self.scale_widgets["repeat_interval"].set_size_request(MAIN_AREA_WIDTH-LABEL_WIDTH, -1)
        # table attach
        self.container_widgets["repeat_table"].attach(
            self.__make_align(self.label_widgets["repeat_interval"], yalign=0.0, yscale=0.0), 0, 1, 1, 2, 4)
        self.container_widgets["repeat_table"].attach(
            self.__make_align(self.scale_widgets["repeat_interval"], yalign=0.0, yscale=1.0, padding_top=4, height=43), 1, 2, 1, 2, 4)
        self.container_widgets["repeat_table"].attach(
            self.__make_align(self.button_widgets["repeat_test_entry"]), 1, 2, 2, 3, 4, 0)
        self.container_widgets["repeat_table"].set_size_request(MAIN_AREA_WIDTH, -1)
        self.button_widgets["repeat_test_entry"].set_size_request(-1, WIDGET_HEIGHT)

        # blink
        self.alignment_widgets["blink_label"].add(self.container_widgets["blink_label_hbox"])
        self.alignment_widgets["blink_table"].add(self.container_widgets["blink_table"])
        self.alignment_widgets["blink_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["blink_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["blink_table"].set(0.0, 0.5, 1.0, 1.0)
        self.alignment_widgets["blink_table"].set_padding(0, 0, OPTION_LEFT_PADDING, 0)
        self.container_widgets["blink_main_vbox"].pack_start(
            self.alignment_widgets["blink_label"])
        self.container_widgets["blink_main_vbox"].pack_start(
            self.alignment_widgets["blink_table"])
        # tips lable
        self.container_widgets["blink_label_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["blink_label_hbox"].pack_start(
            self.__make_align(self.image_widgets["blink"]), False, False)
        self.container_widgets["blink_label_hbox"].pack_start(
            self.label_widgets["blink"], False, False)
        # blink time

        value = self.adjust_widgets["blink_cursor"].get_upper() + self.adjust_widgets["blink_cursor"].get_lower() - settings.keyboard_get_cursor_blink_time()
        self.adjust_widgets["blink_cursor"].set_value(value)
        self.scale_widgets["blink_cursor"].add_mark(self.adjust_widgets["blink_cursor"].get_lower(), gtk.POS_BOTTOM, _("Slow"))
        self.scale_widgets["blink_cursor"].add_mark(self.adjust_widgets["blink_cursor"].get_upper(), gtk.POS_BOTTOM, _("Fast"))
        self.scale_widgets["blink_cursor"].set_size_request(MAIN_AREA_WIDTH-LABEL_WIDTH, -1)
        # table attach
        self.container_widgets["blink_table"].set_col_spacings(WIDGET_SPACING)
        self.container_widgets["blink_table"].attach(
            self.__make_align(self.button_widgets["blink_test_entry"], yalign=0.0, yscale=0.0), 0, 1, 0, 1, 4)
        self.container_widgets["blink_table"].attach(
            self.__make_align(self.scale_widgets["blink_cursor"], yalign=0.0, yscale=1.0, padding_top=4, height=43), 1, 2, 0, 1, 4)
        self.container_widgets["blink_table"].set_size_request(MAIN_AREA_WIDTH, -1)

        # touchpad
        self.alignment_widgets["touchpad_label"].add(self.container_widgets["touchpad_label_hbox"])
        self.alignment_widgets["touchpad_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["touchpad_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.container_widgets["touchpad_main_vbox"].pack_start(
            self.alignment_widgets["touchpad_label"])
        # tips lable
        self.container_widgets["touchpad_label_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["touchpad_label_hbox"].pack_start(
            self.__make_align(self.image_widgets["touchpad"]), False, False)
        self.container_widgets["touchpad_label_hbox"].pack_start(
            self.label_widgets["touchpad"], False, False)
        self.container_widgets["touchpad_label_hbox"].pack_start(
            self.__make_align(self.button_widgets["touchpad_disable"]), False, False)
        self.button_widgets["touchpad_disable"].set_active(
            settings.keyboard_get_disable_touchpad_while_typing())
        
        # relevant setting
        self.container_widgets["right_vbox"].pack_start(
            self.__make_align(self.label_widgets["relevant"]))
        self.container_widgets["right_vbox"].pack_start(
            self.alignment_widgets["mouse_setting"])
        self.container_widgets["right_vbox"].pack_start(
            self.alignment_widgets["touchpad_setting"])
        self.alignment_widgets["mouse_setting"].add(self.button_widgets["mouse_setting"])
        self.alignment_widgets["touchpad_setting"].add(self.button_widgets["touchpad_setting"])
        self.alignment_widgets["mouse_setting"].set(0.0, 0.5, 0.0, 0.0)
        self.alignment_widgets["touchpad_setting"].set(0.0, 0.5, 0.0, 0.0)
        self.alignment_widgets["mouse_setting"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["touchpad_setting"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["mouse_setting"].set_padding(0, 0, 10, 0)
        self.alignment_widgets["touchpad_setting"].set_padding(0, 0, 10, 0)

        ###################################
        # layout set
        self.container_widgets["layout_main_hbox"].pack_start(
            self.alignment_widgets["layout_table"])
        self.alignment_widgets["layout_table"].add(
            self.container_widgets["layout_table"])
        self.container_widgets["layout_swindow"].add_child(
            self.view_widgets["layout_selected"])
        self.alignment_widgets["layout_table"].set(0.0, 0.0, 1, 1)
        self.alignment_widgets["layout_table"].set_padding(10, 10, 10, 10)
        # layout toolbar
        self.alignment_widgets["layout_button_hbox"].set(1.0, 0.5, 0, 0)
        self.alignment_widgets["layout_button_hbox"].set_padding(5, 5, 0, 10)
        self.alignment_widgets["layout_button_hbox"].add(self.container_widgets["layout_button_hbox"])
        self.container_widgets["layout_button_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["layout_button_hbox"].pack_start(self.button_widgets["layout_add"])
        self.container_widgets["layout_button_hbox"].pack_start(self.button_widgets["layout_remove"])
        # table attach
        self.container_widgets["layout_table"].attach(
            self.container_widgets["layout_swindow"], 0, 3, 0, 1)
        self.container_widgets["layout_table"].attach(
            self.alignment_widgets["layout_button_hbox"], 0, 3, 1, 2, 5, 0)
        self.container_widgets["layout_table"].set_row_spacing(0, 10)
        # init layout selected treeview
        current_variants = self.xkb.get_current_variants_description()
        name_list = []
        for name in current_variants:
            name_list.append(LayoutItem(*name))
        self.view_widgets["layout_selected"].add_items(name_list)

        #############################
        # shortcuts set
        self.container_widgets["shortcuts_main_hbox"].pack_start(
            self.alignment_widgets["shortcuts_table"])
        self.alignment_widgets["shortcuts_table"].add(
            self.container_widgets["shortcuts_table"])
        self.view_widgets["shortcuts_selected"].set_size_request(150, -1)
        self.view_widgets["shortcuts_shortcut"].set_size_request(600, -1)
        self.alignment_widgets["shortcuts_table"].set(0.0, 0.0, 1, 1)
        self.alignment_widgets["shortcuts_table"].set_padding(10, 10, 10, 10)
        # shortcut toolbar
        self.container_widgets["shortcuts_toolbar_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["shortcuts_toolbar_hbox"].pack_start(self.button_widgets["shortcuts_add"])
        self.container_widgets["shortcuts_toolbar_hbox"].pack_start(self.button_widgets["shortcuts_remove"])

        # table attach
        self.container_widgets["shortcuts_table"].attach(
            self.__make_align(self.view_widgets["shortcuts_selected"], yalign=1.0, yscale=1.0,
            padding_top=2, padding_bottom=2, padding_left=2, padding_right=2), 0, 1, 0, 2)
        self.container_widgets["shortcuts_table"].attach(
            self.__make_align(self.view_widgets["shortcuts_shortcut"], yalign=0.0, yscale=1.0,
            padding_top=2, padding_bottom=2, padding_left=2, padding_right=7), 1, 2, 0, 1, xpadding=4)
        self.container_widgets["shortcuts_table"].attach(
            self.__make_align(self.container_widgets["shortcuts_toolbar_hbox"], xalign=1.0, xscale=0.0,
            padding_right=7), 1, 2, 1, 2, 5, 0)
        self.container_widgets["shortcuts_table"].attach(
            self.__make_align(self.label_widgets["shortcuts_tips"]), 0, 2, 2, 3, 5, 0)
        self.container_widgets["layout_table"].set_col_spacing(1, 25)
        self.container_widgets["layout_table"].set_row_spacing(0, 10)
        # init shortcuts selected treeview
        self.view_widgets["shortcuts_selected"].add_items(
            shortcuts.get_wm_shortcuts_select_item())
        self.view_widgets["shortcuts_selected"].add_items(
            shortcuts.get_media_shortcuts_select_item())
        self.view_widgets["shortcuts_selected"].add_items(
            [SelectItem(_('Custom Shortcuts'))])
        self.view_widgets["shortcuts_shortcut"].add_items(
            self.__shortcuts_items[self.view_widgets["shortcuts_selected"].visible_items[0].text])
        self.view_widgets["shortcuts_selected"].set_data("is_custom", False)
        self.button_widgets["shortcuts_remove"].set_sensitive(False)

    def __signals_connect(self):
        ''' widget signals connect'''
        ##################################
        # redraw container background white
        self.alignment_widgets["notebook"].connect("expose-event", self.container_expose_cb)
        # typing widget signal
        # repeat delay
        self.settings.connect("changed", self.keyboard_setting_changed_cb)
        self.settings1.connect("changed", self.desktop_setting_changed_cb)
        self.settings2.connect("changed", self.touchpad_setting_changed_cb)
        self.scale_widgets["repeat_delay"].connect(
            "button-release-event", self.adjustment_value_changed, "delay")
        # repeat interval
        self.scale_widgets["repeat_interval"].connect(
            "button-release-event", self.adjustment_value_changed, "repeat-interval")
        self.button_widgets["repeat_test_entry"].connect("expose-event", self.repeat_entry_expose)
        # blink
        self.scale_widgets["blink_cursor"].connect(
            "button-release-event", self.adjustment_value_changed, "cursor-blink-time")
        # touchpad disable 
        self.button_widgets["touchpad_disable"].connect("toggled", self.disable_while_typing_set)
        
        # relevant setting
        self.button_widgets["mouse_setting"].connect("button-press-event", self.relevant_press, "mouse")
        self.button_widgets["touchpad_setting"].connect("button-press-event", self.relevant_press, "touchpad")
        set_clickable_cursor(self.button_widgets["mouse_setting"])
        set_clickable_cursor(self.button_widgets["touchpad_setting"])
        ########################
        # layout widget signal
        self.container_widgets["layout_table"].connect("expose-event", self.layout_table_expose)
        # treeview
        self.view_widgets["layout_selected"].connect("select", self.layout_treeview_selecte)
        if len(self.view_widgets["layout_selected"].visible_items) > 0:
            self.view_widgets["layout_selected"].set_select_rows([0])
        # toolbutton
        self.button_widgets["layout_add"].connect("clicked",
            lambda b: self.__create_add_layout_dialog())
        self.button_widgets["layout_remove"].connect("clicked",
            self.layout_remove_button_clicked)
        ########################
        # shortcuts widget signal
        self.container_widgets["shortcuts_table"].connect("expose-event", self.shortcuts_table_expose)
        self.view_widgets["shortcuts_selected"].connect("select", self.shortcuts_treeview_selecte)
        self.view_widgets["shortcuts_shortcut"].connect("select", self.shortcuts_selecte)
        self.view_widgets["shortcuts_shortcut"].add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.view_widgets["shortcuts_shortcut"].connect("single-click-item", self.shortcuts_clicked)
        self.button_widgets["shortcuts_remove"].connect("clicked", self.__remove_shortcuts_item)
        self.button_widgets["shortcuts_add"].connect("clicked", lambda b: self.__add_shortcuts_item())
    
    ######################################
    def container_expose_cb(self, widget, event):
        cr = widget.window.cairo_create()
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                                               
        cr.rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)                                                 
        cr.fill()
    
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
        settings.keyboard_set_disable_touchpad_while_typing(
            button.get_active())
    
    def disable_while_typing_change(self, key):
        ''' set left or right radio button active '''
        self.button_widgets["touchpad_disable"].set_active(
            settings.keyboard_get_disable_touchpad_while_typing())
    
    def adjustment_value_changed(self, widget, event, key):
        '''adjustment value changed, and settings set the value'''
        #print "adjustment value changed:", adjustment, key
        #return
        if widget.get_data("changed-by-other-app"):
            widget.set_data("changed-by-other-app", False)
            return
        adjustment = widget.get_adjustment()
        value = adjustment.get_upper() - adjustment.get_value() + adjustment.get_lower()
        self.scale_set[key](value)
    
    def settings_value_changed(self, settings, key, adjustment):
        '''settings value changed, and adjustment set the value'''
        value = adjustment.get_upper() + adjustment.get_lower() - self.scale_get[key]()
        adjustment.set_value(value)
        adjustment.set_data("changed-by-other-app", True)

    def repeat_entry_expose(self, widget, event):
        text = widget.get_text()
        if text == "" and not widget.is_focus():
            win = widget.get_text_window()
            cr = win.cairo_create()
            cr.move_to(2, 2)
            context = pangocairo.CairoContext(cr)
            layout = context.create_layout()
            layout.set_font_description(pango.FontDescription("Snas 10"))
            layout.set_alignment(pango.ALIGN_LEFT)
            layout.set_text(_("Click here and hold a key to test repeat rate"))
            cr.set_source_rgb(0.66, 0.66, 0.66)
            context.update_layout(layout)
            context.show_layout(layout)
            return True
    
    def relevant_press(self, widget, event, action):
        '''relevant button pressed'''
        self.module_frame.send_message("goto", action)

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
    
    def layout_treeview_selecte(self, tree_view, item, row_index):
        #print "select:", item.name, item.layout, item.variants, row_index
        # set if can click remove
        if len(tree_view.visible_items) == 1\
                and self.button_widgets["layout_remove"].get_sensitive():
            self.button_widgets["layout_remove"].set_sensitive(False)
        elif not self.button_widgets["layout_remove"].get_sensitive():
            self.button_widgets["layout_remove"].set_sensitive(True)
    
    def layout_remove_button_clicked(self, button):
        '''remove selected layout'''
        print "remove button clicked no select row to remove"
        if not self.view_widgets["layout_selected"].select_rows:
            print "no select row to remove"
            return
        layout_treeview = self.view_widgets["layout_selected"]
        select_row = layout_treeview.select_rows[0]
        layout_list = settings.xkb_get_layouts()
        if select_row >= len(layout_list):
            print "selec row out range", layout_list
            return
        del layout_list[select_row]
        settings.xkb_set_layouts(layout_list)
        self.xkb.update_current_config()
        layout_treeview.delete_select_items()
        button.set_sensitive(False)
        if not self.button_widgets["layout_add"].get_sensitive():
            self.button_widgets["layout_add"].set_sensitive(True)
    
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
            self.view_widgets["layout_selected"].add_items([item])
            item.unselect()
            layouts, variants = xkb.get_treeview_layout_variants(
                self.view_widgets["layout_selected"])
            length = len(layouts)
            if not variants:
                variants = [''] * length
            layout_list = []
            i = 0
            while i < length:
                l_str = layouts[i]
                if variants[i]:
                    l_str += '\t%s' % variants[i]
                i += 1
                layout_list.append(l_str)
            settings.xkb_set_layouts(layout_list)
            self.xkb.update_current_config()
            if len(self.view_widgets["layout_selected"].visible_items) > 3\
                    and self.button_widgets["layout_add"].get_sensitive():
                self.button_widgets["layout_add"].set_sensitive(False)
            dialog.destroy()
        self.container_widgets["layout_button_hbox"].set_sensitive(False)
        dialog_width = 400
        dialog_heigth = 380
        dialog = DialogBox(_("Select an input source to add"), dialog_width, dialog_heigth)
        dialog.connect("destroy", lambda w: self.container_widgets["layout_button_hbox"].set_sensitive(True))
        dialog.set_keep_above(True)
        dialog.set_modal(True)
        #dialog.set_transient_for(parent)
        dialog.body_align.set_padding(0, 0, 10, 10)
        layout_treetimes = map(lambda item: LayoutItem(*item), self.__layout_items)
        layout_add_treeview = TreeView(layout_treetimes, enable_hover=False)
        # search input
        entry = InputEntry()
        entry.set_size(dialog_width-30, 25)
        
        dialog.body_box.pack_start(layout_add_treeview)
        dialog.body_box.pack_start(entry, False, False, 5)
        
        add_button = Button(_("Add"))
        add_button.set_sensitive(False)
        cancel_button = Button(_("Cancel"))
        dialog.right_button_box.set_buttons([cancel_button, add_button])
        # signal 
        entry.entry.connect("changed", entry_changed, layout_add_treeview)
        cancel_button.connect("clicked", lambda w: dialog.destroy())
        add_button.connect("clicked", lambda w: add_layout(layout_add_treeview, dialog))
        layout_add_treeview.connect("select", treeview_select, add_button)
        dialog.show_all()
    
    ######################################
    # shortcuts widget callback
    def shortcuts_table_expose(self, table, event):
        cr = table.window.cairo_create()
        x, y, w, h = table.allocation
        left_rect = self.view_widgets["shortcuts_selected"].allocation
        right_rect = self.view_widgets["shortcuts_shortcut"].allocation
        hbox_rect = self.container_widgets["shortcuts_toolbar_hbox"].allocation
        x1 = left_rect.x - 1
        y1 = left_rect.y - 1
        w1 = left_rect.width + 2
        h1 = left_rect.height + 2
        x2 = right_rect.x - 1
        y2 = right_rect.y - 1
        w2 = right_rect.width + 7
        h2 = right_rect.height + 2
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
            cr.set_line_width(1)
            cr.rectangle(x1, y1, w1, h1)
            cr.rectangle(x2, y2, w2, h2+30)
            cr.move_to(x2, y2+h2+1)
            cr.line_to(x2+w2, y2+h2+1)
            cr.stroke()
    
    def shortcuts_treeview_selecte(self, tree_view, item, row_index):
        #print "select:", item.text, row_index
        self.button_widgets["shortcuts_remove"].set_sensitive(False)
        self.view_widgets["shortcuts_shortcut"].set_select_rows([])
        self.view_widgets["shortcuts_shortcut"].add_items(
            self.__shortcuts_items[item.text], clear_first=True)
        if row_index == len(tree_view.visible_items)-1:
            tree_view.set_data('is_custom', True)
        else:
            tree_view.set_data('is_custom', False)
        vadjust = self.view_widgets["shortcuts_shortcut"].scrolled_window.get_vadjustment()
        vadjust.set_value(vadjust.get_lower())
        vadjust.value_changed()
        self.view_widgets["shortcuts_shortcut"].queue_draw()
    
    def shortcuts_selecte(self, tree_view, item, row_index):
        #print "shortcuts select:", item.description, item.keyname, item.name, row_index
        if self.view_widgets["shortcuts_selected"].get_data('is_custom'):
            if not self.button_widgets["shortcuts_remove"].get_sensitive():
                self.button_widgets["shortcuts_remove"].set_sensitive(True)
        else:
            if self.button_widgets["shortcuts_remove"].get_sensitive():
                self.button_widgets["shortcuts_remove"].set_sensitive(False)
    
    def shortcuts_clicked(self, treeview, item, column, *args):
        ''' '''
        if column != item.COLUMN_ACCEL:
            return
        
        def button_press_callback(widget, event, item):
            gtk.gdk.keyboard_ungrab(0)
            gtk.gdk.pointer_ungrab(0)
            widget.destroy()
            item.keyname = item.old_keyname
            item.redraw_request_callback(item)
        
        def key_press_callback(widget, event, item, tv):
            if event.is_modifier:
                return
            
            def cancel_reassign(dialog):
                item.keyname = item.old_keyname
                item.redraw_request_callback(item)
                dialog.destroy()
            
            def reassign_shortcuts(dialog, accel_buf, conflict):
                dialog.destroy()
                item.accel_buffer = accel_buf
                item.update_accel_setting()
                conflict.accel_buffer.set_keyval(0)
                conflict.accel_buffer.set_state(0)
                conflict.update_accel_setting()
                #item.redraw_request_callback(item)
                treeview.queue_draw()
            
            def check_conflict_item(accel_buf):
                for category in self.__shortcuts_items:
                    for items in self.__shortcuts_items[category]:
                        if items != item and items.accel_buffer == accel_buf:
                            return items
                return None
            gtk.gdk.keyboard_ungrab(0)
            gtk.gdk.pointer_ungrab(0)
            widget.destroy()
            tv.draw_area.grab_focus()
            keyval = event.keyval
            state = event.state & (~gtk.gdk.MOD2_MASK)  # ignore MOD2_MASK
            tmp_accel_buf = AccelBuffer()
            tmp_accel_buf.set_keyval(keyval)
            tmp_accel_buf.set_state(state)
            # cancel edit
            if keyval == gtk.keysyms.Escape:
                item.keyname = item.old_keyname
                item.redraw_request_callback(item)
                return
            # clear edit
            if keyval == gtk.keysyms.BackSpace:
                item.accel_buffer.set_keyval(0)
                item.accel_buffer.set_state(0)
                item.update_accel_setting()
                item.redraw_request_callback(item)
                return
            #Check for unmodified keys
            forbidden_keyvals = [
                # Navigation keys
                gtk.keysyms.Home,
                gtk.keysyms.Left,
                gtk.keysyms.Up,
                gtk.keysyms.Right,
                gtk.keysyms.Down,
                gtk.keysyms.Page_Up,
                gtk.keysyms.Page_Down,
                gtk.keysyms.End,
                gtk.keysyms.Tab,
                # Return 
                gtk.keysyms.KP_Enter,
                gtk.keysyms.Return,
                gtk.keysyms.space,
                gtk.keysyms.Mode_switch]
            if (state == 0 or state == gtk.gdk.SHIFT_MASK) and (
                    gtk.keysyms.a <= keyval <= gtk.keysyms.z or
                    gtk.keysyms.A <= keyval <= gtk.keysyms.Z or
                    gtk.keysyms._0 <= keyval <= gtk.keysyms._9 or
                    gtk.keysyms.kana_fullstop <= keyval <= gtk.keysyms.semivoicedsound or
                    gtk.keysyms.Arabic_comma <= keyval <= gtk.keysyms.Arabic_sukun or
                    gtk.keysyms.Serbian_dje <= keyval <= gtk.keysyms.Cyrillic_HARDSIGN or
                    gtk.keysyms.Greek_ALPHAaccent <= keyval <= gtk.keysyms.Greek_omega or
                    gtk.keysyms.hebrew_doublelowline <= keyval <= gtk.keysyms.hebrew_taf or
                    gtk.keysyms.Thai_kokai <= keyval <= gtk.keysyms.Thai_lekkao or
                    gtk.keysyms.Hangul <= keyval <= gtk.keysyms.Hangul_Special or
                    gtk.keysyms.Hangul_Kiyeog <= keyval <= gtk.keysyms.Hangul_J_YeorinHieuh or
                    keyval in forbidden_keyvals):
                dialog = DialogBox(" ", 550, 150)
                dialog.set_keep_above(True)
                dialog.set_modal(True)
                #dialog.set_transient_for(self.container_widgets["window"])
                dialog.body_align.set_padding(15, 10, 10, 10)
                label1 = Label(_("The shortcut \"%s\" cannot be used because it will become impossible to type using this key.")% tmp_accel_buf.get_accel_label())
                label2 = Label(_("Please try with a key such as Control, Alt or Shift at the same time."))
                dialog.body_box.pack_start(label1)
                dialog.body_box.pack_start(label2)
                button = Button(_("Cancel"))
                button.connect("clicked", lambda b: dialog.destroy())
                dialog.right_button_box.set_buttons([button])
                dialog.show_all()
                item.keyname = item.old_keyname
                item.redraw_request_callback(item)
                return
            # check for conflict
            conflict = check_conflict_item(tmp_accel_buf) 
            #print "select item:", item.description, item.name, item.keyname, item.accel_buffer.keyval, item.accel_buffer.state
            #print "conflict item:", conflict.description, conflict.name, conflict.keyname, conflict.accel_buffer.keyval, conflict.accel_buffer.state
            if conflict is not None:
                dialog = DialogBox(" ", 620, 150)
                dialog.set_keep_above(True)
                dialog.set_modal(True)
                #dialog.set_transient_for(self.container_widgets["window"])
                dialog.body_align.set_padding(15, 10, 10, 10)
                label1 = Label(_("The shortcut \"%s\" is already used for\"%s\"")% (tmp_accel_buf.get_accel_label(), conflict.description))
                label2 = Label(_("If you reassign the shortcut to \"%s\", the \"%s\" shortcut will be disabled.")% (item.description, conflict.description))
                dialog.body_box.pack_start(label1)
                dialog.body_box.pack_start(label2)
                button_reassign = Button(_("Reassign"))
                button_cancel = Button(_("Cancel"))
                button_cancel.connect("clicked", lambda b: cancel_reassign(dialog))
                button_reassign.connect("clicked", lambda b: reassign_shortcuts(dialog, tmp_accel_buf, conflict))
                dialog.right_button_box.set_buttons([button_cancel, button_reassign])
                dialog.show_all()
                return
            item.set_accel_buffer_from_event(event)
            item.update_accel_setting()
            item.redraw_request_callback(item)
        item.old_keyname = item.keyname
        item.keyname = _("New accelerator..")
        if item.redraw_request_callback:
            item.redraw_request_callback(item)
        event_box = gtk.EventBox()
        event_box.set_size_request(0, 0)
        treeview.pack_start(event_box, False, False)
        event_box.show_all()
        if gtk.gdk.keyboard_grab(event_box.window, False, 0) != gtk.gdk.GRAB_SUCCESS:
            event_box.destroy()
            item.keyname = item.old_keyname
            return None
        if gtk.gdk.pointer_grab(event_box.window, False, gtk.gdk.BUTTON_PRESS_MASK, None, None, 0) != gtk.gdk.GRAB_SUCCESS:
            gtk.gdk.keyboard_ungrab(0)
            event_box.destroy()
            item.keyname = item.old_keyname
            return None
        event_box.set_can_focus(True)
        event_box.grab_focus()
        event_box.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        event_box.add_events(gtk.gdk.KEY_PRESS_MASK)
        event_box.connect("button-press-event", button_press_callback, item)
        event_box.connect("key-press-event", key_press_callback, item, treeview)
    
    def __remove_shortcuts_item(self, button):
        if not self.view_widgets["shortcuts_shortcut"].select_rows:
            return
        row = self.view_widgets["shortcuts_shortcut"].select_rows[0]
        item = self.view_widgets["shortcuts_shortcut"].visible_items[row]
        button.set_sensitive(False)
        gconf_dir = item.get_data('gconf-dir')
        settings.GCONF_CLIENT.unset('%s/action' % gconf_dir)
        settings.GCONF_CLIENT.unset('%s/binding' % gconf_dir)
        settings.GCONF_CLIENT.unset('%s/name' % gconf_dir)
        self.view_widgets["shortcuts_shortcut"].delete_select_items()
        if item in self.__shortcuts_items[_('Custom Shortcuts')]:
            self.__shortcuts_items[_('Custom Shortcuts')].remove(item)
        print "remove:", gconf_dir, item.description, item.name, item.keyname
    
    def __add_shortcuts_item(self):
        last_row = len(self.view_widgets["shortcuts_selected"].visible_items) - 1
        self.view_widgets["shortcuts_selected"].set_select_rows([last_row])
        self.__edit_cutsom_shortcuts_dilaog()
    
    def __edit_cutsom_shortcuts_dilaog(self, is_edit=False):
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
            print "add:", name, action, key_dir
            settings.shortcuts_custom_set(key_dir, (action, '', name))
            item = ShortcutItem(name, _('disable'), action)
            item.set_data('gconf-dir', '%s/%s' % (base_dir, key_dir))
            item.set_data('setting-type', 'gconf')
            item.set_data('settings', settings.GCONF_CLIENT)
            self.__shortcuts_items[_('Custom Shortcuts')].append(item)
            self.view_widgets["shortcuts_shortcut"].add_items([item])
            self.view_widgets["shortcuts_shortcut"].queue_draw()
            dialog.destroy()
        self.container_widgets["shortcuts_toolbar_hbox"].set_sensitive(False)
        dialog = DialogBox(_("Custom Shortcuts"), 250, 150)
        dialog.connect("destroy", lambda w:self.container_widgets["shortcuts_toolbar_hbox"].set_sensitive(True))
        dialog.set_keep_above(True)
        dialog.set_modal(True)
        #dialog.set_transient_for(self.container_widgets["window"])
        dialog.body_align.set_padding(15, 10, 10, 10)
        
        table = gtk.Table(2, 2, False)
        name_lable = Label(_("name"))
        name_lable.set_can_focus(False)
        action_lable = Label(_("action"))
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
    
    def __make_align(self, widget=None, xalign=0.0, yalign=0.5, xscale=1.0,
                     yscale=0.0, padding_top=0, padding_bottom=0, padding_left=0,
                     padding_right=0, height=CONTAINNER_HEIGHT):
        align = gtk.Alignment()
        align.set_size_request(-1, height)
        align.set(xalign, yalign, xscale, yscale)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        if widget:
            align.add(widget)
        return align
    
    def set_to_default(self):
        '''set to the default'''
        settings.keyboard_set_to_default()
    
    
if __name__ == '__main__':
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    key_settings = KeySetting(module_frame)
    
    module_frame.add(key_settings.alignment_widgets["notebook"])
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            module_frame.send_module_info()
            key_settings.container_widgets["tab_box"].switch_content(0)

    module_frame.module_message_handler = message_handler        
    
    module_frame.run()
