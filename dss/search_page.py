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

# from dtk.ui.scrolled_window import ScrolledWindow
import gobject
import gtk
import xappy

class DeepinSearch():
    def __init__(self):
        self.__xappy

    def build_index(self, remove_old=True):
        pass

    def search_query(self, keywords):
        pass

# class SearchPage(ScrolledWindow):
class SearchPage(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self, module_infos):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)

        self.__keyword = []

        self.__module_infos = module_infos
        '''
        FIXME: try to import each module keywords
        for module_info_list in self.__module_infos:
            for module_info in module_info_list:
                if module_info.search_keyword != "None":
                    from .modules.power.src.search_keyword import keywords

                    print keywords
        '''

gobject.type_register(SearchPage)
