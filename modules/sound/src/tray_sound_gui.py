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

import sys
import os
from deepin_utils.file import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from theme import app_theme

from dtk.ui.label import Label
from dtk.ui.button import OffButton
from dtk.ui.line import HSeparator
from dtk.ui.hscalebar import HScalebar
from dtk.ui.box import ImageBox
from nls import _
from constant import *
from vtk.button import SelectButton

import threading as td
import gtk
import gobject
import pypulse
import traceback

gtk.gdk.threads_init()

class SettingVolumeThread(td.Thread):
    def __init__(self, obj, func, *args):
        td.Thread.__init__(self)
        # it need a mutex locker
        self.mutex = td.Lock()
        self.setDaemon(True)
        self.obj = obj
        self.args = args
        self.thread_func = func

    def run(self):
        try:
            self.setting_volume()
        except Exception, e:
            print "class LoadingThread got error: %s" % (e)
            traceback.print_exc(file=sys.stdout)

    def setting_volume(self):
        # lock it
        self.mutex.acquire()
        self.thread_func(*self.args)
        # unlock it
        self.mutex.release()


class TrayGui(gtk.VBox):
    '''sound tray gui'''
    def __init__(self):
        super(TrayGui, self).__init__(False)

        hbox = gtk.HBox(False)
        hbox.set_spacing(WIDGET_SPACING)
        separator_color = [(0, ("#000000", 0.3)), (0.5, ("#000000", 0.2)), (1, ("#777777", 0.0))]
        hseparator = HSeparator(separator_color, 0, 0)
        hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        hseparator.set_size_request(150, 3)
        hbox.pack_start(self.__make_align(Label(_("Device"), enable_select=False, enable_double_click=False)), False, False)
        hbox.pack_start(self.__make_align(hseparator), True, True)
        self.pack_start(hbox, False, False)

        volume_max_percent = pypulse.MAX_VOLUME_VALUE * 100 / pypulse.NORMAL_VOLUME_VALUE

        table = gtk.Table(2, 3)
        speaker_img = ImageBox(app_theme.get_pixbuf("sound/tray_speaker-3.png"))
        self.speaker_scale = HScalebar(show_value=False, format_value="%", value_min=0, value_max=volume_max_percent)
        self.speaker_scale.set_size_request(150, 10)
        self.speaker_mute_button = OffButton()
        table.attach(self.__make_align(speaker_img), 0, 1, 0, 1, 4)
        table.attach(self.__make_align(self.speaker_scale, yalign=0.0, yscale=1.0, padding_left=5, padding_right=5, height=30), 1, 2, 0, 1, 4)
        table.attach(self.__make_align(self.speaker_mute_button), 2, 3, 0, 1, 4)

        microphone_img = ImageBox(app_theme.get_pixbuf("sound/tray_microphone.png"))
        self.microphone_scale = HScalebar(show_value=False, format_value="%", value_min=0, value_max=volume_max_percent)
        self.microphone_scale.set_size_request(150, 10)
        self.microphone_mute_button = OffButton()
        table.attach(self.__make_align(microphone_img), 0, 1, 1, 2, 4)
        table.attach(self.__make_align(self.microphone_scale, yalign=0.0, yscale=1.0, padding_left=5, padding_right=5, height=30), 1, 2, 1, 2, 4)
        table.attach(self.__make_align(self.microphone_mute_button), 2, 3, 1, 2, 4)

        self.pack_start(table, False, False)

        separator_color = [(0, ("#777777", 0.0)), (0.5, ("#000000", 0.3)), (1, ("#777777", 0.0))]
        hseparator = HSeparator(separator_color, 0, 0)
        hseparator.set_size_request(190, 3)
        self.pack_start(self.__make_align(hseparator, xalign=0.5, height=14), False, False)
        self.button_more = SelectButton(_("Advanced..."), ali_padding=5)
        button_hbox = gtk.HBox(False)
        button_hbox.set_spacing(WIDGET_SPACING)
        button_hbox.pack_start(self.__make_align(height=-1))
        button_hbox.pack_start(self.button_more)
        self.pack_start((button_hbox), False, False)
        self.pack_start(self.button_more)
        self.pack_start(self.__make_align(height=15))
        ##########################################
        self.__set_output_status()
        self.__set_input_status()

        # widget signals
        self.speaker_mute_button.connect("toggled", self.speaker_toggled)
        self.microphone_mute_button.connect("toggled", self.microphone_toggled)
        self.speaker_scale.connect("value-changed", self.speaker_scale_value_changed)
        self.microphone_scale.connect("value-changed", self.microphone_scale_value_changed)
        # pulseaudio signals
        pypulse.PULSE.connect("sink-changed", self.sink_changed_cb)
        pypulse.PULSE.connect("source-changed", self.source_changed_cb)
        pypulse.PULSE.connect("server-changed", self.server_changed_cb)
        pypulse.PULSE.connect("sink-input-new", self.sink_input_new_cb)
        pypulse.PULSE.connect("sink-input-changed", self.sink_input_changed_cb)
        pypulse.PULSE.connect("sink-input-removed", self.sink_input_removed_cb)
        playback_streams = pypulse.PULSE.get_playback_streams()
        for stream in playback_streams:
            print "channel:", playback_streams[stream]['channel']
            print "client:", playback_streams[stream]['client']
            print "has_volume:", playback_streams[stream]['has_volume']
            print "mute:", playback_streams[stream]['mute']
            print "sink:", playback_streams[stream]['sink']
            print "resample_method:", playback_streams[stream]['resample_method']
            print "volume:", playback_streams[stream]['volume']
            print "voluem_writable:", playback_streams[stream]['volume_writable']
            proplist = playback_streams[stream]['proplist']
            if 'application.icon_name' in proplist:
                print 'application.icon_name:', proplist['application.icon_name']
            if 'application.name' in proplist:
                print 'application.name:', proplist['application.name']
            print "-"*20

    def __make_align(self, widget=None, xalign=0.0, yalign=0.5, xscale=0.0,
                     yscale=0.0, padding_top=0, padding_bottom=0, padding_left=0,
                     padding_right=0, width=-1, height=CONTAINNER_HEIGHT):
        align = gtk.Alignment()
        align.set_size_request(width, height)
        align.set(xalign, yalign, xscale, yscale)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        if widget:
            align.add(widget)
        return align

    ####################################################
    # widget signals
    def speaker_value_changed_thread(self):
        ''' speaker hscale value changed callback thread'''
        current_sink = pypulse.get_fallback_sink_index()
        if current_sink is None:
            return
        volume_list = pypulse.PULSE.get_output_volume_by_index(current_sink)
        channel_list = pypulse.PULSE.get_output_channels_by_index(current_sink)
        if not volume_list or not channel_list:
            return
        balance = pypulse.get_volume_balance(channel_list['channels'], volume_list, channel_list['map'])
        volume = int((self.speaker_scale.get_value()) / 100.0 * pypulse.NORMAL_VOLUME_VALUE)
        pypulse.PULSE.set_output_volume_with_balance(current_sink, volume, balance)
        if not self.speaker_mute_button.get_active():
            self.speaker_mute_button.set_active(True)

    def speaker_scale_value_changed(self, widget, value):
        '''set output volume'''
        #try:
            #SettingVolumeThread(self, self.speaker_value_changed_thread).start()
        #except:
            #pass
        self.speaker_value_changed_thread()

    def microphone_value_changed_thread(self):
        ''' microphone value changed callback thread'''
        current_source = pypulse.get_fallback_source_index()
        if current_source is None:
            return
        volume_list = pypulse.PULSE.get_input_volume_by_index(current_source)
        channel_list = pypulse.PULSE.get_input_channels_by_index(current_source)
        if not volume_list or not channel_list:
            return

        volume = int((self.microphone_scale.get_value()) / 100.0 * pypulse.NORMAL_VOLUME_VALUE)
        pypulse.PULSE.set_input_volume(current_source, [volume] * channel_list['channels'])
        if not self.microphone_mute_button.get_active():
            self.microphone_mute_button.set_active(True)

    def microphone_scale_value_changed(self, widget, value):
        ''' set input volume'''
        self.microphone_value_changed_thread()

    def speaker_toggled(self, button):
        active = button.get_active()
        current_sink = pypulse.get_fallback_sink_index()
        self.speaker_scale.set_enable(active)
        if current_sink is not None:
            pypulse.PULSE.set_output_mute(current_sink, not active)

    def microphone_toggled(self, button):
        active = button.get_active()
        current_source = pypulse.get_fallback_source_index()
        self.microphone_scale.set_enable(active)
        if current_source is not None:
            pypulse.PULSE.set_input_mute(current_source, not active)

    # pulseaudio signals callback
    def sink_changed_cb(self, obj, index):
        obj.get_devices()
        current_sink = pypulse.get_fallback_sink_index()
        if current_sink is None or current_sink != index:
            return
        self.__set_output_status()

    def source_changed_cb(self, obj, index):
        obj.get_devices()
        current_source = pypulse.get_fallback_source_index()
        if current_source is None or current_source != index:
            return
        self.__set_input_status()

    def server_changed_cb(self, obj):
        obj.get_devices()
        self.__set_output_status()
        self.__set_input_status()

    def sink_input_new_cb(self, obj, index):
        print "sink_input new:", index
        obj.get_devices()
        playback = obj.get_playback_streams()

    def sink_input_changed_cb(self, obj, index):
        print "sink_input changed:", obj, index

    def sink_input_removed_cb(self, obj, index):
        print "sink_input removed:", index

    def __set_output_status(self):
        # if sinks list is empty, then can't set output volume
        current_sink = pypulse.get_fallback_sink_index()
        sinks = pypulse.PULSE.get_output_devices()
        if current_sink is None:
            self.speaker_scale.set_sensitive(False)
            self.speaker_mute_button.set_sensitive(False)
            self.speaker_scale.set_enable(False)
            self.speaker_mute_button.set_active(False)
        # set output volume
        elif current_sink in sinks:
            self.speaker_scale.set_sensitive(True)
            self.speaker_mute_button.set_sensitive(True)
            is_mute = sinks[current_sink]['mute']
            self.speaker_mute_button.set_active(not is_mute)
            self.speaker_scale.set_enable(not is_mute)
            sink_volume = pypulse.PULSE.get_output_volume()
            if current_sink in sink_volume:
                volume = max(sink_volume[current_sink])
            else:
                volume = 0
            self.speaker_scale.set_value(volume * 100.0 / pypulse.NORMAL_VOLUME_VALUE)

    def __set_input_status(self):
        # if sources list is empty, then can't set input volume
        current_source = pypulse.get_fallback_source_index()
        sources = pypulse.PULSE.get_input_devices()
        if current_source is None:
            self.microphone_scale.set_sensitive(False)
            self.microphone_mute_button.set_sensitive(False)
            self.microphone_scale.set_enable(False)
            self.microphone_mute_button.set_active(False)
        # set input volume
        elif current_source in sources:
            self.microphone_scale.set_sensitive(True)
            self.microphone_mute_button.set_sensitive(True)
            is_mute = sources[current_source]['mute']
            self.microphone_mute_button.set_active(not is_mute)
            self.microphone_scale.set_enable(not is_mute)
            source_volume = pypulse.PULSE.get_input_volume()
            if current_source in source_volume:
                volume = max(source_volume[current_source])
            else:
                volume = 0
            self.microphone_scale.set_value(volume * 100.0 / pypulse.NORMAL_VOLUME_VALUE)

gobject.type_register(TrayGui)
