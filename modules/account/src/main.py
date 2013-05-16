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

import settings
from nls import _
from icon_button import IconButton
from dtk.ui.theme import ui_theme
from dtk.ui.label import Label
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.button import CheckButton, Button, SwitchButton
from dtk.ui.entry import InputEntry, PasswordEntry
from dtk.ui.combo import ComboBox
from dtk.ui.slider import HSlider
from dtk.ui.utils import container_remove_all, color_hex_to_cairo, cairo_disable_antialias
from dtk.ui.constant import ALIGN_END
from treeitem import MyTreeView as TreeView
from treeitem import MyTreeItem as TreeItem
from account_utils import AccountsPermissionDenied, AccountsUserDoesNotExist, AccountsUserExists, AccountsFailed
import gtk
import pango
import threading
import tools
import getpass
import crypt
from random import randint
from module_frame import ModuleFrame
from constant import *
from pexpect import TIMEOUT, EOF
from set_icon_page import IconSetPage
from edit_icon_page import IconEditPage
from statusbar import StatusBar

MODULE_NAME = "account"
COMBO_WIDTH = 190
LABEL_WIDTH = 180
INSENSITIVE_TEXT_COLOR = "#DCDCDC"

class AccountSetting(object):
    '''account setting'''
    CH_PASSWD_CURRENT_PSWD = 0
    CH_PASSWD_NEW_PSWD = 1
    CH_PASSWD_CONFIRM_PSWD = 2

    CH_PASSWD_ACTION_SET_PSWD = 0
    CH_PASSWD_ACTION_NO_PSWD = 1
    CH_PASSWD_ACTION_ENABLE = 2
    CH_PASSWD_ACTION_DISABLE = 3

    def __init__(self, module_frame):
        super(AccountSetting, self).__init__()
        self.module_frame = module_frame
        self.account_dbus = settings.ACCOUNT
        self.permission = settings.PERMISSION

        self.image_widgets = {}
        self.label_widgets = {}
        self.button_widgets = {}
        self.alignment_widgets = {}
        self.container_widgets = {}
        self.view_widgets = {}
        self.dialog_widget = {}

        self.__is_first_show = True
        self.current_select_user = None
        self.current_passwd_user = None
        self.current_set_user = None
        self.current_select_item = None
        self.mutex = threading.Lock()

        self.__create_widget()
        self.__adjust_widget()
        self.__signals_connect()

    def __create_widget(self):
        #####################################
        # account list page
        # label
        self.label_widgets["account_name"] = Label("", label_width=255, enable_select=False, enable_double_click=False)
        self.label_widgets["account"] = Label(_("Account type"), enable_select=False,
                text_x_align=ALIGN_END, enable_double_click=False, fixed_width=LABEL_WIDTH)
        self.label_widgets["passwd"] = Label(_("Password"), enable_select=False,
                text_x_align=ALIGN_END, enable_double_click=False, fixed_width=LABEL_WIDTH)
        self.label_widgets["passwd_char"] = Label("****", label_width=COMBO_WIDTH-1, enable_select=False, enable_double_click=False)
        ##self.label_widgets["auto_login"] = Label(_("Automatic login"), enable_select=False, enable_double_click=False)
        self.label_widgets["nopw_login"] = Label(_("Log in without a password"), enable_select=False,
                text_x_align=ALIGN_END, enable_double_click=False, fixed_width=LABEL_WIDTH)
        self.label_widgets["deepin_account_tips"] = Label(_("Deepin Account"), enable_select=False, enable_double_click=False)
        self.label_widgets["deepin_account"] = Label(_("Unbound"), enable_select=False, enable_double_click=False)
        self.label_widgets["account_name_new"] = Label(_("Account Name"), enable_select=False, enable_double_click=False)
        self.label_widgets["account_type_new"] = Label(_("Account type"), enable_select=False, enable_double_click=False)
        self.label_widgets["deepin_account_tips_new"] = Label(_("Deepin Account"), enable_select=False, enable_double_click=False)
        self.label_widgets["deepin_account_new"] = Label(_("Unbound"), enable_select=False, enable_double_click=False)
        self.label_widgets["account_create_error"] = Label("", wrap_width=360, enable_select=False, enable_double_click=False)
        self.label_widgets["account_info_error"] = Label("", wrap_width=360, enable_select=False, enable_double_click=False)
        # image
        self.image_widgets["lock_pixbuf"] = app_theme.get_pixbuf("lock/lock.png")
        self.image_widgets["unlock_pixbuf"] = app_theme.get_pixbuf("lock/unlock.png")
        self.image_widgets["default_icon"] = app_theme.get_pixbuf("%s/icon.png" % MODULE_NAME)
        self.image_widgets["account_icon"] = IconButton(self.image_widgets["default_icon"].get_pixbuf())
        # button
        self.button_widgets["account_name"] = InputEntry()
        self.button_widgets["lock"] = gtk.Button()
        self.button_widgets["account_type"] = ComboBox([(_('Standard'), 0), (_('Administrator'), 1)], fixed_width=COMBO_WIDTH)
        #self.button_widgets["auto_login"] = gtk.ToggleButton()
        ##self.button_widgets["auto_login"] = SwitchButton()
        self.button_widgets["nopw_login"] = SwitchButton(
            inactive_disable_dpixbuf=app_theme.get_pixbuf("toggle_button/inactive_normal.png"), 
            active_disable_dpixbuf=app_theme.get_pixbuf("toggle_button/inactive_normal.png"))
        self.button_widgets["passwd"] = InputEntry()
        #self.button_widgets["net_access_check"] = CheckButton(_("网络访问权限"), padding_x=0)
        #self.button_widgets["disk_readonly_check"] = CheckButton(_("磁盘操作权限只读"), padding_x=0)
        #self.button_widgets["mountable_check"] = CheckButton(_("可加载移动设备"), padding_x=0)
        #self.button_widgets["disk_readwrite_check"] = CheckButton(_("磁盘操作权限完全"), padding_x=0)

        #self.button_widgets["backup_check_group"] = CheckButton("", padding_x=0)
        #self.label_widgets["backup_check_group"] = Label(_("自动备份个人偏好设置并上传到云端，重新装机或在另一台计算机登录深度系统时您不再需要设置偏好。"), wrap_width=360, enable_select=False, enable_double_click=False)
        #self.alignment_widgets["backup_check_group"] = gtk.Alignment()
        #self.container_widgets["backup_check_group_hbox"] = gtk.HBox(False)
        #self.container_widgets["backup_check_group_vbox"] = gtk.VBox(False)

        #self.button_widgets["binding"] = Label(_("提示：此功能需要绑定<span foreground=\"blue\" underline=\"single\">深度帐号</span>。"), enable_select=False, enable_double_click=False)
        self.button_widgets["disable_account"] = Button(_("Enable"))
        self.button_widgets["add_account"] = Button(_("Add"))
        self.button_widgets["del_account"] = Button(_("Delete"))
        self.button_widgets["account_create"] = Button(_("Create"))
        self.button_widgets["account_cancle"] = Button(_("Cancel"))
        self.button_widgets["account_type_new"] = ComboBox([(_('Standard'), 0), (_('Administrator'), 1)], fixed_width=COMBO_WIDTH)
        #self.button_widgets["net_access_check_new"] = CheckButton(_("网络访问权限"), padding_x=0)
        #self.button_widgets["disk_readonly_check_new"] = CheckButton(_("磁盘操作权限只读"), padding_x=0)
        #self.button_widgets["mountable_check_new"] = CheckButton(_("可加载移动设备"), padding_x=0)
        #self.button_widgets["disk_readwrite_check_new"] = CheckButton(_("磁盘操作权限完全"), padding_x=0)

        #self.button_widgets["backup_check_group_new"] = CheckButton("", padding_x=0)
        #self.label_widgets["backup_check_group_new"] = Label(_("自动备份个人偏好设置并上传到云端，重新装机或在另一台计算机登录深度系统时您不再需要设置偏好。"), wrap_width=360, enable_select=False, enable_double_click=False)
        #self.alignment_widgets["backup_check_group_new"] = gtk.Alignment()
        #self.container_widgets["backup_check_group_hbox_new"] = gtk.HBox(False)
        #self.container_widgets["backup_check_group_vbox_new"] = gtk.VBox(False)

        #self.button_widgets["binding_new"] = Label(_("提示：此功能需要绑定<span foreground=\"blue\" underline=\"single\">深度帐号</span>。"), enable_select=False, enable_double_click=False)
        # container
        self.container_widgets["main_vbox"] = gtk.VBox(False)
        self.container_widgets["statusbar"] = StatusBar()
        self.container_widgets["slider"] = HSlider()
        self.container_widgets["main_hbox"] = gtk.HBox(False)
        self.container_widgets["left_vbox"] = gtk.VBox(False)
        self.container_widgets["button_hbox"] = gtk.HBox(False)
        self.container_widgets["right_vbox"] = gtk.VBox(False)
        self.container_widgets["account_info_hbox"] = gtk.HBox(False)
        self.container_widgets["account_info_vbox"] = gtk.VBox(False)
        self.container_widgets["account_add_vbox"] = gtk.VBox(False)
        self.container_widgets["account_info_table"] = gtk.Table(6, 2)
        self.container_widgets["check_button_table"] = gtk.Table(4, 2)
        self.container_widgets["account_info_table_new"] = gtk.Table(4, 2)
        self.container_widgets["check_button_table_new"] = gtk.Table(4, 2)
        self.container_widgets["button_hbox_new"] = gtk.HBox(False)
        # treeview
        self.view_widgets["account"] = TreeView()
        # alignment
        self.alignment_widgets["main_hbox"] = gtk.Alignment()
        self.alignment_widgets["left_vbox"] = gtk.Alignment()
        self.alignment_widgets["button_hbox"] = gtk.Alignment()
        self.alignment_widgets["right_vbox"] = gtk.Alignment()
        self.alignment_widgets["account_info_hbox"] = gtk.Alignment()
        self.alignment_widgets["lock_button"] = gtk.Alignment()
        self.alignment_widgets["account_info_vbox"] = gtk.Alignment()
        self.alignment_widgets["account_add_vbox"] = gtk.Alignment()
        self.alignment_widgets["button_hbox_new"] = gtk.Alignment()
        #####################################
        # delete account page
        self.alignment_widgets["del_main_vbox"] = gtk.Alignment()
        self.container_widgets["del_main_vbox"] = gtk.VBox(False)
        self.label_widgets["del_account_tips"] = Label("", wrap_width=400, enable_select=False, enable_double_click=False)
        self.label_widgets["del_account_tips2"] = Label(
            _("It is possible to keep the home directory when deleting a user account."),
            wrap_width=400, enable_select=False, enable_double_click=False)
        self.label_widgets["del_account_error_label"] = Label("", wrap_width=390, enable_select=False, enable_double_click=False)
        self.button_widgets["del_button"] = Button(_("Delete Files"))
        self.button_widgets["keep_button"] = Button(_("Keep Files"))
        self.button_widgets["cancel_button"] = Button(_("Cancel"))
        self.container_widgets["del_account_button_hbox"] = gtk.HBox(False)
        #####################################
        # set icon page
        self.alignment_widgets["set_iconfile"] = gtk.Alignment()
        self.alignment_widgets["edit_iconfile"] = gtk.Alignment()
        self.button_widgets["cancel_set_icon"] = Button(_("Cancel"))
        self.button_widgets["save_edit_icon"] = Button(_("Save"))

    def __adjust_widget(self):
        self.container_widgets["main_vbox"].pack_start(self.container_widgets["slider"])
        self.container_widgets["main_vbox"].pack_start(self.container_widgets["statusbar"], False, False)
        self.container_widgets["slider"].append_page(self.alignment_widgets["main_hbox"])
        self.container_widgets["slider"].append_page(self.alignment_widgets["set_iconfile"])
        self.container_widgets["slider"].append_page(self.alignment_widgets["edit_iconfile"])
        self.container_widgets["slider"].set_size_request(800, 450)
        self.alignment_widgets["main_hbox"].set_name("main_hbox")
        self.alignment_widgets["set_iconfile"].set_name("set_iconfile")
        self.alignment_widgets["edit_iconfile"].set_name("edit_iconfile")

        self.container_widgets["statusbar"].set_buttons([self.button_widgets["disable_account"], 
                                                         self.button_widgets["add_account"],
                                                         self.button_widgets["del_account"]])
        self.statusbar_buttons_bak = []
        self.statusbar_buttons = {
            "main_hbox": [self.button_widgets["disable_account"], self.button_widgets["add_account"], self.button_widgets["del_account"]],
            "set_iconfile": [self.button_widgets["cancel_set_icon"]],
            "edit_iconfile": [self.button_widgets["cancel_set_icon"], self.button_widgets["save_edit_icon"]]}

        self.alignment_widgets["set_iconfile"].set_padding(TEXT_WINDOW_TOP_PADDING, 0, TEXT_WINDOW_LEFT_PADDING, 10)
        self.alignment_widgets["edit_iconfile"].set_padding(TEXT_WINDOW_TOP_PADDING, 0, TEXT_WINDOW_LEFT_PADDING, 100)

        #self.alignment_widgets["main_hbox"].set(0.0, 0.0, 1, 1)
        #self.alignment_widgets["main_hbox"].set_padding(FRAME_TOP_PADDING, 10, 0, FRAME_LEFT_PADDING)
        self.alignment_widgets["main_hbox"].set_padding(0, 0, 0, FRAME_LEFT_PADDING)
        self.alignment_widgets["main_hbox"].add(self.container_widgets["main_hbox"])
        #self.container_widgets["main_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["left_vbox"])
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["right_vbox"])
        self.alignment_widgets["left_vbox"].add(self.container_widgets["left_vbox"])
        self.alignment_widgets["right_vbox"].add(self.container_widgets["right_vbox"])
        self.alignment_widgets["left_vbox"].set_size_request(215, -1)
        self.alignment_widgets["left_vbox"].set_padding(0, 0, 40, 0)
        self.container_widgets["left_vbox"].set_size_request(210, -1)
        self.alignment_widgets["right_vbox"].set_size_request(560, -1)
        self.alignment_widgets["right_vbox"].set_padding(TEXT_WINDOW_TOP_PADDING, 0, 0, 0)
        self.view_widgets["account"].set_size_request(210, 460)
        ##############################
        # accounts list page
        self.container_widgets["left_vbox"].pack_start(self.view_widgets["account"])
        #self.container_widgets["left_vbox"].pack_start(self.alignment_widgets["button_hbox"], False, False)
        self.alignment_widgets["button_hbox"].add(self.container_widgets["button_hbox"])
        self.alignment_widgets["button_hbox"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["button_hbox"].set(1.0, 0.5, 0, 0)
        self.alignment_widgets["button_hbox"].set_padding(0, 0, 0, 10)
        self.container_widgets["button_hbox"].set_spacing(WIDGET_SPACING)
        #self.container_widgets["button_hbox"].pack_start(self.button_widgets["add_account"], False, False)
        #self.container_widgets["button_hbox"].pack_start(self.button_widgets["del_account"], False, False)
        # init treeview item
        self.view_widgets["account"].add_items(self.get_user_list_treeitem(), clear_first=True)
        self.view_widgets["account"].set_expand_column(0)
        ###############
        # accounts info
        self.alignment_widgets["right_vbox"].set(0, 0, 1, 1)
        #self.alignment_widgets["right_vbox"].set_padding(0, 0, 20, 20)
        #self.container_widgets["right_vbox"].pack_start(self.container_widgets["account_info_table"], False, False)
        #self.container_widgets["right_vbox"].pack_start(self.container_widgets["check_button_table"], False, False)
        self.container_widgets["right_vbox"].pack_start(self.alignment_widgets["account_info_vbox"], False, False)
        self.alignment_widgets["account_info_vbox"].set_padding(18, 0, 0, 0)
        self.alignment_widgets["account_info_vbox"].add(self.container_widgets["account_info_vbox"])
        self.container_widgets["account_info_vbox"].pack_start(self.container_widgets["account_info_table"], False, False)
        self.container_widgets["account_info_vbox"].pack_start(self.label_widgets["account_info_error"], False, False)

        self.container_widgets["account_info_table"].set_col_spacings(WIDGET_SPACING)
        self.container_widgets["account_info_table"].attach(
            self.__make_align(self.image_widgets["account_icon"], xalign=1.0, height=58), 0, 1, 0, 1, 4)
        self.container_widgets["account_info_table"].attach(self.alignment_widgets["account_info_hbox"], 1, 2, 0, 1, 4)

        self.container_widgets["account_info_table"].attach(
            self.__make_align(self.label_widgets["account"], xalign=1.0, width=LABEL_WIDTH), 0, 1, 1, 2, 4)
        self.container_widgets["account_info_table"].attach(
            self.__make_align(self.button_widgets["account_type"], xalign=0.0, width=COMBO_WIDTH), 1, 2, 1, 2, 4)

        ##self.container_widgets["account_info_table"].attach(
            ##self.__make_align(self.label_widgets["auto_login"], xalign=1.0, width=LABEL_WIDTH), 0, 1, 2, 3, 4)
        ##self.container_widgets["account_info_table"].attach(
            ##self.__make_align(self.button_widgets["auto_login"], xalign=0.0, width=COMBO_WIDTH), 1, 2, 2, 3, 4)

        self.container_widgets["account_info_table"].attach(
            self.__make_align(self.label_widgets["nopw_login"], xalign=1.0, width=LABEL_WIDTH), 0, 1, 2, 3, 4)
        self.container_widgets["account_info_table"].attach(
            self.__make_align(self.button_widgets["nopw_login"], xalign=0.0, width=COMBO_WIDTH), 1, 2, 2, 3, 4)

        self.container_widgets["account_info_table"].attach(
            self.__make_align(self.label_widgets["passwd"], xalign=1.0, width=LABEL_WIDTH), 0, 1, 3, 4, 4)
        self.container_widgets["account_info_table"].attach(
            self.__make_align(self.label_widgets["passwd_char"], xalign=0.0, width=COMBO_WIDTH), 1, 2, 3, 4, 4)
        #self.container_widgets["account_info_table"].attach(
            #self.__make_align(self.label_widgets["deepin_account_tips"]), 0, 1, 5, 6, 4)
        #self.container_widgets["account_info_table"].attach(
            #self.__make_align(self.label_widgets["deepin_account"]), 1, 2, 5, 6, 4)

        self.label_widgets["passwd_char"].set_size_request(COMBO_WIDTH, WIDGET_HEIGHT)
        self.button_widgets["account_type"].set_size_request(COMBO_WIDTH, WIDGET_HEIGHT)
        #self.image_widgets["account_icon"].set_size_request(48, 48)
        self.button_widgets["lock"].set_size_request(16, 16)
        self.alignment_widgets["account_info_hbox"].set(0.0, 0.5, 0, 0)
        self.alignment_widgets["account_info_hbox"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["account_info_hbox"].add(self.container_widgets["account_info_hbox"])
        self.container_widgets["account_info_hbox"].pack_start(self.label_widgets["account_name"], False, False)
        #self.container_widgets["account_info_hbox"].pack_start(self.alignment_widgets["lock_button"], False, False)
        self.alignment_widgets["lock_button"].add(self.button_widgets["lock"])
        self.alignment_widgets["lock_button"].set(1.0, 0.5, 0, 0)

        #self.container_widgets["backup_check_group_hbox"].pack_start(self.alignment_widgets["backup_check_group"], False, False)
        #self.container_widgets["backup_check_group_hbox"].pack_start(self.container_widgets["backup_check_group_vbox"], False, False)
        #self.alignment_widgets["backup_check_group"].add(self.button_widgets["backup_check_group"])
        #self.container_widgets["backup_check_group_vbox"].pack_start(self.label_widgets["backup_check_group"], False, False)
        #self.container_widgets["backup_check_group_vbox"].pack_start(self.button_widgets["binding"], False, False, BETWEEN_SPACING)

        #self.container_widgets["check_button_table"].set_col_spacings(WIDGET_SPACING)
        #self.container_widgets["check_button_table"].attach(
            #self.__make_align(self.button_widgets["net_access_check"]), 0, 1, 0, 1)
        #self.container_widgets["check_button_table"].attach(
            #self.__make_align(self.button_widgets["disk_readonly_check"]), 1, 2, 0, 1)
        #self.container_widgets["check_button_table"].attach(
            #self.__make_align(self.button_widgets["mountable_check"]), 0, 1, 1, 2)
        #self.container_widgets["check_button_table"].attach(
            #self.__make_align(self.button_widgets["disk_readwrite_check"]), 1, 2, 1, 2)
        #self.container_widgets["check_button_table"].attach(
            #self.__make_align(self.container_widgets["backup_check_group_hbox"]), 0, 2, 2, 3)

        ####################
        # create new account
        self.container_widgets["account_info_table_new"].set_col_spacings(WIDGET_SPACING)
        self.container_widgets["account_info_table_new"].attach(
            self.__make_align(self.label_widgets["account_name_new"], xalign=1.0, width=LABEL_WIDTH), 0, 1, 0, 1, 4)
        self.container_widgets["account_info_table_new"].attach(
            self.__make_align(self.button_widgets["account_name"]), 1, 2, 0, 1, 4)
        self.container_widgets["account_info_table_new"].attach(
            self.__make_align(self.label_widgets["account_type_new"], xalign=1.0, width=LABEL_WIDTH), 0, 1, 1, 2, 4)
        self.container_widgets["account_info_table_new"].attach(
            self.__make_align(self.button_widgets["account_type_new"]), 1, 2, 1, 2, 4)
        #self.container_widgets["account_info_table_new"].attach(
            #self.__make_align(self.label_widgets["deepin_account_tips_new"]), 0, 1, 2, 3, 4)
        #self.container_widgets["account_info_table_new"].attach(
            #self.__make_align(self.label_widgets["deepin_account_new"]), 1, 2, 2, 3, 4)

        self.button_widgets["account_name"].entry.check_text = tools.entry_check_account_name
        self.button_widgets["account_name"].set_size(COMBO_WIDTH, WIDGET_HEIGHT)
        self.button_widgets["account_type_new"].set_size_request(COMBO_WIDTH, WIDGET_HEIGHT)

        #self.container_widgets["backup_check_group_hbox_new"].pack_start(self.alignment_widgets["backup_check_group_new"], False, False)
        #self.container_widgets["backup_check_group_hbox_new"].pack_start(self.container_widgets["backup_check_group_vbox_new"], False, False)
        #self.alignment_widgets["backup_check_group_new"].add(self.button_widgets["backup_check_group_new"])
        #self.container_widgets["backup_check_group_vbox_new"].pack_start(self.label_widgets["backup_check_group_new"], False, False)
        #self.container_widgets["backup_check_group_vbox_new"].pack_start(self.button_widgets["binding_new"], False, False, BETWEEN_SPACING)

        #self.container_widgets["check_button_table_new"].set_col_spacings(WIDGET_SPACING)
        #self.container_widgets["check_button_table_new"].attach(
            #self.__make_align(self.button_widgets["net_access_check_new"]), 0, 1, 0, 1)
        #self.container_widgets["check_button_table_new"].attach(
            #self.__make_align(self.button_widgets["disk_readonly_check_new"]), 1, 2, 0, 1)
        #self.container_widgets["check_button_table_new"].attach(
            #self.__make_align(self.button_widgets["mountable_check_new"]), 0, 1, 1, 2)
        #self.container_widgets["check_button_table_new"].attach(
            #self.__make_align(self.button_widgets["disk_readwrite_check_new"]), 1, 2, 1, 2)
        #self.container_widgets["check_button_table_new"].attach(
            #self.__make_align(self.container_widgets["backup_check_group_hbox_new"]), 0, 2, 2, 3)

        self.alignment_widgets["account_create_error"] = self.__make_align(self.label_widgets["account_create_error"], height=60)
        self.alignment_widgets["button_hbox_new"].set(1, 0, 0, 0)
        self.alignment_widgets["button_hbox_new"].set_padding(BETWEEN_SPACING, 0, 0, 0)
        self.alignment_widgets["button_hbox_new"].add(self.container_widgets["button_hbox_new"])
        self.container_widgets["button_hbox_new"].pack_start(self.__make_align(height=-1))
        self.container_widgets["button_hbox_new"].set_spacing(WIDGET_SPACING)
        #self.container_widgets["button_hbox_new"].pack_start(self.button_widgets["account_cancle"], False, False)
        #self.container_widgets["button_hbox_new"].pack_start(self.button_widgets["account_create"], False, False)
        self.alignment_widgets["account_add_vbox"].add(self.container_widgets["account_add_vbox"])
        self.alignment_widgets["account_add_vbox"].set(0, 0, 1, 1)
        self.alignment_widgets["account_add_vbox"].set_padding(18, 0, 0, 0)
        self.container_widgets["account_add_vbox"].set_size_request(500, -1)
        self.container_widgets["account_add_vbox"].pack_start(self.container_widgets["account_info_table_new"], False, False)
        self.container_widgets["account_add_vbox"].pack_start(self.__make_align(), False, False)
        self.container_widgets["account_add_vbox"].pack_start(self.alignment_widgets["account_create_error"], False, False, BETWEEN_SPACING)
        self.container_widgets["account_add_vbox"].pack_start(self.__make_align(height=-1))
        self.container_widgets["account_add_vbox"].pack_start(self.alignment_widgets["button_hbox_new"], False, False)
        #############################
        # del account
        self.alignment_widgets["del_main_vbox"].set_padding(0, 0, 40, 0)
        self.alignment_widgets["del_main_vbox"].add(self.container_widgets["del_main_vbox"])
        self.container_widgets["del_main_vbox"].set_spacing(BETWEEN_SPACING)
        self.container_widgets["del_main_vbox"].pack_start(self.label_widgets["del_account_tips"], False, False)
        self.container_widgets["del_main_vbox"].pack_start(self.label_widgets["del_account_tips2"], False, False)
        self.container_widgets["del_main_vbox"].pack_start(self.label_widgets["del_account_error_label"], False, False)
        button_align = gtk.Alignment()
        button_align.set(1, 0.5, 1, 1)
        self.container_widgets["del_account_button_hbox"].pack_start(button_align)
        self.container_widgets["del_account_button_hbox"].set_spacing(WIDGET_SPACING)
        #self.container_widgets["del_account_button_hbox"].pack_start(self.button_widgets["del_button"], False, False)
        #self.container_widgets["del_account_button_hbox"].pack_start(self.button_widgets["keep_button"], False, False)
        #self.container_widgets["del_account_button_hbox"].pack_start(self.button_widgets["cancel_button"], False, False)
        self.container_widgets["del_main_vbox"].pack_start(self.container_widgets["del_account_button_hbox"], False, False)
        ############################
        # set widget state
        #if not self.permission.get_can_acquire() and not self.permission.get_can_release():
            #self.button_widgets["lock"].set_sensitive(False)
           # self.button_widgets["lock"].set_no_show_all(True)
        self.set_widget_state_with_author()
        ###########################
        # delete account page
        # set icon file
        self.alignment_widgets["set_iconfile"].set(0.5, 0.5, 1, 1)
        self.container_widgets["icon_set_page"] = IconSetPage(self)
        self.alignment_widgets["set_iconfile"].add(self.container_widgets["icon_set_page"])

        self.alignment_widgets["edit_iconfile"].set(0.5, 0.5, 1, 1)
        self.container_widgets["icon_edit_page"] = IconEditPage(self)
        self.alignment_widgets["edit_iconfile"].add(self.container_widgets["icon_edit_page"])

    def __signals_connect(self):
        #self.container_widgets["slider"].connect("expose-event", self.container_expose_cb)
        self.alignment_widgets["main_hbox"].connect("expose-event", self.container_expose_cb)
        self.alignment_widgets["set_iconfile"].connect("expose-event", self.container_expose_cb)
        self.alignment_widgets["edit_iconfile"].connect("expose-event", self.container_expose_cb)
        self.container_widgets["slider"].connect("completed_slide", self.slider_completed_slide_cb)
        self.module_frame.connect("unmap-event", self.slider_hide_cb)

        self.button_widgets["add_account"].connect("clicked", self.add_account_button_clicked)
        self.button_widgets["del_account"].connect("clicked", self.del_account_button_clicked)
        self.button_widgets["account_cancle"].connect("clicked", self.account_cancle_button_clicked)
        self.button_widgets["account_create"].connect("clicked", self.account_create_button_clicked)
        ##self.button_widgets["auto_login"].connect("toggled", self.auto_login_toggled)
        self.button_widgets["nopw_login"].connect("toggled", self.nopw_login_toggled)
        self.button_widgets["disable_account"].connect("clicked", self.account_lock_button_clicked)

        self.view_widgets["account"].connect("select", self.account_treeview_select)
        self.view_widgets["account"].select_first_item()

        self.button_widgets["del_button"].connect("clicked", self.del_delete_user_file_cd, True)
        self.button_widgets["keep_button"].connect("clicked", self.del_delete_user_file_cd, False)
        self.button_widgets["cancel_button"].connect("clicked", self.del_cancel_delete_cb)

        self.button_widgets["account_type"].connect_after("item-selected", self.account_type_item_selected)

        self.button_widgets["lock"].connect("expose-event", self.lock_button_expose)
        self.button_widgets["lock"].connect("clicked", self.lock_button_clicked)

        self.image_widgets["account_icon"].connect("button-press-event", self.icon_file_press_cb)
        self.button_widgets["cancel_set_icon"].connect("clicked", self.cancel_set_icon)
        self.button_widgets["save_edit_icon"].connect("clicked",
            lambda w: self.container_widgets["icon_edit_page"].save_edit_icon())
        self.label_widgets["account_name"].connect("enter-notify-event", self.label_enter_notify_cb, True)
        self.label_widgets["account_name"].connect("leave-notify-event", self.label_leave_notify_cb, True)
        self.label_widgets["account_name"].connect("button-press-event", self.realname_change_press_cb)
        self.label_widgets["passwd_char"].connect("enter-notify-event", self.label_enter_notify_cb)
        self.label_widgets["passwd_char"].connect("leave-notify-event", self.label_leave_notify_cb)
        self.label_widgets["passwd_char"].connect("button-press-event", self.password_change_press_cb)

        #self.label_widgets["backup_check_group"].connect(
            #"button-press-event",
            #lambda w, e:self.button_widgets["backup_check_group"].set_active(
                #not self.button_widgets["backup_check_group"].get_active()))
        #self.label_widgets["backup_check_group_new"].connect(
            #"button-press-event",
            #lambda w, e:self.button_widgets["backup_check_group_new"].set_active(
                #not self.button_widgets["backup_check_group_new"].get_active()))

        self.button_widgets["account_name"].entry.connect("focus-in-event", self.account_name_focus_in_cb)
        self.button_widgets["account_name"].entry.connect(
            "changed", self.account_name_input_changed, self.button_widgets["account_create"])

        self.account_dbus.connect("user-added", self.account_user_added_cb)
        self.account_dbus.connect("user-deleted", self.account_user_deleted_cb)

    ######################################
    # signals callback begin
    # widget signals
    def container_expose_cb(self, widget, event):
        x, y, w, h, d = widget.window.get_geometry()
        cr = widget.window.cairo_create()
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))
        cr.rectangle(x, y, w, h)
        #cr.fill()
        cr.paint()

    def auto_login_toggled(self, button):
        if not self.current_select_user:
            return
        if button.get_data("changed_by_other_app"):
            button.set_data("changed_by_other_app", False)
            return
        try:
            self.current_select_user.set_automatic_login(button.get_active())
            self.set_account_info_error_text("")
            if button.get_active():
                self.__set_status_text(_("Enabled auto-login for %s") % settings.get_user_show_name(self.current_select_user))
            else:
                self.__set_status_text(_("Disabled auto-login for %s") % settings.get_user_show_name(self.current_select_user))
        except Exception, e:
            if isinstance(e, (AccountsPermissionDenied, AccountsUserExists, AccountsFailed, AccountsUserDoesNotExist)):

                button.set_data("changed_by_other_app", True)
                button.set_active(not button.get_active())
                self.set_account_info_error_text(e.msg)

    def nopw_login_toggled(self, button):
        if not self.current_select_user:
            return
        if button.get_data("changed_by_other_app"):
            button.set_data("changed_by_other_app", False)
            return
        try:
            self.set_account_info_error_text("")
            if button.get_active():
                groups = self.current_select_user.get_groups()
                if "nopasswdlogin" not in groups:
                    groups.append("nopasswdlogin")
                self.current_select_user.set_groups(','.join(groups))
                #self.current_select_user.set_password_mode(2)
                self.__set_status_text(_("Enabled passwordless login for %s") % settings.get_user_show_name(self.current_select_user))
            else:
                groups = self.current_select_user.get_groups()
                if "nopasswdlogin" in groups:
                    groups.remove("nopasswdlogin")
                self.current_select_user.set_groups(','.join(groups))
                #self.current_select_user.set_password_mode(0)
                self.__set_status_text(_("Disabled passwordless login for %s") % settings.get_user_show_name(self.current_select_user))
        except Exception, e:
            #if isinstance(e, (AccountsPermissionDenied, AccountsUserExists, AccountsFailed, AccountsUserDoesNotExist)):

                button.set_data("changed_by_other_app", True)
                button.set_active(not button.get_active())
                self.set_account_info_error_text(e.message)

    def account_lock_button_clicked(self, button):
        if not self.current_select_user:
            return
        try:
            is_locked = self.current_select_user.get_locked()
            self.set_account_info_error_text("")
            self.current_select_user.set_locked(not is_locked)
            if is_locked:
                self.__set_status_text(_("Enable %s") % settings.get_user_show_name(self.current_select_user))
                self.button_widgets["disable_account"].set_label(_("Disable"))
            else:
                self.__set_status_text(_("Disable %s") % settings.get_user_show_name(self.current_select_user))
                self.button_widgets["disable_account"].set_label(_("Enable"))
        except Exception, e:
            if isinstance(e, (AccountsPermissionDenied, AccountsUserExists, AccountsFailed, AccountsUserDoesNotExist)):
                self.set_account_info_error_text(e.msg)
        
    ## add account cb >> ##
    def add_account_button_clicked(self, button):
        container_remove_all(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].pack_start(self.alignment_widgets["account_add_vbox"])

        self.button_widgets["account_name"].set_text("")
        self.button_widgets["account_type_new"].set_select_index(0)
        self.label_widgets["account_create_error"].set_text("")
        self.button_widgets["account_create"].set_sensitive(False)
        self.container_widgets["right_vbox"].show_all()
        self.button_widgets["account_name"].entry.grab_focus()
        self.container_widgets["statusbar"].set_buttons([self.button_widgets["account_cancle"], self.button_widgets["account_create"]])
        #button.set_sensitive(False)
        self.container_widgets["button_hbox"].set_sensitive(False)

    def account_cancle_button_clicked(self, button):
        container_remove_all(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].pack_start(self.alignment_widgets["account_info_vbox"], False, False)
        self.container_widgets["right_vbox"].show_all()
        #self.button_widgets["add_account"].set_sensitive(True)
        self.container_widgets["button_hbox"].set_sensitive(True)
        self.container_widgets["statusbar"].set_buttons([self.button_widgets["disable_account"], 
                                                         self.button_widgets["add_account"],
                                                         self.button_widgets["del_account"]])
        self.set_account_info_error_text("")

    def account_create_button_clicked(self, button):
        username = self.button_widgets["account_name"].get_text().lower()
        account_type = self.button_widgets["account_type_new"].get_current_item()[1]
        try:
            if self.account_dbus.create_user(username, username, account_type):
                self.__set_status_text(_("%s has been created") % username)
        except Exception, e:
            if isinstance(e, (AccountsPermissionDenied, AccountsUserExists, AccountsUserDoesNotExist)):
                #self.label_widgets["account_create_error"].set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), e.msg))
                self.set_status_error_text(e.msg)
            elif isinstance(e, (AccountsFailed)):
                self.set_status_error_text(_("The user name is invalid"))
            return
        self.account_cancle_button_clicked(None)

    def account_name_input_changed(self, entry, value, button):
        if entry.get_text():
            if not button.get_sensitive():
                button.set_sensitive(True)
        else:
            if button.get_sensitive():
                button.set_sensitive(False)

    def account_name_focus_in_cb(self, widget, event):
        if not widget.get_text():
            self.__set_status_text(_("User names can only consist of letters, numbers, underscores and begin with a letter"))
    ## << add account cb ##

    ## del account cb >> ##
    def del_cancel_delete_cb(self, button):
        container_remove_all(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].pack_start(self.alignment_widgets["account_info_vbox"], False, False)
        self.container_widgets["right_vbox"].show_all()
        self.container_widgets["statusbar"].set_buttons([self.button_widgets["disable_account"], 
                                                         self.button_widgets["add_account"],
                                                         self.button_widgets["del_account"]])
        #self.set_account_info_error_text("")

    def del_delete_user_file_cd(self, button, del_file):
        try:
            self.container_widgets["del_account_button_hbox"].set_sensitive(False)
            name = settings.get_user_show_name(self.current_del_user)
            uid = self.current_del_user.get_uid()
            self.account_dbus.delete_user(uid, del_file)
            self.__set_status_text(_("%s has been deleted") % name)
            self.del_cancel_delete_cb(button)
        except Exception, e:
            if isinstance(e, (AccountsPermissionDenied, AccountsUserExists, AccountsFailed, AccountsUserDoesNotExist)):
                #self.label_widgets["del_account_error_label"].set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), e.msg))
                self.set_status_error_text(e.msg)
            self.container_widgets["del_account_button_hbox"].set_sensitive(True)
            print e

    def del_account_button_clicked(self, button):
        if not self.current_select_user:
            return
        self.current_del_user = self.current_select_user
        container_remove_all(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].pack_start(self.alignment_widgets["del_main_vbox"])
        show_name = settings.get_user_show_name(self.current_select_user)
        self.label_widgets["del_account_tips"].set_text(
            "<b>%s</b>" % _("Do you want to keep <u>%s</u>'s files?") %
            tools.escape_markup_string(show_name))
        self.label_widgets["del_account_error_label"].set_text("")
        self.container_widgets["del_account_button_hbox"].set_sensitive(True)
        self.container_widgets["right_vbox"].show_all()
        self.container_widgets["statusbar"].set_buttons([self.button_widgets["del_button"], self.button_widgets["keep_button"], self.button_widgets["cancel_button"]])
    ## << del account cb ##

    def account_treeview_select(self, tv, item, row):
        if self.current_passwd_user:
            try:
                self.button_widgets["cancel_change_pswd"].clicked()
            except:
                pass
        self.set_account_info_error_text("")
        self.current_select_user = dbus_obj = item.dbus_obj
        self.current_select_item = item
        #print "treeview current select:'%s', '%s', '%d'" % ( self.current_select_user.get_user_name(), self.current_select_user.get_real_name(), self.current_select_user.get_uid())
        #print "treeitrem:'%s', '%s'" % (item.real_name, item.user_name)
        self.image_widgets["account_icon"].set_from_pixbuf(item.icon)
        if item.real_name:
            self.label_widgets["account_name"].set_text("<b>%s</b>" % item.real_name)
        else:
            self.label_widgets["account_name"].set_text("<b>--</b>")
        self.label_widgets["account_name"].queue_draw()
        #print "treeview account name:", self.label_widgets["account_name"].get_text()
        self.button_widgets["account_type"].set_select_index(item.user_type)
        if dbus_obj.get_locked():
            self.label_widgets["passwd_char"].set_text(_("Account disabled"))
        elif dbus_obj.get_password_mode() == 1:
            self.label_widgets["passwd_char"].set_text(_("To be set at next login"))
        elif dbus_obj.get_password_mode() == 2:
            self.label_widgets["passwd_char"].set_text(_("None"))
        else:
            self.label_widgets["passwd_char"].set_text("****")
        ##if dbus_obj.get_automatic_login() != self.button_widgets["auto_login"].get_active():
            ##self.button_widgets["auto_login"].set_data("changed_by_other_app", True)
            ##self.button_widgets["auto_login"].set_active(dbus_obj.get_automatic_login())
        #nopw_login = (dbus_obj.get_password_mode() == 2)
        nopw_login = ("nopasswdlogin" in dbus_obj.get_groups())
        if self.button_widgets["nopw_login"].get_active() != nopw_login:
            self.button_widgets["nopw_login"].set_data("changed_by_other_app", True)
            self.button_widgets["nopw_login"].set_active(nopw_login)

        if dbus_obj.get_locked():
            self.button_widgets["disable_account"].set_label(_("Enable"))
        else:
            self.button_widgets["disable_account"].set_label(_("Disable"))

        if item.is_myowner:     # is current user that current process' owner
            if self.button_widgets["del_account"].get_sensitive():
                self.button_widgets["del_account"].set_sensitive(False)
            #if not self.image_widgets["account_icon"].get_sensitive():
                #self.image_widgets["account_icon"].set_sensitive(True)
            #if not self.label_widgets["account_name"].get_sensitive():
                #self.label_widgets["account_name"].set_sensitive(True)
            #if not self.label_widgets["passwd_char"].get_sensitive():
                #self.label_widgets["passwd_char"].set_sensitive(True)
            if self.button_widgets["disable_account"].get_sensitive():
                self.button_widgets["disable_account"].set_sensitive(False)
            if self.button_widgets["account_type"].get_sensitive():
                self.button_widgets["account_type"].set_sensitive(False)
        else:
            if not self.button_widgets["del_account"].get_sensitive():
                self.button_widgets["del_account"].set_sensitive(True)
            #if self.image_widgets["account_icon"].get_sensitive():
                #self.image_widgets["account_icon"].set_sensitive(False)
            #if self.label_widgets["account_name"].get_sensitive():
                #self.label_widgets["account_name"].set_sensitive(False)
            #if self.label_widgets["passwd_char"].get_sensitive():
                #self.label_widgets["passwd_char"].set_sensitive(False)
            if not self.button_widgets["disable_account"].get_sensitive():
                self.button_widgets["disable_account"].set_sensitive(True)
            if not self.button_widgets["account_type"].get_sensitive():
                self.button_widgets["account_type"].set_sensitive(True)

    def lock_button_expose(self, button, event):
        cr = button.window.cairo_create()
        x, y, w, h = button.allocation
        if button.get_data("unlocked"):
            cr.set_source_pixbuf(self.image_widgets["unlock_pixbuf"].get_pixbuf(), x, y)
            cr.paint()
        else:
            cr.set_source_pixbuf(self.image_widgets["lock_pixbuf"].get_pixbuf(), x, y)
            cr.paint()
        if not button.get_sensitive():
            cr.set_source_rgba(1, 1, 1, 0.6)
            cr.rectangle(x, y, w, h)
            cr.fill()
            cr.paint()
        return True

    def lock_button_clicked(self, button):
        if self.get_authorized():
            if self.permission.release():
                button.set_data("unlocked", False)
        else:
            if self.permission.acquire():
                button.set_data("unlocked", True)
        self.set_widget_state_with_author()

    def account_type_item_selected(self, combo_box, item_content, item_value, item_index):
        if not self.current_select_user:
            return
        try:
            self.current_select_user.set_account_type(item_value)
            self.set_account_info_error_text("")
            self.__set_status_text(_("%s's account type has been set as %s") %( settings.get_user_show_name(self.current_select_user), item_content))
        except Exception, e:
            if isinstance(e, (AccountsPermissionDenied, AccountsUserExists, AccountsFailed, AccountsUserDoesNotExist)):
                if self.current_select_item:
                    self.button_widgets["account_type"].set_select_index(self.current_select_item.user_type)
                self.set_account_info_error_text(e.msg)

    def label_enter_notify_cb(self, widget, event, is_realname=False):
        if not self.current_select_item:
            return
        if is_realname:
            realname = self.current_select_item.real_name
            if realname:
                widget.set_text("<u><b>%s</b></u>" % realname)
            else:
                widget.set_text("<u><b>%s</b></u>" % "--")
        else:
            if widget.window:
                widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND2))
            ##widget.set_text("  %s" % widget.get_text())
            p_rect = widget.get_parent().allocation
            rect = widget.allocation
            cr = widget.get_parent().window.cairo_create()
            y = p_rect.y + (p_rect.height - WIDGET_HEIGHT) / 2
            with cairo_disable_antialias(cr):
                cr.set_line_width(1)
                frame_color = ui_theme.get_color("combo_entry_frame")
                cr.set_source_rgb(*color_hex_to_cairo(frame_color.get_color()))
                cr.rectangle(rect.x, y, COMBO_WIDTH, WIDGET_HEIGHT)
                cr.stroke()

    def label_leave_notify_cb(self, widget, event, is_realname=False):
        if not self.current_select_user:
            return
        if is_realname:
            realname = self.current_select_item.real_name
            if realname:
                widget.set_text("<b>%s</b>" % realname)
            else:
                widget.set_text("<b>%s</b>" % "--")
        else:
            if widget.window:
                widget.window.set_cursor(None)
            self.container_widgets["account_info_table"].queue_draw()
            ##widget.set_text("%s" % pango.parse_markup(widget.get_text().strip())[1])

    def realname_change_press_cb(self, widget, event):
        if not self.current_select_user:
            return

        def change_account_name(widget, *args):
            #print "current select:", self.current_select_user.get_user_name()
            if self.label_widgets["account_name"].get_parent():
                return
            text = widget.get_text()
            self.container_widgets["account_info_hbox"].pack_start(
                self.label_widgets["account_name"])
            self.container_widgets["account_info_hbox"].reorder_child(
                self.label_widgets["account_name"], 0)
            if text != self.current_select_user.get_real_name():
                #self.label_widgets["account_name"].set_text("<b>%s</b>" % tools.escape_markup_string(text))
                try:
                    self.current_select_user.set_real_name(text)
                    self.set_account_info_error_text("")
                except Exception, e:
                    if isinstance(e, (AccountsPermissionDenied, AccountsUserExists, AccountsFailed, AccountsUserDoesNotExist)):
                        self.set_account_info_error_text(e.msg)
            align.destroy()
            self.container_widgets["right_vbox"].queue_draw()

        self.set_account_info_error_text("")
        self.container_widgets["account_info_hbox"].remove(self.label_widgets["account_name"])
        #text = pango.parse_markup(widget.get_text())[1]
        text = self.current_select_user.get_real_name()
        align = gtk.Alignment()
        align.set(0.0, 0.5, 0, 0)
        align.set_padding(8, 0, 0, 65)
        input_entry = InputEntry(text)
        input_entry.entry.check_text = tools.entry_check_account_name
        input_entry.set_size(COMBO_WIDTH, WIDGET_HEIGHT)
        input_entry.connect("expose-event", lambda w, e: input_entry.entry.grab_focus())
        input_entry.entry.connect("press-return", change_account_name)
        input_entry.entry.connect("focus-out-event", change_account_name)
        align.add(input_entry)
        align.show_all()
        self.container_widgets["account_info_hbox"].pack_start(align)
        self.container_widgets["account_info_hbox"].reorder_child(align, 0)
        self.container_widgets["right_vbox"].queue_draw()

    ## change password >> ##
    def password_change_press_cb(self, widget, event):
        if not self.current_select_user:
            return
        if widget.window:
            widget.window.set_cursor(None)
        ##widget.set_text("%s" % pango.parse_markup(widget.get_text().strip())[1])
        self.current_passwd_user = self.current_select_user
        passwd_align = self.label_widgets["passwd"].get_parent()
        passwd_char_align = self.label_widgets["passwd_char"].get_parent()
        self.container_widgets["account_info_table"].remove(passwd_align)
        self.container_widgets["account_info_table"].remove(passwd_char_align)
        left_vbox = gtk.VBox(False)
        right_vbox = gtk.VBox(False)
        button_vbox = gtk.VBox(False)
        button_hbox = gtk.HBox(False)
        self.container_widgets["account_info_table"].attach(left_vbox, 0, 1, 4, 5, 4)
        self.container_widgets["account_info_table"].attach(right_vbox, 1, 2, 4, 5, 4)
        self.container_widgets["account_info_table"].attach(button_vbox, 0, 2, 5, 6, 4)

        is_input_empty = {
            self.CH_PASSWD_CURRENT_PSWD: True,
            self.CH_PASSWD_NEW_PSWD: True,
            self.CH_PASSWD_CONFIRM_PSWD: True}
        is_myown = settings.check_is_myown(self.current_passwd_user.get_uid())
        if self.current_passwd_user.get_password_mode() == 2:
            is_myown = False

        label1 = Label(_("Current password"), enable_select=False,
                text_x_align=ALIGN_END, enable_double_click=False, fixed_width=LABEL_WIDTH)
        label2 = Label(_("New password"), enable_select=False,
                text_x_align=ALIGN_END, enable_double_click=False, fixed_width=LABEL_WIDTH)
        label3 = Label(_("Confirm new password"), enable_select=False,
                text_x_align=ALIGN_END, enable_double_click=False, fixed_width=LABEL_WIDTH)

        current_pswd_input = PasswordEntry()
        current_pswd_input.entry.set_name("current")
        new_pswd_input = PasswordEntry()
        new_pswd_input.entry.set_name("new")
        confirm_pswd_input = PasswordEntry()
        confirm_pswd_input.entry.set_name("confirm")
        confirm_pswd_input.entry.check_text = self.check_passwd_text
        new_pswd_input.entry.check_text = self.check_passwd_text
        current_pswd_input.set_size(COMBO_WIDTH, WIDGET_HEIGHT)
        new_pswd_input.set_size(COMBO_WIDTH, WIDGET_HEIGHT)
        confirm_pswd_input.set_size(COMBO_WIDTH, WIDGET_HEIGHT)
        show_pswd_check = CheckButton(_("Show password"), padding_x=0)

        if is_myown:
            left_vbox.pack_start(self.__make_align(label1, xalign=1.0, width=LABEL_WIDTH), False, False)
            right_vbox.pack_start(self.__make_align(current_pswd_input), False, False)

        left_vbox.pack_start(self.__make_align(label2, xalign=1.0, width=LABEL_WIDTH), False, False)
        left_vbox.pack_start(self.__make_align(label3, xalign=1.0, width=LABEL_WIDTH), False, False)

        right_vbox.pack_start(self.__make_align(new_pswd_input), False, False)
        right_vbox.pack_start(self.__make_align(confirm_pswd_input), False, False)
        right_vbox.pack_start(self.__make_align(show_pswd_check), False, False)

        self.button_widgets["cancel_change_pswd"] = cancel_button = Button(_("Cancel"))
        change_button = Button(_("Change"))
        change_button.set_sensitive(False)
        button_hbox.set_spacing(WIDGET_SPACING)

        ##error_label = self.label_widgets["account_info_error"]
        self.set_account_info_error_text("")

        button_vbox.pack_start(self.__make_align(button_hbox, xalign=1.0, width=LABEL_WIDTH+COMBO_WIDTH+WIDGET_SPACING), False, False)

        show_pswd_check.connect("toggled", self.show_input_password, new_pswd_input, confirm_pswd_input)
        cancel_button.connect("clicked", self.cancel_change_password, passwd_align, passwd_char_align,
                              left_vbox, right_vbox, button_vbox, change_button)
        change_button.connect("clicked", self.change_user_password, 
                              (current_pswd_input, new_pswd_input, confirm_pswd_input), is_myown)
        current_pswd_input.entry.connect("changed", self.password_input_changed, 
                                         (current_pswd_input, new_pswd_input, confirm_pswd_input),
                                         change_button, is_myown, is_input_empty, self.CH_PASSWD_CURRENT_PSWD)
        new_pswd_input.entry.connect("changed", self.password_input_changed, 
                                     (current_pswd_input, new_pswd_input, confirm_pswd_input),
                                     change_button, is_myown, is_input_empty, self.CH_PASSWD_NEW_PSWD, 6)
        confirm_pswd_input.entry.connect("changed", self.password_input_changed,
                                         (current_pswd_input, new_pswd_input, confirm_pswd_input),
                                         change_button, is_myown, is_input_empty, self.CH_PASSWD_CONFIRM_PSWD, 6)

        self.container_widgets["account_info_table"].show_all()
        self.container_widgets["right_vbox"].queue_draw()
        self.statusbar_buttons_bak = self.container_widgets["statusbar"].get_buttons()
        self.container_widgets["statusbar"].set_buttons([cancel_button, change_button])

    def show_input_password(self, button, new_pswd_input, confirm_pswd_input):
        new_pswd_input.show_password(button.get_active())
        confirm_pswd_input.show_password(button.get_active())

    def password_input_changed(self, entry, text, entry_widgets, change_button, is_myown, is_input_empty, variety, atleast=0):
        (current_pswd_input, new_pswd_input, confirm_pswd_input) = entry_widgets
        error_text = ""
        # 检测密码长度
        #if not text or len(text)<atleast or len(text)>16:
        if not text:
            is_input_empty[variety] = True
        else:
            is_input_empty[variety] = False
            new_pswd = new_pswd_input.entry.get_text()
            confirm_pswd = confirm_pswd_input.entry.get_text()
            if confirm_pswd and new_pswd != confirm_pswd:
                error_text = _("Password did not match.")
        if (is_myown and is_input_empty[self.CH_PASSWD_CURRENT_PSWD]) or\
                is_input_empty[self.CH_PASSWD_NEW_PSWD] or\
                is_input_empty[self.CH_PASSWD_CONFIRM_PSWD] or\
                new_pswd_input.entry.get_text() != confirm_pswd_input.entry.get_text():
            change_button.set_sensitive(False)
            self.set_status_error_text(error_text)
        else:
            change_button.set_sensitive(True)
            self.set_status_error_text("")

    def change_user_password_thread(self, new_pswd, old_pswd, button):
        print "in thread........."
        try:
            b = self.account_dbus.modify_user_passwd(new_pswd, self.current_passwd_user.get_user_name(), old_pswd)
            if b != 0:
                error_msg = _("password unchanged")
                if b == 10:
                    error_msg = _("authentication token manipulation error")
                if b == -2:
                    error_msg = _("new and old password are too similar")
                gtk.gdk.threads_enter()
                #error_label.set_text("<span foreground='red'>%s%s</span>" % (
                    #_("Error:"), error_msg))
                self.set_status_error_text(error_msg)
                self.container_widgets["main_hbox"].set_sensitive(True)
                button.set_sensitive(True)
                self.button_widgets["cancel_change_pswd"].set_sensitive(True)
                gtk.gdk.threads_leave()
            else:
                gtk.gdk.threads_enter()
                button.set_sensitive(True)
                self.button_widgets["cancel_change_pswd"].set_sensitive(True)
                self.button_widgets["cancel_change_pswd"].clicked()
                self.__set_status_text(_("%s's password has been changed") % settings.get_user_show_name(self.current_select_user))
                gtk.gdk.threads_leave()
            print "thread finish......"
        except Exception, e:
            if not isinstance(e, (TIMEOUT, EOF)):
                error_msg = e.message
            else:
                error_msg = _("password unchanged")
            gtk.gdk.threads_enter()
            #error_label.set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), error_msg))
            self.set_status_error_text(error_msg)
            self.container_widgets["main_hbox"].set_sensitive(True)
            button.set_sensitive(True)
            self.button_widgets["cancel_change_pswd"].set_sensitive(True)
            gtk.gdk.threads_leave()
        self.mutex.release()

    def change_user_password(self, button, entry_widgets, is_myown):
        (current_pswd_input, new_pswd_input, confirm_pswd_input) = entry_widgets
        self.container_widgets["main_hbox"].set_sensitive(False)
        button.set_sensitive(False)
        self.button_widgets["cancel_change_pswd"].set_sensitive(False)
        new_pswd = new_pswd_input.entry.get_text()
        confirm_pswd = confirm_pswd_input.entry.get_text()
        if is_myown:
            old_pswd = current_pswd_input.entry.get_text()
        else:
            old_pswd = " "
        if new_pswd != confirm_pswd:
            self.container_widgets["main_hbox"].set_sensitive(True)
            button.set_sensitive(True)
            self.button_widgets["cancel_change_pswd"].set_sensitive(True)
            return
        # to change myowner passwd, use pexpect.
        # else use AccountsService dbus.
        if getpass.getuser() == self.current_passwd_user.get_user_name():
            self.mutex.acquire()
            t = threading.Thread(target=self.change_user_password_thread,
                                 args=(new_pswd, old_pswd, button))
            t.setDaemon(True)
            t.start()
        else:
            try:
                self.current_passwd_user.set_password(crypt.crypt(new_pswd, '$6$deepin$'))
            except Exception, e:
                if 'nopasswdlogin' not in e.msg:
                    self.set_status_error_text(e.msg)
                    self.container_widgets["main_hbox"].set_sensitive(True)
                    button.set_sensitive(True)
                    self.button_widgets["cancel_change_pswd"].set_sensitive(True)
                    return
            button.set_sensitive(True)
            self.button_widgets["cancel_change_pswd"].set_sensitive(True)
            self.button_widgets["cancel_change_pswd"].clicked()
            self.__set_status_text(_("%s's password has been changed") % settings.get_user_show_name(self.current_select_user))

    def cancel_change_password(self, button, passwd_align, passwd_char_align, *del_widgets):
        for w in del_widgets:
            w.destroy()
        button.destroy()
        self.container_widgets["account_info_table"].attach(passwd_align, 0, 1, 3, 4, 4)
        self.container_widgets["account_info_table"].attach(passwd_char_align, 1, 2, 3, 4, 4)
        self.container_widgets["account_info_table"].show_all()
        self.container_widgets["main_hbox"].set_sensitive(True)
        self.set_account_info_error_text("")
        self.current_passwd_user = None
        self.container_widgets["statusbar"].set_buttons(self.statusbar_buttons_bak)
        self.statusbar_buttons_bak = []

    def check_passwd_text(self, text):
        return len(text) <= 16
    ## << change passowrd ##

    ## set icon >> ##
    def icon_file_press_cb(self, widget, event):
        if not self.current_select_user:
            return
        self.set_account_info_error_text("")
        self.current_set_user = self.current_select_user
        self.container_widgets["icon_set_page"].refresh()
        self.alignment_widgets["set_iconfile"].show_all()
        self.set_to_page(self.alignment_widgets["set_iconfile"], "right")
        self.module_frame.send_submodule_crumb(2, _("Set Picture"))

    def cancel_set_icon(self, button):
        self.container_widgets["icon_edit_page"].stop_camera()
        self.container_widgets["icon_edit_page"].draw_area.panel.hide_panel()
        self.set_to_page(self.alignment_widgets["main_hbox"], "left")
        self.change_crumb(1)
    ## << set icon ##

    # dbus signals
    def user_info_changed_cb(self, user, item):
        icon_file = user.get_icon_file()
        if os.path.exists(icon_file):
            try:
                icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                    icon_file).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
            except:
                icon_pixbuf = self.image_widgets["default_icon"].get_pixbuf()
        else:
            icon_pixbuf = self.image_widgets["default_icon"].get_pixbuf()
        item.icon = icon_pixbuf
        item.user_name = tools.escape_markup_string(user.get_user_name())
        item.real_name = tools.escape_markup_string(user.get_real_name())
        item.user_type = user.get_account_type()
        if item.redraw_request_callback:
            item.redraw_request_callback(item)
        if self.current_select_user == user:
            self.image_widgets["account_icon"].set_from_pixbuf(item.icon)
            if item.real_name:
                self.label_widgets["account_name"].set_text("<b>%s</b>" % item.real_name)
            else:
                self.label_widgets["account_name"].set_text("<b>--</b>")
            self.button_widgets["account_type"].set_select_index(item.user_type)
            if user.get_locked():
                self.label_widgets["passwd_char"].set_text(_("Account disabled"))
            elif user.get_password_mode() == 1:
                self.label_widgets["passwd_char"].set_text(_("To be set at next login"))
            elif user.get_password_mode() == 2:
                self.label_widgets["passwd_char"].set_text(_("None"))
            else:
                self.label_widgets["passwd_char"].set_text("****")
            ##if user.get_automatic_login() != self.button_widgets["auto_login"].get_active():
                ##self.button_widgets["auto_login"].set_data("changed_by_other_app", True)
                ##self.button_widgets["auto_login"].set_active(user.get_automatic_login())
            #nopw_login = (user.get_password_mode() == 2)
            nopw_login = ("nopasswdlogin" in user.get_groups())
            if self.button_widgets["nopw_login"].get_active() != nopw_login:
                self.button_widgets["nopw_login"].set_data("changed_by_other_app", True)
                self.button_widgets["nopw_login"].set_active(nopw_login)
            if user.get_locked():
                self.button_widgets["disable_account"].set_label(_("Enable"))
            else:
                self.button_widgets["disable_account"].set_label(_("Disable"))

    def account_user_set_random_icon(self, user_obj):
        if self.get_authorized():
            try:
                face_dir = '/var/lib/AccountsService/icons'
                if not os.path.exists(face_dir):
                    return False
                inital_list = ['001.jpg', '002.jpg', '003.jpg', '004.jpg', '005.jpg',
                               '006.jpg', '007.jpg', '008.jpg', '009.jpg', '010.jpg',
                               '011.jpg', '012.jpg', '013.jpg', '014.jpg', '015.jpg',
                               '016.jpg', '017.jpg', '018.jpg', '019.jpg', '020.jpg']
                pic_list = []
                for i in inital_list:
                    if os.path.exists("%s/%s" % (face_dir, i)):
                        pic_list.append(i)
                if not pic_list:
                    return False
                total_pic = len(pic_list)
                rand_pic = randint(0, total_pic-1)
                filename = "%s/%s" % (face_dir, pic_list[rand_pic])
                icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                    filename).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
                user_obj.set_icon_file(filename)
                return icon_pixbuf
            except Exception, e:
                print "random:", e
                pass
        return False

    def account_user_added_cb(self, account_obj, user_path):
        print "%s added" % user_path
        if not user_path in self.account_dbus.list_cached_users():
            return
        user_info = settings.get_user_info(user_path)
        icon_file = user_info[1]
        if os.path.exists(icon_file):
            try:
                icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                    icon_file).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
            except:
                icon_pixbuf = self.image_widgets["default_icon"].get_pixbuf()
        else:       # if this user has not icon, then set a random icon
            icon_pixbuf = self.account_user_set_random_icon(user_info[0])
            if not icon_pixbuf:
                icon_pixbuf = self.image_widgets["default_icon"].get_pixbuf()
        user_item = TreeItem(icon_pixbuf, tools.escape_markup_string(user_info[2]),
                             tools.escape_markup_string(user_info[3]),
                             user_info[4], user_info[0])
        self.view_widgets["account"].add_items([user_item])

    def account_user_deleted_cb(self, account_obj, user_path):
        print "%s deleted" % user_path
        i = 0
        for item in self.view_widgets["account"].visible_items:
            if user_path == item.dbus_obj.object_path:
                self.view_widgets["account"].delete_items([item])
                # if delete current selected row, then changed the selected row
                if self.current_select_user == item.dbus_obj:
                    if i >= len(self.view_widgets["account"].visible_items):
                        i = len(self.view_widgets["account"].visible_items) - 1
                    if i >= 0:
                        self.view_widgets["account"].set_select_rows([i])
                break
            i += 1
        # if it is in del_page, then go back
        if self.alignment_widgets["del_main_vbox"] in self.container_widgets["right_vbox"].get_children():
            self.del_cancel_delete_cb(None)

    # signals callback end
    ######################################

    def get_user_list_treeitem(self):
        '''
        get TreeItems of user
        @return: a list contain TreeItem of account
        '''
        user_list = settings.get_user_list()
        user_items = []
        for user in user_list:
            icon_file = user.get_icon_file()
            if os.path.exists(icon_file):
                try:
                    icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                        icon_file).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
                except:
                    icon_pixbuf = self.image_widgets["default_icon"].get_pixbuf()
            else:
                icon_pixbuf = self.image_widgets["default_icon"].get_pixbuf()
            if settings.check_is_myown(user.get_uid()):
                item = TreeItem(icon_pixbuf, tools.escape_markup_string(user.get_real_name()),
                                tools.escape_markup_string(user.get_user_name()),
                                user.get_account_type(), user, True)
                user_items.insert(0, item)
            else:
                item = TreeItem(icon_pixbuf, tools.escape_markup_string(user.get_real_name()),
                                tools.escape_markup_string(user.get_user_name()),
                                user.get_account_type(), user)
                user_items.append(item)
            user.connect("changed", self.user_info_changed_cb, item)
            for compare_user in user_list:
                if user == compare_user:
                    continue
                if user.get_real_name() == compare_user.get_real_name():
                    item.is_unique = False
                    break
        if user_items:
            user_items[0].is_head = True
        return user_items

    def set_widget_state_with_author(self):
        ''' set widgets sensitive if it has authorized, else insensitive '''
        authorized = self.get_authorized()
        self.button_widgets["lock"].set_data("unlocked", authorized)
        #self.container_widgets["button_hbox"].set_sensitive(authorized)
        self.button_widgets["add_account"].set_sensitive(authorized)
        self.button_widgets["account_type"].set_sensitive(authorized)
        ##self.button_widgets["auto_login"].set_sensitive(authorized)
        self.button_widgets["nopw_login"].set_sensitive(authorized)
        self.container_widgets["check_button_table"].set_sensitive(authorized)
        if self.current_select_user and not settings.check_is_myown(self.current_select_user.get_uid()):
            self.image_widgets["account_icon"].set_sensitive(authorized)
            self.label_widgets["account_name"].set_sensitive(authorized)
            self.label_widgets["passwd_char"].set_sensitive(authorized)
            self.button_widgets["del_account"].set_sensitive(authorized)

    def get_authorized(self):
        '''
        @return: True if current process has been authorized, else False
        '''
        #return self.permission.get_allowed()
        return True

    def __make_align(self, widget=None, xalign=0.0, yalign=0.5, xscale=0.0,
                     yscale=0.0, padding_top=0, padding_bottom=0, padding_left=0,
                     padding_right=0, width=-1, height=CONTAINNER_HEIGHT):
        return tools.make_align(widget, xalign, yalign, xscale,
                                yscale, padding_top, padding_bottom, padding_left,
                                padding_right, width, height)

    def set_account_info_error_text(self, text=""):
        #if text:
            #self.label_widgets["account_info_error"].set_text(
                #"<span foreground='red'>%s%s</span>" % (_("Error:"), text))
        #else:
            #self.label_widgets["account_info_error"].set_text("")
        self.set_status_error_text(text)

    def set_status_error_text(self, text=""):
        if text:
            error_text = "%s%s" % (_("Error:"), text)
        else:
            error_text = text
        self.__set_status_text(error_text)

    def __set_status_text(self, text):
        self.container_widgets["statusbar"].set_text(text)

    def change_crumb(self, crumb_index):
        self.module_frame.send_message("change_crumb", crumb_index)

    def crumb_clicked(self, index, text):
        crumb_list = [self.alignment_widgets["main_hbox"],
                      self.alignment_widgets["set_iconfile"],
                      self.alignment_widgets["edit_iconfile"]]
        if index < 3:
            self.container_widgets["icon_edit_page"].stop_camera()
            self.container_widgets["icon_edit_page"].draw_area.panel.hide_panel()
        self.set_to_page(crumb_list[index-1], "left")

    def slider_completed_slide_cb(self, widget):
        if self.__is_first_show:
            self.__is_first_show = False
            widget.set_to_page(self.alignment_widgets["main_hbox"])

    def slider_hide_cb(self, widget, event):
        #self.container_widgets["icon_edit_page"].draw_area.panel.hide()
        self.container_widgets["icon_edit_page"].draw_area.panel.hide_panel()

    def set_to_page(self, widget, direction):
        pre_widget = self.container_widgets["slider"].active_widget
        self.statusbar_buttons[pre_widget.get_name()] = self.container_widgets["statusbar"].get_buttons()
        self.container_widgets["slider"].slide_to_page(widget, direction)

        if widget.get_name() in self.statusbar_buttons:
            button_list = self.statusbar_buttons[widget.get_name()]
        else:
            button_list = []
        self.container_widgets["statusbar"].set_buttons(button_list)

    def app_focus_changed(self, tp):
        if tp == "o":
            self.container_widgets["icon_edit_page"].draw_area.panel.hide_panel()
            self.container_widgets["icon_edit_page"].draw_area.camera_focus_flag = False
        elif tp == "i":
            self.container_widgets["icon_edit_page"].draw_area.camera_focus_flag = True

if __name__ == '__main__':
    gtk.gdk.threads_init()
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    account_settings = AccountSetting(module_frame)

    module_frame.add(account_settings.container_widgets["main_vbox"])
    module_frame.connect("realize", lambda w: account_settings.container_widgets["slider"].set_to_page(gtk.VBox()))
    #module_frame.connect("realize", lambda w: account_settings.container_widgets["slider"].set_to_page(
        #account_settings.alignment_widgets["main_hbox"]))
    if len(sys.argv) > 1:
        print "module_uid:", sys.argv[1]

    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "click_crumb":
            (crumb_index, crumb_label) = message_content
            account_settings.crumb_clicked(crumb_index, crumb_label)
        elif message_type == "show_again":
            print "DEBUG show_again module_uid", message_content
            account_settings.set_to_page(account_settings.alignment_widgets["main_hbox"], None)
            module_frame.send_module_info()
        elif message_type == "focus_changed":
            account_settings.app_focus_changed(message_content)

    module_frame.module_message_handler = message_handler

    module_frame.run()
