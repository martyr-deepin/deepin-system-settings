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
from dtk.ui.button import SwitchButton
from dtk.ui.line import HSeparator
from dtk.ui.scalebar import HScalebar
from dtk.ui.box import ImageBox
from nls import _
from constant import *
from vtk.button import SelectButton
from mpris2 import Mpris2
from glib import markup_escape_text
from urlparse import urlparse

import threading as td
import gtk
import gobject
import pypulse_small as pypulse
import traceback
import psutil
import dtk_cairo_blur
import cairo

gtk.gdk.threads_init()


class TrayGui(gtk.VBox):
    '''sound tray gui'''
    #BASE_HEIGHT = 128  # has microphone
    BASE_HEIGHT = 103   # no microphone

    __gsignals__ = {
        "stream-changed": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())}

    def __init__(self, tray_obj=None):
        super(TrayGui, self).__init__(False)
        self.tray_obj = tray_obj

        self.stream_icon = app_theme.get_pixbuf("sound/device.png").get_pixbuf().scale_simple(16, 16, gtk.gdk.INTERP_TILES)
        self.stream_num = 0
        self.stream_list = {}    # stream widgets
        self.stream_process = {} # process id to stream widgets
        self.stream_mpris = {}   # stream id to mpris process id

        self.__mpris_total_height = 0
        self.mpris_base_height = 70
        self.mpris_list = {}     # mpris widgets
        self.mpris_stream = {}   # mpris process id to stream id
        self.mpris2 = Mpris2()
        self.mpris2.connect("new", self.mpris2_new_cb)
        self.mpris2.connect("removed", self.mpris2_removed_cb)
        self.mpris2.connect("changed", self.mpris2_changed_cb)

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
        self.speaker_scale.set_magnetic_values([(0, 5), (100, 5), (volume_max_percent, 5)])
        self.speaker_scale.set_size_request(90, 10)
        self.speaker_mute_button = SwitchButton(
            inactive_disable_dpixbuf=app_theme.get_pixbuf("toggle_button/inactive_normal.png"), 
            active_disable_dpixbuf=app_theme.get_pixbuf("toggle_button/inactive_normal.png"))
        table.attach(self.__make_align(speaker_img), 0, 1, 0, 1, 4)
        table.attach(self.__make_align(self.speaker_scale, yalign=0.0, yscale=1.0, padding_left=5, padding_right=5, height=25), 1, 2, 0, 1, 4)
        table.attach(self.__make_align(self.speaker_mute_button), 2, 3, 0, 1, 4)

        #microphone_img = ImageBox(app_theme.get_pixbuf("sound/microphone.png"))
        #self.microphone_scale = HScalebar(show_value=False, format_value="%", value_min=0, value_max=volume_max_percent)
        #self.microphone_scale.set_size_request(90, 10)
        #self.microphone_mute_button = SwitchButton(
            #inactive_disable_dpixbuf=app_theme.get_pixbuf("toggle_button/inactive_normal.png"), 
            #active_disable_dpixbuf=app_theme.get_pixbuf("toggle_button/inactive_normal.png"))
        #table.attach(self.__make_align(microphone_img), 0, 1, 1, 2, 4)
        #table.attach(self.__make_align(self.microphone_scale, yalign=0.0, yscale=1.0, padding_left=5, padding_right=5, height=25), 1, 2, 1, 2, 4)
        #table.attach(self.__make_align(self.microphone_mute_button), 2, 3, 1, 2, 4)

        self.pack_start(table, False, False)

        self.__app_vbox = gtk.VBox(False)
        separator_color = [(0, ("#777777", 0.0)), (0.5, ("#000000", 0.3)), (1, ("#777777", 0.0))]
        hseparator = HSeparator(separator_color, 0, 0)
        hseparator.set_size_request(140, 5)
        self.__app_vbox.pack_start(self.__make_align(Label(_("Applications"), enable_select=False, enable_double_click=False)), False, False)
        self.__app_vbox.pack_start(self.__make_align(hseparator, xalign=0.5, height=5), False, False)

        self.__mpris_vbox = gtk.VBox(False)
        self.__app_vbox.pack_start(self.__mpris_vbox)
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
        #state_cb_fun["source"] = self.__source_state_cb
        state_cb_fun["sinkinput"] = self.__sinkinput_state_cb
        pypulse.PULSE.connect_to_pulse(state_cb_fun)
        self.__set_output_status()
        #self.__set_input_status()

        # widget signals
        self.speaker_mute_button.connect("toggled", self.speaker_toggled)
        #self.microphone_mute_button.connect("toggled", self.microphone_toggled)
        self.speaker_scale.connect("value-changed", self.speaker_scale_value_changed)
        #self.microphone_scale.connect("value-changed", self.microphone_scale_value_changed)
        # pulseaudio signals
        pypulse.PULSE.connect("sink-removed", self.sink_removed_cb)
        #pypulse.PULSE.connect("source-removed", self.source_removed_cb)
        pypulse.PULSE.connect("sinkinput-removed", self.sinkinput_removed_cb)

        self.mpris2.get_mpris_list()
        self.mpris_num = len(self.mpris2.mpris_process.keys())
        if self.mpris_num == 0:
            self.__app_vbox.set_no_show_all(True)

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
        process_id = int(stream['proplist']['application.process.id'])
        # if it has show mpris, then don't show sink_input
        if process_id in self.mpris_list:
            self.mpris_stream[process_id] = index
            self.stream_mpris[index] = process_id
            return
        icon_name, is_filtered = self.__white_list_check(stream, index)
        if is_filtered:
            return
        self.stream_list[index] = {}
        volume_max_percent = pypulse.MAX_VOLUME_VALUE * 100 / pypulse.NORMAL_VOLUME_VALUE
        if icon_name:
            if icon_name[0] == '/':
                try:
                    img = gtk.image_new_from_pixbuf(gtk.gdk.pixbuf_new_from_file(
                        icon_name).scale_simple(16, 16, gtk.gdk.INTERP_TILES))
                except:
                    img = gtk.image_new_from_pixbuf(self.stream_icon)
            else:
                image_pixbuf = self.__get_pixbuf_from_icon_name(icon_name)
                if image_pixbuf:
                    img = gtk.image_new_from_pixbuf(image_pixbuf)
                else:
                    img = gtk.image_new_from_pixbuf(self.stream_icon)
                    #img = gtk.image_new_from_icon_name(icon_name, gtk.ICON_SIZE_MENU)
        else:
            img = gtk.image_new_from_pixbuf(self.stream_icon)
        img.set_size_request(16, 16)
        scale = HScalebar(show_value=False, format_value="%", value_min=0, value_max=volume_max_percent)
        scale.set_magnetic_values([(0, 5), (100, 5), (volume_max_percent, 5)])
        scale.set_size_request(90, 10)
        mute_button = SwitchButton(
            inactive_disable_dpixbuf=app_theme.get_pixbuf("toggle_button/inactive_normal.png"), 
            active_disable_dpixbuf=app_theme.get_pixbuf("toggle_button/inactive_normal.png"))
        hbox = gtk.HBox()
        hbox.pack_start(self.__make_align(img), False, False)
        hbox.pack_start(self.__make_align(scale, yalign=0.0, yscale=1.0, padding_left=5, padding_right=5, height=25), False, False)
        hbox.pack_start(self.__make_align(mute_button), False, False)
        self.stream_list[index]['scale'] = scale
        self.stream_list[index]['button'] = mute_button
        self.stream_list[index]['container'] = hbox
        self.stream_list[index]['process_id'] = process_id
        self.stream_list[index]['stream_id'] = index
        self.stream_process[process_id] = self.stream_list[index]
        self.__set_playback_status(stream, scale, mute_button)
        if stream['volume_writable']:
            scale.connect("value-changed", self.playback_stream_scale_changed_cb, index, mute_button)
            mute_button.connect("toggled", self.playback_stream_toggled_cb, index, scale)
        hbox.show_all()
        self.__app_vbox.pack_start(hbox, False, False)

    def __white_list_check(self, stream, index):
        icon_name = None
        # check deepin-media-player
        if 'application.process.binary' in stream['proplist'] and \
                stream['proplist']['application.process.binary'] == 'mplayer':
            process_id = int(stream['proplist']['application.process.id'])
            stream_process_obj = psutil.Process(process_id)
            stream_process_parent_obj = stream_process_obj.parent
            if stream_process_parent_obj.pid != 0 and \
                    stream_process_parent_obj.name.startswith("deepin-media"):
                children_process = stream_process_parent_obj.get_children()
                # check this process is the preview window of deepin-media-player
                if process_id != children_process[0].pid:
                    return None, True
                # check deepin-media-player whether enable mpris
                if stream_process_parent_obj.pid in self.mpris_list:
                    self.mpris_stream[stream_process_parent_obj.pid] = index
                    self.stream_mpris[index] = stream_process_parent_obj.pid
                    return None, True
                return "deepin-media-player", False
        if 'application.icon_name' in stream['proplist']:
            icon_name = stream['proplist']['application.icon_name']
        # check deepin-music-player
        if 'application.name' in stream['proplist']:
            if stream['proplist']['application.name'] == 'deepin-music-player':
                icon_name = "deepin-music-player"
        return icon_name, False

    def __get_pixbuf_from_icon_name(self, name):
        screen = self.get_screen()
        icon_theme = gtk.icon_theme_get_for_screen(screen)
        icon_info = icon_theme.lookup_icon(name, 16, 0)
        if not icon_info:
            return None
        filename = icon_info.get_filename()
        if not filename or not os.path.exists(filename):
            return None
        pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
        if icon_info.get_base_size() != 16:
            pixbuf = pixbuf.scale_simple(16, 16, gtk.gdk.INTERP_TILES)
        return pixbuf

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
        balance = pypulse.get_volume_balance(channel_list['channels'],
                                             volume_list, channel_list['map'])
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
        if index in self.stream_mpris:
            return
        if index not in self.stream_list:
            self.__make_playback_box(dt, index)
            stream_num = len(self.stream_list.keys())
            mpris_num = len(self.mpris_list.keys())
            if stream_num > 0 or mpris_num > 0:
                self.__app_vbox.set_no_show_all(False)
                self.__app_vbox.show_all()
            self.adjust_size()
            self.emit("stream-changed")
        else:
            self.__set_playback_status(dt,
                                       self.stream_list[index]['scale'],
                                       self.stream_list[index]['button'])
        pypulse.playback_info[index] = dt

    def sinkinput_removed_cb(self, obj, index):
        if index in self.stream_mpris:
            if self.stream_mpris[index] in self.mpris_stream:
                del self.mpris_stream[self.stream_mpris[index]]
            del self.stream_mpris[index]
        if index in pypulse.playback_info:
            del pypulse.playback_info[index]
        if index in self.stream_list:
            process_id = self.stream_list[index]['process_id']
            if process_id in self.stream_process:
                del self.stream_process[process_id]
            self.stream_list[index]['container'].destroy()
            del self.stream_list[index]
            self.stream_num -= 1
            stream_num = len(self.stream_list.keys())
            mpris_num = len(self.mpris_list.keys())
            if stream_num == 0 and mpris_num == 0:
                self.__app_vbox.hide_all()
                self.__app_vbox.set_no_show_all(True)
            self.adjust_size()
            self.emit("stream-changed")

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

    # mpris dbus signal
    def mpris2_new_cb(self, obj, pid):
        vbox = gtk.VBox()
        image_pixbuf = self.__get_pixbuf_from_icon_name(obj.mpris_process[pid]['property']['DesktopEntry'])
        if image_pixbuf:
            img = gtk.image_new_from_pixbuf(image_pixbuf)
        else:
            img = gtk.image_new_from_pixbuf(self.stream_icon)
        img.set_size_request(16, 16)
        # application title
        app_title = obj.mpris_process[pid]['property']['Identity']
        #if obj.mpris_process[pid]['property']['PlaybackStatus'] == 'Stopped':
            #app_title = obj.mpris_process[pid]['property']['Identity']
        #else:
            #app_title = "%s - %s" % (obj.mpris_process[pid]['property']['Identity'], _(obj.mpris_process[pid]['property']['PlaybackStatus']))
        label = Label(app_title, label_width=115)
        hbox = gtk.HBox(False, 5)
        hbox.pack_start(self.__make_align(img), False, False)
        hbox.pack_start(self.__make_align(label), False, False)
        vbox.pack_start(hbox, False, False)

        # metadata info
        meta_box = gtk.HBox(False, 10)
        xesam_vbox = gtk.VBox(False)
        #art_img = gtk.Image()
        art_img = gtk.EventBox()
        art_img.set_size_request(40, 40)
        art_img.connect("expose-event", self.__draw_mpris_art_img)

        xesam_title = Label("", label_width=75)
        xesam_artist = Label("", label_width=75)
        xesam_album = Label("", label_width=75)
        xesam_vbox.pack_start(xesam_title)
        xesam_vbox.pack_start(xesam_artist)
        #xesam_vbox.pack_start(xesam_album)
        meta_box.pack_start(self.__make_align(art_img, padding_left=21, height=40), False, False)
        meta_box.pack_start(xesam_vbox)

        self.mpris_list[pid] = {}
        # mpris control
        scale = HScalebar(app_theme.get_pixbuf("sound/point.png"), show_value=False, format_value="%", value_min=0, value_max=1, line_height=3)
        scale.set_magnetic_values([(0, 0.1), (1, 0.1)])
        scale.set_size_request(70, 10)
        prev_bt = gtk.Button()
        pause_bt = gtk.Button()
        stop_bt = gtk.Button()
        next_bt = gtk.Button()

        prev_bt.set_size_request(20, 22)
        pause_bt.set_size_request(29, 30)
        #stop_bt.set_size_request(16, 16)
        next_bt.set_size_request(20, 22)

        prev_bt.pixbuf = "previous"
        if obj.mpris_process[pid]['property']['PlaybackStatus'] == 'Playing':
            pause_bt.pixbuf = "pause"
        else:
            pause_bt.pixbuf = "play"
        #stop_bt.pixbuf = self.stop_img
        next_bt.pixbuf = "next"

        scale.set_value(obj.mpris_process[pid]['property']['Volume'])

        prev_bt.connect("clicked", self.__mpris_prev_cb, obj, pid)
        pause_bt.connect("clicked", self.__mpris_pause_cb, obj, pid)
        #stop_bt.connect("clicked", self.__mpris_stop_cb, obj, pid)
        next_bt.connect("clicked", self.__mpris_next_cb, obj, pid)
        prev_bt.connect("expose-event", self.__draw_mpris_button_cb)
        pause_bt.connect("expose-event", self.__draw_mpris_button_cb)
        stop_bt.connect("expose-event", self.__draw_mpris_button_cb)
        next_bt.connect("expose-event", self.__draw_mpris_button_cb)
        scale.connect("value-changed", self.__mpris_volume_cb, obj, pid)

        hbox = gtk.HBox()
        hbox.pack_start(self.__make_align(prev_bt, height=-1), False, False)
        hbox.pack_start(self.__make_align(pause_bt, height=-1), False, False)
        #hbox.pack_start(self.__make_align(stop_bt, height=-1), False, False)
        hbox.pack_start(self.__make_align(next_bt, height=-1), False, False)
        hbox.pack_start(self.__make_align(scale, yalign=0.0, yscale=1.0, height=-1), False, False)
        vbox.pack_start(self.__make_align(hbox, xalign=0.5, padding_top=5, padding_bottom=10, height=-1), False, False)

        self.mpris_list[pid]['app_title'] = label
        self.mpris_list[pid]['prev'] = prev_bt
        self.mpris_list[pid]['pause'] = pause_bt
        self.mpris_list[pid]['stop'] = stop_bt
        self.mpris_list[pid]['next'] = next_bt
        self.mpris_list[pid]['scale'] = scale
        self.mpris_list[pid]['meta'] = meta_box
        self.mpris_list[pid]['meta_img'] = art_img
        self.mpris_list[pid]['meta_title'] = xesam_title
        self.mpris_list[pid]['meta_artist'] = xesam_artist
        self.mpris_list[pid]['meta_album'] = xesam_album
        self.mpris_list[pid]['container'] = vbox
        if not obj.mpris_process[pid]['property']['Metadata']:
            self.mpris_list[pid]['height'] = self.mpris_base_height
        else:
            vbox.pack_start(meta_box, False, False)
            vbox.reorder_child(meta_box, 1)
            self.__set_mpris_meta_info(pid)
            self.mpris_list[pid]['height'] = self.mpris_base_height + 40
        self.__mpris_total_height += self.mpris_list[pid]['height']
        # delete playback_stream widget
        if pid in self.stream_process:
            self.stream_process[pid]['container'].destroy()
            del self.stream_list[self.stream_process[pid]['stream_id']]
            del self.stream_process[pid]
        vbox.show_all()
        self.__mpris_vbox.pack_start(vbox, False, False)

        stream_num = len(self.stream_list.keys())
        mpris_num = len(self.mpris_list.keys())
        if stream_num > 0 or mpris_num > 0:
            self.__app_vbox.set_no_show_all(False)
            self.__app_vbox.show_all()
        self.adjust_size()
        self.emit("stream-changed")

    def __draw_mpris_art_img(self, widget, event):
        x, y, w, h = widget.allocation
        cr = widget.window.cairo_create()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h) 
        surface_cr = gtk.gdk.CairoContext(cairo.Context(surface))
        surface_cr.set_source_rgba(0, 0, 0, 1.0)
        surface_cr.rectangle(5, 5, w-10, h-10)
        surface_cr.stroke()

        dtk_cairo_blur.gaussian_blur(surface, 3)
        cr.set_source_surface(surface, 0, 0)
        cr.paint()

        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(2, 2, w-4, h-4)
        cr.fill()

        if widget.pixbuf:
            cr.set_source_pixbuf(widget.pixbuf, 4, 4)
            cr.paint()
        return True

    def __set_mpris_meta_info(self, pid):
        if 'mpris:artUrl' in self.mpris2.mpris_process[pid]['property']['Metadata']:
            arturl = urlparse(self.mpris2.mpris_process[pid]['property']['Metadata']['mpris:artUrl'])
            if arturl.scheme == 'file' and os.path.exists(arturl.path):
                art_pixbuf = gtk.gdk.pixbuf_new_from_file(arturl.path).scale_simple(32, 32, gtk.gdk.INTERP_TILES)
                #self.mpris_list[pid]['meta_img'].set_from_pixbuf(art_pixbuf)
                self.mpris_list[pid]['meta_img'].pixbuf = art_pixbuf
        else:
            self.mpris_list[pid]['meta_img'].pixbuf = None
        self.mpris_list[pid]['meta_img'].queue_draw()
        if 'xesam:title' in self.mpris2.mpris_process[pid]['property']['Metadata']:
            self.mpris_list[pid]['meta_title'].set_text(
                markup_escape_text(self.mpris2.mpris_process[pid]['property']['Metadata']['xesam:title']))
        else:
            self.mpris_list[pid]['meta_title'].set_text("-")
        if 'xesam:artist' in self.mpris2.mpris_process[pid]['property']['Metadata']:
            self.mpris_list[pid]['meta_artist'].set_text(
                markup_escape_text('&'.join(self.mpris2.mpris_process[pid]['property']['Metadata']['xesam:artist'])))
        else:
            self.mpris_list[pid]['meta_artist'].set_text("-")
        if 'xesam:album' in self.mpris2.mpris_process[pid]['property']['Metadata']:
            self.mpris_list[pid]['meta_album'].set_text(
                markup_escape_text(self.mpris2.mpris_process[pid]['property']['Metadata']['xesam:album']))
        else:
            self.mpris_list[pid]['meta_album'].set_text("-")
        
    def mpris2_removed_cb(self, obj, pid):
        if pid in self.mpris_list:
            self.mpris_list[pid]['container'].destroy()
            self.mpris_list[pid]['meta'].destroy()
            self.__mpris_total_height -= self.mpris_list[pid]['height']
            del self.mpris_list[pid]
        if pid in self.mpris_stream:
            stream_id = self.mpris_stream[pid]
            if stream_id in pypulse.playback_info:
                self.__make_playback_box(pypulse.playback_info[stream_id], stream_id)
        stream_num = len(self.stream_list.keys())
        mpris_num = len(self.mpris_list.keys())
        if stream_num == 0 and mpris_num == 0:
            self.__app_vbox.hide_all()
            self.__app_vbox.set_no_show_all(True)
        self.adjust_size()
        self.emit("stream-changed")

    def mpris2_changed_cb(self, obj, pid, changed):
        #print "mpris changed", pid, changed
        if pid not in self.mpris_list:
            return
        if 'Volume' in changed:
            self.mpris_list[pid]['scale'].set_value(changed['Volume'])
        if 'PlaybackStatus' in changed:
            # application title && hide meta info
            if changed['PlaybackStatus'] == 'Stopped':
                if self.mpris_list[pid]['meta'] in self.mpris_list[pid]['container'].get_children():
                    self.mpris_list[pid]['container'].remove(self.mpris_list[pid]['meta'])
                    self.__mpris_total_height -= self.mpris_list[pid]['height']
                    self.mpris_list[pid]['height'] = self.mpris_base_height
                    self.__mpris_total_height += self.mpris_list[pid]['height']
                    self.adjust_size()
                    self.emit("stream-changed")
            # button image
            if changed['PlaybackStatus'] == 'Playing':
                self.mpris_list[pid]['pause'].pixbuf = "pause"
            else:
                self.mpris_list[pid]['pause'].pixbuf = "play"
            self.mpris_list[pid]['pause'].queue_draw()
        if 'Metadata' in changed and obj.mpris_process[pid]['property']['PlaybackStatus'] != 'Stopped':
            self.__set_mpris_meta_info(pid)
            if self.mpris_list[pid]['meta'] not in self.mpris_list[pid]['container'].get_children():
                self.mpris_list[pid]['container'].pack_start(self.mpris_list[pid]['meta'], False, False)
                self.mpris_list[pid]['container'].reorder_child(self.mpris_list[pid]['meta'], 1)
                self.mpris_list[pid]['container'].show_all()
                self.__mpris_total_height -= self.mpris_list[pid]['height']
                self.mpris_list[pid]['height'] = self.mpris_base_height + 40
                self.__mpris_total_height += self.mpris_list[pid]['height']
                self.adjust_size()
                self.emit("stream-changed")

    def __mpris_prev_cb(self, bt, obj, pid):
        if pid not in obj.mpris_process:
            return
        try:
            obj.mpris_process[pid]['obj'].get_dbus_method(
                'Previous', 'org.mpris.MediaPlayer2.Player')()
        except Exception, e:
            if e._dbus_error_name == "org.freedesktop.DBus.Error.ServiceUnknown":
                self.mpris2_removed_cb(obj, pid)
        
    def __mpris_pause_cb(self, bt, obj, pid):
        if pid not in obj.mpris_process:
            return
        try:
            if obj.mpris_process[pid]['property']['PlaybackStatus'] == "stop":
                play = obj.mpris_process[pid]['obj'].get_dbus_method(
                    'Play', 'org.mpris.MediaPlayer2.Player')
                play()
            else:
                playpause = obj.mpris_process[pid]['obj'].get_dbus_method(
                    'PlayPause', 'org.mpris.MediaPlayer2.Player')
                playpause()
        except Exception, e:
            if e._dbus_error_name == "org.freedesktop.DBus.Error.ServiceUnknown":
                self.mpris2_removed_cb(obj, pid)
        
    def __mpris_stop_cb(self, bt, obj, pid):
        if pid not in obj.mpris_process:
            return
        try:
            obj.mpris_process[pid]['obj'].get_dbus_method(
                'Stop', 'org.mpris.MediaPlayer2.Player')()
        except Exception, e:
            if e._dbus_error_name == "org.freedesktop.DBus.Error.ServiceUnknown":
                self.mpris2_removed_cb(obj, pid)
        
    def __mpris_next_cb(self, bt, obj, pid):
        if pid not in obj.mpris_process:
            return
        try:
            obj.mpris_process[pid]['obj'].get_dbus_method(
                'Next', 'org.mpris.MediaPlayer2.Player')()
        except Exception, e:
            if e._dbus_error_name == "org.freedesktop.DBus.Error.ServiceUnknown":
                self.mpris2_removed_cb(obj, pid)
        
    def __mpris_volume_cb(self, widget, value, obj, pid):
        if pid not in obj.mpris_process:
            return
        try:
            property_manager = dbus.Interface(obj.mpris_process[pid]['obj'], 'org.freedesktop.DBus.Properties')
            property_manager.Set('org.mpris.MediaPlayer2.Player', 'Volume', value)
        except Exception, e:
            if e._dbus_error_name == "org.freedesktop.DBus.Error.ServiceUnknown":
                self.mpris2_removed_cb(obj, pid)
        
    def __draw_mpris_button_cb(self, bt, event):
        if bt.get_state() == gtk.STATE_PRELIGHT:
            pixbuf = app_theme.get_pixbuf("sound/%s_hover.png" % bt.pixbuf).get_pixbuf()
        elif bt.get_state() == gtk.STATE_ACTIVE:
            pixbuf = app_theme.get_pixbuf("sound/%s_press.png" % bt.pixbuf).get_pixbuf()
        else:
            pixbuf = app_theme.get_pixbuf("sound/%s_normal.png" % bt.pixbuf).get_pixbuf()
        cr = bt.window.cairo_create()
        pix_height = pixbuf.get_height()
        cr.set_source_pixbuf(pixbuf, bt.allocation.x, bt.allocation.y + (bt.allocation.height - pix_height) / 2)
        cr.paint()
        return True

    ######################
    def get_widget_height(self):
        stream_num = len(self.stream_list.keys())
        mpris_num = len(self.mpris_list.keys())
        if stream_num > 0 or mpris_num > 0:
            #return self.BASE_HEIGHT + 30 + 25 * stream_num + 50 * mpris_num + 5
            return self.BASE_HEIGHT + 30 + 25 * stream_num + self.__mpris_total_height + 5
        else:
            return self.BASE_HEIGHT + 5

    def adjust_size(self):
        #self.set_size_request(152, self.get_widget_height())
        self.set_size_request(-1, -1)

gobject.type_register(TrayGui)
