#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yaohua
#
# Author:     Wang Yaohua <mr.asianwang@gmail.com>
# Maintainer: Wang Yaohua <mr.asianwang@gmail.com>
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
import re
import os
import stat
import shutil
from uuid import uuid4

import gtk
from deepin_utils.process import get_command_output, run_command

ETC_DEFAULT_GRUB = "/etc/default/grub"
BOOT_GRUB_CFG = "/boot/grub/grub.cfg"
DSS_CUSTOM_PATH = "/etc/grub.d/80_dss_custom"

DSS_CUSTOM_TEMPLATE = '''#!/bin/sh
cat <<EOF
set menu_color_normal=%(normal_fg)s/%(normal_bg)s
set menu_color_highlight=%(highlight_fg)s/%(highlight_bg)s
EOF'''


class GrubSettingsApi(object):
    def __init__(self):
        self.uuid = str(uuid4())
        self.default_grub_path = "/tmp/%s-grub" % self.uuid
        self.grub_cfg_path = "/tmp/%s-grub.cfg" % self.uuid
        self.dss_custom_path = "/tmp/%s-dss_custom" % self.uuid
        shutil.copy(ETC_DEFAULT_GRUB, self.default_grub_path)
        # backup used to recovery if exception was caught
        shutil.copy(ETC_DEFAULT_GRUB, "%s.bak" % self.default_grub_path)
        
        with open(self.default_grub_path) as file_obj:
            self.default_grub_content = file_obj.readlines()
            
        # initialize color values.
        if os.path.exists(DSS_CUSTOM_PATH):
            shutil.copyfile(DSS_CUSTOM_PATH, self.dss_custom_path)
            with open(DSS_CUSTOM_PATH) as dss_custom:
                lines = dss_custom.readlines()
                print lines
                self.color_normal_fg, self.color_normal_bg = lines[2].strip().split("=")[1].split("/")
                self.color_highlight_fg, self.color_highlight_bg = lines[3].strip().split("=")[1].split("/")
        else:
            self.color_normal_fg = self.color_highlight_fg = "white"
            self.color_highlight_bg = self.color_normal_bg = "black"

    def is_item_active(self, item_name):
        return self.is_setting_item_exists(item_name, True)[0]

    def set_default_delay(self, delay_time):
        self.set_setting_item("GRUB_TIMEOUT", delay_time)

    def get_default_delay(self):
        return self.get_setting_item_value("GRUB_TIMEOUT", "0")

    def is_resolution_active(self):
        return self.is_item_active("GRUB_GFXMODE")

    def set_resolution(self, resolution):
        '''
        Set resolution.
        '''
        self.set_setting_item("GRUB_GFXMODE", resolution)

    def get_resolution(self):
        return self.get_setting_item_value("GRUB_GFXMODE", "")

    def disable_customize_resolution(self):
        self.remove_item("GRUB_GFXMODE")

    def is_background_image_active(self):
        return self.is_item_active("GRUB_MENU_PICTURE")
        
    def set_background_image(self, valid_img_file):
        """
        Set grub background
        """
        self.set_setting_item("GRUB_MENU_PICTURE", valid_img_file)

    def get_background_image(self):
        return self.get_setting_item_value("GRUB_MENU_PICTURE", "None")
    
    def disable_background_image(self):
        self.remove_item("GRUB_MENU_PICTURE")

    def __write_color_settings(self):
        with open(self.dss_custom_path, "w") as dss_custom:
            s = DSS_CUSTOM_TEMPLATE % {"normal_fg": self.color_normal_fg, 
                                       "normal_bg": self.color_normal_bg,
                                       "highlight_fg": self.color_highlight_fg,
                                       "highlight_bg": self.color_highlight_bg}
            dss_custom.write(s)
        os.chmod(self.dss_custom_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        
    def set_item_color(self, color_fg, color_bg, is_highlight_item=False):
        '''
        Set the color of grub items
        '''
        if is_highlight_item:
            self.color_highlight_fg, self.color_highlight_bg = color_fg, color_bg
            # self.set_setting_item("GRUB_COLOR_HIGHLIGHT", "%s/%s" % (color_fg, color_bg))
        else:
            self.color_normal_fg, self.color_normal_bg = color_fg, color_bg            
            # self.set_setting_item("GRUB_COLOR_NORMAL", "%s/%s" % (color_fg, color_bg))
        self.__write_color_settings()

    def get_item_color(self, is_highlight_item=False):
        if is_highlight_item:
            # return self.get_setting_item_value("GRUB_COLOR_HIGHLIGHT", "white/white")
            return self.color_highlight_fg + "/" + self.color_highlight_bg
        else:
            # return self.get_setting_item_value("GRUB_COLOR_NORMAL", "white/white")
            return self.color_normal_fg + "/" + self.color_normal_bg        

    def set_font(self, font_size, font_file):
        run_command("grub-mkfont -s %s -o /boot/grub/unicode.pf2 %s" % (font_size, font_file))
        self.set_setting_item("GRUB_FONT", "/boot/grub/unicode.pf2")

    def reset_all_settings(self):
        shutil.copy(ETC_DEFAULT_GRUB, self.default_grub_path)
        # backup used to recovery if exception was caught
        shutil.copy(ETC_DEFAULT_GRUB, "%s.bak" % self.default_grub_path)
        
        with open(self.default_grub_path) as file_obj:
            self.default_grub_content = file_obj.readlines()
            
        # initialize color values.
        if os.path.exists(DSS_CUSTOM_PATH):
            shutil.copyfile(DSS_CUSTOM_PATH, self.dss_custom_path)
            with open(DSS_CUSTOM_PATH) as dss_custom:
                lines = dss_custom.readlines()
                print lines
                self.color_normal_fg, self.color_normal_bg = lines[2].strip().split("=")[1].split("/")
                self.color_highlight_fg, self.color_highlight_bg = lines[3].strip().split("=")[1].split("/")
        else:
            self.color_normal_fg = self.color_highlight_fg = "white"
            self.color_highlight_bg = self.color_normal_bg = "black"

    def __comment_line(self, line):
        '''
        comment line and clean redundant #s in the line
        '''
        if line.startswith("#"):
            line = self.__uncomment_line(line)
            line = "#" + line
        else:
            line = "#" + line

        return line

    def __uncomment_line(self, line):
        if line.startswith("#"):
            line = line.strip("#")

        return line

    def __write_to_file(self, file_path, lines):
        with open(file_path, "w") as file_obj:
            for line in lines:
                file_obj.write(line)

    def new_setting_item(self, item_name, item_value):
        '''
        make new item if item item_name doesn't exists.
        '''
        new_line = "export %s=\"%s\"\n" % (item_name, item_value)
        self.default_grub_content.append(new_line)
        self.__write_to_file(self.default_grub_path, self.default_grub_content)

    def update_setting_item(self, item_name, item_value, line_index):
        '''
        update the value of item item_name if item exists.
        '''
        the_line = self.default_grub_content[line_index]
        if the_line.startswith("#"):
            the_line = self.__uncomment_line(the_line)
        the_line = "%s=\"%s\"\n" % (the_line.split("=")[0], item_value)
        self.default_grub_content[line_index] = the_line
        self.__write_to_file(self.default_grub_path, self.default_grub_content)

    def set_setting_item(self, item_name, item_value):
        '''
        convenient function for setting item values(doesn't care if item_name exists).
        '''
        is_exists, line_index = self.is_setting_item_exists(item_name)

        if is_exists:
            self.update_setting_item(item_name, item_value, line_index)
        else:
            self.new_setting_item(item_name, item_value)

    def remove_item(self, item_name):
        '''
        if item exists, comment the line the item located.
        '''
        is_exists, line_index = self.is_setting_item_exists(item_name)
        if is_exists:
            self.default_grub_content[line_index] = self.__comment_line(self.default_grub_content[line_index])
            self.__write_to_file(self.default_grub_path, self.default_grub_content)

    def is_setting_item_exists(self, item_name, check_active=False):
        '''
        return True and index of the line contains that item if the item exists, otherwise return False and -1.
        '''
        for line_index, line in enumerate(self.default_grub_content):
            # in case that two variable has the same prefix, eg.GRUB_CMDLINE_LINUX_DEFAULT and GRUB_CMD_LINE_LINUX
            if line.find(item_name + "=") != -1:
                if check_active:
                    if not line.startswith("#"):
                        return True, line_index
                else:
                    return True, line_index
        return False, -1

    def get_setting_item_value(self, item_name, default=""):
        is_exists, line_index= self.is_setting_item_exists(item_name)
        if is_exists:
            return self.default_grub_content[line_index].split("=")[1].strip().strip("\"")
        else:
            return default
        
    def write_sorted_menu_entry(self, ment_entry_list):
        with open(self.grub_cfg_path, "r+") as _grub_cfg:
            boot_grub_cfg_str = join_all(_grub_cfg.readlines())
    
            # clear all entries
            menuentry_pattern = re.compile(r"(?P<entry_content>^menuentry '(?P<entry_name>.*)'.*{[\s\S]*?^})", re.MULTILINE)
            boot_grub_cfg_str = menuentry_pattern.sub("", boot_grub_cfg_str)
            # clear all submenu entries
            menuentry_pattern = re.compile(r"(?P<entry_content>^submenu '(?P<entry_name>.*)'.*{[\s\S]*?}\s*^})", re.MULTILINE)
            boot_grub_cfg_str = menuentry_pattern.sub("", boot_grub_cfg_str)
    
            for menuentry in ment_entry_list:
                boot_grub_cfg_str += "\n" + menuentry["entry_content"]
    
            _grub_cfg.seek(0)
            _grub_cfg.truncate(0)
            _grub_cfg.write(boot_grub_cfg_str)

def validate_number(text):
    try:
        int(text)
        return True
    except:
        return False

def validate_image(file_name):
    '''
    check wether file_name is an invalid image file
    '''
    try:
        gtk.gdk.pixbuf_new_from_file(file_name)
        return True
    except Exception:
        return False


########################################################
# util function for generate proper resolutions for grub
########################################################
def get_proper_resolutions():
    output_lines = get_command_output("hwinfo --framebuffer | grep Mode", True)
    output_str = join_all(output_lines)

    return collect_all_resolutions(output_str)

def join_all(str_list):
    result = ""
    for str in str_list:
        result += str
    return result

def collect_all_resolutions(search_str):
    resolutions = []
    pattern = re.compile(r"Mode.*: (\d*x\d*) .* (\d*) bits")
    pattern.sub(lambda match_obj : resolutions.append("%sx%s" % (match_obj.group(1), match_obj.group(2))), search_str)

    return resolutions


########################################
# util functions for sortting grub items
########################################

# find all menu entries(include submenu entries).
def find_all_menu_entry():
    menu_entry_list = []
    with open(BOOT_GRUB_CFG) as boot_grub_cfg:
        boot_grub_cfg_str = join_all(boot_grub_cfg.readlines())

        # find entries
        menuentry_pattern = re.compile(r"(?P<entry_content>^menuentry '(?P<entry_name>.*?)'.*{[\s\S]*?^})", re.MULTILINE)
        menuentry_pattern.sub(lambda match_obj : menu_entry_list.append((match_obj.groupdict())), boot_grub_cfg_str)
        # find submenu entries
        menuentry_pattern = re.compile(r"(?P<entry_content>^submenu '(?P<entry_name>.*?)'.*{[\s\S]*?^})", re.MULTILINE)
        menuentry_pattern.sub(lambda match_obj : menu_entry_list.append((match_obj.groupdict())), boot_grub_cfg_str)

    return menu_entry_list

def rename_menu_entry(menu_entry, new_name):
    menu_entry["entry_name"] = new_name
    menu_entry["entry_content"] = re.sub("^menuentry '.*?'", "menuentry '%s'" % new_name, menu_entry["entry_content"])
    menu_entry["entry_content"] = re.sub("^submenu '.*?'", "submenu '%s'" % new_name, menu_entry["entry_content"])
    return menu_entry

if __name__ == "__main__":
    # print is_setting_item_exists("GRUB_TIMEOUT")
    # print is_setting_item_exists("GRUB_TIMEOUT_T")

    # remove_item("GRUB_TIMEOUT")
    # set_setting_item("GRUB_TIMEOUT", 50)
    # set_setting_item("GRUB_TIMEOUT_CUSTOMIZE", 20)

    # print get_proper_resolutions()
    # for index, entry in enumerate(find_all_menu_entry()):
    #     if index == 0:
    #         print "entry_name:"
    #         print entry["entry_name"]
    #         print "entry_content:"
    #         print entry["entry_content"]

    #         rename_menu_entry(entry, "new_name")
    #         print "entry_name:"
    #         print entry["entry_name"]
    #         print "entry_content:"
    #         print entry["entry_content"]
    
    for entry in find_all_menu_entry():
        print "entry_name: "
        print entry["entry_name"]
        print "entry_content: "
        print entry["entry_content"]

    # write_sorted_menu_entry([])
