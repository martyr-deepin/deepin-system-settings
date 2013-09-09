#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang YaoHua
# 
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
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
import gobject
from nls import _
from theme import app_theme
from webcam import Webcam
from dtk.ui.button import Button
from dtk.ui.utils import cairo_disable_antialias, color_hex_to_cairo
from dtk.ui.draw import draw_pixbuf

CAMERA_BOX_SIZE = 140
WEBCAM_SIZE = 130
WIDGET_SPACING = 20

class FaceRecordPage(gtk.VBox):
    def __init__(self, account_setting):
        gtk.VBox.__init__(self)
        self.account_setting = account_setting
        
        self.camera_box_align = gtk.Alignment(0.5, 0, 0, 0)
        self.camera_box = gtk.VBox()
        self.camera_box.set_size_request(CAMERA_BOX_SIZE, CAMERA_BOX_SIZE)
        self.camera_box.connect("expose-event", self.__camera_box_expose)
        self.camera_box_align.add(self.camera_box)
        
        self.under_camera_box = gtk.VBox()
        self.under_camera_box_align = gtk.Alignment(0.5, 0, 0, 0)
        self.under_camera_box_align.set_padding(WIDGET_SPACING, 0, 0, 0)
        self.under_camera_box_align.add(self.under_camera_box)
        self.__init_buttons()
        self.under_camera_box.pack_start(self.start_record_button)
        
        self.pack_start(self.camera_box_align, False, False)
        self.pack_start(self.under_camera_box_align, False, False)
        
        self.camera_pixbuf = app_theme.get_pixbuf("account/camera.png").get_pixbuf()
        
    def __init_buttons(self):
        self.start_record_button = Button(_("Start"))
        self.start_record_button.set_size_request(CAMERA_BOX_SIZE, 25)
        self.start_record_button.connect("clicked", self.__start_record_clicked)
    
    def refresh(self):
        pass
    
    def __start_record_clicked(self, widget):
        self.webcam_align = gtk.Alignment(0, 0.5, 0, 0)
        self.webcam_align.set_padding(5, 5, 5, 5)
        if not hasattr(self.account_setting, "record_webcam"):
            self.account_setting.record_webcam = Webcam()
            self.account_setting.record_webcam.set_size_request(WEBCAM_SIZE, 120)
            self.account_setting.record_webcam.create_video_pipeline(160, 120)
        self.webcam_align.add(self.account_setting.record_webcam)
        self.camera_box.add(self.webcam_align)
        self.account_setting.record_webcam.play()
        gobject.timeout_add(2000, self.__do_action)
        
    def __do_action(self):
        self.snapshot_pixbuf = self.account_setting.record_webcam.get_snapshot()
        self.snapshot_pixbuf.save("/tmp/face_recognition.png", "png")
        self.account_setting.record_webcam.pause()
        self.webcam_align.remove(self.account_setting.record_webcam)
    
    def __camera_box_expose(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        # draw frame
        with cairo_disable_antialias(cr):
            cr.rectangle(x, y, w, h)
            cr.set_line_width(1)
            cr.set_source_rgb(*color_hex_to_cairo("#a2a2a2"))
            cr.stroke()
        # draw background
        cr.rectangle(x + 5, y + 5, w - 10, h - 10)
        cr.set_source_rgb(*color_hex_to_cairo("#333333"))
        cr.fill()
        
        # draw camera icon
        if hasattr(self, "scanning") and self.scanning:
            draw_pixbuf(cr, self.snapshot_pixbuf, 
                        x = x + (CAMERA_BOX_SIZE - self.snapshot_pixbuf.get_width()) / 2,
                        y = y + (CAMERA_BOX_SIZE - self.snapshot_pixbuf.get_height()) / 2)
        else:
            draw_pixbuf(cr, self.camera_pixbuf, 
                        x = x + (CAMERA_BOX_SIZE - self.camera_pixbuf.get_width()) / 2,
                        y = y + (CAMERA_BOX_SIZE - self.camera_pixbuf.get_height()) / 2)
        return True
