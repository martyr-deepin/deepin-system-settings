#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
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

import os
from ConfigParser import (RawConfigParser, NoSectionError, NoOptionError)
import common
from xdg_support import get_user_theme_dir, get_system_theme_dir, get_system_wallpaper_dirs

THEME_TYPE_SYSTEM = 1
THEME_TYPE_USER = 2

class ThemeFile(RawConfigParser):
    
    def __init__(self, location, default_location=None):
        RawConfigParser.__init__(self)
        
        if default_location is not None:
            try:
                self.read(default_location)
            except:    
                pass
        
        try:
            self.read(location)
        except:    
            pass
        
        self.location = location    
            
    def set_option(self, section, option, value):
        try:
            self.set(section, option, value)
        except NoSectionError:
            self.add_section(section)
            self.set(section, option, value)
            
    def get_section_options(self, section):        
        try:
            items = self.items(section)
        except NoSectionError:    
            return []
        else:
            return map(lambda (k, v): k, items)

    def get_option(self, section, option, default=None):
        try:
            value = self.get(section, option)
        except NoSectionError:
            value = default
        except NoOptionError:
            value = default
        return value

    def has_option(self, section, option):
        return RawConfigParser.has_option(self, section, option)

    def remove_option(self, section, option):
        RawConfigParser.remove_option(self, section, option)

    def save(self):
        """
            Save the settings to disk
        """
        if self.location is None:
            return

        with open(self.location, 'w') as f:
            self.write(f)
        
    def get_type(self):    
        return self.get_option("theme", "type")
    
    def set_type(self, theme_type):
        self.set_option("theme", "type", theme_type)
        
    def get_name(self):    
        locale_name = "name[%s]" % common.get_system_lang()
        if self.has_option("theme", locale_name):
            return self.get_option("theme", locale_name)
        else:
            return self.get_option("theme", "name")
        
    def set_name(self, theme_name):    
        locale_name = "name[%s]" % common.get_system_lang()
        self.set_option("theme", locale_name, theme_name)
        self.set_option("theme", "name", theme_name)
        
    def get_color(self):    
        return self.get_option("window", "color")
    
    def set_color(self, color):
        self.set_option("window", "color", color)
        
    def get_system_wallpapers(self):    
        wallpapers = []
        names = self.get_section_options("system_wallpaper")
        for wallpaper_dir in get_system_wallpaper_dirs():
            for name in names:
                full_path = os.path.join(wallpaper_dir, name)
                if os.path.exists(full_path):
                    wallpapers.append(full_path)
        return wallpapers            
        
    def get_user_wallpapers(self):
        return self.get_section_options("user_wallpaper")
    
    def add_user_wallpaper(self, path):
        self.set_option("user_wallpaper", path, "")
        
    def is_readonly(self):    
        return self.get_type() == "system"
    
    def get_wallpaper_paths(self):
        return self.get_system_wallpapers() + self.get_user_wallpapers()
    
    def __repr__(self):
        return "<ThemeFile %s>" % self.location
    
    
class ThemeManager(object):    
    
    def __init__(self):
        self.system_themes = []
        self.user_themes = []
        
        self.load_themes()

    def load_themes(self):    
        # load user theme.
            
        for theme_file in os.listdir(get_user_theme_dir()):
            full_theme_file = os.path.join(get_user_theme_dir(), theme_file)
            if full_theme_file.endswith(".ini") and os.path.isfile(full_theme_file):
                self.user_themes.append(ThemeFile(full_theme_file))
                
        # load system themes.        
        for theme_file in os.listdir(get_system_theme_dir()):        
            full_theme_file = os.path.join(get_system_theme_dir(), theme_file)
            if full_theme_file.endswith(".ini") and os.path.isfile(full_theme_file):
                self.system_themes.append(ThemeFile(full_theme_file))
    
    def get_system_themes(self):
        return self.system_themes
    
    def get_user_themes(self):
        return self.user_themes
        
theme_manager = ThemeManager()
