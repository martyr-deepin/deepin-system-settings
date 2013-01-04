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

import urllib

import common
from mycurl import public_curl, CurlException

class ImageObject(object):
    
    def __init__(self, small_url, big_url, name):
        self.small_url = small_url
        self.big_url = big_url
        self.name = name
        
    def get_small_basename(self):    
        return common.get_md5(self.small_url)
    
    def get_display_name(self):
        return "%s_%s" % (self.name, self.small_url.split("/")[-1])
        
    def get_big_basename(self):    
        return common.get_md5(self.big_url)
        
    def __repr__(self):    
        return "<ImageObject %s>" % self.small_url
        
class BaseFetch(object):        
    name = "base"
    
    def __init__(self):
        self.__images = {}
        self.screen_width, self.screen_height = common.get_screen_size()        
        
    def get_images(self):  
        return self.__images.values()
    
    def add_image(self, small_url, big_url):
        self.__images[small_url] = ImageObject(small_url, big_url, name=self.name)
    
    def get_image(self, small_url):
        return self.__images.get(small_url, None)
    
    def clear(self):
        self.__images = {}
    
    def fetch_images(self):
        raise NotImplementedError
    
    def api_request(self, url, method="GET", extra_data=dict(), retry_limit=2,  **params):
        ret = None
        data = {}
        data.update(extra_data)
        data.update(params)
        for key in data:
            if callable(data[key]):
                data[key] = data[key]()
            if isinstance(data[key], (list, tuple, set)):
                data[key] = ",".join(map(str, list(data[key])))
            if isinstance(data[key], unicode):    
                data[key] = data[key].encode("utf-8")
                
        try:        
            if method == "GET":        
                if data:
                    query = urllib.urlencode(data)
                    url = "%s?%s" % (url, query)
                ret = public_curl.get(url)
            elif method == "POST":
                body = urllib.urlencode(data)
                ret = public_curl.post(url, body)
        except CurlException:        
            if retry_limit == 0:
                return data
            else:
                retry_limit -= 1
                return self.api_request(url, method, extra_data, retry_limit, **params)
            
        data = common.parser_json(ret)       
        return data
    
