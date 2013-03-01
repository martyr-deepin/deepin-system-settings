#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dss import app_theme
from dtk.ui.button import ImageButton, ToggleButton, Button
from dtk.ui.dialog import DialogBox
from dtk.ui.new_entry import InputEntry, PasswordEntry
from nm_modules import nm_module
from nmlib.nm_remote_connection import NMRemoteConnection

from dtk.ui.locales import _
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
                 #title, 
                 #init_text, 
                 default_width=330,
                 default_height=145,
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
        DialogBox.__init__(self, "Set password", default_width, default_height, DIALOG_MASK_SINGLE_PAGE)
        self.confirm_callback = confirm_callback
        self.cancel_callback = cancel_callback

        self.connection = connection
        ssid = self.connection.get_setting("802-11-wireless").ssid
        print ssid
        
        self.hint_align = gtk.Alignment()
        self.hint_align.set(0.5, 0.5, 0, 0)
        self.hint_align.set_padding(0, 0, 8, 8)
        self.hint_text = Label("Please input password for %s :"%ssid,
                               enable_select=False,
                               enable_double_click=False)
        self.hint_align.add(self.hint_text)

        self.entry_align = gtk.Alignment()
        self.entry_align.set(0.5, 0.5, 0, 0)
        self.entry_align.set_padding(0, 0, 8, 8)
        if self.connection and isinstance(self.connection, NMRemoteConnection):
            (setting_name, method) = self.connection.guess_secret_info() 
            init_text = nm_module.secret_agent.agent_get_secrets(self.connection.object_path,
                                                    setting_name,
                                                    method)
        else:
            init_text = ''
        self.entry = PasswordEntry(init_text)

        self.entry.set_size(default_width - 20, 25)
        
        self.encry_list = [(_("None"), None),
                      (_("WEP (Hex or ASCII)"), "none"),
                      (_("WEP 104/128-bit Passphrase"), "none"),
                      (_("WPA WPA2 Personal"), "wpa-psk")]
        
        self.confirm_button = Button(_("OK"))
        self.cancel_button = Button(_("Cancel"))
        
        self.confirm_button.connect("clicked", lambda w: self.click_confirm_button())
        self.cancel_button.connect("clicked", lambda w: self.click_cancel_button())
        
        self.entry_align.add(self.entry)
        self.body_box.pack_start(self.hint_align, True, True)
        self.body_box.pack_start(self.entry_align, True, True)
        
        self.right_button_box.set_buttons([self.confirm_button, self.cancel_button])
        
        self.connect("show", self.focus_input)
        
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
        
class CheckButtonM(ToggleButton):

    def __init__(self, group,connection ,callback,padding_x = 8):
        self.label = connection.get_setting("connection").id

        ToggleButton.__init__(self,
                              app_theme.get_pixbuf("network/check_box_out.png"),
                              app_theme.get_pixbuf("network/check_box.png"),
                              button_label = self.label, padding_x = padding_x)
        self.group_list = []
        self.leader = None
        self.callback = callback
        self.connection = connection
        
        if group == None:
            self.group_list.append(self)
            self.leader = self
        else:
            self.leader = group.check
            self.leader.group_list.append(self)

        self.connect("toggled", self.toggled_button)

    def toggled_button(self, widget):
        if widget.get_active():
            for i in self.leader.group_list:
                if not  i == widget and i.get_active() == True:
                    i.set_active(False)
            self.callback(self.connection)

class SettingButton(gtk.HBox):

    def __init__(self, group, connection,setting, callback):
        gtk.HBox.__init__(self)


        self.check = CheckButtonM(group, connection, callback)
        self.setting = setting

        self.pack_start(self.check, False, False)
        
        right_action_button_pixbuf = app_theme.get_pixbuf("network/delete.png")
        self.right_button = ImageButton(right_action_button_pixbuf,
                                       right_action_button_pixbuf,
                                       right_action_button_pixbuf)
        #self.right_button.set_no_show_all(True)
        width = right_action_button_pixbuf.get_pixbuf().get_width()
        height = right_action_button_pixbuf.get_pixbuf().get_height()
        #hbox = gtk.EventBox()
        #hbox.set_visible_window(False)
        #hbox.connect("button-press-event", self.delete_setting, connection)
        #hbox.set_size_request(width, height)
        self.pack_end(self.right_button, False ,False, 0)
        self.right_button.connect("clicked", self.delete_setting, connection)
        #hbox.connect("enter-notify-event", self.enter_notify)
        #hbox.connect("leave-notify-event", self.leave_notify)
        self.show_all()
    
    def delete_setting(self, widget, connection):
        connection.delete()
        self.setting.destroy()
        self.destroy()

    def enter_notify(self, widget, event):
        pass
        #container_remove_all(widget)    
        #widget.add(self.right_button)
        #self.queue_draw()
        ##widget.show_all()
         
        #self.right_button.set_no_show_all(False)
        #self.right_button.show()
        #return False

    def leave_notify(self, widget, event):
        pass
        #container_remove_all(widget)    
        #self.right_button.hide()
        #return False

        
#class MyEntry(Entry):

    #def handle_button_press(self, widget, event):
        ## Select all when double click left button.
        #if is_double_click(event):
            #self.double_click_flag = True
            #self.grab_focus()
            #self.select_all()

#class SettingButton(gtk.EventBox):
    #HORIZONAL_PADDING = 10
    #VERITCAL_PADDING = 5

    #def __init__(self, group, connection, setting, callback): 
        ## Init
        #gtk.EventBox.__init__(self) 
        #self.setting = setting
        ##self.set_visible_window(False)
        #self.label = connection.get_setting("connection").id 
        #left_action_button_pixbuf = app_theme.get_pixbuf("Network/check_box.png") 
        #left_action_button_pixbuf_out = app_theme.get_pixbuf("Network/check_box_out.png") 
        #right_action_button_pixbuf = app_theme.get_pixbuf("Network/delete.png") 

        #self.left_width = left_action_button_pixbuf.get_pixbuf().get_width()
        #self.right_width = right_action_button_pixbuf.get_pixbuf().get_width()
        #self.height = left_action_button_pixbuf.get_pixbuf().get_height()

        ##self.left_button = ToggleButton(left_action_button_pixbuf_out, 
                                       ##left_action_button_pixbuf)
        #self.left_button = CheckButtonM(group, connection, callback)
        #self.right_button = ToggleButton(right_action_button_pixbuf,
                                       #right_action_button_pixbuf,
                                       #right_action_button_pixbuf)
        #self.entry = MyEntry()
        #self.entry.set_text(self.label)
        #self.entry.connect("press-return", self.return_pressed)
        #self.entry.show()

        #self.hbox = gtk.HBox()
        #left_align = gtk.Alignment(0, 0.5, 0, 0)
        #left_align.set_padding(0,0,self.HORIZONAL_PADDING, 0)
        #left_align.add(self.left_button)
        #self.hbox.pack_start(left_align, False , False ,0)

        #mid_align = gtk.Alignment(0.5,0.5,0,0)
        #mid_align.add(self.entry)
        #self.hbox.pack_start(mid_align, False, False, 0)

        #right_align = gtk.Alignment(0, 0.5, 0, 0)
        #right_align.set_padding(0,0,0,self.HORIZONAL_PADDING)
        #right_align.add(self.right_button)
        #self.hbox.pack_end(right_align, False, False, 0)
        #self.add(self.hbox)
        #self.show_all()
        ##self.hbox.connect("expose-event", self.expose_event)
        ##self.right_button.connect("clicked", self.delete_setting, connection)

        #self.set_events(gtk.gdk.BUTTON_PRESS_MASK|
                        #gtk.gdk.POINTER_MOTION_MASK)
        ##self.connect("button-press-event", self.button_press)

    #def return_pressed(self, widget):
        #widget.grab_focus_flag = False
        #widget.im.focus_out()
        #self.queue_draw()

    #def clicked_event(self, widget):
        #pass


    #def delete_setting(self, widget,connection):
        #print "safsdf"
        #connection.delete()
        #self.destroy()
        #self.setting.destroy()
        

    #def expose_event(self, widget, event):
        #cr = widget.window.cairo_create()
        #rect = widget.allocation
        #x, y, w, h = rect.x, rect.y, rect.width, rect.height

        ## Draw frame.
        #with cairo_disable_antialias(cr):
            #cr.set_line_width(1)
            #cr.set_source_rgb(*color_hex_to_cairo(ui_theme.get_color("combo_entry_frame").get_color()))
            #cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            #cr.stroke()
            
            #cr.set_source_rgba(*alpha_color_hex_to_cairo((ui_theme.get_color("combo_entry_background").get_color(), 0.9)))
            #cr.rectangle(rect.x, rect.y, rect.width - 1, rect.height - 1)
            #cr.fill()

    #def set_size(self, width):
        #self.set_size_request(width, self.height + 2 * self.VERITCAL_PADDING)

        #self.entry.set_size_request(width - self.left_width - self.right_width- 2*self.HORIZONAL_PADDING , self.height + 2 * self.VERITCAL_PADDING)
        #padding = (self.left_width + self.right_width)/2 + self.HORIZONAL_PADDING
        ##self.entry.padding_x = padding 

        

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
    
    mm = nm_module.nm_remote_settings.get_wireless_connections()[1]
    my_button.connect("clicked", lambda w: AskPasswordDialog(mm).show_all())
    my_button.set_size_request(200, 200)
    align.add(my_button)
    win.add(align)

    win.show_all()
    
    gtk.main()
