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

import os
import gtk
import gobject

from dtk.ui.utils import is_network_connected, get_optimum_pixbuf_from_file
from dtk.ui.thread_pool import MissionThreadPool

import common
from xdg_support import get_specify_cache_dir, get_image_path


SMALL_SIZE = {"x" : 140, "y" : 90 }

class CacheManager(object):
    
    def __init__(self):
        self.default_image_path = get_image_path("default_cache.jpg")
        
    def get_image_path(self, name):
        return os.path.join(get_specify_cache_dir("images"), name)
        
    def get_temp_path(self, name):    
        return os.path.join(get_specify_cache_dir("temp"), name)
    
    def get_image_pixbuf(self, image_object):
        image_path = self.get_image(image_object, False)
        is_loaded = True
        if not image_path:
            image_path = self.default_image_path
            is_loaded = False
            
        return gtk.gdk.pixbuf_new_from_file(image_path), is_loaded
        
    def get_image(self, image_object, try_web=True):
        image_path = self.get_image_path(image_object.get_small_basename())
        temp_path = self.get_temp_path(image_object.get_small_basename())
        
        if os.path.exists(image_path) and os.path.isfile(image_path):
            try:
                pixbuf = gtk.gdk.pixbuf_new_from_file(image_path)
            except gobject.GError:
                try:
                    os.unlink(image_path)
                except: pass
            else:    
                del pixbuf
                return image_path
            
        if try_web and is_network_connected():
            small_image_url = image_object.small_url
            if small_image_url:
                ret = common.download(small_image_url, temp_path)
                if ret and self.cleanup_small(temp_path, image_path):
                    return image_path
                
        return None        
    
    
    def cleanup_small(self, old_path, new_path=None):
        if not new_path:
            new_path = old_path
        if not os.path.exists(old_path):    
            return False
        
        try:
            pixbuf = get_optimum_pixbuf_from_file(old_path, SMALL_SIZE["x"], SMALL_SIZE["y"])
            
        except gobject.GError:    
            try:
                if os.path.exists(old_path): os.unlink(old_path)                            
            except: pass
            
            try:
                if os.path.exists(new_path): os.unlink(new_path)
            except: pass
            
            return False
        else:
            try:
                if os.path.exists(new_path): os.unlink(new_path)
            except: pass
            
            try:
                if os.path.exists(old_path): os.unlink(old_path)                            
            except: pass
            
            pixbuf.save(new_path, "jpeg", {"quality" : "100"})
            del pixbuf  
            return True

cache_manager = CacheManager()        
cache_thread_pool = MissionThreadPool(5)
cache_thread_pool.start()
        