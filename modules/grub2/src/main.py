#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang YaoHua
#
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
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
import string
from deepin_utils.file import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from theme import app_theme

import gtk
from constant import *
from menu_entry import MenuEntry
from dtk.ui.constant import ALIGN_START, ALIGN_END
from dtk.ui.line import HSeparator
from dtk.ui.box import ImageBox
from dtk.ui.menu import Menu
from dtk.ui.label import Label
from dtk.ui.button import CheckButton, Button
from dtk.ui.combo import ComboBox
from dtk.ui.entry import InputEntry
from dtk.ui.dialog import InputDialog
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.treeview import TreeView
from dtk.ui.dialog import OpenFileDialog
from module_frame import ModuleFrame
from dtk.ui.utils import cairo_disable_antialias, color_hex_to_cairo

from nls import _
from core import core_api
from color_button import ColorButton, DEFAULT_COLOR_LIST, color_to_name
from grub_setting_utils import GrubSettingsApi, validate_number, validate_image
from grub_setting_utils import find_all_menu_entry

def process_resolutions(resolutions):
    result = []
    
    for index, value in enumerate(resolutions):
        result.append((str(value), index + 1))
    result.insert(0, (_("Defaulf"), 0))
    
    return result

def get_index_by_value(combo_items, string):
    for value, index in combo_items:
        if value == string:
            return index
    return 0
        
ALIGN_SPACING = 10
SUB_TITLE_SPACING = 175

RESOLUTIONS = process_resolutions(core_api.get_proper_resolutions())

class GrubSettings(object):
    def __init__(self, module_frame):
        super(GrubSettings, self).__init__()
        self.module_frame = module_frame
        self.setting_api = GrubSettingsApi()

        self.__init_widgets()

    def __init_widgets(self):
        self.main_align = gtk.Alignment(0, 0, 1, 1)
        self.main_align.set_padding(TEXT_WINDOW_TOP_PADDING-25,
                                    0,
                                    TEXT_WINDOW_LEFT_PADDING-40,
                                    TEXT_WINDOW_RIGHT_WIDGET_PADDING)
        self.main_vbox = gtk.VBox()
        self.main_vbox.set_spacing(ALIGN_SPACING)
        self.main_vbox.connect("expose-event", self.__main_box_expose)

        self.appearance_title_align = self.__setup_title_align(
            app_theme.get_pixbuf("desktop/icon.png"),
            _("Appearance Settings"),
            TEXT_WINDOW_TOP_PADDING,
            TEXT_WINDOW_LEFT_PADDING)

        self.default_delay_hbox = gtk.HBox()
        self.default_delay_label = self.__setup_label(_("Default delay:"))
        self.default_delay_input = self.__setup_entry(self.setting_api.get_default_delay())
        self.default_delay_input.entry.connect("changed", self.__input_content_changed)
        self.__widget_pack_start(self.default_delay_hbox, [self.default_delay_label, self.default_delay_input], WIDGET_SPACING)
        self.default_delay_align = self.__setup_align()
        self.default_delay_align.add(self.default_delay_hbox)

        self.customize_resolution_hbox = gtk.HBox()
        self.customize_resolution_label = self.__setup_label(_("Customize resolution:"))
        self.customize_resolution_combo = self.__setup_combo(RESOLUTIONS)
        if self.setting_api.is_resolution_active():
            self.customize_resolution_combo.set_select_index(get_index_by_value(RESOLUTIONS, 
                                                                                self.setting_api.get_resolution()))
        self.__widget_pack_start(self.customize_resolution_hbox, [self.customize_resolution_label,
                                                                  self.customize_resolution_combo], WIDGET_SPACING)
        self.customize_resolution_align = self.__setup_align()
        self.customize_resolution_align.add(self.customize_resolution_hbox)

        self.menu_color_normal_hbox = gtk.HBox()
        self.menu_color_normal_align = self.__setup_align()
        self.menu_color_normal_label = self.__setup_label(_("Normal menu color:"))
        self.__widget_pack_start(self.menu_color_normal_hbox, [self.menu_color_normal_label,],
                                 WIDGET_SPACING)
        self.menu_color_normal_align.add(self.menu_color_normal_hbox)

        self.color_normal_align = self.__setup_align()
        self.color_normal_align.set_padding(8, 0,
                                            TEXT_WINDOW_LEFT_PADDING + IMG_WIDTH + WIDGET_SPACING + SUB_TITLE_SPACING, 0)
        self.color_normal_hbox = gtk.HBox()
        self.color_normal_item_value = self.setting_api.get_item_color().split("/")
        print self.color_normal_item_value
        self.color_normal_fg = self.__setup_label("Font:", text_width=75)
        self.color_normal_fg_button = ColorButton()
        self.color_normal_fg_button.set_color(DEFAULT_COLOR_LIST[self.color_normal_item_value[0]])
        self.color_normal_bg = self.__setup_label("Background:", text_width=75)
        self.color_normal_bg_button = ColorButton()
        self.color_normal_bg_button.set_color(DEFAULT_COLOR_LIST[self.color_normal_item_value[1]])
        self.__widget_pack_start(self.color_normal_hbox, [self.color_normal_fg,
                                                          self.color_normal_fg_button,
                                                          self.color_normal_bg,
                                                          self.color_normal_bg_button],
                                 5)
        self.color_normal_align.add(self.color_normal_hbox)


        self.menu_color_highlight_hbox = gtk.HBox()
        self.menu_color_highlight_align = self.__setup_align()
        self.menu_color_highlight_label = self.__setup_label(_("Highlight menu color:"))
        self.__widget_pack_start(self.menu_color_highlight_hbox, [self.menu_color_highlight_label,],
                                 WIDGET_SPACING)
        self.menu_color_highlight_align.add(self.menu_color_highlight_hbox)

        self.color_highlight_align = self.__setup_align()
        self.color_highlight_align.set_padding(8, 0,
                                               TEXT_WINDOW_LEFT_PADDING + IMG_WIDTH + WIDGET_SPACING + SUB_TITLE_SPACING, 0)
        self.color_highlight_hbox = gtk.HBox()
        self.color_highlight_item_value = self.setting_api.get_item_color(True).split("/")
        print self.color_highlight_item_value
        self.color_highlight_fg = self.__setup_label("Font:", text_width=75)
        self.color_highlight_fg_button = ColorButton()
        self.color_highlight_fg_button.set_color(DEFAULT_COLOR_LIST[self.color_highlight_item_value[0]])
        self.color_highlight_bg = self.__setup_label("Background:", text_width=75)
        self.color_highlight_bg_button = ColorButton()
        self.color_highlight_bg_button.set_color(DEFAULT_COLOR_LIST[self.color_highlight_item_value[1]])
        self.__widget_pack_start(self.color_highlight_hbox, [self.color_highlight_fg,
                                                             self.color_highlight_fg_button,
                                                             self.color_highlight_bg,
                                                             self.color_highlight_bg_button],
                                 5)

        self.color_highlight_align.add(self.color_highlight_hbox)
        
        self.background_img_hbox = gtk.HBox()
        self.background_img_label = self.__setup_label(_("Background image:"))
        if self.setting_api.is_background_image_active():
            self.background_img_entry = self.__setup_entry(self.setting_api.get_background_image())
            self.background_img_pixbuf = gtk.gdk.pixbuf_new_from_file(self.setting_api.get_background_image())
        else:
            self.background_img_entry = self.__setup_entry("")            
            self.background_img_pixbuf = None
        self.background_img_entry.set_size(300, WIDGET_HEIGHT)
        self.find_image_button = Button(_("Choose file"))
        self.find_image_button.set_size_request(100, WIDGET_HEIGHT)
        self.find_image_button.connect("clicked", self.__on_find_image_file)
        self.background_img_align = self.__setup_align()
        self.background_img_align.set_padding(20, 0, 
                                              TEXT_WINDOW_LEFT_PADDING + IMG_WIDTH + WIDGET_SPACING, 0)
        self.__widget_pack_start(self.background_img_hbox, [self.background_img_label,
                                                            self.background_img_entry], WIDGET_SPACING)
        self.background_img_hbox.pack_start(self.find_image_button)
        self.background_img_align.add(self.background_img_hbox)

        self.appearance_vbox = gtk.VBox()
        self.__widget_pack_start(self.appearance_vbox, [self.default_delay_align,
                                                        self.customize_resolution_align,
                                                        self.menu_color_normal_align,
                                                        self.color_normal_align,
                                                        self.menu_color_highlight_align,
                                                        self.color_highlight_align,
                                                        self.background_img_align])

        self.list_title_align = self.__setup_title_align(
            app_theme.get_pixbuf("desktop/icon.png"),
            _("Menu List Settings"),
            TEXT_WINDOW_TOP_PADDING,
            TEXT_WINDOW_LEFT_PADDING)

        self.menu_hbox = gtk.HBox()
        self.menu_hbox.set_size_request(650, 150)
        # self.menu_align = self.__setup_menu_entry()
        # self.menu_button_vbox = self.__setup_menu_buttons()
        # self.menu_hbox.pack_start(self.menu_align, True, True, 5)
        # self.menu_hbox.pack_start(self.menu_button_vbox, False, False)
        self.menu_hbox.add(self.__setup_menu_entry())
        self.menu_align = self.__setup_align()
        self.menu_align.set_padding(10, 20,
                                    TEXT_WINDOW_LEFT_PADDING + IMG_WIDTH + WIDGET_SPACING, 0)
        self.menu_align.add(self.menu_hbox)

        self.__widget_pack_start(self.main_vbox, [self.appearance_title_align,
                                                  self.appearance_vbox,
                                                  self.list_title_align,
                                                  self.menu_align])
        self.scrolled_window = ScrolledWindow()
        self.scrolled_window.set_size_request(-1, 420)
        self.scrolled_window.add_child(self.main_vbox)
        
        # FootBox
        self.foot_box_align = self.__setup_align()
        self.foot_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.foot_box_align.connect("expose-event", self.__foot_box_expose)
        self.notice_label = Label("", text_x_align = ALIGN_START, label_width=480)
        self.reset_button = self.__setup_button(_("Reset"))
        self.reset_button.connect("clicked", lambda : True)
        self.apply_button = self.__setup_button(_("Apply"))        
        self.apply_button.connect("clicked", self.__on_apply)
        self.__widget_pack_start(self.foot_box,
                [self.notice_label,
                 self.reset_button,
                 self.apply_button
                ])
        self.foot_box_align.add(self.foot_box)
        
        self.bigger_main_vbox = gtk.VBox()
        self.__widget_pack_start(self.bigger_main_vbox, [self.scrolled_window, 
                                                         self.foot_box_align])
        self.module_frame.add(self.bigger_main_vbox)

        self.__setup_signals()

    def __color_button_color_selected(self, gobj, color_string, button_name):
        if button_name == "normal_fg":
            map(lambda x : x.set_normal_fg(color_string), self.menu_entries)
        if button_name == "normal_bg":
            map(lambda x : x.set_normal_bg(color_string), self.menu_entries)
        if button_name == "highlight_fg":
            map(lambda x : x.set_highlight_fg(color_string), self.menu_entries)
        if button_name == "highlight_bg":
            map(lambda x : x.set_highlight_bg(color_string), self.menu_entries)
            
        map(lambda x : x.emit_redraw_request(), self.menu_entries)
        
    def __input_content_changed(self, widget, text):
        if text[-1] not in string.digits:
            widget.set_text(text[:-1])
        
    def __setup_signals(self):
        self.color_normal_fg_button.connect("color-select", self.__color_button_color_selected, "normal_fg")
        self.color_normal_bg_button.connect("color-select", self.__color_button_color_selected, "normal_bg")
        self.color_highlight_fg_button.connect("color-select", self.__color_button_color_selected, "highlight_fg")
        self.color_highlight_bg_button.connect("color-select", self.__color_button_color_selected, "highlight_bg")
        
    def __on_find_image_file(self, widget):
        image_file = []
        OpenFileDialog(_("Choose background image"), 
                       self.module_frame.get_parent(), 
                       lambda file_name : image_file.append(file_name))
        if len(image_file) != 0:
            self.background_img_entry.set_text(image_file[0])
            try:
                self.background_img_pixbuf = gtk.gdk.pixbuf_new_from_file(image_file[0])
                self._menu.queue_draw()
            except:
                self._menu.queue_draw()
        
    def __on_apply(self, widget):
        if validate_number(self.default_delay_input.get_text()):
            self.setting_api.set_default_delay(self.default_delay_input.get_text())
        if self.customize_resolution_combo.get_select_index() == 0:
            self.setting_api.disable_customize_resolution()
        else:
            self.setting_api.set_resolution(str(self.customize_resolution_combo.get_current_item()[0]))
        self.setting_api.set_item_color(color_to_name(self.color_normal_fg_button.get_color()), 
                                        color_to_name(self.color_normal_bg_button.get_color()))
        self.setting_api.set_item_color(color_to_name(self.color_highlight_fg_button.get_color()),
                                        color_to_name(self.color_highlight_bg_button.get_color()), True)
        if validate_image(self.background_img_entry.get_text()):
            self.setting_api.set_background_image(self.background_img_entry.get_text())
        else:
            self.background_img_entry.set_text("")
            self.setting_api.disable_background_image()
            
        core_api.update_grub(self.setting_api.uuid)

    def __setup_menu_entry(self):
        self.menu_entries = [MenuEntry(entry) for entry in find_all_menu_entry()]
        self._menu = TreeView(self.menu_entries, expand_column=0)
        self._menu.draw_mask = self.__menu_entry_draw_mask
        self._menu.set_highlight_item(self.menu_entries[0])
        self._menu.connect("right-press-items", self.__menu_entry_right_press_items)
        self._menu.connect("single-click-item", self.__menu_entry_single_click_item)
        self._menu_align = gtk.Alignment(1, 1, 1, 1)
        self._menu_align.set_padding(5, 5, 5, 5)
        self._menu_align.add(self._menu)
        self._menu_align.connect("expose-event", self.__menu_align_expose)

        return self._menu_align
    
    def __move_up_down(self, item, up=True):
        if item not in self.menu_entries:
            return
        
        index = self.menu_entries.index(item)
        if (index == 0 and up) or (index == len(self.menu_entries) - 1 and not up):
            return
        else:
            if up:
                self.menu_entries[index - 1], self.menu_entries[index] = self.menu_entries[index], self.menu_entries[index - 1]
            else:
                self.menu_entries[index], self.menu_entries[index + 1] = self.menu_entries[index + 1], self.menu_entries[index]    
                
            self._menu.add_items(self.menu_entries, clear_first=True)
            self._menu.queue_draw()
            
    def __rename_item(self, item):
        def confirm_callback(s):
            item.title = s
            item.emit_redraw_request()
            
        InputDialog(_("Rename entry"), item.title, confirm_callback=confirm_callback).show_all()
        
    def __delete_item(self, item):
        if item in self.menu_entries and not len(self.menu_entries) == 1:
            self.menu_entries.remove(item)
            self._menu.add_items(self.menu_entries, clear_first=True)
            self._menu.queue_draw()
            
        for entry in self.menu_entries:
            print entry
                
    def __menu_entry_single_click_item(self, widget, item, column, x, y):
        print "single click"
        widget.set_highlight_item(item)

    def __menu_entry_right_press_items(self, widget, x, y, current_item, select_items):
        print "right press"
        widget.set_highlight_item(current_item)
        menu_items = [(None, _("Move up"), lambda : self.__move_up_down(current_item)),
                      (None, _("Move down"), lambda : self.__move_up_down(current_item, False)),
                      (None, _("Rename"), lambda : self.__rename_item(current_item)),
                      (None, _("Delete"), lambda : self.__delete_item(current_item))]
        Menu(menu_items, True).show((x, y))
    
    def __setup_menu_buttons(self):
        menu_button_vbox = gtk.VBox(homogeneous=True)
        
        move_up_button = self.__setup_menu_button(_("Move up"))
        move_down_button = self.__setup_menu_button(_("Move down"))
        rename_button = self.__setup_menu_button(_("Rename"))
        delete_button = self.__setup_menu_button(_("Delete"))
        
        self.__widget_pack_start(menu_button_vbox, [move_up_button,
                                                    move_down_button,
                                                    rename_button,
                                                    delete_button])
        
        return menu_button_vbox
    
    def __menu_entry_draw_mask(self, cr, x, y, w, h):
        if self.background_img_pixbuf:
            try:
                cr.set_source_pixbuf(self.background_img_pixbuf, x, y)
                cr.paint()
            except Exception, e:
                cr.set_source_rgb(0, 0, 0)
                cr.rectangle(x, y, w, h)
                cr.fill()
        else:
            cr.set_source_rgb(0, 0, 0)
            cr.rectangle(x, y, w, h)
            cr.fill()

    def __setup_checkbutton(self, label_text, padding_x=0):
        return CheckButton(label_text, padding_x)

    def __setup_button(self, label):
        button = Button(label)
        button.set_size_request(100, 24)
        return button
    
    def __setup_menu_button(self, label):
        button = Button(label)
        button.set_size_request(50, 24)
        return button 

    def __setup_label(self, text="", text_width = 200, text_size=CONTENT_FONT_SIZE, align=ALIGN_END):
        return Label(text, None, text_size, align, text_width, enable_double_click=False)

    def __setup_combo(self, items=[]):
        combo = ComboBox(items, 200, 0, max_width = 100, fixed_width = 100)
        combo.set_size_request(-1, WIDGET_HEIGHT)
        return combo

    def __setup_toggle(self):
        return ToggleButton(app_theme.get_pixbuf("toggle_button/inactive_normal.png"),
            app_theme.get_pixbuf("toggle_button/active_normal.png"))

    def __setup_entry(self, content="", action_button=None):
        entry = InputEntry(content, action_button)
        entry.set_size(100, WIDGET_HEIGHT)
        return entry

    def __setup_align(self,
                      padding_top=8,
                      padding_bottom=0,
                      padding_left=TEXT_WINDOW_LEFT_PADDING + IMG_WIDTH + WIDGET_SPACING,
                      padding_right=0):
        align = gtk.Alignment()
        align.set(0.0, 0.5, 0, 0)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        return align

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

    def __setup_separator(self):
        hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        hseparator.set_size_request(500, HSEPARATOR_HEIGHT)
        return hseparator

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

    def __widget_pack_start(self, parent_widget, widgets=[], widget_spacing=0):
        if parent_widget == None:
            return
        for item in widgets:
            parent_widget.pack_start(item, False, False, widget_spacing)

    def __main_box_expose(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation

        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
        
    def __foot_box_expose(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
        
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*color_hex_to_cairo("#AEAEAE"))            
            cr.move_to(x, y)
            cr.line_to(x + w, y)
            cr.stroke()

    def __menu_align_expose(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation

        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*color_hex_to_cairo("#AEAEAE"))
            cr.rectangle(x, y, w, h)
            cr.stroke()

    def __send_message(self, message_type, message_content):
        if is_dbus_name_exists(APP_DBUS_NAME):
            bus_object = dbus.SessionBus().get_object(APP_DBUS_NAME, APP_OBJECT_NAME)
            method = bus_object.get_dbus_method("message_receiver")
            method(message_type,
                   message_content,
                   reply_handler=self.__handle_dbus_replay,
                   error_handler=self.__handle_dbus_error)

    def __handle_dbus_replay(self, *reply):
        pass

    def __handle_dbus_error(self, *error):
        pass

if __name__ == "__main__":
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))
    GrubSettings(module_frame)

    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            module_frame.send_module_info()
        elif message_type == "exit":
            module_frame.exit()

    module_frame.module_message_handler = message_handler
    module_frame.run()
