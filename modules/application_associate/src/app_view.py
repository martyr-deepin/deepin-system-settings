#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
import gtk

from app import AppManager
from constants import STANDARD_LINE, TEXT_WINDOW_LEFT_PADDING, FRAME_LEFT_PADDING
import style

from nls import _

class AppView(gtk.VBox):
    ENTRY_WIDTH = 200
    LEFT_WIDTH = STANDARD_LINE - TEXT_WINDOW_LEFT_PADDING
    def __init__(self):
        '''docstring for __'''
        gtk.VBox.__init__(self)
        style.draw_background_color(self)

        self.app = AppManager()
        self.content_type_list = [self.app.http_content_type,
                                  self.app.mail_content_type,
                                  self.app.editor_content_type,
                                  self.app.audio_content_type,
                                  self.app.video_content_type,
                                  self.app.photo_content_type]
        
        self.app_table()
        self.web.connect("item-selected", self.item_select, 0)
        self.mail.connect("item-selected", self.item_select, 1)
        self.editor.connect("item-selected", self.item_select, 2)
        self.music.connect("item-selected", self.item_select, 3)
        self.movie.connect("item-selected", self.item_select, 4)
        self.pic.connect("item-selected", self.item_select, 5)

    def app_table(self):
        # Labels 
        #info_label = Label("您可以根据自己需要对深度系统在默认情况下使用的程序进行设置")
        web_label = Label(_("web"))
        mail_label = Label(_("mail"))
        editor_label = Label(_("editor"))
        music_label = Label(_("music"))
        movie_label = Label(_("video"))
        pic_label = Label(_("photo"))

        self.web = ComboBox([("None",0)], max_width=self.ENTRY_WIDTH)
        self.mail = ComboBox([("None",0)], max_width=self.ENTRY_WIDTH)
        self.editor = ComboBox([("None",0)], max_width=self.ENTRY_WIDTH)
        self.music = ComboBox([("None",0)], max_width=self.ENTRY_WIDTH)
        self.movie = ComboBox([("None",0)], max_width=self.ENTRY_WIDTH)
        self.pic = ComboBox([("None",0)], max_width=self.ENTRY_WIDTH)

        table = gtk.Table(7, 2, False)
        #table.attach(style.wrap_with_align(info_label), 0, 2, 0, 1)
        table.attach(style.wrap_with_align(web_label, width=self.LEFT_WIDTH), 0, 1, 1, 2)
        table.attach(style.wrap_with_align(mail_label, width=self.LEFT_WIDTH), 0, 1, 2, 3)
        table.attach(style.wrap_with_align(editor_label, width=self.LEFT_WIDTH), 0, 1, 3, 4)
        table.attach(style.wrap_with_align(music_label, width=self.LEFT_WIDTH), 0, 1, 4, 5)
        table.attach(style.wrap_with_align(movie_label, width=self.LEFT_WIDTH), 0, 1, 5, 6)
        table.attach(style.wrap_with_align(pic_label, width=self.LEFT_WIDTH), 0, 1, 6, 7)

        table.attach(style.wrap_with_align(self.web), 1, 2, 1, 2, 0)
        table.attach(style.wrap_with_align(self.mail),1, 2, 2, 3, 0)
        table.attach(style.wrap_with_align(self.editor), 1, 2, 3, 4)
        table.attach(style.wrap_with_align(self.music), 1, 2, 4, 5)
        table.attach(style.wrap_with_align(self.movie), 1, 2, 5, 6)
        table.attach(style.wrap_with_align(self.pic), 1, 2, 6, 7)
        align = style.set_box_with_align(table, "text")
        style.set_table(table)

        self.pack_start(align, False, False)

        all_app_dict = self.get_all_app()
        apps = [self.web, self.mail, self.editor, self.music, self.movie, self.pic]
        for app in apps:
            app.set_size_request(self.ENTRY_WIDTH, 22)
        for key in all_app_dict.iterkeys():
            apps[key].add_items(all_app_dict[key])
    
    def attach_to(self, table, widget_list, row, width):
        for index, widget in enumerate(widget_list):
            align = style.wrap_with_align(widget, width=width[index])
            table.attach(align, index, index + 1, row, row +1)
            
    def get_default_app(self):
        dic = {}
        for index, value in enumerate(self.content_type_list):
            default_app = self.app.get_default_for_type(value)
            if default_app:
                dic[index] = default_app

        return dic

    def get_all_app(self):
        dic = {}
        for index, value in enumerate(self.content_type_list):
            all_app = self.app.get_all_for_type(value)
            dic[index] = map(lambda w: (w.get_name(), w), all_app)
        def filter_empty(dic):
            d = {}
            for i in dic.iterkeys():
                if dic[i] != []:
                    d[i] = dic[i]
            return d
        return filter_empty(dic)
            
    def item_select(self, widget, content, value, index, types):
        default_apps = self.get_default_app()
        if content != "None" and default_apps[types].get_name() != content:
            self.app.set_default_for_type(value, self.content_type_list[types])
