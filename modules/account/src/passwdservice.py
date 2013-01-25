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

import pexpect
import os
import traceback
import shutil
import ConfigParser
import time
import dbus
import dbus.service
import dbus.mainloop.glib
import gobject
import getpass
    
def authWithPolicyKit(sender, connection, action, interactive=1):
    system_bus = dbus.SystemBus()
    obj = system_bus.get_object("org.freedesktop.PolicyKit1", 
                                "/org/freedesktop/PolicyKit1/Authority", 
                                "org.freedesktop.PolicyKit1.Authority")

    authority = dbus.Interface(obj, "org.freedesktop.PolicyKit1.Authority")

    info = dbus.Interface(connection.get_object('org.freedesktop.DBus',
                                                '/org/freedesktop/DBus/Bus', 
                                                False), 
                          'org.freedesktop.DBus')
    pid = info.GetConnectionUnixProcessID(sender) 

    subject = ('unix-process', 
               { 'pid' : dbus.UInt32(pid, variant_level=1),
                 'start-time' : dbus.UInt64(0),
                 }
               )
    details = { '' : '' }
    flags = dbus.UInt32(interactive)
    cancel_id = ''
    (ok, notused, details) = authority.CheckAuthorization(subject, action, details, flags, cancel_id)

    return ok


class PasswdService(dbus.service.Object):

    DBUS_INTERFACE_NAME = "com.deepin.passwdservice"

    def __init__(self, bus = None):
        if bus is None:
            bus = dbus.SystemBus()

        bus_name = dbus.service.BusName(self.DBUS_INTERFACE_NAME, bus = bus)    
        dbus.service.Object.__init__(self, bus_name, "/")
        self.icon_dir = "/var/lib/AccountsService/icons"
        self.config_file = "/var/lib/AccountsService/user.config"
        self.image_list = []
        self.user_icon = {}
        self.cf = ConfigParser.RawConfigParser()

    def __init_users_real(self):
        try:
            sys_bus = dbus.SystemBus()
            account_obj = sys_bus.get_object("org.freedesktop.Accounts", "/org/freedesktop/Accounts")
            for user_path in account_obj.ListCachedUsers():
                user_obj = sys_bus.get_object("org.freedesktop.Accounts", user_path)
                user_interface = dbus.Interface(user_obj, "org.freedesktop.DBus.Properties")
                name = user_interface.Get("org.freedesktop.Accounts.User", "UserName")
                image = user_interface.Get("org.freedesktop.Accounts.User", "IconFile")
                if os.path.exists(image):
                    self.user_icon[name] = image
                else:
                    self.user_icon[name] = None
        except:
            traceback.print_exc()

    def __sync_user_config(self):
        try:
            if not os.path.exists(self.icon_dir):
                os.makedirs(self.icon_dir)
            if not os.path.exists(self.config_file):
                open(self.config_file, "w").close()
                
            self.cf.optionxform = str
            self.cf.read(self.config_file)

            if "UserImage" not in self.cf.sections():
                self.cf.add_section("UserImage")

            if "Count" not in self.cf.sections():
                self.cf.add_section("Count")
            
            for files in os.walk(self.icon_dir):
                self.image_list.extend(files[2])

            for key in self.user_icon.keys():
                value = self.user_icon[key]
                if value and os.path.exists(value):
                    if os.path.basename(value) not in self.image_list:
                        print "copyfile from %s to %s" % (value, os.path.join(self.icon_dir, os.path.basename(value)))
                        shutil.copyfile(value, os.path.join(self.icon_dir, os.path.basename(value)))
                        self.image_list.append(os.path.basename(value))
                    else:
                        pass
                    self.cf.set("UserImage", key, os.path.basename(value))
                else:
                    pass

            for image in self.image_list:
                count = 0
                for user in self.user_icon.iterkeys():
                    if user in self.cf.options("UserImage"):
                        if image == self.cf.get("UserImage", user):
                            count = count + 1
                        else:
                            pass
                    else:
                        pass

                self.cf.set("Count", image, count)

        except:
            traceback.print_exc()

    @dbus.service.method(DBUS_INTERFACE_NAME, in_signature = "s", out_signature = "s", 
                         sender_keyword = 'sender', connection_keyword = 'conn')    
    def get_user_fake_icon(self, username, sender = None, conn = None):
        self.__init_users_real()
        self.__sync_user_config()

        selected_image = ""
        if username in self.user_icon.keys():
            if self.user_icon[username]:
                selected_image = self.user_icon[username]
            else:
                try:
                    selected_image = self.cf.get("UserImage", username)
                except:
                    pass

                if not selected_image:
                    mincount = 100
                    for image in self.image_list:
                        count = self.cf.get("Count", image)
                        if count < mincount:
                            mincount = count
                            selected_image = image
                        else:
                            pass

                if selected_image in self.cf.options("Count"):
                    self.cf.set("Count", selected_image, int(self.cf.get("Count", selected_image)) + 1)
                else:
                    self.cf.set("Count", selected_image, 1)

                self.cf.set("UserImage", username, selected_image)

            self.cf.write(open(self.config_file, "w"))
            return os.path.join(self.icon_dir, selected_image)

        else:
            print "invalid username %s"  % username

    @dbus.service.method(DBUS_INTERFACE_NAME, in_signature = "sss", out_signature = "i", 
                         sender_keyword = 'sender', connection_keyword = 'conn')    
    def modify_user_passwd(self, new_password, username, old_password, sender = None, conn = None):
        if getpass.getuser() != username:
            if not authWithPolicyKit(sender, conn, "com.deepin.passwdservice.modify-password"):
                raise dbus.DBusException("not authWithPolicyKit")

        return self.__modify_user_passwd(new_password, username, old_password)

    def __modify_user_passwd(self, new_password, username, old_password = " "):
        ###for normal password
        if len(new_password) < 6:
            raise Exception("You must choose a longer password")

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


if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default = True)
    PasswdService()
    mainloop = gobject.MainLoop()
    gobject.timeout_add(60000, lambda : mainloop.quit())
    mainloop.run()
