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

from account_utils import BusBase
import gobject

class ConsoleKit(BusBase):

    __gsignals__  = {
        "seat-added":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "seat-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "system-idle-hint-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))
            }

    def __init__(self):
        BusBase.__init__(self, path = "/org/freedesktop/ConsoleKit/Manager", interface = "org.freedesktop.ConsoleKit.Manager", 
                         service = "org.freedesktop.ConsoleKit")

        self.bus.add_signal_receiver(self.seat_added_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "SeatAdded")

        self.bus.add_signal_receiver(self.seat_removed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "SeatRemoved")

        self.bus.add_signal_receiver(self.system_idle_hint_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "SystemIdleHintChanged")

    ###Methods
    def can_restart(self):
        return bool(self.dbus_method("CanRestart"))
        
    def can_stop(self):
        return bool(self.dbus_method("CanStop"))
        
    def close_session(self, cookie):
        return bool(self.dbus_method("CloseSession", cookie))

    def get_current_session(self):
        return str(self.dbus_method("GetCurrentSession"))

    def get_seats(self):
        if self.dbus_method("GetSeats"):
            return map(lambda x:str(x), self.dbus_method("GetSeats"))
        else:
            return []

    def get_session_for_cookie(self, cookie):
        return str(self.dbus_method("GetSessionForCookie", cookie))

    def get_session_for_unix_process(self, pid):
        return str(self.dbus_method("GetSessionForUnixProcess", pid))

    def get_sessions(self):
        if self.dbus_method("GetSessions"):
            return map(lambda x:str(x), self.dbus_method("GetSessions"))
        else:
            return []

    def get_sessions_for_unix_user(self, uid):
        if self.dbus_method("GetSessionsForUnixUser", uid):
            return map(lambda x:str(x), self.dbus_method("GetSessionsForUnixUser", uid))
        else:
            return []

    def get_sessions_for_user(self, uid):
        if self.dbus_method("GetSessionsForUser", uid):
            return map(lambda x:str(x), self.dbus_method("GetSessionsForUser", uid))
        else:
            return []

    def get_system_idle_hint(self):
        return bool(self.dbus_method("GetSystemIdleHint"))

    def get_system_idle_since_hint(self):
        return str(self.dbus_method("GetSystemIdleSinceHint"))

    def open_session(self):
        return str(self.dbus_method("OpenSession"))

    def open_session_with_parameters(self, parameters):
        return str(self.dbus_method("OpenSessionWithParameters", parameters))

    def restart(self):
        self.dbus_method("Restart")

    def stop(self):
        self.dbus_method("Stop")

    ###Signals    
    def seat_added_cb(self, seat):
        self.emit("seat-added", seat)

    def seat_removed_cb(self, seat):
        self.emit("seat-removed", seat)

    def system_idle_hint_changed_cb(self, hint):
        self.emit("system-idle-hint-changed", hint)

class Seat(BusBase):

    __gsignals__  = {
        "active-session-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "device-added":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, str)),
        "device-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str, str)),
        "session-added":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        "session-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,))
            }
    
    def __init__(self, seatpath):
        BusBase.__init__(self, path = seatpath, interface = "org.freedesktop.ConsoleKit.Seat", 
                         service = "org.freedesktop.ConsoleKit" )

        self.bus.add_signal_receiver(self.active_session_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "ActiveSessionChanged")

        self.bus.add_signal_receiver(self.device_added_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "DeviceAdded")

        self.bus.add_signal_receiver(self.device_removed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "DeviceRemoved")

        self.bus.add_signal_receiver(self.session_added_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "SessionAdded")

        self.bus.add_signal_receiver(self.session_removed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "SessionRemoved")

    ####Methods    
    def activate_session(self, ssid):
        return self.dbus_method("ActivateSession", ssid)

    def can_activate_sessions(self):
        return bool(self.dbus_method("CanActivateSessions"))
        
    def get_active_session(self):
        return str(self.dbus_method("GetActiveSession"))

    def get_devices(self):
        if self.dbus_method("GetDevices"):
            return map(lambda x:(str(x[0]), str(x[1])), self.dbus_method("GetDevices"))
        else:
            return []

    def get_id(self):
        return str(self.dbus_method("GetId"))

    def get_sessions(self):
        if self.dbus_method("GetSessions"):
            return map(lambda x:str(x), self.dbus_method("GetSessions"))
        else:
            return []

    ###signals
    def active_session_changed_cb(self, session):
        self.emit("active-session-changed", session)

    def device_added_cb(self, arg0, arg1):
        self.emit("device-added", arg0, arg1)

    def device_removed_cb(self, arg0, arg1):
        self.emit("device-removed", arg0, arg1)

    def session_added_cb(self, session):
        self.emit("session-added", session)

    def session_removed_cb(self, session):
        self.emit("session-removed", session)


class Session(BusBase):

    __gsignals__  = {
        "active-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (bool,)),
        "idle-hint-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (bool,)),
        "lock":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "unlock":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
            }
    
    def __init__(self, seatpath):
        BusBase.__init__(self, path = seatpath, interface = "org.freedesktop.ConsoleKit.Session", 
                         service = "org.freedesktop.ConsoleKit" )

        self.bus.add_signal_receiver(self.active_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "ActiveChanged")

        self.bus.add_signal_receiver(self.idle_hint_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "IdleHintChanged")

        self.bus.add_signal_receiver(self.lock_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "Lock")

        self.bus.add_signal_receiver(self.unlock_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "Unlock")

    ###Methods
    def activate(self):
        return self.dbus_method("Activate")

    def get_creation_time(self):
        return str(self.dbus_method("GetCreationTime"))

    def get_display_device(self):
        return str(self.dbus_method("GetDisplayDevice"))

    def get_id(self):
        return str(self.dbus_method("GetId"))

    def get_idle_hint(self):
        return bool(self.dbus_method("GetIdleHint"))

    def get_idle_since_hint(self):
        return str(self.dbus_method("GetIdleSinceHint"))

    def get_login_session_id(self):
        return str(self.dbus_method("GetLoginSessionId"))

    def get_remote_host_name(self):
        return str(self.dbus_method("GetRemoteHostName"))

    def get_seat_id(self):
        return str(self.dbus_method("GetSeatId"))

    def get_session_type(self):
        return str(self.dbus_method("GetSessionType"))

    def get_unix_user(self):
        return int(self.dbus_method("GetUnixUser"))

    def get_user(self):
        return int(self.dbus_method("GetUser"))

    def get_x11_display(self):
        return str(self.dbus_method("GetX11Display"))

    def get_x11_display_device(self):
        return str(self.dbus_method("GetX11DisplayDevice"))

    def is_active(self):
        return bool(self.dbus_method("IsActive"))

    def is_local(self):
        return bool(self.dbus_method("IsLocal"))

    def lock(self):
        return self.dbus_method("Lock")

    def set_idle_hint(self, hint):
        return self.dbus_method("SetIdleHint", hint)
    
    def unlock(self):
        return self.dbus_method("Unlock")

    ###Signals    
    def active_changed_cb(self, active):
        self.emit("active-changed", active)
        
    def idle_hint_changed_cb(self, hint):
        self.emit("idle-hint-changed", hint)

    def lock_cb(self):
        self.emit("lock")

    def unlock_cb(self):
        self.emit("unlock")

ck = ConsoleKit()
        
if __name__ == "__main__":
    pass
