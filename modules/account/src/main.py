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
from dtk.ui.combo import ComboBox
from dtk.ui.new_slider import HSlider
from dtk.ui.utils import propagate_expose, cairo_disable_antialias
from treeitem import MyTreeView as TreeView
from treeitem import MyTreeItem as TreeItem
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
        self.alignment_widgets = {}
        self.container_widgets = {}
        self.view_widgets = {}
        self.dialog_widget = {}

        self.__create_widget()
        self.__adjust_widget()
        self.__signals_connect()
    
    def __create_widget(self):
        # label 
        self.label_widgets["account_name"] = Label("")
        self.label_widgets["account"] = Label(_("Account type"))
        self.label_widgets["passwd"] = Label(_("Password"))
        self.label_widgets["passwd_char"] = Label("****")
        self.label_widgets["auto_login"] = Label(_("Automatic Login"))
        self.label_widgets["deepin_account_tips"] = Label(_("Deepin Account"))
        self.label_widgets["deepin_account"] = Label(_("Unbound"))
        self.label_widgets["account_name_new"] = Label(_("Account Name"))
        self.label_widgets["account_type_new"] = Label(_("Account type"))
        self.label_widgets["deepin_account_new"] = Label(_("Unbound"))
        # image
        self.image_widgets["lock_pixbuf"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/lock.png"))
        self.image_widgets["unlock_pixbuf"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/unlock.png"))
        self.image_widgets["switch_bg_active"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/toggle_bg_active.png"))
        self.image_widgets["switch_bg_nornal"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/toggle_bg_normal.png"))
        self.image_widgets["switch_fg"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/toggle_fg.png"))
        self.image_widgets["set"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/set.png"))
        self.image_widgets["account_ico"] = gtk.Image()
        self.image_widgets["lock"] = gtk.Image()
        # button
        self.button_widgets["account_name"] = InputEntry()
        self.button_widgets["account_type"] = ComboBox([('Administrator', 0), ('Standard', 1)], max_width=115)
        self.button_widgets["auto_login"] = gtk.ToggleButton()
        self.button_widgets["passwd"] = InputEntry()
        self.button_widgets["net_access_check"] = CheckButton(_("网络访问权限"))
        self.button_widgets["disk_readonly_check"] = CheckButton(_("磁盘操作权限只读"))
        self.button_widgets["mountable_check"] = CheckButton(_("可加载移动设备"))
        self.button_widgets["disk_readwrite_check"] = CheckButton(_("磁盘操作权限完全"))
        self.button_widgets["backup_check"] = CheckButton(_("自动备份个人偏好设置并上传到云端，重新装机或在另一台计算机登录深度系统时您不再需要设置偏好。"))
        self.button_widgets["binding"] = Label(_("提示：此功能需要绑定<span foreground=\"blue\" underline=\"single\">深度帐号。</span>"))
        self.button_widgets["add_account"] = Button(_("Add"))
        self.button_widgets["del_account"] = Button(_("Delete"))
        self.button_widgets["account_create"] = Button(_("Create"))
        self.button_widgets["account_cancle"] = Button(_("Cancle"))
        self.button_widgets["account_type_new"] = ComboBox([('Administrator', 0), ('Standard', 1)], max_width=115)
        self.button_widgets["net_access_check_new"] = CheckButton(_("网络访问权限"))
        self.button_widgets["disk_readonly_check_new"] = CheckButton(_("磁盘操作权限只读"))
        self.button_widgets["mountable_check_new"] = CheckButton(_("可加载移动设备"))
        self.button_widgets["disk_readwrite_check_new"] = CheckButton(_("磁盘操作权限完全"))
        self.button_widgets["backup_check_new"] = CheckButton(_("自动备份个人偏好设置并上传到云端，重新装机或在另一台计算机登录深度系统时您不再需要设置偏好。"))
        self.button_widgets["binding_new"] = Label(_("提示：此功能需要绑定<span foreground=\"blue\" underline=\"single\">深度帐号。</span>"))
        # container
        self.container_widgets["slider"] = HSlider()
        self.container_widgets["main_hbox"] = gtk.HBox(False)
        self.container_widgets["left_vbox"] = gtk.VBox(False)
        self.container_widgets["button_hbox"] = gtk.HBox(False)
        self.container_widgets["right_vbox"] = gtk.VBox(False)
        self.container_widgets["account_info_hbox"] = gtk.HBox(False)
        self.container_widgets["account_add_vbox"] = gtk.VBox(False)
        self.container_widgets["account_info_table"] = gtk.Table(5, 2)
        self.container_widgets["check_button_table"] = gtk.Table(4, 2)
        self.container_widgets["account_info_table_new"] = gtk.Table(4, 2)
        self.container_widgets["check_button_table_new"] = gtk.Table(4, 2)
        # treeview
        self.view_widgets["account"] = TreeView()
        # alignment
        self.alignment_widgets["main_hbox"] = gtk.Alignment()
        self.alignment_widgets["left_vbox"] = gtk.Alignment()
        self.alignment_widgets["button_hbox"] = gtk.Alignment()
        self.alignment_widgets["right_vbox"] = gtk.Alignment()
        self.alignment_widgets["account_info_hbox"] = gtk.Alignment()
        self.alignment_widgets["account_add_vbox"] = gtk.Alignment()
        self.alignment_widgets["change_pswd"] = gtk.Alignment()
    
    def __adjust_widget(self):
        self.container_widgets["slider"].append_page(self.alignment_widgets["main_hbox"])
        self.container_widgets["slider"].append_page(self.alignment_widgets["change_pswd"])

        self.alignment_widgets["main_hbox"].add(self.container_widgets["main_hbox"])
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["left_vbox"], False, False)
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["right_vbox"])
        self.alignment_widgets["left_vbox"].add(self.container_widgets["left_vbox"])
        self.alignment_widgets["right_vbox"].add(self.container_widgets["right_vbox"])
        self.alignment_widgets["main_hbox"].set(0.5, 0.5, 1, 1)
        self.alignment_widgets["main_hbox"].set_padding(5, 5, 5, 5)
        # accounts list
        self.container_widgets["left_vbox"].pack_start(self.view_widgets["account"])
        self.container_widgets["left_vbox"].pack_start(self.container_widgets["button_hbox"], False, False, 10)
        self.container_widgets["button_hbox"].pack_start(self.alignment_widgets["button_hbox"])
        self.container_widgets["button_hbox"].pack_start(self.button_widgets["add_account"], False, False, 10)
        self.container_widgets["button_hbox"].pack_start(self.button_widgets["del_account"], False, False)
        self.alignment_widgets["button_hbox"].set(0, 0, 1, 1)
        self.view_widgets["account"].set_size_request(325, 355)
        # accounts info
        self.alignment_widgets["right_vbox"].set(0, 0, 1, 1)
        self.alignment_widgets["right_vbox"].set_padding(0, 0, 20, 20)
        #self.container_widgets["right_vbox"].pack_start(self.container_widgets["account_info_vbox"], False, False)
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["account_info_table"], False, False)
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["check_button_table"], False, False)

        self.container_widgets["account_info_table"].attach(self.image_widgets["account_ico"], 0, 1, 0, 1, 0)
        self.container_widgets["account_info_table"].attach(self.alignment_widgets["account_info_hbox"], 0, 1, 0, 1, 0)
        self.container_widgets["account_info_table"].attach(self.label_widgets["account"], 0, 1, 1, 2, 0)
        self.container_widgets["account_info_table"].attach(self.button_widgets["account_type_new"], 1, 2, 1, 2, 0, 5, 10)
        self.container_widgets["account_info_table"].attach(self.label_widgets["passwd"], 0, 1, 2, 3, 0)
        self.container_widgets["account_info_table"].attach(self.label_widgets["passwd_char"], 1, 2, 2, 3, 0)
        self.container_widgets["account_info_table"].attach(self.label_widgets["auto_login"], 0, 1, 3, 4, 0)
        self.container_widgets["account_info_table"].attach(self.button_widgets["auto_login"], 1, 2, 3, 4, 0)
        self.container_widgets["account_info_table"].attach(self.label_widgets["deepin_account_tips"], 0, 1, 4, 5, 0)
        self.container_widgets["account_info_table"].attach(self.label_widgets["deepin_account"], 1, 2, 4, 5, 0)
        self.button_widgets["auto_login"].set_size_request(49, 22)

    def __signals_connect(self):
        self.button_widgets["auto_login"].connect("expose-event", self.toggle_button_expose)

    ######################################
    # signals callback begine
    # widget signals
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

if __name__ == '__main__':
    gtk.gdk.threads_init()
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    account_settings = AccountSetting(module_frame)
    
    module_frame.add(account_settings.container_widgets["slider"])
    module_frame.connect("realize", 
        lambda w: account_settings.container_widgets["slider"].set_to_page(
        account_settings.alignment_widgets["main_hbox"]))
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            module_frame.send_module_info()

    module_frame.module_message_handler = message_handler        
    
    module_frame.run()
