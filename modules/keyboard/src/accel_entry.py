#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
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

from dtk.ui.new_entry import ShortcutKeyEntry
from dtk.ui.label import Label
import gtk
import gobject

class AccelBuffer(object):
    '''a buffer which store accelerator'''
    def __init__(self):
        super(AccelBuffer, self).__init__()
        self.state = None
        self.keyval = None
    
    def set_state(self, state):
        '''
        set state
        @param state: the state of the modifier keys, a GdkModifierType
        '''
        self.state = state & (~gtk.gdk.MOD2_MASK)
    
    def get_state(self):
        '''
        get state
        @return: the state of the modifier keys, a GdkModifierType or None
        '''
        return self.state
    
    def set_keyval(self, keyval):
        '''
        set keyval
        @param keyval: a keyval, an int type
        '''
        self.keyval = keyval
    
    def get_keyval(self):
        '''
        get keyval
        @return: a keyval, an int type or None
        '''
        return self.keyval
    
    def get_accel_name(self):
        '''
        converts the accelerator keyval and modifier mask into a string
        @return: a acceleratot string
        '''
        if self.state is None or self.keyval is None:
            return ''
        return gtk.accelerator_name(self.keyval, self.state)
    
    def get_accel_label(self):
        '''
        converts the accelerator keyval and modifier mask into a string
        @return: a accelerator string
        '''
        if self.state is None or self.keyval is None:
            return ''
        return gtk.accelerator_get_label(self.keyval, self.state)
    
    def set_from_accel(self, accelerator):
        '''
        parses the accelerator string and update keyval and state
        @parse accelerator: a accelerator string
        '''
        (self.keyval, self.state) = gtk.accelerator_parse(accelerator)
    
    def is_equal(self, accel_buffer):
        '''
        check an other AccelBuffer object is equal
        @param accel_buffer: a AccelBuffer object
        @return: True if their values are equal, otherwise False'''
        if self.get_state() == accel_buffer.get_state()\
                and self.get_keyval() == accel_buffer.get_keyval():
                return True
        else:
            return False

    def __eq__(self, accel_buffer):
        ''' '''
        return self.is_equal(accel_buffer)


class AccelEntry(ShortcutKeyEntry):
    ''' '''
    def __init__(self, content=""):
        super(AccelEntry, self).__init__()
        self.accel_buffer = AccelBuffer()
        self.accel_buffer.set_from_accel(content)
        #super(AccelEntry, self).__init__(self.accel_buffer.get_accel_label())
        self.accel_label = Label(self.accel_buffer.get_accel_label(), enable_select=False)
        self.accel_align = gtk.Alignment()
        self.accel_align.set(0.0, 0.5, 0.0, 0.0)
        self.accel_align.add(self.accel_label)
        self.grab_area = gtk.EventBox()
        self.grab_area.set_size_request(1, -1)
        self.grab_area.set_can_focus(True)
        self.grab_area.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.grab_area.add_events(gtk.gdk.KEY_PRESS_MASK)
        self.h_box.remove(self.entry)
        self.h_box.pack_start(self.accel_align)
        self.h_box.pack_start(self.grab_area, False, False)
        #self.connect("wait-key-input", self.__on_wait_key_input_cb)
        #self.connect("shortcut-key-change", self.__on_shortcut_key_change_cb)
        self.grab_area.connect("button-press-event", self.__on_grab_area_button_press_cb)
        self.grab_area.connect("key-press-event", self.__on_grab_area_key_press_cb)
        self.accel_label.connect("button-press-event", self.__on_label_button_press)
        #self.accel_label.button_press_label = self.__on_label_button_press
        self.accel_label.keymap = {}

    def __on_label_button_press(self, widget, event):
        self.accel_label.set_text(("Please input new shortcuts"))
        if gtk.gdk.keyboard_grab(self.grab_area.window, False, 0) != gtk.gdk.GRAB_SUCCESS:
            self.accel_label.set_text(self.accel_buffer.get_accel_label())
            return None
        if gtk.gdk.pointer_grab(self.grab_area.window, False, gtk.gdk.BUTTON_PRESS_MASK, None, None, 0) != gtk.gdk.GRAB_SUCCESS:
            gtk.gdk.keyboard_ungrab(0)
            self.accel_label.set_text(self.accel_buffer.get_accel_label())
            return None
        self.grab_area.grab_focus()
        
    def __on_grab_area_button_press_cb(self, widget, event):
        gtk.gdk.keyboard_ungrab(0)
        gtk.gdk.pointer_ungrab(0)
        self.accel_label.set_text(self.accel_buffer.get_accel_label())

    def __on_grab_area_key_press_cb(self, widget, event):
        gtk.gdk.keyboard_ungrab(0)
        gtk.gdk.pointer_ungrab(0)
        self.accel_label.set_text(self.accel_buffer.get_accel_label())
        # TODO 按键分析

    def __on_shortcut_key_change_cb(self, widget, new_key):
        print "shortcut key changed:", new_key

    def set_size(self, width, height):
        super(AccelEntry, self).set_size(width, height)
        self.accel_align.set_size_request(width, height)
        
    def __on_wait_key_input_cb(self, widget, old_key):
        print "wait key inout", self.grab_area.window.get_geometry()
        if gtk.gdk.keyboard_grab(self.grab_area.window, False, 0) != gtk.gdk.GRAB_SUCCESS:
            self.set_text(self.shortcut_key)
            return None
        gobject.timeout_add_seconds(3, gtk.gdk.keyboard_ungrab, 0)
        if gtk.gdk.pointer_grab(self.grab_area.window, False, gtk.gdk.BUTTON_PRESS_MASK, None, None, 0) != gtk.gdk.GRAB_SUCCESS:
            gtk.gdk.keyboard_ungrab(0)
            self.set_text(self.shortcut_key)
            return None
        gobject.timeout_add_seconds(3, gtk.gdk.pointer_ungrab, 0)
        self.grab_area.grab_focus()

gobject.type_register(AccelEntry)
