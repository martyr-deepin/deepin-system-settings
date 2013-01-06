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
from dtk.ui.dialog import DialogBox
from dtk.ui.button import Button
from dtk.ui.utils import color_hex_to_cairo
from nls import _
import gtk
import gobject
from glib import markup_escape_text
from constant import *

def check_conflict_item(accel_buf):
    for category in self.__shortcuts_items:
        for items in self.__shortcuts_items[category]:
            if items != item and items.accel_buffer == accel_buf:
                return items
    return None

def draw_widget_background(widget, event):
    x, y, w, h = widget.allocation
    cr = widget.window.cairo_create()
    cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))
    cr.rectangle(x+1, y+1, w-2, h-2)                                                 
    cr.fill()

def process_unmodifier_key(tmp_accel_buf):
    dialog = DialogBox(" ", 550, 150)
    dialog.window_frame.connect("expose-event", draw_widget_background)
    dialog.set_keep_above(True)
    dialog.set_modal(True)
    dialog.body_align.set_padding(15, 10, 10, 10)
    label1 = Label(_("The shortcut \"%s\" cannot be used because it will become impossible to type using this key.")% tmp_accel_buf.get_accel_label())
    label2 = Label(_("Please try with a key such as Control, Alt or Shift at the same time."))
    dialog.body_box.pack_start(label1)
    dialog.body_box.pack_start(label2)
    button = Button(_("Cancel"))
    button.connect("clicked", lambda b: dialog.destroy())
    dialog.right_button_box.set_buttons([button])
    dialog.show_all()

def resolve_accel_entry_conflict(origin_entry, conflict_entry, tmp_accel_buf):
    dialog = DialogBox(" ", 620, 150)
    dialog.window_frame.connect("expose-event", draw_widget_background)
    dialog.set_keep_above(True)
    dialog.set_modal(True)
    dialog.body_align.set_padding(15, 10, 10, 10)
    label1 = Label(_("The shortcut \"%s\" is already used for\"%s\"")%
                   (tmp_accel_buf.get_accel_label(), conflict_entry.settings_description))
    label2 = Label(_("If you reassign the shortcut to \"%s\", the \"%s\" shortcut will be disabled.")%
                   (origin_entry.settings_description, conflict_entry.settings_description))
    dialog.body_box.pack_start(label1)
    dialog.body_box.pack_start(label2)
    button_reassign = Button(_("Reassign"))
    button_cancel = Button(_("Cancel"))
    button_cancel.connect("clicked", lambda b: origin_entry.reassign_cancel(dialog))
    button_reassign.connect("clicked", lambda b: origin_entry.reassign(tmp_accel_buf, conflict_entry, dialog))
    dialog.right_button_box.set_buttons([button_cancel, button_reassign])
    dialog.show_all()

def set_gsettings_or_gconf_value(settings_obj, key, accel_name):
    pass

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
        return markup_escape_text(gtk.accelerator_get_label(self.keyval, self.state))
    
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
    TYPE_GSETTINGS = 0
    TYPE_GCONF = 1
    __gsignals__ = {
        "accel-key-change" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
    }
    def __init__(self, content="",
                 check_conflict_func=None,
                 resolve_conflict_func=None,
                 process_unmodifier_func=process_unmodifier_key):
        '''
        @param content: a string container accelerator
        @param check_conflict_func: a function return a AccelEntry object, if their AccelBuffer is equal
        @param resolve_conflict_func: a function to resolve conflict
        @param process_unmodifier_func: a function to check the Accelerator is whether valid
        '''
        super(AccelEntry, self).__init__()
        self.accel_buffer = AccelBuffer()
        self.accel_buffer.set_from_accel(content)
        self.accel_str = self.accel_buffer.get_accel_label()
        if not self.accel_str:
            self.accel_str = _('disable')
        self.accel_label = Label(self.accel_str, enable_select=False)
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
        self.grab_area.connect("button-press-event", self.__on_grab_area_button_press_cb)
        self.grab_area.connect("key-press-event", self.__on_grab_area_key_press_cb)
        self.accel_label.connect("button-press-event", self.__on_label_button_press_cb)
        self.accel_label.keymap = {}
        self.set_size(180, 24)

        self.check_conflict_func = check_conflict_func
        self.resolve_conflict_func = resolve_conflict_func
        self.process_unmodifier_func = process_unmodifier_func

        self.settings_description = ""
        self.settings_key = ""
        self.settings_obj = None
        self.connect("accel-key-change", self.__on_accel_key_change_cb)

    def __on_label_button_press_cb(self, widget, event):
        self.accel_label.set_text(("Please input new shortcuts"))
        if gtk.gdk.keyboard_grab(self.grab_area.window, False, 0) != gtk.gdk.GRAB_SUCCESS:
            self.accel_label.set_text(self.accel_str)
            return None
        if gtk.gdk.pointer_grab(self.grab_area.window, False, gtk.gdk.BUTTON_PRESS_MASK, None, None, 0) != gtk.gdk.GRAB_SUCCESS:
            gtk.gdk.keyboard_ungrab(0)
            self.accel_label.set_text(self.accel_str)
            return None
        self.grab_area.grab_focus()
        
    def __on_grab_area_button_press_cb(self, widget, event):
        gtk.gdk.keyboard_ungrab(0)
        gtk.gdk.pointer_ungrab(0)
        self.accel_label.set_text(self.accel_str)

    def __on_grab_area_key_press_cb(self, widget, event):
        if event.is_modifier:
            return False
        gtk.gdk.keyboard_ungrab(0)
        gtk.gdk.pointer_ungrab(0)
        keyval = event.keyval
        state = event.state = event.state & (~gtk.gdk.MOD2_MASK)  # ignore MOD2_MASK
        # cancel edit
        if keyval == gtk.keysyms.Escape:
            self.accel_label.set_text(self.accel_str)
            return
        # clear edit
        if keyval == gtk.keysyms.BackSpace:
            self.set_keyval_and_state(0, 0)
            return
        tmp_accel_buf = AccelBuffer()
        tmp_accel_buf.set_keyval(keyval)
        tmp_accel_buf.set_state(state)
        if self.check_unmodified_keys(event) and self.process_unmodifier_func:
            self.accel_label.set_text(self.accel_str)
            self.process_unmodifier_func(tmp_accel_buf)
            return
        if self.check_conflict_func:
            conflict_entry = self.check_conflict_func(self)
            if conflict_entry and self.resolve_conflict_func:
                self.resolve_conflict_func(self, conflict_entry, tmp_accel_buf)
                return
        self.set_keyval_and_state(keyval, state)

    def reassign_cancel(self, widget=None):
        ''' cancel reassign when it conflict '''
        if widget:
            widget.destroy()
        self.accel_label.set_text(self.accel_str)
    
    def reassign(self, accel_buf, conflict_entry, widget=None):
        if widget:
            widget.destroy()
        self.set_keyval_and_state(accel_buf.get_keyval(), accel_buf.get_state())
        conflict_entry.set_keyval_and_state(0, 0)
    
    def check_unmodified_keys(self, event):
        #Check for unmodified keys
        state = event.state
        keyval = event.keyval
        state = event.state & (~gtk.gdk.MOD2_MASK)  # ignore MOD2_MASK
        forbidden_keyvals = [
            # Navigation keys
            gtk.keysyms.Home,
            gtk.keysyms.Left,
            gtk.keysyms.Up,
            gtk.keysyms.Right,
            gtk.keysyms.Down,
            gtk.keysyms.Page_Up,
            gtk.keysyms.Page_Down,
            gtk.keysyms.End,
            gtk.keysyms.Tab,
            # Return 
            gtk.keysyms.KP_Enter,
            gtk.keysyms.Return,
            gtk.keysyms.space,
            gtk.keysyms.Mode_switch]
        return (state == 0 or state == gtk.gdk.SHIFT_MASK) and (
                gtk.keysyms.a <= keyval <= gtk.keysyms.z or
                gtk.keysyms.A <= keyval <= gtk.keysyms.Z or
                gtk.keysyms._0 <= keyval <= gtk.keysyms._9 or
                gtk.keysyms.kana_fullstop <= keyval <= gtk.keysyms.semivoicedsound or
                gtk.keysyms.Arabic_comma <= keyval <= gtk.keysyms.Arabic_sukun or
                gtk.keysyms.Serbian_dje <= keyval <= gtk.keysyms.Cyrillic_HARDSIGN or
                gtk.keysyms.Greek_ALPHAaccent <= keyval <= gtk.keysyms.Greek_omega or
                gtk.keysyms.hebrew_doublelowline <= keyval <= gtk.keysyms.hebrew_taf or
                gtk.keysyms.Thai_kokai <= keyval <= gtk.keysyms.Thai_lekkao or
                gtk.keysyms.Hangul <= keyval <= gtk.keysyms.Hangul_Special or
                gtk.keysyms.Hangul_Kiyeog <= keyval <= gtk.keysyms.Hangul_J_YeorinHieuh or
                keyval in forbidden_keyvals)

    def set_keyval_and_state(self, keyval, state):
        self.accel_buffer.set_keyval(keyval)
        self.accel_buffer.set_state(state)
        self.emit("accel-key-change", self.accel_buffer.get_accel_name())
        self.accel_str = self.accel_buffer.get_accel_label()
        if not self.accel_str:
            self.accel_str = _('disable')
        self.accel_label.set_text(self.accel_str)
    
    def set_size(self, width, height):
        super(AccelEntry, self).set_size(width, height)
        self.accel_align.set_size_request(width, height)
        self.accel_label.label_width = width
        self.accel_label.set_size_request(width, height)

    def __on_accel_key_change_cb(self, widget, accel_name):
        if not self.settings_obj:
            return
        set_gsettings_or_gconf_value(self.settings_obj, self.settings_key, accel_name)
        
gobject.type_register(AccelEntry)
