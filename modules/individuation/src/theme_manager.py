#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
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

import os
from ConfigParser import (RawConfigParser, NoSectionError, NoOptionError)
import common
from xdg_support import (get_user_theme_dir, get_system_theme_dir, 
                         get_system_wallpaper_dirs, get_config_path)

import deepin_gsettings
from settings import global_settings
from nls import _

THEME_TYPE_SYSTEM = 1
THEME_TYPE_USER = 2

class ThemeFile(RawConfigParser):
    
    def __init__(self, location, default_location=None):
        RawConfigParser.__init__(self)
        
        if default_location is None:
            default_location = get_config_path("default_theme.ini")
            
        try:
            self.read(default_location)
        except:    
            pass
        
        try:
            self.read(location)
        except:    
            pass
        
        self.location = location    
        if default_location is None:
            default_location = get_config_path("default_theme.ini")
            
        try:
            self.read(default_location)
        except:    
            pass
        
        try:
            self.read(location)
        except:    
            pass
        
        self.location = location
        
    def optionxform(self, optionstr):
        return optionstr
            
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
        if not self.has_option(section, option):
            return

        RawConfigParser.remove_option(self, section, option)

    def reload(self):
        self = self.__init__(self.location)

    def save(self):
        """
            Save the settings to disk
        """
        if self.location is None:
            return

        with open(self.location, 'w') as f:
            self.write(f)
        
    def get_editable(self):    
        return self.get_option("theme", "editable")
    
    def set_editable(self, value):
        self.set_option("theme", "editable", value)
        
    @property    
    def isdefault(self):    
        value =  self.get_option("theme", "default", "False")
        if value != "True": return False
        return True
    
    def set_background_duration(self, duration):
        self.set_option("background", "duration", str(duration))
        background_gsettings.set_int("background-duration", duration)        
    
    def get_background_duration(self):
        value = self.get_option("background", "duration", 10)
        return int(value)
    
    def get_background_draw_mode(self):
        return self.get_option("background", "draw_mode", "Scaing")
    
    def set_background_draw_mode(self, value):
        self.set_option("background", "draw_mode", value)
        background_gsettings.set_string("draw-mode", value)
        
    def get_background_random_mode(self, ret_string=False):    
        value = self.get_option("background", "random_mode", "false")        
        if value != "True": 
            result = False
        else:    
            result = True
            
        if ret_string:    
            return "Random" if result else "Sequential"
        else:
            return result
    
    def set_background_random_mode(self, value):
        self.set_option("background", "random_mode", str(value))
        self.save()
        if value:
            background_gsettings.set_string("cross-fade-auto-mode", "Random")
        else:    
            background_gsettings.set_string("cross-fade-auto-mode", "Sequential")
        
    def get_name(self):
        lang = common.get_system_lang()
        if self.has_option("name", lang):
            return self.get_option("name", lang)
        else:
            return self.get_option("name", "default", "")
 
    def get_default_name(self):
        return self.get_option("name", "default", "")

    def set_default_name(self, theme_name):    
        self.set_option("name", "default", theme_name)
        
    def set_locale_name(self, theme_name):    
        lang = common.get_system_lang()
        self.set_option("name", lang, theme_name)
        
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
    
    def copy_theme(self, theme):
        """
            Copies one all of the settings contained
            in this instance to another

            :param settings: the settings object to copy to
            :type settings: :class:`xl.settings.SettingsManager`
        """
        
        self.clear()
        for section in theme.sections():
            for (option, value) in theme.items(section):
                self._set_direct(section, option, value)
                
    def clear(self):            
        for section in self.sections():
            self.remove_section(section)
                
    def _set_direct(self, section, option, value):
        """
            Sets the option directly to the value,
            only for use in copying settings.

            :param option: the option path
            :type option: string
            :param value: the value to set
            :type value: any
        """
        try:
            self.set(section, option, value)
        except NoSectionError:
            self.add_section(section)
            self.set(section, option, value)
        
    def get_user_wallpapers(self):
        save_wallpapers = self.get_section_options("user_wallpaper")
        user_wallpapers = []
        is_changed = False
        
        for image in save_wallpapers:
            if os.path.exists(image):
                user_wallpapers.append(image)
            else:    
                self.is_changed = True
                try:
                    self.remove_option("user_wallpaper", image)
                except:    
                    pass
                
        if is_changed:        
            self.save()
        return user_wallpapers
    
    def add_user_wallpapers(self, paths):
        for path in paths:
            self.set_option("user_wallpaper", path, "False")
        self.save()    
        
    def get_user_wallpaper_status(self, path):    
        if self.has_option("user_wallpaper", path):
            value = self.get_option("user_wallpaper", path)
            if value != "True": return False
            return True
        return False
    
    def set_user_wallpaper_status(self, path, value):
        self.set_option("user_wallpaper", path, str(value))
        
    def set_system_wallpaper_status(self, path, value):    
        path = path.split("/")[-1]
        self.set_option("system_wallpaper", path, str(value))
        
    def get_system_wallpaper_status(self, path):    
        path = path.split("/")[-1]
        if self.has_option("system_wallpaper", path):
            value = self.get_option("system_wallpaper", path)
            if value != "True": return False
            return True
        else:
            return False
    
    def get_wallpaper_paths(self):
        return self.get_system_wallpapers() + self.get_user_wallpapers()
    
    def get_enable_wallpaper_paths(self):
        system_wallpapers = filter(self.get_system_wallpaper_status, self.get_system_wallpapers())
        user_wallpapers = filter(self.get_user_wallpaper_status, self.get_user_wallpapers())
        return system_wallpapers + user_wallpapers
    
    def __repr__(self):
        return "<ThemeFile %s>" % self.get_name()
    
    def __hash__(self):
        return hash(self.location)
    
    def __cmp__(self, other):
        if not other: return -1
        try:
            return cmp(self.get_name(), other.get_name())
        except AttributeError: return -1
        
    def __eq__(self, other):    
        try:
           return self.location == other.location
        except: return False
    
class ThemeManager(object):    
    
    def __init__(self):
        self.system_themes = {}
        self.user_themes = {}

    def load(self):    
        # load user theme.

        for theme_file in os.listdir(get_user_theme_dir()):
            full_theme_file = os.path.join(get_user_theme_dir(), theme_file)
            if full_theme_file.endswith(".ini") and os.path.isfile(full_theme_file):
                theme_file_object = ThemeFile(full_theme_file)
                self.user_themes[theme_file_object.location] = theme_file_object

        # load system themes.        
        for theme_file in os.listdir(get_system_theme_dir()):        
            full_theme_file = os.path.join(get_system_theme_dir(), theme_file)
            if full_theme_file.endswith(".ini") and os.path.isfile(full_theme_file):
                theme_file_object = ThemeFile(full_theme_file)
                self.system_themes[theme_file_object.location] = theme_file_object
                
    def get_system_themes(self):
        return self.system_themes.values()
    
    def get_user_themes(self):
        themes = []
        untitled_theme = ThemeFile(os.path.join(get_user_theme_dir(), "untitled.ini"))
        themes.append(untitled_theme)
        
        for item in self.user_themes.values():
            if item.get_default_name() == "untitled":
                continue
            themes.append(item)

        if not themes:
            return [self.untitled_theme(self.get_default_theme())]
        return themes
        
    def get_default_theme(self):    
        for theme in self.system_themes.values():
            if theme.isdefault:
                return theme
    
    def get_theme(self, location):
        pass
    
    def create_new_theme(self, name, copy_theme=None):
        new_theme_path = os.path.join(get_user_theme_dir(), "%s.ini" % name)
        new_theme = ThemeFile(new_theme_path)
        if copy_theme:
            new_theme.copy_theme(copy_theme)
        new_theme.set_default_name(name)    
        new_theme.set_locale_name(name)
        new_theme.save()    
        return new_theme
  
    def rename_theme(self, name, new_name):
        theme_path = os.path.join(get_user_theme_dir(), "%s.ini" % name)
        theme = ThemeFile(theme_path)
        theme.set_locale_name(new_name)
        theme.save()

    def delete_theme(self, name):
        theme_path = os.path.join(get_user_theme_dir(), "%s.ini" % name)
        os.remove(theme_path)

    def untitled_theme(self, copy_theme=None):
        untitled_path = os.path.join(get_user_theme_dir(), "untitled.ini")
        if os.path.exists(untitled_path):
            try:
                os.unlink(untitled_path)
            except:    
                pass
            
        untitled_theme = ThemeFile(untitled_path)
        if copy_theme:
            untitled_theme.copy_theme(copy_theme)
        untitled_theme.set_default_name("untitled")    
        untitled_theme.set_locale_name(_("Untitled"))
        untitled_theme.save()    
        return untitled_theme
    
    def is_current_theme(self, theme):
        return theme.location == global_settings.get_option("settings/theme", "")
    
    def apply_theme(self, theme):
        duration = theme.get_background_duration()
        draw_mode = theme.get_background_draw_mode()
        random_mode = theme.get_background_random_mode(True)
        image_paths = theme.get_enable_wallpaper_paths()
        if image_paths:
            image_uris = ";".join(["file://%s" % path for path in image_paths])
            background_gsettings.set_string("picture-uris", image_uris)
        background_gsettings.set_int("background-duration", duration)
        # background_gsettings.set_string("draw-mode", draw_mode)
        # background_gsettings.set_string("cross-fade-auto-mode", random_mode)
        global_settings.set_option("settings/theme", theme.location)
        global_settings.save()
        
        
theme_manager = ThemeManager()
background_gsettings = background_gsettings = deepin_gsettings.new("com.deepin.dde.background")
