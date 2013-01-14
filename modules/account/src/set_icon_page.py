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

from nls import _
from dtk.ui.label import Label
from dtk.ui.scrolled_window import ScrolledWindow
from icon_button import IconButton
from constant import *
import gtk
import tools
import os

class IconSetPage(gtk.VBox):
    '''docstring for IconSetPage'''
    def __init__(self, account_setting):
        super(IconSetPage, self).__init__(False)
        self.set_spacing(BETWEEN_SPACING)
        self.account_setting = account_setting

        self.tips_label = Label("", text_size=13, wrap_width=460, enable_select=False)
        self.error_label = Label("", wrap_width=560, enable_select=False)
        self.pack_start(tools.make_align(self.tips_label, height=CONTAINNER_HEIGHT), False, False)

        icon_list_sw = ScrolledWindow()
        icon_list_hbox = gtk.HBox(False)
        icon_list_sw.add_child(icon_list_hbox)

        history_list_sw = ScrolledWindow()
        history_list_hbox = gtk.HBox(False)
        history_list_sw.add_child(history_list_hbox)

        self.pack_start(tools.make_align(Label(_("选择用户头像")), height=CONTAINNER_HEIGHT), False, False)
        self.pack_start(tools.make_align(icon_list_sw), False, False)

        self.pack_start(tools.make_align(Label(_("历史使用头像")), height=CONTAINNER_HEIGHT), False, False)
        self.pack_start(tools.make_align(history_list_sw), False, False)

        face_dir = '/usr/share/pixmaps/faces'
        if os.path.exists(face_dir):
            pic_list = os.listdir(face_dir)
        else:
            pic_list = []
        for pic in pic_list:
            try:
                icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                    "%s/%s" %(face_dir, pic)).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
            except:
                continue
            icon_bt = IconButton(icon_pixbuf, "%s/%s" %(face_dir, pic))
            icon_bt.connect("button-release-event", self.on_icon_bt_release_cb)
            icon_list_hbox.pack_start(icon_bt, False, False)
