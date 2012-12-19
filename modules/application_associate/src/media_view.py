#!/usr/bin/env python
#-*- coding:utf-8 -*-

from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
from dtk.ui.button import CheckButton, Button

from media import MediaAutorun
from app import AppManager
import gtk

class MediaView(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)
        self.media_handle = MediaAutorun()
        self.app_manager = AppManager()
        self.init_table()

    def init_table(self):

        table = gtk.Table(8, 3, False)

        info_label = Label("您可以选择插入每种媒体或设备时的后续操作")

        cd_label = Label("CD音频")
        dvd_label = Label("DVD视频")
        player_label = Label("音乐播放器")
        photo_label = Label("图片")
        software_label = Label("软件")
        
        default_list = [("其他应用程序", "other_app"),
                        ("询问如何处理", "ask"),
                        ("不处理", "do_nothing"),
                        ("打开文件夹","open_folder")]
        self.auto_check = CheckButton("为所有媒体和设备使用自动播放")
        self.cd = ComboBox(default_list, max_width=323)
        self.dvd = ComboBox(default_list, max_width=323)
        self.player= ComboBox(default_list, max_width=323)
        self.photo = ComboBox(default_list, max_width=323)
        self.software = ComboBox(default_list, max_width=323)

        self.more_option = Button("更多选项")
        self.more_option.set_size_request(78, 24)

        table.attach(info_label, 0, 3, 0, 1)
        table.attach(cd_label, 0, 1, 2, 3)
        table.attach(dvd_label, 0, 1, 3, 4)
        table.attach(player_label, 0, 1, 4, 5)
        table.attach(photo_label, 0, 1, 5, 6)
        table.attach(software_label, 0, 1, 6, 7)
        
        table.attach(self.auto_check, 0, 3, 1, 2)
        table.attach(self.cd, 1, 3, 2, 3, gtk.SHRINK)
        table.attach(self.dvd, 1, 3, 3, 4, gtk.SHRINK)
        table.attach(self.player, 1, 3, 4, 5, gtk.SHRINK)
        table.attach(self.photo, 1, 3, 5, 6, gtk.SHRINK)
        table.attach(self.software, 1, 3, 6, 7, gtk.SHRINK)
        table.attach(self.more_option, 2, 3, 7, 8, gtk.SHRINK)

        # UI style
        table.set_size_request(447, 290)
        table.set_row_spacings(20)
        table_align = gtk.Alignment(0.5, 0.5, 0, 0)
        table_align.set_padding(25, 19, 0, 0)
        table_align.add(table)

        self.pack_start(table_align, False, False)
        self.refresh_app_list(default_list)
        self.connect_signal_to_combos()

    def refresh_app_list(self, default_list):
        self.all_app_dict = {self.cd: self.media_handle.cd_content_type,
                             self.dvd: self.media_handle.dvd_content_type,
                             self.player: self.media_handle.player_content_type,
                             self.photo: self.media_handle.photo_content_type,
                             self.software: self.media_handle.software_content_type
                             }
        autorun_x_content_start_app = self.media_handle.autorun_x_content_start_app

        for key, value in self.all_app_dict.iteritems():
            app_info_list = []
            app_info_list.extend(self.app_manager.get_all_for_type(value))
            
            state = self.get_state(value)
            if state == "set_default":
                default_value = 0
            else:
                default_value = len(app_info_list) + ["ask", "do_nothing","open_folder"].index(state) + 1

            key.set_items(map(lambda info:(info.get_name(), info), app_info_list) + default_list, max_width=323, select_index=default_value)

    def connect_signal_to_combos(self):
        for combo in self.all_app_dict:
            combo.connect("item-selected", self.change_autorun_callback)

    def change_autorun_callback(self, widget, content, value, index):
        if type(value) is not str:
            self.set_media_handler_preference(self.all_app_dict[widget], "set_default")
            self.app_manager.set_default_for_type(value, self.all_app_dict[widget])
        else:
            self.set_media_handler_preference(self.all_app_dict[widget], value)

    def set_media_handler_preference(self, x_content, action_name=None):
        if action_name == "ask":
            self.media_handle.remove_x_content_start_app(x_content)
            self.media_handle.remove_x_content_ignore(x_content)
            self.media_handle.remove_x_content_open_folder(x_content)

            #print action_name, ">>>",self.get_state(x_content)
        elif action_name == "do_nothing":
            self.media_handle.remove_x_content_start_app(x_content)
            self.media_handle.add_x_content_ignore(x_content)
            self.media_handle.remove_x_content_open_folder(x_content)
            #print action_name, ">>>",self.get_state(x_content)

        elif action_name == "open_folder":
            self.media_handle.remove_x_content_start_app(x_content)
            self.media_handle.remove_x_content_ignore(x_content)
            self.media_handle.add_x_content_open_folder(x_content)
            #print action_name, ">>>",self.get_state(x_content)

        elif action_name == "set_default":
            self.media_handle.add_x_content_start_app(x_content)
            self.media_handle.remove_x_content_ignore(x_content)
            self.media_handle.remove_x_content_open_folder(x_content)
            #print action_name, ">>>",self.get_state(x_content)
        else:
            pass

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
