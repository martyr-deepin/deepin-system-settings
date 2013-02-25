#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dss import app_theme
from dtk.ui.tab_window import TabBox
import gtk
import style
from foot_box_ui import FootBox
from sidebar_ui import SideBar

from nm_modules import nm_module
from lan_config import Wired
from shared_widget import IPV4Conf, IPV6Conf
#from shared_widget import Settings

from helper import Dispatcher
class SettingUI(gtk.Alignment):

    def __init__(self, slide_back_cb, change_crumb_cb):
        gtk.Alignment.__init__(self, 0, 0, 0, 0)
        self.slide_back = slide_back_cb
        self.change_crumb = change_crumb_cb
        style.set_main_window(self)

        main_vbox = gtk.VBox()
        self.foot_box = FootBox()
        hbox = gtk.HBox()
        hbox.connect("expose-event",self.expose_line)

        main_vbox.pack_start(hbox, False, False)
        main_vbox.pack_start(self.foot_box, False, False)

        self.add(main_vbox)

        self.tab_window = TabBox(dockfill = False)
        self.tab_window.draw_title_background = self.draw_tab_title_background
        self.tab_window.set_size_request(674, 415)

        self.sidebar = SideBar( None)
        # Build ui
        hbox.pack_start(self.sidebar, False , False)
        hbox.pack_start(self.tab_window ,True, True)

        style.draw_background_color(self)
        style.draw_separator(self.sidebar, 3)

        self.__init_signals()

    def __init_signals(self):
        Dispatcher.connect("connection-change", self.switch_tab)

    def load_module(self, module_obj):
        self.sidebar.load_list(module_obj)
        self.setting_group = module_obj
        #self.sidebar.add_new_connection = module_obj.setting_add

    def switch_tab(self, widget, connection):
        self.set_tab_content(connection)
        
    def set_tab_content(self, connection, init_connection=False):
        if self.tab_window.tab_items ==  []:
            self.tab_window.add_items(self.setting_group.init_settings(connection))
        else:
            self.tab_window.tab_items = self.setting_group.init_settings(connection)
        if init_connection:
            tab_index = 0
        else:
            tab_index = self.tab_window.tab_index
        self.tab_window.tab_index = -1
        self.tab_window.switch_content(tab_index)
        self.queue_draw()

    def expose_line(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        style.draw_out_line(cr, rect, exclude=["left", "right", "top"])

    def draw_tab_title_background(self, cr, widget):
        rect = widget.allocation
        cr.set_source_rgb(1, 1, 1)    
        cr.rectangle(0, 0, rect.width, rect.height - 1)
        cr.fill()

class Settings(object):
    def __init__(self, setting_list):
        self.setting_list = setting_list 
        
        self.setting_state = {}
        self.settings = {}

    def init_settings(self, connection):
        self.connection = connection 
        if connection not in self.settings:
            setting_list = []
            for setting in self.setting_list:
                s = setting(connection, self.set_button)
                setting_list.append((s.tab_name, s))

            self.settings[connection] = setting_list
        return self.settings[connection]

    def set_button(self, name, state):
        pass
        #self.set_button_callback(name, state)
        #self.setting_state[self.connection] = (name, state)

    def clear(self):
        print "clear settings"
        self.setting_state = {}
        self.settings = {}

    def get_button_state(self, connection):
        return self.setting_state[self.connection]
    
class LanSetting(Settings):
    def __init__(self):
        Settings.__init__(self,[Wired, IPV4Conf, IPV6Conf])

    def get_connections(self, device=None, new_connection=None, init_connection=False):
        self.connections = nm_module.nm_remote_settings.get_wired_connections()

        if init_connection:
            for connection in self.connections:
                connection.init_settings_prop_dict()
        # check connections
        if new_connection:
            self.connections += new_connection
        #else:
            #self.sidebar.new_connection_list = []

        if self.connections == []:
            self.connections = [nm_module.nm_remote_settings.new_wired_connection()]
            #self.sidebar.new_connection_list = [self.connections[0]]
        return self.connections
    
    def add_new_connection(self):
        print "add setting"

if __name__=="__main__":
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_title("Container")
    #win.border_width(2)

    win.connect("destroy", lambda w: gtk.main_quit())
    
    setting_page = SettingUI(None, None)
    setting_page.load_module(LanSetting())

    #vbox = gtk.VBox(False)
    #vbox.pack_start(con)
    win.add(setting_page)
    win.show_all()

    gtk.main()
