#!/usr/bin/env python
#-*- coding:utf-8 -*-
from nmlib.proxysettings import ProxySettings
from dtk.ui.label import Label
from dtk.ui.button import Button
from dtk.ui.entry import InputEntry
from dtk.ui.spin import SpinBox
from dtk.ui.combo import ComboBox
from elements import MyRadioButton as RadioButton
from elements import TableAsm
from dtk.ui.utils import container_remove_all
import gtk

import style
from constants import  STANDARD_LINE, CONTENT_FONT_SIZE
from foot_box import FootBox
from helper import Dispatcher
from nls import _

from dss_log import log

def wrap_all_with_align(obj, attr_list, w=None):
    for attr in attr_list:
        target = getattr(obj, attr)
        if w:
            align = style.wrap_with_align(target, width=w)
        else:
            align = style.wrap_with_align(target)
        setattr(obj, attr +"_align", align)

class ProxyConfig(gtk.VBox):
    ENTRY_WIDTH = 222

    def __init__(self):

        gtk.VBox.__init__(self)

        self.proxysetting = ProxySettings()
        self.__init_widget()
        #self.init()

    def __row_entry_spin(self, label_name, table, types):
        label = Label(label_name,
                      text_size=CONTENT_FONT_SIZE,
                      enable_select=False,
                      enable_double_click=False)
        label.set_can_focus(False)

        label_align = style.wrap_with_align(label, width = 260)

        entry = InputEntry()
        entry.set_size(self.ENTRY_WIDTH, 22)
        spin = SpinBox(0, 0, 49151, 1, 60)
        spin.value_entry.connect("changed", lambda w, v: spin.update_and_emit(int(v)))

        hbox = gtk.HBox(spacing=10)
        hbox.set_size_request(-1 ,22)
        hbox_align = style.wrap_with_align(hbox, align="left")
        hbox.pack_start(entry)
        hbox.pack_start(spin)

        table.row_attach((label_align, hbox_align))
        return [entry, spin]

    def expose_line(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        style.draw_out_line(cr, rect, exclude=["left", "right", "top"])
    
    def __row_check(self, label_name, table, main=None):
        check = RadioButton(main, label_name)
        check_align = style.wrap_with_align(check, align="left", width=260)
        check_align.set_padding(0, 0, 200, 1)
        table.row_attach(check_align)
        return check

    def __init_widget(self):
        self.manual_table = TableAsm()

        self.manual_radio = self.__row_check(_("Manual"), self.manual_table, None)
        self.http_entry, self.http_spin = self.__row_entry_spin(_("Http Proxy"), self.manual_table, "http")
        self.https_entry, self.https_spin = self.__row_entry_spin(_("Https Proxy"), self.manual_table, "https")
        self.ftp_entry, self.ftp_spin = self.__row_entry_spin(_("FTP Proxy"), self.manual_table, "ftp")
        self.socks_entry, self.socks_spin = self.__row_entry_spin(_("Socks Proxy"), self.manual_table, "socks")

        self.auto_table = TableAsm(left_width=STANDARD_LINE, right_width=self.ENTRY_WIDTH)
        self.auto_radio = self.__row_check(_("Automatic"), self.auto_table, self.manual_radio)
        self.conf_entry = self.auto_table.row_input_entry(_("Configuration url"))

        auto_align = gtk.Alignment(0, 0, 0, 0)
        auto_align.add(self.auto_table)

        table_box = gtk.VBox(spacing=15)
        table_box.pack_start(self.manual_table, False, False)
        table_box.pack_start(auto_align, False, False)

        align = gtk.Alignment(0, 0, 0 , 0)
        align.set_padding(35, 0, 0, 0)
        align.add(table_box)
        self.pack_start(align)

        apply_button = Button(_("Apply"))
        apply_button.connect("clicked", self.save_changes)
        foot_box = FootBox()
        align.connect("expose-event", self.expose_line)
        foot_box.set_buttons([apply_button])
        self.pack_end(foot_box, False, False)
        #self.connect("expose-event", self.expose_event)

        self.manual_radio.connect("toggled", self.manual_radio_selected_cb)
        self.auto_radio.connect("toggled", self.auto_radio_selected_cb)
        self.manual_table.table_build()
        self.auto_table.table_build()
        
    def manual_radio_selected_cb(self, widget):
        log.debug("")
        sensitive = widget.get_active()
        self.table_set_sensitive(self.manual_table, sensitive)
       
    def auto_radio_selected_cb(self, widget):
        log.debug("")
        sensitive = widget.get_active()
        self.table_set_sensitive(self.auto_table, sensitive)

    def table_set_sensitive(self, table, sensitive):
        items = table.shared
        for item in items:
            if item[1] != None:
                map(lambda i: i.set_sensitive(sensitive), item)
            else:
                log.debug("radio button", item)
        
    def init(self):
        mode = self.proxysetting.get_proxy_mode()
        if mode == "manual":
            self.manual_radio.set_active(True)
            self.table_set_sensitive(self.auto_table, False)
            self.proxysetting.set_http_enabled(True)

            http_host = self.proxysetting.get_http_host()
            http_port = self.proxysetting.get_http_port() or 8080
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
        elif mode == "auto":
            self.auto_radio.set_active(True)
            self.table_set_sensitive(self.manual_table, False)
            conf_url = self.proxysetting.get_proxy_authconfig_url()
            self.conf_entry.set_text(conf_url)

    def save_changes(self, widget):
        
        log.debug(self.manual_radio.get_active())
            #self.proxysetting.set_proxy_mode("none")
        if self.manual_radio.get_active(): 
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
            self.proxysetting.set_proxy_mode("auto")
            self.proxysetting.set_proxy_autoconfig_url(conf_url)

        Dispatcher.to_main_page()
