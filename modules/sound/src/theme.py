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

from dtk.ui.init_skin import init_skin
from dtk.ui.utils import get_parent_dir
from dtk.ui.theme import DynamicPixbuf, DynamicColor
import os

app_theme = init_skin(
    "deepin-settings",
    "1.0",
    "01",
    os.path.join(get_parent_dir(__file__, 2), "skin"),
    os.path.join(get_parent_dir(__file__, 2), "theme"))


def app_theme_get_pixbuf(filename):
    '''
    from file get theme pixbuf
    @param filename: the image filename
    @return: a gtk.gdk.Pixbuf
    '''
    return app_theme.get_pixbuf(filename).get_pixbuf()


def app_theme_get_dynamic_pixbuf(filename):
    '''
    from file get dynamic pixbuf
    @param filename: the image filename
    @return: a DynamicPixbuf
    '''
    return DynamicPixbuf(app_theme.get_theme_file_path(filename))


def app_theme_get_dynamic_color(color):
    '''
    get them color
    @param color: a hex color string
    @return: a DynamicColor
    '''
    return DynamicColor(color)
