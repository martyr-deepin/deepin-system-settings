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

from dtk.ui.dialog import DialogBox, DIALOG_MASK_MULTIPLE_PAGE
from dtk.ui.new_treeview import TreeView
from dtk.ui.icon_view import IconView
from dtk.ui.scrolled_window import ScrolledWindow
import gtk
import gobject

class AddWallpaper(DialogBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        DialogBox.__init__("添加壁纸",
                           600,
                           400,
                           mask_type=DIALOG_MASK_MULTIPLE_PAGE,
                           )
        
        self.layout_box = gtk.HBox()
        self.category_view = TreeView()
        self.lovewallpaper_view = IconView()
        self.lovewallpaper_scrolledwindow = ScrolledWindow()
        
        self.layout_box.pack_start(self.category_view, False, False)
        self.lovewallpaper_scrolledwindow.add_child(self.lovewallpaper_view)
        self.layout_box.pack_start(self.lovewallpaper_scrolledwindow, True, True)
        
gobject.type_register(AddWallpaper)
        
