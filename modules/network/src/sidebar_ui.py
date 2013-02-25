#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Zeng Zhi
# 
# Author:     Zeng Zhi <zengzhilg@gmail.com>
# Maintainer: Zeng Zhi <zengzhilg@gmail.com>
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

from dtk.ui.new_treeview import TreeView
from dtk.ui.utils import container_remove_all
from settings_widget import SettingItem, AddSettingItem, EntryTreeView
from helper import Dispatcher
import style

import gtk
import style
from helper import Dispatcher
from nls import _

class SideBar(gtk.VBox):
    def __init__(self, connections):
        gtk.VBox.__init__(self, False)
        self.connections = connections
        self.new_connection_list = {'cdma':[], "gsm":[]}
        self.__init_widget()

    def __init_widget(self):
        self.buttonbox = gtk.VBox()
        self.pack_start(self.buttonbox, False, False)
        style.add_separator(self)
        self.connection_tree = EntryTreeView()
        self.add_button = AddSettingItem(_("New Connection") ,self.add_new_connection)
        self.pack_start(TreeView([self.add_button]), False, False)
        self.set_size_request(160, -1)

    def load_list(self, network_object):
        '''
        will add hasattr part for network_object
        '''
        self.network_object = network_object
        self.__init_tree(self.network_object.get_connections())

        if hasattr(self.network_object, "add_new_connection"):
            self.add_button.change_add_setting(self.network_object.add_new_connection)

        if hasattr(self.network_object, "delete_item"):
            pass

    def __init_tree(self, items_list):
        container_remove_all(self.buttonbox)
        self.connection_tree.add_items(map(lambda c: SettingItem(c, None, self.set_button), items_list))
        self.buttonbox.add(self.connection_tree)

    def set_button(self):
        pass

    def delete_item_cb(self, connection):
        '''docstring for delete_item_cb'''
        from nmlib.nm_remote_connection import NMRemoteConnection
        self.connection_tree.delete_select_items()
        if isinstance(connection, NMRemoteConnection):
            connection.delete()
        else:
            mobile_type = self.connection.get_setting("connection").type
            index = self.new_connection_list[mobile_type].index(connection)
            self.new_connection_list[mobile_type].pop(index)

        if self.connection_tree.visible_items == []:
            self.connection_tree.set_size_request(-1,len(self.connection_tree.visible_items) * self.connection_tree.visible_items[0].get_height())
        else:
            container_remove_all(self.buttonbox)

    def get_active(self):
        return self.connection_tree.select_rows[0]

    def set_active(self, connection):
        item = self.cons[self.connections.index(connection)]
        self.connection_tree.select_items([item])
    
    def add_new_connection(self):
        pass

