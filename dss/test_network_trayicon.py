#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Deepin, Inc.
#               2012 Hailong Qiu
#
# Author:     Hailong Qiu <356752238@qq.com>
# Maintainer: Hailong Qiu <356752238@qq.com>
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

#########################################
from theme import app_theme
#########################################
from dtk.ui.line import HSeparator
from dtk.ui.button import OffButton
from dtk.ui.trayicon import TrayIcon
from dtk.ui.label import Label
from dtk.ui.box import ImageBox
from dtk.ui.hscalebar import HScalebar
#########################################
import gtk
import subprocess
#########################################

NET_WORK_CABLE_ICON =  app_theme.get_pixbuf("network/cable.png")
NET_WORK_WIFI_ICON  =  app_theme.get_pixbuf("network/wifi.png")
NET_WORK_G3_ICON    =  app_theme.get_pixbuf("network/3g.png")
NETWORK_CMD = "deepin-system-settings network"

class NetworkTrayIcon(TrayIcon):
    '''网络托盘图标'''
    def __init__(self, width=165):
        TrayIcon.__init__(self, 0, tray_icon_to_screen_width=10)
        self.set_size_request(width, -1)        
        self.set_from_pixbuf(app_theme.get_pixbuf("logo.png").get_pixbuf()) # set tray icon.
        self.main_vbox = gtk.VBox()
        # init widgets.
        self.init_cable()
        self.init_wifi()                
        self.init_wifi_show_list()
        self.init_g3()        
        self.init_h_separator_top()
        self.init_h_separator_bottom()        
        self.init_main_vbox_add_widgets()                
        self.init_advanced_option()
        self.add_widget(self.main_vbox)
        
    def init_cable(self): # 有线网络.
        self.cable_hbox_ali = gtk.Alignment(0, 0, 1, 1)
        self.cable_hbox_ali.set_padding(0, 10, 0, 0)        
        self.cable_hbox = gtk.HBox()
        self.cable_icon   = ImageBox(NET_WORK_CABLE_ICON)
        self.cable_label  = Label('有线网络')
        self.cable_button = OffButton()        
        self.cable_button.connect("toggled", self.cable_button_toggled)                        
        #
        self.cable_hbox.pack_start(self.cable_icon, True, True)
        self.cable_hbox.pack_start(self.cable_label, True, True)
        self.cable_hbox.pack_start(self.cable_button, False, False)
        #
        self.cable_hbox_ali.add(self.cable_hbox)
        
    def init_wifi(self): # 无线网络.
        self.wifi_hbox_ali = gtk.Alignment(0, 0, 1, 1)
        self.wifi_hbox_ali.set_padding(0, 10, 0, 0)
        self.wifi_hbox = gtk.HBox()
        #
        self.wifi_icon   = ImageBox(NET_WORK_WIFI_ICON)
        self.wifi_label  = Label("无线网络")
        self.wifi_button = OffButton()
        self.wifi_button.connect("toggled", self.wifi_button_toggled)
        #
        self.wifi_hbox.pack_start(self.wifi_icon, True, True)
        self.wifi_hbox.pack_start(self.wifi_label, True, True)
        self.wifi_hbox.pack_start(self.wifi_button, False, False)
        #
        self.wifi_hbox_ali.add(self.wifi_hbox)        
        
    def init_wifi_show_list(self):
        self.wifi_show_list_button_hbox = gtk.HBox()
        self.wifi_show_list_button_ali = gtk.Alignment(0, 0, 1, 1)
        self.wifi_show_list_button_ali.set_padding(0, 10, 0, 0)
        self.wifi_show_list_button = SelectButton("更多无线信号源...")
        self.wifi_show_list_button.connect("clicked", self.wifi_show_list_button_clicked)
        self.wifi_show_list_button_ali.add(self.wifi_show_list_button)
        self.wifi_show_list_button_hbox.pack_start(self.wifi_show_list_button_ali, True, True)
        self.btn_ali = gtk.Alignment(0, 0, 1, 1)
        self.btn = gtk.Button("fjsklfjlskdf")
        self.btn_ali.add(self.btn)
        
    def show_wifi_list_btn(self):
        self.wifi_show_list_button_hbox.pack_start(self.wifi_show_list_button_ali, True, True)
        
    def hide_wifi_list_btn(self):        
        self.wifi_show_list_button_hbox.remove(self.wifi_show_list_button_ali)
        
    def init_h_separator_top(self): # 移动网络的 上横线.
        self.h_separator_top_ali = gtk.Alignment(0, 0, 1, 1)
        self.h_separator_top_ali.set_padding(0, 10, 0, 0)
        self.h_separator_top = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        self.h_separator_top_ali.add(self.h_separator_top)
        
    def init_g3(self): # 移动网络.
        self.g3_hbox_ali = gtk.Alignment(0, 0, 1, 1)
        self.g3_hbox_ali.set_padding(0, 10, 0, 0)
        self.g3_hbox = gtk.HBox()
        #
        self.g3_icon   = ImageBox(NET_WORK_G3_ICON)
        self.g3_label  = Label("移动网络")
        self.g3_button = OffButton()
        #
        self.g3_button.connect("toggled", self.g3_button_toggled)
        #
        self.g3_hbox.pack_start(self.g3_icon, True, True)
        self.g3_hbox.pack_start(self.g3_label, True, True)
        self.g3_hbox.pack_start(self.g3_button, False, False)
        #
        self.g3_hbox_ali.add(self.g3_hbox)
                        
    def init_h_separator_bottom(self): # 移动网络的 下横线.
        self.h_separator_bottom_ali = gtk.Alignment(0, 0, 1, 1)        
        self.h_separator_bottom_ali.set_padding(0, 10, 0, 0)
        self.h_separator_bottom = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)        
        self.h_separator_bottom_ali.add(self.h_separator_bottom)
        
    def init_advanced_option(self):
        self.advanced_option_button = SelectButton("更多高级选项...")
        self.advanced_option_button.connect("clicked", self.advanced_option_button_clicked)
        self.main_vbox.pack_start(self.advanced_option_button, False, False)
        
    def init_main_vbox_add_widgets(self): # main_vbox 添加 控件.
        self.main_vbox.pack_start(self.cable_hbox_ali, False, False)
        self.main_vbox.pack_start(self.wifi_hbox_ali, False, False)
        self.main_vbox.pack_start(self.wifi_show_list_button_hbox, False, False)
        self.main_vbox.pack_start(self.h_separator_top_ali)
        self.main_vbox.pack_start(self.g3_hbox_ali, False, False)
        self.main_vbox.pack_start(self.h_separator_bottom_ali)        
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_size_request(150, 150)
        btn = gtk.Button()
        btn.set_size_request(1500, 1500)
        scrolled_window.add_with_viewport(btn)
        adj = gtk.Adjustment(value=0, lower=100, upper=1000)
        pb = gtk.HScale(adj)
        pb_2 = HScalebar(show_value_type=gtk.POS_BOTTOM,  show_value=True, format_value="%")
        self.main_vbox.pack_start(scrolled_window, False, False)
        self.main_vbox.pack_start(pb, False, False)
        self.main_vbox.pack_start(pb_2, False, False)
        
    '''connect widgets events.'''
    def cable_button_toggled(self, widget):
        print "cable_button_clicked..."
        
    def wifi_button_toggled(self, widget):
        print "wifi_button_toggled..."
        self.hide_wifi_list_btn()
        
    def g3_button_toggled(self, widget):
        print "g3_button_toggled..."
        self.show_wifi_list_btn()
        
    def advanced_option_button_clicked(self, widget):
        self.hide_all()
        subprocess.Popen(["deepin-system-settings",
                          "network"])
        
    def wifi_show_list_button_clicked(self, widget):        
        print "wifi_show_list_button_clicked..."
        
from dtk.ui.draw import draw_text
from dtk.ui.utils import color_hex_to_cairo, get_content_size

class SelectButton(gtk.Button):        
    def __init__(self, 
                 text="", 
                 bg_color="#ebf4fd",
                 line_color="#7da2ce"):
        gtk.Button.__init__(self)
        # init values.
        self.text = text
        self.bg_color = bg_color
        self.line_color = line_color
        self.draw_check = False
        width, height = get_content_size(self.text)
        print "size", width, height
        self.set_size_request(width, height + 8)        
        # init events.
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.connect("expose-event", self.select_button_expose_event)        
        
    def select_button_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        # 
        if widget.state == gtk.STATE_PRELIGHT:
        # if self.draw_check:
            print "select_button_expose_event........"
            # draw rectangle.
            cr.set_line_width(3)
            cr.set_source_rgb(*color_hex_to_cairo(self.bg_color))
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.fill()
            cr.set_source_rgb(*color_hex_to_cairo(self.line_color))
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.stroke()            
            
        # draw text.
        draw_text(cr, self.text,
                  rect.x + rect.width - get_content_size(self.text)[0] - 10,
                  rect.y + rect.height/2 - get_content_size(self.text)[1]/2,
                  rect.width, 
                  0)        
        return True
    
    
if __name__ == "__main__":        
    NetworkTrayIcon()
    gtk.main()

    # win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    # win.add(SelectButton("更多高级选项..."))
    # win.show_all()
    # gtk.main()
    
