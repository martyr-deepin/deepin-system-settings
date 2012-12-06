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

import gobject
import gio

class AppManager(gobject.GObject):
    
    def __init__(self):
        gobject.GObject.__init__(self)

        self.http_content_type = "x-scheme-handler/http"
        self.https_content_type = "x-scheme-handler/https"
        self.mail_content_type = "x-scheme-handler/mailto"
        self.calendar_content_type = "text/calendar"
        self.audio_content_type = "audio/x-vorbis+ogg"
        self.video_content_type = "video/x-ogm+ogg"
        self.photo_content_type = "image/jpeg"

    def get_app_info(self, commandline, application_name = None, flags = gio.APP_INFO_CREATE_NONE):
        try:
            return gio.AppInfo(commandline, application_name, flags)
        except:
            print "get app info failed"

    def get_default_for_type(self, content_type, must_support_uris = False):
        return gio.app_info_get_default_for_type(content_type, must_support_uris)

    def get_name(self, desktopapp):
        return desktopapp.get_name()

    def get_id(self, desktopapp):
        return desktopapp.get_id()

    def set_default_for_type(self, desktopapp, content_type):
        gio.app_info_reset_type_associations(content_type)

        commandline = desktopapp.get_commandline()
        app = self.get_app_info(commandline)
        try:
            app.set_as_default_for_type(content_type)
        except:    
            print "set app default failed"

    def get_all_for_type(self, content_type):
        return gio.app_info_get_all_for_type(content_type)

if __name__ == "__main__":

    manager = AppManager()
    print "default for http:"
    print manager.get_default_for_type(manager.http_content_type).get_name()

    print "available list for http:"
    for app in manager.get_all_for_type(manager.http_content_type):
        print app.get_name()


    print "set default for http:"    
    for app in manager.get_all_for_type(manager.http_content_type):
        if app != manager.get_default_for_type(manager.http_content_type):
            ###attention, let https same as http
            manager.set_default_for_type(app, manager.http_content_type)
            manager.set_default_for_type(app, manager.https_content_type)
            break
        else:
            continue

    print "now default for http:"    
    print manager.get_default_for_type(manager.http_content_type).get_name()

    # for app in manager.get_all_for_type(manager.http_content_type):
    #     print app.get_id()
