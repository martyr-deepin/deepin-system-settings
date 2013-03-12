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
from dtk.ui.cache_pixbuf import CachePixbuf
from dtk.ui.utils import cairo_disable_antialias, color_hex_to_cairo, container_remove_all, propagate_expose
from dtk.ui.panel import Panel
from webcam import Webcam
from image_button import ImageButton
from constant import *
from account_utils import AccountsPermissionDenied, AccountsUserDoesNotExist, AccountsUserExists, AccountsFailed
import tools
import gtk
import gobject
import os
from cairo import OPERATOR_SOURCE
from time import time
from tempfile import mkstemp
from stat import S_IRWXU, S_IRWXG, S_IRWXO, S_IWUSR, S_IWGRP, S_IWOTH

class IconEditArea(gtk.Layout):
    __gsignals__ = {
        "pixbuf-changed": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))}

    AREA_WIDTH = 300
    AREA_HEIGHT = 300
    DRAG_WIDTH = 10
    MIN_SIZE = 150

    POS_OUT = 0
    POS_IN_MOVE = 1
    POS_IN_DRAG = 2

    MODE_CAMERA = 0
    MODE_CAMERA_EDIT = 1
    MODE_EDIT = 2

    def __init__(self):
        super(IconEditArea, self).__init__()

        self.edit_area = gtk.EventBox()
        self.camera_area = Webcam()
        self.camera_area_init_flag = False
        self.button_hbox = gtk.HBox(False)
        self.button_hbox_height = 40

        self.edit_area.set_size_request(self.AREA_WIDTH, self.AREA_HEIGHT)
        self.camera_area.set_size_request(self.AREA_WIDTH, self.AREA_HEIGHT)
        self.button_hbox.set_size_request(self.AREA_WIDTH, self.button_hbox_height)

        self.button_zoom_in = ImageButton(
            app_theme.get_pixbuf("account/zoom_in.png"),
            app_theme.get_pixbuf("account/zoom_in.png"),
            app_theme.get_pixbuf("account/zoom_in.png"),
            _("zoom in"))
        self.button_zoom_out = ImageButton(
            app_theme.get_pixbuf("account/zoom_out.png"),
            app_theme.get_pixbuf("account/zoom_out.png"),
            app_theme.get_pixbuf("account/zoom_out.png"),
            _("zoom out"))
        self.button_camera = ImageButton(
            app_theme.get_pixbuf("account/camera.png"),
            app_theme.get_pixbuf("account/camera.png"),
            app_theme.get_pixbuf("account/camera.png"),
            _("拍照"))
        self.button_camera_again = ImageButton(
            app_theme.get_pixbuf("account/camera.png"),
            app_theme.get_pixbuf("account/camera.png"),
            app_theme.get_pixbuf("account/camera.png"),
            _("再次拍照"))

        self.button_zoom_in_align = tools.make_align(self.button_zoom_in, xalign=0.5, yalign=0.5)
        self.button_zoom_out_align = tools.make_align(self.button_zoom_out, xalign=0.5, yalign=0.5)
        self.button_camera_align = tools.make_align(self.button_camera, xalign=0.5, yalign=0.5)
        self.button_camera_again_align = tools.make_align(self.button_camera_again, xalign=0.5, yalign=0.5)

        self.button_zoom_in.connect("clicked", self.on_zoom_in_clicked_cb)
        self.button_zoom_out.connect("clicked", self.on_zoom_out_clicked_cb)
        self.button_camera.connect("clicked", self.on_camera_clicked_cb)
        self.button_camera_again.connect("clicked", self.on_camera_again_clicked_cb)
        self.button_camera_again.connect("button-press-event", self.on_camera_again_press_cb)

        self.box = gtk.VBox(False)
        self.box.pack_start(self.edit_area, False, False)
        #self.box.pack_start(self.button_hbox, False, False)
        #self.box.pack_start(tools.make_align(yalign=0.0, yscale=1.0))
        self.set_size(self.AREA_WIDTH, self.AREA_HEIGHT)
        self.set_size_request(self.AREA_WIDTH, self.AREA_HEIGHT)
        self.connect("expose-event", self.draw_frame_border)
        self.put(self.box, 0, 0)
        self.put(self.button_hbox, 0, self.AREA_HEIGHT-self.button_hbox_height)

        self.edit_area.set_can_focus(True)
        self.edit_area.set_visible_window(False)
        self.edit_area.add_events(gtk.gdk.ALL_EVENTS_MASK)        
        self.edit_area.connect("button-press-event", self.__on_button_press_cb)
        self.edit_area.connect("button-release-event", self.__on_button_release_cb)
        self.edit_area.connect("motion-notify-event", self.__on_motion_notify_cb)
        #self.edit_area.connect("leave-notify-event", self.__on_leave_notify_cb)
        self.edit_area.connect("expose-event", self.__expose_edit)

        self.camera_area.connect("motion-notify-event", self.__on_camera_motion_notify_cb)

        panel_size = self.button_camera.get_size_request()
        #self.panel = Panel(panel_size[0], panel_size[1], gtk.WINDOW_POPUP)
        self.panel = Panel(self.AREA_WIDTH, self.button_hbox_height, gtk.WINDOW_POPUP)
        self.panel_layout = gtk.Fixed()
        self.panel_layout.put(self.button_camera_align, (self.AREA_WIDTH-panel_size[0])/2, 0)
        self.panel.add(self.panel_layout)
        self.panel.hide_panel()
        self.panel.connect("expose-event", self.__draw_panel_background)
        self.panel.connect("size-allocate", lambda w,e: w.queue_draw())

        #self.panel.connect("enter-notify-event", self.__on_camera_enter_notify_cb)
        self.panel.connect("leave-notify-event", self.__on_camera_leave_notify_cb)
        self.camera_focus_flag = True

        self.__refresh_time_id = None
        self.__button_time_id = None
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
        #
        self.__show_button_flag = True
        self.__button_moving_flag = False
        #self.__refresh_flag = False

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
            cr.rectangle(x-1, y-1, w+2, h+2)
            cr.stroke()

    def on_camera_again_clicked_cb(self, button):
        self.set_camera_mode()

    def on_camera_again_press_cb(self, button, event):
        x, y = event.get_coords()
        x_root, y_root = event.get_root_coords()
        win_x = x_root - x - button.allocation.x - self.allocation.x
        win_y = y_root - y - button.allocation.y - self.allocation.y
        self.set_win_pos(win_x, win_y)

    def on_camera_clicked_cb(self, button):
        self.current_mode = self.MODE_CAMERA_EDIT
        drawable = self.camera_area.window
        colormap = drawable.get_colormap()
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 0, 8, *drawable.get_size())
        pixbuf = pixbuf.get_from_drawable(drawable, colormap, 0, 0, 0, 0, *drawable.get_size()) 
        self.__edit_picture(pixbuf)
        container_remove_all(self.button_hbox)
        self.button_hbox.pack_start(self.button_zoom_in_align)
        self.button_hbox.pack_start(self.button_zoom_out_align)
        self.button_hbox.pack_start(self.button_camera_again_align)
        self.button_hbox.show_all()
        self.panel.hide_panel()

    def on_zoom_in_clicked_cb(self, button):
        if self.pixbuf_w >= self.origin_pixbuf_width or self.pixbuf_h >= self.origin_pixbuf_height:
            print "has max size"
            button.set_sensitive(False)
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
        if self.pixbuf_w >= self.origin_pixbuf_width or self.pixbuf_h >= self.origin_pixbuf_height:
            button.set_sensitive(False)
        if not (self.pixbuf_w <= self.MIN_SIZE or self.pixbuf_h <= self.MIN_SIZE) \
                and not self.button_zoom_out.get_sensitive():
            self.button_zoom_out.set_sensitive(True)

    def on_zoom_out_clicked_cb(self, button):
        if self.pixbuf_w <= self.MIN_SIZE or self.pixbuf_h <= self.MIN_SIZE:
            print "has min size"
            button.set_sensitive(False)
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
        self.__update_drag_point_coord()
        if self.pixbuf_w <= self.MIN_SIZE or self.pixbuf_h <= self.MIN_SIZE:
            button.set_sensitive(False)
        if not (self.pixbuf_w >= self.origin_pixbuf_width or self.pixbuf_h >= self.origin_pixbuf_height) \
                and not self.button_zoom_in.get_sensitive():
            self.button_zoom_in.set_sensitive(True)

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
            self.button_zoom_in.set_sensitive(False)
            self.button_zoom_out.set_sensitive(False)
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
        self.__update_button_sensitive()

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
        if not self.camera_focus_flag:
            return
        if not self.drag_flag and not self.move_flag and not self.__button_moving_flag:
            x, y, w, h = widget.allocation
            if not self.__show_button_flag and \
                    y+self.AREA_HEIGHT-self.button_hbox_height<event.y<y+self.AREA_HEIGHT:
                self.slide_button_show()
                return
            if self.__show_button_flag and \
                    y<event.y<y+self.AREA_HEIGHT-self.button_hbox_height and\
                    not self.__refresh_time_id:
                self.slide_button_hide()
                return
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

    def __on_camera_motion_notify_cb(self, widget, event):
        if not self.camera_focus_flag:
            return
        x, y, w, h = widget.allocation
        if not self.panel.get_visible() and \
                y+self.AREA_HEIGHT-self.button_hbox_height<event.y<y+self.AREA_HEIGHT:
            if self.__refresh_time_id:
                gtk.timeout_remove(self.__refresh_time_id)
            if self.__button_time_id:
                gtk.timeout_remove(self.__button_time_id)
            self.__button_time_id = gobject.timeout_add(50, self.__slide_camera_button_show)
            panel_size = self.button_camera.get_size_request()
            self.panel_layout.move(self.button_camera_align,
                                  (self.AREA_WIDTH-panel_size[0])/2, self.button_hbox_height)
            x = event.x_root - event.x
            y = event.y_root - event.y + self.AREA_HEIGHT - self.button_hbox_height
            self.panel.move(int(x), int(y))
            #print "show panel", x, y, self.button_camera_align.allocation
            self.panel.show_panel()

    def __draw_panel_background(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        cr.set_source_rgb(0, 0, 0)
        cr.set_operator(OPERATOR_SOURCE)
        cr.paint()

        cr.set_source_rgba(0, 0, 0, 0.0)
        cr.rectangle(x, y, w, h)
        cr.paint()
        propagate_expose(widget, event)
        return True

    def __on_camera_enter_notify_cb(self, widget, event):
        pass

    def __on_camera_leave_notify_cb(self, widget, event):
        x, y, w, h = widget.allocation
        if x < event.x < x+w and y < event.y < y+h:
            return
        if self.__button_time_id:
            gtk.timeout_remove(self.__button_time_id)
        self.__button_time_id = gobject.timeout_add(50, self.__slide_camera_button_hide)

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
        self.__camera_picture()
        self.__refresh_camera_button()
        self.button_hbox.hide_all()

    def __camera_picture(self):
        self.set_pixbuf(None)
        if self.edit_area in self.box.get_children():
            self.box.remove(self.edit_area)
        if not self.camera_area in self.box.get_children():
            self.box.pack_start(self.camera_area, False, False)
            self.box.reorder_child(self.camera_area, 0)
        self.show_all()
        try:
            if not self.camera_area.video_player:
                self.camera_area.create_video_pipeline()
            else:
                self.camera_start()
        except Exception, e:
            print e

    def set_edit_mode(self, pixbuf):
        self.current_mode = self.MODE_EDIT
        self.__edit_picture(pixbuf)
        container_remove_all(self.button_hbox)
        self.button_hbox.pack_start(self.button_zoom_in_align)
        self.button_hbox.pack_start(self.button_zoom_out_align)

    def __edit_picture(self, pixbuf):
        self.set_pixbuf(pixbuf)
        if self.camera_area in self.box.get_children():
            self.box.remove(self.camera_area)
        if not self.edit_area in self.box.get_children():
            self.box.pack_start(self.edit_area, False, False)
            self.box.reorder_child(self.edit_area, 0)
        self.show_all()
        self.camera_stop()
        self.__refresh_button()

    def __update_button_sensitive(self):
        if self.pixbuf_w >= self.origin_pixbuf_width or self.pixbuf_h >= self.origin_pixbuf_height:
            self.button_zoom_in.set_sensitive(False)
        else:
            self.button_zoom_in.set_sensitive(True)
        if self.pixbuf_w <= self.MIN_SIZE or self.pixbuf_h <= self.MIN_SIZE:
            self.button_zoom_out.set_sensitive(False)
        else:
            self.button_zoom_out.set_sensitive(True)

    def camera_start(self):
        try:
            self.camera_area.play()
        except Exception, e:
            print e
            pass

    def camera_stop(self):
        try:
            self.camera_area.stop()
        except Exception, e:
            print e
            pass

    def slide_button_show(self):
        self.move(self.button_hbox, 0, self.AREA_HEIGHT)
        self.__button_moving_flag = True
        if self.__refresh_time_id:
            gtk.timeout_remove(self.__refresh_time_id)
        if self.__button_time_id:
            gtk.timeout_remove(self.__button_time_id)
        self.__button_time_id = gobject.timeout_add(50, self.__slide_button_show)
        self.position = self.POS_OUT
        self.set_cursor()

    def slide_button_hide(self):
        self.move(self.button_hbox, 0, self.AREA_HEIGHT-self.button_hbox_height)
        self.__button_moving_flag = True
        if self.__refresh_time_id:
            gtk.timeout_remove(self.__refresh_time_id)
        if self.__button_time_id:
            gtk.timeout_remove(self.__button_time_id)
        self.__button_time_id = gobject.timeout_add(50, self.__slide_button_hide)
        self.position = self.POS_OUT
        self.set_cursor()

    def __slide_button_hide(self):
            step = self.button_hbox_height / 5
            y0 = self.button_hbox.allocation.y
            if y0 + step <= self.AREA_HEIGHT:
                self.move(self.button_hbox, 0, y0+step)
                return True
            self.__button_moving_flag = False
            self.__show_button_flag = False
            self.__button_time_id = None
            return False

    def __slide_button_show(self):
            step = self.button_hbox_height / 5
            y0 = self.button_hbox.allocation.y
            h = self.button_hbox.allocation.height
            if y0 + h - step >= self.AREA_HEIGHT:
                self.move(self.button_hbox, 0, y0-step)
                return True
            self.__button_moving_flag = False
            self.__show_button_flag = True
            self.__button_time_id = None
            return False

    def __refresh_button(self):
        self.__show_button_flag = True
        self.__button_moving_flag = True
        if self.__button_time_id:
            gtk.timeout_remove(self.__button_time_id)
        if self.__refresh_time_id:
            gtk.timeout_remove(self.__refresh_time_id)
        self.__refresh_time_id = gobject.timeout_add(2000, self.__refresh_hide_button)
        self.move(self.button_hbox, 0, self.AREA_HEIGHT-self.button_hbox_height)
            
    def __refresh_hide_button(self):
        if self.__button_time_id:
            gtk.timeout_remove(self.__button_time_id)
        self.__button_time_id = gobject.timeout_add(50, self.__slide_button_hide)
        self.__refresh_time_id = None
        return False

    def __refresh_camera_button(self):
        if self.__button_time_id:
            gtk.timeout_remove(self.__button_time_id)
        if self.__refresh_time_id:
            gtk.timeout_remove(self.__refresh_time_id)
        self.__refresh_time_id = gobject.timeout_add(2000, self.__refresh_hide_camera_button)
        panel_size = self.button_camera.get_size_request()
        self.panel_layout.move(self.button_camera_align, (self.AREA_WIDTH-panel_size[0])/2, 0)
        self.panel.move(self.__win_pos_x+TEXT_WINDOW_LEFT_PADDING,
                        self.__win_pos_y+TEXT_WINDOW_TOP_PADDING+30+self.AREA_HEIGHT-self.button_hbox_height)
        self.panel.show_panel()

    def __refresh_hide_camera_button(self):
        if self.__button_time_id:
            gtk.timeout_remove(self.__button_time_id)
        self.__button_time_id = gobject.timeout_add(50, self.__slide_camera_button_hide)
        self.__refresh_time_id = None
        return False

    def __slide_camera_button_hide(self):
            step = self.button_hbox_height / 5
            y0 = self.button_camera_align.allocation.y
            panel_size = self.button_camera.get_size_request()
            if y0 + step <= self.button_hbox_height:
                self.panel_layout.move(self.button_camera_align,
                                      (self.AREA_WIDTH-panel_size[0])/2, y0+step)
                return True
            self.__button_time_id = None
            self.panel.hide_panel()
            return False

    def __slide_camera_button_show(self):
            step = self.button_hbox_height / 5
            y0 = self.button_camera_align.allocation.y
            h = self.button_camera_align.allocation.height
            panel_size = self.button_camera.get_size_request()
            if y0 + h - step >= self.button_hbox_height:
                self.panel_layout.move(self.button_camera_align,
                                      (self.AREA_WIDTH-panel_size[0])/2, y0-step)
                return True
            self.__button_time_id = None
            return False

    def set_win_pos(self, x, y):
        self.__win_pos_x = int(x)
        self.__win_pos_y = int(y)

    def is_toolbar_show(self):
        return self.__show_button_flag

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
        left_vbox.pack_start(tools.make_align(self.draw_area, yalign=0.0, width=300, height=300))

        self.thumbnail_large = gtk.Image()
        self.thumbnail_mid = gtk.Image()
        self.thumbnail_small = gtk.Image()
        self.thumbnail_large.set_size_request(150, 150)
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
        self.draw_area.camera_stop()

    def save_edit_icon(self):
        pixbuf = self.thumbnail_large.get_pixbuf()
        if not pixbuf:
            #self.error_label.set_text("<span foreground='red'>%s%s</span>" % (
                #_("Error:"), _("no picture")))
            self.account_setting.set_status_error_text(_("no picture"))
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
                os.chmod(backup_path, S_IRWXU|S_IRWXG|S_IRWXO)
                history_icon.history.insert(0, backup_path)
                history_icon.set_history(history_icon.history)
        except Exception, e:
            if isinstance(e, (AccountsPermissionDenied, AccountsUserExists, AccountsFailed, AccountsUserDoesNotExist)):
                #self.error_label.set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), e.msg))
                self.account_setting.set_status_error_text(e.msg)
                return
        self.stop_camera()
        self.account_setting.set_to_page(
            self.account_setting.alignment_widgets["main_hbox"], "left")
        self.account_setting.change_crumb(1)

    def __on_pixbuf_changed_cb(self, widget, pixbuf):
        if pixbuf:
            self.thumbnail_large.set_from_pixbuf(pixbuf.scale_simple(
                150, 150, gtk.gdk.INTERP_BILINEAR))
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

    def set_win_pos(self, x, y):
        self.draw_area.set_win_pos(x, y)
gobject.type_register(IconEditPage)
