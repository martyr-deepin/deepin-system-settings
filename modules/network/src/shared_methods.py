#!/usr/bin/env python
#-*- coding:utf-8 -*-
from nm_modules import nm_module
from nmlib.nmcache import cache
from helper import Dispatcher
from device_manager import DeviceManager
from nmlib.servicemanager import servicemanager
from nmlib.nm_remote_connection import NMRemoteConnection
from deepin_utils.ipc import is_dbus_name_exists


DEVICE_UNAVAILABLE = 0
DEVICE_AVAILABLE = 1
DEVICE_DISACTIVE = 1
DEVICE_ACTIVE = 2

class NetManager(object):

    def __init__(self):
        #self.init_devices()
        if is_dbus_name_exists("org.freedesktop.NetworkManager", False):
            servicemanager.connect("service-start", self.__on_service_start_do)
            servicemanager.connect("service-stop", self.__on_service_stop_do)
            self.device_manager = DeviceManager()
            self.init_devices()

            self.cf = nm_module.nm_remote_settings.cf
            self.config_file = nm_module.nm_remote_settings.config_file
            if "hidden" not in self.cf.sections():
                self.cf.add_section("hidden")
        else:
            pass


    def __on_service_start_do(self, widget, s):
        print "Debug::service_start", s
        nm_module.init_objects()
        #device_manager.reinit_cache()
        self.device_manager = DeviceManager()
        self.init_devices()
        #print servicemanager.get_name_owner(s)

    def __on_service_stop_do(self, widget, s):
        print "Debug::service_stop", s
        #self.device_manager.reinit_cache()
        cache.clearcache()
        cache.clear_spec_cache()

    def get_hiddens(self):
        hiddens = list()
        connections = nm_module.nm_remote_settings.get_wireless_connections()
        self.cf.read(self.config_file)

        for index, ssid in enumerate(map(lambda x: x.get_setting("802-11-wireless").ssid, connections)):
            if ssid in self.cf.options("hidden"):
                hiddens.append(connections[index])
        return hiddens
    
    def add_hidden(self, connection):
        ssid = connection.get_setting("802-11-wireless").ssid
        self.cf.read(self.config_file)
        if ssid not in self.cf.options("hidden"):
            self.cf.set("hidden", ssid)
        try:
            self.cf.write(open(self.config_file, "w"))
            print "save succeed"
        except:
            print "save failded in addHidden"

        #print servicemanager.get_name_owner(s)

    def init_devices(self):
        self.wired_devices = self.device_manager.get_wired_devices()
        if self.wired_devices:
            self.wired_device = self.wired_devices[0]
        self.wireless_devices = self.device_manager.get_wireless_devices()
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
            wired = cache.get_spec_object(device.object_path)
            wired.device_wired_disconnect()
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
        #print "DEBUG in get ap list", device_wifi
        ap_list = device_wifi.order_ap_list()
        # 返回ap对象，ap.get_ssid() 获取ssid, ap.get_flags()获得加密状态，0为加密，1加密
        return ap_list

    def get_active_connection(self, ap_list):
        #wireless_device = nm_module.nmclient.get_wireless_devices()[0]
        index = []
        #if not self.wireless_device.is_active():
            #print "not device active"
            #return []
        active_connection = self.wireless_device.get_active_connection()
        if active_connection:
            try:
                print active_connection.get_specific_object()
                index.append([ap.object_path for ap in ap_list].index(active_connection.get_specific_object()))
                return index
            except:
                return []
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
        return device_wifi.active_ssid_connection(ssid)


    def active_wireless_device(self, actived_cb):
        wireless_device = nm_module.nmclient.get_wireless_devices()[0]
        print "fsdf"

        #def device_is_active(widget, reason):
            #print "active"
            #actived_cb()
        #wireless_device.connect("device-active", device_is_active)
        device_wifi = cache.get_spec_object(wireless_device.object_path)
        device_wifi.auto_connect()

    def disactive_wireless_device(self, disactived_cb):
        wireless_device = nm_module.nmclient.get_wireless_devices()[0]
        
        #def device_is_disactive( widget, reason):
            #active = wireless_device.get_active_connection()
            #disactived_cb()
        #wireless_device.connect("device-deactive", device_is_disactive)
        wifi = cache.get_spec_object(wireless_device.object_path)
        wifi.device_wifi_disconnect()
        wireless_device.nm_device_disconnect()

    def get_mm_devices(self):
        cdma = nm_module.mmclient.get_cdma_device()
        gsm = nm_module.mmclient.get_gsm_device()
        return cdma + gsm


    def get_security_by_ap(self, ap_object):
        return ap_object.get_flags()
        #from nmlib.getsec import get_ap_security
        #interface = self.wireless_device.get_ip_iface()
        #return get_ap_security( interface, ap_object.get_hw_address())
        
        #NM_802_11_AP_FLAGS_NONE = 0x0
        #NM_802_11_AP_FLAGS_PRIVACY = 0x1
        #NM_802_11_AP_SEC_NONE = 0x0
        #NM_802_11_AP_SEC_PAIR_WEP40 = 0x1
        #NM_802_11_AP_SEC_PAIR_WEP104 = 0x2
        #NM_802_11_AP_SEC_PAIR_TKIP = 0x4
        #NM_802_11_AP_SEC_PAIR_CCMP = 0x8
        #NM_802_11_AP_SEC_GROUP_WEP40 = 0x10
        #NM_802_11_AP_SEC_GROUP_WEP104 = 0x20
        #NM_802_11_AP_SEC_GROUP_TKIP = 0x40
        #NM_802_11_AP_SEC_GROUP_CCMP = 0x80
        #NM_802_11_AP_SEC_KEY_MGMT_PSK = 0x100
        #NM_802_11_AP_SEC_KEY_MGMT_802_1X = 0x200

        #ap = ap_object

        #wpa_flags = ap.get_wpa_flags()
        #rsn_flags = ap.get_rsn_flags()
        #flags = ap.get_flags()

        #if flags & NM_802_11_AP_FLAGS_PRIVACY:
            #if wpa_flags == NM_802_11_AP_SEC_NONE and rsn_flags == NM_802_11_AP_SEC_NONE :
                #return "none" # WEP
            #if not wpa_flags & NM_802_11_AP_SEC_KEY_MGMT_802_1X and not rsn_flags & NM_802_11_AP_SEC_KEY_MGMT_802_1X :
                #return "wpa-psk" # wpa
        #else:
            #return None

net_manager = NetManager()

class Settings(object):
    def __init__(self, setting_list):
        self.setting_list = setting_list 
        self.setting_state = {}
        self.settings = {}
        self.setting_lock = {}

    def init_items(self, connection):
        self.connection = connection 
        if connection not in self.settings:
            self.setting_lock[connection] = True
            #self.init_button_state(connection)
            setting_list = []
            for setting in self.setting_list:
                s = setting(connection, self.set_button)
                setting_list.append((s.tab_name, s))
            self.settings[connection] = setting_list
        return self.settings[connection][1][1]

    def set_button(self, name, state):
        #Dispatcher.set_button(name, state)
        self.setting_state[self.connection] = (name, state)
    
    def set_lock(self, lock):
        self.setting_lock[self.connection] = lock

    def get_lock(self):
        return self.setting_lock[self.connection]

    def clear(self):
        print "clear settings"
        self.setting_state = {}
        self.settings = {}

    def init_button_state(self, connection):
        if isinstance(connection, NMRemoteConnection):
            self.set_button("apply", True)
        else:
            self.set_button("save", False)

    def get_button_state(self):
        #if connection in self.setting_state.iterkeys():
        try:
            return self.setting_state[self.connection]
        except:
            return None

    def apply_changes(self):
        pass

