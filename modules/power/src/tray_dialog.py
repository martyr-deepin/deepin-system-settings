#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Deepin, Inc.
#               2012 Hailong Qiu
#
# Author:     Hailong Qiu <356752238@qq.com>
# Maintainer: Hailong Qiu <356752238@qq.com>
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

import sys
sys.path.append("/usr/share/deepin-system-tray/src")
sys.path.append("/usr/share/deepin-system-tray/image")

import gtk
from nls import _, LANGUAGE
from vtk.window import Window
from vtk.utils import get_text_size
from vtk.draw import draw_text
from vtk.theme import vtk_theme
from vtk.timer import Timer
from dtk.ui.constant import DEFAULT_FONT, DEFAULT_FONT_SIZE
from dtk.ui.label import Label
from dtk.ui.theme import DynamicColor
from dtk.ui.utils import container_remove_all


APP_WIDTH = 375
APP_HEIGHT = 169
CANCEL_TEXT = _("Cancel")
OK_TEXT = _("OK")


class TrayDialog(Window):
    def __init__(self):
        Window.__init__(self)

        self.show_pixbuf = vtk_theme.get_pixbuf("deepin_shutdown", 50)
        self.cancel_text = CANCEL_TEXT
        self.btn_text_size = 11
        self.btn_text_color = "#b9b9b9"
        self.draw_rectangle_bool = False

        self.timer = Timer(1000)
        self.second = 60
        self.timer.Enabled = False
        self.timer.connect("Tick", self.timer_tick_evnet)
        
        self.run_exec = None
        self.argv = None
        self.set_pango_list()
        self.ok_key_check = False
        self.cancel_key_check = False
        
        self.__init_widgets()
        self.__init_settings()
        
    def show_dialog_window(self, widget):
        for alpha in range(0, 11):
            self.set_opacity(alpha * 0.1)

    def show_warning(self,
                    info_text,
                    ok_text=OK_TEXT,
                    cancel_text=CANCEL_TEXT,
                    ):
        self.show_pixbuf = vtk_theme.get_pixbuf("deepin_warning", 50)
        self.info_text = info_text

        container_remove_all(self.bottom_hbox)
        if OK_TEXT:
            self.ok_button = BottomButton(ok_text, self.btn_text_size)
            self.ok_button.connect("clicked", self.ok_btn_clicked)
            self.bottom_hbox.pack_end(self.ok_button, False, False)

        if CANCEL_TEXT:
            self.cancel_button = BottomButton(cancel_text, self.btn_text_size)
            self.cancel_button.connect("clicked", self.quit_dialog_window)
            self.cancel_button.set_check(True)
            self.bottom_hbox.pack_end(self.cancel_button, False, False)

        self.argv = None
        self.run_exec = None
        
        self.set_pango_list()
        
        if self.show_pixbuf:
            self.show_image.set_from_pixbuf(self.show_pixbuf)
        self.tick_label.set_text(info_text)

        self.timer.Enabled = False

        self.show_all()
        self.cancel_button.grab_focus()

    def show_dialog(self,
                    show_pixbuf_name,
                    info_text,
                    ok_text=OK_TEXT,
                    cancel_text=CANCEL_TEXT,
                    ):
        self.show_pixbuf = vtk_theme.get_pixbuf(show_pixbuf_name, 50)
        self.info_text = info_text

        self.ok_button = BottomButton(ok_text, self.btn_text_size)
        self.ok_button.connect("clicked", self.ok_btn_clicked)
        self.ok_button.set_check(True)
        self.cancel_button = BottomButton(cancel_text, self.btn_text_size)
        self.cancel_button.connect("clicked", self.quit_dialog_window)
        container_remove_all(self.bottom_hbox)
        self.bottom_hbox.pack_end(self.ok_button, False, False)
        self.bottom_hbox.pack_end(self.cancel_button, False, False)

        self.second = 60
        self.argv = None
        self.run_exec = None
        
        self.set_pango_list()
        
        if self.show_pixbuf:
            self.show_image.set_from_pixbuf(self.show_pixbuf)
        self.tick_label.set_text(self.info_text % 60)

        self.timer.Enabled = True

        self.show_all()
        self.ok_button.grab_focus()

    def set_pango_list(self):
        self.pango_list = None
        '''
        r, g, b = (65535, 0, 0)
        self.pango_list = pango.AttrList()
        if cn_check():
            start_index, end_index = 8, 12
        else:
            start_index, end_index = EN_RED_TEXT[self.show_top_text] 
            
        self.pango_list.insert(pango.AttrForeground(r, g, b, start_index, end_index - 1))
        '''
        pass

    def focus_out_window(self, widget, event):
        self.quit_dialog_window(widget)

    def __dialog_realize_event(self, widget):
        self.cancel_btn.grab_focus()

    def __dialog_key_release_event(self, widget, e):
        KEY_LEFT  = 65361
        KEY_RIGHT = 65363
        KEY_ESC   = 65307
        if e.keyval == KEY_LEFT:
            self.ok_button.set_check(False)
            self.cancel_button.set_check(True)
            self.cancel_button.grab_focus()
        elif e.keyval == KEY_RIGHT:
            self.ok_button.set_check(True)
            self.cancel_button.set_check(False)
            self.ok_button.grab_focus()
        elif e.keyval == KEY_ESC: # 退出窗口.
            self.quit_dialog_window(widget)

    def __init_settings(self):
        self.set_bg_pixbuf(vtk_theme.get_pixbuf("deepin_on_off_bg", 372))
        self.set_size_request(APP_WIDTH, APP_HEIGHT)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self.set_keep_above(True)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.connect("show", self.show_dialog_window)
        self.connect("focus-out-event", self.focus_out_window)
        self.connect("realize", self.__dialog_realize_event)
        self.connect("key-release-event", self.__dialog_key_release_event)

    def __init_widgets(self):
        self.main_vbox = gtk.VBox()
        self.mid_hbox = gtk.HBox()
        self.show_text_vbox = gtk.VBox()
        self.bottom_hbox_ali = gtk.Alignment(0, 0.5, 1, 0)
        self.bottom_hbox_ali.set_padding(3, 8, 15, 15)
        self.bottom_hbox = gtk.HBox(spacing=30)
        self.bottom_hbox_ali.add(self.bottom_hbox)
        
        self.init_titlebar()
        self.init_close_button()
        self.init_show_image()
        #self.init_show_text()
        self.init_bottom_button()
        
        self.titlebar_hbox.pack_start(self.close_btn, False, False)
        #self.show_text_vbox.pack_start(self.top_text_btn_ali, False, False)
        #self.show_text_vbox.pack_start(self.bottom_text_btn_ali, False, False)
        if LANGUAGE == 'en_US':
            text_size = 9
        else:
            text_size = 10
        self.tick_label = Label("", 
                text_color=DynamicColor("#FFFFFF"), wrap_width=230, text_size=text_size)
        self.show_text_vbox.pack_start(self.tick_label, False, False)

        self.mid_hbox.pack_start(self.show_image_ali, False, False)
        self.mid_hbox.pack_start(self.show_text_vbox, True, True)

        self.bottom_hbox.pack_end(self.ok_btn, False, False)
        self.bottom_hbox.pack_end(self.cancel_btn, False, False)

        self.main_vbox.pack_start(self.titlebar_ali, False, False)
        self.main_vbox.pack_start(self.mid_hbox, True, True)
        self.main_vbox.pack_start(self.bottom_hbox_ali, False, False)
        self.add_widget(self.main_vbox)

    def init_titlebar(self):
        self.titlebar_ali = gtk.Alignment(1, 0, 0, 0)
        self.titlebar_hbox = gtk.HBox()
        self.titlebar_ali.add(self.titlebar_hbox)

    def init_close_button(self):
        # init close button.
        self.close_btn = gtk.Button("x")
        self.close_btn.set_size_request(20, 20)
        self.close_btn.connect("button-press-event", self.close_btn_clicked)
        self.close_btn.connect("expose-event", self.close_btn_expose_event)

    def close_btn_clicked(self, widget, event):
        if event.button == 1:
            self.quit_dialog_window(widget)

    def close_btn_expose_event(self, widget, event):
        return True

    def init_show_image(self):
        size = 20
        left_padding = 10
        padding = (size, size, size + left_padding, size)
        #
        self.show_image_ali = gtk.Alignment(0, 0, 0, 0)
        self.show_image_ali.set_padding(*padding)
        self.show_image = gtk.Image()
        self.show_image_ali.add(self.show_image)
        #
        if self.show_pixbuf:
            self.show_image.set_from_pixbuf(self.show_pixbuf)

    def timer_tick_evnet(self, timer):
        self.second -= 1
        self.tick_label.set_text(self.info_text % self.second)
        if self.second == 0:
            timer.Enabled = False
            self.quit_dialog_window(self)
            if self.run_exec:
                gtk.timeout_add(1, self.run_exec_timeout)

    def init_bottom_button(self):
        self.cancel_btn = gtk.Button(self.cancel_text)
        self.ok_btn = gtk.Button()

        self.cancel_btn.connect("clicked", self.quit_dialog_window)
        self.cancel_btn.connect("expose-event", self.label_expose_event, 30)
        self.cancel_btn.connect("enter-notify-event", self.label_enter_notify_event)

        self.ok_btn.connect("clicked", self.ok_btn_clicked)
        self.ok_btn.connect("expose-event", self.label_expose_event, 0)
        self.ok_btn.connect("enter-notify-event", self.label_enter_notify_event)

    def label_enter_notify_event(self, widget, event):
        self.ok_btn.queue_draw()
        self.cancel_btn.queue_draw()
        if self.ok_btn != widget:
            self.ok_key_check = False
        if self.cancel_btn != widget:
            self.cancel_key_check = False

    def ok_btn_clicked(self, widget):
        if self.run_exec:
            self.run_exec_timeout()
        self.quit_dialog_window(widget)

    def run_exec_timeout(self):
        if self.argv is None:
            self.run_exec()
        else:
            self.run_exec(self.argv)

    def label_expose_event(self, widget, event, width):
        color = self.btn_text_color
        if widget == self.ok_btn and self.ok_key_check:
            color = "#FFFFFF"
        elif widget == self.cancel_btn and self.cancel_key_check:
            color = "#FFFFFF"

        if widget.state == gtk.STATE_PRELIGHT:
            color = "#FFFFFF"
        
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        size = get_text_size(widget.get_label(), 
                             self.btn_text_size, 
                             DEFAULT_FONT)
        draw_text(cr, 
                  widget.get_label(),
                  rect.x, 
                  rect.y + rect.height/2 - size[1]/2, 
                  text_size=self.btn_text_size, 
                  text_color=color, 
                  text_font=DEFAULT_FONT)  
        widget.set_size_request(size[0] + width, size[1] + 10)
        
        return True

    def quit_dialog_window(self, widget):
        for alpha in range(10, -1, -1):
            self.set_opacity(alpha * 0.1)
        self.hide_all()
        self.timer.Enabled = False
        self.grab_remove()

        if hasattr(self, "quit_alone"):
            gtk.main_quit()

class BottomButton(gtk.Button):
    def __init__(self, label="", label_size=DEFAULT_FONT_SIZE):
        gtk.Button.__init__(self, label)

        self.btn_text = label
        self.btn_text_size = label_size

        size = get_text_size(label, label_size, DEFAULT_FONT)
        self.set_size_request(*size)
        self.btn_text_color = "#b9b9b9"
        self.check = False

        self.connect("expose-event", self.expose)

    def expose(self, widget, event):
        if self.check:
            color = "#FFFFFF"
        else:
            color = self.btn_text_color

        if widget.state == gtk.STATE_PRELIGHT:
            color = "#FFFFFF"
        
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        draw_text(cr, 
                  widget.get_label(),
                  rect.x, 
                  rect.y, 
                  text_size=self.btn_text_size, 
                  text_color=color, 
                  text_font=DEFAULT_FONT)  
        return True

    def set_check(self, check):
        self.check = check
        self.queue_draw()
