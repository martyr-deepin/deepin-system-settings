#!/usr/bin/env python
#-*- coding:utf-8 -*-

from nm_modules import nm_module
from helper import Dispatcher

class DeviceManager(object):

    def __init__(self):
        #self.__init_device()
        self.__signal_list = ["device_active",
                              "device_deactive",
                              "device_unavailable",
                              "activate_start",
                              "activate_failed"]

        self.connected_device = list()

        nm_module.nmclient.connect("device-added", self.device_added_cb)
        nm_module.nmclient.connect("device-removed", self.device_removed_cb)

    def init_device(self):
        self.wired_devices = nm_module.nmclient.get_wired_devices()
        self.wireless_devices = nm_module.nmclient.get_wireless_devices()
        self.mm_devices = nm_module.nmclient.get_modem_devices()
        nm_module.mmclient.connect("device-added", self.mm_device_added)
        nm_module.mmclient.connect("device-removed", self.mm_device_removed)
        self.ap_added(self.wireless_devices)

    def mm_device_added(self, widget, path):
        self.init_device()
        device = nm_module.cache.getobject(path)
        Dispatcher.emit("mmdevice-added", device)
        Dispatcher.emit("recheck-section", 3)

    def mm_device_removed(self, widget, path):
        self.init_device()
        device = nm_module.cache.getobject(path)
        Dispatcher.emit("mmdevice-removed", device)
        Dispatcher.emit("recheck-section", 3)


    def device_added_cb(self, widget, path):
        self.init_device()
        device =  nm_module.cache.getobject(path)
        type = device.get_device_type() 
        if type == 1:
            if device not in self.connected_device:
                Dispatcher.emit("wired-device-add", device)
                Dispatcher.emit("recheck-section", 0)
        elif type == 2:
            if device not in self.connected_device:
                Dispatcher.emit("wireless-device-add", device)
                Dispatcher.emit("recheck-section", 1)

    def device_removed_cb(self, widget, path):
        self.init_device()
        device = nm_module.cache.getobject(path)
        type = device.get_device_type() 
        if type == 1:
            Dispatcher.emit("wired-device-remove", device)
            Dispatcher.emit("recheck-section", 0)
        elif type == 2:
            Dispatcher.emit("wireless-device-remove", device)
            Dispatcher.emit("recheck-section", 1)

    def ap_added(self, devices):
        for device in devices:
            if device not in self.connected_device:
                wifi = nm_module.cache.get_spec_object(device.object_path)
                wifi.connect("access-point-added", lambda w: Dispatcher.emit("ap-added"))
                wifi.connect("access-point-removed", lambda w: Dispatcher.emit("ap-removed"))

    def load_wired_listener(self, module):
        if self.wired_devices:
            for device in self.wired_devices:
                if device not in self.connected_device:
                    map(lambda s: self.__connect(device, s, module, "wired"), self.__signal_list)
                    self.connected_device.append(device)

    def load_wireless_listener(self, module):
        if self.wireless_devices:
            for device in self.wireless_devices:
                if device not in self.connected_device:
                    map(lambda s: self.__connect(device, s, module, "wireless"), self.__signal_list)
                    self.connected_device.append(device)

    def load_mm_listener(self, module):
        if self.mm_devices:
            for d in self.mm_devices:
                map(lambda s: self.__connect(d, s, module, "mm") ,self.__signal_list)

    def __connect(self, sender, signal, module, type):
        sender.connect(signal, getattr(module, type + "_" + signal))

    def __wired_state_change(self, widget, new_state, old_state, reason):
        Dispatcher.wired_change(widget, new_state, reason)

    def __wireless_state_change(self, widget, new_state, old_state, reason):
        Dispatcher.wireless_change(widget, new_state, old_state, reason)

    def get_wireless_devices(self):
        return self.wireless_devices

    def get_wired_devices(self):
        return self.wired_devices
    
    def get_spec_cache(self, device):
        return nm_module.cache.get_spec_object(device.object_path)
    
    def reinit_cache(self):
        self.__init_device()
        #self.init_signals()

    def get_device_by_mac(self, mac_address):
        devices = self.wired_devices + self.wireless_devices
        
        spec_devices = map(lambda d: nm_module.cache.get_spec_object(d.object_path), devices)
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

