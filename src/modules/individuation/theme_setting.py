#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
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
import gobject
from dtk.ui.tab_window import TabBox
from dtk.ui.utils import container_remove_all
from dtk.ui.iconview import IconView

class ThemeSettingView(TabBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        TabBox.__init__(self)
        
        self.wallpaper_box = gtk.VBox()
        self.window_theme_box = gtk.VBox()
        self.theme_icon_view = IconView()
        
        self.add_items([("壁纸", self.wallpaper_box),
                        ("窗口主题", self.window_theme_box)])
        
    def set_theme(self, theme):
        container_remove_all(self.wallpaper_box)
        
gobject.type_register(ThemeSettingView)        
