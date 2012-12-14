#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dtk.ui.new_treeview import TreeView
from treeview import SessionItem, TitleItem

import gtk
class SessionView(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)

        self.tree = TreeView([],enable_drag_drop=False,
                             enable_hover=False)

    
        self.tree.set_size_request(727, 337)

        self.tree.add_items([TitleItem()])
        #self.connect("expose-event", self.expose_outline)
        self.tree.add_items(self.get_list())

        self.pack_start(self.tree, False, False)
        self.show_all()

    def get_list(self):
        return [SessionItem("htop", "xx"), 
                SessionItem("firefox", "yy")]


