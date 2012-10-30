#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os
sys.path.append("../")
from theme import app_theme
from dtk.ui.theme import ui_theme
from dtk.ui.new_treeview import TreeView
from dtk.ui.draw import draw_pixbuf, draw_line
from dtk.ui.utils import color_hex_to_cairo, get_parent_dir
from dtk.ui.label import Label
from dtk.ui.new_slider import HSlider
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.threads import post_gui
import gtk
import traceback
import threading as td

from container import Contain
from lists import WiredItem, WirelessItem

from lan_config import WiredSetting
from wlan_config import WirelessSetting

from nmlib.nmobject import dbus_loop
from wired import *
slider = HSlider()
PADDING = 32
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from module_frame import ModuleFrame 

        

class WiredSection(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)
        wire = Contain(app_theme.get_pixbuf("/Network/wired.png"), "有线网络", self.toggle_cb)
        
        self.settings = None
        self.pack_start(wire, False, False)
        self.tree = TreeView([])
        self.tree.set_no_show_all(True)
        self.tree.hide()
        self.align = gtk.Alignment()
        self.align.show()
        self.align.set(0,0,1,1)
        self.align.set_padding(0,0,PADDING,11*2)
        self.align.add(self.tree)
        self.pack_start(self.align, False, False, 0)

    def add_setting_page(self, setting_page):
        self.settings = setting_page

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            t = self.retrieve_list()
            self.tree.add_items(t,0,True)
            self.tree.visible_items[-1].is_last = True
            self.tree.set_no_show_all(False)
            self.tree.set_size_request(-1,len(self.tree.visible_items) * self.tree.visible_items[0].get_height())
            
            if self.active_one >= 0:
                self.tree.visible_items[self.active_one].is_select = True
            self.show_all()
        else:
            self.tree.add_items([],0,True)
            self.tree.hide()
            #self.h.get_children()[1].destroy()

    def retrieve_list(self):
        """
        retrieve network lists, will use thread
        """
        wired_device.connect("device-active", self.device_activate)
        wired_device.connect("device-deactive", self.device_deactive)
        if wired_device.get_state() == 20:
            self.active_one = -1
        else:
            self.active_one = 0
        return [WiredItem(wired_device.get_device_desc(), self.settings, lambda : slider.slide_to_page(self.settings, "right"))]

    def device_activate(self, widget ,event):
        print "activate"
        self.tree.visible_items[self.active_one].is_select = True
        self.queue_draw()

    def device_deactive(self, widget, event):
        print "deactive"
        self.tree.visible_items[self.active_one].is_select = False
        self.queue_draw()

class Wireless(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        wireless = Contain(app_theme.get_pixbuf("/Network/wireless.png"), "无线网络", self.toggle_cb)
        
        wireless_device.connect("device-active", self.device_is_active)
        wireless_device.connect("device-deactive", self.device_is_deactive)
        self.pack_start(wireless, False, False)
        self.tree = TreeView([], enable_multiple_select = False)
        self.settings = None
        self.wifi = WifiSection()

        self.vbox = gtk.VBox()
        self.vbox.pack_start(self.tree)
        self.vbox.pack_start(self.wifi)
        self.vbox.set_no_show_all(True)
        self.vbox.hide()
        self.align = gtk.Alignment()
        self.align.show()
        self.align.set(0,0,1,1)
        self.align.set_padding(0,0,PADDING,11 + 11)
        self.align.add(self.vbox)

        self.pack_start(self.align, False, False, 0)
    
    def device_is_active(self, widget, state):
        print "active"
        print wireless_device.get_state()
        print wireless_device.is_active()
        #active = wireless_device.get_active_connection()
        #print active
        #index = [ap.object_path for ap in self.ap_list].index(active.get_specific_object())

        #self.tree.visible_items[index].check_select_flag = True
    
    def device_is_deactive(self, widget, event):
        print "deactive"

    def add_setting_page(self, page):
        self.settings = page

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            ap_list = self.retrieve_list()
            item_list = ap_list[0]
            index = ap_list[1]
            self.tree.add_items(item_list,0,True)
            self.tree.visible_items[-1].is_last = True
            self.vbox.set_no_show_all(False)
            self.tree.set_size_request(-1,len(self.tree.visible_items) * self.tree.visible_items[0].get_height())
            self.queue_draw()
            self.show_all()
            if index > 0:
                self.tree.visible_items[index].check_select_flag = True
        else:
            self.tree.add_items([],0,True)
            self.vbox.hide()

    def retrieve_list(self):
        """
        retrieve network lists, will use thread
        """
        #device = nmclient.get_wireless_device()
        device_wifi = NMDeviceWifi(wireless_device.object_path)
        self.ap_list = device_wifi.order_ap_list()
        if wireless_device.get_state() == 100:
            active_connection = wireless_device.get_active_connection()
            index = [ap.object_path for ap in self.ap_list].index(active_connection.get_specific_object())
        else:
            device_wifi.auto_connect()
            index = -1

        #print nm_remote_settings.get_ssid_associate_connections(ap_list[3].get_ssid())
        
        ## After Loading
        items = [WirelessItem(i,self.settings, lambda : slider.slide_to_page(self.settings, "right")) for i in self.ap_list]
        return [items, index]


class WifiSection(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self, 0)
        cont = Contain(app_theme.get_pixbuf("/Network/wifi.png"), "个人热点", self.toggle_cb)
        self.pack_start(cont, False, False)

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            self.align = gtk.Alignment(0, 0.0, 1, 1)
            self.align.set_padding(0, 0, PADDING,0)
            self.align.show()
            self.h = gtk.HBox()
            self.h.show()
            label = gtk.Label("热点密码 ")
            label.show()
            entry = gtk.Entry()
            entry.show()
            self.align.add(self.h)
            self.h.pack_start(label, False, False, 0)
            self.h.pack_start(entry, False, True, 0)
            self.pack_start(self.align, False, True, 0)
        else:
            self.h.destroy()

class DSL(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)
        dsl = Contain(app_theme.get_pixbuf("/Network/wired.png"), "宽带拨号", self.toggle_cb)
        self.pack_start(dsl, False, False)

    def toggle_cb(self, widget):
        pass

class VpnSection(gtk.VBox):
    def __init__(self):

        gtk.VBox.__init__(self)
        vpn = Contain(app_theme.get_pixbuf("/Network/misc.png"), "VPN网络", self.toggle_cb)
        self.add(vpn)

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            self.align = gtk.Alignment(0,0,0,0)
            self.align.set_padding(0,0,PADDING,11)
            label = Label("添加vpn网络", ui_theme.get_color("link_text"))
            label.connect("button-release-event", self.slide_to_event)

            self.align.add(label)
            self.align.connect("expose-event", self.expose_event)
            self.add(self.align)
            self.show_all()
        else:
            self.align.destroy()

    def slide_to_event(self, widget, event):
        print "clicked this label"

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.child.allocation
        cr.set_source_rgb(*color_hex_to_cairo(ui_theme.get_color("link_text").get_color()))
        draw_line(cr, rect.x, rect.y + rect.height, rect.x + rect.width, rect.y + rect.height)


class ThreeG(gtk.VBox):
    def __init__(self):

        gtk.VBox.__init__(self)
        mobile = Contain(app_theme.get_pixbuf("/Network/3g.png"), "移动网络", self.toggle_cb)
        self.add(mobile)

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            self.align = gtk.Alignment(0,0,0,0)
            self.align.set_padding(0,0,PADDING,11)
            label = Label("设置3G网络", ui_theme.get_color("link_text"))
            label.connect("button-release-event", self.slide_to_event)

            self.align.add(label)
            self.align.connect("expose-event", self.expose_event)
            self.add(self.align)
            self.show_all()
        else:
            self.align.destroy()

    def slide_to_event(self, widget, event):
        print "clicked 3G"

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.child.allocation
        cr.set_source_rgb(*color_hex_to_cairo(ui_theme.get_color("link_text").get_color()))
        draw_line(cr, rect.x, rect.y + rect.height, rect.x + rect.width, rect.y + rect.height)


class Proxy(gtk.VBox):
    def __init__(self):

        gtk.VBox.__init__(self)
        proxy = Contain(app_theme.get_pixbuf("/Network/misc.png"), "网络代理", self.toggle_cb)
        self.add(proxy)

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            self.align = gtk.Alignment(0,0,0,0)
            self.align.set_padding(0,0,PADDING,11)
            label = Label("设置网络代理", ui_theme.get_color("link_text"))
            label.connect("button-release-event", self.slide_to_event)

            self.align.add(label)
            self.align.connect("expose-event", self.expose_event)
            self.add(self.align)
            self.show_all()
        else:
            self.align.destroy()

    def slide_to_event(self, widget, event):
        print "clicked proxy config"

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.child.allocation
        cr.set_source_rgb(*color_hex_to_cairo(ui_theme.get_color("link_text").get_color()))
        draw_line(cr, rect.x, rect.y + rect.height, rect.x + rect.width, rect.y + rect.height)




if __name__ == '__main__':

    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))
    
    wireless = Wireless()
    wired = WiredSection()
    #wifi = WifiSection()
    dsl = DSL()
    vpn = VpnSection()
    mobile = ThreeG()
    proxy = Proxy()

    vbox = gtk.VBox(False, 17)
    vbox.pack_start(wired, False, True,5)
    vbox.pack_start(wireless, False, True, 0)
    #vbox.pack_start(wifi, False, True, 0)
    vbox.pack_start(dsl, False, True, 0)
    vbox.pack_start(mobile, False, True, 0)
    vbox.pack_start(vpn, False, True, 0)
    vbox.pack_start(proxy, False, True, 0)
    
    scroll_win = ScrolledWindow()
    scroll_win.set_size_request(825, 425)

    scroll_win.add_with_viewport(vbox)
    main_align = gtk.Alignment(0,0,0,0)
    main_align.set_padding(11,11,11,11)
    main_align.add(scroll_win)
    
    wired_setting_page = WiredSetting(lambda  :slider.slide_to_page(main_align, "left"))
    wired.add_setting_page(wired_setting_page)
    wireless_setting_page = WirelessSetting(None, lambda :slider.slide_to_page(main_align, "left"))
    wireless.add_setting_page(wireless_setting_page)

    slider.append_page(main_align)
    slider.append_page(wired_setting_page)
    slider.append_page(wireless_setting_page)

    #slider.append_widget(WiredSetting(slider))
    #slider.append_widget(gtk.EventBox())
    module_frame.add(slider)
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            module_frame.send_module_info()

    module_frame.module_message_handler = message_handler
    
    module_frame.run()