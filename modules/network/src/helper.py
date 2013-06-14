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
import gobject

from nmlib.nm_dispatcher import nm_events as event_manager                                          
from nls import _

int = gobject.TYPE_INT
obj = gobject.TYPE_PYOBJECT
str = gobject.TYPE_STRING

def event(*arg):
    return (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (arg))

class EventDispatcher(gobject.GObject):
    #SIGNAL = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT))
    #SIGNAL_SIMPLE = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
    #SIGNAL_COMP = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT,gobject.TYPE_INT))
    #SIGNAL_COMP2 = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT))
    #SIGNAL_CONFIG = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING))
    #SIGNAL_BASE = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    #SIGNAL_TUPLE = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_INT))

    __gsignals__= {

            "connection-change" : event(obj),
            "connection-delete" : event(obj),
            "button-change" : event(obj, obj),
            "set-tip" :       event(str),
            "wired_change" : event(obj, int, int),
            "wireless_change" : event(obj, int, int, int),
            "connect_by_ssid" : event(str, obj),
            "select-connection" : event(obj),
            "slide-to" : event(obj, str),
            "change-crumb" : event(str),
            "tray-show-more": event(),

            "nm-start": event(),
            "nm-stop": event(),

            "wired-device-add": event(obj),
            "wired-device-remove": event(obj),
            "wireless-device-add": event(obj),
            "wireless-device-remove": event(obj),
            "mmdevice-added" : event(obj),
            "mmdevice-removed": event(obj),
            "recheck-section" : event(int),

            "ap-added": event(),
            "ap-removed": event(),

            "to-setting-page": event(obj, obj),
            "to-region-page": event(obj),
            "region-back": event(obj, obj, str),

            "new-connection-created": event(obj),

            "setting-saved": event(),
            "setting-appled": event(),
            "connection-replace": event(obj),

            "request_resize": event(),

            "request-redraw": event(),

            "vpn-redraw": event(),
            
            "dsl-redraw": event(),
            "wireless_redraw": event(),

            "dss_start": event(),

            "vpn-type-change": event(obj),

            "service-stop-do-more": event(),
            "service-start-do-more": event(),

            "switch-device": event(obj),
            "vpn-start" : event(obj),
            'vpn-setting-change': event(obj),
            'vpn-force-stop': event(),

            }

    def __init__(self):
        super(EventDispatcher, self).__init__()
        self.__update_source_id = None

    def change_setting(self, connection):
        self.emit("connection-change", connection)

    def delete_setting(self, old_connection):
        self.set_tip(_("%s deleted")%(old_connection.get_setting("connection").id)) 
        self.emit("connection-delete", old_connection)
        #self.emit("connection-change", new_connection)

    def set_button(self, content, state):
        #print "emit button change", content, state
        self.emit("button-change", content, state)

    def set_tip(self, content):
        self.emit("set-tip", content)

    def wired_change(self, device, new_state, reason):
        self.emit("wired_change", device, new_state, reason)

    def add_slider(self, slider):
        self.__slider = slider

    def slide_to(self, page, direction):
        self.emit(page, str)

    def wireless_change(self, device, new_state, old_state, reason):
        '''
        #20: unavailable      0
        #30,..,39: reconfig   1
        #30: disconnect       2
        #40: try connect      3
        #60,50,..: need auth  4
        #100: connected       5
        #'''
        #if new_state is 20:
            #action = 0
        #elif new_state is 30:
        self.emit("wireless_change", device, new_state, old_state, reason)

    def connect_by_ssid(self, ssid, ap):
        self.emit("connect_by_ssid", ssid, ap)

    def tray_show_more(self):
        self.emit("tray-show-more")

    def nm_start(self):
        self.emit('nm-start')
    
    def nm_stop(self):
        self.emit('nm-stop')

    def device_add(self, device):
        pass

    def to_setting_page(self, module, hide_left=False):
        '''
        receiver main Network
        '''
        self.emit('to-setting-page', module, hide_left)

    def load_module_frame(self, module_frame):
        self.__module_frame = module_frame

    def load_slider(self, slider):
        self.__slider = slider

    def slide_to_page(self, name, direction):
        self.__slider.slide_to_page(self.__slider.get_page_by_name(name), direction)

    def to_main_page(self):
        self.__module_frame.send_message("change_crumb", 1)
        self.slide_to_page('main', "left")

    def send_submodule_crumb(self, index, name):
        self.__module_frame.send_submodule_crumb(index, name)

    def request_resize(self):
        self.emit("request_resize")

    def request_redraw(self):
        self.emit("request_redraw")

Dispatcher = EventDispatcher()
