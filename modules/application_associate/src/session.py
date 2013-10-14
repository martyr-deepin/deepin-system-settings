#!/usr/bin/env python
#-*- coding:utf-8 -*-

ENV_USER = "XDG_CONFIG_HOME"
ENV_SYSTEM = "XDG_CONFIG_DIRS"

import os
import glib
import gio
import ConfigParser
import psutil
import locale

from functools import partial

def get_system_lang():    
    (lang, encode) = locale.getdefaultlocale()
    return lang

def get_user_config_dir():
    dirs = os.path.join(glib.get_user_config_dir(), "autostart")
    if not os.path.exists(dirs):
        os.mkdir(dirs)
    return dirs


def get_system_config_dir():
    dirs = os.path.join(glib.get_system_config_dirs()[-1], "autostart")
    #if os.path.exists(dirs):
        #os.mkdir(dirs)
    return dirs

def save_config_to_file(conf, path):
    with open(path, "wb") as configfile:
        conf.write(configfile)

class AutoStart(object):
    SECTION = "Desktop Entry"
    TYPE_USER = 0
    TYPE_SYS = 1

    def __init__(self, file_type, file_path):
        assert(os.path.exists(file_path))
        self.file_name = None
        self.file_path = file_path
        self.type = file_type #TYPE_USER or TYPE_SYS
        self.app_id = os.path.basename(file_path)
        self.dir = get_user_config_dir()
        self.conf = ConfigParser.RawConfigParser()
        self.conf.optionxform = str

        self.file_name = os.path.splitext(os.path.basename(file_path))[0]
        self.conf.read(file_path)

    def get_file(self):
        return self.file_name

    def get_option(self, option):
        try:
            return self.conf.get(self.SECTION, option)
        except:
            return None
        
    def get_locale_option(self, key, default=None):    
        lang_key = "%s[%s]" % (key, get_system_lang())
        if self.conf.has_option(self.SECTION, lang_key):
            return self.conf.get(self.SECTION, lang_key)
        try:
            return self.conf.get(self.SECTION, key)
        except:
            return default
    
    def options(self):
        return self.conf.options(self.SECTION)
    
    @property
    def appid(self):
        return self.app_id


    @property
    def name(self):
        return self.get_locale_option("Name", "Unknow")
    def set_name(self, value):
        self.set_option("Name", value)
    
    @property
    def comment(self):
        return self.get_locale_option("Comment")
    def set_comment(self, value):
        self.set_option("Comment", value)
    
    @property
    def exec_(self):
        try:
            return self.conf.get(self.SECTION, "Exec")
        except:
            return None
    def set_exec(self, value):
        self.set_option("Exec", value)

    def is_autostart(self):
        auto_start = self.get_option("X-GNOME-Autostart-enabled")
        if auto_start == None or auto_start == "true":
            return True
        else:
            return False

    def set_option(self, option, value):
        try:
            self.conf.set(self.SECTION, option, value)
        except Exception:
            pass

    def remove_option(self, option):
        self.conf.remove_option(self.SECTION, option)

    def delete(self):
        if self.file_name:
            path = os.path.join(self.dir , self.file_name + ".desktop")
            os.remove(path)

    def set_shadow_item(self, item):
        assert(self.type == AutoStart.TYPE_SYS)
        self.conf = item.conf
        self.file_path = item.file_path
    def ensure_shadow(self):
        if self.type == AutoStart.TYPE_SYS:
            self.set_shadow_item(create_autostart(self.appid, self.name, self.exec_, self.comment))

    def set_autostart_state(self, value):
        self.ensure_shadow()
        self.set_option("X-GNOME-Autostart-enabled", str(value).lower())
        self.save()

    def save(self):
        self.ensure_shadow()
        save_config_to_file(self.conf, self.file_path)


def create_autostart(app_id, app_name, exec_path, comment):
    conf = ConfigParser.RawConfigParser()
    conf.optionxform = str
    conf.add_section(AutoStart.SECTION)
    conf.set(AutoStart.SECTION, "Type", "Application")
    conf.set(AutoStart.SECTION, "Exec", exec_path)
    conf.set(AutoStart.SECTION, "Hidden", "false")
    conf.set(AutoStart.SECTION, "Name", app_name)
    conf.set(AutoStart.SECTION, "Comment", comment)
    conf.set(AutoStart.SECTION, "X-GNOME-Autostart-enabled", "true")
    save_config_to_file(conf, os.path.join(get_user_config_dir(), app_id))
    return AutoStart(AutoStart.TYPE_USER, os.path.join(get_user_config_dir(), app_id))


class SessionManager(object):
    __user_dir = get_user_config_dir()
    __sys_dir = get_system_config_dir()

    def __init__(self):
        pass

    def list_autostart_items(self):
        items = []
        system_item_name = {}
        for name in filter(self.is_desktop_file_sys, os.listdir(self.__sys_dir)):
            item = AutoStart(AutoStart.TYPE_SYS, os.path.join(self.__sys_dir, name))
            items.append(item)
            system_item_name[name] = item

        for name in filter(self.is_desktop_file_user, os.listdir(self.__user_dir)):
            item = AutoStart(AutoStart.TYPE_USER, os.path.join(self.__user_dir, name))
            if not name in system_item_name.keys():
                items.append(item)
            else:
                system_item_name[name].set_shadow_item(item)


        return items
    
    def locale(self):
        return "[%s]" % get_system_lang()
    
    def add(self, app_name, exec_path, comment):
        if not app_name:
            app_id = "tmp.desktop"
        else:
            app_id = app_name + ".desktop"
        return create_autostart(app_id, app_name, exec_path, comment)
    
    is_desktop_file_user = property(lambda self : partial(is_deepin_desktop_file, basename=self.__user_dir))
    is_desktop_file_sys = property(lambda self : partial(is_deepin_desktop_file, basename=self.__sys_dir))
    
def is_deepin_desktop_file(filename, basename):
    file_path = basename + os.sep + filename
    appinfo = gio.unix.desktop_app_info_new_from_filename(file_path)
    if not appinfo:
        return False
    return appinfo.should_show()
