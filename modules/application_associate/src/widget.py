#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dss import app_theme
from dtk.ui.dialog import DialogBox, OpenFileDialog
from dtk.ui.button import Button
from dtk.ui.entry import InputEntry
from dtk.ui.label import Label
from dtk.ui.button import ImageButton
from dtk.ui.theme import DynamicPixbuf

import gtk
import style
from nls import _
DIALOG_MASK_SINGLE_PAGE = 0
DIALOG_MASK_GLASS_PAGE = 1
DIALOG_MASK_MULTIPLE_PAGE = 2
DIALOG_MASK_TAB_PAGE = 3

class NewSessionDialog(DialogBox):
    '''
    Simple input dialog.
    
    @undocumented: click_confirm_button
    @undocumented: click_cancel_button
    '''
	
    def __init__(self,
                 new_session,
                 default_width=350,
                 default_height=160,
                 confirm_callback=None, 
                 cancel_callback=None):
        '''
        Initialize InputDialog class.
        
        @param title: Input dialog title.
        @param init_text: Initialize input text.
        @param default_width: Width of dialog, default is 330 pixel.
        @param default_height: Height of dialog, default is 330 pixel.
        @param confirm_callback: Callback when user click confirm button, this callback accept one argument that return by user input text.
        @param cancel_callback: Callback when user click cancel button, this callback not need argument.
        '''
        # Init.
        DialogBox.__init__(self, _("Autostart app"), default_width, default_height, DIALOG_MASK_SINGLE_PAGE)
        self.confirm_callback = confirm_callback
        self.cancel_callback = cancel_callback
        
        self.new_session = new_session
        self.app_name = self.new_session.name
        self.command = self.new_session.get_option("Exec")
        self.desc = self.new_session.get_option("Comment")
        
        self.confirm_button = Button(_("OK"))
        self.cancel_button = Button(_("Cancel"))
        
        self.confirm_button.connect("clicked", lambda w: self.click_confirm_button())
        self.cancel_button.connect("clicked", lambda w: self.click_cancel_button())
        self.connect("destroy", self.close_callback)
        # get system pixbuf
        icon_theme = gtk.IconTheme()
        icon_theme.set_custom_theme("Deepin")
        icon_info = None
        if icon_theme:
            icon_info = icon_theme.lookup_icon("folder-open", 16, gtk.ICON_LOOKUP_NO_SVG)
        
        
        self.icon_pixbuf = None
        if icon_info:
            self.icon_pixbuf = DynamicPixbuf(icon_info.get_filename())
        else:
            self.icon_pixbuf = app_theme.get_pixbuf("navigate/none-small.png")
        
        table = self.add_new_box() 
        self.pack(self.body_box, [table])
        self.right_button_box.set_buttons([self.cancel_button, self.confirm_button])
        
        self.connect("show", self.focus_input)


    def pack(self, container, widgets, expand=False, fill=False):
        for widget in widgets:
            container.pack_start(widget, expand, fill)

    def add_new_box(self):
        table = gtk.Table()
        #hbox.set_size_request(-1, 30)
        name_label = Label(_("Name:"), enable_select=False)
        name_label.set_can_focus(False)
        exec_label = Label(_("Exec:"), enable_select=False)
        exec_label.set_can_focus(False)
        desc_label = Label(_("Comment:"), enable_select=False)
        desc_label.set_can_focus(False)
        
        self.name_entry = InputEntry()
        self.exec_entry = InputEntry()
        self.desc_entry = InputEntry()
        self.name_entry.set_text(self.app_name)
        self.exec_entry.set_text(self.command)
        self.desc_entry.set_text(self.desc)
        self.name_entry.set_size(200, 22)
        self.exec_entry.set_size(200, 22)
        self.desc_entry.set_size(200, 22)
        # self.name_entry.entry.connect("changed", self.entry_changed, "Name")
        # self.exec_entry.entry.connect("changed", self.entry_changed, "Exec")
        # self.desc_entry.entry.connect("changed", self.entry_changed, "Comment")

        
        #entry_list = [name_entry, exec_entry, desc_entry]
        #for entry in entry_list:
            #entry.set_size(200, 22)
            #entry.connect("changed", )
        name_label_align = self.wrap_with_align(name_label)
        exec_label_align = self.wrap_with_align(exec_label)
        desc_label_align = self.wrap_with_align(desc_label)

        name_align = style.wrap_with_align(self.name_entry)
        exec_align = style.wrap_with_align(self.exec_entry)
        desc_align = style.wrap_with_align(self.desc_entry)

        table = gtk.Table(3, 4)
        self.table_add(table, [name_label_align, exec_label_align, desc_label_align], 0)
        self.table_add(table, [name_align, exec_align, desc_align], 1)

        open_folder = ImageButton(self.icon_pixbuf, self.icon_pixbuf, self.icon_pixbuf)
        open_folder.connect("clicked", lambda w: OpenFileDialog("Choose file", self, ok_callback=self.ok_callback))
        table.attach(style.wrap_with_align(open_folder), 2, 3, 1, 2)
        
        align = gtk.Alignment(0.5, 0, 0, 0)
        style.set_table(table)
        align.add(table)
        return align

    def entry_changed(self, widget, content, option):
        self.new_session.set_option(option, content)
    
    def table_add(self, table,  widget, column):
        for index, w in enumerate(widget):
            table.attach(w, column, column + 1, index, index + 1)

    def wrap_with_align(self, label):

        align = gtk.Alignment(1, 0.5, 0, 0)
        align.set_padding(0, 0, 1, 0)
        align.add(label)
        return align

    def ok_callback(self, file_name):
        self.exec_entry.set_text(file_name)

    def close_callback(self, widget):
        self.cancel_callback()
        self.destroy()

        
    def focus_input(self, widget):
        '''
        Grab focus on input entry.
        
        @param widget: InputDialog widget.
        '''
        self.name_entry.entry.grab_focus()        
        
    def click_confirm_button(self):
        '''
        Inernal fucntion to handle click confirm button.
        '''
        name = self.name_entry.get_text()
        exec_ = self.exec_entry.get_text()
        comment = self.desc_entry.get_text()
        
        self.new_session.set_option("Name", name)
        self.new_session.set_option("Exec", exec_)
        self.new_session.set_option("Comment", comment)
        
        if self.confirm_callback != None:
            self.confirm_callback(self.new_session)        
        
        self.destroy()
        
    def click_cancel_button(self):
        '''
        Inernal fucntion to handle click cancel button.
        '''
        if self.cancel_callback != None:
            self.cancel_callback()
        
        self.destroy()
