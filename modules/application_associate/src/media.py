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

import deepin_gsettings

class MediaAutorun(object):
    
    def __init__(self):
        self.media_autorun_settings = deepin_gsettings.new("org.gnome.desktop.media-handling")

        self.cd_content_type = "x-content/audio-cdda"
        self.dvd_content_type = "x-content/video-dvd"
        self.player_content_type = "x-content/audio-player"
        self.photo_content_type = "x-content/image-dcf"
        self.software_content_type = "x-content/unix-software"

        ###other content types
        self.audio_dvd_content_type = "x-content/audio-dvd"
        self.blank_bd_content_type = "x-content/blank-bd"
        self.blank_cd_content_type = "x-content/blank-dvd"
        self.blank_hddvd_content_type = "x-content/blank-hddvd"
        self.video_bluray_content_type = "x-content/video-bluray"
        self.ebook_reader_content_type = "x-content/ebook-reader"
        self.video_hddvd_content_type = "x-content/video-hddvd"
        self.image_picturecd_content_type = "x-content/image-picturecd"
        self.video_svcd_content_type = "x-content/video-svcd"
        self.video_vcd_content_type = "x-content/video-vcd"

        '''
        self.other_content_types = {"x-content/audio-dvd", "audio DVD","音频 DVD"
                                    "x-content/blank-bd", "blank Blu-ray disc","空白蓝光光盘"
                                    "x-content/blank-cd", "blank CD disc","空白 CD 光盘"
                                    "x-content/blank-dvd", "blank DVD disc","空白 DVD 光盘"
                                    "x-content/blank-hddvd", "blank HD DVD disc","空白 HD DVD 光盘"
                                    "x-content/video-bluray", "Blu-ray video disc","蓝光视频光盘"
                                    "x-content/ebook-reader", "e-book reader","电子书阅读器"
                                    "x-content/video-hddvd", "HD DVD video disc","HD DVD 视频光盘"
                                    "x-content/image-picturecd", "Picture CD","图片 CD"
                                    "x-content/video-svcd", "Super Video CD","超级 VCD"
                                    "x-content/video-vcd", "Video CD","视频 CD" }
        '''
    @property
    def automount(self):
        if self.media_autorun_settings.get_boolean("automount") != None:
            return self.media_autorun_settings.get_boolean("automount")
        else:
            return True

    @automount.setter
    def automount(self, automount):
        self.media_autorun_settings.set_boolean("automount", automount)
    
    @property
    def automount_open(self):
        if self.media_autorun_settings.get_boolean("automount-open") != None:
            return self.media_autorun_settings.get_boolean("automount-open")
        else:
            return True

    @automount_open.setter
    def automount_open(self, automount_open):
        self.media_autorun_settings.set_boolean("automount-open", automount_open)

    @property
    def autorun_never(self):
        if self.media_autorun_settings.get_boolean("autorun-never") != None:
            return self.media_autorun_settings.get_boolean("autorun-never")
        else:
            return False

    @autorun_never.setter
    def autorun_never(self, autorun_never):
        self.media_autorun_settings.set_boolean("autorun-never", autorun_never)

    @property
    def autorun_x_content_ignore(self):
        content = self.media_autorun_settings.get_strv("autorun-x-content-ignore")
        if content is not None:
            return content
        else:
            return []

    @autorun_x_content_ignore.setter
    def autorun_x_content_ignore(self, autorun_x_content_ignore):
        self.media_autorun_settings.set_strv("autorun-x-content-ignore", autorun_x_content_ignore)

    def add_x_content_ignore(self, x_content):
        if x_content not in self.autorun_x_content_ignore:
            self.autorun_x_content_ignore += [x_content]
    
    def remove_x_content_ignore(self, x_content):
        if x_content in self.autorun_x_content_ignore:
            content = self.autorun_x_content_ignore
            content.remove(x_content)
            self.autorun_x_content_ignore = content

    @property
    def autorun_x_content_open_folder(self):
        content = self.media_autorun_settings.get_strv("autorun-x-content-open-folder")
        if content is not None:
            return content
        else:
            return []

    @autorun_x_content_open_folder.setter 
    def autorun_x_content_open_folder(self, autorun_x_content_open_folder):
        self.media_autorun_settings.set_strv("autorun-x-content-open-folder",autorun_x_content_open_folder)
        
    def add_x_content_open_folder(self, x_content):
        if x_content not in self.autorun_x_content_open_folder:
            self.autorun_x_content_open_folder += [x_content]
    
    def remove_x_content_open_folder(self, x_content):
        if x_content in self.autorun_x_content_open_folder:
            content = self.autorun_x_content_open_folder
            content.remove(x_content)
            self.autorun_x_content_open_folder = content
    @property
    def autorun_x_content_start_app(self):
        content = self.media_autorun_settings.get_strv("autorun-x-content-start-app")
        if content is not None:
            return content
        else:
            return []

    @autorun_x_content_start_app.setter 
    def autorun_x_content_start_app(self, autorun_x_content_start_app):
        self.media_autorun_settings.set_strv("autorun-x-content-start-app", autorun_x_content_start_app)

    def add_x_content_start_app(self, x_content):
        if x_content not in self.autorun_x_content_start_app:
            self.autorun_x_content_start_app += [x_content]
    
    def remove_x_content_start_app(self, x_content):
        if x_content in self.autorun_x_content_start_app:
            content = self.autorun_x_content_start_app
            content.remove(x_content)
            self.autorun_x_content_start_app = content

if __name__ == "__main__":
    pass
