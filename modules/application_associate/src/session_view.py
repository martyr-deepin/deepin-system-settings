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
from session import SessionManager
from widget import NewSessionDialog
from foot_box import FootBox
from nls import _
sessions = SessionManager()

class SessionView(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)
        self.new_session = None
        self.open_dialog = False
        
        # UI style
        style.draw_background_color(self)
        self.tree = TreeView([],enable_drag_drop=False,
                             enable_hover=True,
                             enable_multiple_select=False,
                             )
        self.tree.set_expand_column(2)
        self.tree.set_column_titles((_("Application"), _("Exec"), _("Description")),)

        self.tree.set_size_request(800, -1)
        self.tree.connect("right-press-items", self.right_press_item)

        self.tree.draw_mask = self.draw_mask
        self.tree.add_items(self.get_list())
        align = gtk.Alignment(0, 0, 0, 1)
        align.set_padding(15, 0, 20, 20)
        align.add(self.tree)
        align.connect("expose-event", self.expose_line)


        add_button = Button(_("New"))
        delete_button = Button(_("Delete"))
        add_button.connect("clicked", self.add_autostart)
        delete_button.connect("clicked", self.delete_autostart)
        
        foot_box = FootBox(adjustment=15)
        foot_box.set_buttons([add_button, delete_button])
        self.pack_start(align, True, True)
        
        #self.new_box = self.add_new_box()

        self.pack_end(foot_box, False, False)
        #self.pack_end(self.new_box, False, False)

        self.show_all()

    def add_new_box(self):
        hbox = gtk.HBox()
        hbox.set_size_request(-1, 30)
        name_label = Label("Name:")
        exec_label = Label("Exec:")
        desc_label = Label("Description:")
        
        name_entry = InputEntry()
        exec_entry = InputEntry()
        desc_entry = InputEntry()
        name_entry.set_size(200, 22)
        exec_entry.set_size(200, 22)
        desc_entry.set_size(200, 22)
        name_entry.entry.connect("changed", self.entry_changed, "Name")
        exec_entry.entry.connect("changed", self.entry_changed, "Exec")
        desc_entry.entry.connect("changed", self.entry_changed, "Comment" + sessions.locale())

        
        #entry_list = [name_entry, exec_entry, desc_entry]
        #for entry in entry_list:
            #entry.set_size(200, 22)
            #entry.connect("changed", )

        name_align = style.wrap_with_align(name_entry)
        exec_align = style.wrap_with_align(exec_entry)
        desc_align = style.wrap_with_align(desc_entry)

        self.pack(hbox, [name_label, name_align, exec_label, exec_align, desc_label, desc_align])
        return hbox
    
    def right_press_item(self, widget,  x_root, y_root, current_item, select_items):
        for item in select_items:
            item.unselect()
        if current_item != None:
            session = current_item.item
            #self.tree.unselect_all()
            current_item.select()
            if self.open_dialog == False:
                NewSessionDialog(session, confirm_callback= self.edit_done, cancel_callback = self.cancel_callback).show_all()
                self.open_dialog = True

    def expose_line(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        style.draw_out_line(cr, rect, exclude=["left", "right", "top"])
    
    def sort_method(self):
        pass

    def add_autostart(self, widget):
        self.new_session = sessions.add("","","")
        if self.open_dialog == False:
            NewSessionDialog(self.new_session, confirm_callback= self.confirm_callback, cancel_callback = self.cancel_callback).show_all()
            self.open_dialog = True

    def delete_autostart(self, widget):
        items = map(lambda row: self.tree.visible_items[row], self.tree.select_rows)
        item = items[0].item
        item.delete()
        self.tree.delete_select_items()
        if self.tree.visible_items == []:
            self.tree.add_items([NothingItem()])


    def entry_changed(self, widget, content, option):
        self.new_session.set_option(option, content)

    def edit_done(self, session):
        session.save(session.file_name)
        self.new_session = None
        items = map(lambda row: self.tree.visible_items[row], self.tree.select_rows)
        self.tree.redraw_request(items, True)
        self.open_dialog = False

    def confirm_callback(self, session):
        session.save(session.get_option("Name"))
        items = self.tree.visible_items
        if len(items) == 1 and type(items[0]) is NothingItem:
            self.tree.delete_all_items()
        self.tree.add_items([SessionItem(session)]) 
        self.new_session = None
        self.open_dialog = False

    def cancel_callback(self):
        self.new_session = None
        self.open_dialog = False

    def pack(self, parent, widget_list, expand=False, fill=False):
        for w in widget_list:
            parent.pack_start(w, expand, fill)

    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()

    def get_list(self):
        usr_list = sessions.list_user_auto_starts()
        if usr_list:
            return map(lambda w: SessionItem(w), usr_list)
        else:
            return [NothingItem()]
