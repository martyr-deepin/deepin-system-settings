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

class Card(BusBase):

    __gsignals__  = {
            "active-profile-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "new-profile":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "profile-removed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
            "property-list-updated":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
            }
    
    def __init__(self, path, interface = "org.PulseAudio.Core1.Card"):
        BusBase.__init__(self, path, interface)

        self.init_dbus_properties()

        self.dbus_proxy.connect_to_signal("ActiveProfileUpdated", self.active_profile_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("NewProfile", self.new_profile_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("PropertyListUpdated", self.property_list_updated_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)

        self.dbus_proxy.connect_to_signal("ProfileRemoved", self.profile_removed_cb, dbus_interface = 
                                          self.object_interface, arg0 = None)


    ###Props    
    def get_index(self):
        return self.properties["Index"]

    def get_name(self):
        return self.properties["Name"]

    def get_driver(self):
        return self.properties["Driver"]

    def get_own_module(self):
        return self.properties["OwnModule"]

    def get_sinks(self):
        if self.properties["Sinks"]:
            return map(lambda x:str(x), self.properties["Sinks"])
        else:
            return []

    def get_sources(self):
        if self.properties["Sources"]:
            return map(lambda x:str(x), self.properties["Sources"])
        else:
            return []

    def get_profiles(self):
        if self.properties["Profiles"]:
            return map(lambda x:str(x), self.properties["Profiles"])
        else:
            return []

    def get_active_profile(self):
        return str(self.properties["ActiveProfile"])

    def set_active_profile(self):
        pass

    def get_property_list(self):
        return self.properties["PropertyList"]
    
    ###Methods
    def get_profile_by_name(self, name):
        return str(self.dbus_method("GetProfileByName", name))

    ###Signals
    def active_profile_updated_cb(self, profile):
        self.emit("active-profile-updated", profile)

    def new_profile_cb(self, profile):
        self.emit("new-profile", profile)

    def profile_removed_cb(self, profile):
        self.emit("profile-removed", profile)

    def property_list_updated_cb(self, property_list):
        self.emit("property-list-updated", property_list)
        

class CardProfile(BusBase):
    
    def __init__(self, path, interface = "org.PulseAudio.Core1.CardProfile"):
        BusBase.__init__(self, path, interface)

        self.init_dbus_properties()
    
    ###Props    
    def get_index(self):
        return self.properties["Index"]

    def get_name(self):
        return self.properties["Name"]

    def get_description(self):
        return self.properties["Description"]

    def get_sinks(self):
        return self.properties["Sinks"]

    def get_sources(self):
        return self.properties["Sources"]

    def get_priority(self):
        return self.properties["Priority"]
    
if __name__ == "__main__":
    pass
