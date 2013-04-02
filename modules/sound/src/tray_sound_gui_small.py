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

class TrayGui(gtk.VBox):
    '''sound tray gui'''
    BASE_HEIGHT = 128

    __gsignals__ = {
        "stream-changed": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())}

    def __init__(self, tray_obj=None):
        super(TrayGui, self).__init__(False)
        self.tray_obj = tray_obj

        self.stream_icon = app_theme.get_pixbuf("sound/device.png").get_pixbuf().scale_simple(16, 16, gtk.gdk.INTERP_TILES)
        self.stream_num = 0
        self.stream_list = {}

        hbox = gtk.HBox(False)
        hbox.set_spacing(WIDGET_SPACING)
        #separator_color = [(0, ("#000000", 0.3)), (0.5, ("#000000", 0.2)), (1, ("#777777", 0.0))]
        #hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        #hseparator.set_size_request(150, 3)
        separator_color = [(0, ("#777777", 0.0)), (0.5, ("#000000", 0.3)), (1, ("#777777", 0.0))]
        hseparator = HSeparator(separator_color, 0, 0)
        hseparator.set_size_request(140, 5)
        #hbox.pack_start(self.__make_align(Label(_("Device"), enable_select=False, enable_double_click=False)), False, False)
        #hbox.pack_start(self.__make_align(hseparator), True, True)
        self.pack_start(self.__make_align(Label(_("Device"), enable_select=False, enable_double_click=False), height=-1), False, False)
        self.pack_start(self.__make_align(hseparator, xalign=0.5, height=5), False, False)

        volume_max_percent = pypulse.MAX_VOLUME_VALUE * 100 / pypulse.NORMAL_VOLUME_VALUE

        table = gtk.Table(2, 3)
        speaker_img = ImageBox(app_theme.get_pixbuf("sound/speaker-3.png"))
        self.speaker_scale = HScalebar(show_value=False, format_value="%", value_min=0, value_max=volume_max_percent)
        self.speaker_scale.set_size_request(100, 10)
        self.speaker_mute_button = OffButton()
        table.attach(self.__make_align(speaker_img), 0, 1, 0, 1, 4)
        table.attach(self.__make_align(self.speaker_scale, yalign=0.0, yscale=1.0, height=25), 1, 2, 0, 1, 4)
        table.attach(self.__make_align(self.speaker_mute_button), 2, 3, 0, 1, 4)

        microphone_img = ImageBox(app_theme.get_pixbuf("sound/microphone.png"))
        self.microphone_scale = HScalebar(show_value=False, format_value="%", value_min=0, value_max=volume_max_percent)
        self.microphone_scale.set_size_request(100, 10)
        self.microphone_mute_button = OffButton()
        table.attach(self.__make_align(microphone_img), 0, 1, 1, 2, 4)
        table.attach(self.__make_align(self.microphone_scale, yalign=0.0, yscale=1.0, height=25), 1, 2, 1, 2, 4)
        table.attach(self.__make_align(self.microphone_mute_button), 2, 3, 1, 2, 4)

        self.pack_start(table, False, False)

        self.__app_vbox = gtk.VBox(False)
        separator_color = [(0, ("#777777", 0.0)), (0.5, ("#000000", 0.3)), (1, ("#777777", 0.0))]
        hseparator = HSeparator(separator_color, 0, 0)
        hseparator.set_size_request(140, 5)
        self.__app_vbox.pack_start(self.__make_align(Label(_("Applications"), enable_select=False, enable_double_click=False)), False, False)
        self.__app_vbox.pack_start(self.__make_align(hseparator, xalign=0.5, height=5), False, False)
        self.pack_start(self.__app_vbox)

        hseparator = HSeparator(separator_color, 0, 0)
        hseparator.set_size_request(140, 7)
        self.pack_start(self.__make_align(hseparator, xalign=0.5, height=7), False, False)

        self.button_more = SelectButton(_("Advanced..."), font_size=10, ali_padding=5)
        self.button_more.set_size_request(-1, 25)
        self.pack_start(self.button_more, False, False)
        #self.pack_start(self.__make_align(height=10))
        ##########################################
        self.__fallback_sink_index = None
        self.__fallback_source_index = None
        state_cb_fun = {}
        state_cb_fun["server"] = self.__server_state_cb
        state_cb_fun["sink"] = self.__sink_state_cb
        state_cb_fun["source"] = self.__source_state_cb
        state_cb_fun["sinkinput"] = self.__sinkinput_state_cb
        pypulse.PULSE.connect_to_pulse(state_cb_fun)
        self.__set_output_status()
        self.__set_input_status()

        # widget signals
        self.speaker_mute_button.connect("toggled", self.speaker_toggled)
        self.microphone_mute_button.connect("toggled", self.microphone_toggled)
        self.speaker_scale.connect("value-changed", self.speaker_scale_value_changed)
        self.microphone_scale.connect("value-changed", self.microphone_scale_value_changed)
        # pulseaudio signals
        pypulse.PULSE.connect("sink-removed", self.sink_removed_cb)
        pypulse.PULSE.connect("source-removed", self.source_removed_cb)
        pypulse.PULSE.connect("sinkinput-removed", self.sinkinput_removed_cb)
        self.__app_vbox.set_no_show_all(True)
        ##### TODO
        #playback_streams = pypulse.PULSE.get_playback_streams()
        #self.stream_num = len(playback_streams.keys())
        #if self.stream_num == 0:
            #self.__app_vbox.set_no_show_all(True)
        #for stream in playback_streams:
            #self.__make_playback_box(playback_streams[stream], stream)

    def __make_align(self, widget=None, xalign=0.0, yalign=0.5, xscale=0.0,
                     yscale=0.0, padding_top=0, padding_bottom=0, padding_left=0,
                     padding_right=0, width=-1, height=25):
        align = gtk.Alignment()
        align.set_size_request(width, height)
        align.set(xalign, yalign, xscale, yscale)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        if widget:
            align.add(widget)
        return align

    def __make_playback_box(self, stream, index):
        self.stream_list[index] = {}
        volume_max_percent = pypulse.MAX_VOLUME_VALUE * 100 / pypulse.NORMAL_VOLUME_VALUE
        icon_name = None
        if 'application.icon_name' in stream['proplist']:
            icon_name = stream['proplist']['application.icon_name']
        if 'application.name' in stream['proplist']:
            if stream['proplist']['application.name'] == 'deepin-music-player' and \
                    os.path.exists("/usr/share/deepin-music-player/app_theme/blue/image/skin/logo1.png"):
                icon_name = "/usr/share/deepin-music-player/app_theme/blue/image/skin/logo1.png"
        if icon_name:
            if icon_name[0] == '/' and os.path.exists(icon_name):
                try:
                    img = gtk.image_new_from_pixbuf(gtk.gdk.pixbuf_new_from_file(
                        icon_name).scale_simple(16, 16, gtk.gdk.INTERP_TILES))
                except:
                    img = gtk.image_new_from_pixbuf(self.stream_icon)
            else:
                img = gtk.image_new_from_icon_name(icon_name, gtk.ICON_SIZE_MENU)
        else:
            img = gtk.image_new_from_pixbuf(self.stream_icon)
        scale = HScalebar(show_value=False, format_value="%", value_min=0, value_max=volume_max_percent)
        scale.set_size_request(100, 10)
        mute_button = OffButton()
        hbox = gtk.HBox()
        hbox.pack_start(self.__make_align(img), False, False)
        hbox.pack_start(self.__make_align(scale, yalign=0.0, yscale=1.0, height=25), False, False)
        hbox.pack_start(self.__make_align(mute_button), False, False)
        self.stream_list[index]['scale'] = scale
        self.stream_list[index]['button'] = mute_button
        self.stream_list[index]['container'] = hbox
        self.__set_playback_status(stream, scale, mute_button)
        if stream['volume_writable']:
            scale.connect("value-changed", self.playback_stream_scale_changed_cb, index, mute_button)
            mute_button.connect("toggled", self.playback_stream_toggled_cb, index, scale)
        hbox.show_all()
        self.__app_vbox.pack_start(hbox, False, False)

    ####################################################
    # widget signals
    def speaker_value_changed_thread(self):
        ''' speaker hscale value changed callback thread'''
        if not self.speaker_mute_button.get_active():
            self.speaker_mute_button.set_active(True)
        current_sink = self.__fallback_sink_index
        if current_sink is None:
            return
        volume_list = pypulse.output_volumes[current_sink]
        channel_list = pypulse.output_channels[current_sink]
        if not volume_list or not channel_list:
            return
        balance = pypulse.get_volume_balance(channel_list['channels'], volume_list, channel_list['map'])
        volume = int((self.speaker_scale.get_value()) / 100.0 * pypulse.NORMAL_VOLUME_VALUE)
        pypulse.PULSE.set_output_volume_with_balance(current_sink, volume, balance, channel_list['channels'], channel_list['map'])

    def speaker_scale_value_changed(self, widget, value):
        '''set output volume'''
        self.speaker_value_changed_thread()

    def microphone_value_changed_thread(self):
        ''' microphone value changed callback thread'''
        if not self.microphone_mute_button.get_active():
            self.microphone_mute_button.set_active(True)
        current_source = self.__fallback_source_index
        if current_source is None:
            return
        channel_list = pypulse.input_channels[current_source]
        if not channel_list:
            return
        volume = int((self.microphone_scale.get_value()) / 100.0 * pypulse.NORMAL_VOLUME_VALUE)
        pypulse.PULSE.set_input_volume(current_source, [volume] * channel_list['channels'], channel_list['channels'])

    def microphone_scale_value_changed(self, widget, value):
        ''' set input volume'''
        self.microphone_value_changed_thread()

    def speaker_toggled(self, button):
        active = button.get_active()
        current_sink = self.__fallback_sink_index
        self.speaker_scale.set_enable(active)
        if current_sink is not None:
            pypulse.PULSE.set_output_mute(current_sink, not active)

    def microphone_toggled(self, button):
        active = button.get_active()
        current_source = self.__fallback_source_index
        self.microphone_scale.set_enable(active)
        if current_source is not None:
            pypulse.PULSE.set_input_mute(current_source, not active)

    def playback_stream_scale_changed_cb(self, widget, value, index, button):
        if not button.get_active():
            button.set_active(True)
        volume = int((widget.get_value()) / 100.0 * pypulse.NORMAL_VOLUME_VALUE)
        pypulse.PULSE.set_sink_input_volume(index, [volume] * widget.volume_channels, widget.volume_channels)

    def playback_stream_toggled_cb(self, button, index, scale):
        active = button.get_active()
        scale.set_enable(active)
        pypulse.PULSE.set_sink_input_mute(index, not active)

    # pulseaudio signals callback

    def __sink_state_cb(self, obj, channel, port, volume, sink, idx):
        pypulse.output_channels[idx] = channel
        pypulse.output_active_ports[idx] = port
        pypulse.output_volumes[idx] = volume
        pypulse.output_devices[idx] = sink
        if self.__fallback_sink_index is None and pypulse.get_fallback_sink_name() == sink['name']:
            self.__fallback_sink_index = idx
        if self.__fallback_sink_index == idx:
            self.__set_output_status()

    # update tray_icon
    def update_tray_icon(self):
        if self.tray_obj:
            current_sink = self.__fallback_sink_index
            sinks = pypulse.output_devices
            sink_volume = pypulse.output_volumes
            tip_text = "%s %d%%" % (_("Volume"), self.speaker_scale.get_value())
            if current_sink in sinks and current_sink in sink_volume:
                is_mute = sinks[current_sink]['mute']
                if is_mute:
                    tip_text = _("Mute")
                volume = max(sink_volume[current_sink]) * 100.0 / pypulse.NORMAL_VOLUME_VALUE
                if volume == 0:
                    volume_level = 0
                elif 0 < volume <= 40:
                    volume_level = 1
                elif 40 < volume <= 80:
                    volume_level = 2
                else:
                    volume_level = 3
                self.tray_obj.set_tray_icon(volume_level, is_mute)
            if self.tray_obj.tray_obj:
                self.tray_obj.tray_obj.set_tooltip_text(tip_text)

    def __source_state_cb(self, obj, channel, port, volume, source, idx):
        pypulse.input_channels[idx] = channel
        pypulse.input_active_ports[idx] = port
        pypulse.input_volumes[idx] = volume
        pypulse.input_devices[idx] = source
        if self.__fallback_source_index is None and pypulse.get_fallback_source_name() == source['name']:
            self.__fallback_source_index = idx
        if self.__fallback_source_index == idx:
            self.__set_input_status()

    def __server_state_cb(self, obj, dt):
        pypulse.server_info = dt
        self.__fallback_sink_index = pypulse.get_fallback_sink_index()
        if self.__fallback_sink_index in pypulse.output_volumes:
            self.__set_output_status()
        self.__fallback_source_index = pypulse.get_fallback_source_index()
        if self.__fallback_source_index in pypulse.input_volumes:
            self.__set_input_status()

    def __sinkinput_state_cb(self, obj, dt, index):
        if index not in self.stream_list:
            self.__make_playback_box(dt, index)
            self.stream_num += 1
            if self.stream_num > 0:
                self.__app_vbox.set_no_show_all(False)
                self.__app_vbox.show_all()
            self.adjust_size()
        else:
            self.__set_playback_status(dt,
                                       self.stream_list[index]['scale'],
                                       self.stream_list[index]['button'])
        if index not in pypulse.playback_info:
            self.emit("stream-changed")
        pypulse.playback_info[index] = dt

    def sinkinput_removed_cb(self, obj, index):
        if index in self.stream_list:
            self.stream_list[index]['container'].destroy()
            self.stream_num -= 1
            if self.stream_num == 0:
                self.__app_vbox.hide_all()
                self.__app_vbox.set_no_show_all(True)
            del self.stream_list[index]
            self.adjust_size()
            self.emit("stream-changed")
        print pypulse.playback_info.keys()
        print index
        print "-"*30
        if index in pypulse.playback_info:
            del pypulse.playback_info[index]

    def sink_removed_cb(self, obj, index):
        if index in pypulse.output_devices:
            del pypulse.output_devices[index]
        if index in pypulse.output_channels:
            del pypulse.output_channels[index]
        if index in pypulse.output_active_ports:
            del pypulse.output_active_ports[index]
        if index in pypulse.output_volumes:
            del pypulse.output_volumes[index]

    def source_removed_cb(self, obj, index):
        if index in pypulse.input_devices:
            del pypulse.input_devices[index]
        if index in pypulse.input_channels:
            del pypulse.input_channels[index]
        if index in pypulse.input_active_ports:
            del pypulse.input_active_ports[index]
        if index in pypulse.input_volumes:
            del pypulse.input_volumes[index]

    def __set_output_status(self):
        # if sinks list is empty, then can't set output volume
        current_sink = self.__fallback_sink_index
        sinks = pypulse.output_devices
        if current_sink is None:
            self.speaker_scale.set_sensitive(False)
            self.speaker_mute_button.set_sensitive(False)
            self.speaker_scale.set_enable(False)
            self.speaker_mute_button.set_active(False)
        # set output volume
        else:
            self.speaker_scale.set_sensitive(True)
            self.speaker_mute_button.set_sensitive(True)
            is_mute = sinks[current_sink]['mute']
            self.speaker_mute_button.set_active(not is_mute)
            self.speaker_scale.set_enable(not is_mute)
            volume = max(pypulse.output_volumes[current_sink])
            self.speaker_scale.set_value(volume * 100.0 / pypulse.NORMAL_VOLUME_VALUE)
        self.update_tray_icon()

    def __set_input_status(self):
        # if sources list is empty, then can't set input volume
        current_source = self.__fallback_source_index
        sources = pypulse.input_devices
        if current_source is None:
            self.microphone_scale.set_sensitive(False)
            self.microphone_mute_button.set_sensitive(False)
            self.microphone_scale.set_enable(False)
            self.microphone_mute_button.set_active(False)
        # set input volume
        else:
            self.microphone_scale.set_sensitive(True)
            self.microphone_mute_button.set_sensitive(True)
            is_mute = sources[current_source]['mute']
            self.microphone_mute_button.set_active(not is_mute)
            self.microphone_scale.set_enable(not is_mute)
            volume = max(pypulse.input_volumes[current_source])
            self.microphone_scale.set_value(volume * 100.0 / pypulse.NORMAL_VOLUME_VALUE)
    
    def __set_playback_status(self, stream, scale, button):
        if not stream['has_volume']:
            scale.set_sensitive(False)
            button.set_sensitive(False)
            scale.set_enable(False)
            button.set_active(False)
        else:
            scale.set_sensitive(True)
            button.set_sensitive(True)
            is_mute = stream['mute']
            button.set_active(not is_mute)
            scale.set_enable(not is_mute)
            volume = max(stream['volume'])
            scale.set_value(volume * 100.0 / pypulse.NORMAL_VOLUME_VALUE)
            scale.volume_channels = len(stream['volume'])

    ######################
    def get_widget_height(self):
        if self.stream_num > 0:
            return self.BASE_HEIGHT + 30 + 25 * self.stream_num + 5
        else:
            return self.BASE_HEIGHT + 5

    def adjust_size(self):
        #self.set_size_request(152, self.get_widget_height())
        self.set_size_request(-1, -1)

gobject.type_register(TrayGui)
