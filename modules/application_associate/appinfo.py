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

from gi.repository import Gio
import gobject

class ContentType(object):
    
    def __init__(self):
        pass
    
    @classmethod
    def can_be_executable(self, content_type):
        return Gio.content_type_can_be_executable(content_type)

    @classmethod
    def get_description(self, content_type):
        return Gio.content_type_get_description(content_type)

    @classmethod
    def get_registered(self):
        return Gio.content_types_get_registered()

    @classmethod
    def get_from_mime_type(self, mime_type):
        return Gio.content_type_from_mime_type(mime_type)


class AppManager(gobject.GObject):
    
    def __init__(self):
        gobject.GObject.__init__(self)

        self.http_content_type = ContentType.get_from_mime_type("x-scheme-handler/http")
        self.https_content_type = ContentType.get_from_mime_type("x-scheme-handler/https")
        self.mail_content_type = ContentType.get_from_mime_type("x-scheme-handler/mailto")
        self.calendar_content_type = ContentType.get_from_mime_type("text/calendar")
        self.audio_content_type = ContentType.get_from_mime_type("audio/x-vorbis+ogg")
        self.video_content_type = ContentType.get_from_mime_type("video/x-ogm+ogg")
        self.photo_content_type = ContentType.get_from_mime_type("image/jpeg")

        self.http_app = Gio.DesktopAppInfo.get_default_for_type(self.http_content_type, True)
        self.mail_app = Gio.DesktopAppInfo.get_default_for_type(self.mail_content_type, True)
        self.calendar_app = Gio.DesktopAppInfo.get_default_for_type(self.calendar_content_type, True)
        self.audio_app = Gio.DesktopAppInfo.get_default_for_type(self.audio_content_type, True)
        self.video_app = Gio.DesktopAppInfo.get_default_for_type(self.video_content_type, True)
        self.photo_app = Gio.DesktopAppInfo.get_default_for_type(self.photo_content_type, True)

    def reset_type_associations(self, content_type):
        return Gio.DesktopAppInfo.reset_type_associations(content_type)

    def get_appname(self, desktopappinfo):
        if desktopappinfo.get_display_name():
            return desktopappinfo.get_display_name()
        else:
            return desktopappinfo.get_name()

    def set_http_default(self, desktopappinfo):
        desktopappinfo.set_as_default_for_type(self.http_content_type)
        desktopappinfo.set_as_default_for_type(self.https_content_type)

    def set_mail_default(self, desktopappinfo):
        desktopappinfo.set_as_default_for_type(self.mail_content_type)

    def set_calendar_default(self, desktopappinfo):
        desktopappinfo.set_as_default_for_type(self.calendar_content_type)

    def set_audio_default(self, desktopappinfo):
        desktopappinfo.set_as_default_for_type(self.audio_content_type)

    def set_video_default(self, desktopappinfo):
        desktopappinfo.set_as_default_for_type(self.video_content_type)

    def set_photo_default(self, desktopappinfo):
        desktopappinfo.set_as_default_for_type(self.photo_content_type)

    def get_http_default(self):
        return self.http_app

    def get_mail_default(self):
        return self.mail_app

    def get_calendar_default(self):
        return self.calendar_app

    def get_audio_default(self):
        return self.audio_app

    def get_photo_default(self):
        return self.photo_app

    def get_http_applist(self):
        return Gio.DesktopAppInfo.get_recommended_for_type(self.http_content_type)

    def get_mail_applist(self):
        return Gio.DesktopAppInfo.get_recommended_for_type(self.mail_content_type)

    def get_calendar_applist(self):
        return Gio.DesktopAppInfo.get_recommended_for_type(self.calendar_content_type)

    def get_audio_applist(self):
        return Gio.DesktopAppInfo.get_recommended_for_type(self.audio_content_type)

    def get_photo_applist(self):
        return Gio.DesktopAppInfo.get_recommended_for_type(self.photo_content_type)

if __name__ == "__main__":

    app_manager = AppManager()

    # print app_manager.http_content_type
    # print app_manager.mail_content_type
    # print app_manager.calendar_content_type
    # print app_manager.audio_content_type
    # print app_manager.video_content_type
    # print app_manager.photo_content_type
    # print ContentType.get_registered()
    print app_manager.get_http_applist()

    for app in app_manager.get_http_applist():
        print app_manager.get_appname(app)
