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

from theme import app_theme
from dtk.ui.label import Label
from dtk.ui.button import Button
from dtk.ui.tab_window import TabBox
from dtk.ui.new_slider import HSlider
from dtk.ui.combo import ComboBox
#from dtk.ui.scalebar import HScalebar
#from dtk.ui.new_treeview import TreeView
from dtk.ui.utils import cairo_disable_antialias, get_parent_dir
from treeitem import MyTreeItem as TreeItem
from treeitem import MyTreeView as TreeView
from nls import _
import gtk
import pangocairo
import pango
import settings

import sys
import os
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from module_frame import ModuleFrame

class SoundSetting(object):
    '''keyboard setting class'''
    def __init__(self, module_frame):
        self.module_frame = module_frame
        
        self.image_widgets = {}
        self.label_widgets = {}
        self.button_widgets = {}
        self.adjust_widgets = {}
        self.scale_widgets = {}
        self.alignment_widgets = {}
        self.container_widgets = {}
        self.view_widgets = {}

        self.__create_widget()
        self.__adjust_widget()
        self.__signals_connect()

    def __create_widget(self):
        '''create gtk widget'''
        title_item_font_size = 12
        option_item_font_szie = 9

        self.label_widgets["balance"] = Label(_("Balance"), text_size=title_item_font_size)
        self.label_widgets["speaker"] = Label(_("Speaker"), text_size=title_item_font_size)
        self.label_widgets["microphone"] = Label(_("Microphone"), text_size=title_item_font_size)
        #####################################
        # image init
        self.image_widgets["balance"] = gtk.image_new_from_file(
            app_theme.get_theme_file_path("image/set/balance.png"))
        self.image_widgets["speaker"] = gtk.image_new_from_file(
            app_theme.get_theme_file_path("image/set/speaker.png"))
        self.image_widgets["microphone"] = gtk.image_new_from_file(
            app_theme.get_theme_file_path("image/set/microphone.png"))
        self.image_widgets["switch_bg_active"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/toggle_bg_active.png"))
        self.image_widgets["switch_bg_nornal"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/toggle_bg_normal.png"))
        self.image_widgets["switch_fg"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/toggle_fg.png"))
        self.image_widgets["device"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/device.png"))
        # button init
        self.button_widgets["balance"] = gtk.ToggleButton()
        self.button_widgets["speaker"] = gtk.ToggleButton()
        self.button_widgets["microphone"] = gtk.ToggleButton()
        self.button_widgets["advanced"] = Button("Adcanced")
        '''
        TODO: it is able to set max_width to make ComboBox more cute :)
        '''
        self.button_widgets["speaker_combo"] = ComboBox([(' ', 0)], max_width=530)
        self.button_widgets["microphone_combo"] = ComboBox([(' ', 0)], max_width=530)
        # container init
        self.container_widgets["slider"] = HSlider()
        self.container_widgets["advance_set_tab_box"] = TabBox()
        self.container_widgets["main_hbox"] = gtk.HBox(False)
        self.container_widgets["left_vbox"] = gtk.VBox(False)
        self.container_widgets["right_vbox"] = gtk.VBox(False)
        self.container_widgets["balance_main_vbox"] = gtk.VBox(False)     # balance
        self.container_widgets["balance_label_hbox"] = gtk.HBox(False)
        self.container_widgets["balance_table"] = gtk.Table(1, 1)
        self.container_widgets["balance_scale_hbox"] = gtk.HBox(False)
        self.container_widgets["speaker_main_vbox"] = gtk.VBox(False)     # speaker
        self.container_widgets["speaker_label_hbox"] = gtk.HBox(False)
        self.container_widgets["speaker_table"] = gtk.Table(2, 1)
        self.container_widgets["microphone_main_vbox"] = gtk.VBox(False)     # microphone
        self.container_widgets["microphone_label_hbox"] = gtk.HBox(False)
        self.container_widgets["microphone_table"] = gtk.Table(2, 1)
        # alignment init
        self.alignment_widgets["left"] = gtk.Alignment()
        self.alignment_widgets["right"] = gtk.Alignment()
        self.alignment_widgets["balance_label"] = gtk.Alignment()            # balance
        self.alignment_widgets["balance_set"] = gtk.Alignment()
        self.alignment_widgets["speaker_label"] = gtk.Alignment()      # speaker
        self.alignment_widgets["speaker_set"] = gtk.Alignment()
        self.alignment_widgets["microphone_label"] = gtk.Alignment()      # microphone
        self.alignment_widgets["microphone_set"] = gtk.Alignment()
        self.alignment_widgets["advanced"] = gtk.Alignment()
        # adjust init
        self.adjust_widgets["balance"] = gtk.Adjustment(0, -1.0, 1.0)
        self.adjust_widgets["speaker"] = gtk.Adjustment(0, 0, 150)
        self.adjust_widgets["microphone"] = gtk.Adjustment(0, 0, 150)
        # scale init
        self.scale_widgets["balance"] = gtk.HScale()
        self.scale_widgets["balance"].set_draw_value(False)
        #self.scale_widgets["balance"] = HScalebar(
            #app_theme.get_pixbuf("scalebar/l_fg.png"),
            #app_theme.get_pixbuf("scalebar/l_bg.png"),
            #app_theme.get_pixbuf("scalebar/m_fg.png"),
            #app_theme.get_pixbuf("scalebar/m_bg.png"),
            #app_theme.get_pixbuf("scalebar/r_fg.png"),
            #app_theme.get_pixbuf("scalebar/r_bg.png"),
            #app_theme.get_pixbuf("scalebar/point.png"))
        self.scale_widgets["balance"].set_adjustment(self.adjust_widgets["balance"])
        self.scale_widgets["speaker"] = gtk.HScale()
        #self.scale_widgets["speaker"].set_draw_value(False)
        #self.scale_widgets["speaker"] = HScalebar(
            #app_theme.get_pixbuf("scalebar/l_fg.png"),
            #app_theme.get_pixbuf("scalebar/l_bg.png"),
            #app_theme.get_pixbuf("scalebar/m_fg.png"),
            #app_theme.get_pixbuf("scalebar/m_bg.png"),
            #app_theme.get_pixbuf("scalebar/r_fg.png"),
            #app_theme.get_pixbuf("scalebar/r_bg.png"),
            #app_theme.get_pixbuf("scalebar/point.png"))
        self.scale_widgets["speaker"].set_adjustment(self.adjust_widgets["speaker"])
        self.scale_widgets["microphone"] = gtk.HScale()
        #self.scale_widgets["microphone"].set_draw_value(False)
        #self.scale_widgets["microphone"] = HScalebar(
            #app_theme.get_pixbuf("scalebar/l_fg.png"),
            #app_theme.get_pixbuf("scalebar/l_bg.png"),
            #app_theme.get_pixbuf("scalebar/m_fg.png"),
            #app_theme.get_pixbuf("scalebar/m_bg.png"),
            #app_theme.get_pixbuf("scalebar/r_fg.png"),
            #app_theme.get_pixbuf("scalebar/r_bg.png"),
            #app_theme.get_pixbuf("scalebar/point.png"))
        self.scale_widgets["microphone"].set_adjustment(self.adjust_widgets["microphone"])
        ###################################
        # advance set
        self.container_widgets["advance_input_box"] = gtk.VBox(False)
        self.container_widgets["advance_output_box"] = gtk.VBox(False)
        self.container_widgets["advance_hardware_box"] = gtk.VBox(False)
        self.alignment_widgets["advance_input_box"] = gtk.Alignment()
        self.alignment_widgets["advance_output_box"] = gtk.Alignment()
        self.alignment_widgets["advance_hardware_box"] = gtk.Alignment()
        #
        self.label_widgets["ad_output"] = Label(_("Choose a device for sound output:"))
        self.label_widgets["ad_input"] = Label(_("Choose a device for sound input:"))
        self.label_widgets["ad_hardware"] = Label(_("Choose a device to configure:"))
        #
        self.container_widgets["ad_output"] = gtk.VBox(False)
        self.container_widgets["ad_input"] = gtk.VBox(False)
        self.container_widgets["ad_hardware"] = gtk.VBox(False)
        #
        self.view_widgets["ad_output"] = TreeView()
        self.view_widgets["ad_input"] = TreeView()
        self.view_widgets["ad_hardware"] = TreeView()
     
    def __adjust_widget(self):
        ''' adjust widget '''
        self.container_widgets["slider"].append_page(self.container_widgets["main_hbox"])
        self.container_widgets["slider"].append_page(self.container_widgets["advance_set_tab_box"])
        
        self.container_widgets["advance_set_tab_box"].add_items(
            [(_("Input"), self.alignment_widgets["advance_input_box"]),
             (_("Output"), self.alignment_widgets["advance_output_box"]),
             (_("Hardware"), self.alignment_widgets["advance_hardware_box"])])
        ###########################
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["left"])
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["right"], False, False)
        self.alignment_widgets["left"].add(self.container_widgets["left_vbox"])
        self.alignment_widgets["right"].add(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].set_size_request(200, -1)
        # set left padding
        self.alignment_widgets["left"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["left"].set_padding(15, 0, 20, 0)
        # set right padding
        self.alignment_widgets["right"].set(0.0, 0.0, 0.0, 0.0)
        self.alignment_widgets["right"].set_padding(15, 0, 0, 0)
        
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["balance_main_vbox"], False, False)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["speaker_main_vbox"], False, False, 10)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["microphone_main_vbox"], False, False, 10)
        self.container_widgets["left_vbox"].pack_start(
            self.alignment_widgets["advanced"], False, False, 10)
        # balance
        self.alignment_widgets["balance_label"].add(self.container_widgets["balance_label_hbox"])
        self.alignment_widgets["balance_set"].add(self.container_widgets["balance_table"])
        self.container_widgets["balance_table"].attach(self.container_widgets["balance_scale_hbox"], 0, 1, 0, 1)
        # alignment set
        self.alignment_widgets["balance_label"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["balance_set"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["balance_label"].set_padding(0, 0, 5, 5)
        self.alignment_widgets["balance_set"].set_padding(0, 0, 20, 71)
        self.container_widgets["balance_main_vbox"].pack_start(
            self.alignment_widgets["balance_label"])
        self.container_widgets["balance_main_vbox"].pack_start(
            self.alignment_widgets["balance_set"], True, True, 10)
        # tips lable
        self.container_widgets["balance_label_hbox"].pack_start(
            self.image_widgets["balance"], False, False)
        self.container_widgets["balance_label_hbox"].pack_start(
            self.label_widgets["balance"], False, False, 15)
        self.container_widgets["balance_label_hbox"].pack_start(
            self.button_widgets["balance"], False, False, 25)
        self.button_widgets["balance"].set_size_request(49, 22)
        # 
        self.container_widgets["balance_scale_hbox"].pack_start(self.scale_widgets["balance"])
        self.scale_widgets["balance"].add_mark(self.adjust_widgets["balance"].get_lower(), gtk.POS_BOTTOM, _("Left"))
        self.scale_widgets["balance"].add_mark(self.adjust_widgets["balance"].get_upper(), gtk.POS_BOTTOM, _("Right"))
        self.scale_widgets["balance"].add_mark(0, gtk.POS_TOP, "0")

        # speaker
        self.alignment_widgets["speaker_label"].add(self.container_widgets["speaker_label_hbox"])
        self.alignment_widgets["speaker_set"].add(self.container_widgets["speaker_table"])
        #
        self.alignment_widgets["speaker_label"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["speaker_set"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["speaker_label"].set_padding(0, 0, 5, 5)
        self.alignment_widgets["speaker_set"].set_padding(0, 0, 20, 71)
        self.container_widgets["speaker_main_vbox"].pack_start(
            self.alignment_widgets["speaker_label"])
        self.container_widgets["speaker_main_vbox"].pack_start(
            self.alignment_widgets["speaker_set"], True, True, 10)
        # tips lable
        self.container_widgets["speaker_label_hbox"].pack_start(
            self.image_widgets["speaker"], False, False)
        self.container_widgets["speaker_label_hbox"].pack_start(
            self.label_widgets["speaker"], False, False, 15)
        self.container_widgets["speaker_label_hbox"].pack_start(
            self.button_widgets["speaker"], False, False, 25)
        self.button_widgets["speaker"].set_size_request(49, 22)
        # 
        self.container_widgets["speaker_table"].attach(
            self.button_widgets["speaker_combo"], 0, 1, 0, 1)
        self.container_widgets["speaker_table"].attach(
            self.scale_widgets["speaker"], 0, 1, 1, 2)
        self.container_widgets["speaker_table"].set_row_spacing(0, 10)
        #self.scale_widgets["speaker"].add_mark(100, gtk.POS_BOTTOM, "100%")
        
        # microphone
        self.alignment_widgets["microphone_label"].add(self.container_widgets["microphone_label_hbox"])
        self.alignment_widgets["microphone_set"].add(self.container_widgets["microphone_table"])
        self.alignment_widgets["microphone_label"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["microphone_set"].set(0.5, 0.5, 1.0, 1.0)
        self.alignment_widgets["microphone_set"].set_padding(0, 0, 20, 71)
        self.alignment_widgets["microphone_label"].set_padding(0, 0, 5, 5)
        self.container_widgets["microphone_main_vbox"].pack_start(
            self.alignment_widgets["microphone_label"])
        self.container_widgets["microphone_main_vbox"].pack_start(
            self.alignment_widgets["microphone_set"], True, True, 10)
        # tips lable
        self.container_widgets["microphone_label_hbox"].pack_start(
            self.image_widgets["microphone"], False, False)
        self.container_widgets["microphone_label_hbox"].pack_start(
            self.label_widgets["microphone"], False, False, 15)
        self.container_widgets["microphone_label_hbox"].pack_start(
            self.button_widgets["microphone"], False, False, 25)
        self.button_widgets["microphone"].set_size_request(49, 22)
        #
        self.container_widgets["microphone_table"].attach(
            self.button_widgets["microphone_combo"], 0, 1, 0, 1)
        self.container_widgets["microphone_table"].attach(
            self.scale_widgets["microphone"], 0, 1, 1, 2)
        self.container_widgets["microphone_table"].set_row_spacing(0, 10)
        #self.scale_widgets["microphone"].add_mark(100, gtk.POS_BOTTOM, "100%")

        self.alignment_widgets["advanced"].set(1.0, 0.5, 0, 0)
        self.alignment_widgets["advanced"].set_padding(0, 0, 20, 71)
        self.alignment_widgets["advanced"].add(self.button_widgets["advanced"])

        # advanced
        self.alignment_widgets["advance_input_box"].add(self.container_widgets["advance_input_box"])
        self.alignment_widgets["advance_output_box"].add(self.container_widgets["advance_output_box"])
        self.alignment_widgets["advance_hardware_box"].add(self.container_widgets["advance_hardware_box"])

        self.alignment_widgets["advance_input_box"].set_padding(0, 0, 20, 10)
        self.alignment_widgets["advance_output_box"].set_padding(0, 0, 20, 10)
        self.alignment_widgets["advance_hardware_box"].set_padding(0, 0, 20, 10)
        
        self.container_widgets["advance_input_box"].set_size_request(790, 380)
        self.container_widgets["advance_output_box"].set_size_request(790, 380)
        self.container_widgets["advance_hardware_box"].set_size_request(790, 380)
        
        self.container_widgets["advance_input_box"].pack_start(self.label_widgets["ad_output"], False, False, 10)
        self.container_widgets["advance_input_box"].pack_start(self.view_widgets["ad_output"])

        self.container_widgets["advance_output_box"].pack_start(self.label_widgets["ad_input"], False, False, 10)
        self.container_widgets["advance_output_box"].pack_start(self.view_widgets["ad_input"])

        self.container_widgets["advance_hardware_box"].pack_start(self.label_widgets["ad_hardware"], False, False, 10)
        self.container_widgets["advance_hardware_box"].pack_start(self.view_widgets["ad_hardware"])
        # if PulseAudio connect error, set the widget insensitive
        if settings.PA_CORE is None:
            self.container_widgets["main_hbox"].set_sensitive(False)
            return
        # if sinks list is empty, then can't set output volume
        if settings.CURRENT_SINK is None:
            self.container_widgets["balance_main_vbox"].set_sensitive(False)
            self.container_widgets["speaker_main_vbox"].set_sensitive(False)
        # if sources list is empty, then can't set input volume
        if settings.CURRENT_SOURCE is None:
            self.container_widgets["microphone_main_vbox"].set_sensitive(False)
        
        # TODO 设置均衡器的值
        # set output volume
        if settings.CURRENT_SINK:
            # set balance
            # if is Mono
            if settings.PA_CHANNELS[settings.CURRENT_SINK]['channel_num'] == 1:
                self.container_widgets["balance_main_vbox"].set_sensitive(False)
            else:
                volumes = settings.get_volumes(settings.CURRENT_SINK)
                if volumes[0] == volumes[1]:
                    value = 0
                elif volumes[0] > volumes[1]:     # if left
                    value = float(volumes[1]) / volumes[0] - 1
                else:
                    value = 1 - float(volumes[0]) / volumes[1]
                self.adjust_widgets["balance"].set_value(value)
            self.button_widgets["balance"].set_active(True) # TODO 
            self.button_widgets["speaker"].set_active(not settings.get_mute(settings.CURRENT_SINK))
            self.speaker_ports = settings.get_port_list(settings.CURRENT_SINK)
            if self.speaker_ports:
                items = []
                i = 0
                select_index = self.speaker_ports[1]
                for port in self.speaker_ports[0]:
                    items.append((port.get_description(), i))
                    i += 1
                self.button_widgets["speaker_combo"].set_items(items, select_index, 530)
            self.adjust_widgets["speaker"].set_value(
                settings.get_volume(settings.CURRENT_SINK) * 100.0 / settings.FULL_VOLUME_VALUE)
        # set input volume
        if settings.CURRENT_SOURCE:
            self.button_widgets["microphone"].set_active(not settings.get_mute(settings.CURRENT_SOURCE))
            self.microphone_ports = settings.get_port_list(settings.CURRENT_SOURCE)
            if self.microphone_ports:
                items = []
                select_index = self.microphone_ports[1]
                i = 0
                for port in self.microphone_ports[0]:
                    items.append((port.get_description(), i))
                    i += 1
                self.button_widgets["microphone_combo"].set_items(items, select_index, 530)
            self.adjust_widgets["microphone"].set_value(
                settings.get_volume(settings.CURRENT_SOURCE) * 100.0 / settings.FULL_VOLUME_VALUE)
        # TODO 双击切换设备
        # output list
        output_list = []
        for sink in settings.PA_CARDS[settings.CURRENT_CARD]["sink"]:
            prop = settings.get_object_property_list(sink)
            if prop:
                output_list.append(TreeItem(self.image_widgets["device"], prop["device.description"]))
        self.view_widgets["ad_output"].add_items(output_list)
        # input list
        input_list = []
        for source in settings.PA_CARDS[settings.CURRENT_CARD]["source"]:
            prop = settings.get_object_property_list(source)
            if prop:
                input_list.append(TreeItem(self.image_widgets["device"], prop["device.description"]))
        self.view_widgets["ad_input"].add_items(input_list)
        # hardware list
        card_list = []
        for cards in settings.PA_CARD_LIST:
            prop = settings.get_object_property_list(settings.PA_CARDS[cards]['obj'])
            if prop:
                card_list.append(TreeItem(self.image_widgets["device"], prop["device.description"]))
        self.view_widgets["ad_hardware"].add_items(card_list)
        
    def __signals_connect(self):
        ''' widget signals connect'''
        self.button_widgets["balance"].connect("expose-event", self.toggle_button_expose)
        self.button_widgets["speaker"].connect("expose-event", self.toggle_button_expose)
        self.button_widgets["microphone"].connect("expose-event", self.toggle_button_expose)

        self.button_widgets["balance"].connect("toggled", self.toggle_button_toggled, "balance")
        self.button_widgets["speaker"].connect("toggled", self.toggle_button_toggled, "speaker")
        self.button_widgets["microphone"].connect("toggled", self.toggle_button_toggled, "microphone")

        self.scale_widgets["speaker"].connect("format-value", lambda w, v: "%d%%" % (v))
        self.scale_widgets["microphone"].connect("format-value", lambda w, v: "%d%%" % (v))
        
        self.adjust_widgets["balance"].connect("value-changed", self.balance_value_changed)
        self.adjust_widgets["speaker"].connect("value-changed", self.speaker_value_changed)
        self.adjust_widgets["microphone"].connect("value-changed", self.microphone_value_changed)

        self.button_widgets["speaker_combo"].connect("item-selected", self.speaker_port_changed)
        self.button_widgets["microphone_combo"].connect("item-selected", self.microphone_port_changed)
        if settings.CURRENT_SINK:
            sink = settings.PA_DEVICE[settings.CURRENT_SINK]
            sink.connect("volume-updated", self.speaker_volume_update)

        self.button_widgets["advanced"].connect("clicked", self.slider_to_advanced)
    
    ######################################
    def toggle_button_expose(self, button, event):
        ''' toggle button expose'''
        cr = button.window.cairo_create()
        x, y, w, h = button.allocation
        if button.get_active():
            cr.set_source_pixbuf(
                self.image_widgets["switch_bg_active"], x, y) 
            cr.paint()
            offet_x = self.image_widgets["switch_bg_active"].get_width() - self.image_widgets["switch_fg"].get_width()
            cr.set_source_pixbuf(
                self.image_widgets["switch_fg"], x+offet_x, y) 
            cr.paint()
        else:
            cr.set_source_pixbuf(
                self.image_widgets["switch_bg_nornal"], x, y) 
            cr.paint()
            cr.set_source_pixbuf(
                self.image_widgets["switch_fg"], x, y) 
            cr.paint()
        return True

    def toggle_button_toggled(self, button, tp):
        if tp == "balance":
            callback = self.balance_toggled
        elif tp == "speaker":
            callback = self.speaker_toggled
        elif tp == "microphone":
            callback = self.microphone_toggled
        else:
            return
        callback(button.get_active())
    
    def balance_toggled(self, active):
        if not active:
            self.adjust_widgets["balance"].set_value(0)
            #self.adjust_widgets["balance"].value_changed()
        self.scale_widgets["balance"].set_sensitive(active)
    
    def speaker_toggled(self, active):
        if settings.CURRENT_SINK:
            settings.set_mute(settings.CURRENT_SINK, not active)
    
    def microphone_toggled(self, active):
        if settings.CURRENT_SOURCE:
            settings.set_mute(settings.CURRENT_SOURCE, not active)
    
    def balance_value_changed(self, adjustment):
        ''' set balance value'''
        value = adjustment.get_value()
        sink = settings.CURRENT_SINK
        if value < 0:       # is left, and reduce right volume
            volume = settings.get_volume(sink)
            volume2 = volume * (1 + value)
            settings.set_volumes(sink, [volume, volume2])
        elif value > 0:     # is right, and reduce left volume
            volume = settings.get_volume(sink)
            volume2 = volume * (1 - value)
            settings.set_volumes(sink, [volume2, volume])
        else:               # is balance
            settings.set_volume(sink, settings.get_volume(sink))
    
    def speaker_value_changed(self, adjustment):
        '''set output volume'''
        value = adjustment.get_value()
        balance = self.adjust_widgets["balance"].get_value()
        sink = settings.CURRENT_SINK
        volume_list = []
        volume = value / 100 * settings.FULL_VOLUME_VALUE
        if balance < 0:
            volume_list.append(volume)
            volume_list.append(volume * (1 + balance))
        else:
            volume_list.append(volume * (1 - balance))
            volume_list.append(volume)
        settings.set_volumes(sink, volume_list)
        if not self.button_widgets["speaker"].get_active():
            self.button_widgets["speaker"].set_active(True)
    
    def microphone_value_changed(self, adjustment):
        ''' set input volume'''
        value = adjustment.get_value()
        volume = value / 100 * settings.FULL_VOLUME_VALUE
        source = settings.CURRENT_SOURCE
        settings.set_volume(source, volume)
        if not self.button_widgets["microphone"].get_active():
            self.button_widgets["microphone"].set_active(True)
    
    def speaker_volume_update(self, sink, volume):
        print "sink volume update:", volume

    def speaker_port_changed(self, combo, content, value, index):
        print "port changed:", content, value, index
        port = self.speaker_ports[0][index]
        print port.get_description()
        print port.object_path, port.dbus_proxy
        dev = settings.PA_DEVICE[settings.CURRENT_SINK]
        import dbus
        dev.set_active_port(dbus.ObjectPath(port.object_path))
        
    def microphone_port_changed(self, combo, content, value, index):
        print "port changed:", content, value, index
        print self.microphone_ports[0][index].get_description()
    
    def slider_to_advanced(self, button):
            self.container_widgets["slider"].slide_to_page(
                self.container_widgets["advance_set_tab_box"], "right")
            self.module_frame.send_submodule_crumb(2, _("Advanced"))
    
    def set_to_default(self):
        '''set to the default'''
        pass
    
if __name__ == '__main__':
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    mouse_settings = SoundSetting(module_frame)
    
    module_frame.add(mouse_settings.container_widgets["slider"])
    module_frame.connect("realize", 
        lambda w: mouse_settings.container_widgets["slider"].set_to_page(
        mouse_settings.container_widgets["main_hbox"]))
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "click_crumb":
            (crumb_index, crumb_label) = message_content
            if crumb_index == 1:
                mouse_settings.container_widgets["slider"].slide_to_page(
                    mouse_settings.container_widgets["main_hbox"], "left")
        elif message_type == "show_again":
            mouse_settings.container_widgets["slider"].set_to_page(
                mouse_settings.container_widgets["main_hbox"])
            module_frame.send_module_info()

    module_frame.module_message_handler = message_handler        
    
    module_frame.run()
