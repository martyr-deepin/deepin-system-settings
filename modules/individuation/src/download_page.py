#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
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
from dtk.ui.new_treeview import TreeView

from download_item import DownloadItem

from helper import event_manager

class DownloadPage(gtk.VBox):
    
    def __init__(self):
        gtk.VBox.__init__(self)
        
        self.download_view = TreeView(enable_drag_drop=False, enable_multiple_select=False)
        self.download_view.draw_mask = self.draw_mask
        self.download_view.set_size_request(650, 450)
        self.add(self.download_view)
        event_manager.add_callback("download-image", self.on_download_iamge)
        
    def on_download_iamge(self, name, obj, data):    
        download_item = DownloadItem(data)
        self.download_view.add_items([download_item])
        download_item.start_download()
        
    def draw_mask(self, cr, x, y, w, h):
        '''
        Draw mask interface.
        
        @param cr: Cairo context.
        @param x: X coordiante of draw area.
        @param y: Y coordiante of draw area.
        @param w: Width of draw area.
        @param h: Height of draw area.
        '''
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
        
