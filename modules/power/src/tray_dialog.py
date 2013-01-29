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

import gtk
from vtk.window import Window
from vtk.utils import cn_check, get_text_size, in_window_check 
from vtk.draw import draw_text
from vtk.theme import vtk_theme
from vtk.timer import Timer

APP_WIDTH = 375
APP_HEIGHT = 169

class TrayDialog(Window):
    def __init__(self,
                 show_pixbuf_name="deepin_shutdown",
                 show_top_text="现在关闭此系统吗？",
                 show_bottom_text="系统即将在%s秒后自动关闭。",
                 cancel_text="取消",
                 ok_text="确认"):
        Window.__init__(self,type=gtk.WINDOW_POPUP)
        # init values.
        self.show_pixbuf = vtk_theme.get_pixbuf(show_pixbuf_name, 50)
        self.show_top_text = show_top_text
        self.show_bottom_text = show_bottom_text
        self.top_text_color = "#FFFFFF"
        self.bottom_text_color = "#b9b9b9"
        self.cancel_text = cancel_text
        self.cancel_size = 14
        self.cancel_color = "#FFFFFF"
        self.cancel_font = "文泉驿微米黑 Bold"
        self.ok_text = ok_text
        # init time.
        self.timer = Timer(1000)
        self.second = 60
        self.timer.Enabled = True
        self.timer.connect("Tick", self.timer_tick_evnet)
        #
        self.run_exec = None
        #
        self.__init_widgets()
        self.__init_settings()
        
    def show_dialog_window(self, widget):
        for alpha in range(0, 11):
            self.set_opacity(alpha * 0.1)
        
    def show_dialog(self,
                    show_pixbuf_name="deepin_shutdown",
                    show_top_text="现在关闭此系统吗？",
                    show_bottom_text="系统即将在%s秒后自动关闭。",
                    cancel_text="取消",
                    ok_text="确认"):
        self.show_pixbuf = vtk_theme.get_pixbuf(show_pixbuf_name, 50)
        self.show_top_text = show_top_text
        self.show_bottom_text = show_bottom_text
        self.cancel_text = cancel_text
        self.ok_text = ok_text
        self.second = 60
        #
        self.top_text_btn.set_label(self.show_top_text)
        self.bottom_text_btn.set_label(self.show_bottom_text)
        if self.show_pixbuf:
            self.show_image.set_from_pixbuf(self.show_pixbuf)
        self.bottom_text_btn.set_label(self.show_bottom_text % (self.second))	
        self.bottom_text_btn.queue_draw()
        self.timer.Enabled = True
        self.show_all()
        self.trayicon_show_event()
            
    def trayicon_show_event(self):
        gtk.gdk.pointer_grab(
            self.window,
            True,
            gtk.gdk.POINTER_MOTION_MASK
            | gtk.gdk.BUTTON_PRESS_MASK
            | gtk.gdk.BUTTON_RELEASE_MASK
            | gtk.gdk.ENTER_NOTIFY_MASK
            | gtk.gdk.LEAVE_NOTIFY_MASK,
            None,
            None,
            gtk.gdk.CURRENT_TIME)
        self.grab_add()        

    def button_press_window(self, widget, event):
        if in_window_check(widget, event):
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
        self.connect("button-press-event", self.button_press_window) 

    def __init_widgets(self):
        self.main_vbox = gtk.VBox()
        self.mid_hbox = gtk.HBox()
        self.show_text_vbox = gtk.VBox()
        self.bottom_hbox_ali = gtk.Alignment(1, 0, 0, 0)
        self.bottom_hbox_ali.set_padding(0, 3, 0, 15)
        self.bottom_hbox = gtk.HBox()
        self.bottom_hbox_ali.add(self.bottom_hbox)
        #
        self.init_titlebar()
        self.init_close_button()
        self.init_show_image()
        self.init_show_text()
        self.init_bottom_button()
        #
        self.titlebar_hbox.pack_start(self.close_btn, False, False)
        self.show_text_vbox.pack_start(self.top_text_btn_ali, False, False)
        self.show_text_vbox.pack_start(self.bottom_text_btn_ali, False, False)
        self.mid_hbox.pack_start(self.show_image_ali, False, False)
        self.mid_hbox.pack_start(self.show_text_vbox, True, True)
        self.bottom_hbox.pack_start(self.cancel_btn, False, False)
        self.bottom_hbox.pack_start(self.ok_btn, False, False)
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
        padding = (size, size, size, size)
        #
        self.show_image_ali = gtk.Alignment(0, 0, 1, 1)
        self.show_image_ali.set_padding(*padding)
        self.show_image = gtk.Image()
        self.show_image_ali.add(self.show_image)
        #
        if self.show_pixbuf:
            self.show_image.set_from_pixbuf(self.show_pixbuf)

    def init_show_text(self):
        self.top_text_btn_ali = gtk.Alignment()
        self.top_text_btn_ali.set_padding(20, 0, 0, 0)
        self.top_text_btn = gtk.Button(self.show_top_text)
        self.top_text_btn_ali.add(self.top_text_btn)
        self.bottom_text_btn_ali = gtk.Alignment()
        self.bottom_text_btn = gtk.Button(self.show_bottom_text % (self.second))
        self.bottom_text_btn_ali.add(self.bottom_text_btn)
        #
        self.top_text_btn.connect("expose-event", 
                     self.top_text_btn_expose_event, self.top_text_color)
        self.bottom_text_btn.connect("expose-event", 
                     self.top_text_btn_expose_event, self.bottom_text_color)

    def timer_tick_evnet(self, timer):
        self.bottom_text_btn.set_label(self.show_bottom_text % (self.second))
        self.bottom_text_btn.queue_draw()
        if self.second == 0:
            timer.Enabled = False
            self.quit_dialog_window(self)
            if self.run_exec:
                gtk.timeout_add(1, self.run_exec_timeout)
        self.second -= 1

    def top_text_btn_expose_event(self, widget, event, font_color):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        #
        font_size = 12
        if cn_check():
            font_size = 14
        size = get_text_size(widget.get_label(), font_size)
        #
        draw_text(cr, 
                  widget.get_label(),
                  rect.x,
                  rect.y + rect.height/2 - size[1]/2,
                  font_size,
                  font_color)
        widget.set_size_request(size[0] + 10, size[1] + 4)
        return True

    def init_bottom_button(self):
        self.cancel_btn = gtk.Button(self.cancel_text)
        self.ok_btn = gtk.Button(self.ok_text)
        #
        self.cancel_btn.connect("clicked", self.quit_dialog_window)
        self.cancel_btn.connect("expose-event", self.label_expose_event)
        self.ok_btn.connect("clicked", self.ok_btn_clicked)
        self.ok_btn.connect("expose-event", self.label_expose_event)

    def ok_btn_clicked(self, widget):
        self.quit_dialog_window(widget)
        if self.run_exec:
            gtk.timeout_add(1, self.run_exec_timeout)

    def run_exec_timeout(self):
        self.run_exec()

    def label_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        #
        size = get_text_size(widget.get_label(), 
                             self.cancel_size, 
                             self.cancel_font)
        draw_text(cr, 
                  widget.get_label(),
                  rect.x + rect.width/2 - size[0]/2, 
                  rect.y + rect.height/2 - size[1]/2, 
                  self.cancel_size, 
                  self.cancel_color, 
                  self.cancel_font)  
        widget.set_size_request(size[0] + 10, size[1] + 10)
        #
        return True

    def quit_dialog_window(self, widget):
        for alpha in range(10, -1, -1):
            self.set_opacity(alpha * 0.1)
        self.hide_all()
        self.timer.Enabled = False
        self.grab_remove()
        

'''
#@ show_pixbuf_name="deepin_restart"
#@ show_top_text="现在关闭此系统吗？"
#@ show_bottom_text="系统即将在60秒后自动关闭。"
#@ cancel_text="取消"
#@ ok_text="确认"
#@ run_exec
'''

if __name__ == "__main__":
    def test_run():
        print "i love c and linux..."

    dialog = TrayDialog("deepin_shutdown", 
                        cancel_text="Cancel", 
                        ok_text="Ok")
    dialog.run_exec = test_run
    gtk.main()
