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

class Aibizhi(BaseFetch):
    url = "http://partner.lovebizhi.com/deepinlinux.php"
    name = "爱壁纸HD"
    
    def __init__(self):
        BaseFetch.__init__(self)
        
    def fetch_images(self):    
        results = self.api_request(self.url, width=self.screen_width,
                                   height=self.screen_height, limit=20)
        if results:
            for item in results:
                if isinstance(item, dict):
                    self.add_image(item["s"], item["b"])
            return True    
        return False
        
