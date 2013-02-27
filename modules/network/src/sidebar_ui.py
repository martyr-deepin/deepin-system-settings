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

        self.__init_signals()

    def __init_signals(self):
        Dispatcher.connect("connection-delete", self.delete_item_cb)
        Dispatcher.connect("connection-replace", self.replace_connection)

    def load_list(self, network_object):
        '''
        will add hasattr part for network_object
        '''
        self.network_object = network_object
        self.connections = self.network_object.get_connections()
        for connection in self.connections:
            connection.init_settings_prop_dict()
        self.connection_tree = EntryTreeView()
        self.__init_tree(self.connections)

        if hasattr(self.network_object, "add_new_connection"):
            self.new_connection = self.network_object.add_new_connection
            #self.add_button.change_add_setting(self.network_object.add_new_connection)
        if hasattr(self.network_object, "delete_item"):
            pass
        self.init_select()

    def __init_tree(self, items_list, insert_pos=None):
        if items_list:
            container_remove_all(self.buttonbox)
            self.connection_tree.add_items(map(lambda c: SettingItem(c, None), items_list), insert_pos=insert_pos)
            self.buttonbox.add(self.connection_tree)

    def delete_item_cb(self, widget, connection):
        '''docstring for delete_item_cb'''
        from nmlib.nm_remote_connection import NMRemoteConnection
        self.connection_tree.delete_select_items()
        if isinstance(connection, NMRemoteConnection):
            connection.delete()
        else:
            index = self.connections.index(connection)
            self.connections.pop(index)
        container_remove_all(self.buttonbox)
        self.buttonbox.add(self.connection_tree)
        #self.resize_tree()

    def resize_tree(self):
        if self.connection_tree.visible_items != []:
            self.connection_tree.set_size_request(-1,len(self.connection_tree.visible_items) * self.connection_tree.visible_items[0].get_height())
        else:
            container_remove_all(self.buttonbox)

    def get_active(self):
        return self.connection_tree.select_rows[0]

    def set_active(self, connection):
        index = self.connections.index(connection)
        con = self.connection_tree.visible_items[index]
        self.connection_tree.select_items([con])
    
    def add_new_connection(self):
        "new connection format (connection, index)"
        new_connection, index = self.new_connection()
        if index is -1:
            self.connections.append(new_connection)
            self.__init_tree([new_connection])
        else:
            self.connecttions.insert(index, new_connection)
            self.__init_tree([new_connection], index)

        connect = self.connection_tree.visible_items[index]
        self.connection_tree.select_items([connect])
    
    def init_select(self):
        try:
            self.connection_tree.select_first_item()
        except:
            print "no connections found"

    def replace_connection(self, widget, connection):
        '''
        This is a method used to solve fake connection save thing,
        '''
        print "replace connections"
        index = self.get_active()
        self.connections[index] = connection
        self.connection_tree.delete_item_by_index(index)
        self.__init_tree([connection], index)
        self.set_active(connection)