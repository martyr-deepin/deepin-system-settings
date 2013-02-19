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
#from vtk.button import SelectButton

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
        #separator_color = [(0, ("#000000", 0.3)), (0.5, ("#000000", 0.2)), (1, ("#777777", 0.0))]
        #hseparator = HSeparator(separator_color, 0, 0)
        hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        hseparator.set_size_request(150, 3)
        hbox.pack_start(self.__make_align(Label(_("Device"), enable_select=False, enable_double_click=False)), False, False)
        hbox.pack_start(self.__make_align(hseparator), True, True)
        self.pack_start(hbox, False, False)

        table = gtk.Table(2, 3)
        #speaker_hbox = gtk.HBox(False)
        #speaker_hbox.set_spacing(WIDGET_SPACING)
        speaker_img = ImageBox(app_theme.get_pixbuf("sound/tray_speaker-3.png"))
        self.speaker_scale = HScalebar(show_value=False, format_value="%", value_min=0, value_max=150)
        self.speaker_scale.set_size_request(150, 10)
        self.speaker_mute_button = OffButton()
        #speaker_hbox.pack_start(self.__make_align(speaker_img), False, False)
        #speaker_hbox.pack_start(self.__make_align(self.speaker_scale, yalign=0.5, yscale=0.0, height=30))
        #speaker_hbox.pack_start(self.__make_align(self.speaker_mute_button), False, False)
        #self.pack_start(speaker_hbox, False, False)
        table.attach(self.__make_align(speaker_img), 0, 1, 0, 1, 4)
        table.attach(self.__make_align(self.speaker_scale, yalign=0.0, yscale=1.0, height=30), 1, 2, 0, 1, 4)
        table.attach(self.__make_align(self.speaker_mute_button), 2, 3, 0, 1, 4)

        #microphone_hbox = gtk.HBox(False)
        #microphone_hbox.set_spacing(WIDGET_SPACING)
        microphone_img = ImageBox(app_theme.get_pixbuf("sound/tray_microphone.png"))
        self.microphone_scale = HScalebar(show_value=False, format_value="%", value_min=0, value_max=150)
        self.microphone_scale.set_size_request(150, 10)
        self.microphone_mute_button = OffButton()
        #microphone_hbox.pack_start(self.__make_align(microphone_img), False, False)
        #microphone_hbox.pack_start(self.__make_align(self.microphone_scale, yalign=0.5, yscale=0.0, height=30))
        #microphone_hbox.pack_start(self.__make_align(self.microphone_mute_button), False, False)
        #self.pack_start(microphone_hbox, False, False)
        table.attach(self.__make_align(microphone_img), 0, 1, 1, 2, 4)
        table.attach(self.__make_align(self.microphone_scale, yalign=0.0, yscale=1.0, height=30), 1, 2, 1, 2, 4)
        table.attach(self.__make_align(self.microphone_mute_button), 2, 3, 1, 2, 4)

        self.pack_start(table, False, False)

        separator_color = [(0, ("#777777", 0.0)), (0.5, ("#000000", 0.3)), (1, ("#777777", 0.0))]
        hseparator = HSeparator(separator_color, 0, 0)
        hseparator.set_size_request(190, 3)
        self.pack_start(self.__make_align(hseparator, xalign=0.5, height=14), False, False)
        #self.button_more = SelectButton(_("Advanced..."), ali_padding=5)
        button_hbox = gtk.HBox(False)
        button_hbox.set_spacing(WIDGET_SPACING)
        #button_hbox.pack_start(self.__make_align(height=-1))
        #button_hbox.pack_start(self.button_more)
        self.pack_start((button_hbox), False, False)
        self.pack_start(self.__make_align(height=15))
        ##########################################
        # if PulseAudio connect error, set the widget insensitive
        if not pypulse.PULSE.get_cards():
            self.set_sensitive(False)
            return
        # if sinks list is empty, then can't set output volume
        current_sink = pypulse.get_fallback_sink_index()
        sinks = pypulse.PULSE.get_output_devices()
        if current_sink is None:
            speaker_hbox.set_sensitive(False)
        # set output volume
        elif current_sink in sinks:
            is_mute = sinks[current_sink]['mute']
            self.speaker_mute_button.set_active(not is_mute)
            self.speaker_scale.set_enable(not is_mute)
            sink_volume = pypulse.PULSE.get_output_volume()
            if current_sink in sink_volume:
                volume = max(sink_volume[current_sink])
            else:
                volume = 0
            self.speaker_scale.set_value(volume * 100.0 / pypulse.NORMAL_VOLUME_VALUE)
        # if sources list is empty, then can't set input volume
        current_source = pypulse.get_fallback_source_index()
        sources = pypulse.PULSE.get_input_devices()
        if current_source is None:
            microphone_hbox.set_sensitive(False)
        # set input volume
        elif current_source in sources:
            is_mute = sources[current_source]['mute']
            self.microphone_mute_button.set_active(not is_mute)
            self.microphone_scale.set_enable(not is_mute)
            source_volume = pypulse.PULSE.get_input_volume()
            if current_source in source_volume:
                volume = max(source_volume[current_source])
            else:
                volume = 0
            self.microphone_scale.set_value(volume * 100.0 / pypulse.NORMAL_VOLUME_VALUE)

        # widget signals
        self.speaker_mute_button.connect("toggled", self.speaker_toggled)
        self.microphone_mute_button.connect("toggled", self.microphone_toggled)
        self.speaker_scale.connect("value-changed", self.speaker_scale_value_changed)
        self.microphone_scale.connect("value-changed", self.microphone_scale_value_changed)

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
        ''' speaker hscale value changed callback thread '''
        current_sink = pypulse.get_fallback_sink_index()
        if current_sink is None:
            return
        volume_list = pypulse.PULSE.get_output_volume_by_index(current_sink)
        channel_list = pypulse.PULSE.get_output_channels_by_index(current_sink)
        if not volume_list or not channel_list:
            return
        balance = pypulse.get_volume_balance(channel_list['channels'], volume_list, channel_list['map'])
        volume = int((self.speaker_scale.get_value()) / 100.0 * pypulse.NORMAL_VOLUME_VALUE)
        print "speaker volumel set:", balance, volume
        pypulse.PULSE.set_output_volume_with_balance(current_sink, volume, balance)
        if not self.speaker_mute_button.get_active():
            self.speaker_mute_button.set_active(True)

    def speaker_scale_value_changed(self, widget, value):
        '''set output volume'''
        try:
            SettingVolumeThread(self, self.speaker_value_changed_thread).start()
        except:
            pass

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
        try:
            SettingVolumeThread(self, self.microphone_value_changed_thread).start()
        except:
            pass

    def speaker_toggled(self, button):
        active = button.get_active()
        current_sink = pypulse.get_fallback_sink_index()
        #gtk.gdk.threads_enter()
        self.speaker_scale.set_enable(active)
        #gtk.gdk.threads_leave()
        if current_sink is not None:
            pypulse.PULSE.set_output_mute(current_sink, not active)

    def microphone_toggled(self, button):
        active = button.get_active()
        current_source = pypulse.get_fallback_source_index()
        #gtk.gdk.threads_enter()
        self.microphone_scale.set_enable(active)
        #gtk.gdk.threads_leave()
        if current_source is not None:
            pypulse.PULSE.set_input_mute(current_source, not active)

    #####################################################
    # dbus signals
    def speaker_volume_updated(self, sink, volume):
        # set output volume
        self.speaker_scale.set_data("changed-by-other-app", True)
        self.speaker_scale.set_value(max(volume) * 100.0 / settings.FULL_VOLUME_VALUE)

    def microphone_volume_updated(self, source, volume):
        # set output volume
        self.microphone_scale.set_data("changed-by-other-app", True)
        self.microphone_scale.set_value(max(volume) * 100.0 / settings.FULL_VOLUME_VALUE)

    def pulse_mute_updated(self, dev, is_mute, button):
        if button.get_active() == is_mute:
            button.set_data("changed-by-other-app", True)
            button.set_active(not is_mute)

    def fallback_sink_updated_cb(self, core, sink):
        print 'fallback sink updated', sink
        if not self.speaker_scale.get_sensitive():
            self.speaker_scale.set_sensitive(True)
        settings.CURRENT_SINK = sink
        # disconnect old object signals
        if self.current_sink:
            try:
                self.current_sink.disconnect_by_func(self.speaker_volume_updated)
                self.current_sink.disconnect_by_func(self.pulse_mute_updated)
            except:
                pass
        # connect new object signals
        self.speaker_ports = None
        if settings.CURRENT_SINK:
            self.current_sink = sink = settings.PA_DEVICE[settings.CURRENT_SINK]
            sink.connect("volume-updated", self.speaker_volume_updated)
            sink.connect("mute-updated", self.pulse_mute_updated, self.speaker_mute_button)
        self.speaker_mute_button.set_active(not settings.get_mute(settings.CURRENT_SINK))
        self.speaker_scale.set_value(settings.get_volume(settings.CURRENT_SINK) * 100.0 / settings.FULL_VOLUME_VALUE)

    def fallback_source_udpated_cb(self, core, source):
        print 'fallback source updated', source
        if not self.microphone_scale.get_sensitive():
            self.microphone_scale.set_sensitive(True)
        settings.CURRENT_SOURCE = source
        # disconnect old object signals
        if self.current_source:
            try:
                self.current_source.disconnect_by_func(self.microphone_volume_updated)
                self.current_source.disconnect_by_func(self.pulse_mute_updated)
            except:
                pass
        # connect new object signals
        self.microphone_ports = None
        if settings.CURRENT_SOURCE:
            self.current_source = source = settings.PA_DEVICE[settings.CURRENT_SOURCE]
            source.connect("volume-updated", self.microphone_volume_updated)
            source.connect("mute-updated", self.pulse_mute_updated, self.microphone_mute_button)
        self.microphone_mute_button.set_active(not settings.get_mute(settings.CURRENT_SOURCE))
        self.microphone_scale.set_value(settings.get_volume(settings.CURRENT_SOURCE) * 100.0 / settings.FULL_VOLUME_VALUE)

    def fallback_sink_unset_cb(self, core):
        print 'fallback sink unset'
        box.set_sensitive(False)

    def fallback_source_unset_cb(self, core):
        print 'fallback source unset'
        box.set_sensitive(False)
gobject.type_register(TrayGui)
