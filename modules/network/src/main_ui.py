#!/usr/bin/env python #-*- coding:utf-8 -*-

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

from proxy_config import ProxyConfig, ProxySettings
import sys
import os
from dss import app_theme
from dtk.ui.theme import ui_theme
from dtk.ui.treeview import TreeView
from dtk.ui.draw import  draw_line
from dtk.ui.utils import color_hex_to_cairo, container_remove_all, get_content_size
from deepin_utils.file import  get_parent_dir
from dtk.ui.label import Label
from dtk.ui.scrolled_window import ScrolledWindow
import gtk

from container import Contain, ToggleThread
from lists import (WiredItem, WirelessItem, HidenItem, DSLItem,
                   MobileItem, VPNItem, DeviceToggleItem)
from dsl_config import DSLSetting
from vpn_config import VPNSetting
from mobile_config import MobileSetting
from regions import Region
from settings_widget import HotspotBox

from nm_modules import nm_module
from helper import Dispatcher, event_manager
from shared_methods import net_manager

sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))

from constants import *
from nls import _
from timer import Timer

slider = nm_module.slider
from dtk.ui.theme import DynamicColor

LABEL_COLOR = DynamicColor("#666666")
PADDING = 32

from dss_log import log

def pack_start(parent, child_list, expand=False, fill=False):
    for child in child_list:
        parent.pack_start(child, expand, fill)

class Section(gtk.VBox):
    # Section prototype

    def __init__(self):
        gtk.VBox.__init__(self)

        self.timer = Timer(200, self.action_after_toggle)

    def load(self, toggle, content=[]):
        self.toggle = toggle
        self.content_box = gtk.VBox(spacing=0)
        self.pack_start(self.toggle, False, False)
        self.toggle.switch.connect("toggled", self.toggle_callback)

        self.tree = TreeView([])
        self.tree.set_expand_column(1)
        self.tree.draw_mask = self.draw_mask
        content.insert(0, self.tree)
            
        for c in content:
            self.content_box.pack_start(c, False, False)

        self.align = self._set_align()
        self.pack_start(self.align, False, False)
        self.show_all()

    def init_state(self):
        pass

    def set_active(self, state):
        self.toggle.set_active(state)

    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()

    def _set_align(self):
        align = gtk.Alignment(0,0,1,0)
        align.set_padding(0, 0, PADDING, 11 + 11)
        return align

    def toggle_callback(self, widget):
        if self.timer.alive():
            self.timer.restart()
        else:
            self.timer.start()

    def action_after_toggle(self):
        is_active = self.toggle.get_active()
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
        pass

    def toggle_on_after(self):
        pass

    def toggle_off(self):
        pass
    
    def get_list(self):
        pass
    
    def section_show(self):
        self.set_no_show_all(False)
        self.show_all()

    def section_hide(self):
        self.set_no_show_all(True)
        self.hide()

class WiredDevice(object):

    def _init_signals(self):
        net_manager.device_manager.load_wired_listener(self)

    def wired_device_active(self, widget, new_state, old_state, reason):

        index = self.wired_devices.index(widget)
        if self.tree.visible_items != []:
            log.debug()
            self.tree.visible_items[index].set_net_state(2)
            self.tree.queue_draw()
        self.wire.set_active(True)

    def wired_device_deactive(self, widget, new_state, old_state, reason):
        if reason == 36:
            print "in fact there had device removed"
        ########################
            net_manager.init_devices()
            self.wired_devices = net_manager.wired_devices
            self._init_signals()
            self.tree.delete_all_items()
            item_list = self.get_list()
            if item_list:
                item_list[-1].is_last = True
                self.tree.add_items(item_list, 0, True)
                self.tree.set_size_request(-1, len(self.tree.visible_items)*30)
        index = 0
        for d in self.wired_devices:
            if d.get_state() == 100:
                self.tree.visible_items[index].set_net_state(2)
            index += 1
        if not any([d.get_state() == 100 for d in net_manager.wired_devices]):
            self.wire.set_active(False)

    def wired_device_unavailable(self,  widget, new_state, old_state, reason):
        self.wired_device_deactive(widget, new_state, old_state, reason)

    def wired_activate_start(self, widget, new_state, old_state, reason):
        index = self.wired_devices.index(widget)
        if self.tree.visible_items != []:
            self.tree.visible_items[index].set_net_state(1)
            self.tree.queue_draw()

    def wired_activate_failed(self, widget, new_state, old_state, reason):
        #pass
        index = self.wired_devices.index(widget)
        if self.tree.visible_items != []:
            print "device activate failed,set state 0"
            self.tree.visible_items[index].set_net_state(0)
            self.tree.queue_draw()

class WiredSection(Section, WiredDevice):

    def __init__(self):
        Section.__init__(self)
        self.wire = Contain(app_theme.get_pixbuf("network/cable.png"), _("Wired"), lambda w:w)
        self.load(self.wire, [])
    
    @classmethod
    def show_or_hide(self):
        if net_manager.device_manager.get_wired_devices():
            return True
        else:
            return False

    def init_state(self):
        self.wired_devices = net_manager.device_manager.get_wired_devices()
        if self.wired_devices:
            #if self.get_state(self.wired_devices):
            if nm_module.nmclient.get_wired_active_connection():
                self.wire.set_active(True)
        else:
            pass
        self.init_signals()

    def init_signals(self):
        Dispatcher.connect("wired-device-add", self.device_added)
        self._init_signals()
    
    def get_state(self, devices):
        return any([d.get_state() == 100 for d in devices])
    
    def device_added(self, widget, device):
        print "device added cb"
        self.wired_devices = net_manager.device_manager.get_wired_devices()
        self._init_signals()
        if self.wire.get_active():
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
                if device_ethernet:
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
        if widget not in net_manager.device_manager.wireless_devices:
            return
        self.pwd_failed = False

        if self.selected_item:
            self.selected_item.set_net_state(2)
            return

        index = self.get_actives(self.ap_list)
        if index:
            map(lambda (i, s): self.tree.visible_items[i].set_net_state(2), index)

    def wireless_device_deactive(self, widget, new_state, old_state, reason):
        log.info(widget, widget.get_state())
        if widget not in net_manager.device_manager.wireless_devices:
            return
        #self.wireless.set_sensitive(True)
        if reason == 36:
            log.info("some device removed")
            net_manager.init_devices()
            self.remove_switcher() 
            return 

        if new_state == 60:
            wifi = nm_module.cache.get_spec_object(widget.object_path)
            wifi.nm_device_disconnect()
            return
        if reason == 39:
            if any([d.get_state() == 100 for d in net_manager.device_manager.wireless_devices]):
                return
            else:

                self.wireless.set_active(False)
                return

        if self._get_active_item():
            for item in self._get_active_item():
                item.set_net_state(0)
                #self.device_dict[widget] = [item, 0]

    def wireless_device_unavailable(self, widget, new_state, old_state, reason):
        if widget not in net_manager.device_manager.wireless_devices:
            return

    def wireless_activate_start(self, widget, new_state, old_state, reason):
        log.debug(new_state, old_state, reason)
        if widget not in net_manager.device_manager.wireless_devices:
            return
        self.this_connection = widget.get_real_active_connection()
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
                for i,s in index:
                    self.tree.visible_items[i].set_net_state(1)

    def wireless_activate_failed(self, widget, new_state, old_state, reason):
        if widget not in net_manager.device_manager.wireless_devices:
            return
        if reason == 7:
            self.pwd_failed = True

    #def toggle_dialog(self, connection, security=None):
        #'''
        #This dialog only show up when clicked ap hs no connections
        #'''
        #ssid = connection.get_setting("802-11-wireless").ssid
        #if ssid != None:
            #AskPasswordDialog(connection,
                              #ssid,
                              #key_mgmt=security,
                              #cancel_callback=self.cancel_ask_pwd,
                              #confirm_callback=self.pwd_changed).show_all()

    def cancel_ask_pwd(self):
        pass

    def pwd_changed(self, pwd, connection):
        item = self._get_active_item()
        if item:
            map(lambda i: i.pwd_changed(pwd, connection), item)


class WirelessSection(Section, WirelessDevice):

    def __init__(self):
        Section.__init__(self)
        WirelessDevice.__init__(self)
        self.wireless = Contain(app_theme.get_pixbuf("network/wifi.png"), _("Wireless"), lambda w:w)
        self.label =  Label(_("Set up a hidden wireless connection"), 
                          LABEL_COLOR,
                          underline=True,
                          enable_select=False,
                          enable_double_click=False)

        space = gtk.VBox()
        space.set_size_request(-1, 15)

        self.load(self.wireless, [space, self.label])
        self.content_box.set_spacing(0)

        self.selected_item = None
        self.device_tree = None
        self.focused_device = None
        self.wireless_devices = None

    def add_switcher(self):
        if self.device_tree == None:
            self.device_tree = TreeView([DeviceToggleItem(self.wireless_devices, 0)])
            self.device_tree.set_expand_column(1)
            self.content_box.pack_start(self.device_tree, False, True)
            self.content_box.reorder_child(self.device_tree, 0)
            net_manager.emit_wifi_switch(0)

    def remove_switcher(self):
        if self.device_tree\
           and self.device_tree in self.content_box.get_children():
            self.content_box.remove(self.device_tree)
            self.device_tree = None
            try:
                self.focused_device = self.wireless_devices[0]
            except:
                log.error("get no wireless devices but try to index")
                self.focused_device = None
            self.wireless_redraw(None)


    @classmethod
    def show_or_hide(self):
        if net_manager.device_manager.get_wireless_devices():
            self.wireless_devices = net_manager.device_manager.get_wireless_devices()
            return True
        else:
            self.wireless_devices = []
            return False

    def init_state(self):
        self.ap_list = []
        self.wireless_devices = net_manager.device_manager.get_wireless_devices()
        if self.wireless_devices:
            #self.device_dict = dict()
            self.focused_device = self.wireless_devices[0]
            if len(self.wireless_devices) > 1:
                self.add_switcher()
            self.tree.connect("single-click-item", self.set_selected_item)
            ## check state
            if self.get_state(self.wireless_devices):
                self.wireless.set_active(True)
        else:
            pass
        self.init_signals()


    def init_signals(self):
        self._init_signals() 
        Dispatcher.connect("switch-device", self.switch_devices)
        Dispatcher.connect("wireless-device-add", self.device_added)
        Dispatcher.connect("ap-added", self.ap_added_callback)
        Dispatcher.connect("ap-removed", self.ap_removed_callback)
        Dispatcher.connect("wireless-redraw", self.wireless_redraw)
        self.label.connect("button-release-event", self.create_a_hidden_network)

    def switch_devices(self, widget, device):
        self.focused_device = device
        if self.device_tree:
            self.device_tree.visible_items[0].set_index(device)
        #item, state = self.device_dict[device]
        #item.set_net_state(state)
        self.wireless_redraw(None)

    def wireless_redraw(self, widget):
        if self.wireless.get_active():
            self.wireless.set_active(True, emit=True)

    def device_added(self, widget, device):
        self.wireless_devices = net_manager.device_manager.get_wireless_devices()
        self._init_signals()
        if len(self.wireless_devices) > 1:
            self.add_switcher()
        else:
            self.remove_switcher()
        if self.wireless.get_active():
            self.wireless.set_active(True, emit=True)


    def create_a_hidden_network(self, widget, c):
        from wlan_config import HiddenSetting
        Dispatcher.to_setting_page(HiddenSetting(None), False)

    def ap_added_callback(self, widget):
        if self.wireless.get_active():
            self.wireless.set_active(True, emit=True)

    def ap_removed_callback(self, widget):
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

        def to_item_state(device):
            if device.get_state() <= 30:
                return 0
            elif device.get_state() < 100:
                return 1
            elif device.get_state() == 100:
                return 2

        if not ap_list:
            return []
        index = []
        #for wireless_device in self.wireless_devices:
        active_connection = self.focused_device.get_active_connection()
        if active_connection:
            #if active_connection.get_state() != 2:
                #return []
            try:
                ssid = active_connection.get_connection().get_setting("802-11-wireless").ssid
                index.append([[ap.get_ssid() for ap in ap_list].index(ssid), to_item_state(self.focused_device)])
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
        #self.wireless.set_sensitive(True)
        indexs = self.get_actives(self.ap_list)
        if indexs:
            map(lambda (i, s): self.tree.visible_items[i].set_net_state(s), indexs)
        else:
            for d in self.wireless_devices:
                wifi = nm_module.cache.get_spec_object(d.object_path)
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
        #self.wireless.set_sensitive(False)

    def get_list(self):
        self.ap_list = list()
        if not self.wireless_devices:
            return []

        device_wifi = nm_module.cache.get_spec_object(self.focused_device.object_path)
        self.ap_list += device_wifi.order_ap_list()
        aps = map(lambda i:WirelessItem(i, self.focused_device), self.ap_list)
        hidden_list = self.get_hidden_connection(self.ap_list)
        hiddens = map(lambda c: HidenItem(c), hidden_list)
        return aps + hiddens

    def __ap_list_merge(self):
        ap_ssid = set(map(lambda ap: ap.get_ssid(), self.ap_list))
        merged_ap = []
        for ap in self.ap_list:
            if ap.get_ssid() in ap_ssid:
                merged_ap.append(ap)
                ap_ssid.remove(ap.get_ssid())

        return merged_ap

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
        self.dsl = Contain(app_theme.get_pixbuf("network/dsl.png"), _("DSL"), lambda w: w)
        self.label =  Label(_("Create a DSL connection"), 
                          LABEL_COLOR,
                          underline=True,
                          enable_select=False,
                          enable_double_click=False)
        
        self.load(self.dsl, [self.label])

        self.active_connection = None

    def init_state(self):
        self.wired_devices = net_manager.device_manager.get_wired_devices()
        if self.wired_devices:
            self.__init_signals()
            if nm_module.nmclient.get_pppoe_active_connection():
                print nm_module.nmclient.get_pppoe_active_connection()
                print nm_module.nmclient.get_wired_active_connection()

                self.dsl.set_active(True)
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

        event_manager.add_callback('dsl-connection-start', self.connection_start_by_user)


        signal_list = ["device_active",
                              "device_deactive",
                              "device_unavailable",
                              "activate_start",
                              "activate_failed"]

        for signal in signal_list:
            event_manager.add_callback(('dsl_%s'%signal).replace("_", "-"), getattr(self, signal))


    def connection_start_by_user(self, name, event, data):
        connection = data
        self.active_connection = connection

    def device_active(self, name, event, data):
        print "device active"
        if not self.dsl.get_active():
            self.dsl.set_active(True)
        if self.active_connection:
            index = self.connections.index(self.active_connection)
            if self.tree.visible_items != []:
                self.tree.visible_items[index].set_net_state(2)
                self.tree.queue_draw()

    def device_unavailable(self, name, event, data):
        print "device unavailable"

    def device_deactive(self, name, event, data):
        print "device deactive"
        new_state, old_state, reason = data
        if reason == 39:
            self.dsl.set_active(False)
            return
        if reason == 36:
            print "in fact there had device removed"
        ########################
            net_manager.init_devices()
            self.wired_devices = net_manager.wired_devices
            self._init_signals()
            self.tree.delete_all_items()
            item_list = self.get_list()
            if item_list:
                item_list[-1].is_last = True
                self.tree.add_items(item_list, 0, True)
                self.tree.set_size_request(-1, len(self.tree.visible_items)*30)
        index = 0
        for d in self.wired_devices:
            if d.get_state() == 100:
                self.tree.visible_items[index].set_net_state(2)
            index += 1
        if not any([d.get_state() == 100 for d in net_manager.wired_devices]):
            self.dsl.set_active(False)

    def activate_start(self, name, event, data):
        print "active start in main"
        if self.active_connection:
            index = self.connections.index(self.active_connection)
            if self.tree.visible_items != []:
                self.tree.visible_items[index].set_net_state(1)
                self.tree.queue_draw()

    def activate_failed(self, name, event, data):
        print "device failded"

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
        active_dsl = nm_module.nmclient.get_pppoe_active_connection()
        if active_dsl:
            try:
                for a in active_dsl:
                    connection = a.get_connection()
                    index = self.connections.index(connection)
                    self.tree.visible_items[index].set_net_state(2)
            except:
                index = []
        else:
            # add auto connect stuff
            pass
            
    def toggle_off(self):
        active_dsl = nm_module.nmclient.get_pppoe_active_connection()
        if not active_dsl:
            return
        for wired_device in self.wired_devices:
            wired_device.nm_device_disconnect()

    def get_list(self):
        self.connections =  nm_module.nm_remote_settings.get_pppoe_connections()
        return map(lambda c: DSLItem(c, None), self.connections)

    def jumpto_setting(self):
        Dispatcher.to_setting_page(DSLSetting(),hide_left=True)
        setting = nm_module.slider.get_page_by_name("setting")
        setting.create_new_connection()

class VpnSection(Section):
    def __init__(self):
        Section.__init__(self)

        #init
        self.vpn = Contain(app_theme.get_pixbuf("network/vpn.png"), _("VPN Network"), lambda w:w)
        self.label = Label(_("Create a VPN connection"), 
                           LABEL_COLOR,
                           underline=True,
                           enable_select=False,
                           enable_double_click=False)

        self.load(self.vpn, [self.label])
        self.no_auto_connect = False
        self.no_vpn_connecting = False
        self.this_setting = None
        self.vpn_path = None

    def init_state(self):
        vpn_active = nm_module.nmclient.get_vpn_active_connection()
        if vpn_active:
            self.vpn.set_active(True)
            for active in vpn_active:
                self.connect_vpn_signals(nm_module.cache.get_spec_object(active.object_path))
            
        self.__init_signals()

    @classmethod
    def show_or_hide(self):
        return True

    def __init_signals(self):
        self.label.connect("button-release-event", lambda w,p: self.jumpto_cb())
        Dispatcher.connect("vpn-redraw", self.vpn_redraw)
        Dispatcher.connect('vpn-start', self.vpn_start_cb)

        event_manager.add_callback("vpn-connecting", self.on_vpn_connecting)
        event_manager.add_callback('vpn-connected', self.vpn_connected)
        event_manager.add_callback('vpn-disconnected', self.vpn_disconnected)
        event_manager.add_callback('vpn-user-disconnect', self.on_user_stop_vpn)
        event_manager.add_callback('user-toggle-off-vpn-tray', self.user_toggle_off_vpn_tray)

    def user_toggle_off_vpn_tray(self, name, event, data):
        log.debug("toggle off vpn from tray")
        self.vpn.set_active(False)

    def on_user_stop_vpn(self, name, event, data):
        self.vpn.set_active(False)

    def vpn_redraw(self, widget):
        if self.vpn.get_active():
            self.no_auto_connect = True
            self.vpn.set_active(True, emit=True)
            #self.toggle_on()
            self.show_all()

    def vpn_start_cb(self, widget, path):
        log.debug("vpn start by tray")
        vpn_active = nm_module.cache.get_spec_object(path)
        if vpn_active.get_vpnstate() < 5:
            self.vpn_path = path
            self.on_vpn_connecting(None, None, path)


    def connect_vpn_signals(self, active_vpn):
        active_vpn.connect("vpn-connected", self.vpn_connected)
        active_vpn.connect("vpn-disconnected", self.vpn_disconnected)
        active_vpn.connect('vpn-user-disconnect', lambda w: self.vpn.set_active(False))

    def toggle_on(self):
        item_list = self.get_list()
        if item_list:
            item_list[-1].is_last = True
            self.tree.delete_all_items()
            self.tree.add_items(item_list)

    def on_active_conn_create(self, active_conn):
        net_manager.emit_vpn_start(active_conn)

    def try_active_vpn(self):
        for active_conn in nm_module.nmclient.get_anti_vpn_active_connection():
            if len(nm_module.nmclient.get_vpn_active_connection()) == 0:
                try:
                    active_conn.vpn_auto_connect(self.on_active_conn_create)
                except:
                    pass
            else:
                break

    def toggle_on_after(self):
        if self.no_auto_connect:
            self.no_auto_connect = False
            pass
        else:
            if not self.vpn_path:
                self.try_active_vpn()
            else:
                self.on_vpn_connecting(None, None, self.vpn_path)

        vpn_active = nm_module.nmclient.get_vpn_active_connection()
        if vpn_active:
            # TODO fix for mutiple
            connection = vpn_active[0].get_connection()
            try:
                index = self.connection.index(connection)
                self.tree.visible_items[index].set_net_state(2)
                return
            except Exception, e:
                log.error(e)
        else:
            pass

    def toggle_off(self):
        self.user_toggle_off()
        for active in nm_module.nmclient.get_anti_vpn_active_connection():
            active.device_vpn_disconnect()
        
        if self.vpn_path:
            nm_module.nmclient.deactive_connection_async(self.vpn_path)

    def user_toggle_off(self):
        log.debug("emit user toggle off")
        net_manager.emit_user_toggle_off("vpn-main")
    
    def get_list(self):
        self.connection = nm_module.nm_remote_settings.get_vpn_connections()
        return map(lambda c: VPNItem(c, None), self.connection)
    
    def jumpto_cb(self):
        Dispatcher.to_setting_page(VPNSetting(), True)
        setting = nm_module.slider.get_page_by_name("setting")
        setting.create_new_connection()

    # vpn signals
    def on_vpn_connecting(self, name, event, data):
        if not self.vpn.get_active():
            self.vpn.set_active(True)
            return
        log.debug("vpn start connect", data)
        self.vpn_path = data
        self.this_setting = nm_module.cache.getobject(data).get_connection().object_path
        map(lambda p: p.set_net_state(0), self.tree.visible_items)
        try:
            items = filter(lambda p: p.connection.object_path == self.this_setting, self.tree.visible_items)
            map(lambda i: i.set_net_state(1), items)
        except:
            pass

    def vpn_connected(self, name, event, data):
        log.debug(data)
        items = filter(lambda p: p.connection.object_path == self.this_setting, self.tree.visible_items)
        map(lambda i: i.set_net_state(2), items)

    def vpn_disconnected(self, name, event, data):
        log.debug(data)
        if self.this_setting == None:
            map(lambda i: i.set_net_state(0), self.tree.visible_items)
            return

        items = filter(lambda p: p.connection.object_path == self.this_setting, self.tree.visible_items)
        map(lambda i: i.set_net_state(0), items)
        self.this_setting = None
        self.vpn_path = None

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
        #self.init_signal()

    def init_state(self):
        self.init_signal()
        pass

    def init_signal(self):
        self._init_signals()

    def get_item(self, device):
        modem_path =device.get_udi()
        try:
            index = self.devices.index(modem_path)
            return self.tree.visible_items[index]
        except:
            return None

    @classmethod
    def show_or_hide(self):
        return True

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
        Dispatcher.to_setting_page(MobileSetting(), False)

class Proxy(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.proxy = Contain(app_theme.get_pixbuf("network/proxy.png"), _("Proxy"), self.toggle_cb)
        self.proxysetting = ProxySettings()
        self.add(self.proxy)
        #self.init_state()

    def init_state(self):
        if self.proxysetting.get_proxy_mode() != "none":
            self.proxy.set_active(True)

    @classmethod
    def show_or_hide(self):
        return True

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            if self.proxysetting.get_proxy_mode() == "none":
                self.proxysetting.set_proxy_mode("manual")
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
        settings = ProxyConfig()
        settings.init()
        slider.slide_to_page(settings, "right")
        Dispatcher.send_submodule_crumb(2, _("Proxy"))

    #def add_setting_page(self, setting_page):
        #self.settings = setting_page

    def section_show(self):
        self.set_no_show_all(False)
        self.show_all()

    def section_hide(self):
        self.set_no_show_all(True)
        self.hide()

    def set_active(self, state):
        self.proxy.set_active(state)

class Network(object):
    def __init__(self):        
        #self.init_sections()
        self.__init_ui()

        slider._append_page(self.eventbox, "main")
        slider.connect_after("show", lambda w: self.init_sections_state())
        slider._set_to_page("main")
        slider.show_all()
        Dispatcher.connect("to-setting-page", self.slide_to_setting_page)
        Dispatcher.connect("recheck-section", lambda w, i: self.__init_sections(0))
        Dispatcher.connect("service-stop-do-more", lambda w: self.stop())

    def init_sections_state(self):
        net_manager.init_devices()
        for section in self.vbox.get_children():
            if section.show_or_hide():
                section.section_show()
                section.init_state()
            else:
                section.section_hide()
        slider._append_page(Region(), "region")
        from setting_page_ui import SettingUI
        self.setting_page_ui = SettingUI(None, None)
        slider._append_page(self.setting_page_ui, "setting")
         
    def __init_sections(self, index):
        section_list = [WiredSection, WirelessSection, DSLSection, MobileSection, VpnSection, Proxy]
        if index == -1:
            container_remove_all(self.vbox)
            for section in section_list:
                section_ins = apply(section)
                self.vbox.pack_start(section_ins, False, True)
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
        #scroll_win.connect("event", self.test)
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

    def slide_to_setting_page(self, widget, setting_module, hide_left):
        self.setting_page_ui.load_module(setting_module, hide_left)

    def refresh(self):
        #self.init_sections()
        self.__init_sections(-1)
        self.init_sections_state()
        self.eventbox.set_above_child(False)
        self.eventbox.queue_draw()

    def stop(self):
        for section in self.vbox.get_children():
            section.set_active(False)
        self.eventbox.set_above_child(True)
        
    def get_main_page(self):
        return self.eventbox

