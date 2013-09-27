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

from nls import _
from dtk.ui.label import Label
from dtk.ui.box import ImageBox
from dtk.ui.utils import color_hex_to_cairo
from constant import *
from module_frame import ModuleFrame
import gtk
import settings

MODULE_NAME = "system_information"

class SysInfo(object):
    '''system infomation'''
    def __init__(self, module_frame):
        super(SysInfo, self).__init__()
        self.module_frame = module_frame

        self.label_widgets = {}
        self.image_widgets = {}
        self.alignment_widgets = {}
        self.container_widgets = {}

        self.__create_widget()
        self.__adjust_widget()
        self.__signals_connect()

    def __create_widget(self):
        # label widget
        self.label_widgets["copyright"] = Label("%s%s" % ("Copyright © 2011 - 2013 ", _("Wuhan Deepin Technology Co.Ltd, All rights reserved")), enable_select=False, enable_double_click=False)
        self.label_widgets["version"] = Label(_("Version"), enable_select=False, enable_double_click=False)
        self.label_widgets["cpu"] = Label(_("CPU"), enable_select=False, enable_double_click=False)
        self.label_widgets["mem"] = Label(_("Memory"), enable_select=False, enable_double_click=False)
        self.label_widgets["arch"] = Label(_("OS Type"), enable_select=False, enable_double_click=False)
        self.label_widgets["disk"] = Label(_("Disk"), enable_select=False, enable_double_click=False)
        self.label_widgets["version_info"] = Label("", enable_select=False, enable_double_click=False)
        self.label_widgets["cpu_info"] = Label("", enable_select=False, enable_double_click=False)
        self.label_widgets["mem_info"] = Label("", enable_select=False, enable_double_click=False)
        self.label_widgets["arch_info"] = Label("", enable_select=False, enable_double_click=False)
        self.label_widgets["disk_info"] = Label("", enable_select=False, enable_double_click=False)

        # image widget
        self.image_widgets["logo"] = ImageBox(app_theme.get_pixbuf('%s/logo.png' % MODULE_NAME))
        
        # container widget
        self.container_widgets["main_hbox"] = gtk.HBox(False)
        self.container_widgets["left_vbox"] = gtk.VBox(False)
        self.container_widgets["right_vbox"] = gtk.VBox(False)
        self.container_widgets["info_vbox"] = gtk.VBox(False)
        self.container_widgets["info_table"] = gtk.Table(5, 2)

        # alignment widget
        self.alignment_widgets["main_hbox"] = gtk.Alignment()
        self.alignment_widgets["logo"] = gtk.Alignment()
        self.alignment_widgets["right_vbox"] = gtk.Alignment()

    def __adjust_widget(self):
        MID_SPACING = 10
        self.alignment_widgets["main_hbox"].add(self.container_widgets["main_hbox"])
        self.alignment_widgets["main_hbox"].set(0, 0, 1, 1)
        self.alignment_widgets["main_hbox"].set_padding(
            TEXT_WINDOW_TOP_PADDING-25, 0, TEXT_WINDOW_LEFT_PADDING-40, TEXT_WINDOW_RIGHT_WIDGET_PADDING)
        
        self.container_widgets["main_hbox"].set_spacing(MID_SPACING)
        self.container_widgets["main_hbox"].pack_start(self.container_widgets["left_vbox"])
        #self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["right_vbox"])

        self.container_widgets["left_vbox"].pack_start(self.image_widgets["logo"], False, False)
        #self.container_widgets["left_vbox"].pack_start(self.alignment_widgets["logo"])
        self.container_widgets["left_vbox"].pack_start(self.alignment_widgets["right_vbox"])
        #self.alignment_widgets["logo"].set(0, 0, 1, 1)
        self.alignment_widgets["right_vbox"].set(0, 0, 1, 1)
        self.alignment_widgets["right_vbox"].set_padding(0, 0, 100, 0)
        self.alignment_widgets["right_vbox"].add(self.container_widgets["right_vbox"])

        self.container_widgets["right_vbox"].set_spacing(BETWEEN_SPACING)
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["info_vbox"], False, False)
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["info_table"], False, False)
        self.container_widgets["right_vbox"].pack_start(gtk.Alignment(0, 0, 1, 1))
        #
        #self.container_widgets["info_vbox"].pack_start(
            #self.__make_align(self.label_widgets["version"]), False, False)
        self.container_widgets["info_vbox"].pack_start(
            self.__make_align(self.label_widgets["copyright"]), False, False)
        label_widgets = self.label_widgets
        label_width = max(label_widgets["cpu"].size_request()[0],
                          label_widgets["version"].size_request()[0],
                          label_widgets["mem"].size_request()[0],
                          label_widgets["arch"].size_request()[0],
                          label_widgets["disk"].size_request()[0]) + 2
        #label_widgets["cpu"].set_size_request(label_width, WIDGET_HEIGHT)
        #label_widgets["mem"].set_size_request(label_width, WIDGET_HEIGHT)
        #label_widgets["arch"].set_size_request(label_width, WIDGET_HEIGHT)
        #label_widgets["disk"].set_size_request(label_width, WIDGET_HEIGHT)
        # table attach
        self.container_widgets["info_table"].attach(
            self.__make_align(self.label_widgets['version'], width=label_width), 0, 1, 0, 1, 4)
        self.container_widgets["info_table"].attach(
            self.__make_align(self.label_widgets['cpu'], width=label_width), 0, 1, 1, 2, 4)
        self.container_widgets["info_table"].attach(
            self.__make_align(self.label_widgets['mem'], width=label_width), 0, 1, 2, 3, 4)
        self.container_widgets["info_table"].attach(
            self.__make_align(self.label_widgets['arch'], width=label_width), 0, 1, 3, 4, 4)
        self.container_widgets["info_table"].attach(
            self.__make_align(self.label_widgets['disk'], width=label_width), 0, 1, 4, 5, 4)
        
        self.container_widgets["info_table"].attach(
            self.__make_align(self.label_widgets['version_info']), 1, 2, 0, 1, 5)
        self.container_widgets["info_table"].attach(
            self.__make_align(self.label_widgets['cpu_info']), 1, 2, 1, 2, 5)
        self.container_widgets["info_table"].attach(
            self.__make_align(self.label_widgets['mem_info']), 1, 2, 2, 3, 5)
        self.container_widgets["info_table"].attach(
            self.__make_align(self.label_widgets['arch_info']), 1, 2, 3, 4, 5)
        self.container_widgets["info_table"].attach(
            self.__make_align(self.label_widgets['disk_info']), 1, 2, 4, 5, 5)

        self.container_widgets["info_table"].set_col_spacings(WIDGET_SPACING)

        # show sysinfo
        #self.label_widgets["version_info"].set_text("%s" % settings.get_os_version())
        self.label_widgets["version_info"].set_text('12.12.1')
        self.label_widgets["cpu_info"].set_text("%s" % settings.get_cpu_info())
        self.label_widgets["mem_info"].set_text("%.1fGB" % settings.get_mem_info())
        self.label_widgets["arch_info"].set_text("%s%s" % (settings.get_os_arch(), _("bit")))
        disk_size = settings.get_disk_size()
        if disk_size:
            self.label_widgets["disk_info"].set_text("%.2fGB" % disk_size)
        else:
            self.label_widgets["disk_info"].set_text("--")
    
    def __signals_connect(self):
        self.alignment_widgets["main_hbox"].connect("expose-event", self.container_expose_cb)
    
    def container_expose_cb(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))
        cr.rectangle(x, y, w, h)
        cr.fill()
    
    def __make_align(self, widget=None, xalign=0.0, yalign=0.5, xscale=1.0,
                     yscale=0.0, padding_top=0, padding_bottom=0, padding_left=0,
                     padding_right=0, width=-1, height=CONTAINNER_HEIGHT):
        align = gtk.Alignment()
        align.set_size_request(width, height)
        align.set(xalign, yalign, xscale, yscale)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        if widget:
            align.add(widget)
        return align
if __name__ == '__main__':
    gtk.gdk.threads_init()
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    sys_info = SysInfo(module_frame)
    
    module_frame.add(sys_info.alignment_widgets["main_hbox"])
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            module_frame.send_module_info()
        elif message_type == "exit":
            module_frame.exit()

    module_frame.module_message_handler = message_handler        
    module_frame.run()
