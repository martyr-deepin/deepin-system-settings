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

class AppManager(gobject.GObject):
    def __init__(self):
        self.user_config_dir = ""
        self.system_config_dirs = []

    def get_apps(self):
        """docstring for get_apps"""
        pass

    def find_app_with_basename(self):
        """docstring for find_app_with_basename"""
        pass

    def add_app(self):
        """docstring for add_app"""
        pass
    
    def get_user_config_dir(self):
        """docstring for get_user_config_dir"""
        pass

    def get_system_config_dirs(self):
        """docstring for get_system_config_dirs"""
        pass

    def get_dir(self):
        """docstring for get_dir"""
        pass

class App(gobject.GObject):
    """app"""
    
    __gsignals__  = {
            "changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            "removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            }

    def __init__(self):
        self.basename = ""
        self.path = ""
        self.hidden = False
        self.no_display = False
        self.enabled = False
        self.shown = False

        self.name = ""
        self.exec_ = ""
        self.comment = ""
        self.icon = ""
        self.gicon = None
        self.description = ""
        self.xdg_position = None
        self.xdg_system_position = None
        self.save_timeout = None
        self.save_mask = None
        self.old_system_path = ""
        self.skip_next_monitor_event = False

    def __ensure_user_autostart_dir(self):
        """docstring for __ensure_user_autostart_dir"""
        pass

    def update(self):
        """docstring for update"""
        pass

    def get_basename(self):
        """docstring for get_basename"""
        return self.basename

    def get_path(self):
        """docstring for get_path"""
        return self.path

    def get_hidden(self):
        """docstring for get_hidden"""
        return self.hidden

    def get_enabled(self):
        """docstring for get_enabled"""
        return self.enabled

    def set_enabled(self):
        """docstring for set_enabled"""
        pass

    def get_shown(self):
        """docstring for get_shown"""
        return self.shown

    def get_name(self):
        """docstring for get_name"""
        return self.name

    def get_exec(self):
        """docstring for get_exec"""
        return self.exec_

    def get_comment(self):
        """docstring for get_comment"""
        return self.comment

    def get_description(self):
        """docstring for get_description"""
        return self.description

    def get_icon(self):
        """docstring for get_icon"""
        return self.icon

    def reload_at(self):
        """docstring for reload_at"""
        pass

    def get_xdg_position(self):
        """docstring for get_xdg_position"""
        return self.xdg_position

    def get_xdg_system_position(self):
        """docstring for get_xdg_system_position"""
        return self.xdg_system_position

    def set_xdg_system_position(self):
        """docstring for set_xdg_system_position"""
        pass
    
if __name__ == "__main__":
    pass
