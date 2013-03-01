#!/usr/bin/env python
#-*- coding:utf-8 -*-
from nm_modules import nm_module
from nmlib.nmcache import cache
from helper import Dispatcher
from device_manager import device_manager
from nmlib.servicemanager import servicemanager
from nmlib.nm_remote_connection import NMRemoteConnection

DEVICE_UNAVAILABLE = 0
DEVICE_AVAILABLE = 1
DEVICE_DISACTIVE = 1
DEVICE_ACTIVE = 2

class NetManager(object):

    def __init__(self):
        self.init_devices()
        servicemanager.connect("service-start", self.__on_service_start_do)
        servicemanager.connect("service-stop", self.__on_service_stop_do)

    def __on_service_start_do(self, widget, s):
        print "Debug::service_start", s
        nm_module.init_objects()
        device_manager.reinit_cache()
        self.init_devices()
        #print servicemanager.get_name_owner(s)

    def __on_service_stop_do(self, widget, s):
        print "Debug::service_stop", s
        global cache
        cache.clearcache()
        cache.clear_spec_cache()
        #print servicemanager.get_name_owner(s)

    def init_devices(self):
        self.wired_devices = device_manager.get_wired_devices()
        if self.wired_devices:
            self.wired_device = self.wired_devices[0]
        self.wireless_devices = device_manager.get_wireless_devices()
        if self.wireless_devices:
            self.wireless_device = self.wireless_devices[0]

    def get_wired_state(self):
        if self.wired_devices is []:
            # 没有有限设备
            return None
        else:
            state_list = []
            for device in self.wired_devices:
                state_list.append(device.get_state() == 20)
            
            if True in state_list:
                return (False, False)
            else:
                return (True, self.wired_devices[state_list.index(False)].is_active())

    def active_wired_device(self,  actived_cb):
        #wired_devices = nm_module.nmclient.get_wired_devices()
        #device = wired_devices[0]

        #def device_is_active( widget, reason):
            #actived_cb()
        #device.connect("device-active", device_is_active)
        for device in self.wired_devices:
            if not device.is_active():
                connections = nm_module.nm_remote_settings.get_wired_connections()
                if not connections:
                    connection = nm_module.nm_remote_settings.new_wired_connection()
                    nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')
                device_ethernet = cache.get_spec_object(device.object_path)
                device_ethernet.auto_connect()

    def disactive_wired_device(self, disactived_cb):
        #wired_devices = nm_module.nmclient.get_wired_devices()
        #device = wired_devices[0]

        #def device_is_disactive( widget, reason):
            #disactived_cb()
        #device.connect("device-deactive", device_is_disactive)
        for device in self.wired_devices:
            device.nm_device_disconnect()

    # Wireless
    def get_wireless_state(self):
        wireless_devices = nm_module.nmclient.get_wireless_devices()
        if not wireless_devices:
            return None
        else:
            #if not nm_module.nmclient.wireless_get_enabled():
                #nm_module.nmclient.wireless_set_enabled(True)
            if not nm_module.nmclient.wireless_get_enabled():
                return (False, False)
            else:
                return (True, wireless_devices[0].is_active())

    def get_ap_list(self):
        wireless_device = nm_module.nmclient.get_wireless_devices()[0]
        device_wifi = cache.get_spec_object(wireless_device.object_path)
        ap_list = device_wifi.order_ap_list()
        # 返回ap对象，ap.get_ssid() 获取ssid, ap.get_flags()获得加密状态，0为加密，1加密
        return ap_list

    def get_active_connection(self, ap_list):
        #wireless_device = nm_module.nmclient.get_wireless_devices()[0]
        index = []
        active_connection = self.wireless_device.get_active_connection()
        if active_connection:
            print active_connection.get_specific_object()
            index.append([ap.object_path for ap in ap_list].index(active_connection.get_specific_object()))
            return index
        else:
            return []

    def save_and_connect(self, serect, connection, ap):
        (setting_name, method) = connection.guess_secret_info() 
        connection.settings_dict[setting_name][method] = serect
        connection.update()
        #nm_module.secret_agent.agent_save_secrets(connection.object_path, setting_name, method)
        
        wireless_device = nm_module.nmclient.get_wireless_devices()[0]
        if ap:
            nm_module.nmclient.activate_connection_async(connection.object_path,
                                       wireless_device.object_path,
                                       ap.object_path)
        else:
            nm_module.nmclient.activate_connection_async(connection.object_path,
                                       wireless_device.object_path,
                                       "/")
        

    def connect_wireless_by_ssid(self, ssid):
        device_wifi = cache.get_spec_object(self.wireless_device.object_path)
        return device_wifi.get_ssid_connection(ssid)


    def active_wireless_device(self, actived_cb):
        wireless_device = nm_module.nmclient.get_wireless_devices()[0]

        def device_is_active(widget, reason):
            print "active"
            actived_cb()
        wireless_device.connect("device-active", device_is_active)
        device_wifi = cache.get_spec_object(wireless_device.object_path)
        device_wifi.auto_connect()

    def disactive_wireless_device(self, disactived_cb):
        wireless_device = nm_module.nmclient.get_wireless_devices()[0]
        
        def device_is_disactive( widget, reason):
            active = wireless_device.get_active_connection()
            disactived_cb()
        wireless_device.connect("device-deactive", device_is_disactive)
        wireless_device.nm_device_disconnect()


    def get_security_by_ap(self, ap_object):
        NM_802_11_AP_FLAGS_NONE = 0x0
        NM_802_11_AP_FLAGS_PRIVACY = 0x1
        NM_802_11_AP_SEC_NONE = 0x0
        NM_802_11_AP_SEC_PAIR_WEP40 = 0x1
        NM_802_11_AP_SEC_PAIR_WEP104 = 0x2
        NM_802_11_AP_SEC_PAIR_TKIP = 0x4
        NM_802_11_AP_SEC_PAIR_CCMP = 0x8
        NM_802_11_AP_SEC_GROUP_WEP40 = 0x10
        NM_802_11_AP_SEC_GROUP_WEP104 = 0x20
        NM_802_11_AP_SEC_GROUP_TKIP = 0x40
        NM_802_11_AP_SEC_GROUP_CCMP = 0x80
        NM_802_11_AP_SEC_KEY_MGMT_PSK = 0x100
        NM_802_11_AP_SEC_KEY_MGMT_802_1X = 0x200

        ap = ap_object

        wpa_flags = ap.get_wpa_flags()
        rsn_flags = ap.get_rsn_flags()
        flags = ap.get_flags()

        if flags & NM_802_11_AP_FLAGS_PRIVACY:
            if wpa_flags == NM_802_11_AP_SEC_NONE and rsn_flags == NM_802_11_AP_SEC_NONE :
                return "wep"
            if not wpa_flags & NM_802_11_AP_SEC_KEY_MGMT_802_1X and not rsn_flags & NM_802_11_AP_SEC_KEY_MGMT_802_1X :
                return "wpa"
        else:
            return None

class Settings(object):
    def __init__(self, setting_list):
        self.setting_list = setting_list 
        self.setting_state = {}
        self.settings = {}

    def init_items(self, connection):
        self.connection = connection 
        if connection not in self.settings:
            #self.init_button_state(connection)
            setting_list = []
            for setting in self.setting_list:
                s = setting(connection, self.set_button)
                setting_list.append((s.tab_name, s))
            self.settings[connection] = setting_list
        return self.settings[connection]

    def set_button(self, name, state):
        #Dispatcher.set_button(name, state)
        self.setting_state[self.connection] = (name, state)

    def clear(self):
        print "clear settings"
        self.setting_state = {}
        self.settings = {}

    def init_button_state(self, connection):
        if isinstance(connection, NMRemoteConnection):
            self.set_button("apply", True)
        else:
            self.set_button("save", False)

    def get_button_state(self, connection):
        if connection in self.setting_state.iterkeys():
            return self.setting_state[connection]

    def apply_changes(self):
        pass
