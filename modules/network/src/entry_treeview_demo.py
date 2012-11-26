#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
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

#from dtk.ui.init_skin import init_skin
#from dtk.ui.utils import get_parent_dir
#import os

#app_theme = init_skin(
    #"deepin-ui-demo",
    #"1.0",
    #"01",
    #os.path.join(get_parent_dir(__file__), "skin"),
    #os.path.join(get_parent_dir(__file__), "app_theme"),
    #)

from theme import app_theme
from dtk.ui.new_treeview import TreeView, TreeItem
from dtk.ui.draw import draw_text
from dtk.ui.utils import color_hex_to_cairo, is_left_button, is_right_button
from dtk.ui.new_entry import Entry
from settings_widget import EntryTreeView, SettingItem
import gtk
import gobject

if __name__ == '__main__':
    win = gtk.Window()
    win.set_size_request(300, 290)
    win.connect("destroy", gtk.main_quit)

    item1 = SettingItem("item1", "this is a tree item test")
    item2 = SettingItem("item2", "item2 test")
    item3 = SettingItem("item3", "third item test")
    item4 = SettingItem("item4", "third item test")
    item5 = SettingItem("item5", "third item test")
    item6 = SettingItem("item6", "third item test")
    item7 = SettingItem("item7", "third item test")
    item8 = SettingItem("item8", "third item test")
    item9 = SettingItem("item9", "third item test")
    item10 = SettingItem("item10", "third item test")
    item11 = SettingItem("item11", "third item test")
    item12 = SettingItem("item12", "third item test")
    item13 = SettingItem("item13", "third item test")
    item14 = SettingItem("item14", "third item test")
    item = [item1, item2, item3, item4, item5,
            item6, item7, item8, item9, item10,
            item11, item12, item13, item14]
    tree_view = EntryTreeView(item)
    print tree_view.select_items([item1])

    win.add(tree_view)
    win.show_all()
    gtk.main()
