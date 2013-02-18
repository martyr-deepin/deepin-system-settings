#!/usr/bin/env python
#-*- coding:utf-8 -*-
# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Zeng Zhi
# 
# Author:     Zeng Zhi <zengzhilg@gmail.com>
# Maintainer: Zeng Zhi <zengzhilg@gmail.com>
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

from dtk.ui.utils import container_remove_all
from tray_ui import TrayUI
from shared_methods import NetManager
from helper import Dispatcher
import pynotify
import gtk

class TrayNetworkPlugin(object):

    def __init__(self):
        self.gui = TrayUI(self.toggle_wired, self.toggle_wireless, self.mobile_toggle)
        self.net_manager = NetManager()
        self.init_notifier()

    def init_values(self, this_list):
        self.this_list = this_list
        self.this = self.this_list[0]
        self.tray_icon = self.this_list[1]
        self.loading_pixbuf = self.tray_icon.load_icon("loading")
        self.init_widgets()

    def mobile_toggle(self, widget):
        pass
    
    def init_notifier(self):
        pynotify.init("Deepin network")

    #def notify_send(self, title, message, icon, time_out=):
        #n = pynotify.get

    def init_widgets(self):
        wired_state = self.net_manager.get_wired_state()
        if wired_state:
            self.gui.wire.set_active(wired_state)
            if wired_state[0] and wired_state[1]:
                self.change_status_icon("cable")
            else:
                self.change_status_icon("cable_disconnect")
            Dispatcher.connect("wired-change", self.set_wired_state)
        else:
            self.gui.remove_net("wired")
        
        wireless_state= self.net_manager.get_wireless_state()
        if wireless_state:
            self.gui.wireless.set_active(wireless_state)
            if wireless_state[0] and wireless_state[1]:
                self.change_status_icon("links")

            #else:
                #self.change_status_icon("tray_wifi_icon")

            Dispatcher.connect("wireless-change", self.set_wireless_state)
            Dispatcher.connect("connect_by_ssid", self.connect_by_ssid)
        else:
            self.gui.remove_net("wireless")

        Dispatcher.connect("tray-show-more", self.tray_show_more)

    def toggle_wired(self, widget):
        if widget.get_active():
            self.net_manager.active_wired_device(self.active_wired)
        else:
            self.net_manager.disactive_wired_device(self.disactive_wired)

    def set_wired_state(self, widget, device, new_state, reason):
        '''
        wired-change callback
        '''
        print new_state, reason
        if new_state is 20:
            self.gui.wire.set_active((False, False))
        elif new_state is 30:
            #n1 = pynotify.Notification("Network", "lan disconnect")
            #n1.set_timeout(2)
            #n1.show()
            
            self.gui.wire.set_sensitive(True)
            if self.gui.wireless.get_active():
                self.change_status_icon("links")
            else:
                self.change_status_icon("cable_disconnect")
            if reason is not 0:
                self.gui.wire.set_active((True, False))
        elif new_state is 40:
            #pynotify.Notification("Network", "lan connecting").show()
            self.gui.wire.set_active((True, True))
            self.change_status_icon("loading")
        elif new_state is 100:
            #pynotify.Notification("Network", "lan connect").show()
            self.active_wired()

    def connect_by_ssid(self, widget, ssid):
        connection =  self.net_manager.connect_wireless_by_ssid(ssid)

    def active_wired(self):
        """
        after active
        """
        self.gui.wire.set_active((True, True))
        self.change_status_icon("cable")

    def disactive_wired(self):
        """
        after diactive
        """
        if self.net_manager.get_wired_state()[0]:
            self.gui.wire.set_active((True, False))
        if self.gui.wireless.get_active():
            self.change_status_icon("links")
        else:
            self.change_status_icon("cable_disconnect")
    #####=======================Wireless
    def __get_ssid_list(self):
        return self.net_manager.get_ap_list()

    def init_tree(self):
        print "init+tree"
        self.ap_list = self.__get_ssid_list()
        self.gui.set_ap(self.ap_list)

    def toggle_wireless(self, widget):
        if widget.get_active():
            self.init_tree()
            index = self.net_manager.get_active_connection(self.ap_list)
            if index:
                self.gui.set_active_ap(index, True)
            else:
                self.activate_wireless()
            Dispatcher.tray_show_more()
        else:
            container_remove_all(self.gui.tree_box)
            self.gui.more_button.set_ap_list([])

            def device_disactive():
                pass

            self.net_manager.disactive_wireless_device(device_disactive)
            Dispatcher.tray_show_more()

    def set_wireless_state(self, widget, device, new_state, old_state, reason):
        """
        "wireless-change" signal callback
        """
        print new_state, old_state, reason
        if new_state is 20:
            self.gui.wireless.set_active((False, False))
        elif new_state is 30:
            print "==================="
            self.gui.wireless.set_sensitive(True)

            if self.gui.wire.get_active():
                self.change_status_icon("cable")
            else:
                self.change_status_icon("wifi_disconnect")
            if reason == 39:
                index = self.gui.get_active_ap()
                self.gui.set_active_ap(index, False)
            #elif reason:
                #self.gui.wireless.set_active((True,False))
        elif new_state is 40:
            self.gui.wireless.set_active((True, True))
            self.change_status_icon("loading")
        elif new_state is 60 and old_state == 50:
            print "need auth"
        elif new_state is 100:
            self.change_status_icon("links")
            self.set_active_ap()

    def set_active_ap(self):
        index = self.net_manager.get_active_connection(self.ap_list)
        self.gui.set_active_ap(index, True)

    def activate_wireless(self):
        """
        try to auto active wireless
        """
        def device_actived():
            #self.gui.wireless.set_active((True, True))
            #index = self.net_manager.get_active_connection(self.ap_list)
            #self.gui.set_active_ap(index, True)
            #self.change_status_icon("tray_links_icon")

            pass
        self.net_manager.active_wireless_device(device_actived)
    
    def change_status_icon(self, icon_name):
        """
        change status icon state
        """
        self.tray_icon.set_icon_theme(icon_name)

    def start_loading(self):
        pass

    def draw_loading(self, cr, rect):
        with cairo_state(cr):
            cr.translate(rect.x + 18 , rect.y + 15)
            cr.rotate(radians(60*self.position))
            cr.translate(-18, -15)
     ###############################
    def run(self):
        return True

    def insert(self):
        return 1
        
    def id(self):
        return "tray-network_plugin"

    def plugin_widget(self):
        return self.gui 
    
    def tray_show_more(self, widget):
        print "tray show more"
        height = self.gui.get_widget_height()
        self.this.set_size_request(160, height + 50)

    def show_menu(self):
        if self.gui.wireless.get_active() and hasattr(self, "ap_list"):
            self.gui.set_ap(self.ap_list)
        height = self.gui.get_widget_height()
        self.this.set_size_request(160, height + 50)
        print "shutdown show menu..."

    def hide_menu(self):
        print "shutdown hide menu..."

def return_plugin():
    return TrayNetworkPlugin

#class LoadingThread(td.Thread):
    #def __init__(self, widget):
        #td.Thread.__init__(self)
        #self.setDaemon(True)
        #self.widget = widget
    
    #def run(self):
        #try:
            #position = 0
            #while True:
                #if self.widget.loading:
                    #if position == 5:
                        #position = 0
                    #else:
                        #position += 1
                    #self.widget.refresh_loading(position)
                    #time.sleep(0.1)
                #else:
                    #break
        #except Exception, e:
            #print "class LoadingThread got error %s" % e
