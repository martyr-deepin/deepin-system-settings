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

from fetch_image import BaseFetch


class Bizhi360(BaseFetch):
    url = "http://cdn.apc.360.cn/index.php"
    name = "360壁纸"
    
    def __init__(self):
        BaseFetch.__init__(self)

        self.start = 0
        self.count = 20
        
    def fetch_images(self):    
        params = {
            "c" : "WallPaper",
            "a" : "getAppsByCategory",
            "from" : "360desktop",
            "cid" : 15, # 10, 6
            }
        
        results = self.api_request(self.url, extra_data=params, start=self.start, count=self.count)
                
        if results:
            if not results.has_key("data"):
                return

            for item in results["data"]:
                try:
                    small_url = item["url_mid"]
                    big_url = item["url"]
                except Exception, e:    
                    print e
                    continue
                else:
                    self.add_image(small_url, big_url)
                    
        if self.get_images():            
            self.start  += self.count            
            return True    
        return False
