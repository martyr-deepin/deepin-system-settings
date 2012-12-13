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
from dtk.ui.utils import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))

from nls import _
from theme import app_theme
from dtk.ui.label import Label

from module_frame import ModuleFrame
import gtk
import settings

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

    def __create_widget(self):
        # label widget
        self.label_widgets["version"] = Label(" ", text_size=13, enable_select=False)
        self.label_widgets["copyright"] = Label(_("版权所有© 2009  深之度科技有限公司。保留所有权利。"), enable_select=False)
        self.label_widgets["cpu"] = Label(_("Processor"))
        self.label_widgets["mem"] = Label(_("Memory"))
        self.label_widgets["arch"] = Label(_("OS Type"))
        self.label_widgets["disk"] = Label(_("Disk"))
        self.label_widgets["cpu_info"] = Label("")
        self.label_widgets["mem_info"] = Label("")
        self.label_widgets["arch_info"] = Label("")
        self.label_widgets["disk_info"] = Label("")

        # image widget
        self.image_widgets["logo"] = gtk.image_new_from_file(
            app_theme.get_theme_file_path('image/logo.png'))
        
        # container widget
        self.container_widgets["main_hbox"] = gtk.HBox(False)
        self.container_widgets["left_vbox"] = gtk.VBox(False)
        self.container_widgets["right_vbox"] = gtk.VBox(False)
        self.container_widgets["info_table"] = gtk.Table(5, 2)

        # alignment widget
        self.alignment_widgets["main_hbox"] = gtk.Alignment()
        self.alignment_widgets["logo"] = gtk.Alignment()
        self.alignment_widgets["right_vbox"] = gtk.Alignment()

    def __adjust_widget(self):
        self.alignment_widgets["main_hbox"].add(self.container_widgets["main_hbox"])
        self.alignment_widgets["main_hbox"].set(0, 0, 1, 1)
        self.alignment_widgets["main_hbox"].set_padding(30, 30, 30, 10)

        self.container_widgets["main_hbox"].pack_start(self.container_widgets["left_vbox"], False, False)
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["right_vbox"], False, False, 10)

        self.container_widgets["left_vbox"].pack_start(self.image_widgets["logo"], False, False)
        self.container_widgets["left_vbox"].pack_start(self.alignment_widgets["logo"])
        self.alignment_widgets["logo"].set(0, 0, 1, 1)
        self.alignment_widgets["right_vbox"].set(0, 0, 1, 1)
        self.alignment_widgets["right_vbox"].add(self.container_widgets["right_vbox"])

        self.container_widgets["right_vbox"].pack_start(self.label_widgets["version"], False, False)
        self.container_widgets["right_vbox"].pack_start(self.label_widgets["copyright"], False, False, 10)
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["info_table"], False, False, 25)
        # table attach
        self.container_widgets["info_table"].attach(self.label_widgets['cpu'], 0, 1, 1, 2)
        self.container_widgets["info_table"].attach(self.label_widgets['mem'], 0, 1, 2, 3)
        self.container_widgets["info_table"].attach(self.label_widgets['arch'], 0, 1, 3, 4)
        self.container_widgets["info_table"].attach(self.label_widgets['disk'], 0, 1, 4, 5)
        
        self.container_widgets["info_table"].attach(self.label_widgets['cpu_info'], 1, 2, 1, 2, 4)
        self.container_widgets["info_table"].attach(self.label_widgets['mem_info'], 1, 2, 2, 3, 4)
        self.container_widgets["info_table"].attach(self.label_widgets['arch_info'], 1, 2, 3, 4, 4)
        self.container_widgets["info_table"].attach(self.label_widgets['disk_info'], 1, 2, 4, 5, 4)

        self.container_widgets["info_table"].set_col_spacings(50)
        self.container_widgets["info_table"].set_row_spacings(15)

        # show sysinfo
        self.label_widgets["version"].set_text("<b>%s</b>" % settings.get_os_version())
        self.label_widgets["cpu_info"].set_text("%s" % settings.get_cpu_info())
        self.label_widgets["mem_info"].set_text("%.1fGB" % settings.get_mem_info())
        self.label_widgets["arch_info"].set_text("%s" % settings.get_os_arch())
        disk_size = settings.get_disk_size()
        if disk_size:
            self.label_widgets["disk_info"].set_text("%.2fGB" % disk_size)
        else:
            self.label_widgets["disk_info"].set_text("--")
if __name__ == '__main__':
    gtk.gdk.threads_init()
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    sys_info = SysInfo(module_frame)
    
    module_frame.add(sys_info.alignment_widgets["main_hbox"])
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            module_frame.send_module_info()

    module_frame.module_message_handler = message_handler        
    module_frame.run()
