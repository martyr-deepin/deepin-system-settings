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

import sys
import os
from deepin_utils.file import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from theme import app_theme

from dtk.ui.label import Label
from dtk.ui.button import Button, OffButton
from dtk.ui.tab_window import TabBox
from dtk.ui.new_slider import HSlider
from dtk.ui.line import HSeparator
from dtk.ui.combo import ComboBox
from dtk.ui.box import ImageBox
from dtk.ui.new_scalebar import HScalebar
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.utils import cairo_disable_antialias, color_hex_to_cairo
from treeitem import MyTreeItem as TreeItem
from treeitem import MyTreeView as TreeView
from statusbar import StatusBar
from scalebar import MyHScalebar
from nls import _
import gtk
#import settings
import pypulse

from module_frame import ModuleFrame
from constant import *
import threading as td
import traceback

MODULE_NAME = "sound"
MUTE_TEXT_COLOR = "#DCDCDC"

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

        self.__is_first_show = True

        self.__create_widget()
        self.__adjust_widget()
        self.__signals_connect()

    def __create_widget(self):
        '''create gtk widget'''
        title_item_font_size = TITLE_FONT_SIZE
        option_item_font_szie = CONTENT_FONT_SIZE

        self.label_widgets["speaker"] = Label(_("Speaker"), app_theme.get_color("globalTitleForeground"), text_size=title_item_font_size, enable_select=False, enable_double_click=False)
        self.label_widgets["microphone"] = Label(_("Microphone"), app_theme.get_color("globalTitleForeground"), text_size=title_item_font_size, enable_select=False, enable_double_click=False)
        self.label_widgets["left"] = Label(_("Left"), enable_select=False, enable_double_click=False)
        self.label_widgets["right"] = Label(_("Right"), enable_select=False, enable_double_click=False)
        self.label_widgets["speaker_port"] = Label(_("Output Port"), text_size=option_item_font_szie, enable_select=False, enable_double_click=False)
        self.label_widgets["speaker_volume"] = Label(_("Output Volume"), text_size=option_item_font_szie, enable_select=False, enable_double_click=False)
        self.label_widgets["speaker_mute"] = Label(_("Mute"), text_size=option_item_font_szie, enable_select=False, enable_double_click=False)
        self.label_widgets["speaker_balance"] = Label(_("Balance"), text_size=option_item_font_szie, enable_select=False, enable_double_click=False)
        self.label_widgets["microphone_port"] = Label(_("Input Port"), text_size=option_item_font_szie, enable_select=False, enable_double_click=False)
        self.label_widgets["microphone_volume"] = Label(_("Input Volume"), text_size=option_item_font_szie, enable_select=False, enable_double_click=False)
        self.label_widgets["microphone_mute"] = Label(_("Mute"), text_size=option_item_font_szie, enable_select=False, enable_double_click=False)
        #####################################
        # image init
        self.image_widgets["balance"] = ImageBox(app_theme.get_pixbuf("%s/balance.png" % MODULE_NAME))
        self.image_widgets["speaker"] = ImageBox(app_theme.get_pixbuf("%s/speaker-3.png" % MODULE_NAME))
        self.image_widgets["microphone"] = ImageBox(app_theme.get_pixbuf("%s/microphone.png" % MODULE_NAME))
        self.image_widgets["device"] = app_theme.get_pixbuf("%s/device.png" % MODULE_NAME)
        # button init
        self.button_widgets["balance"] = OffButton()
        self.button_widgets["speaker"] = OffButton()
        self.button_widgets["microphone"] = OffButton()
        self.button_widgets["advanced"] = Button(_("Advanced"))
        self.button_widgets["speaker_combo"] = ComboBox(max_width=HSCALEBAR_WIDTH-5)
        self.button_widgets["microphone_combo"] = ComboBox(max_width=HSCALEBAR_WIDTH-5)
        # container init
        self.container_widgets["main_vbox"] = gtk.VBox(False)
        self.container_widgets["statusbar"] = StatusBar()
        self.container_widgets["slider"] = HSlider()
        self.container_widgets["swin"] = ScrolledWindow()
        self.container_widgets["advance_set_tab_box"] = TabBox()
        self.container_widgets["advance_set_tab_box"].draw_title_background = self.draw_tab_title_background
        self.container_widgets["main_hbox"] = gtk.HBox(False)
        self.container_widgets["left_vbox"] = gtk.VBox(False)
        self.container_widgets["right_vbox"] = gtk.VBox(False)
        self.container_widgets["balance_hbox"] = gtk.HBox(False)
        self.container_widgets["speaker_main_vbox"] = gtk.VBox(False)     # speaker
        self.container_widgets["speaker_label_hbox"] = gtk.HBox(False)
        self.container_widgets["speaker_table"] = gtk.Table(4, 2)
        self.container_widgets["microphone_main_vbox"] = gtk.VBox(False)     # microphone
        self.container_widgets["microphone_label_hbox"] = gtk.HBox(False)
        self.container_widgets["microphone_table"] = gtk.Table(4, 2)
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
        # adjust init
        volume_max_percent = pypulse.MAX_VOLUME_VALUE * 100 / pypulse.NORMAL_VOLUME_VALUE
        self.adjust_widgets["balance"] = gtk.Adjustment(0, -1.0, 1.0, 0.1, 0.2)
        self.adjust_widgets["speaker"] = gtk.Adjustment(0, 0, volume_max_percent, 1, 5)
        self.adjust_widgets["microphone"] = gtk.Adjustment(0, 0, volume_max_percent, 1, 5)
        # scale init
        #self.scale_widgets["balance"] = MyHScalebar(value_min=-1, value_max=1)
        self.scale_widgets["balance"] = HScalebar(value_min=-1, value_max=1, gray_progress=True)
        self.scale_widgets["speaker"] = HScalebar(show_value=True, format_value="%", value_min=0, value_max=volume_max_percent)
        self.scale_widgets["microphone"] = HScalebar(show_value=True, format_value="%", value_min=0, value_max=volume_max_percent)
        ###################################
        # advance set
        self.container_widgets["advance_input_box"] = gtk.VBox(False)
        self.container_widgets["advance_output_box"] = gtk.VBox(False)
        self.container_widgets["advance_hardware_box"] = gtk.VBox(False)
        self.alignment_widgets["advance_input_box"] = gtk.Alignment()
        self.alignment_widgets["advance_output_box"] = gtk.Alignment()
        self.alignment_widgets["advance_hardware_box"] = gtk.Alignment()
        #
        self.label_widgets["ad_output"] = Label(_("Choose a device for sound output:"), enable_select=False, enable_double_click=False)
        self.label_widgets["ad_input"] = Label(_("Choose a device for sound input:"), enable_select=False, enable_double_click=False)
        self.label_widgets["ad_hardware"] = Label(_("Choose a device to configure:"), enable_select=False, enable_double_click=False)
        #
        self.container_widgets["ad_output"] = gtk.VBox(False)
        self.container_widgets["ad_input"] = gtk.VBox(False)
        self.container_widgets["ad_hardware"] = gtk.VBox(False)
        #
        self.view_widgets["ad_output"] = TreeView()
        self.view_widgets["ad_input"] = TreeView()
        self.view_widgets["ad_hardware"] = TreeView()

    def draw_tab_title_background(self, cr, widget):
        rect = widget.allocation
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(0, 0, rect.width, rect.height - 1)
        cr.fill()

    def __adjust_widget(self):
        ''' adjust widget '''
        MID_SPACING = 10
        RIGHT_BOX_WIDTH = TIP_BOX_WIDTH - 20
        MAIN_AREA_WIDTH = 440
        OPTION_LEFT_PADDING = WIDGET_SPACING + 16
        self.container_widgets["main_vbox"].pack_start(self.alignment_widgets["slider"])
        self.container_widgets["main_vbox"].pack_start(self.container_widgets["statusbar"], False, False)
        self.alignment_widgets["slider"].add(self.container_widgets["slider"])
        self.alignment_widgets["slider"].set(0, 0, 1, 1)
        self.container_widgets["slider"].append_page(self.alignment_widgets["main_hbox"])
        self.container_widgets["slider"].append_page(self.alignment_widgets["advance_set_tab_box"])
        self.alignment_widgets["main_hbox"].add(self.container_widgets["main_hbox"])
        self.alignment_widgets["advance_set_tab_box"].add(self.container_widgets["advance_set_tab_box"])
        self.container_widgets["advance_set_tab_box"].set_size_request(WINDOW_WIDTH, -1)
        self.alignment_widgets["main_hbox"].set_padding(
            TEXT_WINDOW_TOP_PADDING, 0, 0, TEXT_WINDOW_RIGHT_WIDGET_PADDING)
        self.alignment_widgets["advance_set_tab_box"].set_padding(
            FRAME_TOP_PADDING, 0, 0, 0)

        self.container_widgets["advance_set_tab_box"].add_items(
            [(_("Input"), self.alignment_widgets["advance_input_box"]),
             (_("Output"), self.alignment_widgets["advance_output_box"])])
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
        # set right padding
        self.alignment_widgets["right"].set(0.0, 0.0, 1.0, 1.0)
        self.alignment_widgets["right"].set_padding(0, 0, 0, 60)

        self.container_widgets["left_vbox"].set_spacing(BETWEEN_SPACING)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["speaker_main_vbox"], False, False)
        self.container_widgets["left_vbox"].pack_start(
            self.container_widgets["microphone_main_vbox"], False, False)

        # speaker
        self.alignment_widgets["speaker_label"].add(self.container_widgets["speaker_label_hbox"])
        self.alignment_widgets["speaker_set"].add(self.container_widgets["speaker_table"])
        #
        self.alignment_widgets["speaker_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["speaker_label"].set_padding(0, 0, TEXT_WINDOW_LEFT_PADDING, 0)
        #self.alignment_widgets["speaker_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        #self.alignment_widgets["speaker_set"].set(0.0, 0.0, 0.0, 0.0)
        #self.alignment_widgets["speaker_set"].set_padding(0, 0, OPTION_LEFT_PADDING, 0)
        self.container_widgets["speaker_main_vbox"].pack_start(
            self.alignment_widgets["speaker_label"])
        self.container_widgets["speaker_main_vbox"].pack_start(
            self.__setup_separator())
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
        self.scale_widgets["speaker"].add_mark(self.adjust_widgets["speaker"].get_lower(), gtk.POS_BOTTOM, "-")
        self.scale_widgets["speaker"].add_mark(self.adjust_widgets["speaker"].get_upper(), gtk.POS_BOTTOM, "+")
        #self.scale_widgets["speaker"].add_mark(100, gtk.POS_BOTTOM, "100%")
        #
        #self.container_widgets["speaker_table"].set_size_request(HSCALEBAR_WIDTH, -1)
        self.container_widgets["speaker_table"].set_col_spacings(WIDGET_SPACING)
        speaker_port_align = self.__make_align(self.label_widgets["speaker_port"])
        speaker_port_align.set_size_request(STANDARD_LINE, CONTAINNER_HEIGHT)
        self.container_widgets["speaker_table"].attach(
            speaker_port_align, 0, 1, 0, 1, 4)
        self.container_widgets["speaker_table"].attach(
            self.__make_align(self.button_widgets["speaker_combo"]), 1, 2, 0, 1, 4)
        speaker_mute_align = self.__make_align(self.label_widgets["speaker_mute"])
        speaker_mute_align.set_size_request(STANDARD_LINE, CONTAINNER_HEIGHT)
        self.container_widgets["speaker_table"].attach(
            speaker_mute_align, 0, 1, 1, 2, 4)
        self.container_widgets["speaker_table"].attach(
            self.__make_align(self.button_widgets["speaker"]), 1, 2, 1, 2, 4)
        speaker_volume_align = self.__make_align(self.label_widgets["speaker_volume"])
        self.container_widgets["speaker_table"].attach(
            speaker_volume_align, 0, 1, 2, 3, 4)
        self.container_widgets["speaker_table"].attach(
            self.__make_align(self.scale_widgets["speaker"], yalign=0.0, yscale=1.0, height=43), 1, 2, 2, 3, 4)
        speaker_balance_align = self.__make_align(self.label_widgets["speaker_balance"])
        self.container_widgets["speaker_table"].attach(
            speaker_balance_align, 0, 1, 3, 4, 4)
        self.container_widgets["speaker_table"].attach(
            self.__make_align(self.scale_widgets["balance"], yalign=0.0, yscale=1.0, height=43), 1, 2, 3, 4, 4)
        self.button_widgets["speaker_combo"].set_size_request(HSCALEBAR_WIDTH, WIDGET_HEIGHT)
        self.scale_widgets["speaker"].set_size_request(HSCALEBAR_WIDTH, -1)
        self.scale_widgets["balance"].set_size_request(HSCALEBAR_WIDTH, -1)

        # microphone
        self.alignment_widgets["microphone_label"].add(self.container_widgets["microphone_label_hbox"])
        self.alignment_widgets["microphone_set"].add(self.container_widgets["microphone_table"])
        self.alignment_widgets["microphone_label"].set(0.0, 0.5, 1.0, 0.0)
        self.alignment_widgets["microphone_label"].set_padding(0, 0, TEXT_WINDOW_LEFT_PADDING, 0)
        #self.alignment_widgets["microphone_label"].set_size_request(-1, CONTAINNER_HEIGHT)
        #self.alignment_widgets["microphone_set"].set(0.0, 0.0, 0.0, 0.0)
        #self.alignment_widgets["microphone_set"].set_padding(0, 0, OPTION_LEFT_PADDING, 0)
        self.container_widgets["microphone_main_vbox"].pack_start(
            self.alignment_widgets["microphone_label"])
        self.container_widgets["microphone_main_vbox"].pack_start(
            self.__setup_separator())
        self.container_widgets["microphone_main_vbox"].pack_start(
            self.alignment_widgets["microphone_set"])
        # tips lable
        self.container_widgets["microphone_label_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["microphone_label_hbox"].pack_start(
            self.image_widgets["microphone"], False, False)
        self.container_widgets["microphone_label_hbox"].pack_start(
            self.label_widgets["microphone"], False, False)
        #
        self.scale_widgets["microphone"].add_mark(self.adjust_widgets["microphone"].get_lower(), gtk.POS_BOTTOM, "-")
        self.scale_widgets["microphone"].add_mark(self.adjust_widgets["microphone"].get_upper(), gtk.POS_BOTTOM, "+")
        #self.scale_widgets["microphone"].add_mark(100, gtk.POS_BOTTOM, "100%")

        #self.container_widgets["microphone_table"].set_size_request(HSCALEBAR_WIDTH, -1)
        self.container_widgets["microphone_table"].set_col_spacings(WIDGET_SPACING)
        microphone_port_align = self.__make_align(self.label_widgets["microphone_port"])
        microphone_port_align.set_size_request(STANDARD_LINE, CONTAINNER_HEIGHT)
        self.container_widgets["microphone_table"].attach(
            microphone_port_align, 0, 1, 0, 1, 4)
        self.container_widgets["microphone_table"].attach(
            self.__make_align(self.button_widgets["microphone_combo"]), 1, 2, 0, 1, 4)
        microphone_mute_align = self.__make_align(self.label_widgets["microphone_mute"])
        microphone_mute_align.set_size_request(STANDARD_LINE, CONTAINNER_HEIGHT)
        self.container_widgets["microphone_table"].attach(
            microphone_mute_align, 0, 1, 1, 2, 4)
        self.container_widgets["microphone_table"].attach(
            self.__make_align(self.button_widgets["microphone"]), 1, 2, 1, 2, 4)
        microphone_volume_align = self.__make_align(self.label_widgets["microphone_volume"])
        microphone_volume_align.set_size_request(STANDARD_LINE, CONTAINNER_HEIGHT)
        self.container_widgets["microphone_table"].attach(
            microphone_volume_align, 0, 1, 2, 3, 4)
        self.container_widgets["microphone_table"].attach(
            self.__make_align(self.scale_widgets["microphone"], yalign=0.0, yscale=1.0, height=43), 1, 2, 2, 3, 4)
        self.container_widgets["microphone_table"].attach(
            self.__make_align(self.button_widgets["advanced"]), 0, 2, 3, 4, 4, ypadding=15)
        self.button_widgets["microphone_combo"].set_size_request(HSCALEBAR_WIDTH, WIDGET_HEIGHT)
        self.scale_widgets["microphone"].set_size_request(HSCALEBAR_WIDTH, -1)

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
        ##########################################
        self.view_widgets["ad_input"].set_expand_column(0)
        self.view_widgets["ad_output"].set_expand_column(0)
        self.view_widgets["ad_hardware"].set_expand_column(0)
        self.__set_output_status()
        self.__set_input_status()

        self.__set_output_port_status()
        self.__set_input_port_status()

        self.__set_card_treeview_status()
        self.__set_output_treeview_status()
        self.__set_input_treeview_status()
        # set output volume
        self.speaker_ports = None
        # set input volume
        self.microphone_ports = None

    def __signals_connect(self):
        ''' widget signals connect'''
        # redraw container background white
        self.container_widgets["slider"].connect("completed_slide", self.slider_completed_slide_cb)
        self.alignment_widgets["main_hbox"].connect("expose-event", self.container_expose_cb)
        self.alignment_widgets["advance_output_box"].connect("expose-event", self.container_expose_cb)
        self.alignment_widgets["advance_input_box"].connect("expose-event", self.container_expose_cb)

        self.button_widgets["speaker"].connect("toggled", self.speaker_toggled_cb)
        self.button_widgets["microphone"].connect("toggled", self.microphone_toggled_cb)

        self.scale_widgets["balance"].connect("value-changed", self.speaker_value_changed_cb)
        self.scale_widgets["speaker"].connect("value-changed", self.speaker_value_changed_cb)
        self.scale_widgets["microphone"].connect("value-changed", self.microphone_value_changed_cb)

        self.button_widgets["speaker_combo"].connect("item-selected", self.speaker_port_changed)
        self.button_widgets["microphone_combo"].connect("item-selected", self.microphone_port_changed)

        self.button_widgets["advanced"].connect("clicked", self.slider_to_advanced)
        self.view_widgets["ad_output"].connect("single-click-item", self.output_treeview_clicked)
        self.view_widgets["ad_input"].connect("single-click-item", self.input_treeview_clicked)
        self.view_widgets["ad_hardware"].connect("single-click-item", self.card_treeview_clicked)
        self.container_widgets["advance_input_box"].connect("expose-event", self.treeview_container_expose_cb, self.view_widgets["ad_input"])
        self.container_widgets["advance_output_box"].connect("expose-event", self.treeview_container_expose_cb, self.view_widgets["ad_output"])
        self.container_widgets["advance_hardware_box"].connect("expose-event", self.treeview_container_expose_cb, self.view_widgets["ad_hardware"])
        #######################
        # pulseaudio signals
        pypulse.PULSE.connect("sink-new", self.pa_sink_new_cb)
        pypulse.PULSE.connect("sink-changed", self.pa_sink_changed_cb)
        pypulse.PULSE.connect("sink-removed", self.pa_sink_removed_cb)

        pypulse.PULSE.connect("source-new", self.pa_source_new_cb)
        pypulse.PULSE.connect("source-changed", self.pa_source_changed_cb)
        pypulse.PULSE.connect("source-removed", self.pa_source_removed_cb)

        pypulse.PULSE.connect("card-new", self.pa_card_new_cb)
        pypulse.PULSE.connect("card-changed", self.pa_card_changed_cb)
        pypulse.PULSE.connect("card-removed", self.pa_card_removed_cb)

        pypulse.PULSE.connect("server-changed", self.pa_server_changed_cb)

    ######################################
    # signals callback begin
    # widget signals
    def slider_completed_slide_cb(self, widget):
        if self.__is_first_show:
            self.__is_first_show = False
            widget.set_to_page(self.alignment_widgets["main_hbox"])

    def container_expose_cb(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h, d = widget.window.get_geometry()
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))
        cr.rectangle(x, y, w, h)
        cr.fill()

    def speaker_toggled_cb(self, button):
        active = button.get_active()
        current_sink = pypulse.get_fallback_sink_index()
        self.scale_widgets["speaker"].set_enable(active)
        if current_sink is not None:
            pypulse.PULSE.set_output_mute(current_sink, not active)
        if not active:
            self.label_widgets["speaker_volume"].set_text("<span foreground=\"%s\">%s</span>" % (MUTE_TEXT_COLOR, _("Output Volume")))
            self.label_widgets["speaker_balance"].set_text("<span foreground=\"%s\">%s</span>" % (MUTE_TEXT_COLOR, _("Balance")))
            self.set_status_text(_("Muted output"))
        else:
            self.label_widgets["speaker_volume"].set_text("%s" % _("Output Volume"))
            self.label_widgets["speaker_balance"].set_text("%s" % _("Balance"))
            self.set_status_text(_("Unmuted output"))

    def microphone_toggled_cb(self, button):
        active = button.get_active()
        current_source = pypulse.get_fallback_source_index()
        self.scale_widgets["microphone"].set_enable(active)
        if current_source is not None:
            pypulse.PULSE.set_input_mute(current_source, not active)
        if not active:
            self.label_widgets["microphone_volume"].set_text("<span foreground=\"%s\">%s</span>" % (MUTE_TEXT_COLOR, _("Input Volume")))
            self.set_status_text(_("Muted input"))
        else:
            self.label_widgets["microphone_volume"].set_text("%s" % _("Input Volume"))
            self.set_status_text(_("Unmuted input"))

    def speaker_value_changed_cb(self, widget, value):
        ''' speaker hscale value changed callback thread'''
        if not self.button_widgets["speaker"].get_active():
            self.button_widgets["speaker"].set_active(True)
        current_sink = pypulse.get_fallback_sink_index()
        if current_sink is None:
            return
        balance = self.scale_widgets["balance"].get_value()
        volume = int((self.scale_widgets["speaker"].get_value()) / 100.0 * pypulse.NORMAL_VOLUME_VALUE)
        pypulse.PULSE.set_output_volume_with_balance(current_sink, volume, balance)

    def microphone_value_changed_cb(self, widget, value):
        if not self.button_widgets["microphone"].get_active():
            self.button_widgets["microphone"].set_active(True)
        current_source = pypulse.get_fallback_source_index()
        if current_source is None:
            return
        channel_list = pypulse.PULSE.get_input_channels_by_index(current_source)
        if not channel_list:
            return
        volume = int((value) / 100.0 * pypulse.NORMAL_VOLUME_VALUE)
        pypulse.PULSE.set_input_volume(current_source, [volume] * channel_list['channels'])

    def speaker_port_changed(self, combo, content, value, index):
        current_sink = pypulse.get_fallback_sink_index()
        if current_sink is None:
            return
        if value in self.__current_sink_ports:
            port = self.__current_sink_ports[value][0]
            pypulse.PULSE.set_output_active_port(current_sink, port)
            self.set_status_text(_("Set output port to %s") % content)

    def microphone_port_changed(self, combo, content, value, index):
        current_source = pypulse.get_fallback_source_index()
        if current_source is None:
            return
        if value in self.__current_source_ports:
            port = self.__current_source_ports[value][0]
            pypulse.PULSE.set_input_active_port(current_source, port)
            self.set_status_text(_("Set input port to %s") % content)

    def treeview_container_expose_cb(self, widget, event, treeview):
        rect = treeview.allocation
        cr = widget.window.cairo_create()
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
            cr.set_line_width(1)
            cr.rectangle(rect.x, rect.y, rect.width+1, rect.height+1)
            cr.stroke()

    def output_treeview_clicked(self, tree_view, item, row, *args):
        if item.device_index == pypulse.get_fallback_sink_index():
            return
        pypulse.PULSE.set_fallback_sink(item.device_name)
        self.set_status_text(_("Output device %s selected") % item.content)

    def input_treeview_clicked(self, tree_view, item, row, *args):
        if item.device_index == pypulse.get_fallback_source_index():
            return
        pypulse.PULSE.set_fallback_source(item.device_name)
        self.set_status_text(_("Input device %s selected") % item.content)

    def card_treeview_clicked(self, tree_view, item, row, *args):
        print "treeview clicked", item.device_name, item.device_index, item.content, row

    #########################
    # pulseaudio signals
    def pa_sink_new_cb(self, obj, index):
        obj.get_devices()
        self.__set_output_treeview_status()

    def pa_sink_changed_cb(self, obj, index):
        obj.get_devices()
        current_sink = pypulse.get_fallback_sink_index()
        if current_sink is None or current_sink != index:
            return
        self.__set_output_status()
        self.__set_output_port_status()

    def pa_sink_removed_cb(self, obj, index):
        obj.get_devices()
        self.__set_output_treeview_status()

    def pa_source_new_cb(self, obj, index):
        obj.get_devices()
        self.__set_input_treeview_status()

    def pa_source_changed_cb(self, obj, index):
        obj.get_devices()
        current_source = pypulse.get_fallback_source_index()
        if current_source is None or current_source != index:
            return
        self.__set_input_status()
        self.__set_input_port_status()

    def pa_source_removed_cb(self, obj, index):
        obj.get_devices()
        self.__set_input_treeview_status()

    def pa_card_new_cb(self, obj, index):
        obj.get_devices()
        self.__set_card_treeview_status()

    def pa_card_changed_cb(self, obj, index):
        obj.get_devices()
        self.__set_card_treeview_status()

    def pa_card_removed_cb(self, obj, index):
        obj.get_devices()
        self.__set_card_treeview_status()

    def pa_server_changed_cb(self, obj):
        obj.get_devices()
        self.__set_output_status()
        self.__set_output_port_status()
        current_sink = pypulse.get_fallback_sink_index()
        if current_sink is not None:
            for item in self.view_widgets["ad_output"].get_items():
                if item.device_index == current_sink:
                    self.view_widgets["ad_output"].select_items([item])
                    break
        self.__set_input_status()
        self.__set_input_port_status()
        current_source = pypulse.get_fallback_source_index()
        if current_source is not None:
            for item in self.view_widgets["ad_input"].get_items():
                if item.device_index == current_source:
                    self.view_widgets["ad_input"].select_items([item])
                    break

    # signals callback end
    ######################################
    def __make_align(self, widget=None, xalign=1.0, yalign=0.5, xscale=0.0,
                     yscale=0.0, padding_top=0, padding_bottom=0, padding_left=0,
                     padding_right=0, height=CONTAINNER_HEIGHT):
        align = gtk.Alignment()
        align.set_size_request(-1, height)
        align.set(xalign, yalign, xscale, yscale)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        if widget:
            align.add(widget)
        return align

    def __make_separator(self):
        hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        hseparator.set_size_request(450, 10)
        return hseparator

    def __setup_separator(self):
        return self.__make_align(self.__make_separator(), xalign=0.0, xscale=0.0,
                                 padding_top=10,# padding_bottom=10,
                                 padding_left=TEXT_WINDOW_LEFT_PADDING, height=-1)

    def slider_to_advanced(self, button):
        self.container_widgets["slider"].slide_to_page(
            self.alignment_widgets["advance_set_tab_box"], "right")
        #self.container_widgets["slider"].slide_to_page(
            #self.container_widgets["advance_set_tab_box"], "right")
        self.module_frame.send_submodule_crumb(2, _("Advanced"))

    def __set_output_status(self):
        # if sinks list is empty, then can't set output volume
        current_sink = pypulse.get_fallback_sink_index()
        sinks = pypulse.PULSE.get_output_devices()
        if current_sink is None:
            self.label_widgets["speaker_port"].set_sensitive(False)
            self.label_widgets["speaker_mute"].set_sensitive(False)
            self.label_widgets["speaker_volume"].set_sensitive(False)
            self.label_widgets["speaker_balance"].set_sensitive(False)

            self.button_widgets["speaker_combo"].set_sensitive(False)
            self.button_widgets["speaker"].set_sensitive(False)
            self.scale_widgets["speaker"].set_sensitive(False)
            self.scale_widgets["balance"].set_sensitive(False)

            self.button_widgets["speaker"].set_active(False)
            self.scale_widgets["speaker"].set_enable(False)
            self.scale_widgets["balance"].set_enable(False)
        # set output volume
        elif current_sink in sinks:
            self.label_widgets["speaker_port"].set_sensitive(True)
            self.label_widgets["speaker_mute"].set_sensitive(True)
            self.label_widgets["speaker_volume"].set_sensitive(True)
            self.label_widgets["speaker_balance"].set_sensitive(True)

            self.button_widgets["speaker_combo"].set_sensitive(True)
            self.button_widgets["speaker"].set_sensitive(True)
            self.scale_widgets["speaker"].set_sensitive(True)
            self.scale_widgets["balance"].set_sensitive(True)

            is_mute = sinks[current_sink]['mute']
            self.button_widgets["speaker"].set_active(not is_mute)
            self.scale_widgets["speaker"].set_enable(not is_mute)
            self.scale_widgets["balance"].set_enable(not is_mute)

            sink_volume = pypulse.PULSE.get_output_volume()
            sink_channel = pypulse.PULSE.get_output_channels_by_index(current_sink)
            balance = None
            if current_sink in sink_volume:
                volume = max(sink_volume[current_sink])
                if sink_channel and sink_channel['can_balance']:
                    balance = pypulse.get_volume_balance(sink_channel['channels'],
                                                         sink_volume[current_sink],
                                                         sink_channel['map'])
                if balance is None:
                    balance = 0
            else:
                volume = 0
                balance = 0
            self.scale_widgets["speaker"].set_value(volume * 100.0 / pypulse.NORMAL_VOLUME_VALUE)
            self.scale_widgets["balance"].set_value(balance)

    def __set_input_status(self):
        # if sources list is empty, then can't set input volume
        current_source = pypulse.get_fallback_source_index()
        sources = pypulse.PULSE.get_input_devices()
        if current_source is None:
            self.label_widgets["microphone_port"].set_sensitive(False)
            self.label_widgets["microphone_mute"].set_sensitive(False)
            self.label_widgets["microphone_volume"].set_sensitive(False)

            self.button_widgets["microphone_combo"].set_sensitive(False)
            self.button_widgets["microphone"].set_sensitive(False)
            self.scale_widgets["microphone"].set_sensitive(False)

            self.button_widgets["microphone"].set_active(False)
            self.scale_widgets["microphone"].set_enable(False)
        # set input volume
        elif current_source in sources:
            self.label_widgets["microphone_port"].set_sensitive(True)
            self.label_widgets["microphone_mute"].set_sensitive(True)
            self.label_widgets["microphone_volume"].set_sensitive(True)

            self.button_widgets["microphone_combo"].set_sensitive(True)
            self.button_widgets["microphone"].set_sensitive(True)
            self.scale_widgets["microphone"].set_sensitive(True)

            is_mute = sources[current_source]['mute']
            self.button_widgets["microphone"].set_active(not is_mute)
            self.scale_widgets["microphone"].set_enable(not is_mute)
            source_volume = pypulse.PULSE.get_input_volume()
            if current_source in source_volume:
                volume = max(source_volume[current_source])
            else:
                volume = 0
            self.scale_widgets["microphone"].set_value(volume * 100.0 / pypulse.NORMAL_VOLUME_VALUE)

    def __set_output_port_status(self):
        current_sink = pypulse.get_fallback_sink_index()
        sinks = pypulse.PULSE.get_output_devices()
        self.__current_sink_ports= {}
        if current_sink is None:
            return
        elif current_sink in sinks:
            ports = sinks[current_sink]['ports']
            active_port = pypulse.PULSE.get_output_active_ports_by_index(current_sink)
            if active_port is None:
                select_index = 0
            i = 0
            items = []
            for p in ports:
                self.__current_sink_ports[i] = (p[0], p[1])
                items.append((p[1], i))
                if active_port and active_port[0] == p[0]:
                    select_index = i
                i += 1
            if not items:
                items.append((" ", 0))
            self.button_widgets["speaker_combo"].add_items(items, select_index)

    def __set_input_port_status(self):
        current_source = pypulse.get_fallback_source_index()
        sources = pypulse.PULSE.get_input_devices()
        self.__current_source_ports= {}
        if current_source is None:
            return
        elif current_source in sources:
            ports = sources[current_source]['ports']
            active_port = pypulse.PULSE.get_input_active_ports_by_index(current_source)
            if active_port is None:
                select_index = 0
            i = 0
            items = []
            for p in ports:
                self.__current_source_ports[i] = (p[0], p[1])
                items.append((p[1], i))
                if active_port and active_port[0] == p[0]:
                    select_index = i
                i += 1
            if not items:
                items.append((" ", 0))
            self.button_widgets["microphone_combo"].add_items(items, select_index)
        
    def __set_card_treeview_status(self):
        card_list = []
        cards = pypulse.PULSE.get_cards()
        for idx in cards:
            active_profile = cards[idx]['active_profile']
            if active_profile:
                if active_profile['n_sinks'] > 1:
                    io_num = _("%d Outputs") % active_profile['n_sinks']
                else:
                    io_num = _("%d Output") % active_profile['n_sinks']
                if active_profile['n_sources'] > 1:
                    io_num += " / " + _("%d Inputs") % active_profile['n_sources']
                else:
                    io_num += " / " + _("%d Input") % active_profile['n_sources']
                if 'device.description' in cards[idx]['proplist']:
                    description = cards[idx]['proplist']['device.description'].strip('\x00')
                else:
                    description = ""
                card_info = "%s(%s)[%s]" % (description, io_num, active_profile['description'])
            else:
                if 'device.description' in cards[idx]['proplist']:
                    card_info = cards[idx]['proplist']['device.description']
                else:
                    card_info = " "
            card_list.append(TreeItem(self.image_widgets["device"], card_info, cards[idx]['name'], idx))
        self.view_widgets["ad_hardware"].add_items(card_list, clear_first=True)
        if card_list:
            self.view_widgets["ad_hardware"].set_select_rows([0])

    def __set_output_treeview_status(self):
        current_sink = pypulse.get_fallback_sink_index()
        sinks = pypulse.PULSE.get_output_devices()
        output_list = []
        i = 0
        selected_row = -1
        for idx in sinks:
            if current_sink is not None and current_sink == idx:
                selected_row = i
            if 'device.description' in sinks[idx]['proplist']:
                description = sinks[idx]['proplist']['device.description'].strip('\x00')
            else:
                description = ""
            output_list.append(TreeItem(self.image_widgets["device"], description, sinks[idx]['name'], idx))
            i += 1
        self.view_widgets["ad_output"].add_items(output_list, clear_first=True)
        if not (selected_row < 0):
            self.view_widgets["ad_output"].set_select_rows([selected_row])

    def __set_input_treeview_status(self):
        current_source = pypulse.get_fallback_source_index()
        sources = pypulse.PULSE.get_input_devices()
        input_list = []
        i = 0
        selected_row = -1
        for idx in sources:
            if current_source is not None and current_source == idx:
                selected_row = i
            if 'device.description' in sources[idx]['proplist']:
                description = sources[idx]['proplist']['device.description'].strip('\x00')
            else:
                description = ""
            input_list.append(TreeItem(self.image_widgets["device"], description, sources[idx]['name'], idx))
            i += 1
        self.view_widgets["ad_input"].add_items(input_list, clear_first=True)
        if not (selected_row < 0):
            self.view_widgets["ad_input"].set_select_rows([selected_row])

    def set_status_text(self, text):
        self.container_widgets["statusbar"].set_text(text)

    def set_to_default(self):
        '''set to the default'''
        pass

if __name__ == '__main__':
    gtk.gdk.threads_init()
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    sound_settings = SoundSetting(module_frame)

    #module_frame.add(sound_settings.alignment_widgets["slider"])
    module_frame.add(sound_settings.container_widgets["main_vbox"])
    module_frame.connect("realize", lambda w: sound_settings.container_widgets["slider"].set_to_page(gtk.VBox()))
    if len(sys.argv) > 1:
        print "module_uid:", sys.argv[1]

    def message_handler(*message):
        (message_type, message_content) = message
        print "message:", message_type, message_content
        if message_type == "click_crumb":
            (crumb_index, crumb_label) = message_content
            if crumb_index == 1:
                sound_settings.container_widgets["slider"].slide_to_page(
                    sound_settings.alignment_widgets["main_hbox"], "left")
                #sound_settings.container_widgets["slider"].slide_to_page(
                    #sound_settings.container_widgets["main_hbox"], "left")
        elif message_type == "show_again":
            print "DEBUG show_again module_uid", message_content
            sound_settings.container_widgets["slider"].set_to_page(
                sound_settings.alignment_widgets["main_hbox"])
            module_frame.send_module_info()

    module_frame.module_message_handler = message_handler

    module_frame.run()
