#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dss import app_theme
from dtk.ui.tab_window import TabBox
import gtk
import style
from foot_box_ui import FootBox
from dtk.ui.paned import HPaned
from sidebar_ui import SideBar
from dtk.ui.utils import container_remove_all
from dtk.ui.scrolled_window import ScrolledWindow
#from shared_widget import Settings

from helper import Dispatcher
class SettingUI(gtk.Alignment):

    def __init__(self, slide_back_cb, change_crumb_cb):
        gtk.Alignment.__init__(self, 0, 0, 0, 0)
        self.slide_back = slide_back_cb
        self.change_crumb = change_crumb_cb
        #style.set_main_window(self)
        
        self.scroll_win = ScrolledWindow()
        #style.draw_background_color(align)

        self.scroll_win.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        main_vbox = gtk.VBox()
        self.foot_box = FootBox()
        self.hbox = gtk.HBox()
        self.hbox.connect("expose-event",self.expose_line)

        #self.add(self.scroll_win)
        self.scroll_win.add_with_viewport(self.hbox)
        self.scroll_align = gtk.Alignment()
        self.scroll_align.set(0, 0, 0, 0)
        self.scroll_align.set_padding(0, 0, 30, 0)
        self.scroll_align.add(self.scroll_win)
        
        padding_align = gtk.Alignment(0, 0, 0, 0)
        padding_align.set_padding(15, 0, 0, 0)
        self.sidebar = SideBar( None)
        padding_align.add(self.sidebar)
        self.hpaned = HPaned(always_show_button=True)
        self.hpaned.add1(padding_align)
        self.hpaned.add2(self.scroll_align)
        self.connect_after("show", self.__init_paned)
        main_vbox.pack_start(self.hpaned, True, True)
        main_vbox.pack_start(self.foot_box, False, False)
        self.add(main_vbox)
        # Build ui
        #self.hbox.pack_start(self.hpaned, False , False)
        style.draw_background_color(self)
        style.draw_separator(self.sidebar, 3)

        self.__init_signals()

    def __init_paned(self, widget):
        self.hpaned.saved_position = 150
        self.hpaned.change_position(1)

    def __init_tab_box(self):
        #container_remove_all(self.hbox)
        self.scroll_win.set_size_request(800, 425)

    def __init_signals(self):
        Dispatcher.connect("connection-change", self.switch_tab)
        Dispatcher.connect("setting-saved", self.save_connection_setting)
        Dispatcher.connect("setting-appled", self.apply_connection_setting)
        Dispatcher.connect("request_redraw", lambda w: self.scroll_win.show_all())

    def load_module(self, module_obj):
        #self.__init_tab()
        self.__init_tab_box()
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
        print "switch tab"
        container_remove_all(self.hbox)
        self.set_tab_content(connection)
        self.set_foot_bar_button(connection)
    
        self.focus_connection = connection

    def set_foot_bar_button(self, connection):
        states = self.setting_group.get_button_state()
        Dispatcher.set_button(*states)
        
    def set_tab_content(self, connection, init_connection=False):
        setting = self.setting_group.init_items(connection)
        self.hbox.add(setting)
        self.hbox.queue_draw()
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
        print type(self.focus_connection)
        self.apply_method(self.focus_connection)

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
