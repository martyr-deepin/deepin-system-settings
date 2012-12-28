#!/usr/bin/env python
#-*- coding:utf-8 -*-
from nmlib.proxysettings import ProxySettings
from dtk.ui.label import Label
from dtk.ui.button import Button
from dtk.ui.new_entry import InputEntry
from dtk.ui.spin import SpinBox
from dtk.ui.combo import ComboBox
from dtk.ui.utils import container_remove_all
import gtk

import style
from constants import FRAME_VERTICAL_SPACING, TEXT_WINDOW_TOP_PADDING, TEXT_WINDOW_LEFT_PADDING

def wrap_all_with_align(obj, attr_list):
    for attr in attr_list:
        if attr is not "add_mnemonic_label" and attr is not "remove_mnemonic_label":
            target = getattr(obj, attr)
            align = style.wrap_with_align(target)
            setattr(obj, attr +"_align", align)

class ProxyConfig(gtk.Alignment):

    def __init__(self, slide_back_cb=None, change_crumb_cb=None):

        gtk.Alignment.__init__(self)
        self.set_padding(TEXT_WINDOW_TOP_PADDING, 0, TEXT_WINDOW_LEFT_PADDING, TEXT_WINDOW_LEFT_PADDING)
        self.proxysetting = ProxySettings()
        self.slide_back = slide_back_cb
        self.change_crumb = change_crumb_cb

        self.table = gtk.Table(5, 4, False)
        #self.table.set_row_spacings(17)
        #self.table.set_col_spacing(0, 30)
        #self.table.set_size_request(340, -1)

        # Add UI Align
        vbox = gtk.VBox()
        self.add(vbox)
        vbox.pack_start(self.table, False, False)

        self.method_label = Label("Method")
        self.http_label = Label("Http Proxy")
        self.https_label = Label("Https Proxy")
        self.ftp_label = Label("FTP Proxy")
        self.socks_label = Label("Socks Proxy")
        self.conf_label = Label("Configuration url")

        self.methods = ComboBox([("None", 0),
                                 ("Manual", 1),
                                 ("Automatic", 2)],
                                 max_width=222)

        self.methods.set_size_request(222,22)
        self.methods.connect("item-selected", self.method_changed)

        width ,height = 222 ,22
        self.http_entry = InputEntry()
        self.http_entry.set_size(width, height)
        self.http_spin = SpinBox(8080, 0, 49151, 1, 60)
        self.https_entry = InputEntry()
        self.https_entry.set_size(width, height)
        self.https_spin = SpinBox(0, 0, 49151, 1, 60)
        self.ftp_entry = InputEntry()
        self.ftp_entry.set_size(width, height)
        self.ftp_spin = SpinBox(0, 0, 49151, 1, 60)
        self.socks_entry = InputEntry()
        self.socks_entry.set_size(width, height)
        self.socks_spin = SpinBox(0, 0, 49151, 1, 60)
        self.conf_entry = InputEntry()
        self.conf_entry.set_size(width, height)
        #self.init(True)
        #label_list = ["method_label", "http_label", "https_label", "ftp_label", "socks_label", "conf_label"] 
        l =  filter(lambda l: l.endswith("label") or l.endswith("entry") or l.endswith("spin"), dir(self))
        wrap_all_with_align(self, l)
        self.methods_align = style.wrap_with_align(self.methods)


        #hbox.pack_start(table_align, False, False)
        apply_button = Button("Apply")
        apply_button.connect("clicked", self.save_changes)
        buttons_aligns = gtk.Alignment(1, 1, 0, 0)
        buttons_aligns.add(apply_button)
        vbox.pack_end(buttons_aligns, False, False)
        self.connect("expose-event", self.expose_event)

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
            index = mode_list.index(mode)
            self.methods.set_select_index(index)
            # Just emit signal
            self.methods.emit("item-selected", None, 0, 0)
            #self.proxysetting.set_http_enabled(True)
        else:
            container_remove_all(self.table)
            mode = self.methods.get_current_item()[1]
            if mode == 0:
                self.table.attach(self.method_label_align, 0, 1, 0, 1)
                self.table.attach(self.methods_align, 1, 3, 0, 1)
            elif mode == 1:
                self.table.attach(self.method_label_align, 0, 1, 0, 1)
                self.table.attach(self.methods_align, 1, 3, 0, 1)

                self.table.attach(self.http_label_align, 0, 1, 1, 2)
                self.table.attach(self.http_entry_align, 1, 3, 1, 2)
                self.table.attach(self.http_spin_align, 3, 4, 1, 2)

                self.table.attach(self.https_label_align, 0, 1, 2, 3)
                self.table.attach(self.https_entry_align, 1, 3, 2, 3)
                self.table.attach(self.https_spin_align, 3, 4, 2, 3)
                self.table.attach(self.ftp_label_align, 0, 1, 3, 4)
                self.table.attach(self.ftp_entry_align, 1, 3, 3, 4)
                self.table.attach(self.ftp_spin_align, 3, 4, 3, 4)
                self.table.attach(self.socks_label_align, 0, 1, 4, 5)
                self.table.attach(self.socks_entry_align, 1, 3, 4, 5)
                self.table.attach(self.socks_spin_align, 3, 4, 4, 5)

                self.proxysetting.set_http_enabled(True)

                http_host = self.proxysetting.get_http_host()
                http_port = self.proxysetting.get_http_port()
                https_host = self.proxysetting.get_https_host()
                https_port = self.proxysetting.get_https_port()
                ftp_host = self.proxysetting.get_ftp_host()
                ftp_port = self.proxysetting.get_ftp_port()
                socks_host = self.proxysetting.get_socks_host()
                socks_port = self.proxysetting.get_socks_port()

                self.http_entry.set_text(http_host)
                self.http_spin.set_value(int(http_port))
                self.https_entry.set_text(https_host)
                self.https_spin.set_value(int(https_port))
                self.ftp_entry.set_text(ftp_host)
                self.ftp_spin.set_value(int(ftp_port))
                self.socks_entry.set_text(socks_host)
                self.socks_spin.set_value(int(socks_port))

            else:
                self.table.attach(self.method_label_align, 0, 1, 0, 1)
                self.table.attach(self.methods_align, 1, 3, 0, 1)
                self.table.attach(self.conf_label_align, 0, 1, 1, 2)
                self.table.attach(self.conf_entry_align, 1, 3, 1, 2)
                conf_url = self.proxysetting.get_proxy_authconfig_url()
                self.conf_entry.set_text(conf_url)
            style.set_table(self.table)
            self.show_all()

    def method_changed(self, widget, content, value, index):
        self.init()
            
    def save_changes(self, widget):
        active = self.methods.get_current_item()[1] 
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
