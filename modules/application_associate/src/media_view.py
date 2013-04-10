#!/usr/bin/env python
#-*- coding:utf-8 -*-

from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
from dtk.ui.button import CheckButton, Button

from media import MediaAutorun
from app import AppManager
import gtk
import style
from constants import STANDARD_LINE, TEXT_WINDOW_LEFT_PADDING
from nls import _

class MediaView(gtk.VBox):
    ENTRY_WIDTH = 200
    LEFT_WIDTH = STANDARD_LINE - TEXT_WINDOW_LEFT_PADDING

    def __init__(self):
        gtk.VBox.__init__(self)
        style.draw_background_color(self)
        self.media_handle = MediaAutorun()
        self.app_manager = AppManager()
        self.init_table()

    def init_table(self):

        table = gtk.Table(8, 3, False)

        #info_label = Label("您可以选择插入每种媒体或设备时的后续操作")

        cd_label = Label(_("CD"))
        dvd_label = Label(_("DVD"))
        player_label = Label(_("music player"))
        photo_label = Label(_("camera"))
        software_label = Label(_("software"))
        
        default_list = [(_("other applications"), "other_app"),
                        (_("ask"), "ask"),
                        (_("do nothing"), "do_nothing"),
                        (_("open folder"),"open_folder")]
        self.auto_check = CheckButton(_("apply auto play for all media and devices"))
        self.cd = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.dvd = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.player= ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.photo = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.software = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)

        self.more_option = Button(_("more option"))
        #self.more_option.set_size_request( 30, 22)

        #table.attach(style.wrap_with_align(info_label, width=self.LEFT_WIDTH), 0, 3, 0, 1)
        table.attach(style.wrap_with_align(cd_label, width=self.LEFT_WIDTH), 0, 1, 2, 3)
        table.attach(style.wrap_with_align(dvd_label, width=self.LEFT_WIDTH), 0, 1, 3, 4)
        table.attach(style.wrap_with_align(player_label, width=self.LEFT_WIDTH), 0, 1, 4, 5)
        table.attach(style.wrap_with_align(photo_label, width=self.LEFT_WIDTH), 0, 1, 5, 6)
        table.attach(style.wrap_with_align(software_label, width=self.LEFT_WIDTH), 0, 1, 6, 7)
        
        #table.attach(style.wrap_with_align(self.auto_check), 0, 3, 1, 2)
        table.attach(style.wrap_with_align(self.cd), 1, 3, 2, 3)
        table.attach(style.wrap_with_align(self.dvd), 1, 3, 3, 4)
        table.attach(style.wrap_with_align(self.player), 1, 3, 4, 5)
        table.attach(style.wrap_with_align(self.photo), 1, 3, 5, 6)
        table.attach(style.wrap_with_align(self.software), 1, 3, 6, 7)
        #table.attach(style.wrap_with_align(self.more_option), 2, 3, 7, 8)

        # UI style
        table_align = style.set_box_with_align(table, "text")
        style.set_table(table)

        self.pack_start(table_align, False, False)

        combo_list = [self.cd, self.dvd, self.player, self.photo, self.software]
        for combo in combo_list:
            combo.set_size_request(self.ENTRY_WIDTH, 22)

        self.refresh_app_list(default_list)
        if self.media_handle.autorun_never:
            for combo in self.all_app_dict:
                combo.set_sensitive(False)
                self.auto_check.set_active(False)
        else:
            for combo in self.all_app_dict:
                combo.set_sensitive(True)
                self.auto_check.set_active(True)

        self.connect_signal_to_combos()

    def refresh_app_list(self, default_list):
        self.default_list = default_list
        self.all_app_dict = {self.cd: self.media_handle.cd_content_type,
                             self.dvd: self.media_handle.dvd_content_type,
                             self.player: self.media_handle.player_content_type,
                             self.photo: self.media_handle.photo_content_type,
                             self.software: self.media_handle.software_content_type
                             }

        for key, value in self.all_app_dict.iteritems():
            app_info_list = []
            app_info_list.extend(self.app_manager.get_all_for_type(value))
            
            state = self.get_state(value)
            if state == "set_default":
                default_value = 0
            else:
                default_value = len(app_info_list) + ["ask", "do_nothing","open_folder"].index(state) + 1

            key.add_items(map(lambda info:(info.get_name(), info), app_info_list) + default_list, select_index=default_value)

    def connect_signal_to_combos(self):
        for combo in self.all_app_dict:
            combo.connect("item-selected", self.change_autorun_callback)
        self.auto_check.connect("toggled", self.autorun_toggle_cb)

    def change_autorun_callback(self, widget, content, value, index):
        if type(value) is not str:
            self.set_media_handler_preference(self.all_app_dict[widget], "set_default")
            self.app_manager.set_default_for_type(value, self.all_app_dict[widget])
        else:
            self.set_media_handler_preference(self.all_app_dict[widget], value)

    def autorun_toggle_cb(self, widget):
        self.media_handle.autorun_never = not widget.get_active()
        
        if widget.get_active():
            for combo in self.all_app_dict:
                combo.set_sensitive(True)
        else:
            for combo in self.all_app_dict:
                combo.set_sensitive(False)

    def set_media_handler_preference(self, x_content, action_name=None):
        if action_name == "ask":
            self.media_handle.remove_x_content_start_app(x_content)
            self.media_handle.remove_x_content_ignore(x_content)
            self.media_handle.remove_x_content_open_folder(x_content)
            print action_name, ">>>",self.get_state(x_content)

        elif action_name == "do_nothing":
            self.media_handle.remove_x_content_start_app(x_content)
            self.media_handle.add_x_content_ignore(x_content)
            self.media_handle.remove_x_content_open_folder(x_content)
            print action_name, ">>>",self.get_state(x_content)

        elif action_name == "open_folder":
            self.media_handle.remove_x_content_start_app(x_content)
            self.media_handle.remove_x_content_ignore(x_content)
            self.media_handle.add_x_content_open_folder(x_content)
            print action_name, ">>>",self.get_state(x_content)

        elif action_name == "set_default":
            self.media_handle.add_x_content_start_app(x_content)
            self.media_handle.remove_x_content_ignore(x_content)
            self.media_handle.remove_x_content_open_folder(x_content)
            print action_name, ">>>",self.get_state(x_content)
        else:
            from dtk.ui.dialog import OpenFileDialog
            OpenFileDialog("test", self.get_toplevel(), lambda name: self.add_app_info(name, x_content))

    def add_app_info(self, app_name, x_content):
        import os
        app_name = os.path.basename(app_name)
        app_info = self.app_manager.get_app_info(app_name + " %u", app_name)
        self.set_media_handler_preference(x_content, "set_default")
        self.app_manager.set_default_for_type(app_info, x_content)
        self.app_manager.get_all_for_type(x_content)
        self.refresh_app_list(self.default_list)

    def get_state(self, x_content):
        start_up = self.media_handle.autorun_x_content_start_app
        ignore = self.media_handle.autorun_x_content_ignore
        open_folder = self.media_handle.autorun_x_content_open_folder

        start_up_flag = x_content in start_up
        ignore_flag = x_content in ignore
        open_folder_flag = x_content in open_folder

        if start_up_flag:
            return "set_default"
        elif ignore_flag:
            return "do_nothing"
        elif open_folder_flag:
            return "open_folder"
        else:
            return "ask"
