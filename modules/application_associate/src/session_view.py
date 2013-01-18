#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dtk.ui.new_treeview import TreeView
from dtk.ui.button import Button
from treeview import SessionItem

import gtk
import style
from session import SessionManager
from foot_box import FootBox
sessions = SessionManager()

class SessionView(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)
        
        # UI style
        style.draw_background_color(self)
        self.tree = TreeView([],enable_drag_drop=False,
                             enable_hover=True)

        self.tree.set_column_titles(("App", "State", "Des"), self.sort_method)

        self.tree.set_size_request(727, 337)

        self.tree.draw_mask = self.draw_mask
        self.tree.add_items(self.get_list())
        align = gtk.Alignment(0.5, 0.5, 0, 0)
        align.set_padding(15, 0 , 20, 20)
        align.add(self.tree)
        align.connect("expose-event", self.expose_line)


        #hbox = gtk.HBox(spacing=5)
        add_button = Button("添加")
        delete_button = Button("删除")
        add_button.connect("clicked", self.add_autostart)
        
        foot_box = FootBox(adjustment=15)
        foot_box.set_buttons([add_button, delete_button])
        self.pack_start(align, True, True)
        self.pack_end(foot_box, False, False)
        self.show_all()

    def expose_line(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        style.draw_out_line(cr, rect, exclude=["left", "right", "top"])
    
    def sort_method(self):
        pass

    def add_autostart(self, widget):
        pass

    def pack(self, parent, widget_list, expand=False, fill=False):
        for w in widget_list:
            parent.pack_start(w, expand, fill)

    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()

    def get_list(self):
        usr_list = sessions.list_user_auto_starts()
        return map(lambda w: SessionItem(w), usr_list)
