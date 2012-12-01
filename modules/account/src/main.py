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
from dtk.ui.utils import container_remove_all
from treeitem import MyTreeView as TreeView
from treeitem import MyTreeItem as TreeItem
from dbus.exceptions import DBusException
import gtk
from module_frame import ModuleFrame


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
        self.label_widgets["passwd_char"] = Label("****", enable_select=False)
        self.label_widgets["auto_login"] = Label(_("Automatic Login"))
        self.label_widgets["deepin_account_tips"] = Label(_("Deepin Account"))
        self.label_widgets["deepin_account"] = Label(_("Unbound"))
        self.label_widgets["account_name_new"] = Label(_("Account Name"))
        self.label_widgets["account_type_new"] = Label(_("Account type"))
        self.label_widgets["deepin_account_tips_new"] = Label(_("Deepin Account"))
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
        self.image_widgets["default_icon"] = gtk.gdk.pixbuf_new_from_file(
            app_theme.get_theme_file_path("image/set/icon.png"))
        self.image_widgets["account_icon"] = gtk.Image()
        # button
        self.button_widgets["account_name"] = InputEntry()
        self.button_widgets["lock"] = gtk.Button()
        self.button_widgets["account_type"] = ComboBox([(_('Standard'), 0), (_('Administrator'), 1)], max_width=165)
        self.button_widgets["auto_login"] = gtk.ToggleButton()
        self.button_widgets["passwd"] = InputEntry()
        self.button_widgets["net_access_check"] = CheckButton(_("网络访问权限"))
        self.button_widgets["disk_readonly_check"] = CheckButton(_("磁盘操作权限只读"))
        self.button_widgets["mountable_check"] = CheckButton(_("可加载移动设备"))
        self.button_widgets["disk_readwrite_check"] = CheckButton(_("磁盘操作权限完全"))

        self.button_widgets["backup_check_group"] = CheckButton("")
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
        self.button_widgets["net_access_check_new"] = CheckButton(_("网络访问权限"))
        self.button_widgets["disk_readonly_check_new"] = CheckButton(_("磁盘操作权限只读"))
        self.button_widgets["mountable_check_new"] = CheckButton(_("可加载移动设备"))
        self.button_widgets["disk_readwrite_check_new"] = CheckButton(_("磁盘操作权限完全"))

        self.button_widgets["backup_check_group_new"] = CheckButton("")
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

    
    def __adjust_widget(self):
        self.container_widgets["slider"].append_page(self.alignment_widgets["main_hbox"])
        self.container_widgets["slider"].append_page(self.alignment_widgets["change_pswd"])
        self.container_widgets["slider"].append_page(self.alignment_widgets["delete_account"])

        self.alignment_widgets["main_hbox"].add(self.container_widgets["main_hbox"])
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["left_vbox"], False, False)
        self.container_widgets["main_hbox"].pack_start(self.alignment_widgets["right_vbox"])
        self.alignment_widgets["left_vbox"].add(self.container_widgets["left_vbox"])
        self.alignment_widgets["right_vbox"].add(self.container_widgets["right_vbox"])
        self.alignment_widgets["main_hbox"].set(0.5, 0.5, 1, 1)
        self.alignment_widgets["main_hbox"].set_padding(5, 5, 5, 5)
        ##############################
        # accounts list page
        self.container_widgets["left_vbox"].pack_start(self.view_widgets["account"])
        self.container_widgets["left_vbox"].pack_start(self.container_widgets["button_hbox"], False, False, 10)
        self.container_widgets["button_hbox"].pack_start(self.alignment_widgets["button_hbox"])
        self.container_widgets["button_hbox"].pack_start(self.button_widgets["add_account"], False, False, 10)
        self.container_widgets["button_hbox"].pack_start(self.button_widgets["del_account"], False, False)
        self.alignment_widgets["button_hbox"].set(0, 0, 1, 1)
        self.view_widgets["account"].set_size_request(325, 355)
        # init treeview item
        self.view_widgets["account"].add_items(self.get_user_list_treeitem(), clear_first=True)
        ###############
        # accounts info
        self.alignment_widgets["right_vbox"].set(0, 0, 1, 1)
        self.alignment_widgets["right_vbox"].set_padding(0, 0, 20, 20)
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["account_info_table"], False, False)
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["check_button_table"], False, False)

        self.container_widgets["account_info_table"].attach(self.image_widgets["account_icon"], 0, 1, 0, 1, 4, ypadding=10)
        self.container_widgets["account_info_table"].attach(self.alignment_widgets["account_info_hbox"], 1, 2, 0, 1, 4, ypadding=10)
        self.container_widgets["account_info_table"].attach(self.label_widgets["account"], 0, 1, 1, 2, 4, ypadding=10)
        self.container_widgets["account_info_table"].attach(self.button_widgets["account_type"], 1, 2, 1, 2, 4, 5, 50, ypadding=10)
        self.container_widgets["account_info_table"].attach(self.label_widgets["passwd"], 0, 1, 2, 3, 4, ypadding=10)
        self.container_widgets["account_info_table"].attach(self.label_widgets["passwd_char"], 1, 2, 2, 3, 4, 5, 50, ypadding=10)
        self.container_widgets["account_info_table"].attach(self.label_widgets["auto_login"], 0, 1, 3, 4, 4, ypadding=10)
        self.container_widgets["account_info_table"].attach(self.button_widgets["auto_login"], 1, 2, 3, 4, 4, 5, 50, ypadding=10)
        self.container_widgets["account_info_table"].attach(self.label_widgets["deepin_account_tips"], 0, 1, 4, 5, 4, ypadding=10)
        self.container_widgets["account_info_table"].attach(self.label_widgets["deepin_account"], 1, 2, 4, 5, 4, 5, 50, ypadding=10)
        # TODO 绑定深度帐号
        #self.container_widgets["right_vbox"].set_sensitive(False)
        self.button_widgets["auto_login"].set_size_request(49, 22)
        self.image_widgets["account_icon"].set_size_request(48, 48)
        self.button_widgets["lock"].set_size_request(16, 16)
        self.alignment_widgets["account_info_hbox"].set(0.5, 0.5, 1, 1)
        self.alignment_widgets["account_info_hbox"].add(self.container_widgets["account_info_hbox"])
        self.container_widgets["account_info_hbox"].pack_start(self.label_widgets["account_name"], False, False)
        self.container_widgets["account_info_hbox"].pack_start(self.alignment_widgets["lock_button"], False, False)
        self.alignment_widgets["lock_button"].add(self.button_widgets["lock"])
        self.alignment_widgets["lock_button"].set(1.0, 0.5, 1, 1)
        self.alignment_widgets["lock_button"].set_padding(16, 16, 20, 0)

        self.container_widgets["backup_check_group_hbox"].pack_start(self.alignment_widgets["backup_check_group"], False, False)
        self.container_widgets["backup_check_group_hbox"].pack_start(self.container_widgets["backup_check_group_vbox"], False, False)
        self.alignment_widgets["backup_check_group"].add(self.button_widgets["backup_check_group"])
        self.alignment_widgets["backup_check_group"].set(0, 0, 1, 1)
        self.container_widgets["backup_check_group_vbox"].pack_start(self.label_widgets["backup_check_group"], False, False)
        self.container_widgets["backup_check_group_vbox"].pack_start(self.button_widgets["binding"], False, False, 20)

        self.container_widgets["check_button_table"].attach(self.button_widgets["net_access_check"], 0, 1, 0, 1, ypadding=10)
        self.container_widgets["check_button_table"].attach(self.button_widgets["disk_readonly_check"], 1, 2, 0, 1, ypadding=10)
        self.container_widgets["check_button_table"].attach(self.button_widgets["mountable_check"], 0, 1, 1, 2, ypadding=10)
        self.container_widgets["check_button_table"].attach(self.button_widgets["disk_readwrite_check"], 1, 2, 1, 2, ypadding=10)
        self.container_widgets["check_button_table"].attach(self.container_widgets["backup_check_group_hbox"], 0, 2, 2, 3, ypadding=10)

        ####################
        # create new account
        #self.container_widgets["right_vbox"].pack_start(self.container_widgets["account_info_table_new"], False, False)
        #self.container_widgets["right_vbox"].pack_start(self.container_widgets["check_button_table_new"], False, False)
        #self.container_widgets["right_vbox"].pack_start(self.container_widgets["button_hbox_new"], False, False)

        self.container_widgets["account_info_table_new"].attach(self.label_widgets["account_name_new"], 0, 1, 0, 1, 4, ypadding=10)
        self.container_widgets["account_info_table_new"].attach(self.button_widgets["account_name"], 1, 2, 0, 1, 4, 5, 50, ypadding=10)
        self.container_widgets["account_info_table_new"].attach(self.label_widgets["account_type_new"], 0, 1, 1, 2, 4, ypadding=10)
        self.container_widgets["account_info_table_new"].attach(self.button_widgets["account_type_new"], 1, 2, 1, 2, 4, 5, 50, ypadding=10)
        self.container_widgets["account_info_table_new"].attach(self.label_widgets["deepin_account_tips_new"], 0, 1, 2, 3, 4, ypadding=10)
        self.container_widgets["account_info_table_new"].attach(self.label_widgets["deepin_account_new"], 1, 2, 2, 3, 4, 5, 50, ypadding=10)

        self.button_widgets["account_name"].set_size(115, 20)

        self.container_widgets["backup_check_group_hbox_new"].pack_start(self.alignment_widgets["backup_check_group_new"], False, False)
        self.container_widgets["backup_check_group_hbox_new"].pack_start(self.container_widgets["backup_check_group_vbox_new"], False, False)
        self.alignment_widgets["backup_check_group_new"].add(self.button_widgets["backup_check_group_new"])
        self.alignment_widgets["backup_check_group_new"].set(0, 0, 1, 1)
        self.container_widgets["backup_check_group_vbox_new"].pack_start(self.label_widgets["backup_check_group_new"], False, False)
        self.container_widgets["backup_check_group_vbox_new"].pack_start(self.button_widgets["binding_new"], False, False, 20)
        
        self.container_widgets["check_button_table_new"].attach(self.button_widgets["net_access_check_new"], 0, 1, 0, 1, ypadding=10)
        self.container_widgets["check_button_table_new"].attach(self.button_widgets["disk_readonly_check_new"], 1, 2, 0, 1, ypadding=10)
        self.container_widgets["check_button_table_new"].attach(self.button_widgets["mountable_check_new"], 0, 1, 1, 2, ypadding=10)
        self.container_widgets["check_button_table_new"].attach(self.button_widgets["disk_readwrite_check_new"], 1, 2, 1, 2, ypadding=10)
        self.container_widgets["check_button_table_new"].attach(self.container_widgets["backup_check_group_hbox_new"], 0, 2, 2, 3, ypadding=10)

        self.alignment_widgets["button_hbox_new"].set(0, 0, 1, 1)
        self.container_widgets["button_hbox_new"].pack_start(self.alignment_widgets["button_hbox_new"])
        self.container_widgets["button_hbox_new"].pack_start(self.button_widgets["account_cancle"], False, False, 10)
        self.container_widgets["button_hbox_new"].pack_start(self.button_widgets["account_create"], False, False)
        
        # set widget state
        self.set_widget_state_with_author()
        ###########################
        # change account password page
        self.alignment_widgets["change_pswd"].set(0.5, 0.5, 1, 1)
        self.alignment_widgets["change_pswd"].set_padding(50, 50, 70, 70)
        ###########################
        # delete account page
        self.alignment_widgets["delete_account"].set(0.5, 0.5, 1, 1)
        self.alignment_widgets["delete_account"].set_padding(50, 50, 70, 70)

    def __signals_connect(self):
        self.view_widgets["account"].connect("select", self.account_treeview_select)
        self.view_widgets["account"].select_first_item()
        self.button_widgets["add_account"].connect("clicked", self.add_account_button_clicked)
        self.button_widgets["del_account"].connect("clicked", self.del_account_button_clicked)
        self.button_widgets["account_cancle"].connect("clicked", self.account_cancle_button_clicked)
        self.button_widgets["account_create"].connect("clicked", self.account_create_button_clicked)
        self.button_widgets["auto_login"].connect("expose-event", self.toggle_button_expose)
        self.button_widgets["auto_login"].connect("toggled", self.auto_login_toggled)

        self.button_widgets["account_type"].connect("item-selected", self.account_type_item_selected)

        self.button_widgets["lock"].connect("expose-event", self.lock_button_expose)
        self.button_widgets["lock"].connect("clicked", self.lock_button_clicked)

        self.label_widgets["account_name"].connect("enter-notify-event", self.label_enter_notify_cb)
        self.label_widgets["account_name"].connect("leave-notify-event", self.label_leave_notify_cb)
        self.label_widgets["account_name"].connect("button-press-event", self.label_button_press_cb)
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

        self.account_dbus.connect("user-added", self.account_user_added_cb)
        self.account_dbus.connect("user-deleted", self.account_user_deleted_cb)

    ######################################
    # signals callback begin
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
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["check_button_table_new"], False, False)
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["button_hbox_new"], False, False)
        self.container_widgets["right_vbox"].show_all()
        button.set_sensitive(False)
    
    def del_account_button_clicked(self, button):
        if not self.current_select_user:
            return
        self.__init_del_user_page(self.current_select_user)
        self.container_widgets["slider"].slide_to_page(
            account_settings.alignment_widgets["delete_account"], "right")
        #self.module_frame.send_submodule_crumb(2, _("Delete User"))
    
    def account_cancle_button_clicked(self, button):
        container_remove_all(self.container_widgets["right_vbox"])
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["account_info_table"], False, False)
        self.container_widgets["right_vbox"].pack_start(self.container_widgets["check_button_table"], False, False)
        self.container_widgets["right_vbox"].show_all()
        self.button_widgets["add_account"].set_sensitive(True)

    def account_create_button_clicked(self, button):
        pass
    
    def account_treeview_select(self, tv, item, row):
        self.current_select_user = dbus_obj = item.dbus_obj
        self.image_widgets["account_icon"].set_from_pixbuf(item.icon)
        if item.real_name:
            self.label_widgets["account_name"].set_text("<b>%s</b>" % item.real_name)
        else:
            self.label_widgets["account_name"].set_text("<b>--</b>")
        self.button_widgets["account_type"].set_select_index(item.user_type)
        if dbus_obj.get_locked():
            self.label_widgets["passwd_char"].set_text(_("Account disabled"))
        elif dbus_obj.get_password_mode():
            self.label_widgets["passwd_char"].set_text(_("None"))
        else:
            self.label_widgets["passwd_char"].set_text("****")
        if dbus_obj.get_automatic_login() != self.button_widgets["auto_login"].get_active():
            self.button_widgets["auto_login"].set_data("changed_by_other_app", True)
            self.button_widgets["auto_login"].set_active(dbus_obj.get_automatic_login())
        
        if item.is_myowner:     # is current user that current process' owner
            if self.button_widgets["del_account"].get_sensitive():
                self.button_widgets["del_account"].set_sensitive(False)
            if not self.label_widgets["account_name"].get_sensitive():
                self.label_widgets["account_name"].set_sensitive(True)
            if not self.label_widgets["passwd_char"].get_sensitive():
                self.label_widgets["passwd_char"].set_sensitive(True)
        elif self.button_widgets["lock"].get_data("unlocked"):
            if not self.button_widgets["del_account"].get_sensitive():
                self.button_widgets["del_account"].set_sensitive(True)
        else:
            if self.label_widgets["account_name"].get_sensitive():
                self.label_widgets["account_name"].set_sensitive(False)
            if self.label_widgets["passwd_char"].get_sensitive():
                self.label_widgets["passwd_char"].set_sensitive(False)
    
    def lock_button_expose(self, button, event):
        cr = button.window.cairo_create()
        x, y, w, h = button.allocation
        if button.get_data("unlocked"):
            cr.set_source_pixbuf(self.image_widgets["lock_pixbuf"], x, y) 
            cr.paint()
        else:
            cr.set_source_pixbuf(
                self.image_widgets["unlock_pixbuf"], x, y) 
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
        except:
            pass
    
    def label_enter_notify_cb(self, widget, event):
        widget.set_data("old_content", widget.get_text())
        widget.set_text("<u>%s</u>" % widget.get_text())
    
    def label_leave_notify_cb(self, widget, event):
        widget.set_text(widget.get_data("old_content"))
    
    def label_button_press_cb(self, widget, event):
        print "press"
    
    def password_change_press_cb(self, widget, event):
        if not self.current_select_user:
            return
        self.__init_change_pswd_page(self.current_select_user)
        self.container_widgets["slider"].slide_to_page(
            account_settings.alignment_widgets["change_pswd"], "right")
        #self.module_frame.send_submodule_crumb(2, _("Change Password"))

    # dbus signals
    def user_info_changed_cb(self, user, item):
        icon_file = user.get_icon_file()
        if os.path.exists(icon_file):
            icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                icon_file).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
        else:
            icon_pixbuf = self.image_widgets["default_icon"]
        item.icon = icon_pixbuf
        item.user_name = user.get_user_name()
        item.real_name = user.get_real_name()
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
            elif user.get_password_mode():
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
            icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                icon_file).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
        else:
            icon_pixbuf = self.image_widgets["default_icon"]
        user_item = TreeItem(icon_pixbuf, user_info[2], user_info[3],
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
                icon_pixbuf = gtk.gdk.pixbuf_new_from_file(
                    icon_file).scale_simple(48, 48, gtk.gdk.INTERP_TILES)
            else:
                icon_pixbuf = self.image_widgets["default_icon"]
            if settings.check_is_myown(user.get_uid()):
                item = TreeItem(icon_pixbuf, user.get_real_name(), user.get_user_name(),
                                user.get_account_type(), user, True)
                user_items.insert(0, item)
            else:
                item = TreeItem(icon_pixbuf, user.get_real_name(), user.get_user_name(),
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
            self.label_widgets["account_name"].set_sensitive(authorized)
            self.label_widgets["passwd_char"].set_sensitive(authorized)
            self.button_widgets["del_account"].set_sensitive(authorized)
    
    def get_authorized(self):
        '''
        @return: True if current process has been authorized, else False
        '''
        return self.permission.get_allowed()
    
    def __init_del_user_page(self, current_del_user):
        def cancel_delete_user(button):
            self.container_widgets["slider"].slide_to_page(
                self.alignment_widgets["main_hbox"], "left")
        
        def delete_user_file_cd(button, del_file):
            try:
                button_hbox.set_sensitive(False)
                self.account_dbus.delete_user(current_del_user.get_uid(), del_file)
                self.container_widgets["slider"].slide_to_page(
                    self.alignment_widgets["main_hbox"], "left")
            except DBusException, e:    # TODO 删除用户出错时显示错误信息
                error_label.set_text("<span foreground='red'>Error:%s</span>" % e.message)
            except Exception, e:
                error_label.set_text("<span foreground='red'>Error:%s</span>" % str(e))
            
        self.container_widgets["del_main_vbox"].destroy()
        self.container_widgets["del_main_vbox"] = gtk.VBox(False)
        self.alignment_widgets["delete_account"].add(self.container_widgets["del_main_vbox"])

        if current_del_user.get_real_name():
            show_name = current_del_user.get_real_name() 
        else:
            show_name = current_del_user.get_user_name()
        tips_label = Label(_("<b>Do you want to keep <u>%s</u>'s files?</b>") % show_name,
                           text_size=13, wrap_width=660, enable_select=False)
        tips_label2 = Label(_("It is possible to keep the home directory when deleting a user account."),
                            wrap_width=660, enable_select=False)
        error_label = Label("", wrap_width=660, enable_select=False)
        button_align = gtk.Alignment()
        button_hbox = gtk.HBox(False)
        button_align.set(1, 0.5, 1, 1)
        del_button = Button(_("Delete Files"))
        keep_button = Button(_("Keep Files"))
        cancel_button = Button(_("Cancel"))
        del_button.connect("clicked", delete_user_file_cd, True)
        keep_button.connect("clicked", delete_user_file_cd, False)
        cancel_button.connect("clicked", cancel_delete_user)
        button_hbox.pack_start(button_align)
        button_hbox.pack_start(del_button, False, False)
        button_hbox.pack_start(keep_button, False, False, 10)
        button_hbox.pack_start(cancel_button, False, False)
        self.container_widgets["del_main_vbox"].pack_start(tips_label, False, False)
        self.container_widgets["del_main_vbox"].pack_start(tips_label2, False, False, 15)
        self.container_widgets["del_main_vbox"].pack_start(button_hbox, False, False, 15)
        self.container_widgets["del_main_vbox"].pack_start(error_label, False, False, 15)
        self.container_widgets["del_main_vbox"].show_all()
    
    def __init_change_pswd_page(self, current_set_user):
        self.container_widgets["change_pswd_main_vbox"].destroy()
        self.container_widgets["change_pswd_main_vbox"] = gtk.VBox(False)
        self.alignment_widgets["change_pswd"].add(self.container_widgets["change_pswd_main_vbox"])

    
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
        if message_type == "click_crumb":
            (crumb_index, crumb_label) = message_content
            if crumb_index == 1:
                account_settings.container_widgets["slider"].slide_to_page(
                    account_settings.alignment_widgets["main_hbox"], "left")
        elif message_type == "show_again":
            account_settings.container_widgets["slider"].set_to_page(
                account_settings.alignment_widgets["main_hbox"])
            module_frame.send_module_info()

    module_frame.module_message_handler = message_handler        
    
    module_frame.run()
