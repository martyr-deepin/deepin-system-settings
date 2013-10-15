#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.                                        
#               2012 ~ 2013 Zhai Xiang                                          
#                                                                               
# Author:     Zhai Xiang <zhaixiang@linuxdeepin.com>                            
# Maintainer: Zhai Xiang <zhaixiang@linuxdeepin.com>                            
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
from dtk.ui.button import Button
from dtk.ui.label import Label
from dtk.ui.entry import InputEntry
from treeview import SessionItem, NothingItem

import gtk
import style
from session import SessionManager, get_user_config_dir
from monitor import LibraryMonitor
from widget import NewSessionDialog
from foot_box import FootBox
from nls import _
session_manager = SessionManager()

class SessionView(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)
        self.open_dialog = False
        self.tmp_editing_session = None
        
        # UI style
        style.draw_background_color(self)
        self.tree = TreeView([],enable_drag_drop=False,
                             enable_hover=True,
                             enable_multiple_select=False,
                             )
        self.tree.set_expand_column(3)
        self.tree.set_column_titles((_("Active"), _("Application"), _("Description"), _("Exec")),)

        self.tree.set_size_request(800, -1)
        self.tree.connect("right-press-items", self.right_press_item)

        self.tree.draw_mask = self.draw_mask
        self.tree.add_items(self.get_list())
        align = gtk.Alignment(0, 0, 0, 1)
        align.set_padding(15, 0, 20, 20)
        align.add(self.tree)
        align.connect("expose-event", self.expose_line)


        add_button = Button(_("New"))
        self.delete_button = Button(_("Delete"))
        add_button.connect("clicked", self.add_autostart)
        self.delete_button.connect("clicked", self.delete_autostart)
        self.delete_button.set_sensitive(False)
        
        foot_box = FootBox(adjustment=15)
        foot_box.set_buttons([add_button, self.delete_button])
        self.pack_start(align, True, True)
        
        self.pack_end(foot_box, False, False)
        #self.pack_end(self.new_box, False, False)

        self.show_all()

        self._init_monitor()

    def disable_delete_button(self, value):
        self.delete_button.set_sensitive(not value)
    def _init_monitor(self):
        self.library_monitor = LibraryMonitor(get_user_config_dir())
        self.library_monitor.set_property("monitored", True)
        self.library_monitor.connect("file-added", self.refresh_list)
        self.library_monitor.connect("location-removed", self.refresh_list)

    def right_press_item(self, widget,  x_root, y_root, current_item, select_items):
        self.tmp_editing_session = current_item.item
        for item in select_items:
            item.unselect()
        if current_item != None:
            current_item.select()
            if self.open_dialog == False:
                dialog = NewSessionDialog(confirm_callback = self.edit_done, cancel_callback = self.cancel_callback)
                dialog.name_entry.set_text(current_item.item.name)
                dialog.exec_entry.set_text(current_item.item.exec_)
                dialog.desc_entry.set_text(current_item.item.comment)
                dialog.place_center()
                dialog.show_all()
                self.open_dialog = True

    def create_session_item(self, dialog):
        name = dialog.name_entry.get_text()
        exec_ = dialog.exec_entry.get_text()
        comment = dialog.desc_entry.get_text()
        session_manager.add(name, exec_, comment)
        self.open_dialog = False

    def expose_line(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        style.draw_out_line(cr, rect, exclude=["left", "right", "top"])
    
    def sort_method(self):
        pass

    def add_autostart(self, widget):
        if self.open_dialog == False:
            dialog = NewSessionDialog(confirm_callback= self.create_session_item, cancel_callback = self.cancel_callback)
            dialog.show_all()
            self.open_dialog = True

    def delete_autostart(self, widget):
        items = map(lambda row: self.tree.visible_items[row], self.tree.select_rows)
        item = items[0].item
        item.delete()
        self.tree.delete_select_items()
        if self.tree.visible_items == []:
            self.tree.add_items([NothingItem()])

    def edit_done(self, dialog):
        self.tmp_editing_session.set_name(dialog.name_entry.get_text())
        self.tmp_editing_session.set_exec(dialog.exec_entry.get_text())
        self.tmp_editing_session.set_comment(dialog.desc_entry.get_text())
        self.tmp_editing_session.save()
        self.tmp_editing_session = None
        items = map(lambda row: self.tree.visible_items[row], self.tree.select_rows)
        self.tree.redraw_request(items, True)
        self.open_dialog = False

    def cancel_callback(self):
        self.tmp_editing_session = None
        self.open_dialog = False

    def pack(self, parent, widget_list, expand=False, fill=False):
        for w in widget_list:
            parent.pack_start(w, expand, fill)

    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()

    def get_list(self):
        usr_list = session_manager.list_autostart_items()
        if usr_list:
            return map(lambda w: SessionItem(self, w), usr_list)
        else:
            return [NothingItem()]

    def refresh_list(self, widget, gfile):
        self.tree.clear()
        self.tree.add_items(self.get_list())
        self.tree.show()
