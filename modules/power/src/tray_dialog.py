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
import pango
from nls import _
from vtk.window import Window
from vtk.utils import get_text_size
from vtk.draw import draw_text
from vtk.theme import vtk_theme
from vtk.timer import Timer
from dtk.ui.draw import draw_text as dtk_draw_text
from dtk.ui.constant import DEFAULT_FONT, DEFAULT_FONT_SIZE
from dtk.ui.label import Label
import inhibit


APP_WIDTH = 375
APP_HEIGHT = 169
CANCEL_TEXT = _("Cancel")
OK_TEXT = _("OK")
#SHUTDOWN_TOP_TEXT = _("现在关闭此系统吗？")
SHUTDOWN_TOP_TEXT = _("<span foreground='#FF0000'>Turn off</span> your computer now?,12")
#SHUTDOWN_BOTTOM_TEXT = _("系统即将在%s秒后自动关闭。")
SHUTDOWN_BOTTOM_TEXT = _("The system will shut down in \n%s secs.,12")
#FONT_TYPE = _("文泉驿微米黑 Bold")
FONT_TYPE = _("WenQuanYi Micro Hei Bold")

EN_RED_TEXT = {"Turn off your computer now?":(0, 9), 
               "Restart your computer now?":(0, 7), 
               "Suspend your computer now?":(0, 7), 
               "Logout your computer now?":(0, 5)} 

class TrayDialog(Window):
    def __init__(self,
                 show_pixbuf_name="deepin_shutdown",
                 show_top_text=SHUTDOWN_TOP_TEXT,
                 show_bottom_text=SHUTDOWN_BOTTOM_TEXT,
                 cancel_text=CANCEL_TEXT,
                 ok_text=OK_TEXT):
        Window.__init__(self)
        # init values.
        self.show_pixbuf = vtk_theme.get_pixbuf(show_pixbuf_name, 50)
        self.show_top_text = show_top_text
        self.show_bottom_text = show_bottom_text
        self.top_text_color = "#FFFFFF"
        self.bottom_text_color = "#b9b9b9"
        self.cancel_text = cancel_text
        self.cancel_size = 12
        self.cancel_color = "#b9b9b9"
        self.cancel_font = FONT_TYPE
        self.ok_text = ok_text
        self.draw_rectangle_bool = False
        # init time.
        self.timer = Timer(1000)
        self.second = 60
        self.timer.Enabled = False
        self.timer.connect("Tick", self.timer_tick_evnet)
        #
        self.run_exec = None
        self.argv = None
        self.set_pango_list()
        self.ok_key_check = False
        self.cancel_key_check = False
        #
        self.__init_widgets()
        self.__init_settings()
        
    def show_dialog_window(self, widget):
        for alpha in range(0, 11):
            self.set_opacity(alpha * 0.1)
        self.ok_key_check = True
        self.cancel_key_check = False
        self.ok_btn.grab_focus()

    def show_warning(self,
                    show_top_text=SHUTDOWN_TOP_TEXT,
                    show_bottom_text=SHUTDOWN_BOTTOM_TEXT,
                    cancel_text=CANCEL_TEXT,
                    ok_text=OK_TEXT,
                    ):
        self.show_pixbuf = vtk_theme.get_pixbuf("deepin_warning", 50)
        self.show_top_text = show_top_text
        self.show_bottom_text = show_bottom_text
        self.cancel_text = cancel_text
        self.ok_text = ok_text
        self.argv = None
        self.run_exec = None
        
        self.set_pango_list()
        
        self.top_text_btn.set_label(self.show_top_text)
        self.bottom_text_btn.set_label(self.show_bottom_text)
        if self.show_pixbuf:
            self.show_image.set_from_pixbuf(self.show_pixbuf)
        self.bottom_text_btn.set_label(self.show_bottom_text)
        self.bottom_text_btn.queue_draw()
        self.timer.Enabled = False
        self.show_all()

    def show_dialog(self,
                    show_pixbuf_name="deepin_shutdown",
                    show_top_text=SHUTDOWN_TOP_TEXT,
                    show_bottom_text=SHUTDOWN_BOTTOM_TEXT,
                    cancel_text=CANCEL_TEXT,
                    ok_text=OK_TEXT,
                    ):
        self.show_pixbuf = vtk_theme.get_pixbuf(show_pixbuf_name, 50)
        self.show_top_text = show_top_text
        self.show_bottom_text = show_bottom_text
        self.cancel_text = cancel_text
        self.ok_text = ok_text
        self.second = 60
        self.argv = None
        self.run_exec = None
        
        self.set_pango_list()
        
        self.top_text_btn.set_label(self.show_top_text)
        self.bottom_text_btn.set_label(self.show_bottom_text)
        if self.show_pixbuf:
            self.show_image.set_from_pixbuf(self.show_pixbuf)
        self.bottom_text_btn.set_label(self.show_bottom_text % (self.second))	
        self.bottom_text_btn.queue_draw()
        self.timer.Enabled = True
        self.show_all()
        self.default_action_btn.hide()

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
        self.ok_btn.grab_focus()

    def __dialog_key_release_event(self, widget, e):
        KEY_LEFT  = 65361
        KEY_RIGHT = 65363
        KEY_ESC   = 65307
        if e.keyval == KEY_LEFT:
            self.ok_key_check = False
            self.cancel_key_check = True
            self.cancel_btn.grab_focus()
        elif e.keyval == KEY_RIGHT:
            self.ok_key_check = True
            self.cancel_key_check = False
            self.ok_btn.grab_focus()
        elif e.keyval == KEY_ESC: # 退出窗口.
            self.quit_dialog_window(widget)

        if e.keyval in [KEY_LEFT, KEY_RIGHT]:
            self.ok_btn.queue_draw()
            self.cancel_btn.queue_draw()

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
        self.bottom_hbox_ali.set_padding(3, 3, 15, 15)
        self.bottom_hbox = gtk.HBox()
        self.bottom_hbox_ali.add(self.bottom_hbox)
        
        self.init_titlebar()
        self.init_close_button()
        self.init_show_image()
        self.init_show_text()
        self.init_bottom_button()
        
        self.titlebar_hbox.pack_start(self.close_btn, False, False)
        self.show_text_vbox.pack_start(self.top_text_btn_ali, False, False)
        self.show_text_vbox.pack_start(self.bottom_text_btn_ali, False, False)

        self.mid_hbox.pack_start(self.show_image_ali, False, False)
        self.mid_hbox.pack_start(self.show_text_vbox, True, True)

        self.bottom_hbox.pack_start(self.default_action_btn, False, False)
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

    def init_show_text(self):
        top_padding = 25
        self.top_text_btn_ali = gtk.Alignment()
        self.top_text_btn_ali.set_padding(top_padding + 3, 8, 0, 0)
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
        text_list = widget.get_label().split(",")
        text = text_list[0]
        font_size = text_list[1]
        #
        size = get_text_size(text, font_size)
        size_padding = get_text_size("a", font_size)
        size_padding = size_padding[0] * 35
        #
        draw_text(cr, 
                  text,
                  rect.x,
                  rect.y + rect.height/2 - size[1]/2,
                  font_size,
                  font_color,
                  markup=text)
        # 
        widget.set_size_request(size[0], size[1])
        return True

    def init_bottom_button(self):
        self.cancel_btn = gtk.Button(self.cancel_text)
        self.ok_btn = gtk.Button(self.ok_text)

        self.default_action_btn = gtk.Button("强制执行")

        self.cancel_btn.connect("clicked", self.quit_dialog_window)
        self.cancel_btn.connect("expose-event", self.label_expose_event, 30)
        self.cancel_btn.connect("enter-notify-event", self.label_enter_notify_event)

        self.ok_btn.connect("clicked", self.ok_btn_clicked)
        self.ok_btn.connect("expose-event", self.label_expose_event, 0)
        self.ok_btn.connect("enter-notify-event", self.label_enter_notify_event)

        self.default_action_btn.connect("expose-event", self.label_expose_event, 0)
        self.default_action_btn.connect("clicked", self.default_action_btn_clicked)
        self.default_action_btn.connect("enter-notify-event", self.label_enter_notify_event)

    def label_enter_notify_event(self, widget, event):
        self.ok_btn.queue_draw()
        self.cancel_btn.queue_draw()
        if self.ok_btn != widget:
            self.ok_key_check = False
        if self.cancel_btn != widget:
            self.cancel_key_check = False

    def ok_btn_clicked(self, widget):
        self.quit_dialog_window(widget)
        if self.run_exec:
            gtk.timeout_add(1, self.run_exec_timeout)

    def default_action_btn_clicked(self, widget):
        pass

    def run_exec_timeout(self):
        if self.argv is None:
            self.run_exec()
        else:
            self.run_exec(self.argv)

    def label_expose_event(self, widget, event, width):
        color = self.cancel_color
        if widget == self.ok_btn and self.ok_key_check:
            color = "#FFFFFF"
        elif widget == self.cancel_btn and self.cancel_key_check:
            color = "#FFFFFF"

        if widget.state == gtk.STATE_PRELIGHT:
            color = "#FFFFFF"
        
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        size = get_text_size(widget.get_label(), 
                             self.cancel_size, 
                             self.cancel_font)
        draw_text(cr, 
                  widget.get_label(),
                  rect.x, 
                  rect.y + rect.height/2 - size[1]/2, 
                  text_size=self.cancel_size, 
                  text_color=color, 
                  text_font=self.cancel_font)  
        widget.set_size_request(size[0] + width, size[1] + 10)
        
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


class InhibitDialog(TrayDialog):
    def __init__(self, ok_text=OK_TEXT, cancel_text=CANCEL_TEXT):
        super(InhibitDialog, self).__init__(cancel_text=cancel_text, ok_text=ok_text)
        self.show_top_text = "<span foreground='#FF0000'>%s</span>" % _("A program is still running:")
        self.show_bottom_text = _("Waiting for applications to terminate. Interrupting these may cause unexpected results.")
        self.wrap_width = 320

        # remove image and title
        self.show_image_ali.destroy()
        #self.titlebar_ali.destroy()

        # text
        self.mid_hbox.remove(self.show_text_vbox)
        show_text_align = gtk.Alignment(0.5, 0, 0, 0)
        show_text_align.set_padding(0, 0, 5, 5)
        show_text_align.add(self.show_text_vbox)
        self.mid_hbox.pack_start(show_text_align, True, True)

        self.top_text_btn_ali.set_padding(0, 3, 0, 0)
        self.bottom_text_btn_ali.set_padding(3, 0, 0, 0)

        inhibit_vbox = gtk.VBox(True)
        inhibit_vbox.set_size_request(-1, 40)
        self.inhibit_app_label = Label(label_width=320)
        self.inhibit_reason_label = Label(label_width=320)
        inhibit_vbox.pack_start(self.inhibit_app_label, False, False)
        inhibit_vbox.pack_start(self.inhibit_reason_label, False, False)
        self.show_text_vbox.pack_start(inhibit_vbox, False, False)
        self.show_text_vbox.reorder_child(inhibit_vbox, 1)
        #self.set_size_request(APP_WIDTH, 200)

    def show_dialog(self, cancel_text=CANCEL_TEXT, ok_text=OK_TEXT):
        self.cancel_text = cancel_text
        self.ok_text = ok_text
        self.cancel_btn.set_label(cancel_text)
        self.ok_btn.set_label(ok_text)
        self.argv = None
        self.run_exec = None
        self.set_pango_list()
        self.top_text_btn.set_label(self.show_top_text)
        self.bottom_text_btn.set_label(self.show_bottom_text)
        w, h = self.get_text_size(self.show_top_text, self.wrap_width)
        if h > 15: h = 15
        self.top_text_btn.set_size_request(w, h)
        w, h = self.get_text_size(self.show_bottom_text, self.wrap_width)
        if h > 30: h = 30
        self.bottom_text_btn.set_size_request(w, h)

        self.init_inhibit_list()
        self.show_all()

    def focus_out_window(self, widget, event=None):
        pass

    def top_text_btn_expose_event(self, widget, event, color):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        text = widget.get_label()
        dtk_draw_text(cr, text, rect.x, rect.y,
                      rect.width, rect.height,
                      text_color=color, wrap_width=self.wrap_width)
        return True

    def get_text_size(self, text, wrap_width,
                      text_size=DEFAULT_FONT_SIZE,
                      text_font=DEFAULT_FONT):
        try:
            layout = self.create_pango_layout(" ")
            layout.set_wrap(pango.WRAP_WORD_CHAR)
            layout.set_width(wrap_width*pango.SCALE)
            layout.get_pixel_size()

            temp_font = pango.FontDescription("%s %s" % (text_font, text_size))
            layout.set_font_description(temp_font)
            layout.set_markup(text)
            return layout.get_pixel_size()
        except:
            return (-1, -1)

    def __inhibit_added_cb(self, path):
        if path not in self.__inhibit_dict:
            self.__inhibit_dict[path] = inhibit.get_inhibit_info(path)
            self.__inhibit_list.append(path)

    def __inhibit_removed_cb(self, path):
        if path in self.__inhibit_dict:
            del self.__inhibit_dict[path]
            self.__inhibit_list.remove(path)
        if self.__inhibit_list:
            self.inhibit_app_label.set_text(
                "<b><span foreground='#FFFFFF'>%s</span></b>" % self.__inhibit_dict[self.__inhibit_list[0]][0])
            self.inhibit_reason_label.set_text(
                "<span foreground='#FFFFFF'>%s</span>" % self.__inhibit_dict[self.__inhibit_list[0]][1])
        if not self.__inhibit_list:
            self.ok_btn_clicked(None)

    def init_inhibit_list(self):
        self.__inhibit_dict = {}
        self.__inhibit_list = []
        for path in inhibit.get_inhibis():
            self.__inhibit_dict[path] = inhibit.get_inhibit_info(path)
            self.__inhibit_list.append(path)
        if self.__inhibit_list:
            self.inhibit_app_label.set_text(
                "<b><span foreground='#FFFFFF'>%s</span></b>" % self.__inhibit_dict[self.__inhibit_list[0]][0])
            self.inhibit_reason_label.set_text(
                "<span foreground='#FFFFFF'>%s</span>" % self.__inhibit_dict[self.__inhibit_list[0]][1])

        print self.__inhibit_dict
        inhibit.gs_bus.add_signal_receiver(
            self.__inhibit_removed_cb,
            dbus_interface="org.gnome.SessionManager",
            path="/org/gnome/SessionManager",
            signal_name="InhibitorRemoved")
        inhibit.gs_bus.add_signal_receiver(
            self.__inhibit_added_cb,
            dbus_interface="org.gnome.SessionManager",
            path="/org/gnome/SessionManager",
            signal_name="InhibitorAdded")

    def __treeview_draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgba(0.32, 0.4, 0.4, 0.3)
        cr.rectangle(x, y, w, h)
        cr.fill()


if __name__ == "__main__":
    def test_run():
        print "i love c and linux..."

    dialog = TrayDialog("deepin_shutdown", 
                        cancel_text="Cancel", 
                        ok_text="Ok")
    dialog.set_bg_pixbuf(gtk.gdk.pixbuf_new_from_file('/usr/share/deepin-system-tray/src/image/on_off_dialog/deepin_on_off_bg.png'))
    dialog.run_exec = test_run
    dialog.show_all()
    gtk.main()
