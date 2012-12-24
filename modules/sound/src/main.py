#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
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
from dtk.ui.button import Button, ToggleButton
from dtk.ui.tab_window import TabBox
from dtk.ui.new_slider import HSlider
from dtk.ui.combo import ComboBox
from dtk.ui.scalebar import HScalebar
from dtk.ui.utils import get_parent_dir, cairo_disable_antialias, color_hex_to_cairo
from treeitem import MyTreeItem as TreeItem
from treeitem import MyTreeView as TreeView
from nls import _
import gtk
import settings

import sys
import os
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from module_frame import ModuleFrame
from constant import *
import threading as td
import traceback


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

class SoundSetting(object):
    '''sound setting class'''
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
        title_item_font_size = TITLE_FONT_SIZE
        option_item_font_szie = CONTENT_FONT_SIZE

        self.label_widgets["balance"] = Label(_("Balance"), text_size=title_item_font_size)
        self.label_widgets["speaker"] = Label(_("Speaker"), text_size=title_item_font_size)
        self.label_widgets["microphone"] = Label(_("Microphone"), text_size=title_item_font_size)
        self.label_widgets["left"] = Label(_("Left"))
        self.label_widgets["right"] = Label(_("Right"))
        #####################################
        # image init
        self.image_widgets["balance"] = gtk.image_new_from_file(
            app_theme.get_theme_file_path("image/set/balance.png"))
        self.image_widgets["speaker"] = gtk.image_new_from_file(
            app_theme.get_theme_file_path("image/set/speaker.png"))
        self.image_widgets["microphone"] = gtk.image_new_from_file(
            app_theme.get_theme_file_path("image/set/microphone.png"))
        self.image_widgets["device"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/device.png"))
        # button init
        self.button_widgets["balance"] = ToggleButton(
            app_theme.get_pixbuf("set/inactive_normal.png"),
            app_theme.get_pixbuf("set/active_normal.png"))
        self.button_widgets["speaker"] = ToggleButton(
            app_theme.get_pixbuf("set/inactive_normal.png"),
            app_theme.get_pixbuf("set/active_normal.png"))
        self.button_widgets["microphone"] = ToggleButton(
            app_theme.get_pixbuf("set/inactive_normal.png"),
            app_theme.get_pixbuf("set/active_normal.png"))
        self.button_widgets["advanced"] = Button(_("Advanced"))
        self.button_widgets["speaker_combo"] = ComboBox([(' ', 0)], max_width=420)
        self.button_widgets["microphone_combo"] = ComboBox([(' ', 0)], max_width=420)
        # container init
        self.container_widgets["slider"] = HSlider()
        self.container_widgets["advance_set_tab_box"] = TabBox()
        self.container_widgets["main_hbox"] = gtk.HBox(False)
        self.container_widgets["left_vbox"] = gtk.VBox(False)
        self.container_widgets["right_vbox"] = gtk.VBox(False)
        self.container_widgets["balance_hbox"] = gtk.HBox(False)
        self.container_widgets["speaker_main_vbox"] = gtk.VBox(False)     # speaker
        self.container_widgets["speaker_label_hbox"] = gtk.HBox(False)
        self.container_widgets["speaker_table"] = gtk.Table(3, 2)
        self.container_widgets["microphone_main_vbox"] = gtk.VBox(False)     # microphone
        self.container_widgets["microphone_label_hbox"] = gtk.HBox(False)
        self.container_widgets["microphone_table"] = gtk.Table(3, 2)
        self.container_widgets["advanced_hbox"] = gtk.HBox(False)
        # alignment init
        self.alignment_widgets["slider"] = gtk.Alignment()
        self.alignment_widgets["main_hbox"] = gtk.Alignment()
        self.alignment_widgets["advance_set_tab_box"] = gtk.Alignment()
        self.alignment_widgets["left"] = gtk.Alignment()
        self.alignment_widgets["right"] = gtk.Alignment()
        self.alignment_widgets["speaker_label"] = gtk.Alignment()      # speaker
        self.alignment_widgets["speaker_set"] = gtk.Alignment()
        self.alignment_widgets["microphone_label"] = gtk.Alignment()      # microphone
        self.alignment_widgets["microphone_set"] = gtk.Alignment()
        self.alignment_widgets["advanced"] = gtk.Alignment()
        # adjust init
        self.adjust_widgets["balance"] = gtk.Adjustment(0, -1.0, 1.0, 0.1, 0.2)
        self.adjust_widgets["speaker"] = gtk.Adjustment(0, 0, 150, 1, 5)
        self.adjust_widgets["microphone"] = gtk.Adjustment(0, 0, 150, 1, 5)
        # scale init
        self.scale_widgets["balance"] = HScalebar(
            app_theme.get_pixbuf("scalebar/l_fg.png"),
            app_theme.get_pixbuf("scalebar/l_bg.png"),
            app_theme.get_pixbuf("scalebar/m_fg.png"),
            app_theme.get_pixbuf("scalebar/m_bg.png"),
            app_theme.get_pixbuf("scalebar/r_fg.png"),
            app_theme.get_pixbuf("scalebar/r_bg.png"),
            app_theme.get_pixbuf("scalebar/point.png"))
        self.scale_widgets["balance"].set_adjustment(self.adjust_widgets["balance"])
        self.scale_widgets["speaker"] = HScalebar(
            app_theme.get_pixbuf("scalebar/l_fg.png"),
            app_theme.get_pixbuf("scalebar/l_bg.png"),
            app_theme.get_pixbuf("scalebar/m_fg.png"),
            app_theme.get_pixbuf("scalebar/m_bg.png"),
            app_theme.get_pixbuf("scalebar/r_fg.png"),
            app_theme.get_pixbuf("scalebar/r_bg.png"),
            app_theme.get_pixbuf("scalebar/point.png"),
            True,
            '%')
        self.scale_widgets["speaker"].set_adjustment(self.adjust_widgets["speaker"])
        self.scale_widgets["microphone"] = HScalebar(
            app_theme.get_pixbuf("scalebar/l_fg.png"),
            app_theme.get_pixbuf("scalebar/l_bg.png"),
            app_theme.get_pixbuf("scalebar/m_fg.png"),
            app_theme.get_pixbuf("scalebar/m_bg.png"),
            app_theme.get_pixbuf("scalebar/r_fg.png"),
            app_theme.get_pixbuf("scalebar/r_bg.png"),
            app_theme.get_pixbuf("scalebar/point.png"),
            True,
            '%')
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
        MID_SPACING = 10
        RIGHT_BOX_WIDTH = TIP_BOX_WIDTH - 20
        MAIN_AREA_WIDTH = 440
        OPTION_LEFT_PADDING = WIDGET_SPACING + 16
        self.alignment_widgets["slider"].add(self.container_widgets["slider"])
        self.alignment_widgets["slider"].set(0, 0, 1, 1)
        self.container_widgets["slider"].append_page(self.alignment_widgets["main_hbox"])
        self.container_widgets["slider"].append_page(self.alignment_widgets["advance_set_tab_box"])
        self.alignment_widgets["main_hbox"].add(self.container_widgets["main_hbox"])
        self.alignment_widgets["advance_set_tab_box"].add(self.container_widgets["advance_set_tab_box"])
        self.alignment_widgets["main_hbox"].set_padding(
            TEXT_WINDOW_TOP_PADDING, 0, TEXT_WINDOW_LEFT_PADDING, TEXT_WINDOW_RIGHT_WIDGET_PADDING)
        self.alignment_widgets["advance_set_tab_box"].set_padding(
            FRAME_TOP_PADDING, 0, 0, 0)
        
        self.container_widgets["advance_set_tab_box"].add_items(
            [(_("Output"), self.alignment_widgets["advance_output_box"]),
             (_("Input"), self.alignment_widgets["advance_input_box"])])
             #(_("Hardware"), self.alignment_widgets["advance_hardware_box"])])
        ###########################
        self.container_widgets["main_hbox"].set_spacing(MID_SPACING)    # the spacing between left and right
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["left"])
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["right"], False, False)
        self.alignment_widgets["left"].add(self.container_widgets["left_vbox"])
        self.alignment_widgets["right"].add(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].set_size_request(RIGHT_BOX_WIDTH, -1)
        # set left padding
        self.alignment_widgets["left"].set(0.0, 0.0, 1.0, 1.0)
        #self.alignment_widgets["left"].set_padding(15, 0, 20, 0)
        # set right padding
        self.alignment_widgets["right"].set(0.0, 0.0, 1.0, 1.0)
        self.alignment_widgets["right"].set_padding(0, 0, 0, 20)
        
        self.container_widgets["left_vbox"].set_spacing(BETWEEN_SPACING)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["speaker_main_vbox"], False, False)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["microphone_main_vbox"], False, False)

        # speaker
        self.alignment_widgets["speaker_label"].add(self.container_widgets["speaker_label_hbox"])
        self.alignment_widgets["speaker_set"].add(self.container_widgets["speaker_table"])
        #
        self.alignment_widgets["speaker_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["speaker_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["speaker_set"].set(0.0, 0.5, 1.0, 1.0)
        self.alignment_widgets["speaker_set"].set_padding(0, 0, OPTION_LEFT_PADDING, 0)
        self.container_widgets["speaker_main_vbox"].pack_start(
            self.alignment_widgets["speaker_label"])
        self.container_widgets["speaker_main_vbox"].pack_start(
            self.alignment_widgets["speaker_set"])
        # tips lable
        self.container_widgets["speaker_label_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["speaker_label_hbox"].pack_start(
            self.image_widgets["speaker"], False, False)
        self.container_widgets["speaker_label_hbox"].pack_start(
            self.label_widgets["speaker"], False, False)
        # balance
        self.scale_widgets["balance"].add_mark(self.adjust_widgets["balance"].get_lower(), gtk.POS_BOTTOM, _("Left"))
        self.scale_widgets["balance"].add_mark(self.adjust_widgets["balance"].get_upper(), gtk.POS_BOTTOM, _("Right"))
        self.scale_widgets["balance"].add_mark(0, gtk.POS_BOTTOM, "0")
        # 
        self.container_widgets["speaker_table"].set_size_request(MAIN_AREA_WIDTH, -1)
        self.container_widgets["speaker_table"].set_col_spacings(WIDGET_SPACING)
        self.container_widgets["speaker_table"].attach(
            self.__make_align(self.button_widgets["speaker_combo"]), 0, 1, 0, 1, 4)
        self.container_widgets["speaker_table"].attach(
            self.__make_align(self.scale_widgets["speaker"], padding_top=1, height=37), 0, 1, 1, 2, 4)
        self.container_widgets["speaker_table"].attach(
            self.__make_align(self.button_widgets["speaker"], padding_top=18), 1, 2, 1, 2, 0)
        self.container_widgets["speaker_table"].attach(
            self.__make_align(self.scale_widgets["balance"], height=53), 0, 1, 2, 3, 4)
        button_width = self.button_widgets["speaker"].get_size_request()[0]
        self.button_widgets["speaker_combo"].set_size_request(-1, WIDGET_HEIGHT)
        self.scale_widgets["speaker"].set_size_request(MAIN_AREA_WIDTH-button_width, -1)
        self.scale_widgets["balance"].set_size_request(MAIN_AREA_WIDTH-button_width, -1)
        
        # microphone
        self.alignment_widgets["microphone_label"].add(self.container_widgets["microphone_label_hbox"])
        self.alignment_widgets["microphone_set"].add(self.container_widgets["microphone_table"])
        self.alignment_widgets["microphone_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["microphone_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["microphone_set"].set(0.0, 0.5, 1.0, 1.0)
        self.alignment_widgets["microphone_set"].set_padding(0, 0, OPTION_LEFT_PADDING, 0)
        self.container_widgets["microphone_main_vbox"].pack_start(
            self.alignment_widgets["microphone_label"])
        self.container_widgets["microphone_main_vbox"].pack_start(
            self.alignment_widgets["microphone_set"])
        # tips lable
        self.container_widgets["microphone_label_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["microphone_label_hbox"].pack_start(
            self.image_widgets["microphone"], False, False)
        self.container_widgets["microphone_label_hbox"].pack_start(
            self.label_widgets["microphone"], False, False)
        #
        self.container_widgets["microphone_table"].set_size_request(MAIN_AREA_WIDTH, -1)
        self.container_widgets["microphone_table"].set_col_spacings(WIDGET_SPACING)
        self.container_widgets["microphone_table"].attach(
            self.__make_align(self.button_widgets["microphone_combo"]), 0, 1, 0, 1, 4)
        self.container_widgets["microphone_table"].attach(
            self.__make_align(self.scale_widgets["microphone"], height=37), 0, 1, 1, 2, 4)
        self.container_widgets["microphone_table"].attach(
            self.__make_align(self.button_widgets["microphone"], padding_top=18), 1, 2, 1, 2, 0)
        self.container_widgets["microphone_table"].attach(
            self.__make_align(self.container_widgets["advanced_hbox"]), 0, 2, 2, 3, ypadding=15)
        button_width = self.button_widgets["microphone"].get_size_request()[0]
        self.button_widgets["microphone_combo"].set_size_request(-1, WIDGET_HEIGHT)
        self.scale_widgets["microphone"].set_size_request(MAIN_AREA_WIDTH-button_width, -1)

        self.container_widgets["advanced_hbox"].pack_start(self.alignment_widgets["advanced"])
        self.container_widgets["advanced_hbox"].pack_start(self.button_widgets["advanced"], False, False)

        # advanced
        self.alignment_widgets["advance_input_box"].add(self.container_widgets["advance_input_box"])
        self.alignment_widgets["advance_output_box"].add(self.container_widgets["advance_output_box"])
        self.alignment_widgets["advance_hardware_box"].add(self.container_widgets["advance_hardware_box"])

        self.alignment_widgets["advance_input_box"].set_padding(0, 0, 20, 10)
        self.alignment_widgets["advance_output_box"].set_padding(0, 0, 20, 10)
        self.alignment_widgets["advance_hardware_box"].set_padding(0, 0, 20, 10)
        
        self.container_widgets["advance_input_box"].set_size_request(750, 380)
        self.container_widgets["advance_output_box"].set_size_request(750, 380)
        self.container_widgets["advance_hardware_box"].set_size_request(750, 380)
        
        self.container_widgets["advance_input_box"].pack_start(self.label_widgets["ad_input"], False, False, 10)
        self.container_widgets["advance_input_box"].pack_start(self.view_widgets["ad_input"])

        self.container_widgets["advance_output_box"].pack_start(self.label_widgets["ad_output"], False, False, 10)
        self.container_widgets["advance_output_box"].pack_start(self.view_widgets["ad_output"])

        self.container_widgets["advance_hardware_box"].pack_start(self.label_widgets["ad_hardware"], False, False, 10)
        self.container_widgets["advance_hardware_box"].pack_start(self.view_widgets["ad_hardware"])
        # if PulseAudio connect error, set the widget insensitive
        if settings.PA_CORE is None or not settings.PA_CARDS:
            self.container_widgets["main_hbox"].set_sensitive(False)
            return
        # if sinks list is empty, then can't set output volume
        if settings.CURRENT_SINK is None:
            self.scale_widgets["balance"].set_sensitive(False)
            self.container_widgets["speaker_main_vbox"].set_sensitive(False)
        # if sources list is empty, then can't set input volume
        if settings.CURRENT_SOURCE is None:
            self.container_widgets["microphone_main_vbox"].set_sensitive(False)
        
        # set output volume
        self.speaker_ports = None
        if settings.CURRENT_SINK:
            # set balance
            # if is Mono, set it insensitive
            if settings.PA_CHANNELS[settings.CURRENT_SINK]['channel_num'] == 1:
                self.scale_widgets["balance"].set_sensitive(False)
            else:
                volumes = settings.get_volumes(settings.CURRENT_SINK)
                if volumes[0] == volumes[1]:
                    value = 0
                elif volumes[0] > volumes[1]:     # if left
                    value = float(volumes[1]) / volumes[0] - 1
                else:
                    value = 1 - float(volumes[0]) / volumes[1]
                self.adjust_widgets["balance"].set_value(value)
            self.button_widgets["balance"].set_active(True)
            self.button_widgets["speaker"].set_active(not settings.get_mute(settings.CURRENT_SINK))
            self.speaker_ports = settings.get_port_list(settings.CURRENT_SINK)
            if self.speaker_ports:
                items = []
                i = 0
                select_index = self.speaker_ports[1]
                for port in self.speaker_ports[0]:
                    items.append((port.get_description(), i))
                    i += 1
                self.button_widgets["speaker_combo"].set_items(items, select_index, 420)
            self.adjust_widgets["speaker"].set_value(
                settings.get_volume(settings.CURRENT_SINK) * 100.0 / settings.FULL_VOLUME_VALUE)
        # set input volume
        self.microphone_ports = None
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
                self.button_widgets["microphone_combo"].set_items(items, select_index, 420)
            self.adjust_widgets["microphone"].set_value(
                settings.get_volume(settings.CURRENT_SOURCE) * 100.0 / settings.FULL_VOLUME_VALUE)
        card_list = []
        output_list = []
        input_list = []
        output_selected_row = -1
        input_selected_row = -1
        out_index = 0
        in_index = 0
        for cards in settings.PA_CARDS:
            # output list
            for sink in settings.PA_CARDS[cards]["sink"]:
                if sink.object_path == settings.CURRENT_SINK:
                    output_selected_row = out_index
                prop = settings.get_object_property_list(sink)
                if prop:
                    output_list.append(TreeItem(self.image_widgets["device"], prop["device.description"], sink.object_path))
                    out_index += 1
            # input list
            for source in settings.PA_CARDS[cards]["source"]:
                if source.object_path == settings.CURRENT_SOURCE:
                    input_selected_row = in_index
                prop = settings.get_object_property_list(source)
                if prop:
                    input_list.append(TreeItem(self.image_widgets["device"], prop["device.description"], source.object_path))
                    in_index += 1
            # hardware list
            if not cards:
                continue
            prop = settings.get_object_property_list(settings.PA_CARDS[cards]['obj'])
            if prop:
                active_profile = settings.PA_CARDS[cards]['obj'].get_active_profile()
                if active_profile:
                    profile = settings.get_card_profile_property(active_profile)
                    if profile['sinks'] > 1:
                        io_num = _("%d Outputs") % profile['sinks']
                    else:
                        io_num = _("%d Output") % profile['sinks']
                    if profile['sources'] > 1:
                        io_num += " / " + _("%d Inputs") % profile['sources']
                    else:
                        io_num += " / " + _("%d Input") % profile['sources']
                    card_info = "%s(%s)[%s]" % (prop['device.description'].strip('\x00'), io_num, profile['description'])
                else:
                    card_info = prop["device.description"]
                card_list.append(TreeItem(self.image_widgets["device"], card_info, cards))
        self.view_widgets["ad_output"].add_items(output_list)
        self.view_widgets["ad_input"].add_items(input_list)
        self.view_widgets["ad_hardware"].add_items(card_list)
        if not (output_selected_row < 0):
            self.view_widgets["ad_output"].set_select_rows([output_selected_row])
        if not (input_selected_row < 0):
            self.view_widgets["ad_input"].set_select_rows([input_selected_row])
        if card_list:
            self.view_widgets["ad_hardware"].set_select_rows([0])
        
    def __signals_connect(self):
        ''' widget signals connect'''
        # redraw container background white
        self.alignment_widgets["main_hbox"].connect("expose-event", self.container_expose_cb)
        self.alignment_widgets["advance_set_tab_box"].connect("expose-event", self.container_expose_cb)
        
        self.button_widgets["balance"].connect("toggled", self.toggle_button_toggled, "balance")
        self.button_widgets["speaker"].connect("toggled", self.toggle_button_toggled, "speaker")
        self.button_widgets["microphone"].connect("toggled", self.toggle_button_toggled, "microphone")

        # TODO 使用键盘改变scale的值
        self.scale_widgets["balance"].connect("button-release-event", self.balance_scale_value_changed)
        self.scale_widgets["balance"].connect("button-press-event", lambda w, e: self.scale_widgets["balance"].set_data("has_pressed", True))
        self.scale_widgets["balance"].connect("move-slider", self.balance_scale_move_slider_cb)
        self.scale_widgets["speaker"].connect("button-release-event", self.speaker_scale_value_changed)
        self.scale_widgets["speaker"].connect("button-press-event", lambda w, e: self.scale_widgets["speaker"].set_data("has_pressed", True))
        self.scale_widgets["speaker"].connect("move-slider", self.speaker_scale_move_slider_cb)
        self.scale_widgets["microphone"].connect("button-release-event", self.microphone_scale_value_changed)
        self.scale_widgets["microphone"].connect("button-press-event", lambda w, e: self.scale_widgets["microphone"].set_data("has_pressed", True))
        self.scale_widgets["microphone"].connect("move-slider", self.microphone_scale_move_slider_cb)

        self.button_widgets["speaker_combo"].connect("item-selected", self.speaker_port_changed)
        self.button_widgets["microphone_combo"].connect("item-selected", self.microphone_port_changed)
        
        self.button_widgets["advanced"].connect("clicked", self.slider_to_advanced)
        self.view_widgets["ad_output"].connect("single-click-item", self.output_treeview_clicked)
        self.view_widgets["ad_input"].connect("single-click-item", self.input_treeview_clicked)
        self.view_widgets["ad_hardware"].connect("single-click-item", self.card_treeview_clicked)
        self.container_widgets["advance_input_box"].connect("expose-event", self.treeview_container_expose_cb, self.view_widgets["ad_input"])
        self.container_widgets["advance_output_box"].connect("expose-event", self.treeview_container_expose_cb, self.view_widgets["ad_output"])
        self.container_widgets["advance_hardware_box"].connect("expose-event", self.treeview_container_expose_cb, self.view_widgets["ad_hardware"])
        # dbus signals
        self.current_sink = None
        if settings.CURRENT_SINK:
            self.current_sink = sink = settings.PA_DEVICE[settings.CURRENT_SINK]
            sink.connect("volume-updated", self.speaker_volume_updated)
            sink.connect("mute-updated", self.pulse_mute_updated, self.button_widgets["speaker"])
            sink.connect("active-port-updated", self.pulse_active_port_updated,
                         self.button_widgets["speaker_combo"], self.speaker_ports)
            #sink.connect("property-list-updated", self.speaker_volume_updated)
        self.current_source = None
        if settings.CURRENT_SOURCE:
            self.current_source = source = settings.PA_DEVICE[settings.CURRENT_SOURCE]
            source.connect("volume-updated", self.microphone_volume_updated)
            source.connect("mute-updated", self.pulse_mute_updated, self.button_widgets["microphone"])
            source.connect("active-port-updated", self.pulse_active_port_updated,
                           self.button_widgets["microphone_combo"], self.microphone_ports)
        if settings.PA_CORE:
            core = settings.PA_CORE
            core.connect("new-card", self.new_card_cb)
            core.connect("new-sink", self.new_sink_cb)
            core.connect("new-source", self.new_source_cb)
            core.connect("card-removed", self.card_removed_cb)
            core.connect("sink-removed", self.sink_removed_cb)
            core.connect("source-removed", self.source_removed_cb)
            core.connect("fallback-sink-updated", self.fallback_sink_updated_cb)
            core.connect("fallback-sink-unset", self.fallback_sink_unset_cb)
            core.connect("fallback-source-updated", self.fallback_source_udpated_cb)
            core.connect("fallback-source-unset", self.fallback_source_unset_cb)
        for cards in settings.PA_CARDS:
            if not cards:
                continue
            settings.PA_CARDS[cards]['obj'].connect("active-profile-updated", self.card_active_profile_update)
    
    ######################################
    # signals callback begin
    # widget signals
    def container_expose_cb(self, widget, event):
        cr = widget.window.cairo_create()
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                                               
        cr.rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)                                                 
        cr.fill()
    
    def toggle_button_toggled(self, button, tp):
        if button.get_data("changed-by-other-app"):
            button.set_data("changed-by-other-app", False)
            return
        if tp == "balance":
            callback = self.balance_toggled
        elif tp == "speaker":
            callback = self.speaker_toggled
        elif tp == "microphone":
            callback = self.microphone_toggled
        else:
            return
        try:
            SettingVolumeThread(self, callback, button.get_active()).start()
            #callback(button.get_active())
        except:
            traceback.print_exc()
            pass
    
    def balance_toggled(self, active):
        if not active:
            self.adjust_widgets["balance"].set_value(0)
            self.balance_scale_value_changed(self.scale_widgets["balance"], None)
        self.scale_widgets["balance"].set_sensitive(active)
    
    def speaker_toggled(self, active):
        if settings.CURRENT_SINK:
            settings.set_mute(settings.CURRENT_SINK, not active)
    
    def microphone_toggled(self, active):
        if settings.CURRENT_SOURCE:
            settings.set_mute(settings.CURRENT_SOURCE, not active)
    
    def balance_value_changed_thread(self):
        ''' balance value changed callback thread'''
        value = self.adjust_widgets["balance"].get_value()
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
    
    def balance_scale_value_changed(self, widget, event):
        ''' set balance value'''
        if not widget.get_data("has_pressed"):
            return
        widget.set_data("has_pressed", False)
        try:
            SettingVolumeThread(self, self.balance_value_changed_thread).start()
        except:
            traceback.print_exc()
            pass
    
    def balance_scale_move_slider_cb(self, widget, scrolltype):
        try:
            SettingVolumeThread(self, self.balance_value_changed_thread).start()
        except:
            traceback.print_exc()
            pass
    
    def speaker_value_changed_thread(self):
        ''' speaker hscale value changed callback thread '''
        balance = self.adjust_widgets["balance"].get_value()
        sink = settings.CURRENT_SINK
        volume_list = []
        volume = self.adjust_widgets["speaker"].get_value() / 100 * settings.FULL_VOLUME_VALUE
        if balance < 0:
            volume_list.append(volume)
            volume_list.append(volume * (1 + balance))
        else:
            volume_list.append(volume * (1 - balance))
            volume_list.append(volume)
        settings.set_volumes(sink, volume_list)
        if not self.button_widgets["speaker"].get_active():
            self.button_widgets["speaker"].set_active(True)

    def speaker_scale_value_changed(self, widget, event):
        '''set output volume'''
        if not widget.get_data("has_pressed"):
            return
        widget.set_data("has_pressed", False)
        try:
            SettingVolumeThread(self, self.speaker_value_changed_thread).start()
        except:
            traceback.print_exc()
            pass
    
    def speaker_scale_move_slider_cb(self, widget, scrolltype):
        try:
            SettingVolumeThread(self, self.speaker_value_changed_thread).start()
        except:
            traceback.print_exc()
            pass

    def microphone_value_changed_thread(self):
        ''' microphone value changed callback thread'''
        value = self.adjust_widgets["microphone"].get_value()
        volume = value / 100 * settings.FULL_VOLUME_VALUE
        source = settings.CURRENT_SOURCE
        settings.set_volume(source, volume)
        if not self.button_widgets["microphone"].get_active():
            self.button_widgets["microphone"].set_active(True)
        
    def microphone_scale_value_changed(self, widget, event):
        ''' set input volume'''
        if not widget.get_data("has_pressed"):
            return
        widget.set_data("has_pressed", False)
        try:
            SettingVolumeThread(self, self.microphone_value_changed_thread).start()
        except:
            traceback.print_exc()
            pass
    
    def microphone_scale_move_slider_cb(self, widget, scrolltype):
        try:
            SettingVolumeThread(self, self.microphone_value_changed_thread).start()
        except:
            traceback.print_exc()
            pass
    
    def speaker_port_changed_thread(self, port, dev):
        ''' set active port thread '''
        dev.set_active_port(port.object_path)
        
    def speaker_port_changed(self, combo, content, value, index):
        ''' set active port'''
        if not self.speaker_ports:
            return
        port = self.speaker_ports[0][index]
        dev = settings.PA_DEVICE[settings.CURRENT_SINK]
        try:
            SettingVolumeThread(self, self.speaker_port_changed_thread, port, dev).start()
        except:
            traceback.print_exc()
            pass
    
    def microphone_port_changed_thread(self, port, dev):
        ''' set active port thread '''
        dev.set_active_port(port.object_path)
    
    def microphone_port_changed(self, combo, content, value, index):
        if not self.microphone_ports:
            return
        port = self.microphone_ports[0][index]
        dev = settings.PA_DEVICE[settings.CURRENT_SOURCE]
        try:
            SettingVolumeThread(self, self.microphone_port_changed_thread, port, dev).start()
        except:
            traceback.print_exc()
            pass
    
    def treeview_container_expose_cb(self, widget, event, treeview):
        rect = treeview.allocation
        cr = widget.window.cairo_create()
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*color_hex_to_cairo(app_theme.get_color("line_border").get_color()))
            cr.set_line_width(1)
            cr.rectangle(rect.x, rect.y, rect.width+1, rect.height+1)
            cr.stroke()
    
    def output_treeview_clicked(self, tree_view, item, row, *args):
        if item.obj_path == settings.CURRENT_SINK:
            return
        if settings.PA_CORE:
            settings.PA_CORE.set_fallback_sink(item.obj_path)
        
    def input_treeview_clicked(self, tree_view, item, row, *args):
        if item.obj_path == settings.CURRENT_SOURCE:
            return
        if settings.PA_CORE:
            settings.PA_CORE.set_fallback_source(item.obj_path)
        
    def card_treeview_clicked(self, tree_view, item, row, *args):
        print "treeview clicked", item.obj_path, item.content, row
    
    #########################
    # dbus signals 
    def pulse_mute_updated(self, dev, is_mute, button):
        #print "mute updated:", dev.get_active_port(), "is_mute:", is_mute, "button:", not button.get_active()
        if button.get_active() == is_mute:
            button.set_data("changed-by-other-app", True)
            button.set_active(not is_mute)
    
    def speaker_volume_updated(self, sink, volume):
        # set output volume
        self.adjust_widgets["speaker"].set_data("changed-by-other-app", True)
        self.adjust_widgets["speaker"].set_value(max(volume) * 100.0 / settings.FULL_VOLUME_VALUE)
        ## set balance
        dev = sink.object_path
        left_volumes = []
        right_volumes = []
        for channel in settings.PA_CHANNELS[dev]['left']:
            left_volumes.append(volume[channel])
        for channel in settings.PA_CHANNELS[dev]['right']:
            right_volumes.append(volume[channel])
        if not left_volumes:
            left_volumes.append(0)
        if not right_volumes:
            right_volumes.append(0)
        (left_volume, right_volume) = [max(left_volumes), max(right_volumes)]
        if left_volume == right_volume:
            value = 0
        elif left_volume > right_volume:
            value = float(right_volume) / left_volume - 1
        else:
            value = 1 - float(left_volume) / right_volume
        self.adjust_widgets["balance"].set_data("changed-by-other-app", True)
        self.adjust_widgets["balance"].set_value(value)

    def microphone_volume_updated(self, source, volume):
        # set output volume
        self.adjust_widgets["microphone"].set_data("changed-by-other-app", True)
        self.adjust_widgets["microphone"].set_value(max(volume) * 100.0 / settings.FULL_VOLUME_VALUE)
    
    def pulse_active_port_updated(self, dev, port, combo, port_list):
        if not port_list:
            return
        length = len(port_list[0])
        i = 0
        while i < length:
            if port == port_list[0][i].object_path:
                combo.set_select_index(i)
                return
            i += 1
    
    # add / remove device
    def new_card_cb(self, core, card):
        ''' new card '''
        print "new card", core, card
        self.refresh_hardware_treeview()

    def card_removed_cb(self, core, card):
        print 'removed card:', card
        self.refresh_hardware_treeview()

    def refresh_hardware_treeview(self):
        ''' when add/remove card refresh hardware-treeview '''
        settings.refresh_info()
        if settings.PA_CORE is None or not settings.PA_CARDS:
            self.container_widgets["main_hbox"].set_sensitive(False)
        elif not self.container_widgets["main_hbox"].get_sensitive():
            self.container_widgets["main_hbox"].set_sensitive(True)
        card_list = []
        for cards in settings.PA_CARDS:
            if not cards:
                continue
            prop = settings.get_object_property_list(settings.PA_CARDS[cards]['obj'])
            if prop:
                active_profile = settings.PA_CARDS[cards]['obj'].get_active_profile()
                if active_profile:
                    profile = settings.get_card_profile_property(active_profile)
                    if profile['sinks'] > 1:
                        io_num = _("%d Outputs") % profile['sinks']
                    else:
                        io_num = _("%d Output") % profile['sinks']
                    if profile['sources'] > 1:
                        io_num += " / " + _("%d Inputs") % profile['sources']
                    else:
                        io_num += " / " + _("%d Input") % profile['sources']
                    card_info = "%s (%s) [%s]" % (prop["device.description"].strip('\x00'), io_num, profile['description'])
                else:
                    card_info = prop["device.description"]
                card_list.append(TreeItem(self.image_widgets['device'], card_info, cards))
        self.view_widgets["ad_hardware"].add_items(card_list, clear_first=True)
        if card_list:
            self.view_widgets["ad_hardware"].set_select_rows([0])
        
    def card_active_profile_update(self, cards, active_profile):
        ''' Card ActiveProfileUpdted '''
        for item in self.view_widgets["ad_hardware"].visible_items:
            if item.obj_path == cards.object_path:
                prop = settings.get_object_property_list(cards)
                if prop:
                    profile = settings.get_card_profile_property(active_profile)
                    if profile['sinks'] > 1:
                        io_num = _("%d Outputs") % profile['sinks']
                    else:
                        io_num = _("%d Output") % profile['sinks']
                    if profile['sources'] > 1:
                        io_num += " / " + _("%d Inputs") % profile['sources']
                    else:
                        io_num += " / " + _("%d Input") % profile['sources']
                    card_info = "%s (%s) [%s]" % (prop["device.description"].strip('\x00'), io_num, profile['description'])
                    item.content = card_info
                    if item.redraw_request_callback:
                        item.redraw_request_callback(item)
                break
    
    def new_source_cb(self, core, source):
        ''' new source'''
        print "new source", core, source
        self.refresh_input_treeview()
        
    def source_removed_cb(self, core, source):
        print 'removed source:', source
        self.refresh_input_treeview()
    
    def refresh_input_treeview(self):
        ''' when add/remove source refresh input-treeview '''
        settings.refresh_info()
        if settings.CURRENT_SOURCE is None:
            self.container_widgets["microphone_main_vbox"].set_sensitive(False)
        elif not self.container_widgets["microphone_main_vbox"].get_sensitive():
            self.container_widgets["microphone_main_vbox"].set_sensitive(True)
        input_list = []
        input_selected_row = -1
        in_index = 0
        for cards in settings.PA_CARDS:
            for source in settings.PA_CARDS[cards]["source"]:
                if source.object_path == settings.CURRENT_SOURCE:
                    input_selected_row = in_index
                prop = settings.get_object_property_list(source)
                if prop:
                    input_list.append(TreeItem(self.image_widgets["device"], prop["device.description"], source.object_path))
                    in_index += 1
        self.view_widgets["ad_input"].add_items(input_list, clear_first=True)
        if not (input_selected_row < 0):
            self.view_widgets["ad_input"].set_select_rows([input_selected_row])
        
    def new_sink_cb(self, core, sink):
        ''' new sink '''
        print "new sink", core, sink
        self.refresh_output_treeview()
        
    def sink_removed_cb(self, core, sink):
        print 'removed sink:', sink
        self.refresh_output_treeview()
    
    def refresh_output_treeview(self):
        ''' when add/remove sink refresh output-treeview ''' 
        settings.refresh_info()
        if settings.CURRENT_SOURCE is None:
            self.container_widgets["microphone_main_vbox"].set_sensitive(False)
        else:
            if not self.scale_widgets["balance"].get_sensitive():
                self.scale_widgets["balance"].set_sensitive(True)
            if not self.container_widgets["speaker_main_vbox"].get_sensitive():
                self.container_widgets["speaker_main_vbox"].set_sensitive(True)
        output_list = []
        output_selected_row = -1
        out_index = 0
        for cards in settings.PA_CARDS:
            for sink in settings.PA_CARDS[cards]["sink"]:
                if sink.object_path == settings.CURRENT_SINK:
                    output_selected_row = out_index
                prop = settings.get_object_property_list(sink)
                if prop:
                    output_list.append(TreeItem(self.image_widgets["device"], prop["device.description"], sink.object_path))
                    out_index + 1
        self.view_widgets["ad_output"].add_items(output_list, clear_first=True)
        if not (output_selected_row < 0):
            self.view_widgets["ad_output"].set_select_rows([output_selected_row])
    
    # default device changed
    def fallback_sink_updated_cb(self, core, sink):
        print 'fallback sink updated', sink
        if not self.scale_widgets["balance"].get_sensitive():
            self.scale_widgets["balance"].set_sensitive(True)
        if not self.container_widgets["speaker_main_vbox"].get_sensitive():
            self.container_widgets["speaker_main_vbox"].set_sensitive(True)
        settings.CURRENT_SINK = sink
        # disconnect old object signals
        if self.current_sink:
            try:
                self.current_sink.disconnect_by_func(self.speaker_volume_updated)
                self.current_sink.disconnect_by_func(self.pulse_mute_updated)
                self.current_sink.disconnect_by_func(self.pulse_active_port_updated)
            except:
                traceback.print_exc()
        # connect new object signals
        self.speaker_ports = None
        if settings.CURRENT_SINK:
            self.speaker_ports = settings.get_port_list(settings.CURRENT_SINK)
            self.current_sink = sink = settings.PA_DEVICE[settings.CURRENT_SINK]
            sink.connect("volume-updated", self.speaker_volume_updated)
            sink.connect("mute-updated", self.pulse_mute_updated, self.button_widgets["speaker"])
            sink.connect("active-port-updated", self.pulse_active_port_updated,
                         self.button_widgets["speaker_combo"], self.speaker_ports)
        if settings.PA_CHANNELS[settings.CURRENT_SINK]['channel_num'] == 1:
            self.scale_widgets["balance"].set_sensitive(False)
        else:
            volumes = settings.get_volumes(settings.CURRENT_SINK)
            if volumes[0] == volumes[1]:
                value = 0
            elif volumes[0] > volumes[1]:     # if left
                value = float(volumes[1]) / volumes[0] - 1
            else:
                value = 1 - float(volumes[0]) / volumes[1]
            self.adjust_widgets["balance"].set_value(value)
        self.button_widgets["balance"].set_active(True)
        self.button_widgets["speaker"].set_active(not settings.get_mute(settings.CURRENT_SINK))
        if self.speaker_ports:
            items = []
            i = 0
            select_index = self.speaker_ports[1]
            for port in self.speaker_ports[0]:
                items.append((port.get_description(), i))
                i += 1
            self.button_widgets["speaker_combo"].set_items(items, select_index, 460)
        self.adjust_widgets["speaker"].set_value(
            settings.get_volume(settings.CURRENT_SINK) * 100.0 / settings.FULL_VOLUME_VALUE)
        for item in self.view_widgets["ad_output"].visible_items:
            if item.obj_path == sink.object_path:
                self.view_widgets["ad_output"].select_items([item])
                break
        
    def fallback_source_udpated_cb(self, core, source):
        print 'fallback source updated', source
        if not self.container_widgets["microphone_main_vbox"].get_sensitive():
            self.container_widgets["microphone_main_vbox"].set_sensitive(True)
        settings.CURRENT_SOURCE = source
        # disconnect old object signals
        if self.current_source:
            try:
                self.current_source.disconnect_by_func(self.microphone_volume_updated)
                self.current_source.disconnect_by_func(self.pulse_mute_updated)
                self.current_source.disconnect_by_func(self.pulse_active_port_updated)
            except:
                traceback.print_exc()
        # connect new object signals
        self.microphone_ports = None
        if settings.CURRENT_SOURCE:
            self.microphone_ports = settings.get_port_list(settings.CURRENT_SOURCE)
            self.current_source = source = settings.PA_DEVICE[settings.CURRENT_SOURCE]
            source.connect("volume-updated", self.microphone_volume_updated)
            source.connect("mute-updated", self.pulse_mute_updated, self.button_widgets["microphone"])
            source.connect("active-port-updated", self.pulse_active_port_updated,
                           self.button_widgets["microphone_combo"], self.microphone_ports)
        self.button_widgets["microphone"].set_active(not settings.get_mute(settings.CURRENT_SOURCE))
        if self.microphone_ports:
            items = []
            select_index = self.microphone_ports[1]
            i = 0
            for port in self.microphone_ports[0]:
                items.append((port.get_description(), i))
                i += 1
            self.button_widgets["microphone_combo"].set_items(items, select_index, 460)
        self.adjust_widgets["microphone"].set_value(
            settings.get_volume(settings.CURRENT_SOURCE) * 100.0 / settings.FULL_VOLUME_VALUE)
        for item in self.view_widgets["ad_input"].visible_items:
            if item.obj_path == source.object_path:
                self.view_widgets["ad_input"].select_items([item])
                break
        
    def fallback_sink_unset_cb(self, core):
        print 'fallback sink unset'
        self.container_widgets["speaker_main_vbox"].set_sensitive(False)
        
    def fallback_source_unset_cb(self, core):
        print 'fallback source unset'
        self.container_widgets["microphone_main_vbox"].set_sensitive(False)
    
    # signals callback end
    ######################################
    def __make_align(self, widget=None, xalign=0.0, yalign=0.5, xscale=1.0,
                     yscale=0.0, padding_top=0, padding_bottom=0, padding_left=0,
                     padding_right=0, height=CONTAINNER_HEIGHT):
        align = gtk.Alignment()
        align.set_size_request(-1, height)
        align.set(xalign, yalign, xscale, yscale)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        if widget:
            align.add(widget)
        return align
    
    def slider_to_advanced(self, button):
        self.container_widgets["slider"].slide_to_page(
            self.alignment_widgets["advance_set_tab_box"], "right")
        #self.container_widgets["slider"].slide_to_page(
            #self.container_widgets["advance_set_tab_box"], "right")
        self.module_frame.send_submodule_crumb(2, _("Advanced"))
    
    def set_to_default(self):
        '''set to the default'''
        pass
    
if __name__ == '__main__':
    gtk.gdk.threads_init()
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    mouse_settings = SoundSetting(module_frame)
    
    module_frame.add(mouse_settings.alignment_widgets["slider"])
    module_frame.connect("realize", 
        lambda w: mouse_settings.container_widgets["slider"].set_to_page(
        mouse_settings.alignment_widgets["main_hbox"]))
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "click_crumb":
            (crumb_index, crumb_label) = message_content
            if crumb_index == 1:
                mouse_settings.container_widgets["slider"].slide_to_page(
                    mouse_settings.alignment_widgets["main_hbox"], "left")
                #mouse_settings.container_widgets["slider"].slide_to_page(
                    #mouse_settings.container_widgets["main_hbox"], "left")
        elif message_type == "show_again":
            mouse_settings.container_widgets["slider"].set_to_page(
                mouse_settings.alignment_widgets["main_hbox"])
            module_frame.send_module_info()

    module_frame.module_message_handler = message_handler        
    
    module_frame.run()
