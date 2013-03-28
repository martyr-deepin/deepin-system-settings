#!/usr/bin/env python
#-*- coding:utf-8 -*-

#import dss
import time
t = time.time()
from shared_methods import net_manager, nm_module
print time.time() - t
import gtk

def get_ap_list(widget):
    print net_manager.get_ap_list()

def get_wired_connection(widget):
    print nm_module.nm_remote_settings.get_wired_connections()

def get_wireless_connection(widget):
    print nm_module.nm_remote_settings.get_wireless_connections()

def get_devices(widget):
    print "wired", net_manager.wired_devices
    print "wireless", net_manager.wireless_devices
    print "nmclient", nm_module.nmclient.get_wired_devices()

    assert net_manager.wired_devices == nm_module.nmclient.get_wired_devices()
    print "wired_spec",nm_module.cache.get_spec_object(net_manager.wired_device.object_path)
    print "wireless_spec",nm_module.cache.get_spec_object(net_manager.wireless_device.object_path)


def init_all(widget):
    print nm_module.nm_remote_settings.list_connections()
    print nm_module.nmclient.get_devices()

if __name__ == "__main__":
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_title("Main")
    win.set_size_request(100,50)

    win.set_border_width(11)
    win.set_resizable(True)
    win.connect("destroy", lambda w: gtk.main_quit())

    button = gtk.Button("get connection")

    test_function = get_devices
    button.connect("clicked", test_function)
    win.add(button)

    win.show_all()
    
    gtk.main()
