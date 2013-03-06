#!/usr/bin/env python
#-*- coding:utf-8 -*-

from nm_modules import nm_module
from nmlib.nmcache import cache
from helper import Dispatcher


class DeviceManager(object):

    def __init__(self):
        self.__init_device()
        #self.init_signals()
        
        self.__signal_list = ["device_active",
                              "device_deactive",
                              "device_unavailable",
                              "device_available",
                              "activate_start",
                              "activate_failed"]

    def __init_device(self):
        self.wired_devices = nm_module.nmclient.get_wired_devices()
        self.wireless_devices = nm_module.nmclient.get_wireless_devices()

    #def init_signals(self):
        #if self.wired_devices:
            #for device in self.wired_devices:
                #device.connect("state-changed", self.__wired_state_change)

        #if self.wireless_devices:
            #for device in self.wireless_devices:
                #device.connect("state-changed", self.__wireless_state_change)

    def load_wired_listener(self, module):
        if self.wired_devices:
            for device in self.wired_devices:
                map(lambda s: self.__connect(device, s, module), self.__signal_list)

    def load_wireless_listener(self, module):
        if self.wireless_devices:
            for device in self.wireless_devices:
                map(lambda s: self.__connect(device, s, module), self.__signal_list)
                
    
    def __connect(self, sender, signal, module):
        sender.connect(signal, getattr(module, signal))

    def __wired_state_change(self, widget, new_state, old_state, reason):
        Dispatcher.wired_change(widget, new_state, reason)

    def __wireless_state_change(self, widget, new_state, old_state, reason):
        Dispatcher.wireless_change(widget, new_state, old_state, reason)

    def get_wireless_devices(self):
        return self.wireless_devices

    def get_wired_devices(self):
        return self.wired_devices
    
    def reinit_cache(self):
        self.__init_device()
        self.init_signals()

    def get_device_by_mac(self, mac_address):
        devices = self.wired_devices + self.wireless_devices
        
        spec_devices = map(lambda d: cache.get_spec_object(d.object_path), devices)
        for index, device in enumerate(spec_devices):
            if device.get_hw_address == mac_address:
                return (devices[index], spec_devices[index])

class Handler(object):

    def device_active(self, new_state, old_state, reason):
        pass
    def device_deactive(self, new_state, old_state, reason):
        pass
    def device_unavailable(self, new_state, old_state, reason):
        pass
    def device_available(self, new_state, old_state, reason):
        pass
    def activate_start(self, new_state, old_state, reason):
        pass
    def activate_failed(self, new_state, old_state, reason):
        pass
device_manager = DeviceManager()

if __name__ == "__main__":

    h = Handler()
    device_manager.load_wired_listener(h)

