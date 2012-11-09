#!/usr/bin/env python
#-*- coding:utf-8 -*-

from nmlib.proxysettings import ProxySettings
from theme import app_theme
from dtk.ui.label import Label
from dtk.ui.entry import InputEntry
from dtk.ui.spin import SpinBox
from dtk.ui.utils import container_remove_all
import gtk

class ProxyConfig(gtk.VBox):

    def __init__(self,a,b ):
        gtk.VBox.__init__(self)
        self.proxysetting = ProxySettings()

        self.table = gtk.Table(5, 4, False)

        self.method_label = Label("Method")
        self.http_label = Label("Http Proxy")
        self.https_label = Label("Https Proxy")
        self.ftp_label = Label("FTP Proxy")
        self.socks_label = Label("Socks Proxy")
        self.conf_label = Label("Configuration url")

        self.methods = gtk.combo_box_new_text()
        self.methods.connect("changed", self.method_changed)

        method_list = ["None", "Manual", "Automatic"]
        map(lambda m: self.methods.append_text(m), method_list)
        
        width ,height = 100 ,20
        self.http_entry = InputEntry()
        self.http_entry.set_size(width, height)
        self.http_spin = SpinBox(8080, 0, 49151, 1, 50)
        self.https_entry = InputEntry()
        self.https_entry.set_size(width, height)
        self.https_spin = SpinBox(0, 0, 49151, 1, 50)
        self.ftp_entry = InputEntry()
        self.ftp_entry.set_size(width, height)
        self.ftp_spin = SpinBox(0, 0, 49151, 1, 50)
        self.socks_entry = InputEntry()
        self.socks_entry.set_size(width, height)
        self.socks_spin = SpinBox(0, 0, 49151, 1, 50)
        self.conf_entry = InputEntry()
        self.conf_entry.set_size(width, height)
        self.init(True)

        self.pack_start(self.table, False, False)

        # Build ui
    def init(self, first_start = False):
        mode_list = ["none", "manual", "auto"]
        if first_start:
            mode = self.proxysetting.get_proxy_mode()
            self.methods.set_active(mode_list.index(mode))

        mode = self.methods.get_active()
        container_remove_all(self.table)
        if mode == 0:
            self.table.attach(self.method_label, 0, 1, 0, 1)
            self.table.attach(self.methods, 1, 4, 0, 1)
        elif mode == 1:
            self.table.attach(self.method_label, 0, 1, 0, 1)
            self.table.attach(self.methods, 1, 4, 0, 1)

            self.table.attach(self.http_label, 0, 1, 1, 2)
            self.table.attach(self.http_entry, 1, 3, 1, 2)
            self.table.attach(self.http_spin, 3, 4, 1, 2)

            self.table.attach(self.https_label, 0, 1, 2, 3)
            self.table.attach(self.https_entry, 1, 3, 2, 3)
            self.table.attach(self.https_spin, 3, 4, 2, 3)
            self.table.attach(self.ftp_label, 0, 1, 3, 4)
            self.table.attach(self.ftp_entry, 1, 3, 3, 4)
            self.table.attach(self.ftp_spin, 3, 4, 3, 4)
            self.table.attach(self.socks_label, 0, 1, 4, 5)
            self.table.attach(self.socks_entry, 1, 3, 4, 5)
            self.table.attach(self.socks_spin, 3, 4, 4, 5)

        else:
            self.table.attach(self.method_label, 0, 1, 0, 1)
            self.table.attach(self.methods, 1, 4, 0, 1)
            self.table.attach(self.conf_label, 0, 1, 1, 2)
            self.table.attach(self.conf_entry, 1, 4, 1, 2)

        self.table.show_all()

    

    def method_changed(self, widget):
        self.init()
            

        
       
        
        

