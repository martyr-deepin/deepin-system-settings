#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dtk.ui.button import Button, CheckButton
from dtk.ui.dialog import DialogBox
from dtk.ui.entry import PasswordEntry
from nm_modules import nm_module
from nmlib.nm_remote_connection import NMRemoteConnection

from nls import _
from dtk.ui.label import Label
import gtk

DIALOG_MASK_SINGLE_PAGE = 0
DIALOG_MASK_GLASS_PAGE = 1
DIALOG_MASK_MULTIPLE_PAGE = 2
DIALOG_MASK_TAB_PAGE = 3


class AskPasswordDialog(DialogBox):
    '''
    Simple input dialog.
    @undocumented: click_confirm_button
    @undocumented: click_cancel_button
    '''
    
    def __init__(self,
                 connection,
                 ssid,
                 key_mgmt=None,
                 #title, 
                 #init_text, 
                 default_width=330,
                 default_height=120,
                 confirm_callback=None, 
                 cancel_callback=None,
                 ):
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
        #DialogBox.__init__(self, _("Set password"), default_width, default_height, DIALOG_MASK_SINGLE_PAGE)
        DialogBox.__init__(self, _("Please input password for %s") % ssid, default_width, default_height, DIALOG_MASK_SINGLE_PAGE)
        self.confirm_callback = confirm_callback
        self.cancel_callback = cancel_callback
    
        self.connection = connection
        
        self.hint_align = gtk.Alignment()
        self.hint_align.set(0.5, 0.5, 0, 0)
        self.hint_align.set_padding(0, 0, 10, 10)
        self.hint_text = Label(_("Please input password for %s")%ssid,
                               enable_select=False,
                               enable_double_click=False)
        self.hint_align.add(self.hint_text)

        self.entry_align = gtk.Alignment()
        self.entry_align.set(0.0, 0.5, 0, 0)
        self.entry_align.set_padding(10, 0, 5, 9)
        if self.connection and isinstance(self.connection, NMRemoteConnection):
            (setting_name, method) = self.connection.guess_secret_info()  
            if setting_name and method:
                init_text = nm_module.secret_agent.agent_get_secrets(self.connection.object_path,
                                                        setting_name,
                                                        method)
            else:
                init_text = ""
        else:
            self.connection = nm_module.nm_remote_settings.new_wireless_connection(ssid, "wpa-psk")
            init_text = ''
        self.entry = PasswordEntry(init_text)
        self.show_key_check = CheckButton(_("Show key"), 0)
        self.show_key_check.connect("toggled", self.show_key_check_button_cb)

        self.entry.set_size(default_width - 22, 25)
        self.main_box = gtk.VBox()
        entry_align = gtk.Alignment(0.0, 0.5, 0, 0)
        entry_align.set_padding(0, 0, 5, 0)
        entry_align.set_size_request(-1, 30)
        entry_align.add(self.entry)
        self.main_box.pack_start(entry_align, False, False)
        self.main_box.pack_start(self.show_key_check, False, False)
        
        self.confirm_button = Button(_("OK"))
        self.cancel_button = Button(_("Cancel"))
        
        self.entry.entry.connect("press-return", lambda w: self.click_confirm_button())
        self.confirm_button.connect("clicked", lambda w: self.click_confirm_button())
        self.cancel_button.connect("clicked", lambda w: self.click_cancel_button())
        
        self.entry_align.add(self.main_box)
        #self.body_box.pack_start(self.hint_align, True, True)
        self.body_box.pack_start(self.entry_align, True, True)

        #self.body_box.pack_start(self.main_box, True, True)
        
        self.right_button_box.set_buttons([self.cancel_button, self.confirm_button])
        self.connect("show", self.focus_input)

    def __set_label(self, name):
        return Label(name, enable_select=False, enable_double_click=False)

    def show_key_check_button_cb(self, widget):
        if widget.get_active():
            self.entry.show_password(True)
        else:
            self.entry.show_password(False)

    def focus_input(self, widget):
        '''
        Grab focus on input entry.
        @param widget: InputDialog widget.
        '''
        self.entry.entry.grab_focus()        

        
    def click_confirm_button(self):
        '''
        Inernal fucntion to handle click confirm button.
        '''
        print self.connection
        if self.confirm_callback != None:
            self.confirm_callback(self.entry.entry.get_text(), self.connection)        
        self.destroy()
        
    def click_cancel_button(self):
        '''
        Inernal fucntion to handle click cancel button.
        '''
        if self.cancel_callback != None:
            self.cancel_callback()
        
        self.destroy()

if __name__ == "__main__":

    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_title("Main")
    win.set_size_request(770,500)
    win.set_border_width(11)
    win.set_resizable(True)
    win.connect("destroy", lambda w: gtk.main_quit())

    align = gtk.Alignment(1 , 1, 0,0)
    vbox = gtk.VBox()

    #my_button = SettingButton("another setting")
    my_button = gtk.Button("click")
    
    def show_dialog():
        mm = nm_module.nm_remote_settings.get_wireless_connections()
        i = filter(lambda i: i.get_setting("802-11-wireless").ssid == "linuxdeepin-1", mm)
        connection = i[0]
        ssid = connection.get_setting("802-11-wireless").ssid
        if ssid != None:
            AskPasswordDialog(connection, ssid).show_all()
        
    my_button.connect("clicked", lambda w: show_dialog())
    my_button.set_size_request(200, 200)
    align.add(my_button)
    win.add(align)

    win.show_all()
    
    gtk.main()
