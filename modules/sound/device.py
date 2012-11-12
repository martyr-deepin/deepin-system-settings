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
import gobject

class Device(BusBase):
    
    def __init__(self, path, interface = "org.PulseAudio.Core1.Device"):
        BusBase.__init__(self, path, interface)

        self.init_dbus_properties()
    ###Props    
    def get_index(self):
        return self.properties["Index"]

    def get_name(self):
        return self.properties["Name"]

    def get_driver(self):
        return self.properties["Driver"]

    def get_owner_module(self):
        return str(self.properties["OwnerModule"])

    def get_card(self):
        return str(self.properties["Card"])

    def get_sample_format(self):
        return self.properties["SampleFormat"]

    def get_sample_rate(self):
        return self.properties

    def get_channels(self):
        if self.properties["Channels"]:
            return map(lambda x:int(x), self.properties["Channels"])

    def get_volume(self):
        pass

    def set_volume(self):
        pass

    def get_has_flat_volume(self):
        pass

    def get_has_convertible_to_decibel_volume(self):
        pass

    
    
    ###Signals
if __name__ == "__main__":
    pass
