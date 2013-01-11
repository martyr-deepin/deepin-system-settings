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
from theme import app_theme

import settings
from nls import _
from icon_button import IconButton
from dtk.ui.label import Label
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.button import CheckButton, Button, OffButton
from dtk.ui.new_entry import InputEntry, PasswordEntry
from dtk.ui.combo import ComboBox
from dtk.ui.new_slider import HSlider
from dtk.ui.utils import container_remove_all, color_hex_to_cairo, cairo_disable_antialias
from treeitem import MyTreeView as TreeView
from treeitem import MyTreeItem as TreeItem
from utils import AccountsPermissionDenied, AccountsUserDoesNotExist, AccountsUserExists, AccountsFailed
import gtk
import pango
import threading
from module_frame import ModuleFrame
from constant import *
from pexpect import TIMEOUT, EOF
from glib import markup_escape_text

MODULE_NAME = "account"
COMBO_WIDTH = 165

class AccountSetting(object):
    '''account setting'''
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
        
        self.current_select_user = None
        self.current_select_item = None

        self.__create_widget()
        self.__adjust_widget()
        self.__signals_connect()
    
    def __create_widget(self):
        #####################################
        # account list page
        # label 
        self.label_widgets["account_name"] = Label("", label_width=230, enable_select=False)
        self.label_widgets["account"] = Label(_("Account type"))
        self.label_widgets["passwd"] = Label(_("Password"))
        self.label_widgets["passwd_char"] = Label("****", label_width=COMBO_WIDTH, enable_select=False)
        self.label_widgets["auto_login"] = Label(_("Automatic Login"))
        self.label_widgets["deepin_account_tips"] = Label(_("Deepin Account"))
        self.label_widgets["deepin_account"] = Label(_("Unbound"))
        self.label_widgets["account_name_new"] = Label(_("Account Name"))
        self.label_widgets["account_type_new"] = Label(_("Account type"))
        self.label_widgets["deepin_account_tips_new"] = Label(_("Deepin Account"))
        self.label_widgets["deepin_account_new"] = Label(_("Unbound"))
        self.label_widgets["account_create_error"] = Label("", wrap_width=360, enable_select=False)
        # image
        self.image_widgets["lock_pixbuf"] = app_theme.get_pixbuf("lock/lock.png")
        self.image_widgets["unlock_pixbuf"] = app_theme.get_pixbuf("lock/unlock.png")
        self.image_widgets["default_icon"] = app_theme.get_pixbuf("%s/icon.png" % MODULE_NAME)
        self.image_widgets["account_icon"] = IconButton(self.image_widgets["default_icon"].get_pixbuf())
        # button
        self.button_widgets["account_name"] = InputEntry()
        self.button_widgets["lock"] = gtk.Button()
        self.button_widgets["account_type"] = ComboBox([(_('Standard'), 0), (_('Administrator'), 1)], max_width=COMBO_WIDTH)
        #self.button_widgets["auto_login"] = gtk.ToggleButton()
        self.button_widgets["auto_login"] = OffButton()
        self.button_widgets["passwd"] = InputEntry()
        self.button_widgets["net_access_check"] = CheckButton(_("网络访问权限"), padding_x=0)
        self.button_widgets["disk_readonly_check"] = CheckButton(_("磁盘操作权限只读"), padding_x=0)
        self.button_widgets["mountable_check"] = CheckButton(_("可加载移动设备"), padding_x=0)
        self.button_widgets["disk_readwrite_check"] = CheckButton(_("磁盘操作权限完全"), padding_x=0)

        self.button_widgets["backup_check_group"] = CheckButton("", padding_x=0)
        self.label_widgets["backup_check_group"] = Label(_("自动备份个人偏好设置并上传到云端，重新装机或在另一台计算机登录深度系统时您不再需要设置偏好。"), wrap_width=360, enable_select=False)
        self.alignment_widgets["backup_check_group"] = gtk.Alignment()
        self.container_widgets["backup_check_group_hbox"] = gtk.HBox(False)
        self.container_widgets["backup_check_group_vbox"] = gtk.VBox(False)

        self.button_widgets["binding"] = Label(_("提示：此功能需要绑定<span foreground=\"blue\" underline=\"single\">深度帐号</span>。"), enable_select=False)
        self.button_widgets["add_account"] = Button(_("Add"))
        self.button_widgets["del_account"] = Button(_("Delete"))
        self.button_widgets["account_create"] = Button(_("Create"))
        self.button_widgets["account_cancle"] = Button(_("Cancel"))
        self.button_widgets["account_type_new"] = ComboBox([(_('Standard'), 0), (_('Administrator'), 1)], max_width=125)
        self.button_widgets["net_access_check_new"] = CheckButton(_("网络访问权限"), padding_x=0)
        self.button_widgets["disk_readonly_check_new"] = CheckButton(_("磁盘操作权限只读"), padding_x=0)
        self.button_widgets["mountable_check_new"] = CheckButton(_("可加载移动设备"), padding_x=0)
        self.button_widgets["disk_readwrite_check_new"] = CheckButton(_("磁盘操作权限完全"), padding_x=0)

        self.button_widgets["backup_check_group_new"] = CheckButton("", padding_x=0)
        self.label_widgets["backup_check_group_new"] = Label(_("自动备份个人偏好设置并上传到云端，重新装机或在另一台计算机登录深度系统时您不再需要设置偏好。"), wrap_width=360, enable_select=False)
        self.alignment_widgets["backup_check_group_new"] = gtk.Alignment()
        self.container_widgets["backup_check_group_hbox_new"] = gtk.HBox(False)
        self.container_widgets["backup_check_group_vbox_new"] = gtk.VBox(False)

        self.button_widgets["binding_new"] = Label(_("提示：此功能需要绑定<span foreground=\"blue\" underline=\"single\">深度帐号</span>。"), enable_select=False)
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
        self.alignment_widgets["account_add_vbox"] = gtk.Alignment()
        self.alignment_widgets["button_hbox_new"] = gtk.Alignment()
        #####################################
        # change password page
        self.alignment_widgets["change_pswd"] = gtk.Alignment()
        self.container_widgets["change_pswd_main_vbox"] = gtk.VBox(False)
        #####################################
        # delete account page
        self.alignment_widgets["delete_account"] = gtk.Alignment()
        self.container_widgets["del_main_vbox"] = gtk.VBox(False)
        self.label_widgets["del_account_tips"] = Label("", wrap_width=400, enable_select=False)
        self.label_widgets["del_account_tips2"] = Label(
            _("It is possible to keep the home directory when deleting a user account."),
            wrap_width=400, enable_select=False)
        self.label_widgets["del_account_error_label"] = Label("", wrap_width=390, enable_select=False)
        self.button_widgets["del_button"] = Button(_("Delete Files"))
        self.button_widgets["keep_button"] = Button(_("Keep Files"))
        self.button_widgets["cancel_button"] = Button(_("Cancel"))
        self.container_widgets["del_account_button_hbox"] = gtk.HBox(False)
        #####################################
        # set icon page
        self.alignment_widgets["set_iconfile"] = gtk.Alignment()
        self.container_widgets["set_iconfile_main_vbox"] = gtk.VBox(False)
    
    def __adjust_widget(self):
        self.container_widgets["slider"].append_page(self.alignment_widgets["main_hbox"])
        self.container_widgets["slider"].append_page(self.alignment_widgets["change_pswd"])
        self.container_widgets["slider"].append_page(self.alignment_widgets["set_iconfile"])
        #self.container_widgets["slider"].append_page(self.alignment_widgets["delete_account"])
        
        self.alignment_widgets["change_pswd"].set_padding(TEXT_WINDOW_TOP_PADDING, 10, TEXT_WINDOW_LEFT_PADDING, TIP_BOX_WIDTH)
        #self.alignment_widgets["delete_account"].set_padding(TEXT_WINDOW_TOP_PADDING, 10, TEXT_WINDOW_LEFT_PADDING, TIP_BOX_WIDTH)
        self.alignment_widgets["set_iconfile"].set_padding(TEXT_WINDOW_TOP_PADDING, 10, TEXT_WINDOW_LEFT_PADDING, 20)

        self.alignment_widgets["main_hbox"].set(0.0, 0.0, 1, 1)
        self.alignment_widgets["main_hbox"].set_padding(FRAME_TOP_PADDING, 10, 0, FRAME_LEFT_PADDING)
        self.alignment_widgets["main_hbox"].add(self.container_widgets["main_hbox"])
        self.container_widgets["main_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["left_vbox"], False, False)
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["right_vbox"])
        self.alignment_widgets["left_vbox"].add(self.container_widgets["left_vbox"])
        self.alignment_widgets["left_vbox"].set(0, 0, 1, 1)
        #self.alignment_widgets["left_vbox"].set_padding(1, 1, 1, 1)
        self.alignment_widgets["right_vbox"].add(self.container_widgets["right_vbox"])
        self.container_widgets["left_vbox"].set_size_request(275, -1)
        #self.view_widgets["account"].set_size_request(325, 370)
        ##############################
        # accounts list page
        self.container_widgets["left_vbox"].pack_start(self.view_widgets["account"])
        self.container_widgets["left_vbox"].pack_start(self.alignment_widgets["button_hbox"], False, False)
        self.alignment_widgets["button_hbox"].add(self.container_widgets["button_hbox"])
        self.alignment_widgets["button_hbox"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["button_hbox"].set(1.0, 0.5, 0, 0)
        #self.alignment_widgets["button_hbox"].set_padding(0, 0, 0, 10)
        self.container_widgets["button_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["button_hbox"].pack_start(self.button_widgets["add_account"], False, False)
        self.container_widgets["button_hbox"].pack_start(self.button_widgets["del_account"], False, False)
        # init treeview item
        self.view_widgets["account"].add_items(self.get_user_list_treeitem(), clear_first=True)
        ###############
        # accounts info
        self.alignment_widgets["right_vbox"].set(0, 0, 1, 1)
        #self.alignment_widgets["right_vbox"].set_padding(0, 0, 20, 20)
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["account_info_table"], False, False)
        #self.container_widgets["right_vbox"].pack_start(self.container_widgets["check_button_table"], False, False)

        self.container_widgets["account_info_table"].set_col_spacings(WIDGET_SPACING)
        self.container_widgets["account_info_table"].attach(
            self.__make_align(self.image_widgets["account_icon"], height=58), 0, 1, 0, 1, 4)
        self.container_widgets["account_info_table"].attach(self.alignment_widgets["account_info_hbox"], 1, 2, 0, 1, 4)

        self.container_widgets["account_info_table"].attach(
            self.__make_align(self.label_widgets["account"], xalign=1.0), 0, 1, 1, 2, 4)
        self.container_widgets["account_info_table"].attach(
            self.__make_align(self.button_widgets["account_type"], xalign=0.0, width=COMBO_WIDTH), 1, 2, 1, 2, 4)
        self.container_widgets["account_info_table"].attach(
            self.__make_align(self.label_widgets["passwd"], xalign=1.0), 0, 1, 2, 3, 4)
        self.container_widgets["account_info_table"].attach(
            self.__make_align(self.label_widgets["passwd_char"], xalign=0.0, width=COMBO_WIDTH), 1, 2, 2, 3, 4)
        self.container_widgets["account_info_table"].attach(
            self.__make_align(self.label_widgets["auto_login"], xalign=1.0), 0, 1, 3, 4, 4)
        self.container_widgets["account_info_table"].attach(
            self.__make_align(self.button_widgets["auto_login"], xalign=0.0, width=COMBO_WIDTH), 1, 2, 3, 4, 4)
        #self.container_widgets["account_info_table"].attach(
            #self.__make_align(self.label_widgets["deepin_account_tips"]), 0, 1, 4, 5, 4)
        #self.container_widgets["account_info_table"].attach(
            #self.__make_align(self.label_widgets["deepin_account"]), 1, 2, 4, 5, 4)
        # TODO 绑定深度帐号
        self.button_widgets["account_type"].set_size_request(-1, WIDGET_HEIGHT)
        #self.image_widgets["account_icon"].set_size_request(48, 48)
        self.button_widgets["lock"].set_size_request(16, 16)
        self.alignment_widgets["account_info_hbox"].set(0.0, 0.5, 0, 0)
        self.alignment_widgets["account_info_hbox"].set_size_request(-1, CONTAINNER_HEIGHT)
        self.alignment_widgets["account_info_hbox"].add(self.container_widgets["account_info_hbox"])
        self.container_widgets["account_info_hbox"].pack_start(self.label_widgets["account_name"], False, False)
        self.container_widgets["account_info_hbox"].pack_start(self.alignment_widgets["lock_button"], False, False)
        self.alignment_widgets["lock_button"].add(self.button_widgets["lock"])
        self.alignment_widgets["lock_button"].set(1.0, 0.5, 0, 0)

        self.container_widgets["backup_check_group_hbox"].pack_start(self.alignment_widgets["backup_check_group"], False, False)
        self.container_widgets["backup_check_group_hbox"].pack_start(self.container_widgets["backup_check_group_vbox"], False, False)
        self.alignment_widgets["backup_check_group"].add(self.button_widgets["backup_check_group"])
        self.container_widgets["backup_check_group_vbox"].pack_start(self.label_widgets["backup_check_group"], False, False)
        self.container_widgets["backup_check_group_vbox"].pack_start(self.button_widgets["binding"], False, False, BETWEEN_SPACING)

        self.container_widgets["check_button_table"].set_col_spacings(WIDGET_SPACING)
        self.container_widgets["check_button_table"].attach(
            self.__make_align(self.button_widgets["net_access_check"]), 0, 1, 0, 1)
        self.container_widgets["check_button_table"].attach(
            self.__make_align(self.button_widgets["disk_readonly_check"]), 1, 2, 0, 1)
        self.container_widgets["check_button_table"].attach(
            self.__make_align(self.button_widgets["mountable_check"]), 0, 1, 1, 2)
        self.container_widgets["check_button_table"].attach(
            self.__make_align(self.button_widgets["disk_readwrite_check"]), 1, 2, 1, 2)
        self.container_widgets["check_button_table"].attach(
            self.__make_align(self.container_widgets["backup_check_group_hbox"]), 0, 2, 2, 3)

        ####################
        # create new account
        self.container_widgets["account_info_table_new"].set_col_spacings(WIDGET_SPACING)
        self.container_widgets["account_info_table_new"].attach(
            self.__make_align(self.label_widgets["account_name_new"]), 0, 1, 0, 1, 4)
        self.container_widgets["account_info_table_new"].attach(
            self.__make_align(self.button_widgets["account_name"]), 1, 2, 0, 1, 4)
        self.container_widgets["account_info_table_new"].attach(
            self.__make_align(self.label_widgets["account_type_new"]), 0, 1, 1, 2, 4)
        self.container_widgets["account_info_table_new"].attach(
            self.__make_align(self.button_widgets["account_type_new"]), 1, 2, 1, 2, 4)
        #self.container_widgets["account_info_table_new"].attach(
            #self.__make_align(self.label_widgets["deepin_account_tips_new"]), 0, 1, 2, 3, 4)
        #self.container_widgets["account_info_table_new"].attach(
            #self.__make_align(self.label_widgets["deepin_account_new"]), 1, 2, 2, 3, 4)

        self.button_widgets["account_name"].set_size(125, WIDGET_HEIGHT)
        self.button_widgets["account_type_new"].set_size_request(-1, WIDGET_HEIGHT)

        self.container_widgets["backup_check_group_hbox_new"].pack_start(self.alignment_widgets["backup_check_group_new"], False, False)
        self.container_widgets["backup_check_group_hbox_new"].pack_start(self.container_widgets["backup_check_group_vbox_new"], False, False)
        self.alignment_widgets["backup_check_group_new"].add(self.button_widgets["backup_check_group_new"])
        self.container_widgets["backup_check_group_vbox_new"].pack_start(self.label_widgets["backup_check_group_new"], False, False)
        self.container_widgets["backup_check_group_vbox_new"].pack_start(self.button_widgets["binding_new"], False, False, BETWEEN_SPACING)
        
        self.container_widgets["check_button_table_new"].set_col_spacings(WIDGET_SPACING)
        self.container_widgets["check_button_table_new"].attach(
            self.__make_align(self.button_widgets["net_access_check_new"]), 0, 1, 0, 1)
        self.container_widgets["check_button_table_new"].attach(
            self.__make_align(self.button_widgets["disk_readonly_check_new"]), 1, 2, 0, 1)
        self.container_widgets["check_button_table_new"].attach(
            self.__make_align(self.button_widgets["mountable_check_new"]), 0, 1, 1, 2)
        self.container_widgets["check_button_table_new"].attach(
            self.__make_align(self.button_widgets["disk_readwrite_check_new"]), 1, 2, 1, 2)
        self.container_widgets["check_button_table_new"].attach(
            self.__make_align(self.container_widgets["backup_check_group_hbox_new"]), 0, 2, 2, 3)

        self.alignment_widgets["account_create_error"] = self.__make_align(self.label_widgets["account_create_error"])
        self.alignment_widgets["button_hbox_new"].set(0, 0, 1, 0)
        self.alignment_widgets["button_hbox_new"].set_padding(BETWEEN_SPACING, 0, 0, 0)
        self.alignment_widgets["button_hbox_new"].add(self.container_widgets["button_hbox_new"])
        self.container_widgets["button_hbox_new"].pack_start(self.__make_align(height=-1))
        self.container_widgets["button_hbox_new"].set_spacing(WIDGET_SPACING)
        self.container_widgets["button_hbox_new"].pack_start(self.button_widgets["account_cancle"], False, False)
        self.container_widgets["button_hbox_new"].pack_start(self.button_widgets["account_create"], False, False)
        #############################
        # del account
        self.container_widgets["del_main_vbox"].set_spacing(BETWEEN_SPACING)
        self.container_widgets["del_main_vbox"].pack_start(self.label_widgets["del_account_tips"], False, False)
        self.container_widgets["del_main_vbox"].pack_start(self.label_widgets["del_account_tips2"], False, False)
        self.container_widgets["del_main_vbox"].pack_start(self.label_widgets["del_account_error_label"], False, False)
        button_align = gtk.Alignment()
        button_align.set(1, 0.5, 1, 1)
        self.container_widgets["del_account_button_hbox"].pack_start(button_align)
        self.container_widgets["del_account_button_hbox"].set_spacing(WIDGET_SPACING)
        self.container_widgets["del_account_button_hbox"].pack_start(self.button_widgets["del_button"], False, False)
        self.container_widgets["del_account_button_hbox"].pack_start(self.button_widgets["keep_button"], False, False)
        self.container_widgets["del_account_button_hbox"].pack_start(self.button_widgets["cancel_button"], False, False)
        self.container_widgets["del_main_vbox"].pack_start(self.container_widgets["del_account_button_hbox"], False, False)
        # set widget state
        if not self.permission.get_can_acquire() and not self.permission.get_can_release():
            self.button_widgets["lock"].set_sensitive(False)
        self.set_widget_state_with_author()
        ###########################
        # change account password page
        self.alignment_widgets["change_pswd"].set(0.5, 0.5, 1, 1)
        ###########################
        # delete account page
        self.alignment_widgets["delete_account"].set(0.5, 0.0, 1, 1)
        # set icon file
        self.alignment_widgets["set_iconfile"].set(0.5, 0.5, 1, 1)

    def __signals_connect(self):
        self.alignment_widgets["main_hbox"].connect("expose-event", self.container_expose_cb)
        self.alignment_widgets["change_pswd"].connect("expose-event", self.container_expose_cb)
        self.alignment_widgets["delete_account"].connect("expose-event", self.container_expose_cb)
        self.alignment_widgets["set_iconfile"].connect("expose-event", self.container_expose_cb)
        
        #self.container_widgets["left_vbox"].connect("expose-event", self.on_left_vbox_expose_cb)
        
        self.view_widgets["account"].connect("select", self.account_treeview_select)
        self.view_widgets["account"].select_first_item()
        self.button_widgets["add_account"].connect("clicked", self.add_account_button_clicked)
        self.button_widgets["del_account"].connect("clicked", self.del_account_button_clicked)
        self.button_widgets["account_cancle"].connect("clicked", self.account_cancle_button_clicked)
        self.button_widgets["account_create"].connect("clicked", self.account_create_button_clicked)
        self.button_widgets["auto_login"].connect("toggled", self.auto_login_toggled)
        
        self.button_widgets["del_button"].connect("clicked", self.del_delete_user_file_cd, True)
        self.button_widgets["keep_button"].connect("clicked", self.del_delete_user_file_cd, False)
        self.button_widgets["cancel_button"].connect("clicked", self.del_cancel_delete_cb)

        self.button_widgets["account_type"].connect("item-selected", self.account_type_item_selected)

        self.button_widgets["lock"].connect("expose-event", self.lock_button_expose)
        self.button_widgets["lock"].connect("clicked", self.lock_button_clicked)

        self.image_widgets["account_icon"].connect("button-press-event", self.icon_file_press_cb)
        self.label_widgets["account_name"].connect("enter-notify-event", self.label_enter_notify_cb, True)
        self.label_widgets["account_name"].connect("leave-notify-event", self.label_leave_notify_cb, True)
        self.label_widgets["account_name"].connect("button-press-event", self.realname_change_press_cb)
        self.label_widgets["passwd_char"].connect("enter-notify-event", self.label_enter_notify_cb)
        self.label_widgets["passwd_char"].connect("leave-notify-event", self.label_leave_notify_cb)
        self.label_widgets["passwd_char"].connect("button-press-event", self.password_change_press_cb)

        self.label_widgets["backup_check_group"].connect(
            "button-press-event",
            lambda w, e:self.button_widgets["backup_check_group"].set_active(
                not self.button_widgets["backup_check_group"].get_active()))
        self.label_widgets["backup_check_group_new"].connect(
            "button-press-event",
            lambda w, e:self.button_widgets["backup_check_group_new"].set_active(
                not self.button_widgets["backup_check_group_new"].get_active()))

        self.button_widgets["account_name"].entry.connect(
            "changed", self.account_name_input_changed, self.button_widgets["account_create"])

        self.account_dbus.connect("user-added", self.account_user_added_cb)
        self.account_dbus.connect("user-deleted", self.account_user_deleted_cb)

    ######################################
    # signals callback begin
    # widget signals
    def container_expose_cb(self, widget, event):
        cr = widget.window.cairo_create()
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                                               
        cr.rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)                                                 
        cr.fill()
    
    def on_left_vbox_expose_cb(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        left_rect = self.view_widgets["account"].allocation
        print "geometry:", widget.window.get_geometry()
        print "wiget:", x, y, w, h
        print "treeview:", left_rect
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))
            cr.set_line_width(1)
            cr.move_to(x+w, y)
            cr.line_to(x+w, y+h)
            cr.stroke()
    
    def auto_login_toggled(self, button):
        if not self.current_select_user:
            return
        if button.get_data("changed_by_other_app"):
            button.set_data("changed_by_other_app", False)
            return
        self.current_select_user.set_automatic_login(button.get_active())
    
    def add_account_button_clicked(self, button):
        container_remove_all(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["account_info_table_new"], False, False)
        #self.container_widgets["right_vbox"].pack_start(self.container_widgets["check_button_table_new"], False, False)
        self.container_widgets["right_vbox"].pack_start(self.__make_align(), False, False)
        self.container_widgets["right_vbox"].pack_start(self.alignment_widgets["account_create_error"], False, False, BETWEEN_SPACING)
        self.container_widgets["right_vbox"].pack_start(self.__make_align())
        self.container_widgets["right_vbox"].pack_start(self.alignment_widgets["button_hbox_new"], False, False)
        # TODO 绑定深度
        self.button_widgets["account_name"].set_text("")
        self.button_widgets["account_type"].set_select_index(0)
        self.label_widgets["account_create_error"].set_text("")
        self.button_widgets["account_create"].set_sensitive(False)
        self.container_widgets["right_vbox"].show_all()
        button.set_sensitive(False)
    
    def del_cancel_delete_cb(self, button):
        container_remove_all(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["account_info_table"], False, False)
        #self.container_widgets["right_vbox"].pack_start(self.container_widgets["check_button_table"], False, False)
        self.container_widgets["right_vbox"].show_all()
        
    def del_delete_user_file_cd(self, button, del_file):
        try:
            self.container_widgets["del_account_button_hbox"].set_sensitive(False)
            self.account_dbus.delete_user(self.current_del_user.get_uid(), del_file)
        except Exception, e:
            if isinstance(e, (AccountsPermissionDenied)):
                error_label.set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), e.msg))
            return
        self.del_cancel_delete_cb(button)
        
    def del_account_button_clicked(self, button):
        if not self.current_select_user:
            return
        self.current_del_user = self.current_select_user
        container_remove_all(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["del_main_vbox"])
        if self.current_select_user.get_real_name():
            show_name = self.current_select_user.get_real_name() 
        else:
            show_name = self.current_select_user.get_user_name()
        self.label_widgets["del_account_tips"].set_text(
            "<b>%s</b>" % _("Do you want to keep <u>%s</u>'s files?") % 
            self.escape_markup_string(show_name))
        self.label_widgets["del_account_error_label"].set_text("")
        self.container_widgets["del_account_button_hbox"].set_sensitive(True)
        self.container_widgets["right_vbox"].show_all()
    
    def account_cancle_button_clicked(self, button):
        container_remove_all(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["account_info_table"], False, False)
        #self.container_widgets["right_vbox"].pack_start(self.container_widgets["check_button_table"], False, False)
        self.container_widgets["right_vbox"].show_all()
        self.button_widgets["add_account"].set_sensitive(True)

    def account_create_button_clicked(self, button):
        username = self.button_widgets["account_name"].get_text()
        account_type = self.button_widgets["account_type_new"].get_current_item()[1]
        try:
            self.account_dbus.create_user(username, username, account_type)
        except Exception, e:
            if isinstance(e, (AccountsPermissionDenied, AccountsUserExists, AccountsFailed, AccountsUserDoesNotExist)):
                self.label_widgets["account_create_error"].set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), e.msg))
            return
        self.account_cancle_button_clicked(None)
    
    def account_treeview_select(self, tv, item, row):
        self.current_select_user = dbus_obj = item.dbus_obj
        self.current_select_item = item
        print "treeview current select:'%s', '%s'" % ( self.current_select_user.get_user_name(), self.current_select_user.get_real_name())
        print "treeitrem:'%s', '%s'" % (item.real_name, item.user_name)
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
        if dbus_obj.get_automatic_login() != self.button_widgets["auto_login"].get_active():
            self.button_widgets["auto_login"].set_data("changed_by_other_app", True)
            self.button_widgets["auto_login"].set_active(dbus_obj.get_automatic_login())
        
        if item.is_myowner:     # is current user that current process' owner
            if self.button_widgets["del_account"].get_sensitive():
                self.button_widgets["del_account"].set_sensitive(False)
            if not self.image_widgets["account_icon"].get_sensitive():
                self.image_widgets["account_icon"].set_sensitive(True)
            if not self.label_widgets["account_name"].get_sensitive():
                self.label_widgets["account_name"].set_sensitive(True)
            if not self.label_widgets["passwd_char"].get_sensitive():
                self.label_widgets["passwd_char"].set_sensitive(True)
        elif self.button_widgets["lock"].get_data("unlocked"):
            if not self.button_widgets["del_account"].get_sensitive():
                self.button_widgets["del_account"].set_sensitive(True)
        else:
            if self.image_widgets["account_icon"].get_sensitive():
                self.image_widgets["account_icon"].set_sensitive(False)
            if self.label_widgets["account_name"].get_sensitive():
                self.label_widgets["account_name"].set_sensitive(False)
            if self.label_widgets["passwd_char"].get_sensitive():
                self.label_widgets["passwd_char"].set_sensitive(False)
    
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
            #print "get_allowed:", self.permission.get_allowed()
        else:
            if self.permission.acquire():
                button.set_data("unlocked", True)
            #print "get_allowed:", self.permission.get_allowed()
        print "get_allowed:", self.permission.get_allowed(),
        print "get_can_acquire:", self.permission.get_can_acquire(),
        print "get_can_release:", self.permission.get_can_release()
        self.set_widget_state_with_author()
    
    def account_type_item_selected(self, combo_box, item_content, item_value, item_index):
        if not self.current_select_user:
            return
        try:
            self.current_select_user.set_account_type(item_value)
        except:
            pass
    
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
            cr = widget.window.cairo_create()
            with cairo_disable_antialias(cr):
                cr.set_line_width(1)
                cr.set_source_rgb(*color_hex_to_cairo("#000000"))                                               
                x, y, w, h = widget.allocation
                cr.rectangle(x+1, y+1, w-2, h-2)                                                 
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
            widget.set_text("%s" % pango.parse_markup(widget.get_text())[1])
    
    def realname_change_press_cb(self, widget, event):
        if not self.current_select_user:
            return
        
        def check_account_name(name):
            return len(name) <= 20
        
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
                #self.label_widgets["account_name"].set_text("<b>%s</b>" % self.escape_markup_string(text))
                try:
                    self.current_select_user.set_real_name(text)
                except:
                    pass
            self.label_widgets["account_name"].queue_draw()
            #print "account name changed:", self.label_widgets["account_name"].get_text()
            align.destroy()
        
        self.container_widgets["account_info_hbox"].remove(self.label_widgets["account_name"])
        #text = pango.parse_markup(widget.get_text())[1]
        text = self.current_select_user.get_real_name()
        align = gtk.Alignment()
        align.set(0.0, 0.5, 0, 0)
        align.set_padding(8, 0, 2, 63)
        input_entry = InputEntry(text)
        input_entry.entry.check_text = check_account_name
        input_entry.set_size(165, WIDGET_HEIGHT)
        input_entry.connect("expose-event", lambda w, e: input_entry.entry.grab_focus())
        input_entry.entry.connect("press-return", change_account_name)
        input_entry.entry.connect("focus-out-event", change_account_name)
        align.add(input_entry)
        align.show_all()
        self.container_widgets["account_info_hbox"].pack_start(align)
        self.container_widgets["account_info_hbox"].reorder_child(align, 0)
    
    def password_change_press_cb(self, widget, event):
        if not self.current_select_user:
            return
        self.__init_change_pswd_page(self.current_select_user)
        self.container_widgets["slider"].slide_to_page(
            account_settings.alignment_widgets["change_pswd"], "right")
        self.module_frame.send_submodule_crumb(2, _("Change Password"))
    
    def icon_file_press_cb(self, widget, event):
        if not self.current_select_user:
            return
        self.__init_set_icon_page(self.current_select_user)
        self.container_widgets["slider"].slide_to_page(
            account_settings.alignment_widgets["set_iconfile"], "right")
        self.module_frame.send_submodule_crumb(2, _("Set Icon"))
    
    def account_name_input_changed(self, entry, value, button):
        if entry.get_text():
            if not button.get_sensitive():
                button.set_sensitive(True)
        else:
            if button.get_sensitive():
                button.set_sensitive(False)

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
        item.user_name = self.escape_markup_string(user.get_user_name())
        item.real_name = self.escape_markup_string(user.get_real_name())
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
            if user.get_automatic_login() != self.button_widgets["auto_login"].get_active():
                self.button_widgets["auto_login"].set_data("changed_by_other_app", True)
                self.button_widgets["auto_login"].set_active(user.get_automatic_login())
    
    def account_user_added_cb(self, account_obj, user_path):
        print "%s added" % user_path
        user_info = settings.get_user_info(user_path)
        icon_file = user_info[1]
        if os.path.exists(icon_file):
            try:
                icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                    icon_file).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
            except:
                icon_pixbuf = self.image_widgets["default_icon"].get_pixbuf()
        else:
            icon_pixbuf = self.image_widgets["default_icon"].get_pixbuf()
        user_item = TreeItem(icon_pixbuf, self.escape_markup_string(user_info[2]),
                             self.escape_markup_string(user_info[3]),
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
                item = TreeItem(icon_pixbuf, self.escape_markup_string(user.get_real_name()),
                                self.escape_markup_string(user.get_user_name()),
                                user.get_account_type(), user, True)
                user_items.insert(0, item)
            else:
                item = TreeItem(icon_pixbuf, self.escape_markup_string(user.get_real_name()),
                                self.escape_markup_string(user.get_user_name()),
                                user.get_account_type(), user)
                user_items.append(item)
            user.connect("changed", self.user_info_changed_cb, item)
            for compare_user in user_list:
                if user == compare_user:
                    continue
                if user.get_real_name() == compare_user.get_real_name():
                    item.is_unique = False
                    break
        return user_items
    
    def set_widget_state_with_author(self):
        ''' set widgets sensitive if it has authorized, else insensitive '''
        authorized = self.get_authorized()
        self.button_widgets["lock"].set_data("unlocked", authorized)
        self.container_widgets["button_hbox"].set_sensitive(authorized)
        self.button_widgets["account_type"].set_sensitive(authorized)
        self.button_widgets["auto_login"].set_sensitive(authorized)
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
        return self.permission.get_allowed()
    
    def __init_set_icon_page(self, current_set_user):
        def cancel_set_icon(button):
            self.container_widgets["slider"].slide_to_page(self.alignment_widgets["main_hbox"], "left")
            self.change_crumb(1)
        
        def choose_picture(button, event):
            file_filter = gtk.FileFilter()
            file_filter.add_pixbuf_formats()
            f = gtk.FileChooserDialog(buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
            f.set_filter(file_filter)
            response = f.run()
            filename = f.get_filename()
            f.destroy()
            if response != gtk.RESPONSE_ACCEPT:
                return
            try:
                current_set_user.set_icon_file(filename)
            except Exception, e:
                if isinstance(e, (AccountsPermissionDenied)):
                    error_label.set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), e.msg))
                return
            self.container_widgets["slider"].slide_to_page(
                self.alignment_widgets["main_hbox"], "left")
            self.change_crumb(1)

        def table_expose_cb(widget, event):
            x, y, w, h = widget.allocation
            print x, y, w, h
            cr = widget.window.cairo_create()
            cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                                               
            cr.rectangle(x, y, 370, 257)                                                 
            cr.paint()
            with cairo_disable_antialias(cr):
                cr.set_source_rgb(*color_hex_to_cairo(TREEVIEW_BORDER_COLOR))                                               
                cr.rectangle(0, 0, 372, 259)                                                 
                cr.stroke()
        
        def icon_bt_release_cb(widget, event):
            try:
                file_path = widget.get_image_path()
                current_set_user.set_icon_file(file_path)
            except Exception, e:
                if isinstance(e, (AccountsPermissionDenied)):
                    error_label.set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), e.msg))
                return
            self.container_widgets["slider"].slide_to_page(
                self.alignment_widgets["main_hbox"], "left")
            self.change_crumb(1)
        self.container_widgets["set_iconfile_main_vbox"].destroy()
        self.container_widgets["set_iconfile_main_vbox"] = gtk.VBox(False)
        self.alignment_widgets["set_iconfile"].add(self.container_widgets["set_iconfile_main_vbox"])
        
        if current_set_user.get_real_name():
            show_name = current_set_user.get_real_name() 
        else:
            show_name = current_set_user.get_user_name()
        tips_label = Label("<b>%s</b>" % _("Set <u>%s</u>'s icon") % 
                           self.escape_markup_string(show_name),
                           text_size=13, wrap_width=460, enable_select=False)
        error_label = Label("", wrap_width=560, enable_select=False)
        swin = ScrolledWindow()
        face_dir = '/usr/share/pixmaps/faces'
        if os.path.exists(face_dir):
            pic_list = os.listdir(face_dir)
        else:
            pic_list = []
        row_num = (len(pic_list) + 1) / 10 + 1
        table = gtk.Table(row_num, 10)
        table.set_col_spacings(FRAME_VERTICAL_SPACING)
        table.set_row_spacings(FRAME_HORIZONTAL_SPACING)
        i = 0
        j = 0
        for pic in pic_list:
            try:
                icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                    "%s/%s" %(face_dir, pic)).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
            except:
                continue
            icon_bt = IconButton(icon_pixbuf, "%s/%s" %(face_dir, pic))
            icon_bt.connect("button-release-event", icon_bt_release_cb)
            table.attach(icon_bt, j, j+1, i, i+1, 4, 4)
            j += 1
            if j >= 10:
                j = 0
                i += 1
        more_button = IconButton(app_theme.get_pixbuf("%s/more.png" % MODULE_NAME).get_pixbuf())
        more_button.connect("button-release-event", choose_picture)
        table.attach(more_button, j, j+1, i, i+1, 4, 4)
        swin.add_child(self.__make_align(table, yalign=-1.0, padding_top=3, padding_left=2, height=-1))
        swin.set_size_request(650, 259)
        #table.connect("expose-event", table_expose_cb)
        table.connect("expose-event", self.container_expose_cb)

        button_hbox = gtk.HBox(False)
        button_hbox.set_spacing(WIDGET_SPACING)
        #more_button = Button(_("More"))
        cancel_button = Button(_("Cancel"))
        #button_hbox.pack_start(self.__make_align(height=-1))
        #button_hbox.pack_start(more_button, False, False)
        button_hbox.pack_start(cancel_button, False, False)

        cancel_button.connect("clicked", cancel_set_icon)
        #more_button.connect("clicked", choose_picture)

        self.container_widgets["set_iconfile_main_vbox"].set_spacing(BETWEEN_SPACING)
        self.container_widgets["set_iconfile_main_vbox"].pack_start(tips_label, False, False)
        self.container_widgets["set_iconfile_main_vbox"].pack_start(self.__make_align(swin, yalign=0.0, height=-1))
        self.container_widgets["set_iconfile_main_vbox"].pack_start(error_label, False, False)
        self.container_widgets["set_iconfile_main_vbox"].pack_start(button_hbox, False, False)
        self.container_widgets["set_iconfile_main_vbox"].show_all()
    
    def __init_change_pswd_page(self, current_set_user):
        def show_input_password(button):
            new_pswd_input.show_password(button.get_active())
            confirm_pswd_input.show_password(button.get_active())
        
        def password_input_changed(entry, text, variety, atleast=0):
            if not text or len(text)<atleast:
                is_input_empty[variety] = True
            else:
                is_input_empty[variety] = False
            if (is_myown and is_input_empty[CURRENT_PSWD]) or\
                    is_input_empty[NEW_PSWD] or\
                    is_input_empty[CONFIRM_PSWD] or\
                    new_pswd_input.entry.get_text() != confirm_pswd_input.entry.get_text():
                change_button.set_sensitive(False)
            else:
                change_button.set_sensitive(True)
        
        def action_combo_selected(combo_box, item_content, item_value, item_index):
            if item_value != ACTION_SET_PSWD:
                current_pswd_input.set_sensitive(False)
                new_pswd_input.set_sensitive(False)
                confirm_pswd_input.set_sensitive(False)
                show_pswd_check.set_sensitive(False)
                if not change_button.get_sensitive():
                    change_button.set_sensitive(True)
            else:
                current_pswd_input.set_sensitive(True)
                new_pswd_input.set_sensitive(True)
                confirm_pswd_input.set_sensitive(True)
                show_pswd_check.set_sensitive(True)
                if (is_myown and is_input_empty[CURRENT_PSWD]) or\
                        is_input_empty[NEW_PSWD] or\
                        is_input_empty[CONFIRM_PSWD] or\
                        new_pswd_input.entry.get_text() != confirm_pswd_input.entry.get_text():
                    change_button.set_sensitive(False)
                else:
                    change_button.set_sensitive(True)
        
        def change_user_password_thread(new_pswd, mutex):
            print "in thread"
            mutex.acquire()
            try:
                if is_myown:
                    old_pswd = current_pswd_input.entry.get_text()
                else:
                    old_pswd = " "
                b = self.account_dbus.modify_user_passwd(new_pswd, current_set_user.get_user_name(), old_pswd)
                print "changed status:", b
                if b != 0:
                    error_msg = _("password unchanged")
                    if b == 10:
                        error_msg = _("Authentication token manipulation error")
                    if b == -2:
                        error_msg = _("new and old password are too similar")
                    gtk.gdk.threads_enter()
                    error_label.set_text("<span foreground='red'>%s%s</span>" % (
                        _("Error:"), error_msg))
                    table2.set_sensitive(True)
                    gtk.gdk.threads_leave()
                else:
                    gtk.gdk.threads_enter()
                    self.container_widgets["slider"].slide_to_page(self.alignment_widgets["main_hbox"], "left")
                    self.change_crumb(1)
                    gtk.gdk.threads_leave()
            except Exception, e:
                if not isinstance(e, (TIMEOUT, EOF)):
                    error_msg = e.message
                else:
                    error_msg = _("password unchanged")
                gtk.gdk.threads_enter()
                error_label.set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), error_msg))
                table2.set_sensitive(True)
                gtk.gdk.threads_leave()
            mutex.release()
            
        def change_user_password(button):
            table2.set_sensitive(False)
            if is_authorized:
                do_action = action_combo.get_current_item()[1]
                try:
                    if do_action == ACTION_ENABLE:
                        current_set_user.set_locked(False)
                    elif do_action == ACTION_DISABLE:
                        current_set_user.set_locked(True)
                    elif do_action == ACTION_NO_PSWD:
                        current_set_user.set_password_mode(2)
                except Exception, e:
                    if isinstance(e, (AccountsPermissionDenied, AccountsUserExists, AccountsFailed, AccountsUserDoesNotExist)):
                        error_label.set_text("<span foreground='red'>%s%s</span>" % (_("Error:"), e.msg))
                        return
                # action is not setting password, then return
                if do_action != ACTION_SET_PSWD:
                    self.container_widgets["slider"].slide_to_page(self.alignment_widgets["main_hbox"], "left")
                    self.change_crumb(1)
                    return
            new_pswd = new_pswd_input.entry.get_text()
            confirm_pswd = confirm_pswd_input.entry.get_text()
            if new_pswd != confirm_pswd:
                error_label.set_text("<span foreground='red'>%s</span>" % _("两次输入的密码不一致"))
                table2.set_sensitive(True)
                return
            mutex = threading.Lock()
            t = threading.Thread(target=change_user_password_thread, args=(new_pswd, mutex))
            t.setDaemon(True)
            t.start()
        
        def cancel_change_password(button):
            self.container_widgets["slider"].slide_to_page(self.alignment_widgets["main_hbox"], "left")
            self.change_crumb(1)
        CURRENT_PSWD = 0
        NEW_PSWD = 1
        CONFIRM_PSWD = 2

        ACTION_SET_PSWD = 0
        ACTION_NO_PSWD = 1
        ACTION_ENABLE = 2
        ACTION_DISABLE = 3
        is_input_empty = {
            CURRENT_PSWD: True,
            NEW_PSWD: True,
            CONFIRM_PSWD: True}
        is_authorized = self.get_authorized()
        is_myown = settings.check_is_myown(current_set_user.get_uid())
        
        self.container_widgets["change_pswd_main_vbox"].destroy()
        self.container_widgets["change_pswd_main_vbox"] = gtk.VBox(False)
        self.alignment_widgets["change_pswd"].add(self.container_widgets["change_pswd_main_vbox"])

        table1 = gtk.Table(2, 2)
        table2 = gtk.Table(7, 2)
        button_hbox = gtk.HBox(False)
        
        if current_set_user.get_real_name():
            show_name = current_set_user.get_real_name() 
        else:
            show_name = current_set_user.get_user_name()
        icon_file = current_set_user.get_icon_file()
        if os.path.exists(icon_file):
            try:
                icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                    icon_file).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
            except:
                icon_pixbuf = self.image_widgets["default_icon"].get_pixbuf()
        else:
            icon_pixbuf = self.image_widgets["default_icon"].get_pixbuf()
        icon = gtk.Image()
        icon.set_from_pixbuf(icon_pixbuf)
        tips_label = Label(_("Changing password for"), enable_select=False)
        username_label = Label(self.escape_markup_string(show_name), enable_select=False)
        table1.set_col_spacings(WIDGET_SPACING)
        table1.attach(self.__make_align(icon, height=48), 0, 1, 0, 2, 4)
        table1.attach(self.__make_align(tips_label), 1, 2, 0, 1)
        table1.attach(self.__make_align(username_label), 1, 2, 1, 2)
        
        label1 = Label(_("Action"))
        label2 = Label(_("Current password"))
        label3 = Label(_("New password"))
        label4 = Label(_("Confirm password"))
        table2.set_col_spacings(WIDGET_SPACING)
        table2.attach(self.__make_align(label3), 0, 1, 2, 3, 4)
        table2.attach(self.__make_align(label4), 0, 1, 3, 4, 4)
        
        action_items = [(_("Set a password now"), ACTION_SET_PSWD),
                        (_("Log in without a password"), ACTION_NO_PSWD)]
        if current_set_user.get_locked():
            action_items.append((_("Enable this account"), ACTION_ENABLE))
        else:
            action_items.append((_("Disable this account"), ACTION_DISABLE))
        action_combo = ComboBox(action_items, max_width=180)
        action_combo.set_size_request(-1, WIDGET_HEIGHT)
        current_pswd_input = PasswordEntry()
        new_pswd_input = PasswordEntry()
        confirm_pswd_input = PasswordEntry()
        current_pswd_input.set_size(180, WIDGET_HEIGHT)
        new_pswd_input.set_size(180, WIDGET_HEIGHT)
        confirm_pswd_input.set_size(180, WIDGET_HEIGHT)
        show_pswd_check = CheckButton(_("Show password"), padding_x=0)
        if is_authorized:
            table2.attach(self.__make_align(label1), 0, 1, 0, 1, 4)
            table2.attach(self.__make_align(action_combo), 1, 2, 0, 1, 4)
        if is_myown:
            table2.attach(self.__make_align(label2), 0, 1, 1, 2, 4)
            table2.attach(self.__make_align(current_pswd_input), 1, 2, 1, 2, 4)
        table2.attach(self.__make_align(new_pswd_input), 1, 2, 2, 3, 4)
        table2.attach(self.__make_align(confirm_pswd_input), 1, 2, 3, 4, 4)
        table2.attach(self.__make_align(show_pswd_check), 1, 2, 4, 5, 4)
        table2.attach(self.__make_align(button_hbox, xalign=1.0), 1, 2, 6, 7, 4)
        
        cancel_button = Button(_("Cancel"))
        change_button = Button(_("Change"))
        change_button.set_sensitive(False)
        button_hbox.set_spacing(WIDGET_SPACING)
        button_hbox.pack_start(cancel_button, False, False)
        button_hbox.pack_start(change_button, False, False)
        
        error_label = Label("")
        #table2.attach(error_label, 0, 2, 5, 6, 4, 0)
        
        self.container_widgets["change_pswd_main_vbox"].set_spacing(BETWEEN_SPACING)
        self.container_widgets["change_pswd_main_vbox"].pack_start(table1, False, False)
        self.container_widgets["change_pswd_main_vbox"].pack_start(table2, False, False)
        self.container_widgets["change_pswd_main_vbox"].pack_start(error_label, False, False)
        self.container_widgets["change_pswd_main_vbox"].pack_start(gtk.Alignment(0, 0, 1, 1))
        self.container_widgets["change_pswd_main_vbox"].show_all()

        action_combo.connect("item-selected", action_combo_selected)
        current_pswd_input.entry.connect("changed", password_input_changed, CURRENT_PSWD)
        new_pswd_input.entry.connect("changed", password_input_changed, NEW_PSWD, 6)
        confirm_pswd_input.entry.connect("changed", password_input_changed, CONFIRM_PSWD, 6)
        show_pswd_check.connect("toggled", show_input_password)
        cancel_button.connect("clicked", cancel_change_password)
        change_button.connect("clicked", change_user_password)

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

    def escape_markup_string(self, string):
        '''
        escape markup string
        @param string: a markup string
        @return: a escaped string
        '''
        if not string:
            return ""
        return markup_escape_text(string)
    
    def change_crumb(self, crumb_index):
        self.module_frame.send_message("change_crumb", crumb_index)
        
if __name__ == '__main__':
    gtk.gdk.threads_init()
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    account_settings = AccountSetting(module_frame)
    
    module_frame.add(account_settings.container_widgets["slider"])
    module_frame.connect("realize", lambda w: account_settings.container_widgets["slider"].set_to_page(
        account_settings.alignment_widgets["main_hbox"]))
    if len(sys.argv) > 1:
        print "module_uid:", sys.argv[1]
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "click_crumb":
            (crumb_index, crumb_label) = message_content
            if crumb_index == 1:
                account_settings.container_widgets["slider"].slide_to_page(
                    account_settings.alignment_widgets["main_hbox"], "left")
        elif message_type == "show_again":
            print "DEBUG show_again module_uid", message_content
            account_settings.container_widgets["slider"].set_to_page(
                account_settings.alignment_widgets["main_hbox"])
            module_frame.send_module_info()

    module_frame.module_message_handler = message_handler        
    
    module_frame.run()
