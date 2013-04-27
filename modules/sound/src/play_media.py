#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Changjin
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

import gtk
import gst


class Play(object):
    STOP = 0
    PLAYING = 1

    def __init__(self, uri):
        super(Play, self).__init__()
        self.uri = uri
        self.status = self.STOP

        self.player = gst.element_factory_make("playbin2", "player")
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self.player.set_property("video_sink", fakesink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def play(self):
        if self.status != self.PLAYING:
            self.player.set_property("uri", "file://"+self.uri)
            self.player.set_state(gst.STATE_PLAYING)
            self.status = self.PLAYING

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.status = self.STOP
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            self.status = self.STOP

if __name__ == '__main__':
    from deepin_utils.file import get_parent_dir
    import os
    media = os.path.join(get_parent_dir(__file__, 1), 'dingdong.wav')
    Play(media).play()
    gtk.main()
