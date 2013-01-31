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

class EventDispatcher(gobject.GObject):
    SIGNAL = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT))
    SIGNAL_SIMPLE = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
    SIGNAL_COMP = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT,gobject.TYPE_INT))
    SIGNAL_COMP2 = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT))
    SIGNAL_CONFIG = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING))
    SIGNAL_BASE = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    SIGNAL_TUPLE = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_INT))

    __gsignals__= {

            "connection-change" : SIGNAL_SIMPLE,
            "connection-delete" : SIGNAL_SIMPLE,
            "button-change" : SIGNAL,
            "set-tip" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),

            "wired_change" : SIGNAL_TUPLE,
            "wireless_change" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_INT, gobject.TYPE_INT,)),
            "connect_by_ssid" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),

            }

    def __init__(self):
        super(EventDispatcher, self).__init__()
        self.__update_source_id = None

    def change_setting(self, connection):
        self.emit("connection-change", connection)

    def delete_setting(self, old_connection, new_connection):
        self.emit("connection-delete", old_connection)
        #self.emit("connection-change", new_connection)

    def set_button(self, content, state):
        self.emit("button_change", content, state)

    def set_tip(self, content):
        self.emit("set-tip", content)

    def wired_change(self, new_state, reason):
        self.emit("wired_change",new_state, reason)

    def wireless_change(self, new_state, old_state, reason):
        self.emit("wireless_change", new_state, old_state, reason)

    def connect_by_ssid(self, ssid):
        self.emit("connect_by_ssid", ssid)


Dispatcher = EventDispatcher()

