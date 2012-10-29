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
from dtk.ui.slider import Slider
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
slider = Slider()
PADDING = 32
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from module_frame import ModuleFrame 

def slider_append(slide, item):
    layout_child = slide.layout.get_children()
    if len(layout_child) > 1:
        slide.layout.remove(layout_child[1])

    slide.append_widget(item)
    item.show_all()
    
#class LoadingThread(td.Thread):
    #def __init__(self, obj, device, setting):
        #td.Thread.__init__(self)
        #self.setDaemon(True)
        #self.obj = obj
        #self.tree = self.obj.tree
        #self.device = device
        #self.setting = setting

    #def run(self):
        #print "enter thread"
        #ap_list = self.device.order_ap_list()
        #print "leave thread"
        #items = [WirelessItem(i,self.setting, slider) for i in ap_list]
        #self.render_list([items, 3]) 
        #self.tree.set_size_request(-1,len(self.tree.visible_items) * self.tree.visible_items[0].get_height())
        ##except Exception, e:
            ##print "class LoadingThread got error: %s" % (e)
            ##traceback.print_exc(file=sys.stdout)
        #### After Loading

    #@post_gui
    #def render_list(self,item_list):
        #"""
        #retrieve network lists, will use thread
        #"""
        #print "gui"
        ##self.tree.visible_items[-1].is_last = False
        #self.tree.add_items(item_list[0],0,True)
        #self.tree.visible_items[-1].is_last = True
        #self.tree.select_items([self.tree.visible_items[item_list[1]]])
class DSL(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)
        dsl = Contain(app_theme.get_pixbuf("/Network/wired.png"), "宽带拨号", self.toggle_cb)
        self.pack_start(dsl, False, False)

    def toggle_cb(self, widget):
        pass

        

class WiredSection(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)
        wire = Contain(app_theme.get_pixbuf("/Network/wired.png"), "有线网络", self.toggle_cb)

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

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            self.wired_setting = WiredSetting(slider)
            slider_append(slider, self.wired_setting)
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
        return [WiredItem(wired_device.get_device_desc(), self.wired_setting, slider)]

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

        self.pack_start(wireless, False, False)
        self.tree = TreeView([], enable_multiple_select = False)
        #self.tree.set_no_show_all(True)
        #self.tree.hide()

        self.wifi = WifiSection()
        #self.wifi.set_no_show_all(True)
        #self.wifi.hide()


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

    def toggle_cb(self, widget):

        active = widget.get_active()
        if active:
            self.global_setting = WirelessSetting(None,slider)
            slider_append(slider, self.global_setting)
            device_path = nmclient.get_wireless_device()
            wireless_devices = NMDeviceWifi(device_path.object_path)
            active_connection = wireless_device.get_active_connection()
            #LoadingThread(self, wireless_devices, global_setting).start()
            #self.tree.set_no_show_all(False)
            ap_list = self.retrieve_list()
            #self.queue_draw()
            #self.show_all()
            item_list = ap_list[0]
            index = ap_list[1]
            self.tree.add_items(item_list,0,True)
            self.tree.visible_items[-1].is_last = True
            self.vbox.set_no_show_all(False)
            self.tree.set_size_request(-1,len(self.tree.visible_items) * self.tree.visible_items[0].get_height())
            self.queue_draw()
            self.show_all()
            self.tree.select_items([self.tree.visible_items[index]])

        else:
            self.tree.add_items([],0,True)
            self.vbox.hide()
            #self.h.get_children()[1].destroy()

    def retrieve_list(self):
        """
        retrieve network lists, will use thread
        """
        device_path = nmclient.get_wireless_device()
        wireless_devices = NMDeviceWifi(device_path.object_path)
        #active_connection = NMActiveConnection(wireless_device.get_active_connection())
        ap_list = wireless_devices.order_ap_list()
        #index = [ap.object_path for ap in ap_list].index(active_connection.get_specific_object())
        index = 3

        #print nm_remote_settings.get_ssid_associate_connections(ap_list[3].get_ssid())
        
        ## After Loading
        items = [WirelessItem(i,self.global_setting, slider) for i in ap_list]
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
    align = gtk.Alignment(0,0,0,0)
    align.set_padding(11,11,11,11)
    align.add(scroll_win)
    slider.append_widget(align)

    #slider.append_widget(WiredSetting(slider))
    #slider.append_widget(gtk.EventBox())
    module_frame.add(slider)
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            module_frame.send_module_info()

    module_frame.module_message_handler = message_handler
    
    module_frame.run()
#if __name__ == "__main__":

    #win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    #win.set_title("Main")
    #win.set_size_request(770,500)
    ##win.set_border_width(11)
    #win.set_resizable(True)
    #win.connect("destroy", lambda w: gtk.main_quit())

    #wireless = Wireless()
    #wired = WiredSection()
    ##wifi = WifiSection()
    #dsl = DSL()
    #vpn = VpnSection()
    #mobile = ThreeG()
    #proxy = Proxy()

    #vbox = gtk.VBox(False, 17)
    #vbox.pack_start(wired, False, True,5)
    #vbox.pack_start(wireless, False, True, 0)
    ##vbox.pack_start(wifi, False, True, 0)
    #vbox.pack_start(dsl, False, True, 0)
    #vbox.pack_start(mobile, False, True, 0)
    #vbox.pack_start(vpn, False, True, 0)
    #vbox.pack_start(proxy, False, True, 0)
    
    #scroll_win = ScrolledWindow()
    #scroll_win.set_size_request(765, 482)

    #scroll_win.add_with_viewport(vbox)
    #align = gtk.Alignment(0,0,0,0)
    #align.set_padding(11,11,11,11)
    #align.add(scroll_win)
    #slider.append_widget(align)

    ##slider.append_widget(WiredSetting(slider))
    ##slider.append_widget(gtk.EventBox())

    #win.add(slider)
    
        
    #win.show_all()

    #gtk.main()

