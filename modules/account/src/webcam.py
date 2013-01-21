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

import gtk
import gst

class Webcam(gtk.DrawingArea):
    
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.pipestr = "v4l2src !  xvimagesink"
        #self.create_video_pipeline()
        
    def create_video_pipeline(self):    
        self.video_player = gst.parse_launch(self.pipestr)
        self.video_player.set_state(gst.STATE_PLAYING)
        
        self.__video_bus = self.video_player.get_bus()
        self.__video_bus.add_signal_watch()
        self.__video_bus.enable_sync_message_emission()
        self.__video_bus.connect("message", self.__on_bus_message)
        self.__video_bus.connect("sync-message::element", self.__on_bus_sync_message)        

    def set_playing(self):
        self.video_player.set_state(gst.STATE_PLAYING)
        self.__video_bus.add_signal_watch()

    def set_paused(self):
        self.video_player.set_state(gst.STATE_NULL)
        self.__video_bus.remove_signal_watch()
        
    def __on_bus_message(self, bus, message):    
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.video_player.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.video_player.set_state(gst.STATE_NULL)
            
    def __on_bus_sync_message(self, bus, message):
        """ Set up the Webcam <--> GUI messages bus """
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            imagesink = message.src
            # imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_xwindow_id(self.window.xid) 
            
    def get_snapshot(self):        
        drawable = self.window
        colormap = drawable.get_colormap()
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 0, 8, *drawable.get_size())
        pixbuf = pixbuf.get_from_drawable(drawable, colormap, 0, 0, 0, 0, *drawable.get_size()) 
        return pixbuf
