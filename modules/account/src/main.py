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

import settings

import sys
import os
from dtk.ui.utils import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))

from nls import _
from theme import app_theme
from dtk.ui.label import Label
from dtk.ui.button import CheckButton, Button
from dtk.ui.new_entry import InputEntry
from dtk.ui.utils import propagate_expose, cairo_disable_antialias
import gtk
from module_frame import ModuleFrame


class AccountSetting(object):
    '''account setting'''
    def __init__(self, module_frame):
        super(AccountSetting, self).__init__()
        self.module_frame = module_frame
        
        self.image_widgets = {}
        self.label_widgets = {}
        self.button_widgets = {}
        self.adjust_widgets = {}
        self.scale_widgets = {}
        self.alignment_widgets = {}
        self.container_widgets = {}
        self.view_widgets = {}
        self.dialog_widget = {}
    
    def __create_widget(self):
        # label 
        self.label_widgets["account"] = Label(_("Account type"))
        self.label_widgets["passwd"] = Label(_("Password"))
        self.label_widgets["auto_login"] = Label(_("Automatic Login"))
        self.label_widgets["deepin_account_tips"] = Label(_("Deepin Account"))
        self.label_widgets["account_type"] = Label("")
        self.label_widgets["deepin_account"] = Label("")
        # image
        self.image_widgets["lock"] = gtk.image_new_from_file(
            app_theme.get_theme_file_path("image/set/lock.png"))
        self.image_widgets["unlock"] = gtk.image_new_from_file(
            app_theme.get_theme_file_path("image/set/unlock.png"))
        self.image_widgets["switch_bg_active"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/toggle_bg_active.png"))
        self.image_widgets["switch_bg_nornal"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/toggle_bg_normal.png"))
        self.image_widgets["switch_fg"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/toggle_fg.png"))
        self.image_widgets["set"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/set.png"))
        # button
        self.button_widgets["auto_login"] = gtk.ToggleButton()
        self.button_widgets["passwd"] = InputEntry()
        self.button_widgets["net_access_check"] = CheckButton(_("网络访问权限"))
        self.button_widgets["disk_readonly_check"] = CheckButton(_("磁盘操作权限只读"))
        self.button_widgets["mountable_check"] = CheckButton(_("可加载移动设备"))
        self.button_widgets["disk_readwrite_check"] = CheckButton(_("磁盘操作权限完全"))
        self.button_widgets["backup_check"] = CheckButton(_("自动备份个人偏好设置并上传到云端，重新装机或在另一台计算机登录深度系统时您不再需要设置偏好。"))
        self.button_widgets["binding"] = Label(_("提示：此功能需要绑定深度帐号。"))
        self.button_widgets["add_account"] = Button(_("Add"))
        self.button_widgets["del_account"] = Button(_("Delete"))

if __name__ == '__main__':
    gtk.gdk.threads_init()
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    account_settings = AccountSetting(module_frame)
    
    module_frame.add(account_settings.container_widgets["main_hbox"])
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            module_frame.send_module_info()

    module_frame.module_message_handler = message_handler        
    
    module_frame.run()
