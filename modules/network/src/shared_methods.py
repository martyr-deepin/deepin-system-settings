#!/usr/bin/env pythonelif 
#-*- coding:utf-8 -*-
from nm_modules import nm_module
from helper import Dispatcher, event_manager
from device_manager import DeviceManager
from nmlib.servicemanager import servicemanager
from nmlib.nm_remote_connection import NMRemoteConnection
from deepin_utils.ipc import is_dbus_name_exists
import dbus

from dss_log import log
from tray_log import tray_log



DEVICE_UNAVAILABLE = 0
DEVICE_AVAILABLE = 1
DEVICE_DISACTIVE = 1
DEVICE_ACTIVE = 2


class NetManager(object):

    def __init__(self):
        #self.init_devices()
        if is_dbus_name_exists("org.freedesktop.NetworkManager", False):
            tray_log.debug("network-manager start")

            if not nm_module.nmclient.networking_get_enabled():
                try:
                    nm_module.nmclient.networking_set_enabled()
                except Exception,e:
                    print "network enable failed", e

            servicemanager.connect("service-start", self.__on_service_start_do)
            servicemanager.connect("service-stop", self.__on_service_stop_do)
            self.device_manager = DeviceManager()

            self.cf = nm_module.nm_remote_settings.cf
            self.config_file = nm_module.nm_remote_settings.config_file
            self.cf.read(self.config_file)
            if "hidden" not in self.cf.sections():
                self.cf.add_section("hidden")

            bus = dbus.SystemBus()
            bus.add_signal_receiver(lambda i: Dispatcher.emit("switch-device", self.device_manager.wireless_devices[i]),
                                    dbus_interface = "com.deepin.network",
                                    signal_name = "DeviceChanged")
            bus.add_signal_receiver(lambda path: Dispatcher.emit("vpn-start", path),
                                    dbus_interface = "com.deepin.network",
                                    signal_name="VpnStart")
            bus.add_signal_receiver(lambda type: self.classify_network_type(type),
                                    dbus_interface = "com.deepin.network",
                                    signal_name="userToggleOff")
        else:
            tray_log.debug("network-manager disabled")
            pass

    def init_all_objects(self):
        self.device_manager = DeviceManager()

    def classify_network_type(self, type):
        event_manager.emit("user-toggle-off-%s"%type, None)

    def init_devices(self):
        self.device_manager.init_device()
        self.wired_devices = self.device_manager.get_wired_devices()
        if self.wired_devices:
            self.wired_device = self.wired_devices[0]
        else:
            self.wired_device = None
        self.wireless_devices = self.device_manager.get_wireless_devices()
        if self.wireless_devices:
            self.wireless_device = self.wireless_devices[0]
        else:
            self.wireless_device = None
        
    def __on_service_start_do(self, widget, s):
        print "Debug::service_start", s
        nm_module.update_cache()
        nm_module.init_objects()
        nm_module.nm_remote_settings.list_connections()
        nm_module.nmclient.get_devices()
        self.device_manager = DeviceManager()
        self.init_devices()
        Dispatcher.emit("service-start-do-more")
        #print servicemanager.get_name_owner(s)

    def __on_service_stop_do(self, widget, s):
        print "Debug::service_stop", s
        nm_module.cache.clearcache()
        nm_module.cache.clear_spec_cache()
        Dispatcher.emit("service-stop-do-more")

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

    def remove_hidden(self, connection):
        ssid = connection.get_setting("802-11-wireless").ssid
        self.cf.read(self.config_file)
        if ssid not in self.cf.options("hidden"):
            self.cf.remove_option("hidden", ssid)
        try:
            self.cf.write(open(self.config_file, "w"))
            print "save succeed"
        except:
            print "save failded in addHidden"

        #print servicemanager.get_name_owner(s)


    def get_wired_state(self):
        self.wired_devices = self.device_manager.get_wired_devices()
        if self.wired_devices is []:
            # No wired device
            return None
        else:
            dev_state = any([device.get_state() > 20 for device in self.wired_devices])
            conn_state = any([device.is_active() and nm_module.nmclient.get_wired_active_connection() for device in self.wired_devices])
            return (dev_state, conn_state)
            #state_list = []
            #for device in self.wired_devices:
            #    state_list.append(device.get_state() == 20)
            #if True in state_list:
            #    return (False, False)
            #else:
            #    '''
            #    TODO: my_list.index(x) is an error if there is no such item, 
            #          so please check whether or not there is such item in list at first
            #    '''
            #    if False in state_list:
            #        return (True, self.wired_devices[state_list.index(False)].is_active())
            #    else:
            #        return (True, False)

    def active_wired_device(self):
        self.wired_devices = self.device_manager.get_wired_devices()
        if any([d.get_active_connection() for d in self.wired_devices]):
            return

        for device in self.wired_devices:
            if not device.is_active():
                connections = nm_module.nm_remote_settings.get_wired_connections()
                if not connections:
                    connection = nm_module.nm_remote_settings.new_wired_connection()
                    nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')
                device_ethernet = nm_module.cache.get_spec_object(device.object_path)
                device_ethernet.auto_connect()

    def disactive_wired_device(self, device_spec=[]):
        if device_spec:
            self.wired_devices = device_spec
        else:
            self.wired_devices = self.device_manager.get_wired_devices()
        for device in self.wired_devices:
            wired = nm_module.cache.get_spec_object(device.object_path)
            if wired:
                wired.device_wired_disconnect()
            device.nm_device_disconnect()

    # Wireless
    def get_wireless_state(self):
        devices = self.device_manager.get_wireless_devices()
        if not devices:
            return None
        else:
            dev_state = any([device.get_state() > 20 for device in devices])
            conn_state = any([device.is_active() for device in devices])
            return (dev_state, conn_state)

    def get_ap_list(self, device):
        self.wireless_devices = self.device_manager.get_wireless_devices()
        if not self.wireless_devices:
            return []

        device_wifi = nm_module.cache.get_spec_object(device.object_path)
        return device_wifi.order_ap_list()

    def get_active_connection(self, ap_list, device):
        index = []
        self.wireless_devices = self.device_manager.get_wireless_devices()
        if self.wireless_devices:
            self.wireless_device = device
            active_connection = self.wireless_device.get_active_connection()
            if active_connection:
                #print active_connection.get_state(), "Debug in get active connection"
                try:
                    ssid = active_connection.get_connection().get_setting("802-11-wireless").ssid
                    index.append([ap.get_ssid() for ap in ap_list].index(ssid))
                    return index
                except:
                    return []
        else:
            return []

    def save_and_connect(self, serect, connection, ap):
        print connection, "save and connect"
        (setting_name, method) = connection.guess_secret_info() 
        print setting_name, method
        connection.settings_dict[setting_name][method] = serect
        connection.update()
        if ap:
            nm_module.nmclient.activate_connection_async(connection.object_path,
                                       self.wireless_device.object_path,
                                       ap.object_path)
        else:
            nm_module.nmclient.activate_connection_async(connection.object_path,
                                       self.wireless_device.object_path,
                                       "/")
        
    def connect_wireless_by_ssid(self, ssid, device=None):
        # TODO will change device to no arg, since tray doesnt change yet
        if device:
            device_wifi = nm_module.cache.get_spec_object(device.object_path)
        else:
            device_wifi = nm_module.cache.get_spec_object(self.wireless_device.object_path)
        return device_wifi.active_ssid_connection(ssid)


    def active_wireless_device(self, device):
        device_wifi = nm_module.cache.get_spec_object(device.object_path)
        device_wifi.auto_connect()

    def disactive_wireless_device(self):
        self.wireless_devices = self.device_manager.get_wireless_devices()
        for device in self.wireless_devices:
            wifi = nm_module.cache.get_spec_object(device.object_path)
            wifi.device_wifi_disconnect()

    def get_mm_devices(self):
        cdma = nm_module.mmclient.get_cdma_device()
        gsm = nm_module.mmclient.get_gsm_device()
        return cdma + gsm
    
    def connect_mm_device(self):
        cdma = nm_module.mmclient.get_cdma_device()
        gsm = nm_module.mmclient.get_gsm_device()
        device = cdma + gsm
        if device:
            d = device[0]
            from mm.mmdevice import MMDevice
            MMDevice(d).auto_connect()

    def disconnect_mm_device(self):
        device = nm_module.nmclient.get_modem_devices()
        if device:
            device[0].nm_device_disconnect()

    def get_security_by_ap(self, ap_object):
        return ap_object.get_flags()
    
    def get_sec_ap(self, ap_object):
        "fast version of get security using wpa_cli"
        hw_address = ap_object.get_hw_address().lower()
        bus = dbus.SystemBus()                                                   
        proxy = bus.get_object("com.deepin.network", "/com/deepin/network")      
        interface = dbus.Interface(proxy, "com.deepin.network")                  
        log.debug(hw_address)
        return interface.get_ap_sec(hw_address)        

    def emit_wifi_switch(self, index):
        bus = dbus.SystemBus()
        proxy = bus.get_object("com.deepin.network", "/com/deepin/network")
        interface = dbus.Interface(proxy, "com.deepin.network")
        interface.emitDeviceChanged(index)

    def emit_vpn_start(self, active_conn):
        bus = dbus.SystemBus()
        proxy = bus.get_object("com.deepin.network", "/com/deepin/network")
        interface = dbus.Interface(proxy, "com.deepin.network")
        interface.emitVpnStart(active_conn.object_path)
        print "emit vpn start"

    def emit_vpn_setting_change(self, connection):
        bus = dbus.SystemBus()
        proxy = bus.get_object("com.deepin.network", "/com/deepin/network")
        interface = dbus.Interface(proxy, "com.deepin.network")
        interface.emitVpnSettingChange(connection.object_path)

    def emit_user_toggle_off(self, network_type):
        bus = dbus.SystemBus()
        proxy = bus.get_object("com.deepin.network", "/com/deepin/network")
        interface = dbus.Interface(proxy, "com.deepin.network")
        interface.emitUserToggleOff(network_type)

net_manager = NetManager()

class Settings(object):
    def __init__(self, section):
        self.section = section 
        #print "Settings:", section
        self.setting_state = {}
        self.settings = {}
        self.setting_lock = {}

    def init_items(self, connection):
        self.connection = connection 
        # 
        self.connection.settings_obj = self
        # 新增以下几个变量，用于set_button时判断输入的合法性。
        # 基本设置
        self.mac_is_valid = True
        self.ipv4_ip_is_valid = True
        self.ipv4_dns_is_valid = True
        self.ipv6_ip_is_valid = True
        self.ipv6_dns_is_valid = True
        # 无线设置
        self.wlan_encry_is_valid = True
        # 拨号设置
        self.dsl_is_valid = True
        self.ppp_is_valid = True
        # VPN设置
        self.vpn_is_valid = True

        if connection not in self.settings:
            self.setting_lock[connection] = True
            #self.init_button_state(connection)
                # 新增了settings_obj参数，方便访问xxx_is_valid变量
            s = self.section(connection, self.set_button, settings_obj=self)
            self.settings[connection] = s
        return self.settings[connection]

    #################
    def set_button(self, name, state):
        #print "-"*15
        #print "mac_is_valid:", self.mac_is_valid, "ipv4:", self.ipv4_ip_is_valid, self.ipv4_dns_is_valid, "ipv6:", self.ipv6_ip_is_valid, self.ipv6_dns_is_valid
        #print "wlan dsl ppp vpn", self.wlan_encry_is_valid, self.dsl_is_valid, self.ppp_is_valid, self.vpn_is_valid
        #print "-"*15
        # 输入合法性检查，再统一设置按钮状态
        #log.debug("someone set button", name, state)
        if self.mac_is_valid and \
                self.ipv4_ip_is_valid and \
                self.ipv4_dns_is_valid and \
                self.ipv6_ip_is_valid and \
                self.ipv6_dns_is_valid and \
                self.wlan_encry_is_valid and \
                self.dsl_is_valid and \
                self.ppp_is_valid and \
                self.vpn_is_valid:
            Dispatcher.set_button(name, True)
            self.setting_state[self.connection] = (name, True)
        else:
            Dispatcher.set_button(name, False)
            self.setting_state[self.connection] = (name, False)
        #print "set button", name, state, self.connection
    
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
            Dispatcher.set_button("save", False)
        else:
            if connection.check_setting_finish():
                Dispatcher.set_button("save", True)
            else:
                Dispatcher.set_button("save", False)

    def get_button_state(self, connection):
        try:
            return self.setting_state[connection]
        except:
            log.debug("no button state for this connection, will init one")
            self.init_button_state(connection)
            return None



    def apply_changes(self):
        pass

