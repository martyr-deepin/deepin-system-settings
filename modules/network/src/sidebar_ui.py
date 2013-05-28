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

from dtk.ui.treeview import TreeView
from dtk.ui.utils import container_remove_all
from settings_widget import SettingItem, AddSettingItem, EntryTreeView
from nmlib.nm_remote_connection import NMRemoteConnection
from helper import Dispatcher
import style

import gtk
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
        #self.connection_tree = EntryTreeView()
        self.add_button = AddSettingItem(_("New Connection") ,self.add_new_connection)
        add_setting_tree = TreeView([self.add_button])
        add_setting_tree.set_expand_column(1)
        self.pack_start(add_setting_tree, False, False)
        self.set_size_request(160, -1)
        self.show_all()

        self.__init_signals()

    def __init_signals(self):
        Dispatcher.connect("connection-delete", self.delete_item_cb)
        Dispatcher.connect("connection-replace", self.replace_connection)

        # This one just for mobile setting
        Dispatcher.connect("region-back", self.append_new_connection)

    def load_list(self, network_object):
        '''
        will add hasattr part for network_object
        '''
        self.network_object = network_object
        self.connections = self.network_object.get_connections()
        print self.connections, "load_list"
        connections = []
        for connection in self.connections:
            if isinstance(connection, NMRemoteConnection):
                connection.init_settings_prop_dict()
            connections.append(connection)
        self.connections = connections
        self.connection_tree = EntryTreeView()
        self.connection_tree.set_expand_column(1)
        self.__init_tree(self.connections)

        if hasattr(self.network_object, "add_new_connection"):
            self.new_connection = self.network_object.add_new_connection
            #self.add_button.change_add_setting(self.network_object.add_new_connection)
        if hasattr(self.network_object, "delete_item"):
            pass
        self.init_select(network_object.spec_connection)
        # FIXME: COME ON, why check the connections count?!
        #if self.connections !=[]:
        crumb_name = network_object.crumb_name
        if crumb_name == "":
            crumb_name = _("Hidden network")
        Dispatcher.send_submodule_crumb(2, crumb_name)
        Dispatcher.slide_to_page("setting", "right")

    def __init_tree(self, items_list, insert_pos=None):
        if items_list and items_list != [None, -1]:
            print items_list, "__init_tree"
            container_remove_all(self.buttonbox)
            self.connection_tree.add_items(map(lambda c: SettingItem(c, None), items_list), insert_pos=insert_pos)
            self.buttonbox.pack_start(self.connection_tree, False, False)

    def delete_item_cb(self, widget, connection):
        '''docstring for delete_item_cb'''
        self.connection_tree.delete_select_items()
        if isinstance(connection, NMRemoteConnection):
            connection.delete()
            if hasattr(self.network_object, "delete_request_redraw"):
                print "redraw"
                self.network_object.delete_request_redraw()
        else:
            index = self.connections.index(connection)
            self.connections.pop(index)
        if len(self.connection_tree.visible_items) == 0:
            Dispatcher.to_main_page()
            return
        self.connection_tree.select_last_item()
        container_remove_all(self.buttonbox)
        self.buttonbox.add(self.connection_tree)
    
    #def delete_request_redraw(self):
        #pass

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
        if new_connection == None:
            return

        if index is -1:
            self.connections.append(new_connection)
            self.__init_tree([new_connection])
        else:
            self.connections.insert(index, new_connection)
            self.__init_tree([new_connection], index)

        connect = self.connection_tree.visible_items[index]
        self.connection_tree.select_items([connect])

    def append_new_connection(self, widget, connection, prop_dict, type):
        if isinstance(connection, NMRemoteConnection):
            index = self.connections.index(connection)
            conn = self.connection_tree.visible_items[index]
            self.connection_tree.select_items([conn])
        else:
            self.__init_tree([connection])
            self.connections.append(connection)
            conn = self.connection_tree.visible_items[-1]
            self.connection_tree.select_items([conn])

        broadband = self.network_object.get_broadband(connection)
        broadband.set_new_values(prop_dict, type)
    
    def init_select(self, spec_connection=None):
        if spec_connection:
            self.set_active(spec_connection)
        else:
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
