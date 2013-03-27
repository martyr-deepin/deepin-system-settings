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

import dss
from proxy_config import ProxyConfig, ProxySettings
import sys
import os
from dss import app_theme
from dtk.ui.theme import ui_theme
from dtk.ui.new_treeview import TreeView
from dtk.ui.draw import  draw_line
from dtk.ui.utils import color_hex_to_cairo, container_remove_all, get_content_size
from deepin_utils.file import  get_parent_dir
from dtk.ui.label import Label
from dtk.ui.scrolled_window import ScrolledWindow
import gtk

from container import Contain, ToggleThread
from lists import (WiredItem, WirelessItem,
                  HidenItem, InfoItem, DSLItem, MobileItem,
                  VPNItem)
from widgets import AskPasswordDialog
from dsl_config import DSLSetting
from vpn_config import VPNSetting
from mobile_config import MobileSetting
from regions import Region
from settings_widget import HotspotBox

#from nmlib.nmcache import cache
from nm_modules import nm_module
from helper import Dispatcher
from shared_methods import net_manager

sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
#from module_frame import ModuleFrame 
#from nmlib.servicemanager import servicemanager

from nls import _
from constants import *

slider = nm_module.slider
PADDING = 32
from dtk.ui.theme import DynamicColor
LABEL_COLOR = DynamicColor("#666666")

def pack_start(parent, child_list, expand=False, fill=False):
    for child in child_list:
        parent.pack_start(child, expand, fill)

class Section(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)

    def load(self, toggle, content=[]):
        self.content_box = gtk.VBox(spacing=15)
        self.pack_start(toggle, False, False)
        toggle.switch.connect("toggled", self.toggle_callback)

        self.tree = TreeView([])
        self.tree.set_expand_column(1)
        self.tree.draw_mask = self.draw_mask
        #self.content_box.pack_start(self.tree, False, False)
        content.insert(0, self.tree)
            
        for c in content:
            self.content_box.pack_start(c, False, False)

        self.align = self._set_align()
        self.pack_start(self.align, False, False)
        self.show_all()

    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()

    def _set_align(self):
        align = gtk.Alignment(0,0,1,0)
        align.set_padding(0,0,PADDING,11 + 11)
        #align.add(self.content_box)
        return align

    def toggle_callback(self, widget):
        is_active = widget.get_active()
        if is_active:
            if self.content_box not in self.align.get_children():
                self.align.add(self.content_box)
            self.show_all()

            self.td = ToggleThread(self.get_list, self.tree, self.toggle_on_after)
            self.td.start()
        else:
            self.align.remove(self.content_box)
            self.td.stop_run()
            self.toggle_off()

    def toggle_on(self):
        '''
        method cb when toggle on
        '''
        print "on"
        pass

    def toggle_on_after(self):
        pass

    def toggle_off(self):
        print "off"
        pass
    
    def get_list(self):
        pass
    
    def section_show(self):
        self.set_no_show_all(False)
        self.show_all()

    def section_hide(self):
        self.set_no_show_all(True)
        self.hide()

class TestSection(Section):

    def __init__(self):
        Section.__init__(self)
        self.wire = Contain(app_theme.get_pixbuf("network/cable.png"), _("Wired"), lambda w: w)
        self.button = gtk.Button("Test")
        self.label = Label("this is a test")
        self.load(self.wire, (self.button, self.label))

class WiredDevice(object):

    def __init__(self):
        pass

    def _init_signals(self):
        net_manager.device_manager.load_wired_listener(self)

    def wired_device_active(self, widget, new_state, old_state, reason):
        index = self.wired_devices.index(widget)
        self.wire.set_active(True)
        if self.tree.visible_items != []:
            self.tree.visible_items[index].set_net_state(2)
            self.tree.queue_draw()

    def wired_device_deactive(self, widget, new_state, old_state, reason):
        index = self.wired_devices.index(widget)
        if not reason == 0:
            if self.tree.visible_items != []:
                self.tree.visible_items[index].set_net_state(0)
                self.tree.queue_draw()

    def wired_device_unavailable(self,  widget, new_state, old_state, reason):
        pass

    def wired_activate_start(self, widget, new_state, old_state, reason):
        index = self.wired_devices.index(widget)
        if self.tree.visible_items != []:
            self.tree.visible_items[index].set_net_state(1)
            self.tree.queue_draw()

    def wired_activate_failed(self, widget, new_state, old_state, reason):
        pass

class WiredSection(Section, WiredDevice):

    def __init__(self):
        Section.__init__(self)
        WiredDevice.__init__(self)
        self.wired_devices = net_manager.device_manager.get_wired_devices()
        self.init_state()

        self.init_signals()
    
    @classmethod
    def show_or_hide(self):
        if net_manager.device_manager.get_wired_devices():
            return True
        else:
            return False

    def init_state(self):
        if self.wired_devices:
            self.wire = Contain(app_theme.get_pixbuf("network/cable.png"), _("Wired"), lambda w:w)
            #self.tree = TreeView([])
            #self.tree.set_expand_column(1)
            self.load(self.wire, [])
            if self.get_state(self.wired_devices):
                self.wire.set_active(True)
        else:
            pass

    def init_signals(self):
        Dispatcher.connect("wired-device-add", self.device_added)
        self._init_signals()
    
    def get_state(self, devices):
        for d in devices:
            if d.get_state() == 100:
                return True
        return False
    
    def device_added(self, widget, device):
        print "device_added"
        self.wired_devices = net_manager.device_manager.get_wired_devices()
        self.wire.set_active(True, emit=True)

    def get_list(self):
        return map(lambda d: WiredItem(d), self.wired_devices)

    def toggle_on(self):
        self.tree.delete_all_items()
        item_list = self.get_list()
        if item_list:
            item_list[-1].is_last = True
            
            self.tree.add_items(item_list, 0, True)
            self.tree.set_size_request(-1, len(self.tree.visible_items)*30)

    def toggle_on_after(self):
        for i,d in enumerate(self.wired_devices):
            if d.get_state() == 100:
                self.tree.visible_items[i].set_net_state(2)
            else:
                device_ethernet = nm_module.cache.get_spec_object(d.object_path)
                device_ethernet.auto_connect()

    def toggle_off(self):
        for wired_device in self.wired_devices:
            wired_device.nm_device_disconnect()

class WirelessDevice(object):
    def __init__(self):
        self.pwd_failed = False

    def _init_signals(self):
        net_manager.device_manager.load_wireless_listener(self)

    def wireless_device_active(self,  widget, new_state, old_state, reason):
        self.pwd_failed = False

        if self.selected_item:
            self.selected_item.set_net_state(2)
            return

        index = self.get_actives(self.ap_list)
        if index:
            map(lambda i: self.tree.visible_items[i].set_net_state(2), index)

    def wireless_device_deactive(self, widget, new_state, old_state, reason):
        self.wireless.set_sensitive(True)
        if new_state == 60:
            wifi = nm_module.cache.get_spec_object(widget.object_path)
            wifi.nm_device_disconnect()
            return
        if reason == 39:
            self.wireless.set_active(False)
            return
            #if self.hotspot.get_net_state() == 1:
            #if self._get_active_item():
                #for item in self._get_active_item():
                    #item.set_net_state(0)
                #return

            # toggle off
            #self.toggle_lock = True
            #self.wireless.set_active(False)

        if self._get_active_item():
            for item in self._get_active_item():
                item.set_net_state(0)

    def wireless_device_unavailable(self, widget, new_state, old_state, reason):
        pass

    def wireless_activate_start(self, widget, new_state, old_state, reason):
        self.this_connection = widget.get_real_active_connection()
        print "Debug: (wireless active start in main):",self.this_connection.get_setting("802-11-wireless").ssid
        if not self.wireless.get_active():
            self.wireless.set_active(True)

        if self._get_active_item():
            for item in self._get_active_item():
                item.set_net_state(0)

        if self.selected_item:
            self.selected_item.set_net_state(1)
        else:
            index = self.get_actives(self.ap_list)
            if index and self.tree.visible_items:
                for i in index:
                    self.tree.visible_items[i].set_net_state(1)

    def wireless_activate_failed(self, widget, new_state, old_state, reason):
        if reason == 7:
            self.pwd_failed = True

    def toggle_dialog(self, connection, security=None):
        ssid = connection.get_setting("802-11-wireless").ssid
        if ssid != None:
            AskPasswordDialog(connection,
                              ssid,
                              key_mgmt=security,
                              cancel_callback=self.cancel_ask_pwd,
                              confirm_callback=self.pwd_changed).show_all()

    def cancel_ask_pwd(self):
        pass

    def pwd_changed(self, pwd, connection):
        item = self._get_active_item()
        print item
        index = self.get_actives(self.ap_list)
        print index,"sdf"
        if item:
            map(lambda i: i.pwd_changed(pwd, connection), item)
        else:
            print "no active items found"
    ######

class WirelessSection(Section, WirelessDevice):

    def __init__(self):
        Section.__init__(self)
        WirelessDevice.__init__(self)
        self.wireless_devices = net_manager.device_manager.get_wireless_devices()

        self.selected_item = None

        self.init_state()
        self.init_signals()

    @classmethod
    def show_or_hide(self):
        if net_manager.device_manager.get_wireless_devices():
            return True
        else:
            return False

    def init_state(self):
        if self.wireless_devices:
            self.wireless = Contain(app_theme.get_pixbuf("network/wifi.png"), _("Wireless"), lambda w:w)
            #self.tree = TreeView([], enable_multiple_select=False)
            #self.tree.set_expand_column(1)
            #self.hotspot = HotSpot(None)
            self.vbox = gtk.VBox(False)
            self.label =  Label(_("Creat Hidden network"), 
                              LABEL_COLOR,
                              underline=True,
                              enable_select=False,
                              enable_double_click=False)

            self.label.connect("button-release-event", self.create_a_hidden_network)
            self.space = gtk.VBox()
            self.space.set_size_request(-1, 15)
            self.load(self.wireless, [self.label])
            self.tree.connect("single-click-item", self.set_selected_item)
            ## check state
            if self.get_state(self.wireless_devices):
                self.wireless.set_active(True)
        else:
            pass

    def init_signals(self):
        self._init_signals()
        Dispatcher.connect("ap-added", self.ap_added_callback)
        Dispatcher.connect("ap-removed", self.ap_removed_callback)
        Dispatcher.connect("wireless-redraw", self.wireless_redraw)

    def wireless_redraw(self, widget):
        print "wireless redraw"
        if self.wireless.get_active():
            self.wireless.set_active(True, emit=True)

    def create_a_hidden_network(self, widget, c):
        from wlan_config import HiddenSetting
        Dispatcher.to_setting_page(HiddenSetting(None))

    def ap_added_callback(self, widget):
        print "ap added"
        if self.wireless.get_active():
            self.wireless.set_active(True, emit=True)

    def ap_removed_callback(self, widget):
        print "ap removed"
        if self.wireless.get_active():
            self.wireless.set_active(True, emit=True)

    def set_selected_item(self, widget, item, column, x, y):
        self.selected_item = item

    #def toggle_on(self):
        #self.tree.delete_all_items()
        #self.td = ToggleThread(self.get_list, self.tree, self.after)
        #self.td.start()
        #item_list = self.get_list()
        #if self.ap_list:
            #self.tree.add_items(item_list)
        #self.tree.visible_items[-1].is_last = True

    def get_actives(self, ap_list):
        if not ap_list:
            return []
        index = []
        for wireless_device in self.wireless_devices:
            active_connection = wireless_device.get_active_connection()
            if active_connection:
                #if active_connection.get_state() != 2:
                    #return []
                try:
                    conn = active_connection.get_connection()
                    #print map(lambda a: a.object_path, ap_list)
                    index.append([ap.object_path for ap in ap_list].index(active_connection.get_specific_object()))
                except ValueError:
                    print "not found in ap list"
        return index

    def _get_active_item(self):
        return filter(lambda i: i.get_net_state() > 0, self.tree.visible_items)

    def toggle_on_after(self):
        #pass
        ###while self.td.isAlive():
            ###continue
    #def after(self):
        self.wireless.set_sensitive(True)
        indexs = self.get_actives(self.ap_list)
        if indexs:
            map(lambda i: self.tree.visible_items[i].set_net_state(2), indexs)
        else:
            for d in self.wireless_devices:
                wifi = nm_module.cache.get_spec_object(d.object_path)
                print "auto connect"
                wifi.auto_connect()

    def toggle_off(self):
        self.ap_list = []
        #self.td.stop_run()
        self.selected_item = None
        for wireless_device in self.wireless_devices:
            wireless_device.nm_device_disconnect()
            #wifi = nm_module.cache.get_spec_object(wireless_device.object_path)
            #wifi.device_wifi_disconnect()
            #self.device_stop(wireless_device)
        #self.toggle_lock = True
        self.wireless.set_sensitive(False)

    def get_list(self):
        self.ap_list = list()
        for wireless_device in self.wireless_devices:
            device_wifi = nm_module.cache.get_spec_object(wireless_device.object_path)
            self.ap_list += device_wifi.order_ap_list()
        aps = map(lambda i:WirelessItem(i), self.ap_list)
        

        hidden_list = self.get_hidden_connection(self.ap_list)
        #hidden_list = []
        hiddens = map(lambda c: HidenItem(c), hidden_list)

        return aps + hiddens
        #return self.ap_list

    def get_hidden_connection(self, ap_list):
        from shared_methods import net_manager


        #ssids = map(lambda a: a.get_ssid(), ap_list)
        #hiddens = filter(lambda c: c.get_setting("802-11-wireless").ssid not in ssids, 
                         #nm_module.nm_remote_settings.get_wireless_connections())
        return net_manager.get_hiddens()

        ## need to filter all aps
    def get_state(self, devices):
        for d in devices:
            if d.get_state() == 100:
                return True
        return False
    
    def device_stop(self, device):
        device.nm_device_disconnect()
        #wifi = cache.get_spec_object(device.object_path)
        #wifi.nm_device_disconnect()
    
class HotSpot(gtk.VBox):

    def __init__(self, send_to_crumb_cb):
        gtk.VBox.__init__(self, 0)
        cont = Contain(app_theme.get_pixbuf("network/wifi.png"), _("Hotspot"), self.toggle_cb)
        self.pack_start(cont, False, False)
        self.settings = None
        self.send_to_crumb_cb = send_to_crumb_cb
        self.align = gtk.Alignment(0, 0, 1, 1)
        self.align.set_padding(0, 0, PADDING, 22)
        self.hotspot_box = HotspotBox(self.active_connection)
        self.align.add(self.hotspot_box)
        self.active_this_adhoc = False

        if self.is_adhoc_active():
            cont.set_active(True)
            self.hotspot_box.set_net_state(2)
            self.active_this_adhoc = True
        self.__init_state()

    def set_net_state(self, state):
        self.hotspot_box.set_net_state(state)

    def get_net_state(self):
        self.hotspot_box.get_net_state()

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            self.add(self.align)
            self.show_all()

            # Handle data
            self.fill_entries()
            if self.hotspot_box.get_net_state() == 2:
                self.hotspot_box.set_active(False)
            else:
                self.hotspot_box.set_active(True)
        else:
            from nmlib.nm_remote_connection import NMRemoteConnection
            if isinstance(self.connection, NMRemoteConnection):
                self.connection.delete()
            self.hotspot_box.set_net_state(0)
            self.hotspot_box.set_active(False)
            self.remove(self.align)

    def fill_entries(self):
        self.connection = self.get_adhoc_connection()
        security_setting = self.connection.get_setting("802-11-wireless-security")
        security_setting.wep_key_type = 2
        if self.connection:
            (ssid, pwd) = self.get_settings(self.connection)
            self.hotspot_box.set_ssid(ssid)
            self.hotspot_box.set_pwd(pwd)

    def get_settings(self, connection):
        ssid = connection.get_setting("802-11-wireless").ssid
        pwd = self.__get_pwd(connection)
        return (ssid, pwd)

    def __get_pwd(self, connection):
        try:
            (setting_name, method) = connection.guess_secret_info() 
            secret = nm_module.secret_agent.agent_get_secrets(connection.object_path,
                                                    setting_name,
                                                    method)
        except:
            secret = ""

        return secret
            

    def get_adhoc_connection(self):
        connections = filter(lambda c: c.get_setting("802-11-wireless").mode == "adhoc",
                             nm_module.nm_remote_settings.get_wireless_connections())
        if connections:
            print "adhoc connection:",connections[0].get_setting("802-11-wireless").ssid
            return connections[0]
        else:
           return nm_module.nm_remote_settings.new_adhoc_connection("")

    def is_adhoc_active(self):
        # TODO just for one device
        wireless_device = net_manager.device_manager.get_wireless_devices()[0]
        active = wireless_device.get_active_connection()
        if active:
            if active.get_connection().get_setting("802-11-wireless").mode == "adhoc":
                return True
            else:
                return False
        else:
            return False
    def is_valid(self):
        security_setting = self.connection.get_setting("802-11-wireless-security")
        #active = security_setting.wep_tx_keyidx 
        return security_setting.verify_wep_key(self.hotspot_box.get_pwd(), 2)
        
    def active_connection(self):
        ssid = self.hotspot_box.get_ssid()
        pwd = self.hotspot_box.get_pwd()
        if self.is_valid():
            from nmlib.nm_remote_connection import NMRemoteConnection
            self.connection.get_setting("802-11-wireless").ssid = ssid
            self.connection.get_setting("802-11-wireless-security").set_wep_key(0, pwd)
            
            if not isinstance(self.connection, NMRemoteConnection):
                self.connection = nm_module.nm_remote_settings.new_connection_finish(self.connection.settings_dict, 'lan')

            if isinstance(self.connection, NMRemoteConnection):
                self.connection.update()
                wireless_device = net_manager.device_manager.get_wireless_devices()[0]
                self.active_this_adhoc = True
                wireless_device.nm_device_disconnect()

                nm_module.nmclient.activate_connection_async(self.connection.object_path,
                                               wireless_device.object_path,
                                               "/")
            return True
        else:
            print "pwd not valid"
            return False

        

    def slide_to_event(self, widget, event):
        self.settings.init("",init_connections=True, all_adhoc=True)
        self.send_to_crumb_cb()
        slider.slide_to_page(self.settings, "right")

    def __init_state(self):
        pass

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.child.allocation
        width, height = get_content_size(self.label_name)
        cr.set_source_rgb(*color_hex_to_cairo(ui_theme.get_color("link_text").get_color()))
        draw_line(cr, rect.x, rect.y + rect.height, rect.x + width, rect.y + rect.height)

class DSLSection(Section):
    def __init__(self):
        Section.__init__(self)
        self.wired_devices = net_manager.device_manager.get_wired_devices()
        if self.wired_devices:

            self.dsl = Contain(app_theme.get_pixbuf("network/dsl.png"), _("DSL"), lambda w: w)
            #self.tree = TreeView([])
            #self.tree.set_expand_column(1)
            self.label =  Label(_("Create DSL Setting"), 
                              LABEL_COLOR,
                              underline=True,
                              enable_select=False,
                              enable_double_click=False)
            
            self.load(self.dsl, [self.label])

            self.__init_signals()
        else:
            pass

    @classmethod
    def show_or_hide(self):
        if net_manager.device_manager.get_wired_devices():
            return True
        else:
            return False

    def __init_signals(self):
        self.label.connect("button-release-event", lambda w,x: self.jumpto_setting())
        Dispatcher.connect("dsl-redraw", self.dsl_redraw)

    def dsl_redraw(self, widget):
        if self.dsl.get_active():
            self.dsl.set_active(True, emit=True)

    def toggle_on(self):
        self.tree.delete_all_items()
        item_list = self.get_list()
        if item_list:
            item_list[-1].is_last = True
            self.tree.add_items(item_list)

    def toggle_on_after(self):
        pass
    
    def toggle_off(self):
        pass

    def get_list(self):
        self.connections =  nm_module.nm_remote_settings.get_pppoe_connections()
        return map(lambda c: DSLItem(c, None), self.connections)

    def jumpto_setting(self):
        Dispatcher.to_setting_page(DSLSetting())
        setting = nm_module.slider.get_page_by_name("setting")
        setting.create_new_connection()

class VpnSection(Section):
    def __init__(self):
        Section.__init__(self)

        #init
        self.vpn = Contain(app_theme.get_pixbuf("network/vpn.png"), _("VPN Network"), lambda w:w)
        #self.tree = TreeView([])
        #self.tree.set_expand_column(1)
        self.label = Label(_("Create VPN Setting"), 
                           LABEL_COLOR,
                           underline=True,
                           enable_select=False,
                           enable_double_click=False)

        self.load(self.vpn, [self.label])
        self.init_state()
        
        self.__init_signals()

    def init_state(self):
        vpn_active = nm_module.nmclient.get_vpn_active_connection()
        if vpn_active:
            self.vpn.set_active(True)

    @classmethod
    def show_or_hide(self):
        return True

    def __init_signals(self):
        self.label.connect("button-release-event", lambda w,p: self.jumpto_cb())
        Dispatcher.connect("vpn-redraw", self.vpn_redraw)

    def vpn_redraw(self, widget):
        print "vpn-redraw"
        if self.vpn.get_active():
            self.vpn.set_active(True, emit=True)
            self.show_all()


    def connect_vpn_signals(self, active_vpn, connection_name):
        active_vpn.connect("vpn-connected", self.vpn_connected, connection_name)
        active_vpn.connect("vpn-connecting", self.vpn_connecting, connection_name)
        active_vpn.connect("vpn-disconnected", self.vpn_disconnected)

    def toggle_on(self):
        item_list = self.get_list()
        #item_list=[]
        if item_list:
            item_list[-1].is_last = True
            self.tree.delete_all_items()
            self.tree.add_items(item_list)

    def toggle_on_after(self):
        vpn_active = nm_module.nmclient.get_vpn_active_connection()
        if vpn_active:
            # TODO fix for mutiple
            connection = vpn_active[0].get_connection()

            try:
                index = self.connection.index(connection)
                self.tree.visible_items[index].set_net_state(2)
                return
            except Exception, e:
                print e
        else:
            pass

    def toggle_off(self):
        vpn_active = nm_module.nmclient.get_vpn_active_connection()
        if vpn_active:
            nm_module.nmclient.deactive_connection_async(vpn_active[0].object_path)
    
    def get_list(self):
        self.connection = nm_module.nm_remote_settings.get_vpn_connections()
        return map(lambda c: VPNItem(c, None), self.connection)
    
    def jumpto_cb(self):
        Dispatcher.to_setting_page(VPNSetting())
        setting = nm_module.slider.get_page_by_name("setting")
        setting.create_new_connection()
        

class MobileDevice(object):

    def __init__(self):
        pass

    def _init_signals(self):
        net_manager.device_manager.load_mm_listener(self)

    def mm_device_active(self, widget, new_state, old_state, reason):
        item = self.get_item(widget)
        if item:
            item.set_net_state(2)

    def mm_device_deactive(self, widget, new_state, old_state, reason):
        item = self.get_item(widget)
        if item:
            item.set_net_state(0)
        #index = self.wired_devices.index(widget)
        #if not reason == 0:
            #if self.tree.visible_items != []:
                #self.tree.visible_items[index].set_net_state(0)
                #self.tree.queue_draw()

    def mm_device_unavailable(self,  widget, new_state, old_state, reason):
        pass

    def mm_activate_start(self, widget, new_state, old_state, reason):
        item = self.get_item(widget)
        if item:
            item.set_net_state(1)

    def mm_activate_failed(self, widget, new_state, old_state, reason):
        item = self.get_item(widget)
        if item:
            item.set_net_state(0)

class MobileSection(Section, MobileDevice):

    def __init__(self):
        Section.__init__(self)
        MobileDevice.__init__(self)
        # init values
        self.mobile = Contain(app_theme.get_pixbuf("network/3g.png"), _("Mobile Network"), lambda w:w)
        self.label = Label(_("Mobile Configuration"),
                      LABEL_COLOR,
                      underline=True,
                      enable_select=False,
                      enable_double_click=False)

        self.load(self.mobile, [])
        self.init_signal()

    def init_signal(self):
        self._init_signals()

    def get_item(self, device):
        modem_path =device.get_udi()
        try:
            index = self.devices.index(modem_path)
            return self.tree.visible_items[index]
        except:
            print "get device index error"
            return None
        

    @classmethod
    def show_or_hide(self):
        if nm_module.mmclient.get_cdma_device() or nm_module.mmclient.get_gsm_device():
            return True
        else:
            return False

    def __init_signals(self):
        #nm_module.mmclient.connect("device-added", lambda w,p: mobile.set_active(True))
        Dispatcher.connect("mmdevice-added", self.device_added)
        self.label.connect("button-release-event", lambda w,p: self.jumpto_cb())

    def device_added(self, widget, device):
        self.init_signal()
        if self.mobile.get_active():
            self.mobile.set_active(True)


    def toggle_on(self):
        item_list = self.get_list()
        if item_list:
            item_list[-1].is_last = True

            self.tree.delete_all_items()
            self.tree.add_items(item_list)

    def toggle_on_after(self):
        pass

    def toggle_off(self):
        pass

    def get_list(self):
        self.cdma = nm_module.mmclient.get_cdma_device()
        self.gsm = nm_module.mmclient.get_gsm_device()

        #self.cdma = nm_module.nm_remote_settings.get_cdma_connections()
        #self.gsm = nm_module.nm_remote_settings.get_gsm_connections()
        
        self.devices = self.cdma + self.gsm
        return map(lambda c: MobileItem(c, None), self.devices)
    
    def jumpto_cb(self):
        Dispatcher.to_setting_page(MobileSetting())


class Mobile(gtk.VBox):
    def __init__(self,
                 send_to_crumb_cb):
        gtk.VBox.__init__(self)
        self.send_to_crumb_cb = send_to_crumb_cb
        mobile = Contain(app_theme.get_pixbuf("network/3g.png"), _("Mobile Network"), self.toggle_cb)
        self.add(mobile)
        self.settings = None
        nm_module.mmclient.connect("device-added", lambda w,p: mobile.set_active(True))

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            self.align = gtk.Alignment(0,0,0,0)
            self.align.set_padding(0,0,PADDING,11 + 11)
            self.add(self.align)
        # Check if there's any mobile device
            mobile_device = nm_module.mmclient.get_cdma_device()
            if mobile_device:
                self.show_device(mobile_device[0])
            else:
                self.show_link()
            self.show_all()
        else:
            self.align.destroy()

    def show_link(self):
        container_remove_all(self.align)
        label = Label(_("Mobile Configuration"),
                      LABEL_COLOR,
                      underline=True,
                      enable_select=False,
                      enable_double_click=False)
        label.connect("button-release-event", self.slide_to_event)
        self.align.add(label)

    def show_device(self, device_path):
        from mm.mmdevice import MMDevice
        container_remove_all(self.align)
        device = MMDevice(device_path)
        manufacturer = device.get_manufacturer()
        model = device.get_model()
        info = model + " " + manufacturer
        item = InfoItem(info, self.jumpto_cb,is_last=True)
        #item = GeneralItem(info,
                           #None,
                           #self.settings,
                           #lambda :slider.slide_to_page(self.settings, "right"),
                           #self.send_to_crumb_cb)
        self.tree = TreeView([item])
        self.tree.set_size_request(758, len(self.tree.visible_items) * self.tree.visible_items[0].get_height())
        self.tree.show_all()
        self.align.add(self.tree)

    def jumpto_cb(self):
        Dispatcher.to_setting_page(MobileSetting(None))

    def device_is_active(self, widget, a):
        print a, "active"

    def device_is_deactive(self, widget, a):
        '''docstring for device_is_deactive'''
        print a, "deactive"

    def slide_to_event(self, widget, event):
        Dispatcher.to_setting_page(MobileSetting(None))

    def add_setting_page(self, setting_page):
        self.settings = setting_page

class Proxy(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.proxy = Contain(app_theme.get_pixbuf("network/proxy.png"), _("Proxy"), self.toggle_cb)
        self.proxysetting = ProxySettings()
        self.settings = None
        self.add(self.proxy)
        self.init_state()

    def init_state(self):
        if self.proxysetting.get_proxy_mode() != "none":
            self.proxy.set_active(True)

    @classmethod
    def show_or_hide(self):
        return True

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            self.align = gtk.Alignment(0,0,0,0)
            self.align.set_padding(0,0,PADDING,11)
            label = Label(_("Proxy Configuration"),
                          LABEL_COLOR,
                          underline=True,
                          enable_select=False,
                          enable_double_click=False)
            label.connect("button-release-event", self.slide_to_event)

            self.align.add(label)
            self.add(self.align)
            self.show_all()
        else:
            self.align.destroy()
            self.proxysetting.set_proxy_mode("none")

    def slide_to_event(self, widget, event):
        self.settings = ProxyConfig()
        self.settings.init(True)
        slider.slide_to_page(self.settings, "right")
        Dispatcher.send_submodule_crumb(2, _("Proxy"))

    #def add_setting_page(self, setting_page):
        #self.settings = setting_page

    def section_show(self):
        self.set_no_show_all(False)
        self.show_all()

    def section_hide(self):
        self.set_no_show_all(True)
        self.hide()

class Network(object):
    def __init__(self):        
        self.init_sections()
        self.__init_ui()

        slider._append_page(self.eventbox, "main")
        from setting_page_ui import SettingUI
        self.setting_page_ui = SettingUI(None, None)
        slider._append_page(self.setting_page_ui, "setting")
        
        slider._append_page(Region(), "region")
        slider.show_all()
        slider._set_to_page("main")
        Dispatcher.connect("to-setting-page", self.slide_to_setting_page)
        Dispatcher.connect("recheck-section", lambda w, i: self.__init_sections(0))
        Dispatcher.connect("service-stop-add-more", lambda w: self.stop())

        self.sections = []
    
    def __init_sections(self, index):
        section_list = [WiredSection, WirelessSection, DSLSection, MobileSection, VpnSection, Proxy]
        self.sections = map(lambda s: s.show_or_hide(), section_list)
        if index == -1:
            container_remove_all(self.vbox)
            for section in section_list:
                section_ins = apply(section)
                self.vbox.pack_start(section_ins, False, True)
                if section.show_or_hide():
                    section_ins.section_show()
                else:
                    section_ins.section_hide()
        else:
            for section in self.vbox.get_children():
                if section.show_or_hide():
                    section.section_show()
                else:
                    section.section_hide()

    def __init_ui(self):

        self.vbox = gtk.VBox(False, BETWEEN_SPACING)
        self.__init_sections( -1)
        self.vbox.set_size_request(WINDOW_WIDTH - 2 * TEXT_WINDOW_LEFT_PADDING, -1)
        
        scroll_win = ScrolledWindow(right_space=0, top_bottom_space=0)
        scroll_win.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        # FIXME UI a align to adjust ui
        ui_align = gtk.Alignment(0, 0, 0, 0)
        ui_align.set_padding(TEXT_WINDOW_TOP_PADDING,
                                    TEXT_WINDOW_TOP_PADDING,
                                    TEXT_WINDOW_LEFT_PADDING,
                                    TEXT_WINDOW_LEFT_PADDING)

        ui_align.add(self.vbox)
        scroll_win.add_with_viewport(ui_align)

        self.eventbox = gtk.EventBox()
        self.eventbox.set_above_child(False)
        self.eventbox.add(scroll_win)
        self.vbox.connect("expose-event", self.expose_callback)
        ui_align.connect("expose-event", self.expose_callback)
    
    def __pack_start(self, parent, child_list, expand=False, fill=False):
        for child in child_list:
            parent.pack_start(child, expand, fill)

    def expose_callback(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb( 1, 1, 1) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

    #def slide_to_setting_page(self, widget, setting_module):
        #self.setting_page_ui.load_module(setting_module)

    #def activate_succeed(self, widget, connection_path):
        #print "active_succeed with", connection_path
        #print connection_path

    #def activate_failed(self, widget, connection_path):
        #print "active failed"

    #def device_added(self, widget, connection_path):
        #print "device add:", connection_path
        #self.wired.refresh_device()

    #def device_removed(self, widget, connection_path):
        #print "device remove:", connection_path
        #self.wired.refresh_device()

    #def init_sections(self):
        ##slider._set_to_page("main")
        #self.wired = WiredSection()
        #self.wireless = WirelessSection()
        #self.dsl = DSLSection()
        #self.proxy = Proxy()
        #self.mobile = MobileSection()
        #self.vpn = VpnSection()

    def refresh(self):
        #self.init_sections()
        self.__init_sections(-1)
        self.eventbox.set_above_child(False)
        self.eventbox.queue_draw()

    def stop(self):
        self.eventbox.set_above_child(True)
        
    def get_main_page(self):
        return self.eventbox

