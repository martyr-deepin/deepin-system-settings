#!/usr/bin/env python
#-*- coding:utf-8 -*-

from nmlib.proxysettings import ProxySettings
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

        self.methods = gtk.combobox_new_text()

        method_list = ["None", "Manual", "Automatic"]
        map(lambda m: self.methods.append_text(m), method_list)

        self.http_entry = InputEntry()
        self.http_spin = SpinBox(8080, 0, 49151, 1, 50)
        self.https_entry = InputEntry()
        self.https_spin = SpinBox(0, 0, 49151, 1, 50)
        self.htp_entry = InputEntry()
        self.htp_spin = SpinBox(0, 0, 49151, 1, 50)
        self.socks_entry = InputEntry()
        self.socks_spin = SpinBox(0, 0, 49151, 1, 50)
        self.init()

        # Build ui
    def init(self):

        mode = self.proxysettings.get_proxy_mode()
        print mode
        mode_list = ["none", "auto", "manual"]
        container_remove_all(self.table)
        if mode == "none":
            self.table.attach(self.method_label, 0, 1, 0, 1)
            self.table.attach(self.methods, 1, 4, 0, 1)
            

        
       
        
        

