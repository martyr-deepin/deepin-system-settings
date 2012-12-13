#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
import gtk

from app import AppManager

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
        
        table.attach(info_label, 0, 2, 0, 1)
        table.attach(web_label, 0, 1, 1, 2)
        table.attach(mail_label, 0, 1, 2, 3)
        table.attach(editor_label, 0, 1, 3, 4)
        table.attach(music_label, 0, 1, 4, 5)
        table.attach(movie_label, 0, 1, 5, 6)
        table.attach(pic_label, 0, 1 ,6, 7)

        table.attach(self.web, 1, 2, 1, 2, 0)
        table.attach(self.mail,1, 2, 2, 3, 0)
        table.attach(self.editor, 1, 2, 3, 4, 0)
        table.attach(self.music, 1, 2, 4, 5, 0)
        table.attach(self.movie, 1, 2, 5, 6, 0)
        table.attach(self.pic, 1, 2, 6, 7, 0)

        table.set_size_request(455, 230)
        table.set_row_spacings(20)
        table_align = gtk.Alignment(0.5, 0.5, 0, 0)
        table_align.set_padding(25, 0, 0, 0)
        table_align.add(table)

        self.pack_start(table_align, False, False)

        all_app_dict = self.get_all_app()
        print all_app_dict
        apps = [self.web, self.mail, self.editor, self.music, self.movie, self.pic]
        for app in apps:
            app.set_size_request(408, 25)
        for key in all_app_dict.iterkeys():
            if all_app_dict[key]:
                apps[key].set_items(all_app_dict[key], max_width=408)


    
    def get_default_app(self):
        dic = {}
        for index, value in enumerate(self.content_type_list):
            dic[index] = self.app.get_default_for_type(value).get_name()

        return dic

    def get_all_app(self):
        dic = {}
        for index, value in enumerate(self.content_type_list):
            all_app = self.app.get_all_for_type(value)
            dic[index] = map(lambda w: (w[1].get_name(), w[0]), enumerate(all_app))
        return dic
            

    def item_select(self, widget, content, value, index, types):
        pass
        
        # set items




    

    
