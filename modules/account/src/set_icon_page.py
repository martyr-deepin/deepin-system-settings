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
from dtk.ui.utils import color_hex_to_cairo, cairo_disable_antialias
from dtk.ui.cache_pixbuf import CachePixbuf
from icon_button import IconButton
from constant import *
from utils import AccountsPermissionDenied, AccountsUserDoesNotExist, AccountsUserExists, AccountsFailed
import gtk
import gobject
import tools
import os
from tempfile import mkstemp
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

        self.choose_menu = Menu([(None, _("从本地文件"), self.choose_from_picture), (None, _("使用深度截图"), self.choose_from_screenshot)], True)
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
        icon_button_list = self.icon_list_hbox.get_children()
        for pic in self.histroy_icon.histroy:
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
            icon_pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
        except Exception, e:
            self.error_label.set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), str(e)))
            return
        self.account_setting.container_widgets["icon_edit_page"].set_pixbuf(icon_pixbuf)
        self.account_setting.alignment_widgets["edit_iconfile"].show_all()
        self.account_setting.set_to_page(self.account_setting.alignment_widgets["edit_iconfile"], "right")
        self.account_setting.module_frame.send_submodule_crumb(3, _("Edit Icon"))

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
        cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
        cr.rectangle(x, y, w, h)
        cr.stroke()
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

    def __init__(self):
        super(IconEditArea, self).__init__(False)

        self.edit_area = gtk.EventBox()
        self.button_vbox = gtk.VBox(False)

        self.edit_area.set_size_request(self.AREA_WIDTH, self.AREA_HEIGHT)
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
        #self.edit_area.connect("focus-in-event", self.__on_focus_in_cb)
        #self.edit_area.connect("focus-out-event", self.__on_focus_out_cb)
        #self.edit_area.connect("enter-notify-event", self.__on_enter_notify_cb)
        #self.edit_area.connect("leave-notify-event", self.__on_leave_notify_cb)

        self.origin_pixbuf = None
        self.cache_pixbuf = CachePixbuf()
        self.border_color = "#000000"

        self.cursor = {
            self.POS_IN_DRAG : gtk.gdk.Cursor(gtk.gdk.BOTTOM_RIGHT_CORNER),
            self.POS_IN_MOVE : gtk.gdk.Cursor(gtk.gdk.FLEUR),
            self.POS_OUT : None}
        self.cursor_current = None

        self.press_point_coord = (0, 0)
        self.position = self.POS_OUT
        self.drag_flag = False
        self.move_flag = False

        # the select box coord
        self.edit_coord_x = 0
        self.edit_coord_y = 0
        self.edit_coord_w = self.AREA_WIDTH
        self.edit_coord_h = self.AREA_HEIGHT
        self.edit_coord_backup_x = 0
        self.edit_coord_backup_y = 0
        self.edit_coord_backup_w = self.AREA_WIDTH
        self.edit_coord_backup_h = self.AREA_HEIGHT
        self.__update_drag_point_coord()

    def draw_frame_border(self, widget, event):
        cr = widget.window.cairo_create()
        with cairo_disable_antialias(cr):
            cr.set_line_width(1)
            x, y, w, h = widget.allocation
            cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
            cr.rectangle(x, y, w, h)
            cr.stroke()

    def __expose_edit(self, widget, event):
        pixbuf = self.cache_pixbuf.get_cache()
        if not pixbuf:
            return
        cr = widget.window.cairo_create()
        cr.set_source_pixbuf(pixbuf, self.offset_x, self.offset_y)
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
        w = pixbuf.get_width()
        h = pixbuf.get_height()
        if h >= w:
            w = int(float(w) / h * self.AREA_HEIGHT)
            h = self.AREA_HEIGHT
            self.edit_coord_w = self.edit_coord_h = w
        else:
            h = int(float(h) / w * self.AREA_WIDTH)
            w = self.AREA_WIDTH
            self.edit_coord_w = self.edit_coord_h = h
        # count the offset coord
        self.offset_x = 0
        self.offset_y = 0
        if w < self.AREA_WIDTH:
            self.offset_x = (self.AREA_WIDTH - w) / 2
        if h < self.AREA_HEIGHT :
            self.offset_y = (self.AREA_HEIGHT - h) / 2
        # update select box coord
        self.edit_coord_x = self.offset_x
        self.edit_coord_y = self.offset_y
        self.cache_pixbuf.scale(pixbuf, w, h)
        self.drag_point_x = self.edit_coord_x + self.edit_coord_w - self.DRAG_WIDTH
        self.drag_point_y = self.edit_coord_y + self.edit_coord_h - self.DRAG_WIDTH
        self.edit_area.queue_draw()
        self.emit_changed()

    def emit_changed(self):
        pix = self.cache_pixbuf.get_cache()
        if pix:
            pix = pix.subpixbuf(int(self.edit_coord_x-self.offset_x),
                                int(self.edit_coord_y-self.offset_y),
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
        if not self.drag_flag and not self.move_flag:
            self.__update_position(event.x, event.y)
            self.set_cursor()
        if self.move_flag:
            self.edit_coord_x = self.edit_coord_backup_x + event.x - self.press_point_coord[0]
            self.edit_coord_y = self.edit_coord_backup_y + event.y - self.press_point_coord[1]

            if self.edit_coord_x < 0:
                self.edit_coord_x = 0
            if self.edit_coord_y < 0:
                self.edit_coord_y = 0
            if self.edit_coord_x + self.edit_coord_w > self.AREA_WIDTH:
                self.edit_coord_x = self.AREA_WIDTH - self.edit_coord_w
            if self.edit_coord_y + self.edit_coord_h > self.AREA_HEIGHT:
                self.edit_coord_y = self.AREA_HEIGHT - self.edit_coord_h
            self.__update_drag_point_coord()
            self.emit_changed()
        elif self.drag_flag:
            drag_offset = max(event.x - self.press_point_coord[0],
                              event.y - self.press_point_coord[1])
            self.edit_coord_h = self.edit_coord_w = self.edit_coord_backup_w + drag_offset
            if self.edit_coord_h < self.MIN_SIZE or self.edit_coord_w < self.MIN_SIZE:
                self.edit_coord_h = self.edit_coord_w = self.MIN_SIZE
            if self.edit_coord_x + self.edit_coord_w > self.AREA_WIDTH:
                self.edit_coord_w = self.edit_coord_h = self.AREA_WIDTH - self.edit_coord_x
            if self.edit_coord_y + self.edit_coord_h > self.AREA_HEIGHT:
                self.edit_coord_w = self.edit_coord_h = self.AREA_HEIGHT - self.edit_coord_y
            self.__update_drag_point_coord()
            self.emit_changed()

    def __update_drag_point_coord(self):
        self.drag_point_x = self.edit_coord_x + self.edit_coord_w - self.DRAG_WIDTH
        self.drag_point_y = self.edit_coord_y + self.edit_coord_h - self.DRAG_WIDTH
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

    def __on_focus_in_cb(self, widget, event):
        print "focus in"

    def __on_focus_out_cb(self, widget, event):
        print "focus out"

    def __on_enter_notify_cb(self, widget, event):
        print "enter"
        widget.window.set_cursor(self.cursor_move)

    def __on_leave_notify_cb(self, widget, event):
        print "leave"
gobject.type_register(IconEditArea)


class IconEditPage(gtk.HBox):
    def __init__(self, account_setting):
        super(IconEditPage, self).__init__(False)
        self.account_setting = account_setting
        self.error_label = Label("", label_width=350, enable_select=False)

        left_align = gtk.Alignment()
        right_align = gtk.Alignment()
        left_align.set_padding(0, 0, 0, 60)
        right_align.set_padding(0, 0, 0, 60)

        left_vbox = gtk.VBox(False)
        right_vbox = gtk.VBox(False)
        left_vbox.set_spacing(BETWEEN_SPACING)
        right_vbox.set_spacing(BETWEEN_SPACING)

        left_align.add(left_vbox)
        right_align.add(right_vbox)

        self.draw_area = IconEditArea()
        left_vbox.pack_start(tools.make_align(Label(_("截取头像"))), False, False)
        left_vbox.pack_start(tools.make_align(self.draw_area))

        self.thumbnail_large = gtk.Image()
        self.thumbnail_mid = gtk.Image()
        self.thumbnail_small = gtk.Image()
        self.thumbnail_large.set_size_request(144, 144)
        self.thumbnail_mid.set_size_request(48, 48)
        self.thumbnail_small.set_size_request(24, 24)

        right_vbox.pack_start(tools.make_align(Label(_("头像预览"))), False, False)
        right_vbox.pack_start(tools.make_align(self.thumbnail_large), False, False)
        right_vbox.pack_start(tools.make_align(self.thumbnail_mid), False, False)
        right_vbox.pack_start(tools.make_align(self.thumbnail_small), False, False)
        right_vbox.pack_start(tools.make_align(self.error_label), False, False)

        self.pack_start(left_align)
        self.pack_start(right_align)
        self.connect("expose-event", self.draw_frame_border)
        self.draw_area.connect("pixbuf-changed", self.__on_pixbuf_changed_cb)

    def draw_frame_border(self, widget, event):
        cr = widget.window.cairo_create()
        with cairo_disable_antialias(cr):
            cr.set_line_width(1)
            x, y, w, h = self.thumbnail_large.allocation
            cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
            cr.rectangle(x, y, w, h)
            cr.stroke()
            x, y, w, h = self.thumbnail_mid.allocation
            cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
            cr.rectangle(x, y, w, h)
            cr.stroke()
            x, y, w, h = self.thumbnail_small.allocation
            cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
            cr.rectangle(x, y, w, h)
            cr.stroke()

    def set_pixbuf(self, pixbuf):
        self.draw_area.set_pixbuf(pixbuf)
    
    def refresh(self):
        self.set_pixbuf(None)
        self.error_label.set_text("")

    def save_edit_icon(self):
        pixbuf = self.thumbnail_large.get_pixbuf()
        if not pixbuf:
            self.error_label.set_text("<span foreground='red'>%s%s</span>" % (
                _("Error:"), _("头像为空")))
            return
        tmp = mkstemp(".tmp", "account-settings")
        os.close(tmp[0])
        filename = tmp[1]
        pixbuf.save(filename, "png")
        try:
            self.account_setting.current_set_user.set_icon_file(filename)
            histroy_icon = self.account_setting.container_widgets["icon_set_page"].histroy_icon
            if not filename in histroy_icon.histroy:
                path = "/var/lib/AccountsService/icons/" + self.account_setting.current_set_user.get_user_name()
                histroy_icon.histroy.append(path)
                histroy_icon.set_histroy(self.histroy_icon.histroy)
        except Exception, e:
            print e
            if isinstance(e, (AccountsPermissionDenied, AccountsUserExists, AccountsFailed, AccountsUserDoesNotExist)):
                self.error_label.set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), e.msg))
            return
        # TODO 更新histroy
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
        if not self.account_setting.button_widgets["save_edit_icon"].get_sensitive():
            self.account_setting.button_widgets["save_edit_icon"].set_sensitive(True)

gobject.type_register(IconEditPage)
