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
from proxy_config import ProxyConfig
import sys
import os
from dss import app_theme
from dtk.ui.theme import ui_theme
from dtk.ui.new_treeview import TreeView
from dtk.ui.draw import  draw_line
from dtk.ui.utils import color_hex_to_cairo, container_remove_all, get_content_size
from deepin_utils.file import  get_parent_dir
from deepin_utils.ipc import is_dbus_name_exists
from dtk.ui.label import Label
from dtk.ui.scrolled_window import ScrolledWindow
import gtk

from container import Contain
from lists import WiredItem, WirelessItem, GeneralItem, HidenItem

from lan_config import WiredSetting
from wlan_config import WirelessSetting
from dsl_config import DSLSetting
from vpn_config import VPNSetting
from mobile_config import MobileSetting
from regions import Region
from settings_widget import HotspotBox

from nmlib.nmcache import cache
from nm_modules import nm_module

PADDING = 32
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from module_frame import ModuleFrame 
from nmlib.servicemanager import servicemanager

from nls import _
from constants import *

slider = nm_module.slider

def pack_start(parent, child_list, expand=False, fill=False):
    for child in child_list:
        parent.pack_start(child, expand, fill)

class WiredDevice(object):
    def __init__(self, device, treeview, index):
        self.wired_device = device
        self.tree = treeview
        self.index = index
        device_ethernet = cache.get_spec_object(self.wired_device.object_path)
        self.wired_device.connect("device-active", self.device_activate)
        self.wired_device.connect("device-deactive", self.device_deactive)
        device_ethernet.connect("try-activate-begin", self.try_activate_begin)

    def device_activate(self, widget ,reason):
        print "wired is active"
        if self.tree.visible_items != []:
            self.tree.visible_items[self.index].network_state = 2
            self.tree.queue_draw()

    def device_deactive(self, widget, reason):
        print "wired is deactive"
        if not reason == 0:
            if self.tree.visible_items != []:
                self.tree.visible_items[self.index].network_state = 0
                self.tree.queue_draw()

    def try_activate_begin(self, widget):
        if self.tree.visible_items != []:
            self.tree.visible_items[self.index].set_net_state(1)
            self.tree.queue_draw()

class WiredSection(gtk.VBox):
    def __init__(self, send_to_crumb_cb):
        gtk.VBox.__init__(self)

        self.wired_devices = nm_module.nmclient.get_wired_devices()
        if self.wired_devices:
            self.wire = Contain(app_theme.get_pixbuf("network/cable.png"), _("Wired"), self.toggle_cb)
            self.send_to_crumb_cb = send_to_crumb_cb
            self.pack_start(self.wire, False, False, 0)
            self.settings = None
            self.tree = TreeView([])
            self.tree.set_no_show_all(True)
            self.tree.hide()
            self.align = gtk.Alignment()
            self.align.show()
            self.align.set(0,0,1,1)
            self.align.set_padding(0,0,PADDING,11*2)
            self.align.add(self.tree)
            self.pack_start(self.align, False, False, 0)

    def refresh_device(self):
        if self.wire.get_active():
            self.wired_devices = nm_module.nmclient.get_wired_devices()
            item_list = self.retrieve_list()
            self.tree.add_items(item_list, 0, True)
            self.tree.visible_items[-1].is_last = True
            self.tree.set_no_show_all(False)
            self.tree.set_size_request(-1,len(self.tree.visible_items) * self.tree.visible_items[0].get_height())
            for index, wired_device in enumerate(self.wired_devices):
                WiredDevice(wired_device,self.tree, index)

            #self.try_active()
            self.show_all()

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            item_list = self.retrieve_list()
            self.tree.add_items(item_list, 0, True)
            self.tree.visible_items[-1].is_last = True
            self.tree.set_no_show_all(False)
            self.tree.set_size_request(-1,len(self.tree.visible_items) * self.tree.visible_items[0].get_height())
            for index, wired_device in enumerate(self.wired_devices):
                WiredDevice(wired_device,self.tree, index)

            self.try_active()
            self.show_all()
        else:
            print "toggle deactive"
            self.tree.delete_all_items()
            self.tree.set_no_show_all(True)
            self.tree.hide()
            for wired_device in self.wired_devices:
                wired_device.nm_device_disconnect()

    def retrieve_list(self):
        """
        retrieve network lists, will use thread
        """
        wired_items = []
        for wired_device in self.wired_devices:
            wired_items.append(WiredItem(wired_device,
                                         self.settings, 
                                         lambda : slider.slide_to_page(self.settings, "right"),
                                         self.send_to_crumb_cb))
        return wired_items


    def try_active(self):
        for index, device in enumerate(self.wired_devices):
            if int(device.get_state()) == 20:
                self.tree.visible_items[index].network_state = 0
                return
            else:
                if not device.is_active():
                    device_ethernet = cache.get_spec_object(device.object_path)
                    device_ethernet.auto_connect()
                    device_ethernet.emit("try-activate-begin")
                else:
                    self.tree.visible_items[index].network_state = 2

    def add_setting_page(self, setting_page):
        self.settings = setting_page
        if self.wired_devices:
            for device in self.wired_devices:
                if device.is_active():
                    self.wire.set_active(True)
                    return
                else:
                    self.wire.set_active(False)

class WirelessDevice(object):
    def __init__(self, device, treeview, ap_list, refresh_list, hotspot):
        self.wireless_device = device
        self.ap_list = ap_list
        self.tree = treeview
        self.refresh_list = refresh_list
        self.hotspot = hotspot
        self.device_wifi = cache.get_spec_object(self.wireless_device.object_path)
        self.wireless_device.connect("device-active", self.device_is_active)
        self.wireless_device.connect("device-deactive", self.device_is_deactive)
        self.device_wifi.connect("try-ssid-begin", self.try_to_connect)
        self.device_wifi.connect("access-point-added", self.ap_added)

        #self.device_wifi.connect_after("try-ssid-end", self.try_ssid_end)

    def try_to_connect(self, widget, ssid):
        print "try_to_connect"
        ap_list  = [ap.get_ssid() for ap in self.ap_list]
        try:
            index = ap_list.index(ssid)
            self.tree.visible_items[index].set_net_state(1)
        except:
            self.hotspot.set_net_state(1)
    
    def device_is_active(self, widget, reason):
        print "wireless active"
        active = self.wireless_device.get_active_connection()
        # FIXME little wierd
        for item in self.tree.visible_items:
            item.set_net_state(0)
 
        try:
            index = [ap.object_path for ap in self.ap_list].index(active.get_specific_object())
            self.index = index
            self.tree.visible_items[index].set_net_state(2)
            self.tree.visible_items[index].redraw()
        except ValueError:
            if self.check_connection_mode(active.get_connection()):
                self.hotspot.set_net_state(2)

    def ap_added(self, ap_object):
        print "ad_added"

    def check_connection_mode(self, connection):
        mode = connection.get_setting("802-11-wireless").mode
        print mode
        if mode == "adhoc":
            return True
        else:
            return False

    def device_is_deactive(self, widget, reason):
        print "wireless deactive"
        if not reason == 0:
            try:
                if self.tree.visible_items != []:
                    self.tree.visible_items[self.index].set_net_state(0)
                    self.tree.visible_items[self.index].redraw()
            except:
                if self.hotspot.get_net_state() == 1:
                    self.hotspot.set_net_state(0)


class WirelessSection(gtk.VBox):
    def __init__(self, send_to_crumb_cb):
        gtk.VBox.__init__(self)
        self.wireless_devices = nm_module.nmclient.get_wireless_devices()
        if not nm_module.nmclient.wireless_get_enabled():
            nm_module.nmclient.wireless_set_enabled(True)
        if self.wireless_devices:
            # FIXME will support multi devices
            self.wireless = Contain(app_theme.get_pixbuf("network/wifi.png"), _("Wireless"), self.toggle_cb)
            self.send_to_crumb_cb = send_to_crumb_cb

            self.pack_start(self.wireless, False, False)
            self.tree = TreeView([], enable_multiple_select=False)
            self.settings = None
            self.hotspot = HotSpot(send_to_crumb_cb)
            self.vbox = gtk.VBox(False, spacing=15)
            self.vbox.set_no_show_all(True)
            self.vbox.hide()
            self.align = gtk.Alignment()
            self.align.show()
            self.align.set(0,0,1,1)
            self.align.set_padding(0,0,PADDING,11 + 11)
            self.align.add(self.tree)
            self.vbox.pack_start(self.align, False, False)
            self.vbox.pack_start(self.hotspot, False, False)


            self.pack_start(self.vbox, False, False, 0)
            #self.pack_start(self.hotspot, False, False, 0)

            # Add signals
            for device in self.wireless_devices:
                device.connect("state-changed", self.state_changed_callback)

    def state_changed_callback(self, widget, new_state, old_state, reason):
        if new_state == 20:
            print "device is not available"
            self.wireless.set_active(False)
        
    def ap_added(self):
        self.show_ap_list()
    
    def add_setting_page(self, page):
        self.settings = page
        if self.wireless_devices:
            self.hotspot.add_setting_page(page)
            for wireless_device in self.wireless_devices:
                if wireless_device.is_active():
                    self.wireless.set_active(True)
                else:
                    self.wireless.set_active(False)
    
    def show_ap_list(self):
        item_list = self.retrieve_list()
        if item_list:
            self.tree.add_items(item_list,0,True)
            self.tree.visible_items[-1].is_last = True
            self.vbox.set_no_show_all(False)
            self.tree.set_size_request(-1,len(self.tree.visible_items) * self.tree.visible_items[0].get_height())
        else:
            self.tree.delete_all_items()
        self.queue_draw()
        self.show_all()

        for wireless_device in self.wireless_devices:
            WirelessDevice(wireless_device, self.tree, self.ap_list,self.show_ap_list, self.hotspot)

        index = self.get_actives(self.ap_list)
        if index:
            if index == [-1]:
                pass
            elif index[0] == -2:
                # add hiden network
                self.tree.add_items([HidenItem(index[1],
                                     self.settings,
                                     lambda :slider.slide_to_page(self.settings, "right"),
                                     self.send_to_crumb_cb,
                                     check_state=2)
                                     ])
            else:
                for i in index:
                    self.tree.visible_items[i].network_state = 2
        else:
            for wireless_device in self.wireless_devices:
                device_wifi = cache.get_spec_object(wireless_device.object_path)
                device_wifi.auto_connect()
        self.index = index

    def toggle_cb(self, widget):
        active = widget.get_active()
        print "toggled", active
    
        if active: 
            self.show_ap_list()
        else:
            self.tree.delete_all_items()
            self.vbox.set_no_show_all(True)
            self.vbox.hide()
            for wireless_device in self.wireless_devices:
                wireless_device.nm_device_disconnect()

    def retrieve_list(self):
        """
        retrieve network lists, will use thread
        """
        self.ap_list = []
        for wireless_device in self.wireless_devices:
            device_wifi = cache.get_spec_object(wireless_device.object_path)
            self.ap_list += device_wifi.order_ap_list()

        items = [WirelessItem(i,
                              self.settings,
                              lambda : slider.slide_to_page(self.settings, "right"),
                              self.send_to_crumb_cb) for i in self.ap_list]
        # Comment for modify
        #items.append(GeneralItem(_("connect to hidden network"),
                                 #self.ap_list,
                                 #self.settings,
                                 #lambda :slider.slide_to_page(self.settings, "right"),
                                 #self.send_to_crumb_cb,
                                 #check_state=0))
        return items

    def get_hiden_list(self):
        ssid_list = []
        if self.ap_list:
            for wireless_device in self.wireless_devices:
                for con in wireless_device.get_wireless_connections():

                    pass

    def get_actives(self, ap_list):
        index = []
        for wireless_device in self.wireless_devices:
            active_connection = wireless_device.get_active_connection()
            if active_connection:
                try:
                    index.append([ap.object_path for ap in ap_list].index(active_connection.get_specific_object()))
                except ValueError:
                    if check_connection_mode(active_connection.get_connection()):
                        return [-1]
                    else:
                        return [-2, active_connection.get_connection()]
        return index

    def check_connection_mode(self, connection):
        mode = connection.get_setting("802-11-wireless").mode
        if mode == "adhoc":
            return True
        else:
            return False
                
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

        if self.is_adhoc_active():
            cont.set_active(True)
            self.hotspot_box.set_net_state(2)


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
            return connections[0]
        else:
           return nm_module.nm_remote_settings.new_adhoc_connection("")

    def is_adhoc_active(self):
        # TODO just for one device
        wireless_device = nm_module.nmclient.get_wireless_devices()[0]
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
        active = security_setting.wep_tx_keyidx 
        return security_setting.verify_wep_key(self.hotspot_box.get_ssid(), 2)
        
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
                wireless_device = nm_module.nmclient.get_wireless_devices()[0]
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

    def add_setting_page(self, setting_page):
        self.settings = setting_page

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.child.allocation
        width, height = get_content_size(self.label_name)
        cr.set_source_rgb(*color_hex_to_cairo(ui_theme.get_color("link_text").get_color()))
        draw_line(cr, rect.x, rect.y + rect.height, rect.x + width, rect.y + rect.height)

class DSL(gtk.VBox):
    def __init__(self, slide_to_setting_cb):
        gtk.VBox.__init__(self)
        self.slide_to_setting = slide_to_setting_cb
        self.setting_page = None
        self.dsl = Contain(app_theme.get_pixbuf("network/dsl.png"), _("DSL"), self.toggle_cb)
        self.pack_start(self.dsl, False, False)

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            self.align = gtk.Alignment(0,0,0,0)
            self.align.set_padding(0,0,PADDING,11)
            label = Label(_("DSL Configuration"), 
                          ui_theme.get_color("link_text"),
                          underline=True,
                          enable_select=False,
                          enable_double_click=False)
            label.connect("button-release-event", self.slide_to_event)

            self.align.add(label)
            self.add(self.align)
            self.show_all()
        else:
            self.align.destroy()

    def add_setting_page(self, setting_page):
        self.setting_page = setting_page

    def slide_to_event(self, widget, event):
        self.setting_page.init(init_connections=True)
        self.slide_to_setting()
        slider.slide_to_page(self.setting_page, "right")

class VpnSection(gtk.VBox):
    def __init__(self, slide_to_subcrumb_cb):
        gtk.VBox.__init__(self)
        self.slide_to_subcrumb = slide_to_subcrumb_cb
        self.vpn = Contain(app_theme.get_pixbuf("network/vpn.png"), _("VPN Network"), self.toggle_cb)
        self.connection_tree = TreeView([])
        self.label = Label(_("VPN Setting"), 
                           ui_theme.get_color("link_text"),
                           underline=True,
                           enable_select=False,
                           enable_double_click=False)
        self.label.connect("button-release-event", self.slide_to_event)

        self.vbox = gtk.VBox(False, spacing=15)
        self.align = gtk.Alignment()
        self.align.show()
        self.align.set(0,0,1,0)
        self.align.set_padding(0,0,PADDING,11 + 11)
        self.align.add(self.vbox)
        self.pack_start(self.vpn, False, False)
        self.pack_start(self.align, False, False)

        

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            vpn_active = nm_module.nmclient.get_vpn_active_connection()
            if vpn_active:
                connection = vpn_active[0].get_connection()
                connection_name = connection.get_setting("connection").id
                #self.vbox.pack_start(self.connection_tree, False, False)
                self.add_item(connection_name, state=2)
                #self.vbox.pack_end(self.label, False, False)
            else:
                self.vbox.pack_end(self.label, False, False)

            self.show_all()
        else:
            container_remove_all(self.vbox)
            vpn_active = nm_module.nmclient.get_vpn_active_connection()
            if vpn_active:
                nm_module.nmclient.deactive_connection_async(vpn_active[0].object_path)

    def add_item(self, connection_name , state):
        #self.vbox.remove(self.connection_tree) 
        container_remove_all(self.vbox)
        self.connection_tree.delete_all_items()
        self.item = GeneralItem(connection_name,
                            self.setting,
                            lambda :slider.slide_to_page(self.setting, "right"),
                            self.slide_to_subcrumb,
                            check_state=state)
        self.connection_tree.add_items([self.item]) 
        #self.connection_tree.set_size_request(, -1)
        self.vbox.pack_start(self.connection_tree, False, False)
        
    
    def connect_vpn_signals(self, active_vpn, connection_name):
        active_vpn.connect("vpn-connected", self.vpn_connected, connection_name)
        active_vpn.connect("vpn-connecting", self.vpn_connecting, connection_name)
        active_vpn.connect("vpn-disconnected", self.vpn_disconnected)

    #def vpn_state_changed(self, widget, state, reason):
        #print "changed",state

    def vpn_connected(self, widget, connection_name):
        print "vpn connected"
        self.item.set_net_state(2)
        #self.sidebar.set_active()

    def vpn_connecting(self, widget, connection_name):
        self.add_item(connection_name, state=1)
        self.item.set_net_state(1)

        #self.vbox.pack_start(self.connection_tree, False, False)
        print "vpn connecting"

    def vpn_disconnected(self, widget):
        print "vpn disconnected"
        container_remove_all(self.vbox)
        if self.vpn.switch.get_active():
            self.vbox.pack_start(self.label, False, False)
        cache.del_spec_object(widget.object_path)

    def slide_to_event(self, widget, event):
        self.setting.init(init_connections=True)
        self.slide_to_subcrumb()
        slider.slide_to_page(self.setting, "right")

    def add_setting_page(self, setting_page):
        self.setting = setting_page
        self.setting.state_change_cb = self.connect_vpn_signals
        vpn_active = nm_module.nmclient.get_vpn_active_connection()
        if vpn_active:
            self.vpn.switch.set_active(True)

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
                      ui_theme.get_color("link_text"),
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
        item = GeneralItem(info,
                           self.settings,
                           lambda :slider.slide_to_page(self.settings, "right"),
                           self.send_to_crumb_cb)
        self.tree = TreeView([item])
        self.tree.set_size_request(758, len(self.tree.visible_items) * self.tree.visible_items[0].get_height())
        self.tree.show_all()
        self.align.add(self.tree)

    def device_is_active(self, widget, a):
        print a, "active"

    def device_is_deactive(self, widget, a):
        '''docstring for device_is_deactive'''
        print a, "deactive"

    def slide_to_event(self, widget, event):
        self.settings.init(init_connections=True)
        self.send_to_crumb_cb()
        slider.slide_to_page(self.settings, "right")
    def add_setting_page(self, setting_page):
        self.settings = setting_page

class Proxy(gtk.VBox):
    def __init__(self, slide_to_setting_cb):
        gtk.VBox.__init__(self)
        self.slide_to_setting = slide_to_setting_cb
        proxy = Contain(app_theme.get_pixbuf("network/proxy.png"), _("Proxy"), self.toggle_cb)
        self.settings = None
        self.add(proxy)

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            self.align = gtk.Alignment(0,0,0,0)
            self.align.set_padding(0,0,PADDING,11)
            label = Label(_("Proxy Configuration"),
                          ui_theme.get_color("link_text"),
                          underline=True,
                          enable_select=False,
                          enable_double_click=False)
            label.connect("button-release-event", self.slide_to_event)

            self.align.add(label)
            self.add(self.align)
            self.show_all()
        else:
            self.align.destroy()

    def slide_to_event(self, widget, event):
        self.settings.init(True)
        self.slide_to_setting()
        slider.slide_to_page(self.settings, "right")

    def add_setting_page(self, setting_page):
        self.settings = setting_page


class Network(object):
    def __init__(self, module_frame):
        
        self.module_frame = module_frame
        self.init_sections(self.module_frame)
        vbox = gtk.VBox(False, BETWEEN_SPACING)
        if hasattr(self.wired, "wire"):
            vbox.pack_start(self.wired, False, True,0)
        if hasattr(self.wireless, "wireless"):
            vbox.pack_start(self.wireless, False, True, 0)
        vbox.pack_start(self.dsl, False, True, 0)
        vbox.pack_start(self.mobile, False, True, 0)
        vbox.pack_start(self.vpn, False, True, 0)
        vbox.pack_start(self.proxy, False, True, 0)
        vbox.set_size_request(WINDOW_WIDTH - 2 * TEXT_WINDOW_LEFT_PADDING, -1)
        
        scroll_win = ScrolledWindow(right_space=0, top_bottom_space=0)
        scroll_win.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        # FIXME UI a align to adjust ui
        ui_align = gtk.Alignment(0, 0, 0, 0)
        ui_align.set_padding(TEXT_WINDOW_TOP_PADDING,
                                    TEXT_WINDOW_TOP_PADDING,
                                    TEXT_WINDOW_LEFT_PADDING,
                                    TEXT_WINDOW_LEFT_PADDING)
        ui_align.add(vbox)
        scroll_win.add_with_viewport(ui_align)

        self.eventbox = gtk.EventBox()
        self.eventbox.set_above_child(False)
        self.eventbox.add(scroll_win)
        vbox.connect("expose-event", self.expose_callback)
        ui_align.connect("expose-event", self.expose_callback)
        nm_module.nmclient.connect("activate-succeed", self.activate_succeed) 
        nm_module.nmclient.connect("activate-failed", self.activate_failed) 
        nm_module.nmclient.connect("device-added", self.device_added)
        nm_module.nmclient.connect("device-removed", self.device_removed)

        slider._append_page(self.eventbox, "main")
        slider._append_page(self.wired_setting_page, "wired")
        slider._append_page(self.dsl_setting_page, "dsl")
        slider._append_page(self.wireless_setting_page, "wireless")
        slider._append_page(self.proxy_setting_page, "proxy")
        slider._append_page(self.vpn_setting_page, "vpn")
        slider._append_page(Region(), "region")
        slider._append_page(self.mobile_setting_page, "mobile")
        #pdb.set_trace()
        slider.show_all()
        slider._set_to_page("main")

    def expose_callback(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb( 1, 1, 1) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

    def activate_succeed(self, widget, connection_path):
        print "active_succeed with", connection_path
        #print connection_path

    def activate_failed(self, widget, connection_path):
        print "active failed"

    def device_added(self, widget, connection_path):
        print "device add:", connection_path
        self.wired.refresh_device()

    def device_removed(self, widget, connection_path):
        print "device remove:", connection_path
        self.wired.refresh_device()


    def init_sections(self, module_frame):
        #slider._set_to_page("main")
        self.wired = WiredSection(lambda : module_frame.send_submodule_crumb(2, _("Wired Setting")))
        self.wireless = WirelessSection(lambda : module_frame.send_submodule_crumb(2, _("Wireless Setting")))
        self.dsl = DSL(lambda : module_frame.send_submodule_crumb(2, _("DSL")))
        self.proxy = Proxy(lambda : module_frame.send_submodule_crumb(2, _("Proxy")))
        self.vpn = VpnSection(lambda : module_frame.send_submodule_crumb(2, _("VPN")))

        self.wired_setting_page = WiredSetting(lambda  :slider.slide_to_page(self.eventbox, "left"),
                                          lambda  : module_frame.send_message("change_crumb", 1))
        self.wired.add_setting_page(self.wired_setting_page)

        self.wireless_setting_page = WirelessSetting(lambda :slider.slide_to_page(self.eventbox, "left"),
                                                lambda : module_frame.send_message("change_crumb", 1))
        self.wireless.add_setting_page(self.wireless_setting_page)

        self.dsl_setting_page = DSLSetting( lambda  :slider.slide_to_page(self.eventbox, "left"),
                                          lambda  : module_frame.send_message("change_crumb", 1))
        self.dsl.add_setting_page(self.dsl_setting_page)

        self.proxy_setting_page = ProxyConfig( lambda  :slider.slide_to_page(self.eventbox, "left"),
                                          lambda  : module_frame.send_message("change_crumb", 1))
        self.proxy.add_setting_page(self.proxy_setting_page)
        self.vpn_setting_page = VPNSetting( lambda : slider.slide_to_page(self.eventbox, "left"),
                               lambda : module_frame.send_message("change_crumb", 1),
                               module_frame)
        self.vpn.add_setting_page(self.vpn_setting_page)

        self.mobile = Mobile(lambda : module_frame.send_submodule_crumb(2, _("Mobile Network")))
        self.mobile_setting_page = MobileSetting( lambda  :slider.slide_to_page(self.eventbox, "left"),
                                          lambda  : module_frame.send_message("change_crumb", 1))
        self.mobile.add_setting_page(self.mobile_setting_page)

    def refresh(self):
        from nmlib.nm_secret_agent import NMSecretAgent
        from mm.mmclient import MMClient
        nm_module.nmclient = cache.getobject("/org/freedesktop/NetworkManager")
        nm_module.nm_remote_settings = cache.getobject("/org/freedesktop/NetworkManager/Settings")
        nm_module.secret_agent = NMSecretAgent()
        nm_module.mmclient = MMClient
        self.init_sections(self.module_frame)
        self.eventbox.set_above_child(False)
        self.eventbox.queue_draw()

    def stop(self):
        
        self.eventbox.set_above_child(True)
        self.wired_setting_page = None
        self.wireless_setting_page = None
        self.dsl_setting_page = None
        
    def get_main_page(self):
        return self.eventbox

if __name__ == '__main__':
    if is_dbus_name_exists("org.freedesktop.NetworkManager", False):
        module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))
        
        network = Network(module_frame)

        def service_stop_cb(widget, s):
            network.stop()
            global cache
            cache.clearcache()
            cache.clear_spec_cache()

        def service_start_cb(widget, s):
            network.refresh()

        servicemanager.connect("service-start", service_start_cb)
        servicemanager.connect("service-stop", service_stop_cb)
        main_align = network.get_main_page()
        module_frame.add(slider)
        
        def message_handler(*message):
            (message_type, message_content) = message
            if message_type == "show_again":
                slider._set_to_page("main")
                module_frame.send_module_info()
            elif message_type == "click_crumb":
                print "click_crumb"
                (crumb_index, crumb_label) = message_content
                if crumb_index == 1:
                    slider._slide_to_page("main", "left")
                if crumb_label == _("VPN"):
                    slider._slide_to_page("vpn", "left")

        module_frame.module_message_handler = message_handler
        module_frame.run()
