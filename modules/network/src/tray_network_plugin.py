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
import gtk

class TrayNetworkPlugin(object):

    def __init__(self):
        self.gui = TrayUI(self.toggle_wired, self.toggle_wireless, self.mobile_toggle)
        self.net_manager = NetManager()

    def init_values(self, this_list):
        self.this_list = this_list
        self.this = self.this_list[0]
        self.tray_icon = self.this_list[1]
        self.init_widgets()

    def mobile_toggle(self, widget):
        pass

    def init_widgets(self):
        wired_state = self.net_manager.get_wired_state()
        if wired_state:
            self.gui.wire.set_active(wired_state)
            if wired_state[0] and wired_state[1]:
                self.change_status_icon("tray_lan_icon")
            else:
                self.change_status_icon("tray_usb_icon")
            Dispatcher.connect("wired-change", self.set_wired_state)
        else:
            self.gui.remove_net("wired")
        
        wireless_state= self.net_manager.get_wireless_state()
        if wireless_state:
            self.gui.wireless.set_active(wireless_state)
            if wireless_state[0] and wireless_state[1]:
                self.change_status_icon("tray_links_icon")
            else:
                self.change_status_icon("tray_wifi_icon")

            Dispatcher.connect("wireless-change", self.set_wireless_state)
            Dispatcher.connect("connect_by_ssid", self.connect_by_ssid)
        else:
            self.gui.remove_net("wireless")
    
    def toggle_wired(self, widget):
        if widget.get_active():
            self.net_manager.active_wired_device(self.active_wired)
        else:
            self.net_manager.disactive_wired_device(self.disactive_wired)

    def set_wired_state(self, widget, new_state, reason):
        '''
        wired-change callback
        '''
        if new_state is 20:
            self.gui.wire.set_active((False, False))
        elif new_state is 30:
            self.gui.wire.set_sensitive(True)
            self.change_status_icon("tray_goc_icon")

    def connect_by_ssid(self, widget, ssid):
        connection =  self.net_manager.connect_wireless_by_ssid(ssid)

    def active_wired(self):
        """
        after active
        """
        self.gui.wire.set_active((True, True))
        self.change_status_icon("tray_lan_icon")

    def disactive_wired(self):
        """
        after diactive
        """
        if self.net_manager.get_wired_state()[0]:
            self.gui.wire.set_active((True, False))
        if self.gui.wireless.get_active():
            self.change_status_icon("tray_links_icon")
        else:
            self.change_status_icon("tray_usb_icon")
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
        else:
            container_remove_all(self.gui.tree_box)
            self.gui.more_button.set_ap_list([])

            def device_disactive():
                pass

            self.net_manager.disactive_wireless_device(device_disactive)

    def set_wireless_state(self, widget, new_state, old_state, reason):
        """
        "wireless-change" signal callback
        """
        print new_state, old_state, reason
        if new_state is 20:
            self.gui.wireless.set_active((False, False))
        elif new_state is 30:
            print "==================="
            self.gui.wireless.set_sensitive(True)
            self.change_status_icon("tray_usb_icon")
            if reason == 39:
                index = self.gui.get_active_ap()
                self.gui.set_active_ap(index, False)
            #elif reason:
                #self.gui.wireless.set_active((True,False))
        elif new_state is 40:
            self.gui.wireless.set_active((True, True))
            self.change_status_icon("tray_goc_icon")
        elif new_state is 60 and old_state == 50:
            print "need auth"
        elif new_state is 100:
            self.change_status_icon("tray_links_icon")
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

     ###############################
    def run(self):
        return True

    def insert(self):
        return 0
        
    def id(self):
        return "tray-network_plugin"

    def plugin_widget(self):
        return self.gui 

    def show_menu(self):
        self.this.set_size_request(160, 300)
        print "shutdown show menu..."

    def hide_menu(self):
        print "shutdown hide menu..."

def return_plugin():
    return TrayNetworkPlugin
