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

from nls import _
from theme import app_theme
from dtk.ui.label import Label
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.menu import Menu
from dtk.ui.utils import color_hex_to_cairo, cairo_disable_antialias
from icon_button import IconButton
from constant import *
from utils import AccountsPermissionDenied, AccountsUserDoesNotExist, AccountsUserExists, AccountsFailed
import gtk
import tools
import os
from stat import S_IRWXU, S_IRWXG, S_IRWXO

MODULE_NAME = "account"

class HistroyIcon(object):
    def __init__(self, account_setting):
        super(HistroyIcon, self).__init__()
        self.account_setting = account_setting
        self.cfg_dir = os.path.join(self.account_setting.get_home_directory(), ".config/deepin-system-settings")
        self.cfg_file = os.path.join(self.cfg_dir, "icon_histroy")
        if not os.path.exists(self.cfg_dir):
            try:
                os.makedirs(self.cfg_dir)
            except:
                pass
        if not os.path.exists(self.cfg_file):
            try:
                open(self.cfg_file, 'w').close()
                os.chmod(self.cfg_file, S_IRWXU|S_IRWXG|S_IRWXO)
            except:
                pass

    def get_histroy(self):
        self.histroy = []
        try:
            f = open(self.cfg_file, 'r')
        except:
            return self.histroy
        lines = f.readlines()
        f.close()
        for l in lines:
            line = l.strip(os.linesep)
            if os.path.exists(line) and not line in self.histroy:
                self.histroy.append(line)
        return self.histroy

    def set_histroy(self, histroy):
        try:
            f = open(self.cfg_file, 'w')
        except:
            return
        for line in histroy:
            f.write("%s%s" % (line, os.linesep))
        f.close()

class IconSetPage(gtk.VBox):
    def __init__(self, account_setting):
        super(IconSetPage, self).__init__(False)
        #self.set_spacing(BETWEEN_SPACING)
        self.account_setting = account_setting

        self.choose_menu = Menu([(None, "从本地文件", self.choose_from_picture), (None, "使用深度截图", self.choose_from_screenshot)], True)
        self.tips_label = Label("Set icon", text_size=13, label_width=460, enable_select=False)
        self.error_label = Label("", wrap_width=560, enable_select=False)
        self.pack_start(tools.make_align(self.tips_label), False, False)
        self.pack_start(tools.make_align(height=20), False, False)

        icon_list_sw = ScrolledWindow()
        icon_list_sw.set_size_request(600, 70)
        self.icon_list_hbox = gtk.HBox(False)
        icon_list_sw.add_child(tools.make_align(self.icon_list_hbox, yalign=0.0, height=-1))
        self.icon_list_hbox.get_parent().connect("expose-event", self.draw_white_background)

        histroy_list_sw = ScrolledWindow()
        icon_list_sw.set_size_request(600, 70)
        self.histroy_list_hbox = gtk.HBox(False)
        self.histroy_list_hbox.set_size_request(-1, 70)
        histroy_list_sw.add_child(tools.make_align(self.histroy_list_hbox, yalign=0.0, height=-1))
        self.histroy_list_hbox.get_parent().connect("expose-event", self.draw_white_background)

        self.pack_start(tools.make_align(Label(_("选择用户头像")), height=CONTAINNER_HEIGHT), False, False)
        self.pack_start((icon_list_sw), False, False)
        self.pack_start(tools.make_align(height=20), False, False)

        self.pack_start(tools.make_align(Label(_("历史使用头像")), height=CONTAINNER_HEIGHT), False, False)
        self.pack_start((histroy_list_sw), False, False)
        self.pack_start(tools.make_align(height=20), False, False)

        self.pack_start(tools.make_align(self.error_label), False, False)

        face_dir = '/usr/share/pixmaps/faces'
        if os.path.exists(face_dir):
            pic_list = os.listdir(face_dir)
        else:
            pic_list = []
        for pic in pic_list:
            try:
                icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                    "%s/%s" %(face_dir, pic)).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
            except:
                continue
            icon_bt = IconButton(icon_pixbuf, "%s/%s" %(face_dir, pic))
            icon_bt.connect("pressed", self.on_icon_bt_pressed_cb)
            self.icon_list_hbox.pack_start(icon_bt, False, False)
        more_button = IconButton(app_theme.get_pixbuf("%s/more.png" % MODULE_NAME).get_pixbuf())
        more_button.connect("button-press-event", self.choose_more_picture)
        self.icon_list_hbox.pack_start(more_button, False, False)

        self.connect("expose-event", self.draw_frame_border, icon_list_sw, histroy_list_sw)

    def refresh(self):
        self.error_label.set_text("")
        if not self.account_setting.current_set_user:
            return
        if self.account_setting.current_set_user.get_real_name():
            show_name = self.account_setting.current_set_user.get_real_name()
        else:
            show_name = self.account_setting.current_set_user.get_user_name()
        self.tips_label.set_text("<b>%s</b>" % _("Set <u>%s</u>'s icon") % tools.escape_markup_string(show_name))
        self.histroy_icon = HistroyIcon(self.account_setting.current_set_user)
        self.histroy_icon.get_histroy()
        self.histroy_list_hbox.foreach(lambda w: w.destroy())
        for pic in self.histroy_icon.histroy:
            if not os.path.exists(pic):
                continue
            try:
                icon_pixbuf = gtk.gdk.pixbuf_new_from_file(pic).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
            except Exception, e:
                print e
                continue
            icon_bt = IconButton(icon_pixbuf, pic, can_del=True)
            icon_bt.connect("pressed", self.on_icon_bt_pressed_cb)
            icon_bt.connect("del-pressed", self.on_icon_bt_del_pressed_cb)
            self.histroy_list_hbox.pack_start(icon_bt, False, False)
        self.histroy_list_hbox.show_all()

    def on_icon_bt_del_pressed_cb(self, widget):
        try:
            file_path = widget.get_image_path()
            if file_path in self.histroy_icon.histroy:
                self.histroy_icon.histroy.remove(file_path)
                self.histroy_icon.set_histroy(self.histroy_icon.histroy)
            widget.destroy()
        except Exception, e:
            print e
        
    def on_icon_bt_pressed_cb(self, widget):
        try:
            file_path = widget.get_image_path()
            self.account_setting.current_set_user.set_icon_file(file_path)
            if not file_path in self.histroy_icon.histroy:
                self.histroy_icon.histroy.append(file_path)
                self.histroy_icon.set_histroy(self.histroy_icon.histroy)
        except Exception, e:
            print e
            if isinstance(e, (AccountsPermissionDenied, AccountsUserExists, AccountsFailed, AccountsUserDoesNotExist)):
                self.error_label.set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), e.msg))
            return
        self.account_setting.container_widgets["slider"].slide_to_page(
            self.account_setting.alignment_widgets["main_hbox"], "left")
        self.account_setting.change_crumb(1)

    def choose_more_picture(self, widget, event):
        x = int(event.x_root - event.x)
        y = int(event.y_root - event.y + widget.allocation.height)
        self.choose_menu.show((x, y))

    def choose_from_picture(self):
        file_filter = gtk.FileFilter()
        file_filter.add_pixbuf_formats()
        f = gtk.FileChooserDialog(buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
        f.set_filter(file_filter)
        response = f.run()
        filename = f.get_filename()
        f.destroy()
        if response != gtk.RESPONSE_ACCEPT:
            return
        try:
            # TODO 切换到剪辑页面
            self.account_setting.current_set_user.set_icon_file(filename)
        except Exception, e:
            print e
            if isinstance(e, (AccountsPermissionDenied, AccountsUserExists, AccountsFailed, AccountsUserDoesNotExist)):
                self.error_label.set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), e.msg))
            return
        self.account_setting.container_widgets["slider"].slide_to_page(
            self.account_setting.alignment_widgets["main_hbox"], "left")
        self.account_setting.change_crumb(1)

    def choose_from_screenshot(self):
        pass

    def draw_white_background(self, widget, event):
        x, y, w, h = widget.allocation
        cr = widget.window.cairo_create()
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))
        cr.rectangle(x, y, w, h)
        cr.paint()

    def draw_frame_border(self, widget, event, sw1, sw2):
        x, y, w, h = sw1.allocation
        cr = widget.window.cairo_create()
        cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
        cr.rectangle(x, y, w, h)
        cr.stroke()
        x, y, w, h = sw2.allocation
        cr = widget.window.cairo_create()
        cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
        cr.rectangle(x, y, w, h)
        cr.stroke()
