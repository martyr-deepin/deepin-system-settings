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
import shutil
from uuid import uuid4

import gtk
from deepin_utils.process import get_command_output, run_command

ETC_DEFAULT_GRUB = "/etc/default/grub"
BOOT_GRUB_CFG = "/boot/grub/grub.cfg"

class GrubSettingsApi(object):
    def __init__(self):
        self.uuid = uuid4()
        self.default_grub_path = "/tmp/%s-grub" % self.uuid
        self.grub_cfg_path = "/tmp/%s-grub.cfg" % self.uuid
        shutil.copy(ETC_DEFAULT_GRUB, self.default_grub_path)
        shutil.copy(BOOT_GRUB_CFG, self.grub_cfg_path)
        
    def is_item_active(self, item_name):
        return is_setting_item_exists(self.default_grub_path, item_name, True)[0]
        
    def set_default_delay(self, delay_time):
        set_setting_item(self.default_grub_path, "GRUB_TIMEOUT", delay_time)

    def get_default_delay(self):
        return get_setting_item_value(self.default_grub_path, "GRUB_TIMEOUT", "0")
    
    def is_resolution_active(self):
        return self.is_item_active("GRUB_GFXMODE")
    
    def set_resolution(self, resolution):
        '''
        Set resolution.
        '''
        set_setting_item(self.default_grub_path, "GRUB_GFXMODE", resolution)
    
    def get_resolution(self):
        return get_setting_item_value(self.default_grub_path, "GRUB_GFXMODE", "")
    
    def set_background_image(self, valid_img_file):
        """
        Set grub background
        """
        set_setting_item(self.default_grub_path, "GRUB_MENU_PICTURE", valid_img_file)
        
    def get_background_image(self):
        return get_setting_item_value(self.default_grub_path, "GRUB_MENU_PICTURE", "None")
    
    def set_item_color(self, color_fg, color_bg, is_highlight_item=False):
        '''
        Set the color of grub items
        '''
        if is_highlight_item:
            set_setting_item(self.default_grub_path, "GRUB_COLOR_HIGHLIGHT", "%s/%s" % (color_fg, color_bg))
        else:
            set_setting_item(self.default_grub_path, "GRUB_COLOR_NORMAL", "%s/%s" % (color_fg, color_bg))
            
    def get_item_color(self, is_highlight_item=False):
        if is_highlight_item:
            return get_setting_item_value(self.default_grub_path, "GRUB_COLOR_HIGHLIGHT", "")
        else:
            return get_setting_item_value(self.default_grub_path, "GRUB_COLOR_NORMAL", "")
    
    def set_font(self, font_size, font_file):
        run_command("grub-mkfont -s %s -o /boot/grub/unicode.pf2 %s" % (font_size, font_file))
        set_setting_item("GRUB_FONT", "/boot/grub/unicode.pf2")
    
    def reset_all_setttings(self):
        self.uuid = uuid4()
        self.default_grub_path = "/tmp/%s-grub" % self.uuid
        self.grub_cfg_path = "/tmp/%s-grub.cfg" % self.uuid
        shutil.copy(ETC_DEFAULT_GRUB, self.default_grub_path)
        shutil.copy(BOOT_GRUB_CFG, self.grub_cfg_path)
        # set_setting_item("GRUB_TIMEOUT", "10")
        # remove_item("GRUB_GFXMODE")
        # remove_item("GRUB_MENU_PICTURE")
        # remove_item("GRUB_COLOR_HIGHLIGHT")
        # remove_item("GRUB_COLOR_NORMAL")
        # remove_item("GRUB_FONT")
    
        
########################################################
# util functions for editting the /etc/default/grub file
########################################################
def comment_line(line):
    '''
    comment line and clean redundant #s in the line
    '''
    if line.startswith("#"):
        line = uncomment_line(line)
        line = "#" + line
    else:
        line = "#" + line

    return line

def uncomment_line(line):
    if line.startswith("#"):
        line = line.strip("#")

    return line


def new_setting_item(file_path, item_name, item_value):
    '''
    make new item if item item_name doesn't exists.
    '''
    etc_default_grub = open(file_path, "r+")
    content = etc_default_grub.readlines()
    new_line = "export %s=\"%s\"\n" % (item_name, item_value)
    content.append(new_line)
    etc_default_grub.seek(0)
    etc_default_grub.truncate(0)
    for line in content:
        etc_default_grub.write(line)
    etc_default_grub.close()


def update_setting_item(file_path, item_name, item_value, line_index):
    '''
    update the value of item item_name if item exists.
    '''
    etc_default_grub = open(file_path, "r+")
    content = etc_default_grub.readlines()


    the_line = content[line_index]
    if the_line.startswith("#"):
        the_line = uncomment_line(the_line)
    the_line = "%s=\"%s\"\n" % (the_line.split("=")[0], item_value)
    content[line_index] = the_line

    etc_default_grub.seek(0)
    etc_default_grub.truncate(0)
    for line in content:
        etc_default_grub.write(line)
    etc_default_grub.close()


def set_setting_item(file_path, item_name, item_value):
    '''
    convenient function for setting item values(doesn't care if item_name exists).
    '''
    is_exists, line_index = is_setting_item_exists(file_path, item_name)

    if is_exists:
        update_setting_item(file_path, item_name, item_value, line_index)
    else:
        new_setting_item(file_path, item_name, item_value)

def remove_item(file_path, item_name):
    '''
    if item exists, comment the line the item located.
    '''
    is_exists, line_index = is_setting_item_exists(file_path, item_name)
    if is_exists:
        etc_default_grub = open(file_path, "r+")
        content = etc_default_grub.readlines()
        content[line_index] = comment_line(content[line_index])
        etc_default_grub.seek(0)
        etc_default_grub.truncate(0)
        for line in content:
            etc_default_grub.write(line)
        etc_default_grub.close()

def is_setting_item_exists(file_path, item_name, check_active=False):
    '''
    return True and index of the line contains that item if the item exists, otherwise return False and -1.
    '''
    with open(file_path) as etc_default_grub:
        lines = etc_default_grub.readlines()
        for line_index, line in enumerate(lines):
            # in case that two variable has the same prefix, eg.GRUB_CMDLINE_LINUX_DEFAULT and GRUB_CMD_LINE_LINUX
            if line.find(item_name + "=") != -1:
                if check_active:
                    if not line.startswith("#"):
                        return True, line_index
                else:
                    return True, line_index
        return False, -1

def get_setting_item_value(file_path, item_name, default=""):
    is_exists, line_index= is_setting_item_exists(file_path, item_name)
    if is_exists:
        with open(file_path) as etc_default_grub:
            content = etc_default_grub.readlines()
            return content[line_index].split("=")[1].strip().strip("\"")
    else:
        return default

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
        menuentry_pattern = re.compile(r"(?P<entry_content>^menuentry '(?P<entry_name>.*)'.*{[\s\S]*?})", re.MULTILINE)
        menuentry_pattern.sub(lambda match_obj : menu_entry_list.append((match_obj.groupdict())), boot_grub_cfg_str)
        # find submenu entries
        menuentry_pattern = re.compile(r"(?P<entry_content>^submenu '(?P<entry_name>.*)'.*{[\s\S]*?})", re.MULTILINE)
        menuentry_pattern.sub(lambda match_obj : menu_entry_list.append((match_obj.groupdict())), boot_grub_cfg_str)

    return menu_entry_list

def write_sorted_menu_entry(ment_entry_list):
    with open(BOOT_GRUB_CFG, "r+") as boot_grub_cfg:
        boot_grub_cfg_str = join_all(boot_grub_cfg.readlines())

        # clear all entries
        menuentry_pattern = re.compile(r"(?P<entry_content>^menuentry '(?P<entry_name>.*)'.*{[\s\S]*?})", re.MULTILINE)
        boot_grub_cfg_str = menuentry_pattern.sub("", boot_grub_cfg_str)
        # clear all submenu entries
        menuentry_pattern = re.compile(r"(?P<entry_content>^submenu '(?P<entry_name>.*)'.*{[\s\S]*?}\s*})", re.MULTILINE)
        boot_grub_cfg_str = menuentry_pattern.sub("", boot_grub_cfg_str)

        for menuentry in ment_entry_list:
            boot_grub_cfg_str += menuentry["entry_content"]

        boot_grub_cfg.seek(0)
        boot_grub_cfg.truncate(0)
        boot_grub_cfg.write(boot_grub_cfg_str)
        
if __name__ == "__main__":
    # print is_setting_item_exists("GRUB_TIMEOUT")
    # print is_setting_item_exists("GRUB_TIMEOUT_T")

    # remove_item("GRUB_TIMEOUT")
    # set_setting_item("GRUB_TIMEOUT", 50)
    # set_setting_item("GRUB_TIMEOUT_CUSTOMIZE", 20)

    print get_proper_resolutions()
    # for entry in find_all_menu_entry():
    #     print "entry_name:"
    #     print entry["entry_name"]
    #     print "entry_content"
    #     print entry["entry_content"]
    # write_sorted_menu_entry([])
