#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
import gtk

from app import AppManager
import style

class AppView(gtk.VBox):
    def __init__(self):
        '''docstring for __'''
        gtk.VBox.__init__(self)

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
        info_label = Label("您可以根据自己需要对深度系统在默认情况下使用的程序进行设置")
        web_label = Label("网络")
        mail_label = Label("邮件")
        editor_label = Label("文本")
        music_label = Label("音乐")
        movie_label = Label("视频")
        pic_label = Label("图片")

        self.web = ComboBox([("None",0)], max_width=408)
        self.mail = ComboBox([("None",0)], max_width=408)
        self.editor = ComboBox([("None",0)], max_width=408)
        self.music = ComboBox([("None",0)], max_width=408)
        self.movie = ComboBox([("None",0)], max_width=408)
        self.pic = ComboBox([("None",0)], max_width=408)

        table = gtk.Table(7, 2, False)
        
        table.attach(style.wrap_with_align(info_label), 0, 2, 0, 1)
        table.attach(style.wrap_with_align(web_label), 0, 1, 1, 2)
        table.attach(style.wrap_with_align(mail_label), 0, 1, 2, 3)
        table.attach(style.wrap_with_align(editor_label), 0, 1, 3, 4)
        table.attach(style.wrap_with_align(music_label), 0, 1, 4, 5)
        table.attach(style.wrap_with_align(movie_label), 0, 1, 5, 6)
        table.attach(style.wrap_with_align(pic_label), 0, 1, 6, 7)

        table.attach(style.wrap_with_align(self.web), 1, 2, 1, 2, 0)
        table.attach(style.wrap_with_align(self.mail),1, 2, 2, 3, 0)
        table.attach(style.wrap_with_align(self.editor), 1, 2, 3, 4, 0)
        table.attach(style.wrap_with_align(self.music), 1, 2, 4, 5, 0)
        table.attach(style.wrap_with_align(self.movie), 1, 2, 5, 6, 0)
        table.attach(style.wrap_with_align(self.pic), 1, 2, 6, 7, 0)

        #table.set_size_request(455, 230)
        #table.set_row_spacings(20)
        #table_align = gtk.Alignment(0.5, 0.5, 0, 0)
        #table_align.set_padding(25, 0, 0, 0)
        #table_align.add(table)
        align = style.set_box_with_align(table, "text")
        style.set_table(table)

        self.pack_start(align, False, False)

        #combo_list = [self.web, self.mail, self.editor, self.music, self.movie, self.pic]
        #for combo in combo_list:
            #combo.set_size_request(222, 22)

        all_app_dict = self.get_all_app()
        apps = [self.web, self.mail, self.editor, self.music, self.movie, self.pic]
        for app in apps:
            app.set_size_request(408, 22)
        for key in all_app_dict.iterkeys():
            apps[key].set_items(all_app_dict[key], max_width=408)

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
