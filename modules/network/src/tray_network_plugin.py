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
from tray_log import tray_log

class BaseMixIn(object):

    def change_status_icon(self, load_image_name):
        event_manager.emit("change-status-icon", load_image_name)

    def hide_menu(self, state):
        event_manager.emit("hide_menu", state)

    def close(self):
        # used when network_manager restarts
        self.this_gui.set_active((False, False))

    def check_net_state(self):
        # which tray icon to show
        wire = any([d.get_state() == 100 for d in net_manager.device_manager.wired_devices])

        mm = any([d.get_state() == 100 for d in net_manager.device_manager.mm_devices])

        wireless = any([d.get_state() == 100 for d in net_manager.device_manager.wireless_devices])

        if wireless:
            self.change_status_icon("links")
        else:
            if wire or mm:
                self.change_status_icon("cable")
            else:
                self.change_status_icon("cable_disconnect")

    def net_state(self):
        pass

class WireSection(BaseMixIn):

    def __init__(self, tray_ui):
        tray_log.debug()
        self.gui = tray_ui
        self.this_gui = tray_ui.wire
        self._init_signals()
        self._init_section()

    def _init_section(self):
        tray_log.debug()
        wired_state = net_manager.get_wired_state()
        if wired_state:
            self.gui.show_net("wire")
            self.gui.wire.set_active(wired_state)
            if wired_state[0] and wired_state[1]:
                self.change_status_icon("cable")
            else:
                self.change_status_icon("cable_disconnect")
        else:
            self.gui.remove_net("wire")
            return

    def _init_signals(self):
        tray_log.debug()
        self.gui.wire.connect_to_toggle(self._toggle_callback)
        Dispatcher.connect("wired-device-add", lambda w,p: self.init_wired_signals())
        self.init_wired_signals()

    def init_wired_signals(self):
        tray_log.debug()
        net_manager.device_manager.load_wired_listener(self)

    def _toggle_callback(self):
        tray_log.debug()
        if self.gui.wire.get_active():
            tray_log.debug("active wired device")
            net_manager.active_wired_device()
        else:
            net_manager.disactive_wired_device()

    # Actions callback
    def wired_device_active(self, widget, new_state, old_state, reason):
        '''
        wired device is active , state 100. button toggle on,
        also change trayicon
        '''
        tray_log.debug("wired active")
        self.gui.wire.set_active((True, True))
        self.change_status_icon("cable")

    def wired_device_deactive(self, widget, new_state, old_state, reason):
        '''
        wired device deavtive
        . user disconnect, toggle off
        . reason 40 means cable was unpluged, make it insensitive
        '''
        tray_log.debug("===wired deactive", new_state, reason)
        if reason != 0:
            if not any([d.get_state() == 100 for d in net_manager.device_manager.wired_devices]):
                if reason == 36:
                    tray_log.debug("there's one device removed")
                if reason == 40:
                    # cable unpluged
                    self.gui.wire.set_active((False, False))
                else:
                    self.gui.wire.set_active((True, False))
            self.check_net_state()

    def wired_device_unavailable(self,  widget, new_state, old_state, reason):
        '''
        make it insensitive for sure
        '''
        tray_log.debug("wired unaviable")
        if not any([d.get_state() == 100 for d in net_manager.device_manager.wired_devices]):
            self.gui.wire.set_active((False, False))
            event_manager.emit("dsl-init-state", None)
            self.check_net_state()
        #self.wired_device_deactive(widget, new_state, old_state, reason)

    def wired_device_available(self, widget, new_state, old_state, reason):
        '''
        Once device available, set sensitive to True
        '''
        tray_log.debug("wired available")
        if not any([d.get_state() == 100 for d in net_manager.device_manager.wired_devices]):
            self.gui.wire.set_active((True, False))
        event_manager.emit("dsl-init-state", None)

    def wired_activate_start(self, widget, new_state, old_state, reason):
        '''
        device start to connect
        '''
        tray_log.debug("===wired start")
        if not self.gui.wire.get_active():
            self.gui.wire.set_active((True, True))
        self.change_status_icon("loading")

    def wired_activate_failed(self, widget, new_state, old_state, reason):
        '''
        Just disconnect
        '''
        tray_log.debug("wired failed", reason)
        self.gui.wire.set_active((True, False))
        # force loading stop
        self.check_net_state()

class WirelessSection(BaseMixIn):

    def __init__(self, gui):
        tray_log.debug()
        self.gui = gui
        self.this_gui = self.gui.wireless

        self.this_device = None
        self.this_connection = None
        self.dialog_toggled_flag = False
        self.focus_device = None
        self.pwd_failed = False

        self._init_signals()
        self._init_section()

    def _init_section(self):
        tray_log.debug()
        wireless_state = net_manager.get_wireless_state()
        if wireless_state:
            # always focus on first device on init
            self.focus_device = net_manager.device_manager.wireless_devices[0]
            self.gui.show_net("wireless")
            self.gui.wireless.set_active(wireless_state)
            if wireless_state[0] and wireless_state[1]:
                self.change_status_icon("links")
            else:
                if not self.gui.wire.get_active():
                    self.change_status_icon("wifi_disconnect")
        else:
            self.gui.remove_net("wireless")

    def _init_signals(self):
        tray_log.debug()
        self.this_gui.connect_to_toggle(self._toggle_callback)
        Dispatcher.connect("switch-device", self.switch_device)
        Dispatcher.connect("wireless-device-add", self.wireless_device_added)
        Dispatcher.connect("ap-added", self.wireless_ap_added)
        Dispatcher.connect("ap-removed", self.wireless_ap_removed)
        Dispatcher.connect("connect_by_ssid", self.connect_by_ssid)
        self.init_wireless_signals()

    def init_wireless_signals(self):
        tray_log.debug()
        net_manager.device_manager.load_wireless_listener(self)
        self.gui.ap_tree.connect("single-click-item", self.ap_selected)
        self.selected_item = None

    def ap_selected(self, widget, item, column, x, y):
        '''
        selected item when user click item
        '''
        self.selected_item = item

    def switch_device(self, widget, device):
        #print "switch device in tray"
        '''
        this function is used on multi device support
        '''
        self.focus_device = device
        if self.gui.device_tree:
            self.gui.device_tree.visible_items[0].set_index(device)
        self._toggle_callback()

    def wireless_device_added(self, widget, path):
        tray_log.info("one wireless device added")
        self.init_wireless_signals()
        if len(net_manager.device_manager.wireless_devices) > 1:
            self.gui.add_switcher()

    def init_tree(self):
        try:
            self.ap_list = net_manager.get_ap_list(self.focus_device)
        except Exception,e:
            tray_log.error("no self.focus_device")
            raise e
        self.gui.set_ap(self.ap_list)

    def _toggle_callback(self):
        tray_log.debug()
        if self.gui.wireless.get_active():
            self.init_tree()
            if len(net_manager.device_manager.wireless_devices) > 1:
                self.gui.add_switcher()
            index = net_manager.get_active_connection(self.ap_list, self.focus_device)
            if index:
                tray_log.info(index)
                self.gui.set_active_ap(index, True)
                # wireless is active for sure, so check status icon 
                self.check_net_state()
            else:
                self.activate_wireless(self.focus_device)
            Dispatcher.request_resize()
        else:
            container_remove_all(self.gui.tree_box)
            self.gui.remove_switcher()
            Dispatcher.request_resize()
            
            if self.gui.wire.get_active():
                self.change_status_icon("cable")
            else:
                self.change_status_icon("wifi_disconnect")
            net_manager.disactive_wireless_device()

    # wireless device singals 
    def wireless_device_active(self,  widget, new_state, old_state, reason):
        tray_log.debug("wireless device active")
        self.change_status_icon("links")
        self.set_active_ap()

    def wireless_device_deactive(self, widget, new_state, old_state, reason):
        tray_log.debug("==wireless deactive", new_state, old_state, reason)
        self.this_connection = None
        self.gui.wireless.set_sensitive(True)
        if net_manager.get_wireless_state()[1]:
            self.change_status_icon("links")
        elif self.gui.wire.get_active():
            self.change_status_icon("cable")
        else:
            self.change_status_icon("wifi_disconnect")

        if reason == 36:
            net_manager.init_devices()
            self.gui.remove_switcher()
            try:
                self.focus_device = net_manager.wireless_devices[0]
            except:
                tray_log.info("there's no wireless device")
                self.focus_device = None
        if old_state == 50:
            return
        if reason == 39:
            #print "user close"
            self.gui.wireless.set_active((True, False))

    def wireless_device_unavailable(self, widget, new_state, old_state, reason):
        tray_log.debug("unaviable")
        self.gui.wireless.set_active((False, False))
        self.check_net_state()

    def wireless_device_available(self, widget, new_state, old_state, reason):
        tray_log.debug("aviable")
        self.gui.wireless.set_active((True, False))

    def wireless_activate_start(self, widget, new_state, old_state, reason):
        tray_log.debug("==wireless start")
        if old_state == 120 or self.dialog_toggled_flag:
            wifi = nm_module.cache.get_spec_object(widget.object_path)
            wifi.device_wifi_disconnect()
            return

        #connections = nm_module.nmclient.get_wireless_active_connection()
        self.this_connection = widget.get_real_active_connection()
        if self._get_active_item():
            for item in self._get_active_item():
                item.set_active(False)

        if self.selected_item and self.pwd_failed:
            widget.nm_device_disconnect()
            self.toggle_dialog(self.this_connection)
            self.pwd_failed = False
            return

        self.gui.wireless.set_active((True, True))
        self.change_status_icon("loading")
        self.this_device = widget

    def wireless_activate_failed(self, widget, new_state, old_state, reason):
        tray_log.debug("wireless failed")

        if reason == 7:
            self.toggle_dialog(self.this_connection, "wpa")
            # pwd failed
    def wireless_ap_added(self, widget):
        #print "wireless_ap_added in tray"
        if self.gui.wireless.get_active():
            self.gui.wireless.set_active((True, True), emit=True)

    def wireless_ap_removed(self, widget):
        # since this print too much info ....
        #tray_log.info("wireless ap removed in tray")
        if self.gui.wireless.get_active():
            self.gui.wireless.set_active((True, True), emit=True)

    def connect_by_ssid(self, widget, ssid, ap):
        connection = net_manager.connect_wireless_by_ssid(ssid)
        self.ap = ap
        if connection and not isinstance(connection, NMRemoteConnection):
            security = net_manager.get_sec_ap(self.ap)
            if security:
                tray_log.debug("NMCONNECTION", security, self.ap.get_hw_address())
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
            self.hide_menu(True)
            tray_log.debug(ssid, security)
            dialog = AskPasswordDialog(connection,
                              ssid,
                              key_mgmt=security,
                              cancel_callback=self.cancel_ask_pwd,
                              confirm_callback=self.pwd_changed)

            dialog.place_center()
            dialog.show_all()
        self.dialog_toggled_flag = True
        tray_log.debug()

    def cancel_ask_pwd(self):
        self.dialog_toggled_flag = False
        if self.this_device:
            self.this_device.nm_device_disconnect()
        
    def pwd_changed(self, pwd, connection):
        self.dialog_toggled_flag = False
        if not isinstance(connection, NMRemoteConnection):
            connection = nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')
        
        if hasattr(self, "ap"):
            if self.ap:
                net_manager.save_and_connect(pwd, connection, self.ap)
            else:
                net_manager.save_and_connect(pwd, connection, None)
        else:
            net_manager.save_and_connect(pwd, connection, None)
            
    def set_active_ap(self):
        index = net_manager.get_active_connection(self.ap_list, self.focus_device)
        tray_log.info("acitve_index"%index)
        self.gui.set_active_ap(index, True)

    def activate_wireless(self, device):
        """
        try to auto active wireless
        """
        net_manager.active_wireless_device(device)

    def _get_active_item(self):
        return filter(lambda i: i.get_active(), self.gui.ap_tree.visible_items)

class MobileSection(BaseMixIn):

    def __init__(self, gui):
        self.gui = gui
        self.this_gui = self.gui.mobile
        
        self._init_signals()
        self._init_section()

    def _init_section(self):
        if net_manager.get_mm_devices():
            self.gui.show_net("mobile")
        else:
            self.gui.remove_net("mobile")

    def _init_signals(self):
        self.this_gui.connect_to_toggle(self._toggle_callback)
        Dispatcher.connect("mmdevice-added", lambda w,p: self.init_mm_signals())
        self.init_mm_signals()

    def init_mm_signals(self):
        net_manager.device_manager.load_mm_listener(self)

    def _toggle_callback(self):
        if self.gui.mobile.get_active():
            self.mm_device = net_manager.connect_mm_device()
        else:
            net_manager.disconnect_mm_device()

    def mm_device_active(self, widget, new_state, old_state, reason):
        tray_log.debug("===mobile active")
        self.gui.mobile.set_active((True, True))
        self.change_status_icon("cable")

    def mm_device_deactive(self, widget, new_state, old_state, reason):
        tray_log.debug("===mobile deactive", new_state, reason)
        self.gui.mobile.set_active((True, False))

        self.check_net_state()
        #if self.gui.wire.get_active():
            #self.change_status_icon("cable")
        #elif self.gui.wireless.get_active():
            #self.change_status_icon("links")
        #else:
            #self.change_status_icon("cable_disconnect")

    def mm_device_unavailable(self,  widget, new_state, old_state, reason):
        self.gui.mobile.set_active((True, False))

    def mm_device_available(self,  widget, new_state, old_state, reason):
        self.gui.mobile.set_active((True, False))

    def mm_activate_start(self, widget, new_state, old_state, reason):
        tray_log.debug("===mobile connecting")
        self.gui.mobile.set_active((True, True))
        self.change_status_icon("loading")

    def mm_activate_failed(self, widget, new_state, old_state, reason):
        tray_log.debug("mobile active failed")
        self.gui.mobile.set_active((True, False))

        self.check_net_state()
        #if self.gui.wire.get_active():
            #self.change_status_icon("cable")
        #elif self.gui.wireless.get_active():
            #self.change_status_icon("links")
        #else:
            #self.change_status_icon("cable_disconnect")
class VPNSection(BaseMixIn):

    def __init__(self, gui):
        self.gui = gui
        self.this_gui = self.gui.vpn

        self.this_setting = None
        self.vpn_path = None

        self._init_signals()
        self._init_section()

    def _init_section(self):
        if nm_module.nm_remote_settings.get_vpn_connections():
            self.gui.show_net("vpn")
            self.gui.vpn_list.connecting_cb = lambda:self.change_status_icon('loading')
            self.active_vpn = None
            self.no_vpn_connecting = False
            if nm_module.nmclient.get_vpn_active_connection():
                self.gui.vpn.set_active((True, True))
                self.change_status_icon("links_vpn")

            tray_log.info("vpn section show and start")
        else:
            self.gui.remove_net("vpn")

    def _init_signals(self):
        # vpn signals 
        self.this_gui.connect_to_toggle(self._toggle_callback)
        event_manager.add_callback("vpn-connecting", self.__on_vpn_connecting)
        event_manager.add_callback('vpn-connected', self.__vpn_active_callback)
        event_manager.add_callback('vpn-disconnected', self.__vpn_failed_callback)
        event_manager.add_callback('vpn-user-disconnect', self.__on_user_stop_vpn)
        # from nm_remote_connection
        event_manager.add_callback('vpn-connection-removed', self.__vpn_connection_remove_cb)
        # from nm_remote_setting
        event_manager.add_callback('vpn-new-added', self.__on_vpn_setting_change)
        Dispatcher.connect('vpn-start', self.vpn_start_cb)
        event_manager.add_callback('user-toggle-off-vpn-main', self.user_toggle_off_vpn_main)

    def user_toggle_off_vpn_main(self, name, event, data):
        tray_log.debug("from MAIN toggle off")
        self.gui.vpn.set_active((True, False))
    
    def __on_vpn_setting_change(self, name, event, conn):
        '''
        dss user add vpn setting
        show vpn if at least one setting
        '''
        tray_log.debug("vpn setting added")
        if self.gui.vpn_state == False:
            self.gui.show_net("vpn")
            return

        if self.gui.vpn.get_active():
            self.gui.vpn.set_active((True, True), emit=True)

    def __vpn_connection_remove_cb(self, name, event, data):

        tray_log.debug("vpn connection was destroyed")
        if not nm_module.nm_remote_settings.get_vpn_connections():
            self.gui.remove_net('vpn')
            return
        if self.gui.vpn.get_active():
            self.gui.vpn.set_active((True, True), emit=True)

    def __init_vpn_list(self):
        self.gui.vpn_list.clear()
        cons = nm_module.nm_remote_settings.get_vpn_connections()
        self.gui.vpn_list.add_items(cons)
        self.gui.queue_draw()

    def _toggle_callback(self):
        if self.gui.vpn.get_active():
            tray_log.info("*vpn toggle on*")
            self.__init_vpn_list()
            vpn_active = nm_module.nmclient.get_vpn_active_connection()
            if vpn_active:
                try:
                    for vpn in vpn_active:
                        index = nm_module.nm_remote_settings.get_vpn_connections().index(vpn.get_connection())
                        self.gui.vpn_list.set_active_by(index)
                        self.vpn_path = vpn.object_path
                        return
                except Exception, e:
                    tray_log.error(e)
            else:
                pass
        else:
            self.user_toggle_off_button()
            tray_log.info("*vpn toggle off*")
            self.gui.vpn_list.clear()
            self.check_net_state()
            for active in nm_module.nmclient.get_anti_vpn_active_connection():
                active.device_vpn_disconnect()
            
            if self.vpn_path:
                nm_module.nmclient.deactive_connection_async(self.vpn_path)
            self.this_setting = None
        Dispatcher.request_resize()

    def user_toggle_off_button(self):
        tray_log.debug("user toggle off from tray")
        net_manager.emit_user_toggle_off("vpn-tray")

    def __on_user_stop_vpn(self, name, event, data):
        tray_log.debug("user stop vpn")
        self.gui.vpn.set_active((True, False))

    def vpn_start_cb(self, widget, path):
        tray_log.debug("vpn_start")
        vpn_active = nm_module.cache.get_spec_object(path)
        if vpn_active.get_vpnstate() < 5:
            self.__on_vpn_connecting(None, None, path)

    def __on_vpn_connecting(self, name, event, path):
        tray_log.debug("vpn connecting start")
        #print "tray vpn connecting"
        if not self.gui.vpn.get_active():
            self.gui.vpn.set_active((True, True))

        self.change_status_icon('loading')
        try:
            self.this_setting = nm_module.cache.getobject(path).get_connection().object_path
        except Exception, e:
            tray_log.error(e)
            self.this_setting = None
        self.vpn_path = path

    def __vpn_active_callback(self, name, event, path):
        #print name, data
        path = path
        tray_log.debug("==Vpn active")

        self.set_device_vpn(nm_module.cache.getobject(path))
        try:
            index = map(lambda i: i.connection.object_path, self.gui.vpn_list).index(self.this_setting)
        except Exception, e:
            tray_log.error(e)
            index = []
        self.gui.vpn_list.set_active_by(index)
        return 

    def set_device_vpn(self, vpn_active):
        tray_log.debug(vpn_active)
        for d in vpn_active.get_devices():
            tray_log.debug(d)
            if d.get_device_type() == 1:
                self.change_status_icon("cable_vpn")
            else:
                self.change_status_icon("links_vpn")

    def __vpn_failed_callback(self, name, event, path):
        tray_log.debug("==Vpn active failed or disconnected")
        #print "vpn failed callback"
        self.check_net_state()
        self.gui.vpn_list.reset_state()
        self.this_setting = None
        self.vpn_path = None

class DSLSection(BaseMixIn):

    def __init__(self, gui):
        self.gui = gui
        self.this_gui = self.gui.dsl
        
        self._init_signals()
        self._init_section()

    def _init_section(self):
        wired_state = net_manager.get_wired_state()
        if wired_state[0] and nm_module.nm_remote_settings.get_pppoe_connections():
            self.gui.show_net("dsl")
            self.gui.dsl_list.connecting_cb = lambda:self.change_status_icon('loading')
            tray_log.info("dsl section start and show")
            if nm_module.nmclient.get_pppoe_active_connection():
                self.gui.dsl.set_active((True, True))
                self.change_status_icon("cable")
        else:
            self.gui.remove_net("dsl")

    def _init_signals(self):
        self.this_gui.connect_to_toggle(self._toggle_callback)
        signal_list = ["device_active",
                              "device_deactive",
                              "device_unavailable",
                              "activate_start",
                              "activate_failed"]

        for signal in signal_list:
            event_manager.add_callback(('dsl_%s'%signal).replace("_", "-"), getattr(self, signal))

        event_manager.add_callback('dsl-new-added', self.on_dsl_setting_change)
        event_manager.add_callback('dsl-connection-removed', self.dsl_connection_remove_cb)

        # wired available will re init dsl
        event_manager.add_callback('dsl-init-state', self.need_init)

    # dsl settings
    def need_init(self, name, event, data):
        tray_log.debug()
        self._init_section()
        Dispatcher.emit("request_resize") 

    def device_active(self, name, event, data):
        tray_log.debug("=== dsl active", data)
        self.gui.dsl.set_active((True, True), emit=True)
        self.change_status_icon("cable")

    def device_unavailable(self, name, event, data):
        tray_log.debug("device unavailable")

    def device_deactive(self, name, event, data):
        tray_log.debug('dsl deactive', data) 
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
        tray_log.debug('dsl active start', data)
        if not self.gui.dsl.get_active():
            self.gui.dsl.set_active((True, True))
        self.change_status_icon("loading")

    def activate_failed(self, name, event, data):
        tray_log.debug("dsl active failed", data)
        #print "device failded"
        new_state, old_state, reason = data
        if self.gui.wireless.get_active():
            self.change_status_icon('links')
        else:
            self.change_status_icon('wifi_disconnect')
        if reason == 13:
            self.gui.dsl.set_active((True, False))


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

    def _toggle_callback(self):
        if self.gui.dsl.get_active():
            self.__init_dsl_list()

            dsl_active = nm_module.nmclient.get_pppoe_active_connection()
            tray_log.debug(dsl_active)
            if dsl_active:
                try:
                    for dsl in dsl_active:
                        index = nm_module.nm_remote_settings.get_pppoe_connections().index(dsl.get_connection())
                        self.gui.dsl_list.set_active_by(index)
                        return
                except Exception, e:
                    tray_log.error(e)
            else:
                pass
        
        else:
            self.gui.dsl_list.clear()
            for wired_device in net_manager.device_manager.wired_devices:
                wired_device.nm_device_disconnect()
        
        Dispatcher.request_resize()
            
class TrayNetworkPlugin(object):
    sections = [WireSection, 
                WirelessSection,
                MobileSection,
                VPNSection,
                DSLSection,
                ]
    def __init__(self):

        self.menu_showed = False
        self.need_auth_flag = False
        self.this_device = None
        self.this_connection = None
        self.dialog_toggled_flag = False
        
        # TODO add section signal init

    def _init_sections(self):
        event_manager.add_callback('change-status-icon', self.change_status_icon)
        event_manager.add_callback('hide_menu', self.hide_this_menu)
        self.section_instance = []
        for section in self.sections:
            self.section_instance.append(section(self.gui))

    def _init_tray_signals(self):
        Dispatcher.connect("request_resize", self.request_resize)
        Dispatcher.connect("recheck-section", self.recheck_sections)
        Dispatcher.connect("service_start_do_more", self.service_start_do_more)
        self.gui.button_more.connect("clicked", self.more_setting_callback)

    def more_setting_callback(self, button):
        '''
        show dss main program
        '''
        try:
            self.this.hide_menu()
            Popen(("deepin-system-settings", "network"))
        except Exception, e:
            print e
            pass

    def request_resize(self, widget):
        """
        resize this first
        """
        self.this.resize(1,1)
        # dirty way to refresh
        if self.menu_showed:
            self.this.hide_menu()
            self.show_menu()
            self.tray_icon.emit("popup-menu-event", TrayNetworkPlugin.__class__)
            #self.this.show_menu()

    def service_start_do_more(self, widget):
        self.init_wired_signals()
        self.init_wireless_signals()
        self.init_mm_signals()

    def recheck_sections(self, widget, index):
        #print "recheck sections"
        if index == 0:
            self.section_instance[index]._init_section()
            self.section_instance[4]._init_section()
        else:
            map(lambda s: s._init_section(), self.section_instance)
        Dispatcher.emit("request-resize")

    # tray settings
    def init_values(self, this_list):
        self.this_list = this_list
        self.this = self.this_list[0]
        self.tray_icon = self.this_list[1]

        self.gui = TrayUI()
        net_manager.init_devices()
        self._init_tray_signals()
        self._init_sections()
    
    def change_status_icon(self, name, event, data):
        """
        change status icon state
        """
        tray_log.debug("change status icon", data)
        icon_name = data
        self.let_rotate(False)
        self.tray_icon.set_icon_theme(icon_name)
        if icon_name == 'loading':
            self.let_rotate(True)

    def let_rotate(self, rotate_check, interval=100):
        self.tray_icon.set_rotate(rotate_check, interval)

    def run(self):
        return True

    def insert(self):
        return 3

    def id(self):
        return "tray-network_plugin"

    def plugin_widget(self):
        return self.gui 

    def hide_this_menu(self, name, event, data):
        '''
        Callback from Basemixin
        '''
        tray_log.debug("hide this menu", data)
        state = data
        if state:
            self.this.hide_menu()
        else:
            self.show_menu()

    def show_menu(self):
        self.menu_showed = True
        height = self.gui.get_widget_height()
        self.this.set_size_request(185, height + 46)

    def hide_menu(self):
        self.menu_showed = False
        if self.gui.wireless.get_active() and hasattr(self, "ap_list"):
            self.gui.reset_tree()

def return_insert():
    return 3

def return_id():
    return "network"
    
def return_plugin():
    return TrayNetworkPlugin
