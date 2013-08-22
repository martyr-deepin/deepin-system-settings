#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
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
import gobject
import re
import traceback
import time
import datetime
import deepin_tz

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default = True)

name_re = re.compile("[0-9a-zA-Z-]*")
datetime_bus = dbus.SystemBus()

def valid_object_path(object_path):
    if not isinstance(object_path, str):
        return False

    if not object_path.startswith("/"):
        return False

    return all(map(lambda x:name_re.match(x), object_path.split(".")))    

class InvalidPropType(Exception):
    
    def __init__(self, prop_name, need_type, real_type = "string"):
        self.prop_name = prop_name
        self.need_type = need_type
        self.real_type = real_type

    def __str__(self):
        return repr("property %s need type %s ,but given type is :%s",
                    (self.prop_name, self.need_type, self.real_type))

class InvalidObjectPath(Exception):
    
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return repr("InvalidObjectPath:" + self.path)


class BusBase(gobject.GObject):
    
    def __init__(self, path, interface, service = "org.gnome.SettingsDaemon.DateTimeMechanism", bus = datetime_bus):

        if valid_object_path(path):
            self.object_path = path
        else:
            raise InvalidObjectPath(path)

        self.object_interface = interface
        self.service = service
        self.bus = bus
        self.init_dbus_service()

    def init_dbus_service(self):
        try:
            self.dbus_proxy = self.bus.get_object(self.service, self.object_path)
            self.dbus_interface = dbus.Interface(self.dbus_proxy, self.object_interface)
        except dbus.exceptions.DBusException:
            traceback.print_exc()

    def init_dbus_properties(self):        
        try:
            self.properties_interface = dbus.Interface(self.dbus_proxy, "org.freedesktop.DBus.Properties" )
        except dbus.exceptions.DBusException:
            traceback.print_exc()

        if self.properties_interface:
            try:
                self.properties = self.properties_interface.GetAll(self.object_interface)
            except:
                print "get properties failed"
                traceback.print_exc()

    def dbus_method(self, method_name, *args, **kwargs):
        try:
            return apply(getattr(self.dbus_interface, method_name), args, kwargs)
        except dbus.exceptions.DBusException:
            self.init_dbus_service()
            try:
                return apply(getattr(self.dbus_interface, method_name), args, kwargs)
            except dbus.exceptions.DBusException:
                print "call dbus method failed:%s\n" % method_name
                traceback.print_exc()

    def call_async(self, method_name, *args, **kwargs):
        try:
            return apply(getattr(self.dbus_interface, method_name), args, kwargs)
        except dbus.exceptions.DBusException:
            self.init_dbus_service()
            try:
                return apply(getattr(self.dbus_interface, method_name), args, kwargs)
            except dbus.exceptions.DBusException:
                print "call dbus method failed:%s\n" % method_name
                traceback.print_exc()

class DeepinDateTime(BusBase):
    
    def __init__(self):
        BusBase.__init__(self, path = "/", interface = "org.gnome.SettingsDaemon.DateTimeMechanism")

    def adjust_time(self, seconds_to_add):
        self.call_async("AdjustTime", seconds_to_add)

    def can_set_time(self):
        return self.dbus_method("CanSetTime")

    def can_set_timezone(self):
        return self.dbus_method("CanSetTimezone")

    def can_set_using_ntp(self):
        if self.dbus_method("CanSetUsingNtp") == 2:
            return True
        else:
            return False

    def get_hardware_clock_using_utc(self):
        return self.dbus_method("GetHardwareClockUsingUtc")
    
    def get_timezone(self):
        return self.dbus_method("GetTimezone")

    def get_gmtoff(self):
        return deepin_tz.gmtoff()

    def get_using_ntp(self):
        if self.dbus_method("GetUsingNtp"):
            return self.dbus_method("GetUsingNtp")[1]
        else:
            return False

    def set_date(self, day, month, year):
        return self.call_async("SetDate", day, month, year,
                                reply_handler = self.set_date_reply, error_handler = self.set_date_error)

    def set_date_reply(self):
        print "set date reply"

    def set_date_error(self, error = None):
        print "set date error"
        print error

    def set_hardware_clock_using_utc(self, is_using_utc):
        return self.call_async("SetHardwareClockUsingUTC", is_using_utc, 
                                reply_handler = self.set_using_utc_reply, error_handler = self.set_using_utc_error)

    def set_using_utc_reply(self):
        print "set using utc reply"

    def set_using_utc_error(self, error = None):
        print "set using utc error"

    def set_time(self, seconds_since_epoch):
        if self.can_set_time():
            return self.call_async("SetTime", seconds_since_epoch,
                                reply_handler = self.set_time_reply, error_handler = self.set_time_error)

        else:
            self.set_time_error()

    def set_time_reply(self):
        print "set time reply"

    def set_time_error(self, error = None):
        print "set time error"
        print error

    def set_time_by_hms(self, hour, min, sec):
        datetime_str = "%04d-%02d-%02d %02d:%02d:%02d" % (time.localtime().tm_year, 
                                                    time.localtime().tm_mon, 
                                                    time.localtime().tm_mday, 
                                                    hour, 
                                                    min, 
                                                    sec)
        d = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        seconds_since_epoch = time.mktime(d.timetuple())
        return self.set_time(seconds_since_epoch)

    def set_timezone_by_gmtoff(self, gmtoff):
        tz = "Asia/Shanghai"

        if gmtoff == -11:
            tz = "Pacific/Pago_Pago"
        elif gmtoff == -10:
            tz = "Pacific/Tahiti"
        elif gmtoff == -9:
            tz = "Pacific/Gambier"
        elif gmtoff == -8:
            tz = "America/Los_Angeles"
        elif gmtoff == -7:
            tz = "America/Edmonton"
        elif gmtoff == -6:
            tz = "America/Rainy_River"
        elif gmtoff == -5:
            tz = "America/Montreal"
        elif gmtoff == -4:
            tz = "America/Goose_Bay"
        elif gmtoff == -3:
            tz = "America/Godthab"
        elif gmtoff == -2:
            tz = "America/Noronha"
        elif gmtoff == -1:
            tz = "America/Scoresbysund"
        elif gmtoff == 0:
            tz = "Africa/Bamako"
        elif gmtoff == 1:
            tz = "Africa/Ndjamena"
        elif gmtoff == 2:
            tz = "Africa/Lusaka"
        elif gmtoff == 3:
            tz = "Africa/Addis_Ababa"
        elif gmtoff == 4:
            tz = "Asia/Dubai"
        elif gmtoff == 5:
            tz = "Indian/Maldives"
        elif gmtoff == 6:
            tz = "Asia/Almaty"
        elif gmtoff == 7:
            tz = "Asia/Phnom_Penh"
        elif gmtoff == 8:
            tz = "Asia/Shanghai"
        elif gmtoff == 9:
            tz = "Asia/Tokyo"
        elif gmtoff == 10:
            tz = "Asia/Yakutsk"
        elif gmtoff == 11:
            tz = "Pacific/Guadalcanal"
        elif gmtoff == 12:
            tz = "Asia/Kamchatka"
        
        self.set_timezone(tz)
    
    def set_timezone(self, tz):
        if self.can_set_timezone():
            return self.call_async("SetTimezone", tz,
                                reply_handler = self.set_timezone_reply, error_handler = self.set_timezone_error)
        else:
            self.set_timezone_error()

    def set_timezone_reply(self):
        print "set timezone reply"

    def set_timezone_error(self, error = None):
        print "set timezone error"
        print error

    def sync_time(self):
        return self.dbus_method("SyncTime")

    def set_using_ntp(self, is_using_ntp):
        try:
            if is_using_ntp:
                self.sync_time()

            if self.can_set_using_ntp():
                if bool(self.get_using_ntp()) == bool(is_using_ntp):
                    pass
                else:
                    return self.call_async("SetUsingNtp", is_using_ntp, 
                        reply_handler = self.set_using_ntp_reply, 
                        error_handler = self.set_using_ntp_error)
                        
        except:
            print "set using ntp failed"
            traceback.print_exc()

    def set_using_ntp_reply(self):
        print "set using ntp reply"

    def set_using_ntp_error(self, error = None):
        print "set using ntp error"
        print error

if __name__ == "__main__":
    deepin_dt = DeepinDateTime()
    print "get timezone:"

    print deepin_dt.get_timezone(), deepin_dt.get_gmtoff()
    deepin_dt.set_timezone("Asia/Shanghai")

    for i in range(1000):
        #print deepin_dt.get_timezone(), deepin_dt.get_gmtoff()
        #deepin_dt.set_timezone("Asia/Shanghai")
        deepin_dt.set_using_ntp(True)
        print "using", deepin_dt.get_using_ntp()
        deepin_dt.set_using_ntp(False)
        print "using", deepin_dt.get_using_ntp()
    

    #gobject.MainLoop().run()
