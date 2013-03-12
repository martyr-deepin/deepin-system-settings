#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
#             Long Changjin <admin@longchangjin.cn>
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

# " gstreamer0.10-x"

import os
import gtk
import gst

class Webcam(gtk.EventBox):
    
    def __init__(self):
        gtk.EventBox.__init__(self)
        self.set_can_focus(True)
        self.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self.video_player = None

    @classmethod    
    def has_device(cls):
        return True
        devices = os.listdir('/dev')
        for d in devices:
            if d.startswith('video'):
                return True
        return False
        
    def create_video_pipeline(self):    
        # size list : ['352:288', '640:480', '800:600', '960:720', '1280:720']
        #self.pipestr = "v4l2src ! video/x-raw-yuv,width=320,height=240 ! ffmpegcolorspace ! xvimagesink"
        self.pipestr = "v4l2src ! video/x-raw-yuv ! ffmpegcolorspace ! xvimagesink"
        self.video_player = gst.parse_launch(self.pipestr)
        self.video_player.set_state(gst.STATE_PLAYING)
        self.__video_bus = self.video_player.get_bus()
        self.__video_bus.add_signal_watch()
        self.__video_bus.enable_sync_message_emission()
        self.__video_bus.connect("message", self.__on_bus_message)
        self.__video_bus.connect("sync-message::element", self.__on_bus_sync_message)        

    def play(self):
        if self.video_player:
            self.video_player.set_state(gst.STATE_PLAYING)

    def pause(self):
        if self.video_player:
            self.video_player.set_state(gst.STATE_PAUSED)
        
    def stop(self):
        if self.video_player:
            self.video_player.set_state(gst.STATE_NULL)
        
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
    
if __name__ == "__main__":    
    window = gtk.Window()
    window.set_size_request(400, 400)
    
    webcam = Webcam()    
    if webcam.has_device():
        webcam.create_video_pipeline()
    main_box = gtk.VBox()
    button_box = gtk.HBox()
    play_button = gtk.Button("play")
    play_button.connect("clicked", lambda w: webcam.play())
    pause_button = gtk.Button("pause",)
    pause_button.connect("clicked",  lambda w: webcam.pause())
    stop_button = gtk.Button("stop",)
    stop_button.connect("clicked",  lambda w: webcam.stop())
    button_box.pack_start(play_button, False, False)
    button_box.pack_start(pause_button, False, False)
    button_box.pack_start(stop_button, False, False)
    
    def stop_webcam():
        webcam.stop()
        gtk.main_quit()
    
    main_box.pack_start(webcam, True, True)    
    main_box.pack_start(button_box, False, False)
    window.connect("destroy", lambda w: stop_webcam())
    window.add(main_box)
    window.show_all()
    gtk.main()
