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
from dtk.ui.button import ImageButton
from dtk.ui.utils import color_hex_to_cairo, cairo_disable_antialias, container_remove_all
from dtk.ui.cache_pixbuf import CachePixbuf
from icon_button import IconButton
from webcam import Webcam
from constant import *
from utils import AccountsPermissionDenied, AccountsUserDoesNotExist, AccountsUserExists, AccountsFailed
import gtk
import gobject
import tools
import os
import dbus
from time import sleep, time
from subprocess import Popen
from tempfile import mkstemp
from stat import S_IRWXU, S_IRWXG, S_IRWXO

MODULE_NAME = "account"

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
        main_vbox.pack_start(tools.make_align(self.tips_label), False, False)
        main_vbox.pack_start(tools.make_align(height=20), False, False)

        self.history_list_hbox = gtk.HBox(False)
        self.history_list_hbox.set_size_request(-1, 54)

        main_vbox.pack_start(tools.make_align(Label(_("Choose a new picture for your account"), enable_select=False, enable_double_click=False), height=CONTAINNER_HEIGHT), False, False)
        main_vbox.pack_start(tools.make_align(self.icon_list_tabel), False, False)
        main_vbox.pack_start(tools.make_align(height=20), False, False)

        main_vbox.pack_start(tools.make_align(Label(_("Previously used pictures"), enable_select=False, enable_double_click=False), height=CONTAINNER_HEIGHT), False, False)
        main_vbox.pack_start(tools.make_align(self.history_list_hbox), False, False)
        main_vbox.pack_start(tools.make_align(height=20), False, False)

        main_vbox.pack_start(tools.make_align(self.error_label), False, False)

        # public picture list
        face_dir = '/usr/share/pixmaps/faces'
        if os.path.exists(face_dir):
            pic_list = os.listdir(face_dir)
        else:
            pic_list = []
        self.public_icon_list = []

        for pic in pic_list:
            try:
                icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                    "%s/%s" %(face_dir, pic)).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
            except:
                continue
            icon_bt = IconButton(icon_pixbuf, "%s/%s" %(face_dir, pic))
            icon_bt.connect("pressed", self.on_icon_bt_pressed_cb)
            self.public_icon_list.append(icon_bt)

        self.more_icon_button = IconButton(app_theme.get_pixbuf("%s/more.png" % MODULE_NAME).get_pixbuf())
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
        private_icon_list = []
        for pic in pic_list:
            try:
                icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                    "%s/%s" %(history_dir, pic)).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
            except:
                continue
            icon_bt = IconButton(icon_pixbuf, "%s/%s" %(history_dir, pic))
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
            icon_bt = IconButton(icon_pixbuf, pic, can_del=True)
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
        
    def on_icon_bt_pressed_cb(self, widget):
        try:
            file_path = widget.get_image_path()
            self.account_setting.current_set_user.set_icon_file(file_path)
            if not file_path in self.history_icon.history:
                self.history_icon.history.insert(0, file_path)
                self.history_icon.set_history(self.history_icon.history)
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
            self.error_label.set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), str(e)))
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
        while i < 5:
            try:
                obj = bus.get_object(DBUS_NAME, OBJECT_PATH)
                obj.connect_to_signal("finish", self.screenshot_finish, dbus_interface=DBUS_NAME)
                break
            except dbus.DBusException, e:
                print e, i
                sleep(0.5)
                i += 1

    def screenshot_finish(self, save_type, file_name):
        print "finish:", save_type, file_name
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

    # TODO 判断是否有摄像头
    def is_has_camera(self):
        return True
gobject.type_register(IconSetPage)

        
class IconEditArea(gtk.HBox):
    __gsignals__ = {
        "pixbuf-changed": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))}

    AREA_WIDTH = 300
    AREA_HEIGHT = 300
    DRAG_WIDTH = 10
    MIN_SIZE = 144

    POS_OUT = 0
    POS_IN_MOVE = 1
    POS_IN_DRAG = 2

    MODE_CAMERA = 0
    MODE_EDIT = 1

    def __init__(self):
        super(IconEditArea, self).__init__(False)

        self.edit_area = gtk.EventBox()
        self.camera_area = Webcam()
        self.camera_area_init_flag = False
        self.button_vbox = gtk.VBox(False)

        self.edit_area.set_size_request(self.AREA_WIDTH, self.AREA_HEIGHT)
        self.camera_area.set_size_request(self.AREA_WIDTH, self.AREA_HEIGHT)
        self.button_vbox.set_size_request(50, self.AREA_HEIGHT)

        self.button_zoom_in = ImageButton(
            app_theme.get_pixbuf("account/zoom_in.png"),
            app_theme.get_pixbuf("account/zoom_in.png"),
            app_theme.get_pixbuf("account/zoom_in.png"))
        self.button_zoom_out = ImageButton(
            app_theme.get_pixbuf("account/zoom_out.png"),
            app_theme.get_pixbuf("account/zoom_out.png"),
            app_theme.get_pixbuf("account/zoom_out.png"))
        self.button_camera = ImageButton(
            app_theme.get_pixbuf("account/camera.png"),
            app_theme.get_pixbuf("account/camera.png"),
            app_theme.get_pixbuf("account/camera.png"))
        self.button_cut = ImageButton(
            app_theme.get_pixbuf("account/cut.png"),
            app_theme.get_pixbuf("account/cut.png"),
            app_theme.get_pixbuf("account/cut.png"))
        self.button_undo = ImageButton(
            app_theme.get_pixbuf("account/undo.png"),
            app_theme.get_pixbuf("account/undo.png"),
            app_theme.get_pixbuf("account/undo.png"))

        self.button_zoom_in.connect("clicked", self.on_zoom_in_clicked_cb)
        self.button_zoom_out.connect("clicked", self.on_zoom_out_clicked_cb)
        self.button_camera.connect("clicked", self.on_camera_clicked_cb)
        self.button_cut.connect("clicked", self.on_button_clicked_cb)
        self.button_undo.connect("clicked", self.on_undo_clicked_cb)

        self.button_vbox.pack_start(tools.make_align(self.button_zoom_in, xalign=0.5))
        self.button_vbox.pack_start(tools.make_align(self.button_zoom_out, xalign=0.5))
        self.button_vbox.pack_start(tools.make_align(self.button_camera, xalign=0.5))
        self.button_vbox.pack_start(tools.make_align(self.button_cut, xalign=0.5))
        self.button_vbox.pack_start(tools.make_align(self.button_undo, xalign=0.5))

        self.pack_start(self.edit_area, False, False)
        self.pack_start(self.button_vbox, False, False)
        self.set_size_request(self.AREA_WIDTH + 50, self.AREA_HEIGHT)
        self.connect("expose-event", self.draw_frame_border)

        self.edit_area.set_can_focus(True)
        self.edit_area.add_events(gtk.gdk.ALL_EVENTS_MASK)        
        self.edit_area.connect("button-press-event", self.__on_button_press_cb)
        self.edit_area.connect("button-release-event", self.__on_button_release_cb)
        self.edit_area.connect("motion-notify-event", self.__on_motion_notify_cb)
        self.edit_area.connect("expose-event", self.__expose_edit)

        self.current_mode = self.MODE_EDIT
        self.origin_pixbuf = None
        self.origin_pixbuf_width = 0
        self.origin_pixbuf_height = 0
        self.cache_pixbuf = CachePixbuf()
        self.border_color = "#000000"

        # cursor
        self.cursor = {
            self.POS_IN_DRAG : gtk.gdk.Cursor(gtk.gdk.BOTTOM_RIGHT_CORNER),
            self.POS_IN_MOVE : gtk.gdk.Cursor(gtk.gdk.FLEUR),
            self.POS_OUT : None}
        self.cursor_current = None

        self.press_point_coord = (0, 0)
        self.position = self.POS_OUT
        self.drag_flag = False
        self.move_flag = False

        # the pixbuf shown area
        self.pixbuf_offset_x = 0
        self.pixbuf_offset_y = 0
        self.pixbuf_offset_cmp_x = 0
        self.pixbuf_offset_cmp_y = 0
        self.pixbuf_x = 0
        self.pixbuf_y = 0
        self.pixbuf_w = self.AREA_WIDTH
        self.pixbuf_h = self.AREA_HEIGHT
        # the select box area
        self.edit_coord_x = 0
        self.edit_coord_y = 0
        self.edit_coord_w = self.AREA_WIDTH
        self.edit_coord_h = self.AREA_HEIGHT
        self.edit_coord_backup_x = 0
        self.edit_coord_backup_y = 0
        self.edit_coord_backup_w = self.AREA_WIDTH
        self.edit_coord_backup_h = self.AREA_HEIGHT

        self.drag_point_x = 0
        self.drag_point_y = 0
        self.__update_drag_point_coord()

    def draw_frame_border(self, widget, event):
        cr = widget.window.cairo_create()
        with cairo_disable_antialias(cr):
            cr.set_line_width(1)
            x, y, w, h = widget.allocation
            cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
            cr.rectangle(x, y, w, h)
            cr.stroke()

    def on_button_clicked_cb(self, widget):
        print "clicked---------------------"

    def on_undo_clicked_cb(self, button):
        if self.current_mode != self.MODE_EDIT:
            return
        self.set_camera_mode()

    def on_camera_clicked_cb(self, button):
        if self.current_mode != self.MODE_CAMERA:
            return
        drawable = self.camera_area.window
        colormap = drawable.get_colormap()
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 0, 8, *drawable.get_size())
        pixbuf = pixbuf.get_from_drawable(drawable, colormap, 0, 0, 0, 0, *drawable.get_size()) 
        self.set_edit_mode(pixbuf)

    def on_zoom_in_clicked_cb(self, button):
        if self.current_mode != self.MODE_EDIT:
            return
        if self.pixbuf_w >= self.origin_pixbuf_width or self.pixbuf_h >= self.origin_pixbuf_height:
            print "has max size"
            return
        width = int(self.pixbuf_w * 1.1)
        height = int(self.pixbuf_h * 1.1)
        if width >= self.origin_pixbuf_width:
            width = self.origin_pixbuf_width
        if height >= self.origin_pixbuf_height:
            height = self.origin_pixbuf_height
        self.cache_pixbuf.scale(self.origin_pixbuf, width, height)
        # count show area
        self.pixbuf_w = width
        self.pixbuf_h = height
        self.pixbuf_x = (self.AREA_WIDTH - width) / 2
        self.pixbuf_y = (self.AREA_HEIGHT - height) / 2
        if self.pixbuf_x < 0:
            self.pixbuf_offset_x -= self.pixbuf_x
            if self.pixbuf_offset_x + self.AREA_WIDTH > self.pixbuf_w:
                self.pixbuf_offset_x = self.pixbuf_w - self.AREA_WIDTH
            self.pixbuf_x = 0
        if self.pixbuf_y < 0:
            self.pixbuf_offset_y -= self.pixbuf_y
            if self.pixbuf_offset_y + self.AREA_HEIGHT > self.pixbuf_h:
                self.pixbuf_offset_y = self.pixbuf_h - self.AREA_HEIGHT
            self.pixbuf_y = 0
        self.__update_drag_point_coord()

    def on_zoom_out_clicked_cb(self, button):
        if self.current_mode != self.MODE_EDIT:
            return
        if self.pixbuf_w <= self.MIN_SIZE or self.pixbuf_h <= self.MIN_SIZE:
            print "has min size"
            return
        width = int(self.pixbuf_w * 0.9)
        height = int(self.pixbuf_h * 0.9)
        if height >= width and width <= self.MIN_SIZE:
            height = int(float(height) / width * self.MIN_SIZE)
            width = self.MIN_SIZE
        elif height < self.MIN_SIZE:
            width = int(float(width) / height * self.MIN_SIZE)
            height = self.MIN_SIZE
        self.cache_pixbuf.scale(self.origin_pixbuf, width, height)
        # count show area
        self.pixbuf_w = width
        self.pixbuf_h = height
        self.pixbuf_x = (self.AREA_WIDTH - width) / 2
        self.pixbuf_y = (self.AREA_HEIGHT - height) / 2
        # count pixbuf offset
        if self.pixbuf_x < 0:
            self.pixbuf_offset_x -= self.pixbuf_x
            if self.pixbuf_offset_x + self.AREA_WIDTH > self.pixbuf_w:
                self.pixbuf_offset_x = self.pixbuf_w - self.AREA_WIDTH
            self.pixbuf_x = 0
        if self.pixbuf_y < 0:
            self.pixbuf_offset_y -= self.pixbuf_y
            if self.pixbuf_offset_y + self.AREA_HEIGHT > self.pixbuf_h:
                self.pixbuf_offset_y = self.pixbuf_h - self.AREA_HEIGHT
            self.pixbuf_y = 0
        if self.pixbuf_x + self.pixbuf_w < self.AREA_WIDTH:
            self.pixbuf_offset_x = 0
        if self.pixbuf_y + self.pixbuf_h < self.AREA_HEIGHT:
            self.pixbuf_offset_y = 0
        # count edit area
        if self.edit_coord_x < self.pixbuf_x:
            self.edit_coord_x = self.pixbuf_x
        if self.edit_coord_y < self.pixbuf_y:
            self.edit_coord_y = self.pixbuf_y
        right_pos = min(self.pixbuf_x+self.pixbuf_w, self.AREA_WIDTH)
        bottom_pos = min(self.pixbuf_y+self.pixbuf_h, self.AREA_HEIGHT)
        if self.edit_coord_x + self.edit_coord_w > right_pos:
            self.edit_coord_w = self.edit_coord_h = right_pos - self.edit_coord_x
        if self.edit_coord_y + self.edit_coord_h > bottom_pos:
            self.edit_coord_w = self.edit_coord_h = bottom_pos - self.edit_coord_y
        print "after zoomout:", self.edit_coord_x, self.edit_coord_y, self.edit_coord_w, self.edit_coord_h
        print "---", self.pixbuf_x, self.pixbuf_y, self.pixbuf_w, self.pixbuf_h, self.pixbuf_offset_x, self.pixbuf_offset_y
        self.__update_drag_point_coord()

    def __expose_edit(self, widget, event):
        pixbuf = self.cache_pixbuf.get_cache()
        if not pixbuf:
            return
        cr = widget.window.cairo_create()
        cr.set_source_pixbuf(pixbuf, self.pixbuf_x-self.pixbuf_offset_x, self.pixbuf_y-self.pixbuf_offset_y)
        cr.paint()
        self.__draw_mask(cr, widget.allocation)
        self.__draw_frame(cr, widget.allocation)
        return True

    def __draw_frame(self, cr, allocation):
        with cairo_disable_antialias(cr):
            cr.set_line_width(1)
            cr.set_source_rgb(*color_hex_to_cairo(self.border_color))
            x = self.edit_coord_x
            y = self.edit_coord_y
            w = self.edit_coord_w
            h = self.edit_coord_h
            if x == 0:
                x = 1
            if y == 0:
                y = 1
            if x + w > self.AREA_WIDTH:
                w = self.AREA_WIDTH- x
            if y + h > self.AREA_HEIGHT:
                h = self.AREA_HEIGHT- y
            cr.rectangle(x, y, w, h)
            cr.stroke()
            cr.set_source_rgb(*color_hex_to_cairo(self.border_color))
            cr.rectangle(self.drag_point_x, self.drag_point_y, self.DRAG_WIDTH, self.DRAG_WIDTH)
            cr.stroke()

    def __draw_mask(self, cr, allocation):
        x, y, w, h = allocation
        x = 0
        y = 0
        # Draw left.
        if self.edit_coord_x > 0:
            cr.set_source_rgba(0, 0, 0, 0.5)
            cr.rectangle(x, y, self.edit_coord_x, h)
            cr.fill()

        # Draw top.
        if self.edit_coord_y > 0:
            cr.set_source_rgba(0, 0, 0, 0.5)
            cr.rectangle(x+self.edit_coord_x, y, w-self.edit_coord_x, self.edit_coord_y)
            cr.fill()

        # Draw bottom.
        if self.edit_coord_y + self.edit_coord_h < h:
            cr.set_source_rgba(0, 0, 0, 0.5)
            cr.rectangle(x+self.edit_coord_x, y+self.edit_coord_y+self.edit_coord_h,
                         w-self.edit_coord_x, h-self.edit_coord_y-self.edit_coord_h)
            cr.fill()

        # Draw right.
        if self.edit_coord_x + self.edit_coord_w < w:
            cr.set_source_rgba(0, 0, 0, 0.5)
            cr.rectangle(x+self.edit_coord_x+self.edit_coord_w, y+self.edit_coord_y,
                         w-self.edit_coord_x-self.edit_coord_w, self.edit_coord_h)
            cr.fill()

    def set_pixbuf(self, pixbuf):
        if not pixbuf:
            self.cache_pixbuf.cache_pixbuf = None
            self.edit_area.queue_draw()
            self.emit_changed()
            return
        self.origin_pixbuf = pixbuf
        self.origin_pixbuf_width = w = pixbuf.get_width()
        self.origin_pixbuf_height = h = pixbuf.get_height()
        if h >= w:
            w = int(float(w) / h * self.AREA_HEIGHT)
            h = self.AREA_HEIGHT
            if w < self.MIN_SIZE:
                h = int(float(h) / w * self.MIN_SIZE)
                w = self.MIN_SIZE
            self.edit_coord_w = self.edit_coord_h = w
        else:
            h = int(float(h) / w * self.AREA_WIDTH)
            w = self.AREA_WIDTH
            if h < self.MIN_SIZE:
                w = int(float(w) / h * self.MIN_SIZE)
                h = self.MIN_SIZE
            self.edit_coord_w = self.edit_coord_h = h
        # count the offset coord
        self.pixbuf_offset_x = 0
        self.pixbuf_offset_y = 0
        self.pixbuf_x = 0
        self.pixbuf_y = 0
        self.pixbuf_w = w
        self.pixbuf_h = h
        if w < self.AREA_WIDTH:
            self.pixbuf_x = (self.AREA_WIDTH - w) / 2
        if h < self.AREA_HEIGHT :
            self.pixbuf_y = (self.AREA_HEIGHT - h) / 2
        # update select box coord
        self.edit_coord_x = self.pixbuf_x
        self.edit_coord_y = self.pixbuf_y
        self.cache_pixbuf.scale(pixbuf, w, h)
        self.drag_point_x = self.edit_coord_x + self.edit_coord_w - self.DRAG_WIDTH
        self.drag_point_y = self.edit_coord_y + self.edit_coord_h - self.DRAG_WIDTH
        self.edit_area.queue_draw()
        self.emit_changed()

    def emit_changed(self):
        pix = self.cache_pixbuf.get_cache()
        if pix:
            pix = pix.subpixbuf(int(self.edit_coord_x-self.pixbuf_x+self.pixbuf_offset_x),
                                int(self.edit_coord_y-self.pixbuf_y+self.pixbuf_offset_y),
                                int(self.edit_coord_w),
                                int(self.edit_coord_h))
        self.emit("pixbuf-changed", pix)

    def get_pixbuf(self):
        return self.cache_pixbuf.get_cache()

    def set_cursor(self):
        if not self.edit_area.window:
            return
        if self.cursor_current != self.cursor[self.position]:
            self.cursor_current = self.cursor[self.position]
            self.edit_area.window.set_cursor(self.cursor_current)

    def __on_button_press_cb(self, widget, event):
        self.__update_position(event.x, event.y)
        if self.position == self.POS_IN_DRAG:
            self.drag_flag = True
        elif self.position == self.POS_IN_MOVE:
            self.move_flag = True
        self.press_point_coord = (event.x, event.y)
        self.edit_coord_backup_x = self.edit_coord_x
        self.edit_coord_backup_y = self.edit_coord_y
        self.edit_coord_backup_w = self.edit_coord_w
        self.edit_coord_backup_h = self.edit_coord_h

    def __on_button_release_cb(self, widget, event):
        self.drag_flag = False
        self.move_flag = False

    def __on_motion_notify_cb(self, widget, event):
        pixbuf = self.cache_pixbuf.get_cache()
        if not pixbuf:
            return
        if not self.drag_flag and not self.move_flag:
            self.__update_position(event.x, event.y)
            self.set_cursor()
        right_pos = min(self.pixbuf_x+self.pixbuf_w, self.AREA_WIDTH)
        bottom_pos = min(self.pixbuf_y+self.pixbuf_h, self.AREA_HEIGHT)
        if self.move_flag:
            self.edit_coord_x = self.edit_coord_backup_x + event.x - self.press_point_coord[0]
            self.edit_coord_y = self.edit_coord_backup_y + event.y - self.press_point_coord[1]

            # check left
            if self.edit_coord_x < self.pixbuf_x:
                # move the pixbuf into canvas
                if self.pixbuf_w > self.AREA_WIDTH:
                    if self.pixbuf_offset_x > 0:
                        self.pixbuf_offset_x -= self.pixbuf_x - self.edit_coord_x
                    if self.pixbuf_offset_x < 0:
                        self.pixbuf_offset_x = 0
                self.edit_coord_x = self.pixbuf_x
            # check top
            if self.edit_coord_y < self.pixbuf_y:
                # move the pixbuf into canvas
                if self.pixbuf_h > self.AREA_HEIGHT:
                    if self.pixbuf_offset_y > 0:
                        self.pixbuf_offset_y -= self.pixbuf_y - self.edit_coord_y
                    if self.pixbuf_offset_y < 0:
                        self.pixbuf_offset_y = 0
                self.edit_coord_y = self.pixbuf_y
            # check right
            if self.edit_coord_x + self.edit_coord_w > right_pos:
                # move the pixbuf into canvas
                if self.pixbuf_w > self.AREA_WIDTH:
                    if self.pixbuf_offset_x + self.AREA_WIDTH < self.pixbuf_w:
                        self.pixbuf_offset_x += (self.edit_coord_x + self.edit_coord_w) - self.AREA_WIDTH
                    if self.pixbuf_offset_x + self.AREA_WIDTH > self.pixbuf_w:
                        self.pixbuf_offset_x = self.pixbuf_w - self.AREA_WIDTH
                self.edit_coord_x = right_pos - self.edit_coord_w
            # check bottom
            if self.edit_coord_y + self.edit_coord_h > bottom_pos:
                # move the pixbuf into canvas
                if self.pixbuf_h > self.AREA_HEIGHT:
                    if self.pixbuf_offset_y + self.AREA_HEIGHT < self.pixbuf_h:
                        self.pixbuf_offset_y += (self.edit_coord_y + self.edit_coord_h) - self.AREA_HEIGHT
                    if self.pixbuf_offset_y + self.AREA_HEIGHT > self.pixbuf_h:
                        self.pixbuf_offset_y = self.pixbuf_h - self.AREA_HEIGHT
                self.edit_coord_y = bottom_pos - self.edit_coord_h
        elif self.drag_flag:
            drag_offset = max(event.x - self.press_point_coord[0],
                              event.y - self.press_point_coord[1])
            self.edit_coord_h = self.edit_coord_w = self.edit_coord_backup_w + drag_offset
            if self.edit_coord_h < self.MIN_SIZE or self.edit_coord_w < self.MIN_SIZE:
                self.edit_coord_h = self.edit_coord_w = self.MIN_SIZE

            if self.edit_coord_x + self.edit_coord_w > right_pos:
                self.edit_coord_h = self.edit_coord_w = right_pos - self.edit_coord_x
            if self.edit_coord_y + self.edit_coord_h > bottom_pos:
                self.edit_coord_h = self.edit_coord_w = bottom_pos - self.edit_coord_y
        self.__update_drag_point_coord()

    def __update_drag_point_coord(self):
        new_x = self.edit_coord_x + self.edit_coord_w - self.DRAG_WIDTH
        new_y = self.edit_coord_y + self.edit_coord_h - self.DRAG_WIDTH
        if self.drag_point_x != new_x or self.drag_point_y != new_y or\
                self.pixbuf_offset_cmp_x != self.pixbuf_offset_x or\
                self.pixbuf_offset_cmp_y != self.pixbuf_offset_y:
            self.drag_point_x = new_x
            self.drag_point_y = new_y
            self.pixbuf_offset_cmp_x = self.pixbuf_offset_x
            self.pixbuf_offset_cmp_y = self.pixbuf_offset_y
            self.emit_changed()
        self.edit_area.queue_draw()

    def __update_position(self, x, y):
        if self.drag_point_x <= x <= self.drag_point_x + self.DRAG_WIDTH and\
                self.drag_point_y <= y <= self.drag_point_y + self.DRAG_WIDTH:
            self.position = self.POS_IN_DRAG
        elif self.edit_coord_x <= x <= self.edit_coord_x + self.edit_coord_w and\
                self.edit_coord_y <= y <= self.edit_coord_y + self.edit_coord_h:
            self.position = self.POS_IN_MOVE
        else:
            self.position = self.POS_OUT

    def set_camera_mode(self):
        self.current_mode = self.MODE_CAMERA
        self.set_pixbuf(None)
        if self.edit_area in self.get_children():
            self.remove(self.edit_area)
        if not self.camera_area in self.get_children():
            self.pack_start(self.camera_area, False, False)
            self.reorder_child(self.camera_area, 0)
        self.show_all()
        #self.button_zoom_in.set_sensitive(False)
        #self.button_zoom_out.set_sensitive(False)
        #self.button_camera.set_sensitive(True)
        #self.button_cut.set_sensitive(True)
        #self.button_undo.set_sensitive(True)
        try:
            self.camera_area.create_video_pipeline()
        except Exception, e:
            print e

    def set_edit_mode(self, pixbuf):
        self.current_mode = self.MODE_EDIT
        self.set_pixbuf(pixbuf)
        if self.camera_area in self.get_children():
            self.remove(self.camera_area)
        if not self.edit_area in self.get_children():
            self.pack_start(self.edit_area, False, False)
            self.reorder_child(self.edit_area, 0)
        self.show_all()
        #self.button_zoom_in.set_sensitive(True)
        #self.button_zoom_out.set_sensitive(True)
        #self.button_camera.set_sensitive(False)
        #self.button_cut.set_sensitive(False)
        #self.button_undo.set_sensitive(True)
        self.camera_pause()

    def camera_start(self):
        try:
            self.camera_area.set_playing()
        except Exception, e:
            print e
            pass

    def camera_pause(self):
        try:
            self.camera_area.set_paused()
        except Exception, e:
            print e
            pass
gobject.type_register(IconEditArea)


class IconEditPage(gtk.HBox):
    def __init__(self, account_setting):
        super(IconEditPage, self).__init__(False)
        self.account_setting = account_setting
        self.error_label = Label("", label_width=350, enable_select=False, enable_double_click=False)

        left_align = gtk.Alignment()
        right_align = gtk.Alignment()
        left_align.set_padding(0, 0, 0, 60)
        #right_align.set_padding(0, 0, 0, 60)

        left_vbox = gtk.VBox(False)
        right_vbox = gtk.VBox(False)
        left_vbox.set_spacing(BETWEEN_SPACING)
        right_vbox.set_spacing(BETWEEN_SPACING)

        left_align.add(left_vbox)
        right_align.add(right_vbox)

        self.draw_area = IconEditArea()
        left_vbox.pack_start(tools.make_align(Label(_("Clip"), enable_select=False, enable_double_click=False)), False, False)
        left_vbox.pack_start(tools.make_align(self.draw_area, yalign=0.0, width=350, height=300))

        self.thumbnail_large = gtk.Image()
        self.thumbnail_mid = gtk.Image()
        self.thumbnail_small = gtk.Image()
        self.thumbnail_large.set_size_request(144, 144)
        self.thumbnail_mid.set_size_request(48, 48)
        self.thumbnail_small.set_size_request(24, 24)

        right_vbox.pack_start(tools.make_align(Label(_("Preview"), enable_select=False, enable_double_click=False)), False, False)
        right_vbox.pack_start(tools.make_align(self.thumbnail_large), False, False)
        right_vbox.pack_start(tools.make_align(self.thumbnail_mid), False, False)
        right_vbox.pack_start(tools.make_align(self.thumbnail_small), False, False)
        right_vbox.pack_start(tools.make_align(self.error_label, yalign=0.0))

        self.pack_start(left_align, False, False)
        self.pack_start(right_align, False, False)
        self.connect("expose-event", self.draw_frame_border, left_align, right_align)
        self.draw_area.connect("pixbuf-changed", self.__on_pixbuf_changed_cb)

    def draw_frame_border(self, widget, event, la, ra):
        cr = widget.window.cairo_create()
        with cairo_disable_antialias(cr):
            cr.set_line_width(1)
            x, y, w, h = self.thumbnail_large.allocation
            cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
            cr.rectangle(x-1, y-1, w+2, h+2)
            cr.stroke()
            x, y, w, h = self.thumbnail_mid.allocation
            cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
            cr.rectangle(x-1, y-1, w+2, h+2)
            cr.stroke()
            x, y, w, h = self.thumbnail_small.allocation
            cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
            cr.rectangle(x-1, y-1, w+2, h+2)
            cr.stroke()

    def set_pixbuf(self, pixbuf):
        self.error_label.set_text("")
        self.draw_area.set_edit_mode(pixbuf)
    
    def refresh(self):
        self.set_pixbuf(None)
        self.error_label.set_text("")

    def set_camera_mode(self):
        self.error_label.set_text("")
        self.draw_area.set_camera_mode()

    def stop_camera(self):
        self.draw_area.camera_pause()

    def save_edit_icon(self):
        pixbuf = self.thumbnail_large.get_pixbuf()
        if not pixbuf:
            self.error_label.set_text("<span foreground='red'>%s%s</span>" % (
                _("Error:"), _("no picture")))
            return
        tmp = mkstemp(".tmp", "account-settings")
        os.close(tmp[0])
        filename = tmp[1]
        pixbuf.save(filename, "png")
        try:
            self.account_setting.current_set_user.set_icon_file(filename)
            history_icon = self.account_setting.container_widgets["icon_set_page"].history_icon
            if not filename in history_icon.history:
                # backup picture to user home
                path = "/var/lib/AccountsService/icons/" + self.account_setting.current_set_user.get_user_name()
                backup_path = "%s/%s" % (history_icon.icons_dir, str(int(time())))
                fp1 = open(path, 'r')
                fp2 = open(backup_path, 'w')
                fp2.write(fp1.read())
                fp1.close()
                fp2.close()
                history_icon.history.insert(0, backup_path)
                history_icon.set_history(history_icon.history)
        except Exception, e:
            from traceback import print_exc
            print_exc()
            print e
            if isinstance(e, (AccountsPermissionDenied, AccountsUserExists, AccountsFailed, AccountsUserDoesNotExist)):
                self.error_label.set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), e.msg))
                return
        self.stop_camera()
        self.account_setting.container_widgets["slider"].slide_to_page(
            self.account_setting.alignment_widgets["main_hbox"], "left")
        self.account_setting.change_crumb(1)

    def __on_pixbuf_changed_cb(self, widget, pixbuf):
        if pixbuf:
            self.thumbnail_large.set_from_pixbuf(pixbuf.scale_simple(
                144, 144, gtk.gdk.INTERP_BILINEAR))
            self.thumbnail_mid.set_from_pixbuf(pixbuf.scale_simple(
                48, 48, gtk.gdk.INTERP_BILINEAR))
            self.thumbnail_small.set_from_pixbuf(pixbuf.scale_simple(
                24, 24, gtk.gdk.INTERP_BILINEAR))
        else:
            self.thumbnail_large.set_from_pixbuf(None)
            self.thumbnail_mid.set_from_pixbuf(None)
            self.thumbnail_small.set_from_pixbuf(None)
        if pixbuf:
            self.account_setting.button_widgets["save_edit_icon"].set_sensitive(True)
        else:
            self.account_setting.button_widgets["save_edit_icon"].set_sensitive(False)

gobject.type_register(IconEditPage)
