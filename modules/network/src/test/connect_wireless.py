#! /usr/bin/env python

from nmlib.nm_remote_settings import NMRemoteSettings
from nmlib.nmclient import NMClient
from nmlib.nmdevice_wifi import NMDeviceWifi

nmclient = NMClient()
device_path = nmclient.get_wireless_device()
wireless_device = NMDeviceWifi(device_path)
ap_list = wireless_device.update_ap_list()
remote_setting = NMRemoteSettings()

def list_ap():
    print "select ssid to connect:"
    for i in range(len(ap_list)):
        print i,ap_list[i].get_ssid()

def list_security():
    security_list = ["wep", "wpa-psk"]
    print "select encrypt method:\n"
    for i in range(len(security_list)):
        print i, security_list[i]

if __name__ == "__main__":
    list_ap()
    ssid = raw_input("\nplease input the ssid to connect:\n")

    list_security()
    method = raw_input("\nplease input encrypt method:\n")
    
    pwd = raw_input("\nplease input wireless password:\n")
    
    conn_path = remote_setting.new_spec_wireless_connection(ssid, method, pwd)
    
    device_path = nmclient.get_wireless_device()
    
    specific_path = wireless_device.get_ap_by_ssid(ssid).object_path

    nmclient.activate_connection(conn_path, device_path, specific_path)
    
