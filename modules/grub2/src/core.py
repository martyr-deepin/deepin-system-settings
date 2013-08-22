#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang YaoHua
# 
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
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

from deepin_utils.process import run_command
from grub_setting_utils import set_setting_item, remove_item

def set_default_delay(delay_time):
    set_setting_item("GRUB_TIMEOUT", delay_time)
    
def set_resolution(resolution):
    '''
    Set resolution.
    '''
    set_setting_item("GRUB_GFXMODE", resolution)
    
def set_background_image(valid_img_file):
    """
    Set grub background
    """
    set_setting_item("GRUB_MENU_PICTURE", valid_img_file)

def set_item_color(color_fg, color_bg, is_highlight_item=False):
    '''
    Set the color of grub items
    '''
    if is_highlight_item:
        set_setting_item("GRUB_COLOR_HIGHLIGHT", "%s/%s" % (color_fg, color_bg))
    else:
        set_setting_item("GRUB_COLOR_NORMAL", "%s/%s" % (color_fg, color_bg))

def set_font(font_size, font_file):
    run_command("sudo grub-mkfont -s %s -o /boot/grub/unicode.pf2 %s" % (font_size, font_file))
    set_setting_item("GRUB_FONT", "/boot/grub/unicode.pf2")

def reset_all_setttings():
    set_setting_item("GRUB_TIMEOUT", "10")
    remove_item("GRUB_GFXMODE")
    remove_item("GRUB_MENU_PICTURE")
    remove_item("GRUB_COLOR_HIGHLIGHT")
    remove_item("GRUB_COLOR_NORMAL")
    remove_item("GRUB_FONT")


if __name__ == "__main__":
    set_default_delay("10")
