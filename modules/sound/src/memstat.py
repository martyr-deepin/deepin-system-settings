#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
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

from pulseaudio import BusBase

class MemStat(BusBase):
    
    def __init__(self, path = "/org/pulseaudio/core1/memstats", interface = "org.PulseAudio.Core1.Memstats"):
        BusBase.__init__(self, path, interface)

        self.init_dbus_properties()
        
    ###Props    
    def get_current_mem_blocks(self):
        return self.properties["CurrentMemBlocks"]

    def get_current_mem_blocks_size(self):
        return self.properties["CurrentMemBlocksSize"]

    def get_accumulated_mem_blocks(self):
        return self.properties["AccumulatedMemBlocks"]

    def get_accumulated_mem_blocks_size(self):
        return self.properties["AccumulatedMemBlocksSize"]

    def get_sample_cache_size(self):
        return self.properties["SampleCacheSize"]
    ###Methods

    ###Signals
    
if __name__ == "__main__":
    pass