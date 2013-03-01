#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Deepin, Inc.
#               2013 Hailong Qiu
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

from vtk.utils import is_usb_device, get_text_size
from vtk.draw import draw_pixbuf, draw_text
from dtk.ui.line import HSeparator
from nls import _
import gtk
import gio
import glib
import gobject


ICON_SIZE = 16

class Device(gtk.Button):
    __gsignals__ = {
    "unmounted-event" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    "removed-event" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
    }
    def __init__(self, drive, device):
        gtk.Button.__init__(self)
        self.drive  = drive
        self.device = device
        self.conf = Conf()

        self.eject_check = False
        try:
            get_m = drive.get_volumes()[0].get_mount()
            if get_m == None:
                self.set_mounted(False)
        except Exception, e:
            print "Device[error]:", e

        self.was_removed = False
        self.icon_updated = False
        self.d_name = ""
        self.description = ""
        self.volumes = []
        self.mounts  = []
        self.volume_count = 0;
        self.mount_count  = 0;
        self.icon = gtk.image_new_from_gicon(self.drive.get_icon(), ICON_SIZE)
        self.off_pixbuf = gtk.gdk.pixbuf_new_from_file("image/offbutton/off.png")
        self.on_pixbuf = gtk.gdk.pixbuf_new_from_file("image/offbutton/on.png")
        #
        self.connect("clicked", self.clicked_eject)
        self.drive.connect("disconnected", self.handle_removed_drive)
        #
        self.set_label("")
        self.set_image(self.icon)
        self.connect("expose-event", self.device_expose_event)
        self.show_all()

    def device_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        #
        text = widget.get_label().decode("utf-8")
        text_width = get_text_size("ABCDEFABCDEFH")[0]
        ch_width = get_text_size("a")[0]
        dec_width = get_text_size(text)[0] - text_width
        if dec_width > 0:
            index = dec_width/ch_width
            text = text[0:len(text)-index] + "..."
        if self.eject_check:
            simple_pixbuf = self.on_pixbuf
            text_color_value = "#000000"
        else:
            simple_pixbuf = self.off_pixbuf
            text_color_value = "#9d9d9d"

        draw_text(cr, 
                  text, 
                  rect.x, 
                  rect.y, 
                  text_color=text_color_value,
                  text_size=9)
        draw_pixbuf(cr, 
                    simple_pixbuf, 
                    rect.x + rect.width - simple_pixbuf.get_width(), 
                    rect.y)
        return True

    def clicked_eject(self, widget):
        op = gtk.MountOperation()
        if self.drive.can_eject():
            try:
                self.drive.eject(self.cancallable_operation,
                                gio.MOUNT_OPERATION_HANDLED)
                self.emit("unmounted-event")
            except Exception,e:
                print "error:", e
        else:
            for v in self.drive.get_volumes():
                try:
                    if v.get_mount():
                        v.eject(self.cancallable_operation,
                                gio.MOUNT_OPERATION_HANDLED)
                        self.emit("unmounted-event")
                    else:
                        v.mount(op, self.cancallable_operation)
                except Exception, e:
                    print "error:", e

    def cancallable_operation(self, obj, res):
        pass

    def handle_unmounted(self, mount):
        self.mounts.remove(mount)
        self.mount_count = self.mount_count - 1;
        self.update_label()

        if self.mount_count <= 0:
            self.set_mounted(False)
            self.emit("unmounted-event")

    def handle_removed_drive(self, drive):
        id = drive.get_identifier(self.conf.device_identifier)
        self.emit("removed-event", id)

    def handle_removed_volume(self, volume):
        self.volumes.remove(volume)
        self.volume_count = self.volume_count - 1;
        self.update_label()

        if self.volume_count == 0:
            id = self.drive.get_identifier(self.conf.device_identifier)
            self.emit("removed-event", id)

    def add_volume(self, volume):
        self.volumes.insert(0, volume)
        self.volume_count = self.volume_count + 1
        volume.connect("removed", self.handle_removed_volume)

        if not self.icon_updated:
            self.icon = gtk.image_new_from_gicon(volume.get_icon(), ICON_SIZE)
            self.icon_updated = True

        self.update_label()

    def add_mount(self, mount):
        volume = mount.get_volume()
        # add volume.
        if not (volume in self.volumes):
            self.add_volume(volume)

        try:
            self.mounts.remove(mount)
        except:
            pass
        self.mounts.insert(0, mount)

        self.mount_count = self.mount_count + 1
        self.set_mounted(True)
        mount.connect("unmounted", self.handle_unmounted)
        self.update_label()

    def update_label(self):
        if self.volume_count == 0:
            self.d_name = self.drive.get_name()
            self.description = ""
        elif self.volume_count == 1:
            v = self.volumes[0]
            self.d_name = v.get_name()
            self.description = self.drive.get_name()
        else:
            volumes = ""
            first = True

            for v in self.volumes:
                if first:
                    volumes = volumes + v.get_name()
                    first = False
                else:
                    volumes = volumes + ", " + v.get_name()

            self.d_name = self.drive.get_name()
            self.description = volumes
            
        # set show label.
        #print "name:", self.d_name
        #print "description:", self.description
        #self.set_label(self.d_name + " (" + self.description + ")")
        self.set_label(self.d_name)

    def d_remove(self):
        if self.was_removed:
            return False;
        self.meit("removed")
        self.was_removed = True

    def set_mounted(self, mounted):
        self.eject_check = mounted

gobject.type_register(Device)

class Conf(object):
    def __init__(self):
        self.device_identifier = "unix-device"
        self.show_internal = False

class EjecterApp(gobject.GObject):
    __gsignals__ = {
    "update-usb" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    "remove-usb" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    "empty-usb" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    def __init__(self):
        gobject.GObject.__init__(self)
        self.__init_values()
        self.__init_ejecter_settings()

    def __init_values(self):
        hseparator_color = [(0,   ("#777777", 0.0)),
                            (0.5, ("#000000", 0.3)),
                            (1,   ("#777777", 0.0))
                           ]
        self.hbox = gtk.HBox()
        self.title_image = gtk.image_new_from_file("image/usb/usb_label.png")
        self.title_label = gtk.Label(_("USB Device"))
        self.title_label.connect("expose-event", self.title_label_expose_event)
        self.title_label_ali = gtk.Alignment(0, 0, 0, 0)
        self.title_label_ali.set_padding(0, 0, 0, 0)
        self.title_label_ali.add(self.title_label)

        self.hbox.pack_start(self.title_image, False, False)
        self.hbox.pack_start(self.title_label_ali, True, True)

        self.h_separator_top = HSeparator(hseparator_color, 0, 0)
        self.h_separator_ali = gtk.Alignment(1, 1, 1, 1)
        self.h_separator_ali.set_padding(5, 10, 0, 0)
        self.h_separator_ali.add(self.h_separator_top)

        self.vbox = gtk.VBox()
        self.vbox.pack_start(self.hbox, False, False)
        self.vbox.pack_start(self.h_separator_ali, True, True)

        self.conf = Conf()
        self.devices = {}
        self.invalid_devices = [] 
        self.monitor = gio.VolumeMonitor()

    def title_label_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        text = widget.get_label()
        size = get_text_size(text)
        draw_text(cr, 
                  text, 
                  rect.x + 5, 
                  rect.y + rect.height - size[1] + 1,
                  text_color="#000000",
                  text_size=9)
        return True

    def __init_ejecter_settings(self):
        self.load_devices()
        self.monitor.connect("volume-added", self.volume_added)
        self.monitor.connect("mount-added", self.mount_added)

    def volume_added(self, monitor, volume):
        #print "volume_added..."
        self.monitor_manage_volume(volume)

    def mount_added(self, monitor, mount):
        #print "mount_added..."
        self.monitor_manage_mount(mount)


    def load_devices(self):
        for v in self.monitor.get_volumes():
            d = v.get_drive()
            
            self.monitor_manage_drive(d)
            self.monitor_manage_volume(v)

            m = v.get_mount()
            if m != None:
                self.monitor_manage_mount(m)
        #self.check_icon()

    def monitor_manage_drive(self, drive):
        # gio.Drive 
        #print "monitor_manage_drive..."
        if drive == None:
            return False
        
        id = drive.get_identifier(self.conf.device_identifier)
        #print "id:", id, drive.get_name()
        if is_usb_device(id):
            d = Device(drive, 0)
            self.devices[id] = d

            self.vbox.pack_start(d, True, True) 
            self.vbox.show_all()
            self.emit("update-usb")

            d.connect('unmounted-event', self.d_unmounted_event)
            d.connect('removed-event', self.d_removed_event)

    def d_unmounted_event(self, device):
        #print "d_unmounted_event..."
        pass

    def d_removed_event(self, device, id):
        if self.devices.has_key(id):
            #print "d_removed_event...", id, self.devices[id]
            self.vbox.remove(self.devices[id])
            del self.devices[id]
            self.vbox.show_all()
            self.emit("remove-usb")
            if self.devices == {}:
                self.emit("empty-usb")
        
    def monitor_manage_volume(self, v):
        # gio.Volume
        #print "monitor_manage_volume..."
        drive = v.get_drive()
        id = drive.get_identifier(self.conf.device_identifier)
        if id == None: 
            return False

        try: 
            dev = self.devices[id]
            if dev == None:
                return False
            dev.add_volume(v)
        except:
            #print "create dev..."
            self.monitor_manage_drive(drive)
            #dev = self.devices[id]


    def monitor_manage_mount(self, m):
        # gio.Mount
        #print "monitor_manage_mount..."
        drive = m.get_drive()
        #print m.get_name(), drive.get_name()
        id = drive.get_identifier(self.conf.device_identifier) 
        if id == None:
            return False

        try:
            dev = self.devices[id]
            if dev == None:
                return False
        except:
            return False

        dev.add_mount(m)


if __name__ == "__main__":
    EjecterApp()
    gtk.main()

