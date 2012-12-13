#!/usr/bin/env python
#-*- coding:utf-8 -*-

from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
from dtk.ui.button import CheckButton, Button
import gtk

class MediaView(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)
        self.init_table()

    def init_table(self):

        table = gtk.Table(8, 3, False)

        info_label = Label("您可以选择插入每种媒体或设备时的后续操作")

        cd_label = Label("CD音频")
        dvd_label = Label("DVD视频")
        player_label = Label("音乐播放器")
        photo_label = Label("图片")
        software_label = Label("软件")

        self.auto_check = CheckButton("为所有媒体和设备使用自动播放")
        self.cd = ComboBox(["None", 0], max_width=323)
        self.dvd = ComboBox(["None", 0], max_width=323)
        self.player= ComboBox(["None", 0], max_width=323)
        self.photo = ComboBox(["None", 0], max_width=323)
        self.software = ComboBox(["None", 0], max_width=323)

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
        

