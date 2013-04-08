#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
#             Long Changjin <admin@longchangjin.cn>
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

from account_utils import BusBase
import gobject
import commands
import pexpect
import time
import os
import dbus
import getpass
import subprocess
from consolekit import ck

class Accounts(BusBase):

    __gsignals__  = {
        "user-added":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "user-deleted":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,))
            }

    def __init__(self):
        BusBase.__init__(self, path = "/org/freedesktop/Accounts", interface = "org.freedesktop.Accounts")

        self.bus.add_signal_receiver(self.user_added_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "UserAdded")

        self.bus.add_signal_receiver(self.user_deleted_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "UserDeleted")

        self.init_dbus_properties()

    def get_daemon_version(self):
        return str(self.properties["DaemonVersion"])

    def create_user(self, name, fullname = "", account_type = 0):
        if not fullname:
            fullname = name
        return str(self.dbus_method("CreateUser", name, fullname, account_type))

    def delete_user(self, id, remove_files_flag):
        if self.find_user_by_id(id):
            self.call_async("DeleteUser", id, remove_files_flag, reply_handler = None, error_handler = None)
            #self.dbus_method("DeleteUser", id, remove_files_flag)
        else:
            print "user doesn't exists"

    def find_user_by_id(self, id):
        return str(self.dbus_method("FindUserById", id))

    def find_user_by_name(self, name):
        return str(self.dbus_method("FindUserByName", name))

    def list_cached_users(self):
        return map(lambda x:str(x), self.dbus_method("ListCachedUsers"))

    def get_current_user(self):
        for uid in map(lambda x:User(x).get_uid(), self.list_cached_users()):
            if ck.get_sessions_for_unix_user(uid):
                return uid
            else:
                continue
        else:
            print "must have a user logged in"

    def modify_user_passwd(self, new_password, username, old_password = " "):
        #print "current user:", getpass.getuser(), username
        if getpass.getuser() == username:
            return self.__modify_user_passwd(new_password, username, old_password)
        else:
            bus = dbus.SystemBus()
            dbus_object = bus.get_object("com.deepin.passwdservice", "/")
            dbus_interface = dbus.Interface(dbus_object, "com.deepin.passwdservice")

            return dbus_interface.modify_user_passwd(new_password, username, old_password)

    def __modify_user_passwd(self, new_password, username, old_password = " "):
        ###for normal password
        #if len(new_password) < 6:
            #raise Exception("You must choose a longer password")

        passwd = pexpect.spawn("/usr/bin/passwd %s" %username, timeout=8, env={"LANGUAGE": "en_US"})
        passwd.setecho(False)
        
        if passwd.expect(["(current)", pexpect.EOF, pexpect.TIMEOUT], 5) == 0:
            try:
                #print "input old:'%s'" % old_password
                passwd.sendline(old_password)
                passwd.expect(["new", "New", pexpect.EOF, pexpect.TIMEOUT], 5)
                if not passwd.isalive():
                    return passwd.exitstatus
            except Exception, e:
                raise e
        try:
            #print "input new"
            passwd.sendline(new_password)
            time.sleep(0.1)

            #print "confirm new"
            passwd.sendline(new_password)
            time.sleep(0.1)

            #print passwd.read()
            code = -1
            if passwd.expect(["Bad", pexpect.EOF, pexpect.TIMEOUT], 3) == 0:
                code = -2
            if passwd.isalive():
                if not passwd.terminate():
                    passwd.kill(9)
                return code
            #print "succeed\n"
            #passwd.expect("已成功更新密码")
            return passwd.exitstatus
        except Exception, e:
            raise e

    def get_username_from_uid(self, uid):
        if self.find_user_by_id(uid):
            return User(self.find_user_by_id(uid)).get_user_name()

    def get_exist_username_list(self):
        return commands.getoutput("awk -F : '{print $1}' /etc/passwd").split("\n")

    def is_username_exists(self, username):
        return username in self.get_exist_username_list()

    def user_added_cb(self, userpath):
        self.emit("user-added", userpath)

    def user_deleted_cb(self, userpath):
        self.emit("user-deleted", userpath)

accounts = Accounts()

class User(BusBase):

    __gsignals__  = {
        "changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            }
    
    def __init__(self, userpath):
        BusBase.__init__(self, path = userpath, interface = "org.freedesktop.Accounts.User")
        self.bus.add_signal_receiver(self.changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "Changed")
        self.init_dbus_properties()

    ###get properties    
    def get_x_keyboard_layouts(self):
        if self.properties["XKeyboardLayouts"]:
            return map(lambda x:str(x), self.properties["XKeyboardLayouts"])
        else:
            return []

    def get_automatic_login(self):
        return bool(self.properties["AutomaticLogin"])

    def get_locked(self):
        return bool(self.properties["Locked"])

    def get_system_account(self):
        return bool(self.properties["SystemAccount"])

    def get_x_has_messages(self):
        return bool(self.properties["XHasMessages"])

    def get_account_type(self):
        return int(self.properties["AccountType"])

    def get_password_mode(self):
        return int(self.properties["PasswordMode"])

    def get_background_file(self):
        return str(self.properties["BackgroundFile"])

    def get_email(self):
        return str(self.properties["Email"])

    def get_formats_locale(self):
        return str(self.properties["FormatsLocale"])

    def get_home_directory(self):
        return str(self.properties["HomeDirectory"])
    
    def get_icon_file(self):
        if self.properties["IconFile"] and os.path.exists(self.properties["IconFile"]):
            return str(self.properties["IconFile"])
        else:
            bus = dbus.SystemBus()
            dbus_object = bus.get_object("com.deepin.passwdservice", "/")
            dbus_interface = dbus.Interface(dbus_object, "com.deepin.passwdservice")

            return dbus_interface.get_user_fake_icon(self.get_user_name())

    def get_language(self):
        return str(self.properties["Language"])

    def get_location(self):
        return str(self.properties["Location"])

    def get_password_hint(self):
        return str(self.properties["PasswordHint"])

    def get_real_name(self):
        return str(self.properties["RealName"])

    def get_shell(self):
        return str(self.properties["Shell"])
    
    def get_user_name(self):
        return str(self.properties["UserName"])

    def get_x_session(self):
        return str(self.properties["XSession"])

    def get_login_frequency(self):
        return long(self.properties["LoginFrequency"])

    def get_uid(self):
        return long(self.properties["Uid"])

    def get_groups(self):
        name = self.get_user_name()
        try:
            p = subprocess.Popen(['groups', name], stdout=subprocess.PIPE)
            p.wait()
            s = p.stdout.read()
            if not s.startswith(name):
                return []
            return s.split(':')[1].strip().split(' ')
        except:
            return []

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

    def set_password(self, password, hint = ""):
        self.call_async("SetPassword", password, hint, reply_handler = None, error_handler = None)

    def set_password_mode(self, password_mode = 1):
        self.call_async("SetPasswordMode", password_mode, reply_handler = None, error_handler = None)

    def modify_password(self, old_password, new_password):
        pass

    def set_real_name(self, name):
        self.call_async("SetRealName", name, reply_handler = None, error_handler = None)

    def set_shell(self, shell = "/bin/bash"):
        self.call_async("SetShell", shell, reply_handler = None, error_handler = None)

    def set_user_name(self, username):
        if username == self.get_user_name():
            pass
        elif username in accounts.get_exist_username_list():
            pass
        else:
            self.call_async("SetUserName", username, reply_handler = None, error_handler = None)

    def set_x_has_messages(self, has_messages):
        self.call_async("SetXHasMessages", has_messages, reply_handler = None, error_handler = None)

    def set_x_keyboard_layouts(self, layouts):
        self.call_async("SetXKeyboardLayouts", layouts, reply_handler = None, error_handler = None)

    def set_x_session(self, x_session):
        self.call_async("SetXSession", x_session, reply_handler = None, error_handler = None)

    def set_groups(self, groups):
        bus = dbus.SystemBus()
        dbus_object = bus.get_object("com.deepin.passwdservice", "/")
        dbus_interface = dbus.Interface(dbus_object, "com.deepin.passwdservice")

        return dbus_interface.modify_user_groups(
            self.get_user_name(), groups)

    ###signals
    def changed_cb(self):
        self.init_dbus_properties()
        self.emit("changed")

if __name__ == "__main__":
    accounts = Accounts()
    print accounts.get_current_user()

    # user_path = accounts.create_user("acu", "acu", 0)
    # user = User(user_path)
    
    # user.set_password("acu", "acu")
    # # user.set_user_name("account_user")
    # # print accounts.get_exist_username_list()

    user_path = accounts.find_user_by_name("lfs");
    user = User(user_path)

    user.set_password("lfs", "lfs");

    gobject.MainLoop().run()
