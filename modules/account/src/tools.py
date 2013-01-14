#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
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

import gtk
from glib import markup_escape_text

def make_align(widget=None, xalign=0.0, yalign=0.5, xscale=0.0,
               yscale=0.0, padding_top=0, padding_bottom=0, padding_left=0,
               padding_right=0, width=-1, height=-1):
    align = gtk.Alignment()
    align.set_size_request(width, height)
    align.set(xalign, yalign, xscale, yscale)
    align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
    if widget:
        align.add(widget)
    return align

def entry_check_account_name(name):
    return len(name) <= 20

def escape_markup_string(string):
    '''
    escape markup string
    @param string: a markup string
    @return: a escaped string
    '''
    if not string:
        return ""
    return markup_escape_text(string)

