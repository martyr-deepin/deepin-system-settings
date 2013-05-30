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
from nm_modules import nm_module
#from shared_methods import net_manager, device_manager
from shared_methods import net_manager
from helper import Dispatcher, event_manager
from nmlib.nm_remote_connection import NMRemoteConnection
from subprocess import Popen

from widgets import AskPasswordDialog
from vtk.timer import Timer

WAIT_TIME = 15000

class TrayNetworkPlugin(object):

    def __init__(self):
        self.menu_showed = False
        self.gui = TrayUI(self.toggle_wired,
                          self.toggle_wireless,
                          self.mobile_toggle,
                          self.toggle_vpn,
                          self.toggle_dsl)
        self.net_manager = net_manager
        self.net_manager.init_devices()
        Dispatcher.connect("request_resize", self.request_resize)
        Dispatcher.connect("ap-added", self.wireless_ap_added)
        Dispatcher.connect("ap-removed", self.wireless_ap_removed)
        Dispatcher.connect("recheck-section", self.recheck_sections)
        self.gui.button_more.connect("clicked", self.more_setting)

        self.need_auth_flag = False
        self.this_device = None
        self.this_connection = None
        self.dialog_toggled_flag = False

        self.timer = Timer(WAIT_TIME)
        self.timer.Enabled = False
        self.timer.connect("Tick", self.timer_count_down_finish)

        self.init_wired_signals()
        self.init_wireless_signals()
        self.init_mm_signals()
        Dispatcher.connect("mmdevice-added", lambda w,p: self.init_mm_signals())
        Dispatcher.connect("wired-device-add", lambda w,p: self.init_wired_signals())
        Dispatcher.connect("wireless-device-add", self.wireless_device_added)
        Dispatcher.connect("switch-device", self.switch_device)
        Dispatcher.connect('vpn-start', self.vpn_start_cb)

        # vpn signals 
        event_manager.add_callback("vpn-connecting", self.on_vpn_connecting)
        event_manager.add_callback('vpn-connected', self.__vpn_active_callback)
        event_manager.add_callback('vpn-disconnected', self.__vpn_failed_callback)

        event_manager.add_callback('vpn-user-disconnect', self.on_user_stop_vpn)
        event_manager.add_callback('vpn-connection-removed', self.vpn_connection_remove_cb)
        event_manager.add_callback('vpn-new-added', self.on_vpn_setting_change)
        self.__init_dsl_signals()

        # dsl signals
        #event_manager.add_callback('dsl-new-added', self.dsl_new_added)
        #event_manager.add_callback('dsl-connection-removed', self.dsl_removed)

        Dispatcher.connect("service_start_do_more", self.service_start_do_more)

    def service_start_do_more(self, widget):
        self.init_wired_signals()
        self.init_wireless_signals()
        self.init_mm_signals()

    def recheck_sections(self, widget, index):
        print "recheck sections"
        self.init_widgets()
        Dispatcher.emit("request-resize")

    def wireless_ap_added(self, widget):
        print "wireless_ap_added in tray"
        if self.gui.wireless.get_active():
            self.gui.wireless.set_active((True, True), emit=True)

    def wireless_ap_removed(self, widget):
        print "wireless ap removed in tray"
        if self.gui.wireless.get_active():
            self.gui.wireless.set_active((True, True), emit=True)

    def init_values(self, this_list):
        self.this_list = this_list
        self.this = self.this_list[0]
        self.tray_icon = self.this_list[1]
        self.init_widgets()

    def init_mm_signals(self):
        net_manager.device_manager.load_mm_listener(self)

    def mm_device_active(self, widget, new_state, old_state, reason):
        self.gui.mobile.set_active((True, True))
        self.change_status_icon("cable")

    def mm_device_deactive(self, widget, new_state, old_state, reason):
        self.gui.mobile.set_active((True, False))
        if self.gui.wire.get_active():
            self.change_status_icon("cable")
        elif self.gui.wireless.get_active():
            self.change_status_icon("links")
        else:
            self.change_status_icon("cable_disconnect")

    def mm_device_unavailable(self,  widget, new_state, old_state, reason):
        self.gui.mobile.set_active((True, False))

    def mm_activate_start(self, widget, new_state, old_state, reason):
        self.gui.mobile.set_active((True, True))
        self.change_status_icon("loading")
        self.let_rotate(True)

    def mm_activate_failed(self, widget, new_state, old_state, reason):
        self.gui.mobile.set_active((True, False))
        if self.gui.wire.get_active():
            self.change_status_icon("cable")
        elif self.gui.wireless.get_active():
            self.change_status_icon("links")
        else:
            self.change_status_icon("cable_disconnect")

    def mobile_toggle(self):
        if self.gui.mobile.get_active():
            self.mm_device = self.net_manager.connect_mm_device()
        else:
            self.net_manager.disconnect_mm_device()
    
    def timer_count_down_finish(self, widget):
        connections = nm_module.nmclient.get_active_connections()
        active_connection = connections[-1]
        
        self.this_connection = active_connection.get_connection()
        self.this_device.nm_device_disconnect()
        self.toggle_dialog(self.this_connection)
        widget.Enabled = False

    def init_widgets(self):
        wired_state = self.net_manager.get_wired_state()
        if wired_state:
            self.gui.show_net("wire")
            self.gui.wire.set_active(wired_state)
            if wired_state[0] and wired_state[1]:
                self.change_status_icon("cable")
            else:
                self.change_status_icon("cable_disconnect")
            #Dispatcher.connect("wired-change", self.set_wired_state)
        else:
            self.gui.remove_net("wire")
        
        wireless_state= self.net_manager.get_wireless_state()
        if wireless_state:
            self.focus_device = self.net_manager.device_manager.wireless_devices[0]
            self.gui.show_net("wireless")
            self.gui.wireless.set_active(wireless_state)
            if wireless_state[0] and wireless_state[1]:
                self.change_status_icon("links")
            else:
                if not self.gui.wire.get_active():
                    self.change_status_icon("wifi_disconnect")
            #Dispatcher.connect("wireless-change", self.set_wireless_state)
            Dispatcher.connect("connect_by_ssid", self.connect_by_ssid)
            self.pwd_failed = False
        else:
            self.gui.remove_net("wireless")
        
        # Mobile init
        if self.net_manager.get_mm_devices():
            self.gui.show_net("mobile")

        else:
            self.gui.remove_net("mobile")

        def change_to_loading():
            self.change_status_icon('loading')
            self.let_rotate(True)

        if nm_module.nm_remote_settings.get_vpn_connections():
            self.gui.show_net("vpn")
            self.gui.vpn_list.connecting_cb = change_to_loading
            self.active_vpn = None
            self.no_vpn_connecting = False
            if nm_module.nmclient.get_vpn_active_connection():
                #for vpn_active in nm_module.nmclient.get_vpn_active_connection():
                    #vpn_spec = nm_module.cache.get_spec_object(vpn_active.object_path)
                    #self.connect_vpn_signals(vpn_spec)
                self.gui.vpn.set_active((True, True))
                self.tray_icon.set_icon_theme("links_vpn")
        else:
            self.gui.remove_net("vpn")
        
        if wired_state[0] and nm_module.nm_remote_settings.get_pppoe_connections():
            self.gui.show_net("dsl")
            self.gui.dsl_list.connecting_cb = change_to_loading
            #self.active_dsl = None
            #self.no_vpn_connecting = False
            if nm_module.nmclient.get_pppoe_active_connection():
                self.gui.dsl.set_active((True, True))
                self.tray_icon.set_icon_theme("cable")
        else:
            self.gui.remove_net("dsl")


        #if nm_module.nmclient.get_pppoe_connections():
            #self.gui.dsl.set_active((True, True))

        
    def toggle_wired(self):
        if self.gui.wire.get_active():
            self.net_manager.active_wired_device(self.active_wired)
        else:
            self.net_manager.disactive_wired_device(self.disactive_wired)

    def init_wired_signals(self):
        net_manager.device_manager.load_wired_listener(self)

    def wired_device_active(self, widget, new_state, old_state, reason):
        self.active_wired()

    def wired_device_deactive(self, widget, new_state, old_state, reason):
        #print widget, reason
        #self.gui.wire.set_sensitive(True)
        print "tray:wired_device_deactive"
        print "wired", self.gui.wire.get_active()
        print "wireless", self.gui.wireless.get_active()

        if any([d.get_state() == 100 for d in net_manager.wired_devices]):
            self.change_status_icon("cable")
        else:
            if any([d.get_state() == 100 for d in net_manager.wireless_devices]):
                self.change_status_icon("links")
            else:
                self.change_status_icon("cable_disconnect")
            if reason != 0:
                self.gui.wire.set_active((True, False))
                if reason == 40:
                    self.gui.wire.set_active((False, False))

    def wired_device_unavailable(self,  widget, new_state, old_state, reason):
        self.wired_device_deactive(widget, new_state, old_state, reason)

    def wired_device_available(self, widget, new_state, old_state, reason):
        self.gui.wire.set_sensitive(True)
        if self.gui.wire.get_active():
            self.change_status_icon("cable")
        elif self.gui.wireless.get_active():
            self.change_status_icon("links")
        else:
            self.change_status_icon("cable_disconnect")
        #if reason is not 0:
        #    self.gui.wire.set_active((True, False))

    def wired_activate_start(self, widget, new_state, old_state, reason):
        if not self.gui.wire.get_active():
            self.gui.wire.set_active((True, True))
        self.change_status_icon("loading")
        self.let_rotate(True)

    def wired_activate_failed(self, widget, new_state, old_state, reason):
        #Dispatcher.connect("wired_change", self.wired_changed_cb)
        self.wired_device_deactive(widget, new_state, old_state, reason)

    def active_wired(self):
        """
        after active
        """
        self.gui.wire.set_active((True, True))
        self.change_status_icon("cable")
        self.let_rotate(False)
    
    def tray_resize(self, widget, height):
        pass

    def disactive_wired(self):
        """
        after diactive
        """
        #if self.net_manager.get_wired_state()[0]:
        #    self.gui.wire.set_active((True, False))

        if self.gui.wire.get_active():
            self.change_status_icon("wired")
        elif self.gui.wireless.get_active():
            self.change_status_icon("links")
        else:
            self.change_status_icon("cable_disconnect")
    #####=======================Wireless
    def switch_device(self, widget, device):
        print "switch device in tray"
        self.focus_device = device
        if self.gui.device_tree:
            self.gui.device_tree.visible_items[0].set_index(device)
        self.toggle_wireless()

    def __get_ssid_list(self):
        return self.net_manager.get_ap_list()

    def wireless_device_added(self, widget, path):
        self.init_wireless_signals()
        if len(self.net_manager.device_manager.wireless_devices) > 1:
            self.gui.add_switcher()

    def init_tree(self):
        print "init+tree"
        self.ap_list = self.net_manager.get_ap_list(self.focus_device)
        self.gui.set_ap(self.ap_list)

    def toggle_wireless(self):
        if self.gui.wireless.get_active():
            self.init_tree()
            if len(self.net_manager.device_manager.wireless_devices) > 1:
                self.gui.add_switcher()
            index = self.net_manager.get_active_connection(self.ap_list, self.focus_device)
            if index:
                print "Debug", index
                self.gui.set_active_ap(index, True)
            else:
                self.activate_wireless(self.focus_device)
            Dispatcher.request_resize()
        else:
            container_remove_all(self.gui.tree_box)
            self.gui.remove_switcher()
            Dispatcher.request_resize()
            
            def device_disactive():
                pass

            if self.gui.wire.get_active():
                self.change_status_icon("cable")
            else:
                self.change_status_icon("wifi_disconnect")
            self.net_manager.disactive_wireless_device(device_disactive)

    def init_wireless_signals(self):
        net_manager.device_manager.load_wireless_listener(self)
        self.gui.ap_tree.connect("single-click-item", self.ap_selected)
        self.selected_item = None
        #TODO signals 

    def ap_selected(self, widget, item, column, x, y):
        self.selected_item = item
    
    # wireless device singals 
    def wireless_device_active(self,  widget, new_state, old_state, reason):
        self.change_status_icon("links")
        #print "this device state:", widget.is_active()
        self.set_active_ap()
        self.let_rotate(False)

    def wireless_device_deactive(self, widget, new_state, old_state, reason):
        self.this_connection = None
        self.gui.wireless.set_sensitive(True)
        if net_manager.get_wireless_state()[1]:
            self.change_status_icon("links")
        elif self.gui.wire.get_active():
            self.change_status_icon("cable")
        else:
            self.change_status_icon("wifi_disconnect")

        if reason == 36:
            print "some device removed"
            self.net_manager.init_devices()
            self.gui.remove_switcher()
            self.focus_device = self.net_manager.wireless_devices[0]

        if reason == 39:
            print "user close"
            self.gui.wireless.set_active((True, False))

    def wireless_device_unavailable(self, widget, new_state, old_state, reason):
        self.gui.wireless.set_active((False, False))

    def wireless_activate_start(self, widget, new_state, old_state, reason):
        if old_state == 120:
            wifi = nm_module.cache.get_spec_object(widget)
            wifi.device_wifi_disconnect()
            return

        #connections = nm_module.nmclient.get_wireless_active_connection()
        self.this_connection = widget.get_real_active_connection()

        if self.selected_item and self.pwd_failed:
            widget.nm_device_disconnect()
            self.toggle_dialog(self.this_connection)
            self.pwd_failed = False
            return

        self.gui.wireless.set_active((True, True))
        self.change_status_icon("loading")
        self.let_rotate(True)
        self.this_device = widget
        #self.timer.Enabled = True
        #self.timer.Interval = WAIT_TIME

    def wireless_activate_failed(self, widget, new_state, old_state, reason):

        if reason == 7:
            self.toggle_dialog(self.this_connection, "wpa")
            # pwd failed

    def connect_by_ssid(self, widget, ssid, ap):
        connection = self.net_manager.connect_wireless_by_ssid(ssid)
        self.ap = ap
        print self.ap.object_path
        if connection and not isinstance(connection, NMRemoteConnection):
            security = self.net_manager.get_sec_ap(self.ap)
            if security:
                print "NMCONNECTION", security, self.ap.get_hw_address()
                self.toggle_dialog(connection, security)
            else:
                connection = nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')
                #ap = filter(lambda ap:ap.get_ssid() == ssid, self.ap_list)
                nm_module.nmclient.activate_connection_async(connection.object_path,
                                          self.focus_device.object_path,
                                           ap.object_path)

    def toggle_dialog(self, connection, security=None):
        if self.dialog_toggled_flag:
            return
        ssid = connection.get_setting("802-11-wireless").ssid
        if ssid != None:
            self.this.hide_menu()
            dialog = AskPasswordDialog(connection,
                              ssid,
                              key_mgmt=security,
                              cancel_callback=self.cancel_ask_pwd,
                              confirm_callback=self.pwd_changed)
            dialog.place_center()
            dialog.show_all()
        self.dialog_toggled_flag = True

    def cancel_ask_pwd(self):
        self.dialog_toggled_flag = False
        self.timer.Enabled = False
        self.timer.Interval = WAIT_TIME
        if self.this_device:
            self.this_device.nm_device_disconnect()
        

    def pwd_changed(self, pwd, connection):
        self.dialog_toggled_flag = False
        if not isinstance(connection, NMRemoteConnection):
            connection = nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')
        
        if hasattr(self, "ap"):
            if self.ap:
                self.net_manager.save_and_connect(pwd, connection, self.ap)
            else:
                self.net_manager.save_and_connect(pwd, connection, None)
        else:
            self.net_manager.save_and_connect(pwd, connection, None)
            
    def set_active_ap(self):
        index = self.net_manager.get_active_connection(self.ap_list, self.focus_device)
        print "active index", index
        self.gui.set_active_ap(index, True)

    def activate_wireless(self, device):
        """
        try to auto active wireless
        """
        self.net_manager.active_wireless_device(device)


    # TODO VPN

    def on_vpn_setting_change(self, name, event, conn):
        #connection = nm_module.cache.getobject(path)
        #connection.connect("removed", self.vpn_connection_remove_cb)

        if self.gui.vpn_state == False:
            self.gui.show_net("vpn")
            return

        if self.gui.vpn.get_active():
            self.gui.vpn.set_active((True, True), emit=True)

    def vpn_connection_remove_cb(self, name, event, data):
        if not nm_module.nm_remote_settings.get_vpn_connections():
            self.gui.remove_net('vpn')
            return
        if self.gui.vpn.get_active():
            self.gui.vpn.set_active((True, True), emit=True)

        #print "setting_added"
        # dss vpn setting add or remove will call this function

    def __init_vpn_list(self):
        #print "init vpn list in tray"
        self.gui.vpn_list.clear()
        cons = nm_module.nm_remote_settings.get_vpn_connections()
        self.gui.vpn_list.add_items(cons)
        self.gui.queue_draw()

    def toggle_vpn(self):
        if self.gui.vpn.get_active():
            self.__init_vpn_list()

            vpn_active = nm_module.nmclient.get_vpn_active_connection()
            if vpn_active:
                try:
                    for vpn in vpn_active:
                        index = nm_module.nm_remote_settings.get_vpn_connections().index(vpn.get_connection())
                        self.gui.vpn_list.set_active_by(index)
                        return
                except Exception, e:
                    print e
            else:
                pass
                #for active_conn in nm_module.nmclient.get_anti_vpn_active_connection():
                    #active_conn.vpn_auto_connect(self.vpn_active, self.vpn_stop, self.vpn_connecting)
        else:
            self.gui.vpn_list.clear()
            self.__vpn_failed_callback(None, None, None)
            for active in nm_module.nmclient.get_anti_vpn_active_connection():
                active.device_vpn_disconnect()

            vpn_active = nm_module.nmclient.get_vpn_active_connection()
            for vpn in vpn_active:
                nm_module.nmclient.deactive_connection_async(vpn.object_path)
        Dispatcher.request_resize()

    def on_user_stop_vpn(self, name, event, data):
        self.gui.vpn.set_active((True, False))

    def on_vpn_force_stop(self, widget):
        if self.active_vpn:
            return
        self.__vpn_failed_callback(None)
        self.no_vpn_connecting = True

    def vpn_start_cb(self, widget, path):
        vpn_active = nm_module.cache.get_spec_object(path)
        if vpn_active.get_vpnstate() < 5:
            self.on_vpn_connecting(None, None, path)

    def on_vpn_connecting(self, name, event, path):
        print "tray vpn connecting"
        if not self.gui.vpn.get_active():
            self.gui.vpn.set_active((True, True))

        self.change_status_icon('loading')
        self.let_rotate(True)
        self.this_setting = nm_module.cache.getobject(path).get_connection().object_path

    def __vpn_active_callback(self, name, event, path):
        #print name, data
        if self.gui.wire.get_active():
            self.change_status_icon("cable_vpn")
        elif self.gui.wireless.get_active():
            self.change_status_icon('links_vpn')

        index = map(lambda i: i.connection.object_path, self.gui.vpn_list).index(self.this_setting)

        self.gui.vpn_list.set_active_by(index)
        return 


    def __vpn_failed_callback(self, name, event, path):
        print "vpn failed callback"
        if self.gui.wire.get_active():
            self.change_status_icon("cable")
        elif self.gui.wireless.get_active():
            self.change_status_icon('links')
        self.this_setting = None

    # dsl settings
    def device_active(self, name, event, data):
        self.gui.dsl.set_active((True, True), emit=True)
        self.change_status_icon("cable")
        self.let_rotate(False)

    def device_unavailable(self, name, event, data):
        print "device unavailable"

    def device_deactive(self, name, event, data):
        new_state, old_state, reason = data
        if any([d.get_state() == 100 for d in net_manager.wired_devices]):
            self.change_status_icon("cable")
        else:
            if any([d.get_state() == 100 for d in net_manager.wireless_devices]):
                self.change_status_icon("links")
            else:
                self.change_status_icon("cable_disconnect")
            if reason != 0:
                self.gui.dsl.set_active((True, False))
                if reason == 40:
                    self.gui.dsl.set_active((True, False))

    def activate_start(self, name, event, data):
        if not self.gui.dsl.get_active():
            self.gui.dsl.set_active((True, True))
        self.change_status_icon("loading")
        self.let_rotate(True)


    def activate_failed(self, name, event, data):
        print "device failded"
        new_state, old_state, reason = data
        if self.gui.wireless.get_active():
            self.change_status_icon('links')
        else:
            self.change_status_icon('wifi_disconnect')
        if reason == 13:
            self.dsl.set_active(False)

    def __init_dsl_signals(self):
        signal_list = ["device_active",
                              "device_deactive",
                              "device_unavailable",
                              "activate_start",
                              "activate_failed"]

        for signal in signal_list:
            event_manager.add_callback(('dsl_%s'%signal).replace("_", "-"), getattr(self, signal))

        event_manager.add_callback('dsl-new-added', self.on_dsl_setting_change)
        event_manager.add_callback('dsl-connection-removed', self.dsl_connection_remove_cb)

    def on_dsl_setting_change(self, name, event, conn):
        if self.gui.dsl_state == False:
            self.gui.show_net("dsl")
            return

        if self.gui.dsl.get_active():
            self.gui.dsl.set_active((True, True), emit=True)

    def dsl_connection_remove_cb(self, name, event, data):
        if not nm_module.nm_remote_settings.get_pppoe_connections():
            self.gui.remove_net('dsl')
            return
        if self.gui.dsl.get_active():
            self.gui.dsl.set_active((True, True), emit=True)
        
    def __init_dsl_list(self):
        self.gui.dsl_list.clear()
        cons = nm_module.nm_remote_settings.get_pppoe_connections()
        self.gui.dsl_list.add_items(cons)
        self.gui.queue_draw()

    def toggle_dsl(self):
        if self.gui.dsl.get_active():
            self.__init_dsl_list()

            dsl_active = nm_module.nmclient.get_pppoe_active_connection()
            if dsl_active:
                try:
                    for dsl in dsl_active:
                        index = nm_module.nm_remote_settings.get_pppoe_connections().index(dsl.get_connection())
                        self.gui.dsl_list.set_active_by(index)
                        return
                except Exception, e:
                    print e
            else:
                pass
        
        else:
            self.gui.dsl_list.clear()
            for wired_device in net_manager.device_manager.wired_devices:
                wired_device.nm_device_disconnect()
        
        Dispatcher.request_resize()

            
    # tray settings
    
    def change_status_icon(self, icon_name):
        """
        change status icon state
        """
        self.timer.Enabled = False
        self.timer.Interval = WAIT_TIME
        self.let_rotate(False)
        self.tray_icon.set_icon_theme(icon_name)

    def let_rotate(self, rotate_check, interval=100):
        self.tray_icon.set_rotate(rotate_check, interval)

    def run(self):
        return True

    def insert(self):
        return 3

    def more_setting(self, button):
        try:
            self.this.hide_menu()
            Popen(("deepin-system-settings", "network"))
        except Exception, e:
            print e
            pass
        
    def id(self):
        return "tray-network_plugin"

    def plugin_widget(self):
        return self.gui 
    
    def tray_show_more(self, widget):
        print "tray show more"

    def show_menu(self):
        self.menu_showed = True
        height = self.gui.get_widget_height()
        self.this.set_size_request(185, height + 46)
        #Dispatcher.request_resize()

    def hide_menu(self):
        self.menu_showed = False
        if self.gui.wireless.get_active() and hasattr(self, "ap_list"):
            self.gui.reset_tree()

    def request_resize(self, widget):
        """
        resize this first
        """
        self.this.resize(1,1)
        if self.menu_showed:
            self.this.hide_menu()
            #self.this.set_size_request(185, height + 40)
            self.show_menu()
            self.this.show_menu()
        #height = self.gui.get_widget_height()

def return_insert():
    return 3

def return_id():
    return "network"
    
def return_plugin():
    return TrayNetworkPlugin
