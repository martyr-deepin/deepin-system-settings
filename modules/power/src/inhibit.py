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

import dbus
import traceback

import gobject
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default = True)

gs_bus = dbus.SessionBus()

try:
    gs_proxy = gs_bus.get_object("org.gnome.SessionManager", "/org/gnome/SessionManager")
    gs_interface = dbus.Interface(gs_proxy, "org.gnome.SessionManager")
except:
    traceback.print_exc()

def is_logout_inhibit():
    try:
        return gs_interface.IsInhibited(1)
    except:
        return False

def is_switch_user_inhibit():
    try:
        return gs_interface.IsInhibited(2)
    except:
        return False

def is_suspend_inhibit():
    try:
        return gs_interface.IsInhibited(4)
    except:
        return False

def is_idle_inhibit():
    try:
        return gs_interface.IsInhibited(8)
    except:
        return False

def get_inhibit_programs():
    '''return list of (exec_path, inhibit_reason)
       you can write another if you don't like the return result 
    '''
    programs = []
    for inhibit_path in gs_interface.GetInhibitors():
        try:
            inhibit_proxy = gs_bus.get_object("org.gnome.SessionManager", inhibit_path)
            inhibit_interface = dbus.Interface(inhibit_proxy, "org.gnome.SessionManager.Inhibitor")
        except:
            traceback.print_exc()

        app_id = str(inhibit_interface.GetAppId())
        reason = inhibit_interface.GetReason()
        programs.append((app_id, reason))
        
    return programs

def get_inhibis():
    return gs_interface.GetInhibitors()

def get_inhibit_info(path):
    try:
        inhibit_proxy = gs_bus.get_object("org.gnome.SessionManager", path)
        inhibit_interface = dbus.Interface(inhibit_proxy, "org.gnome.SessionManager.Inhibitor")
    except:
        traceback.print_exc()
        return ("", "")

    app_id = str(inhibit_interface.GetAppId())
    reason = inhibit_interface.GetReason()
    return (app_id, reason)

def test_cb(path):
    print "inhibit added path", path
    print "inhibit programs", get_inhibit_programs()


if __name__ == "__main__":

    gs_bus.add_signal_receiver(test_cb, 
                                     dbus_interface = "org.gnome.SessionManager",
                                     path = "/org/gnome/SessionManager",
                                     signal_name = "InhibitorAdded")
    gobject.MainLoop().run()
