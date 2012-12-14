#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dtk.ui.new_treeview import TreeView
from dtk.ui.button import Button
from treeview import SessionItem, TitleItem

import gtk
class SessionView(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)

        self.tree = TreeView([],enable_drag_drop=False,
                             enable_hover=False)

        self.tree.set_size_request(727, 337)

        self.tree.add_items([TitleItem()])
        self.tree.add_items(self.get_list())
        align = gtk.Alignment(0.5, 0.5, 0, 0)
        align.set_padding(7, 30 , 7, 7)
        align.add(self.tree)
        self.pack_start(align, False, False)
        self.show_all()

        hbox = gtk.HBox(spacing=5)
        add_button = Button("添加")
        delete_button = Button("删除")

        hbox.pack_start(add_button, False, False)
        hbox.pack_start(delete_button, False, False)

        btn_align = gtk.Alignment(1, 0, 0, 1)
        btn_align.set_padding(0, 0, 0, 30)
        btn_align.add(hbox)
        self.pack_start(btn_align, False, False)


    def get_list(self):
        return [SessionItem("htop", "xx"), 
                SessionItem("firefox", "yy")]


