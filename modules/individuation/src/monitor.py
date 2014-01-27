#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
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

import gio
import gobject
import glib
import threading

import common

class LibraryMonitor(gobject.GObject):
    """
        Monitors library locations for changes
    """
    __gproperties__ = {
        'monitored': (
            gobject.TYPE_BOOLEAN,
            'monitoring state',
            'Whether to monitor this library',
            False,
            gobject.PARAM_READWRITE
        )
    }
    __gsignals__ = {
        'folder-added': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            [gio.File]
        ),
        'location-removed': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            [gio.File]
        ),
        'file-added': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            [gio.File]
        ),
    }
    
    def __init__(self, root_dir):
        """
            :param library: the library to monitor
            :type library: :class:`Library`
        """
        gobject.GObject.__init__(self)

        self.__root = gio.File(root_dir)
        self.__monitored = False
        self.__monitors = {}
        self.__queue = []
        self.__lock = threading.RLock()

    def do_get_property(self, property):
        """
            Gets GObject properties
        """
        if property.name == 'monitored':
            return self.__monitored
        else:
            raise AttributeError('unkown property %s' % property.name)

    def do_set_property(self, property, value):
        """
            Sets GObject properties
        """
        if property.name == 'monitored':
            if value != self.__monitored:
                self.__monitored = value
                update_thread = threading.Thread(target=self.__update_monitors)
                update_thread.daemon = True
                glib.idle_add(update_thread.start)
        else:
            raise AttributeError('unkown property %s' % property.name)

    def __update_monitors(self):
        """
            Sets up or removes library monitors
        """
        with self.__lock:
            if self.props.monitored:
                for directory in common.walk_directories(self.__root):
                    monitor = directory.monitor_directory()
                    monitor.connect('changed', self.on_location_changed)
                    self.__monitors[directory] = monitor
            else:
 
                for directory, monitor in self.__monitors.iteritems():
                    monitor.cancel()

                self.__monitors = {}

    def on_location_changed(self, monitor, gfile, other_gfile, event):
        """
            Updates the library on changes of the location
        """
        if event == gio.FILE_MONITOR_EVENT_CHANGES_DONE_HINT:
            if gfile in self.__queue:
                self.emit("file-added", gfile)
                self.__queue.remove(gfile)
                
        elif event == gio.FILE_MONITOR_EVENT_CREATED:
            # Enqueue tracks retrieval
            fileinfo = gfile.query_info('standard::type')            
            if fileinfo.get_file_type() == gio.FILE_TYPE_REGULAR:
                if gfile not in self.__queue:
                    self.__queue += [gfile]

            # Set up new monitor if directory


            if fileinfo.get_file_type() == gio.FILE_TYPE_DIRECTORY and \
               gfile not in self.__monitors:
                for directory in common.walk_directories(gfile):
                    monitor = directory.monitor_directory()
                    monitor.connect('changed', self.on_location_changed)
                    self.__monitors[directory] = monitor

                    self.emit('folder-added', directory)

        elif event == gio.FILE_MONITOR_EVENT_DELETED:
            
            self.emit("location-removed", gfile)

            # Remove obsolete monitors
            removed_directories = [d for d in self.__monitors \
                if d == gfile or d.has_prefix(gfile)]

            for directory in removed_directories:
                self.__monitors[directory].cancel()
                del self.__monitors[directory]
