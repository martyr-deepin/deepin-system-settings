#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang YaoHua
# 
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
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

from bus_utils import BusBase

class CoreApi(BusBase):
    
    def __init__(self):
        BusBase.__init__(self, path="/", interface="com.deepin.grub2")

    def get_proper_resolutions(self):
        return self.dbus_method("getResolutions")
    
    def update_grub(self, uuid):
        return self.dbus_method("updateGrub", uuid)
    
core_api = CoreApi()

if __name__ == "__main__":
    print core_api.get_proper_resolutions()
