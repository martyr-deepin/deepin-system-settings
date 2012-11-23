#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
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

from utils import BusBase
import gobject

class Accounts(BusBase):

    __gsignals__  = {
        "user-added":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,)),
        "user-deleted":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,))
            }

    def __init__(self):
        BusBase.__init__(self, path = "/org/freedesktop/Accounts", interface = "org.freedesktop.Accounts")

        self.bus.add_signal_receiver(self.user_added_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "UserAdded")

        self.bus.add_signal_receiver(self.user_deleted_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "UserDeleted")

        self.init_dbus_properties()

    def get_daemon_version(self):
        return self.properties["DaemonVersion"]

    def create_user(self, name, fullname, account_type):
        return str(self.dbus_method("CreateUser", name, fullname, account_type))

    def delete_user(self, id, remove_files_flag):
        self.call_async("DeleteUser", id, remove_files_flag, reply_handler = None, error_handler = None)

    def find_user_by_id(self, id):
        return str(self.dbus_method("FindUserById", id))

    def find_user_by_name(self, name):
        return str(self.dbus_method("FindUserByName", name))

    def list_cached_users(self):
        return map(lambda x:str(x), self.dbus_method("ListCachedUsers"))

    def user_added_cb(self, userpath):
        self.emit("user-added", userpath)

    def user_deleted_cb(self, userpath):
        self.emit("user-deleted", userpath)


class User(BusBase):

    __gsignals__  = {
        "changed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
            }
    
    def __init__(self, userpath):
        BusBase.__init__(self, path = userpath, interface = "org.freedesktop.Accounts.User")
        
        self.init_dbus_properties()

    ###get properties    
    def get_x_keyboard_layouts(self):
        if self.properties["XKeyboardLayouts"]:
            return map(lambda x:str(x), self.properties["XKeyboardLayouts"])
        else:
            return []

    def get_automatic_login(self):
        return self.properties["AutomaticLogin"]

    def get_locked(self):
        return self.properties["Locked"]

    def get_system_account(self):
        return self.properties["SystemAccount"]

    def get_x_has_messages(self):
        return self.properties["XHasMessages"]

    def get_account_type(self):
        return self.properties["AccountType"]

    def get_password_mode(self):
        return self.properties["PasswordMode"]

    def get_background_file(self):
        return self.properties["BackgroundFile"]

    def get_email(self):
        return self.properties["Email"]

    def get_formats_locale(self):
        return self.properties["FormatsLocale"]

    def get_home_directory(self):
        return self.properties["HomeDirectory"]
    
    def get_icon_file(self):
        return self.properties["IconFile"]

    def get_language(self):
        return self.properties["Language"]

    def get_location(self):
        return self.properties["Location"]

    def get_password_hint(self):
        return self.properties["PasswordHint"]

    def get_real_name(self):
        return self.properties["RealName"]

    def get_shell(self):
        return self.properties["Shell"]

    def get_x_session(self):
        return self.properties["XSession"]

    def get_login_frequency(self):
        return self.properties["LoginFrequency"]

    def get_uid(self):
        return self.properties["Uid"]

    ###set methods
    def set_account_type(self, account_type):
        self.call_async("SetAccountType", account_type, reply_handler = None, error_handler = None)

    def set_automatic_login(self, automatic_login):
        self.call_async("SetAutomaticLogin", automatic_login, reply_handler = None, error_handler = None)

    def set_background_file(self, background_file):
        self.call_async("SetBackgroundFile", background_file, reply_handler = None, error_handler = None)

    def set_email(self, email):
        self.call_async("SetEmail", email, reply_handler = None, error_handler = None)

    def set_formats_locale(self, formats_locale):
        self.call_async("SetFormatsLocale", formats_locale, reply_handler = None, error_handler = None)

    def set_home_directory(self, home_directory):
        self.call_async("SetHomeDirectory", home_directory, reply_handler = None, error_handler = None)

    def set_icon_file(self, filename):
        self.call_async("SetIconFile", filename, reply_handler = None, error_handler = None)

    def set_language(self, language):
        self.call_async("SetLanguage", language, reply_handler = None, error_handler = None)

    def set_location(self, location):
        self.call_async("SetLocation", location, reply_handler = None, error_handler = None)

    def set_locked(self, locked):
        self.call_async("SetLocked", locked, reply_handler = None, error_handler = None)

    def set_password(self, password, hint):
        self.call_async("SetPassword", password, hint, reply_handler = None, error_handler = None)

    def set_password_mode(self, password_mode):
        self.call_async("SetPasswordMode", password_mode, reply_handler = None, error_handler = None)

    def set_real_name(self, name):
        self.call_async("SetRealName", name, reply_handler = None, error_handler = None)

    def set_shell(self, shell):
        self.call_async("SetShell", shell, reply_handler = None, error_handler = None)

    def set_user_name(self, username):
        self.call_async("SetUserName", username, reply_handler = None, error_handler = None)

    def set_x_has_messages(self, has_messages):
        self.call_async("SetXHasMessages", has_messages, reply_handler = None, error_handler = None)

    def set_x_keyboard_layouts(self, layouts):
        self.call_async("SetXKeyboardLayouts", layouts, reply_handler = None, error_handler = None)

    def set_x_session(self, x_session):
        self.call_async("SetXSession", x_session, reply_handler = None, error_handler = None)

    ###signals
    def changed_cb(self):
        self.emit("changed")

if __name__ == "__main__":
    accounts = Accounts()
    accounts.create_user("test", "test", 1)
    gobject.MainLoop().run()
