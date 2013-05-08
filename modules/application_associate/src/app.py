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
import threading as td
import time

def threaded(f):
    def wraps(*args, **kwargs):
        t = td.Thread(target=f, args=args, kwargs=kwargs)
        t.start()
    return wraps

class ThreadSet(td.Thread):
    def __init__(self, desktopapp, types, set_func):
        td.Thread.__init__(self)
        #self.setDaemon(True)
        self.desktopapp = desktopapp
        self.types = types
        self.set_func = set_func
        self.stop = False

    def run(self):
        content_types = filter(lambda c: c.startswith(self.types) , gio.content_types_get_registered())
        print len(content_types)
        if content_types:
            for content_type in content_types:
                if self.stop:
                    break
                else:
                    time.sleep(0.1)
                    self.set_func(self.desktopapp, content_type)
            print "ThreadSet finish"
            self.stop_run()

    def stop_run(self):
        print "ThreadSet stop"
        self.stop = True

class AppManager(gobject.GObject):
    
    def __init__(self):
        gobject.GObject.__init__(self)

        self.http_content_type = "x-scheme-handler/http"
        self.https_content_type = "x-scheme-handler/https"
        self.mail_content_type = "x-scheme-handler/mailto"
        self.calendar_content_type = "text/calendar"
        self.editor_content_type = "text/plain"
        self.audio_content_type = "audio/mpeg"
        self.video_content_type = "video/mp4"
        self.photo_content_type = "image/jpeg"
        self.rough_types = ["audio", "video"]
        self.thread = None
    
    def get_app_info(self, commandline, application_name = None, flags = gio.APP_INFO_CREATE_NONE):
        try:
            return gio.AppInfo(commandline, application_name, flags)
        except:
            print "get app info failed"

    def set_default_for_rough_type(self, desktopapp, types):
        if self.thread and self.thread.isAlive():
            self.thread.stop_run()
            self.thread = ThreadSet(desktopapp, types, self.set_default_for_type)
            self.thread.start()
        else:
            self.thread = ThreadSet(desktopapp, types, self.set_default_for_type)
            self.thread.start()


    def get_default_for_type(self, content_type, must_support_uris = False):
        return gio.app_info_get_default_for_type(content_type, must_support_uris)

    def get_name(self, desktopapp):
        return desktopapp.get_name()

    def get_id(self, desktopapp):
        return desktopapp.get_id()

    def set_default_for_type(self, desktopapp, content_type):
        gio.app_info_reset_type_associations(content_type)

        #commandline = desktopapp.get_commandline()
        #app = self.get_app_info(commandline)

        try:
            #print desktopapp
            desktopapp.set_as_default_for_type(content_type)
        except:    
            print "set app default failed for type ",content_type 

    def get_all_for_type(self, content_type):
        apps = gio.app_info_get_all_for_type(content_type)
        default_app = self.get_default_for_type(content_type)
        if default_app and default_app.get_id().startswith("userapp"):
            apps.remove(default_app)

            # get real default
            app = filter(lambda a: a.get_commandline().split(" ")[0] == default_app.get_commandline().split(" ")[0], apps)
            if app:
                apps.remove(app[0])
                apps.insert(0, app[0])
        return apps

if __name__ == "__main__":

    manager = AppManager()
    gio.app_info_reset_type_associations(manager.photo_content_type)
    app = manager.get_default_for_type(manager.photo_content_type)
    print "default for http:", app
        
    print "available list for http:"
    for app in manager.get_all_for_type(manager.photo_content_type):
        print app.get_commandline(), app.get_name(),app.get_id()


    #print "set default for http:"    
    #for app in manager.get_all_for_type(manager.http_content_type):
        #if app != manager.get_default_for_type(manager.http_content_type):
            ####attention, let https same as http
            #manager.set_default_for_type(app, manager.http_content_type)
            #manager.set_default_for_type(app, manager.https_content_type)
            #break
        #else:
            #continue

    #print "now default for http:"    
    #print manager.get_default_for_type(manager.http_content_type).get_name()

    ## for app in manager.get_all_for_type(manager.http_content_type):
    ##     print app.get_id()
