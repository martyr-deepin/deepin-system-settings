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
from dtk.ui.utils import color_hex_to_cairo, container_remove_all
from icon_button import IconButton
from webcam import Webcam
from constant import *
from account_utils import AccountsPermissionDenied, AccountsUserDoesNotExist, AccountsUserExists, AccountsFailed
import gtk
import gobject
import tools
import os
import dbus
import md5
from time import sleep
from subprocess import Popen
from stat import S_IRWXU, S_IRWXG, S_IRWXO, S_IWUSR, S_IWGRP, S_IWOTH

MODULE_NAME = "account"


def get_file_md5(file_name):
    fp = open(file_name, 'rb')
    m = md5.new()
    while True:
        d = fp.read(8096)
        if not d:
            break
        m.update(d)
    fp.close()
    return m.hexdigest()

def check_file_writable(file_path):
    if not os.path.exists(file_path):
        return False
    file_st = os.stat(file_path)
    st_mode = file_st.st_mode
    if file_st.st_uid != os.getuid():
        return False
    if file_st.st_uid == os.getuid() and st_mode & S_IWUSR:
        return True
    if file_st.st_gid in os.getgroups() and st_mode & S_IWGRP:
        return True
    if st_mode & S_IWOTH:
        return True
    return False

class HistroyIcon(object):
    def __init__(self, account_setting):
        super(HistroyIcon, self).__init__()
        self.account_setting = account_setting
        self.cfg_dir = os.path.join(self.account_setting.get_home_directory(), ".config/deepin-system-settings/account")
        self.icons_dir = self.cfg_dir+"/icons"
        self.cfg_file = os.path.join(self.cfg_dir, "account_icon_history")
        if not os.path.exists(self.cfg_dir):
            try:
                os.makedirs(self.cfg_dir)
            except:
                pass
        if not os.path.exists(self.icons_dir):
            try:
                os.makedirs(self.icons_dir)
            except Exception, e:
                print e
                pass
        if not os.path.exists(self.cfg_file):
            try:
                open(self.cfg_file, 'w').close()
                os.chmod(self.cfg_file, S_IRWXU|S_IRWXG|S_IRWXO)
            except:
                pass

    def get_history(self):
        self.history = []
        try:
            f = open(self.cfg_file, 'r')
        except:
            return self.history
        lines = f.readlines()
        f.close()
        for l in lines:
            line = l.strip(os.linesep)
            if os.path.exists(line) and not line in self.history:
                self.history.append(line)
        return self.history

    def set_history(self, history):
        try:
            f = open(self.cfg_file, 'w')
        except:
            return
        for line in history:
            f.write("%s%s" % (line, os.linesep))
        f.close()

class IconSetPage(gtk.VBox):
    def __init__(self, account_setting):
        super(IconSetPage, self).__init__(False)
        #self.set_spacing(BETWEEN_SPACING)
        self.account_setting = account_setting

        self.choose_menu_without_camera = Menu(
            [(None, _("Local picture"), self.choose_from_picture), (None, _("Take a screeshot"), self.choose_from_screenshot),], True)
        self.choose_menu_with_camera = Menu(
            [(None, _("Local picture"), self.choose_from_picture),
             (None, _("Take a screeshot"), self.choose_from_screenshot),
             (None, _("From camera"), self.choose_from_camera)], True)
        self.tips_label = Label("Set icon", label_width=460, enable_select=False, enable_double_click=False)
        self.error_label = Label("", wrap_width=560, enable_select=False, enable_double_click=False)

        set_page_sw = ScrolledWindow()
        self.pack_start(set_page_sw)
        main_vbox = gtk.VBox(False)
        set_page_sw.add_child(main_vbox)
        self.icon_list_tabel = gtk.Table()
        self.icon_list_tabel.set_row_spacings(4)
        self.icon_list_tabel.set_col_spacings(4)
        main_vbox.pack_start(tools.make_align(self.tips_label), False, False)
        main_vbox.pack_start(tools.make_align(height=20), False, False)

        self.history_list_hbox = gtk.HBox(False)
        self.history_list_hbox.set_size_request(-1, 56)
        self.history_list_hbox.set_spacing(4)

        main_vbox.pack_start(tools.make_align(Label(_("Choose a new picture for your account"), enable_select=False, enable_double_click=False), height=CONTAINNER_HEIGHT), False, False)
        main_vbox.pack_start(tools.make_align(self.icon_list_tabel), False, False)
        main_vbox.pack_start(tools.make_align(height=20), False, False)

        main_vbox.pack_start(tools.make_align(Label(_("Previously used pictures"), enable_select=False, enable_double_click=False), height=CONTAINNER_HEIGHT), False, False)
        main_vbox.pack_start(tools.make_align(self.history_list_hbox), False, False)
        main_vbox.pack_start(tools.make_align(height=20), False, False)

        main_vbox.pack_start(tools.make_align(self.error_label), False, False)

        # public picture list
        #face_dir = '/usr/share/pixmaps/faces'
        face_dir = '/var/lib/AccountsService/icons'
        if os.path.exists(face_dir):
            pic_list = os.listdir(face_dir)
        else:
            pic_list = []
        pic_list.sort()
        self.public_icon_list = []
        inital_list = ['001.jpg', '002.jpg', '003.jpg', '004.jpg', '005.jpg',
                       '006.jpg', '007.jpg', '008.jpg', '009.jpg', '010.jpg',
                       '011.jpg', '012.jpg', '013.jpg', '014.jpg', '015.jpg',
                       '016.jpg', '017.jpg', '018.jpg', '019.jpg', '020.jpg']

        for pic in pic_list:
            if pic not in inital_list:
                continue
            try:
                icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                    "%s/%s" %(face_dir, pic)).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
            except:
                continue
            icon_bt = IconButton(icon_pixbuf, "%s/%s" %(face_dir, pic), has_frame=True)
            icon_bt.connect("pressed", self.on_icon_bt_pressed_cb)
            self.public_icon_list.append(icon_bt)

        self.more_icon_button = IconButton(app_theme.get_pixbuf("%s/more.png" % MODULE_NAME).get_pixbuf(), has_frame=True)
        self.more_icon_button.connect("button-press-event", self.choose_more_picture)
        main_vbox.connect("expose-event", self.draw_white_background)

    def refresh(self):
        self.error_label.set_text("")
        if not self.account_setting.current_set_user:
            return
        if self.account_setting.current_set_user.get_real_name():
            show_name = self.account_setting.current_set_user.get_real_name()
        else:
            show_name = self.account_setting.current_set_user.get_user_name()
        self.tips_label.set_text("<b>%s</b>" % _("Set <u>%s</u>'s picture") % tools.escape_markup_string(show_name))
        self.history_icon = HistroyIcon(self.account_setting.current_set_user)
        self.history_icon.get_history()
        self.history_list_hbox.foreach(lambda w: w.destroy())

        # the private history icon files
        history_dir = os.path.join(self.account_setting.current_set_user.get_home_directory(), ".config/deepin-system-settings/account/icons")
        if os.path.exists(history_dir):
            pic_list = os.listdir(history_dir)
        else:
            pic_list = []
        pic_list.sort()
        private_icon_list = []
        for pic in pic_list:
            try:
                icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                    "%s/%s" %(history_dir, pic)).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
            except:
                continue
            pic_file_path = "%s/%s" %(history_dir, pic)
            icon_bt = IconButton(icon_pixbuf, pic_file_path,
                                 has_frame=True, can_del=check_file_writable(pic_file_path))
            icon_bt.connect("pressed", self.on_icon_bt_pressed_cb)
            private_icon_list.append(icon_bt)
        container_remove_all(self.icon_list_tabel)

        pic_list = self.public_icon_list + private_icon_list
        total_pic = len(pic_list)
        rows = (total_pic + 1) / 10 + 1
        self.icon_list_tabel.resize(rows, 10)
        i = j = 0
        for pic in pic_list:
            self.icon_list_tabel.attach(pic, i, i+1, j, j+1, 4)
            if pic.can_del:
                pic.row = j
                pic.col = i
                pic.connect("del-pressed", self.on_icon_bt_del_icon_file_cb)
            i += 1
            if i >= 10:
                i = 0
                j += 1
        self.icon_list_tabel.attach(self.more_icon_button, i, i+1, j, j+1, 4)

        # history pic IconButton
        icon_button_list = pic_list
        i = 0
        for pic in self.history_icon.history:
            if not os.path.exists(pic):
                continue
            icon_pixbuf = None
            for bt in icon_button_list:
                if pic == bt.get_image_path():
                    icon_pixbuf = bt.pixbuf
                    break
            if not icon_pixbuf:
                try:
                    icon_pixbuf = gtk.gdk.pixbuf_new_from_file(pic).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
                except Exception, e:
                    print e
                    continue
            if i >= 10:
                break
            i += 1
            icon_bt = IconButton(icon_pixbuf, pic, has_frame=True, can_del=True)
            icon_bt.connect("pressed", self.on_icon_bt_pressed_cb)
            icon_bt.connect("del-pressed", self.on_icon_bt_del_pressed_cb)
            self.history_list_hbox.pack_start(icon_bt, False, False)
        self.history_list_hbox.show_all()

    def on_icon_bt_del_pressed_cb(self, widget):
        try:
            file_path = widget.get_image_path()
            widget.destroy()
            if file_path in self.history_icon.history:
                self.history_icon.history.remove(file_path)
                self.history_icon.set_history(self.history_icon.history)
        except Exception, e:
            print e
        
    def on_icon_bt_del_icon_file_cb(self, widget):
        try:
            face_dir = '/var/lib/AccountsService/icons'
            icon_file = self.account_setting.current_set_user.get_icon_file()
            account_server_icon_file = "%s/%s" % (face_dir, self.account_setting.current_set_user.get_user_name())
            file_path = widget.get_image_path()
            if icon_file == account_server_icon_file and \
                    os.path.exists(icon_file) and \
                    os.path.exists(file_path) and \
                    os.stat(icon_file).st_size == os.stat(file_path).st_size:
                file1_md5 = get_file_md5(icon_file)
                file2_md5 = get_file_md5(file_path)
                if file1_md5 == file2_md5:
                    self.account_setting.account_user_set_random_icon(
                        self.account_setting.current_set_user)
            os.remove(file_path)
        except Exception, e:
            print e
        row = widget.row
        col = widget.col
        children = self.icon_list_tabel.get_children()
        children.reverse()
        self.on_icon_bt_del_pressed_cb(widget)
        # widget has destroied
        if not widget.get_visible():
            i = col
            j = row
            for w in children[row*10+col+1:]:
                self.icon_list_tabel.remove(w)
                self.icon_list_tabel.attach(w, i, i+1, j, j+1, 4)
                w.row = j
                w.col = i
                i += 1
                if i >= 10:
                    i = 0
                    j += 1

    def on_icon_bt_pressed_cb(self, widget):
        try:
            file_path = widget.get_image_path()
            self.account_setting.current_set_user.set_icon_file(file_path)
            if not file_path in self.history_icon.history:
                self.history_icon.history.insert(0, file_path)
                self.history_icon.set_history(self.history_icon.history)
        except Exception, e:
            print "set_icon 286:", e
            if isinstance(e, (AccountsPermissionDenied, AccountsUserExists, AccountsFailed, AccountsUserDoesNotExist)):
                #self.error_label.set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), e.msg))
                self.account_setting.set_status_error_text(e.msg)
            return
        self.account_setting.set_to_page(
            self.account_setting.alignment_widgets["main_hbox"], "left")
        self.account_setting.change_crumb(1)

    def choose_more_picture(self, widget, event):
        x = int(event.x_root - event.x)
        y = int(event.y_root - event.y + widget.allocation.height)
        if self.is_has_camera():
            self.choose_menu_with_camera.show((x, y))
        else:
            self.choose_menu_without_camera.show((x, y))

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
            icon_pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
        except Exception, e:
            #self.error_label.set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), str(e)))
            self.account_setting.set_status_error_text(str(e))
            return
        self.account_setting.container_widgets["icon_edit_page"].set_pixbuf(icon_pixbuf)
        self.account_setting.alignment_widgets["edit_iconfile"].show_all()
        self.account_setting.set_to_page(self.account_setting.alignment_widgets["edit_iconfile"], "right")
        self.account_setting.module_frame.send_submodule_crumb(3, _("Edit Picture"))

    def choose_from_screenshot(self):
        cmd = ("/usr/bin/deepin-screenshot", "-d 1", "--sub")
        Popen(cmd)
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        DBUS_NAME = "com.deepin.screenshot"
        OBJECT_PATH = "/com/deepin/screenshot"
        i = 0
        while i < 7:
            try:
                obj = bus.get_object(DBUS_NAME, OBJECT_PATH)
                obj.connect_to_signal("finish", self.screenshot_finish, dbus_interface=DBUS_NAME)
                break
            except dbus.DBusException, e:
                print e, i
                sleep(0.5)
                i += 1

    def screenshot_finish(self, save_type, file_name):
        if save_type == 1:
            pixbuf = gtk.gdk.pixbuf_new_from_file(file_name)
        else:
            clip = gtk.Clipboard()
            pixbuf = clip.wait_for_image()
        self.account_setting.container_widgets["icon_edit_page"].set_pixbuf(pixbuf)
        self.account_setting.alignment_widgets["edit_iconfile"].show_all()
        self.account_setting.set_to_page(self.account_setting.alignment_widgets["edit_iconfile"], "right")
        self.account_setting.module_frame.send_submodule_crumb(3, _("Edit Picture"))

    def choose_from_camera(self):
        self.account_setting.container_widgets["icon_edit_page"].set_camera_mode()
        self.account_setting.alignment_widgets["edit_iconfile"].show_all()
        self.account_setting.set_to_page(self.account_setting.alignment_widgets["edit_iconfile"], "right")
        self.account_setting.module_frame.send_submodule_crumb(3, _("Edit Picture"))

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
        cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
        cr.rectangle(x, y, w, h)
        cr.stroke()

    def is_has_camera(self):
        return Webcam.has_device()
gobject.type_register(IconSetPage)
