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

class MediaAutorun(object):
    
    def __init__(self):
        self.media_autorun_settings = Gio.Settings.new("org.gnome.desktop.media-handling")
        
    def get_automount(self):
        if self.media_autorun_settings.get_boolean("automount") != None:
            return self.media_autorun_settings.get_boolean("automount")
        else:
            return True

    def set_automount(self, automount):
        self.media_autorun_settings.set_boolean("automount", automount)
    
    def get_automount_open(self):
        if self.media_autorun_settings.get_boolean("automount-open") != None:
            return self.media_autorun_settings.get_boolean("automount-open")
        else:
            return True

    def set_automount_open(self, automount_open):
        self.media_autorun_settings.set_boolean("automount-open", automount_open)

    def get_autorun_never(self):
        if self.media_autorun_settings.get_boolean("autorun-never") != None:
            return self.media_autorun_settings.get_boolean("autorun-never")
        else:
            return False

    def set_autorun_never(self, autorun_never):
        self.media_autorun_settings.set_boolean("autorun-never", autorun_never)

    ###Attention for below list    
    def get_autorun_x_content_ignore(self):
        if self.media_autorun_settings.get_autorun_x_content_ignore() != None:
            return self.media_autorun_settings.get_autorun_x_content_ignore()
        else:
            return []

    def set_autorun_x_content_ignore(self, autorun_x_content_ignore):
        self.media_autorun_settings.set_strv("autorun-x-content-ignore", autorun_x_content_ignore)

    def get_autorun_x_content_open_folder(self):
        if self.media_autorun_settings.get_autorun_x_content_open_folder() != None:
            return self.media_autorun_settings.get_autorun_x_content_open_folder()
        else:
            return []
        
    def set_autorun_x_content_open_folder(self, autorun_x_content_open_folder):
        self.media_autorun_settings.set_strv("autorun-x-content-open-folder",autorun_x_content_open_folder)
        
    def get_autorun_x_content_start_app(self):
        if self.media_autorun_settings.get_autorun_x_content_start_app() != None:
            return self.media_autorun_settings.get_autorun_x_content_start_app()
        else:
            return []
        
    def set_autorun_x_content_start_app(self, autorun_x_content_start_app):
        self.media_autorun_settings.set_strv("autorun-x-content-start-app", autorun_x_content_start_app)


if __name__ == "__main__":
    pass
