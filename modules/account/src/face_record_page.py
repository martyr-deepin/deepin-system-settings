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
import dbus
import gobject
import cairo
import getpass
from nls import _
from theme import app_theme
from webcam import Webcam
from dtk.ui.button import Button
from dtk.ui.label import Label
from dtk.ui.utils import cairo_disable_antialias, color_hex_to_cairo, container_remove_all
from dtk.ui.draw import draw_pixbuf

from facepp import API, File
facepp = API("e7d24ca8e91351b8cac02eb6e6080678", "iH_Dls3_gE2wx5dp2cKHPrO8W5V5NTr-")

CAMERA_BOX_SIZE = 140
WEBCAM_SIZE = 130
WIDGET_SPACING = 20

def get_person_name():
    bus = dbus.SystemBus()
    dbus_object = bus.get_object("com.deepin.passwdservice", "/")
    dbus_interface = dbus.Interface(dbus_object, "com.deepin.passwdservice")
    return dbus_interface.cfg_get(getpass.getuser(), "person_name")

class FaceRecordPage(gtk.VBox):
    def __init__(self, account_setting):
        gtk.VBox.__init__(self)
        self.account_setting = account_setting

        self.camera_box_align = gtk.Alignment(0.5, 0, 0, 0)
        self.camera_box = gtk.VBox()
        self.camera_box.set_size_request(CAMERA_BOX_SIZE, CAMERA_BOX_SIZE)
        self.camera_box.connect("expose-event", self.__camera_box_expose)
        self.camera_box_align.add(self.camera_box)

        self.under_camera_box = gtk.VBox(spacing=10)
        self.under_camera_box_align = gtk.Alignment(0.5, 0, 0, 0)
        self.under_camera_box_align.set_padding(WIDGET_SPACING, 0, 0, 0)
        self.under_camera_box_align.add(self.under_camera_box)
        self.__init_widgets()
        self.under_camera_box.pack_start(self.start_record_button)

        self.pack_start(self.camera_box_align, False, False)
        self.pack_start(self.under_camera_box_align, False, False)

        self.camera_pixbuf = app_theme.get_pixbuf("account/camera.png").get_pixbuf()

    def __init_widgets(self):
        self.start_record_button = Button(_("Start"))
        self.start_record_button.set_size_request(CAMERA_BOX_SIZE, 25)
        self.start_record_button.connect("clicked", self.__start_record_clicked)
        
        self.keep_few_minutes = Label(_("Please keep still for 5 seconds"))
        self.success = Label(_("Your face has been successfully recorded"))
        self.fail = Label(_("Face recording failed."))

    def refresh(self):
        pass

    def __start_record_clicked(self, widget):
        container_remove_all(self.under_camera_box)
        self.under_camera_box.pack_start(self.keep_few_minutes)
        
        self.webcam_align = gtk.Alignment(0, 0.5, 0, 0)
        self.webcam_align.set_padding(5, 5, 5, 5)
        if not hasattr(self.account_setting, "record_webcam"):
            self.account_setting.record_webcam = Webcam()
            self.account_setting.record_webcam.set_size_request(WEBCAM_SIZE, 120)
            self.account_setting.record_webcam.create_video_pipeline(160, 120)
        self.webcam_align.add(self.account_setting.record_webcam)
        container_remove_all(self.camera_box)
        self.camera_box.add(self.webcam_align)
        self.account_setting.record_webcam.play()
        gobject.timeout_add(2000, self.__do_save_photo, 0)
        gobject.timeout_add(2500, self.__do_save_photo, 1)
        gobject.timeout_add(3000, self.__do_save_photo, 2)
        gobject.timeout_add(3500, self.__do_save_photo, 3)
        
        gobject.timeout_add(4000, self.__do_action)
        
    def __do_save_photo(self, num):
        pixbuf = self.account_setting.record_webcam.get_snapshot()
        path = "/tmp/face_recognition_%s.png" % num
        pixbuf.save(path, "png")
        
    # def __do_detection(self):
        
    #     def recognition_process(pixbuf):
    #         path = "/tmp/face_recognition_%s.png" % thread.get_ident()
    #         pixbuf.save(path, "png")
    #         result = facepp.detection.detect(img=File(path), mode="oneface")
    #         print result
    #         if result["face"]:
    #             try:
    #                 facepp.person.create(person_name=get_person_name())
    #             except:
    #                 pass
    #             facepp.person.add_face(person_name=get_person_name(), face_id=result["face"][0]["face_id"])
        
    #     pixbuf = self.account_setting.record_webcam.get_snapshot()
    #     # gtk.gdk.threads_enter()
    #     # Thread(target=recognition_process, args=[pixbuf]).start()
    #     # gtk.gdk.threads_leave()
    #     recognition_process(pixbuf)

    def __do_action(self):
        success = 0
        
        try:
            facepp.person.delete(person_name=get_person_name(), timeout=2)
        except:
            pass
        
        try:
            facepp.person.create(person_name=get_person_name(), timeout=2)
        except:
            pass
        
        for i in xrange(3):
            result = facepp.detection.detect(img=File("/tmp/face_recognition_%s.png" % i), 
                                             mode="oneface", timeout=2, retry_delay=3)
            if result["face"]:
                add_result = facepp.person.add_face(person_name=get_person_name(), face_id=result["face"][0]["face_id"], timeout=2)
                print "add_result, ", add_result
                success += 1
        
        self.snapshot_pixbuf = self.account_setting.record_webcam.get_snapshot()
        self.account_setting.record_webcam.stop()
        self.webcam_align.remove(self.account_setting.record_webcam)

        self.scanning_box = ScanningBox(self.snapshot_pixbuf)
        self.scanning_box.set_size_request(WEBCAM_SIZE, WEBCAM_SIZE)
        self.webcam_align.add(self.scanning_box)
        self.webcam_align.show_all()
        
        container_remove_all(self.under_camera_box)
        self.start_record_button.label = _("Another time")
        if success > 0:
            facepp.train.verify(person_name=get_person_name())
            self.under_camera_box.pack_start(self.success)
        else:
            self.under_camera_box.pack_start(self.fail)
        self.under_camera_box.pack_start(self.start_record_button)

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
            
class ScanningBox(gtk.Button):

    def __init__(self, pix):
        gtk.Button.__init__(self)
        self.set_can_focus(True)

        self.pixbuf = pix
        self.scan_line_pixbuf = app_theme.get_pixbuf("account/scan_line.png").get_pixbuf().scale_simple(130, 3, gtk.gdk.INTERP_BILINEAR)
        self.bg_grid_path = app_theme.get_theme_file_path("image/account/bg_grid.png")
        self.progress = WEBCAM_SIZE - 3 # 3 is the height of scan_line.png, if i set progress as webcam_size, 
                                        # there will be some shit remaining.

        self.connect("expose-event", self.__expose)

    def __expose(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        
        if self.progress >= 0:
            surface = cairo.ImageSurface.create_from_png(self.bg_grid_path)
            surface_pattern = cairo.SurfacePattern(surface)
            surface_pattern.set_extend(cairo.EXTEND_REPEAT)
            
            # Draw picture
            draw_pixbuf(cr, self.pixbuf, x, y + (h - self.pixbuf.get_height()) / 2)
            
            # Draw mask
            cr.rectangle(x, y, w, self.progress)
            cr.set_source(surface_pattern)
            cr.fill()
            
            # Draw scanning line.
            draw_pixbuf(cr, self.scan_line_pixbuf, x, y + self.progress)
            
            self.scanning_timeout = gobject.timeout_add(10, lambda : self.queue_draw())
            self.progress -= 1
        else:
            gobject.source_remove(self.scanning_timeout)
            draw_pixbuf(cr, self.pixbuf, x, y + (h - self.pixbuf.get_height()) / 2)            
            
        return True
