#!/usr/bin/env python
#-*- coding:utf-8 -*-
from nm_modules import nm_module
from nmlib.nmcache import cache

def get_wired_state():
    wired_devices = nm_module.nmclient.get_wired_devices()
    if wired_devices is None:
        # 没有有限设备
        return False
    else:
        device = wired_devices[0]

        return device.is_active()

def active_wired_device():
    wired_devices = nm_module.nmclient.get_wired_devices()
    device = wired_devices[0]

    if not device.is_active():
        connections = nm_module.nm_remote_settings.get_wired_connections()
        if not connections:
            connection = nm_module.nm_remote_settings.new_wired_connection()
            nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')

        device_ethernet = cache.get_spec_object(device.object_path)
        device_ethernet.auto_connect()

def disactive_wired_device():
    wired_devices = nm_module.nmclient.get_wired_devices()
    device = wired_devices[0]
    device.nm_device_disconnect()






