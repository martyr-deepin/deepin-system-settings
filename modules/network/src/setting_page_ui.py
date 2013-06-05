#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dss import app_theme
import gtk
import style
from foot_box_ui import FootBox
from dtk.ui.paned import HPaned
from sidebar_ui import SideBar
from dtk.ui.utils import container_remove_all
from dtk.ui.scrolled_window import ScrolledWindow
from nmlib.nm_remote_connection import NMRemoteConnection
#from shared_widget import Settings

from helper import Dispatcher
class SettingUI(gtk.Alignment):

    def __init__(self, slide_back_cb, change_crumb_cb):
        gtk.Alignment.__init__(self, 0, 0, 0, 0)
        self.slide_back = slide_back_cb
        self.change_crumb = change_crumb_cb
        #style.set_main_window(self)
        
        self.scroll_win = ScrolledWindow()
        self.scroll_win.set_can_focus(False)
        #style.draw_background_color(align)

        self.scroll_win.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        main_vbox = gtk.VBox()
        self.foot_box = FootBox()
        self.hbox = gtk.HBox()

        self.scroll_win.add_with_viewport(self.hbox)
        self.scroll_align = gtk.Alignment()
        self.scroll_win.set_size_request(800, 435)
        self.scroll_align.set(0, 0, 0, 0)
        self.scroll_align.set_padding(0, 0, 30, 0)
        self.scroll_align.add(self.scroll_win)
        
        padding_align = gtk.Alignment(0, 0, 0, 0)
        padding_align.set_padding(15, 0, 0, 0)
        self.sidebar = SideBar( None)
        padding_align.add(self.sidebar)
        self.hpaned = MyPaned()
        self.hpaned.set_size_request(800, -1)
        self.hpaned.connect("expose-event",self.expose_line)
        #self.hpaned.do_enter_notify_event = self.enter_notify_event
        self.hpaned.add1(padding_align)
        self.hpaned.add2(self.scroll_align)
        self.connect_after("show", self.__init_paned)
        main_vbox.pack_start(self.hpaned, True, True)
        main_vbox.pack_start(self.foot_box, False, False)
        self.add(main_vbox)

        self.__init_signals()

    def enter_notify_event(self, e):
        pass

    def __init_paned(self, widget):
        self.hpaned.saved_position = 160
        self.hpaned.set_position(1)
        self.hpaned.animation_position_frames = [0]
        self.hpaned.update_position()

    def __init_tab_box(self):
        self.__init_paned(None)
        #container_remove_all(self.hbox)

    def __init_signals(self):
        Dispatcher.connect("connection-change", self.switch_tab)
        Dispatcher.connect("setting-saved", self.save_connection_setting)
        Dispatcher.connect("setting-appled", self.apply_connection_setting)
        Dispatcher.connect("request_redraw", lambda w: self.scroll_win.show_all())

    def load_module(self, module_obj, hide_left):
        #self.__init_tab()
        self.__init_tab_box()

        self.hpaned.set_button_show(hide_left)

        # need this for corect button set
        self.foot_box.set_setting(module_obj)
        self.setting_group = module_obj
        self.sidebar.load_list(module_obj)
        self.apply_method = module_obj.apply_changes
        self.save_method = module_obj.save_changes

    def __init_tab(self):
        tabs = self.tab_window.tab_items
        if tabs:
            self.tab_window.delete_items(tabs)

    def switch_tab(self, widget, connection):
        #print "switch tab"
        container_remove_all(self.hbox)
        self.set_tab_content(connection)
        self.set_foot_bar_button(connection)
    
        self.focus_connection = connection

    def set_foot_bar_button(self, connection):
        states = self.setting_group.get_button_state()

        if type(connection) == NMRemoteConnection:
            self.foot_box.show_delete(connection)
        else:
            self.foot_box.hide_delete()

        if states:
            Dispatcher.set_button(*states)
        
    def set_tab_content(self, connection, init_connection=False):
        setting = self.setting_group.init_items(connection)
        self.hbox.add(setting)
        #self.hbox.queue_draw()
        self.hbox.show_all()
        self.foot_box.set_lock(False)

    def expose_line(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        style.draw_out_line(cr, rect, exclude=["left", "right", "top"])

    def draw_tab_title_background(self, cr, widget):
        rect = widget.allocation
        cr.set_source_rgb(1, 1, 1)    
        cr.rectangle(0, 0, rect.width, rect.height - 1)
        cr.fill()

    def save_connection_setting(self, widget):
        self.save_method(self.focus_connection)

    def apply_connection_setting(self, widget):
        #print type(self.focus_connection)
        self.apply_method(self.focus_connection)

    def create_new_connection(self):
        self.sidebar.add_new_connection()

class MyPaned(HPaned):

    def __init__(self):
        HPaned.__init__(self,
                        always_show_button=True)
        self.no_show_button = False

    def do_enter_notify_event(self, e):
        pass

    def set_button_show(self, hide):
        self.no_show_button = hide
        self.always_show_button = not hide
        self.queue_draw()
        
    def do_motion_notify_event(self, e):
        '''
        change the cursor style  when move in handler
        '''
        # Reset press coordinate if motion mouse after press event.

        handle = self.get_handle_window()
        if self.no_show_button:
            handle.set_cursor(None)
            return
        self.press_coordinate = None
        
        (width, height) = handle.get_size()
        if self.is_in_button(e.x, e.y):
            handle.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
            
            self.init_button("hover")
        else:
            if self.enable_drag:
                handle.set_cursor(self.cursor_type)
                gtk.Paned.do_motion_notify_event(self, e)                
            else:    
                handle.set_cursor(None)
            self.init_button("normal")

    #def do_button_press_event(self, e):
        #'''
        #when press the handler's button change the position.
        #'''
        #if self.no_show_button:
            #return
        #handle = self.get_handle_window()
        #if e.window == handle:
            #if self.is_in_button(e.x, e.y):
                #self.init_button("press")
            
                #self.do_press_actoin()
            #else:
                #(width, height) = handle.get_size()
                #if is_in_rect((e.x, e.y), (0, 0, width, height)):
                    #self.press_coordinate = (e.x, e.y)
            
                #gtk.Paned.do_button_press_event(self, e)
        #else:
            #gtk.Paned.do_button_press_event(self, e)
        #return True
    

if __name__=="__main__":
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_title("Container")
    #win.border_width(2)

    win.connect("destroy", lambda w: gtk.main_quit())
    
    setting_page = SettingUI(None, None)
    setting_page.load_module(LanSetting(None))

    #vbox = gtk.VBox(False)
    #vbox.pack_start(con)
    win.add(setting_page)
    win.show_all()

    gtk.main()
