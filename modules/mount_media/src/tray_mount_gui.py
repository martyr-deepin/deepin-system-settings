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

import sys
import os
from deepin_utils.file import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from theme import app_theme
from dtk.ui.dialog import ConfirmDialog
from dtk.ui.line import HSeparator
from vtk.draw  import draw_text, draw_pixbuf
from vtk.utils import get_text_size
from nls import _
from permanent_settings import get_auto_mount

import os
import sys
import gtk
import gio
import gobject

import pynotify
pynotify.init("Storage Device")
def notify_message(summary, body):
    noti = pynotify.Notification(summary, body, "/usr/share/icons/Deepin/apps/48/mountmanager.png")
    noti.show()

image_path = os.path.dirname(sys.argv[0])
ICON_SIZE = 16

#class Device(gtk.Button):
class Device(gtk.HBox):
    def __init__(self):
        #gtk.Button.__init__(self)
        gtk.HBox.__init__(self)
        self.icon_image_event = gtk.EventBox()
        self.icon_image_event.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.icon_image  = gtk.Image()
        self.icon_image_event.add(self.icon_image)
        self.open_btn  = gtk.Button()
        self.close_btn = gtk.Button()
        self.open_btn.connect("expose-event", self.open_btn_expose_event)
        self.open_btn.connect("enter-notify-event", self.set_cursor_enter_notify_event)
        self.open_btn.connect("leave-notify-event", self.set_cursor_leave_notify_event)
        self.icon_image_event.connect("enter-notify-event", self.set_cursor_enter_notify_event)
        self.icon_image_event.connect("leave-notify-event", self.set_cursor_leave_notify_event)
        self.close_btn.connect("enter-notify-event", self.close_btn_set_cursor_enter_notify_event)
        self.close_btn.connect("leave-notify-event", self.set_cursor_leave_notify_event)

        self.close_btn.connect("expose-event", self.close_btn_expose_event)
        self.pack_start(self.icon_image_event, False, False)
        self.pack_start(self.open_btn, True, True, 5)
        self.pack_start(self.close_btn, False, False)
        self.icon_image.set_size_request(20, 20)
        self.__init_values()

    def close_btn_set_cursor_enter_notify_event(self, widget, event):
        self.__set_cursor_type(widget, cursor_type = gtk.gdk.HAND2)

    def set_cursor_enter_notify_event(self, widget, event):
        if self.eject_check:
            self.__set_cursor_type(widget, cursor_type = gtk.gdk.HAND2)

    def set_cursor_leave_notify_event(self, widget, event):
        self.__set_cursor_type(widget, cursor_type = None)

    def __set_cursor_type(self, widget, cursor_type):
        if isinstance(widget, gtk.Widget):
            cursor_window = widget.window
        elif isinstance(widget, gtk.gdk.window):
            cursor_window = widget
        if cursor_type == None:
            cursor_window.set_cursor(None)
        else:
            cursor_window.set_cursor(gtk.gdk.Cursor(cursor_type))

    def __init_values(self):
        self.eject_check = False
        self.icon_pixbuf = None
        self.off_pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(image_path, "image/offbutton/off.png"))
        self.on_pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(image_path, "image/offbutton/on.png"))
        close_w = self.on_pixbuf.get_width()
        close_h = self.on_pixbuf.get_height()
        self.close_btn.set_size_request(close_w, close_h)
        self.show_all()

    def open_btn_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        text = widget.get_label().decode("utf-8")
        text_width = get_text_size("ABCDEFABCDEFH", text_size=9)[0]
        ch_width = get_text_size("a", text_size=9)[0]
        dec_width = get_text_size(text, text_size=9)[0] - text_width
        if dec_width > 0:
            index = (dec_width/ch_width) + 2
            text = text[0:len(text)-index] + "..."
        if self.eject_check:
            text_color_value = "#000000"
        else:
            text_color_value = "#9d9d9d"
        draw_text(cr, 
                  text, 
                  rect.x, 
                  rect.y + rect.height/2 - get_text_size(text)[1]/2, 
                  text_color=text_color_value,
                  text_size=9)
        return True

    def close_btn_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation

        if self.eject_check:
            simple_pixbuf = self.on_pixbuf
        else:
            simple_pixbuf = self.off_pixbuf

        draw_pixbuf(cr, 
                    simple_pixbuf, 
                    rect.x,
                    rect.y + rect.height/2 - simple_pixbuf.get_height()/2)
        return True

    def set_eject_check(self, check):
        self.eject_check = check
        self.queue_draw()

class EjecterApp(gobject.GObject):
    '''
    __gsignals__ = {
    "update-usb" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    "remove-usb" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    "empty-usb" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    '''
    def __init__(self):
        gobject.GObject.__init__(self)
        self.__init_values()
        self.__load_monitor()
        self.__init_monitor_events()

    def __init_values(self):
        hseparator_color = [(0,   ("#777777", 0.0)),
                            (0.5, ("#000000", 0.3)),
                            (1,   ("#777777", 0.0))
                           ]
        self.height = 0
        self.size_check = False
        self.hbox = gtk.HBox()
        self.title_image = gtk.image_new_from_file(os.path.join(image_path, "image/usb/usb_label.png"))
        self.title_label = gtk.Label(_("Storage Device"))
        #self.title_label.connect("expose-event", self.title_label_expose_event)
        self.title_label_ali = gtk.Alignment(0, 0, 0, 0)
        self.title_label_ali.set_padding(0, 0, 0, 0)
        self.title_label_ali.add(self.title_label)
        
        self.hbox.pack_start(self.title_image, False, False)
        self.hbox.pack_start(self.title_label_ali, True, True)

        self.h_separator_top = HSeparator(hseparator_color, 0, 0)
        self.h_separator_ali = gtk.Alignment(1, 1, 1, 1)
        self.h_separator_ali.set_padding(5, 10, 0, 0)
        self.h_separator_ali.add(self.h_separator_top)

        self.monitor_vbox = gtk.VBox()
        self.vbox = gtk.VBox()
        self.vbox.pack_start(self.hbox, False, False)
        self.vbox.pack_start(self.h_separator_ali, True, True)
        self.vbox.pack_start(self.monitor_vbox, True, True)

        self._ask_confirmed = False
        self.monitor = gio.VolumeMonitor()
        self.op = gio.MountOperation()        
        
    def __load_monitor(self):
        # 移除挂载上的控件.
        self.height = 75
        self.width = 210
        for widget in self.monitor_vbox.get_children():
            self.monitor_vbox.remove(widget)
        self.network_mounts_list = []
        self.network_volumes_list = []
        
        drives = self.monitor.get_connected_drives()
        # 获取大硬盘下的东西.
        for drive in drives:
            volumes = drive.get_volumes() 
            if volumes:
                for volume in volumes:
                    id = volume.get_identifier("unix-device")
                    if id.startswith("network"):
                        self.network_volumes_list.append(volume)
                        continue
                    mount = volume.get_mount()
                    if mount: # moutn != None
                        icon = mount.get_icon() 
                        root  = mount.get_root()
                        mount_uri = root.get_uri()
                        tooltip   = root.get_parse_name()
                        name = mount.get_name()
                        #
                        self.__add_place(
                                name, icon, mount_uri, tooltip, 
                                drive, volume, mount)
                    else:
                        icon = volume.get_icon() 
                        name = volume.get_name()
                        self.__add_place(
                                name, icon, None, None,
                                drive, volume, None)
            else: # volumes.
                if (drive.is_media_removable() and 
                    not drive.is_media_check_automatic()):
                    icon = drive.get_icon()
                    name = drive.get_name()
                    self.__add_place(
                            name, icon, None, None,
                            drive, None, None)

        volumes = self.monitor.get_volumes()
        for volume in volumes:
            drive = volume.get_drive()
            if drive:
                continue
            id = volume.get_identifier("unix-device")

            mount = volume.get_mount()
            if mount:
                icon = mount.get_icon()
                root = mount.get_root()
                name = mount.get_name()
                mount_uri  = root.get_uri()
                tooltip   = root.get_parse_name()
                self.__add_place(
                        name, icon, mount_uri, tooltip,
                        None, volume, mount)
            else:
                icon = volume.get_icon()
                name = volume.get_name()
                self.__add_place(
                        name, icon, None, None,
                        None, volume, None)

        mounts = self.monitor.get_mounts() 
        for mount in mounts:
            if mount.is_shadowed():
                continue
            volume = mount.get_volume()
            if volume:
                continue
            root = mount.get_root()
            if not root.is_native():
                # 保存到网络列表中.
                self.network_mounts_list.insert(0, mount)
                continue;

            icon      = mount.get_icon()
            mount_uri = root.get_uri()
            tooltip   = root.get_parse_name()
            name      = mount.get_name()
            self.__add_place(
                    name, icon, mount_uri, tooltip,
                    None, None, mount)

        # mounts  网络列表过滤.
        for mount in self.network_mounts_list:
            root = mount.get_root()
            icon = mount.get_icon()
            mount_uri = root.get_uri()
            tooltip   = root.get_parse_name()
            name = mount.get_name()
            self.__add_place(
                    name, icon, mount_uri, tooltip, 
                    None, None, mount)
        # 设置高度.
        self.set_menu_size(self.height)

    def __add_place(self, 
                    name, icon, uri, tooltip, 
                    drive, volume, mount):
        show_unmount, show_eject = self.__set_mount_and_eject_bit(drive, volume, mount)
        device_btn = Device()
        #set_clickable_cursor(device_btn.open_btn)
        #
        # 设置图标右边的显示标志位.
        if mount == None:
            device_btn.set_eject_check(False)
        else:
            device_btn.set_eject_check((show_unmount or show_eject))
        # 设置图标.
        device_btn.icon_image.set_from_gicon(icon, 1)
        # 设置名字.
        device_btn.open_btn.set_label(name)
        if tooltip:
            device_btn.set_tooltip_text(tooltip)
        # 连接事件.
        device_btn.icon_image_event.connect("button-press-event", self.device_btn_icon_image_button_press_event, uri)
        device_btn.open_btn.connect("clicked", self.device_btn_open_btn_clicked, uri)
        device_btn.close_btn.connect("clicked", self.device_btn_close_btn_clicked, drive, volume, mount)
        #
        self.monitor_vbox.pack_start(device_btn)
        self.monitor_vbox.show_all()
        self.height += 23

    def set_menu_size(self, height):
        pass

    def device_btn_icon_image_button_press_event(self, widget, event, uri):
        pass

    def device_btn_open_btn_clicked(self, widget, uri):
        pass

    def run_open_dir_command(self, uri):
        pass

    def device_btn_close_btn_clicked(self, widget, drive, volume, mount):
        pass

    def __set_mount_and_eject_bit(self, drive, volume, mount):
        show_unmount = False # 是否存在.
        show_eject   = False # 是否挂载上去了.
        if drive:
            show_eject = drive.can_eject()
        if volume:
            show_eject = volume.can_eject()
        if mount:
            show_eject = mount.can_eject()
            show_unmount = (mount.can_unmount() and (not show_eject))
        return show_unmount, show_eject

    def __init_monitor_events(self):
        # mount events.
        self.monitor.connect("mount-added", self.mount_added_callback)
        self.monitor.connect("mount-removed", self.mount_removed_callback)
        self.monitor.connect("mount-changed", self.mount_changed_callback)
        # volume events.
        self.monitor.connect("volume-added", self.volume_added_callback)
        self.monitor.connect("volume-removed", self.volume_removed_callback)
        self.monitor.connect("volume-changed", self.volume_changed_callback)
        # drive events.
        self.monitor.connect("drive-disconnected", self.drive_disconnected_callback)
        self.monitor.connect("drive-connected", self.drive_connected_callback)
        self.monitor.connect("drive-changed", self.drive_changed_callback)

    def mount_added_callback(self, volume_monitor, mount):
        print "mount added"
        if get_auto_mount() == "mount_and_open" or self._ask_confirmed:
            os.popen("xdg-open %s" % (mount.get_root().get_uri()))
            self._ask_confirmed = False

        self.__load_monitor()

    def mount_removed_callback(self, volume_monitor, mount):
        print "mount removed"
        self.__load_monitor()

    def mount_changed_callback(self, volume_monitor, mount):
        print "mount changed"
        self.__load_monitor()

    def volume_added_callback(self, volume_monitor, volume):
        print "volume added"
        
        def confirm_cb():
            if not volume.get_mount():
                self._ask_confirmed = True
                volume.mount(self.op, self.cancall_opeartion, flags=gio.MOUNT_MOUNT_NONE)
            
        auto = get_auto_mount()
        if auto == "mount" or auto == "mount_and_open":
            if not volume.get_mount():
                volume.mount(self.op, self.cancall_opeartion, flags=gio.MOUNT_MOUNT_NONE)
        elif auto == "ask":
            ConfirmDialog(_("Storage Device"), 
                          _("Mount and open device \"%s\"?") % volume.get_name(),
                          confirm_callback=confirm_cb).show_all()

        self.__load_monitor()

    def volume_removed_callback(self, volume_monitor, volume):
        print "volume removed"
        self.__load_monitor()

    def volume_changed_callback(self, volume_monitor, volume):
        print "volume changed"
        self.__load_monitor()

    def drive_disconnected_callback(self, volume_monitor, drive):
        print "drive disconnected"
        notify_message(_("Storage Device"), _("Removable media \"%s\" has been removed") % drive.get_name())
        self.__load_monitor()

    def drive_connected_callback(self, volume_monitor, drive):
        print "drive connected"
        notify_message(_("Storage Device"), _("Found new removable media \"%s\"") % drive.get_name())
        self.__load_monitor()

    def drive_changed_callback(self, volume_monitor, drive):
        print "drive changed"
        self.__load_monitor()
        
if __name__ == "__main__":
    import gtk
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    
    eject = EjecterApp()
    win.add(eject.vbox)
    win.show_all()
    
    gtk.main()


