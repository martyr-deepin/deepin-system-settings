#!/usr/bin/env python
#-*- coding:utf-8 -*-
from nmlib.proxysettings import ProxySettings
from dtk.ui.label import Label
from dtk.ui.button import Button
from dtk.ui.new_entry import InputEntry
from dtk.ui.address_entry import IpAddressEntry
from dtk.ui.spin import SpinBox
from elements import MyRadioButton as RadioButton
from elements import TableAsm
from dtk.ui.utils import container_remove_all
import gtk

import style
from constants import TEXT_WINDOW_TOP_PADDING, TEXT_WINDOW_LEFT_PADDING, STANDARD_LINE, CONTENT_FONT_SIZE
from foot_box import FootBox
from helper import Dispatcher
from nls import _

def wrap_all_with_align(obj, attr_list, w=None):
    for attr in attr_list:
        target = getattr(obj, attr)
        if w:
            align = style.wrap_with_align(target, width=w)
        else:
            align = style.wrap_with_align(target)
        setattr(obj, attr +"_align", align)

class proxyConfig(gtk.VBox):
    ENTRY_WIDTH = 222

    def __init__(self):

        gtk.VBox.__init__(self)
        #self.set_padding(TEXT_WINDOW_TOP_PADDING, 0, TEXT_WINDOW_LEFT_PADDING, TEXT_WINDOW_LEFT_PADDING)
        self.proxysetting = ProxySettings()

        self.table = gtk.Table(5, 4, False)

        # Add UI Align
        #table_align = gtk.Alignment()
        table_align = gtk.Alignment(0, 0, 0, 0)
        table_align.connect("expose-event", self.expose_line)
        table_align.set_padding(30, 0, 0, 0)
        table_align.add(self.table)
        self.pack_start(table_align, True, True)

        self.method_label = Label(_("Method"),
                               enable_select=False,
                               enable_double_click=False)
        self.http_label = Label(_("Http Proxy"),
                               enable_select=False,
                               enable_double_click=False)
        self.https_label = Label(_("Https Proxy"),
                               enable_select=False,
                               enable_double_click=False)
        self.ftp_label = Label(_("FTP Proxy"),
                               enable_select=False,
                               enable_double_click=False)
        self.socks_label = Label(_("Socks Proxy"),
                               enable_select=False,
                               enable_double_click=False)
        self.conf_label = Label(_("Configuration url"),
                               enable_select=False,
                               enable_double_click=False)

        self.methods = ComboBox([(_("None"), 0),
                                 (_("Manual"), 1),
                                 (_("Automatic"), 2)],
                                 fixed_width=self.ENTRY_WIDTH )

        self.methods.set_size_request(-1,22)
        self.methods.connect("item-selected", self.method_changed)

        width , height = self.ENTRY_WIDTH , 22
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
        label_list = ["method_label", "http_label", "https_label", "ftp_label", "socks_label", "conf_label"] 
        entry_list = ["http_entry", "https_entry", "ftp_entry", "socks_entry", "conf_entry"]
        spin_list = ["http_spin", "https_spin", "ftp_spin", "socks_spin"]

        wrap_all_with_align(self, label_list, STANDARD_LINE )
        wrap_all_with_align(self, entry_list)
        wrap_all_with_align(self, spin_list)
        
        for label in label_list:
            l = getattr(self, label)
            l.set_can_focus(False)

        self.methods_align = style.wrap_with_align(self.methods)
        #for entry in entry_list:
            #getattr(self, entry).set_size_request(self.ENTRY_WIDTH, 22)


        #hbox.pack_start(table_align, False, False)
        apply_button = Button(_("Apply"))
        apply_button.connect("clicked", self.save_changes)
        #buttons_aligns = gtk.Alignment(1, 1, 0, 0)
        #buttons_aligns.add(apply_button)
        foot_box = FootBox()
        foot_box.set_buttons([apply_button])
        self.pack_end(foot_box, False, False)
        self.connect("expose-event", self.expose_event)

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb( 1, 1, 1) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

    def expose_line(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        style.draw_out_line(cr, rect, exclude=["left", "right", "top"])

        # Build ui
    def init(self, first_start = False):
        mode_list = ["none", "manual", "auto"]
        if first_start:
            mode = self.proxysetting.get_proxy_mode()
            index = mode_list.index(mode)
            self.methods.set_select_index(index)
            # Just emit signal
            self.methods.emit("item-selected", None, 0, 0)
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
            self.queue_draw()

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

        Dispatcher.to_main_page()

class ProxyConfig(gtk.VBox):
    ENTRY_WIDTH = 222

    def __init__(self):

        gtk.VBox.__init__(self)

        self.proxysetting = ProxySettings()
        self.__init_widget()
        self.init()

    def __row_entry_spin(self, label_name, table):
        label = Label(label_name,
                      text_size=CONTENT_FONT_SIZE,
                      enable_select=False,
                      enable_double_click=False)
        label.set_can_focus(False)

        label_align = style.wrap_with_align(label, width = 260)

        entry = InputEntry()
        entry.set_size(self.ENTRY_WIDTH, 22)
        spin = SpinBox(0, 0, 49151, 1, 60)

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
        check_align = style.wrap_with_align(check, width=260)
        table.row_attach(check_align)
        return check

    def __init_widget(self):
        self.manual_table = TableAsm()

        self.manual_radio = self.__row_check(_("Manual"), self.manual_table, None)
        self.http_entry, self.http_spin = self.__row_entry_spin(_("Http Proxy"), self.manual_table)
        self.https_entry, self.https_spin = self.__row_entry_spin(_("Https Proxy"), self.manual_table)
        self.ftp_entry, self.ftp_spin = self.__row_entry_spin(_("FTP Proxy"), self.manual_table)
        self.socks_entry, self.socks_spin = self.__row_entry_spin(_("Socks Proxy"), self.manual_table)

        self.auto_table = TableAsm(right_width=self.ENTRY_WIDTH)
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
        #buttons_aligns = gtk.Alignment(1, 1, 0, 0)
        #buttons_aligns.add(apply_button)
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
       self.manual_table.set_sensitive(widget.get_active()) 
       self.manual_radio.set_sensitive(True)
    
    def auto_radio_selected_cb(self, widget):
       self.auto_table.set_sensitive(widget.get_active())
       self.auto_radio.set_sensitive(True)

    
    def init(self):
        mode = self.proxysetting.get_proxy_mode()
        if mode == "manual":
            self.manual_radio.set_active(True)
            self.auto_table.set_sensitive(False)
            self.auto_radio.set_sensitive(True)
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
            self.manual_table.set_sensitive(False)
            self.manual_radio.set_sensitive(True)
            conf_url = self.proxysetting.get_proxy_authconfig_url()
            self.conf_entry.set_text(conf_url)

    def save_changes(self, widget):
        
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
            self.proxysetting.set_proxy_mode = "auto"
            self.proxysetting.set_proxy_autoconfig_url = conf_url

        Dispatcher.to_main_page()
