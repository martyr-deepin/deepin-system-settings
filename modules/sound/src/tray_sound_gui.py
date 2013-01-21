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

import settings
import threading as td
import gtk
import gobject

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
        separator_color = [(0, ("#777777", 0.8)), (0.5, ("#777777", 0.8)), (1, ("#777777", 0.8))]
        hseparator = HSeparator(separator_color, 0, 0)
        #hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        hseparator.set_size_request(150, 3)
        hbox.pack_start(self.__make_align(Label(_("Device"))), False, False)
        hbox.pack_start(self.__make_align(hseparator), True, True)
        self.pack_start(hbox, False, False)

        speaker_hbox = gtk.HBox(False)
        speaker_hbox.set_spacing(WIDGET_SPACING)
        speaker_img = ImageBox(app_theme.get_pixbuf("sound/speaker-3.png"))
        self.speaker_scale = HScalebar(show_value=False, format_value="%", value_min=0, value_max=150)
        self.speaker_scale.set_size_request(150, 10)
        self.speaker_mute_button = OffButton()
        speaker_hbox.pack_start(self.__make_align(speaker_img), False, False)
        speaker_hbox.pack_start(self.__make_align(self.speaker_scale, yalign=0.5, yscale=0.0, height=30))
        speaker_hbox.pack_start(self.__make_align(self.speaker_mute_button), False, False)
        self.pack_start(speaker_hbox, False, False)

        microphone_hbox = gtk.HBox(False)
        microphone_hbox.set_spacing(WIDGET_SPACING)
        microphone_img = ImageBox(app_theme.get_pixbuf("sound/microphone.png"))
        self.microphone_scale = HScalebar(show_value=False, format_value="%", value_min=0, value_max=150)
        self.microphone_scale.set_size_request(150, 10)
        self.microphone_mute_button = OffButton()
        microphone_hbox.pack_start(self.__make_align(microphone_img), False, False)
        microphone_hbox.pack_start(self.__make_align(self.microphone_scale, yalign=0.5, yscale=0.0, height=30))
        microphone_hbox.pack_start(self.__make_align(self.microphone_mute_button), False, False)
        self.pack_start(microphone_hbox, False, False)

        hseparator = HSeparator(separator_color, 0, 0)
        hseparator.set_size_request(150, 3)
        self.pack_start(hseparator, False, False)
        button_more = SelectButton(_("更多高级选项..."))
        self.pack_start((button_more), False, False)
        ##########################################
        # if PulseAudio connect error, set the widget insensitive
        if settings.PA_CORE is None or not settings.PA_CARDS:
            self.set_sensitive(False)
            return
        # if sinks list is empty, then can't set output volume
        if settings.CURRENT_SINK is None:
            speaker_hbox.set_sensitive(False)
        # if sources list is empty, then can't set input volume
        if settings.CURRENT_SOURCE is None:
            microphone_hbox.set_sensitive(False)
        # set output volume
        if settings.CURRENT_SINK:
            is_mute = settings.get_mute(settings.CURRENT_SINK)
            self.speaker_mute_button.set_active(not is_mute)
            self.speaker_scale.set_enable(not is_mute)
            self.speaker_scale.set_value(settings.get_volume(settings.CURRENT_SINK) * 100.0 / settings.FULL_VOLUME_VALUE)
        # set input volume
        self.microphone_ports = None
        if settings.CURRENT_SOURCE:
            is_mute = settings.get_mute(settings.CURRENT_SOURCE)
            self.microphone_mute_button.set_active(not is_mute)
            self.microphone_scale.set_enable(not is_mute)
            self.microphone_scale.set_value(settings.get_volume(settings.CURRENT_SOURCE) * 100.0 / settings.FULL_VOLUME_VALUE)

        # widget signals
        self.speaker_mute_button.connect("toggled", self.speaker_toggled)
        self.microphone_mute_button.connect("toggled", self.microphone_toggled)
        self.speaker_scale.connect("value-changed", self.speaker_scale_value_changed)
        self.microphone_scale.connect("value-changed", self.microphone_scale_value_changed)
        # dbus signals
        self.current_sink = None
        if settings.CURRENT_SINK:
            self.current_sink = sink = settings.PA_DEVICE[settings.CURRENT_SINK]
            sink.connect("volume-updated", self.speaker_volume_updated)
            sink.connect("mute-updated", self.pulse_mute_updated, self.speaker_mute_button)
        self.current_source = None
        if settings.CURRENT_SOURCE:
            self.current_source = source = settings.PA_DEVICE[settings.CURRENT_SOURCE]
            source.connect("volume-updated", self.microphone_volume_updated)
            source.connect("mute-updated", self.pulse_mute_updated, self.microphone_mute_button)
        if settings.PA_CORE:
            core = settings.PA_CORE
            core.connect("fallback-sink-updated", self.fallback_sink_updated_cb, speaker_hbox)
            core.connect("fallback-sink-unset", self.fallback_sink_unset_cb, speaker_hbox)
            core.connect("fallback-source-updated", self.fallback_source_udpated_cb, microphone_hbox)
            core.connect("fallback-source-unset", self.fallback_source_unset_cb, microphone_hbox)

    def __make_align(self, widget=None, xalign=0.0, yalign=0.5, xscale=0.0,
                     yscale=0.0, padding_top=0, padding_bottom=0, padding_left=0,
                     padding_right=0, height=CONTAINNER_HEIGHT):
        align = gtk.Alignment()
        align.set_size_request(-1, height)
        align.set(xalign, yalign, xscale, yscale)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        if widget:
            align.add(widget)
        return align

    ####################################################
    # widget signals
    def speaker_value_changed_thread(self):
        ''' speaker hscale value changed callback thread '''
        sink = settings.CURRENT_SINK
        volume = (self.speaker_scale.get_value()) / 100.0 * settings.FULL_VOLUME_VALUE
        settings.set_volume(sink, volume)
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
        value = self.microphone_scale.get_value()
        volume = value / 100.0 * settings.FULL_VOLUME_VALUE
        source = settings.CURRENT_SOURCE
        settings.set_volume(source, volume)
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
        if settings.CURRENT_SINK:
            settings.set_mute(settings.CURRENT_SINK, not active)
        self.speaker_scale.set_enable(active)

    def microphone_toggled(self, button):
        active = button.get_active()
        if settings.CURRENT_SOURCE:
            settings.set_mute(settings.CURRENT_SOURCE, not active)
        self.microphone_scale.set_enable(active)

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

    def fallback_sink_updated_cb(self, core, sink, box):
        print 'fallback sink updated', sink
        if not self.speaker_scale.get_sensitive():
            self.speaker_scale.set_sensitive(True)
        if not box.get_sensitive():
            box.set_sensitive(True)
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

    def fallback_source_udpated_cb(self, core, source, box):
        print 'fallback source updated', source
        if not self.microphone_scale.get_sensitive():
            self.microphone_scale.set_sensitive(True)
        if not box.get_sensitive():
            box.set_sensitive(True)
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

    def fallback_sink_unset_cb(self, core, box):
        print 'fallback sink unset'
        box.set_sensitive(False)

    def fallback_source_unset_cb(self, core, box):
        print 'fallback source unset'
        box.set_sensitive(False)
gobject.type_register(TrayGui)
