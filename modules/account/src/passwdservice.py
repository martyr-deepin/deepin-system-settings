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

import pexpect
import time
import dbus
import dbus.service
import dbus.mainloop.glib
import gobject
    
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

    @dbus.service.method(DBUS_INTERFACE_NAME, in_signature = "ssis", out_signature = "b", 
                         sender_keyword = 'sender', connection_keyword = 'conn')    
    def modify_user_passwd(self, new_password, username, need_old, old_password, sender = None, conn = None):

        if not authWithPolicyKit(sender, conn, "com.deepin.passwdservice.modify-password"):
            print "not authWithPolicyKit"
            return False

        return self.__modify_user_passwd(new_password, username, need_old, old_password)

    def __modify_user_passwd(self, new_password, username, need_old = 0, old_password = None):
        ###for normal password
        if len(new_password) < 6:
            return False

        passwd = pexpect.spawn("/usr/bin/passwd %s" %username)

        if need_old == 1:
            try:
                passwd.expect("UNIX")
                print "input old"
                passwd.sendline(old_password)
                time.sleep(0.1)
            except:
                return False

        try:
            # passwd.expect("输入新的 UNIX 密码：")
            passwd.expect("UNIX")
            print "input new"
            passwd.sendline(new_password)
            time.sleep(0.1)

            # passwd.expect("重新输入新的 UNIX 密码：")
            passwd.expect("UNIX")
            print "confirm new"
            passwd.sendline(new_password)
            time.sleep(0.1)

            print "succeed\n"
            passwd.expect("已成功更新密码")

            return True

        except Exception, e:
            print e
            return False


if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default = True)
    PasswdService()
    gobject.MainLoop().run()
