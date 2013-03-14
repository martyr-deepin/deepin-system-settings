#!/usr/bin/env python
#-*- coding:utf-8 -*-

ENV_USER = "XDG_CONFIG_HOME"
ENV_SYSTEM = "XDG_CONFIG_DIRS"

import os
import glib
import ConfigParser
import psutil

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

class AutoStart(object):
    SECTION = "Desktop Entry"

    def __init__(self, file_path=None):
        self.file_name = None
        self.dir = get_user_config_dir()
        self.conf = ConfigParser.RawConfigParser()
        self.conf.optionxform = str
        if file_path != None and os.path.exists(file_path):
            self.file_name = os.path.basename(file_path).split(".")[0]
            self.conf.read(file_path)
        else:
            self.new()

    def get_file(self):
        return self.file_name

    def get_option(self, option):
        try:
            return self.conf.get(self.SECTION, option)
        except:
            pass

    def options(self):
        return self.conf.options(self.SECTION)
    
    def name(self):
        name = self.get_option("Name")
        if name:
            return name
        else:
            return self.file_name

    def has_gnome_auto(self):
        enable = self.get_option("X-GNOME-Autostart-enabled")
        if enable:
            if enable == "true":
                return True
            else:
                return False
        else:
            return False

    def set_option(self, option, value):
        self.conf.set(self.SECTION, option, value)

    def save(self, file_name):
        path = os.path.join(self.dir , file_name + ".desktop")
        with open(path, "wb") as configfile:
            self.conf.write(configfile)

        self.file_name = file_name

    def remove_option(self, option):

        self.conf.remove_option(self.SECTION, option)

    def delete(self):
        if self.file_name:
            path = os.path.join(self.dir , self.file_name + ".desktop")
            os.remove(path)
            print "autostart removed"
            
    def new(self):
        self.conf.add_section(self.SECTION)
        new_autostart = [("Type", "Application"),
                         ("Exec", ""),
                         ("Hidden", "false"),
                         ("NoDisplay", "false"),
                         ("X-GNOME-Autostart-enabled", "true"),
                         ("Name", ""),
                         ("Comment", "")]

        for option in new_autostart:
            self.set_option(*option)

    def is_active(self):
        try:
            this_proc = filter(lambda w: w.name == self.name(), psutil.get_process_list())
        except:
            this_proc = None
        if this_proc:
            return True
        else:
            return False

class SessionManager(object):
    __user_dir = get_user_config_dir()
    __sys_dir = get_system_config_dir()

    def __init__(self):
        pass

    def list_user_auto_starts(self):
        return map(lambda w: AutoStart(os.path.join( self.__user_dir, w)), os.listdir(self.__user_dir))
    
    def list_sys_auto_starts(self):
        return map(lambda w: AutoStart(os.path.join(self.__sys_dir, w)), os.listdir(self.__sys_dir))

    def locale(self):
        lang = os.environ["LANG"].split(".")[0]
        return "[%s]"%lang

    def add(self, app_name, exec_path, comment):
        auto_file = AutoStart()
        auto_file.set_option("Name", app_name)
        auto_file.set_option("Exec", exec_path)
        auto_file.set_option("Comment" + self.locale(), comment)
        return auto_file
