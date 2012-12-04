#!/usr/bin/env python
#-*- coding:utf-8 -*-
from nmlib.proxysettings import ProxySettings
from theme import app_theme
from dtk.ui.label import Label
from dtk.ui.entry import InputEntry
from dtk.ui.spin import SpinBox
from dtk.ui.combo import ComboBox
from dtk.ui.utils import container_remove_all
import gtk

class ProxyConfig(gtk.VBox):

    def __init__(self, slide_back_cb = None, change_crumb_cb = None):

        gtk.VBox.__init__(self)
        self.proxysetting = ProxySettings()
        self.slide_back = slide_back_cb
        self.change_crumb = change_crumb_cb

        self.table = gtk.Table(5, 4, False)
        #self.table.set_size_request(290, 165)
        table_align = gtk.Alignment(0, 0 ,0 , 0)
        table_align.set_padding(57, 0, 110, 0)
        table_align.add(self.table)

        self.method_label = Label("Method")
        self.http_label = Label("Http Proxy")
        self.https_label = Label("Https Proxy")
        self.ftp_label = Label("FTP Proxy")
        self.socks_label = Label("Socks Proxy")
        self.conf_label = Label("Configuration url")

        self.methods = gtk.combo_box_new_text()
        method_list = ["None", "Manual", "Automatic"]
        #self.methods = ComboBox([lambda m,i: (m, i), enumerate(method_list)])
        self.methods.connect("changed", self.method_changed)

        #method_list = ["None", "Manual", "Automatic"]
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

        self.pack_start(table_align, False, False)
        apply_button = gtk.Button("Apply")
        apply_button.connect("clicked", self.save_changes)
        buttons_aligns = gtk.Alignment(0.5 , 1, 0, 0)
        buttons_aligns.add(apply_button)
        self.pack_start(buttons_aligns, False , False)


    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb( 1, 1, 1) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

        # Build ui
    def init(self, first_start = False):
        mode_list = ["none", "manual", "auto"]
        if first_start:
            mode = self.proxysetting.get_proxy_mode()
            self.methods.set_active(mode_list.index(mode))
            #self.proxysetting.set_http_enabled(True)
        else:
            container_remove_all(self.table)
            mode = self.methods.get_active()
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

                self.proxysetting.set_http_enabled(True)

                http_host = self.proxysetting.get_http_host()
                http_port = self.proxysetting.get_http_port()
                https_host = self.proxysetting.get_https_host()
                https_port = self.proxysetting.get_https_port()
                ftp_host = self.proxysetting.get_ftp_host()
                ftp_port = self.proxysetting.get_ftp_port()
                socks_host = self.proxysetting.get_socks_host()
                socks_port = self.proxysetting.get_socks_port()

                print http_port, https_port
                self.http_entry.set_text(http_host)
                self.http_spin.set_value(int(http_port))
                self.https_entry.set_text(https_host)
                self.https_spin.set_value(int(https_port))
                self.ftp_entry.set_text(ftp_host)
                self.ftp_spin.set_value(int(ftp_port))
                self.socks_entry.set_text(socks_host)
                self.socks_spin.set_value(int(socks_port))

            else:
                self.table.attach(self.method_label, 0, 1, 0, 1)
                self.table.attach(self.methods, 1, 4, 0, 1)
                self.table.attach(self.conf_label, 0, 1, 1, 2)
                self.table.attach(self.conf_entry, 1, 4, 1, 2)
                conf_url = self.proxysetting.get_proxy_authconfig_url()
                self.conf_entry.set_text(conf_url)


        self.table.show_all()

    def method_changed(self, widget):
        self.init()
            
    def save_changes(self, widget):
        active = self.methods.get_active()
        if active == 0:
            self.proxysetting.set_proxy_mode("none")
            
        elif active == 1:
            http_host = self.http_entry.get_text()
            http_port = self.http_spin.get_value()
            https_host = self.https_entry.get_text()
            https_port = self.https_spin.get_value()
            ftp_host = self.ftp_entry.get_text()
            ftp_port = self.ftp_spin.get_value()
            socks_host = self.socks_entry.get_text()
            socks_port = self.socks_spin.get_value()

            mode = "manual"
            self.proxysetting.set_proxy_mode(mode)
            self.proxysetting.set_http_host(http_host)
            self.proxysetting.set_http_port(http_port)
            self.proxysetting.set_https_host(https_host)
            self.proxysetting.set_https_port(https_port)
            self.proxysetting.set_ftp_host(ftp_host)
            self.proxysetting.set_ftp_port(ftp_port)

            self.proxysetting.set_socks_host(socks_host)
            self.proxysetting.set_socks_port(socks_port)

        else:
            conf_url = self.conf_entry.get_text()
            self.proxysetting.set_proxy_mode = "auto"
            self.proxysetting.set_proxy_autoconfig_url = conf_url


        self.slide_back()
        self.change_crumb()
