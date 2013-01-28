#!/usr/bin/env python
#-*- coding:utf-8 -*-

from dtk.ui.label import Label
from dtk.ui.entry import InputEntry
from nmlib.nm_utils import TypeConvert
from dtk.ui.button import OffButton
from nmlib.nm_remote_connection import NMRemoteConnection
from dtk.ui.utils import container_remove_all
import gtk

import style
from constants import CONTENT_FONT_SIZE, TITLE_FONT_SIZE, WIDGET_HEIGHT
from nls import _
from container import MyRadioButton as RadioButton

def wrap_with_align(self, widget_list):
    for widget in widget_list:
        w = getattr(self, widget)
        align = style.wrap_with_align(w)
        setattr(self, widget+"_align", align)

class IPV4Conf(gtk.VBox):
    ENTRY_WIDTH = 150
    def __init__(self, connection=None, set_button_callback=None, dns_only=False):
        
        gtk.VBox.__init__(self)
        self.tab_name = _("IPv4 Setting")
        self.connection = connection 
        self.set_button = set_button_callback
        self.dns_only = dns_only
        self.table = gtk.Table(9, 2, False)
        # Ip configuration
        self.ip_label = Label(_("Automatic get IP address"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.auto_ip = OffButton()

        self.addr_label = Label(_("IP Address:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.addr_entry = InputEntry()
        self.addr_entry.set_sensitive(False)

        self.mask_label = Label(_("Mask:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.mask_entry = InputEntry()
        
        self.gate_label = Label(_("Gateway:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.gate_entry = InputEntry()
        
        #DNS configuration
        self.dns_label = Label( _("Automatic get DNS server"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.auto_dns = OffButton()

        self.master_dns = Label(_("Primary DNS server address:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.slave_dns = Label(_("Slave DNS server address:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.master_entry = InputEntry()
        self.slave_entry = InputEntry()
        
        __widget_list = ["ip_label", "addr_label", "addr_entry",
                         "mask_label", "mask_entry", "gate_label", "gate_entry",
                         "dns_label", "master_entry", "slave_entry",
                         "slave_dns", "master_dns"]

        wrap_with_align(self, __widget_list)

        self.auto_ip_align = style.wrap_with_align(self.auto_ip, align="left")
        self.auto_dns_align = style.wrap_with_align(self.auto_dns, align="left")

        # TODO UI change
        style.draw_background_color(self)
        style.set_table(self.table)
        align = style.set_box_with_align(self.table, 'text')
        self.add(align)
        self.addr_entry.set_size(self.ENTRY_WIDTH, WIDGET_HEIGHT)
        self.gate_entry.set_size(self.ENTRY_WIDTH, WIDGET_HEIGHT)
        self.mask_entry.set_size(self.ENTRY_WIDTH, WIDGET_HEIGHT)
        self.master_entry.set_size(self.ENTRY_WIDTH, WIDGET_HEIGHT)
        self.slave_entry.set_size(self.ENTRY_WIDTH, WIDGET_HEIGHT)

        #self.auto_ip_align.set_size_request(self.ENTRY_WIDTH, 30)
        #self.auto_dns_align.set_size_request(self.ENTRY_WIDTH, 30)
        
        self.show_all()

        # Init Settings
        self.ip = ["","",""]
        self.dns = ["",""]
        self.reset(connection)
        self.addr_entry.entry.connect("changed", self.set_ip_address, 0)
        self.mask_entry.entry.connect("changed", self.set_ip_address, 1)
        self.gate_entry.entry.connect("changed", self.set_ip_address, 2)
        self.master_entry.entry.connect("changed", self.set_dns_address, 0)
        self.slave_entry.entry.connect("changed", self.set_dns_address, 1)
        
        #ip_switch.connect("toggled", self.manual_ip_entry)
        self.auto_ip.connect("toggled", self.get_ip_addr)
        self.auto_dns.connect("toggled", self.dns_set)

        if type(self.connection) is NMRemoteConnection:
            self.set_button("apply", True)
        else:
            self.set_button("save", True)

    def reset(self, connection):
        self.setting = connection.get_setting("ipv4")       

        if self.setting.method == "auto":
            self.auto_ip.set_active(True)
            #self.set_group_sensitive("ip", False)
            
        else:
            self.auto_ip.set_active(False)
            #self.set_group_sensitive("ip", True)
            if not self.setting.addresses == []:
                self.addr_entry.set_text(self.setting.addresses[0][0])
                self.mask_entry.set_text(self.setting.addresses[0][1])
                self.gate_entry.set_text(self.setting.addresses[0][2])
                self.ip = self.setting.addresses[0]

        if self.setting.dns == []:
            self.auto_dns.set_active(True)
            #self.set_group_sensitive("dns", False)
        else:
            self.auto_dns.set_active(False)
            #self.set_group_sensitive("dns", True)
            self.master_entry.set_text(self.setting.dns[0])
            self.dns = self.setting.dns + [""]
            if len(self.setting.dns) > 1:
                self.slave_entry.set_text(self.setting.dns[1])
                self.dns = self.setting.dns

        self.reset_table()

        #if self.dns_only:
            #self.set_group_sensitive("ip", False)
            #self.auto_ip.set_sensitive(False)
            #self.manual_ip.set_sensitive(False)

    def reset_table(self):
        container_remove_all(self.table)
        self.table.attach(self.ip_label_align, 0,1,0,1)
        self.table.attach(self.auto_ip_align, 1, 2, 0, 1)
        if not self.auto_ip.get_active():
            self.table.attach(self.addr_label_align, 0,1,2,3)
            self.table.attach(self.addr_entry_align, 1,2,2,3)
            self.table.attach(self.mask_label_align, 0,1,3,4)
            self.table.attach(self.mask_entry_align, 1,2,3,4)
            self.table.attach(self.gate_label_align, 0,1,4,5)
            self.table.attach(self.gate_entry_align, 1,2,4,5)
        
        hbox = gtk.HBox()
        hbox.set_size_request(-1, 20)
        self.table.attach(hbox, 0, 1, 5, 6) 
        self.table.attach(self.dns_label_align, 0, 1, 6, 7) 
        self.table.attach(self.auto_dns_align, 1, 2, 6, 7)
        if not self.auto_dns.get_active():
            self.table.attach(self.master_dns_align, 0, 1, 7, 8)
            self.table.attach(self.master_entry_align, 1, 2, 7, 8)
            self.table.attach(self.slave_dns_align, 0, 1, 8, 9)
            self.table.attach(self.slave_entry_align, 1, 2, 8, 9)

        #self.table.show_all()
        self.queue_draw()

    def set_group_sensitive(self, group_name, sensitive):
        if group_name is "ip":
            self.addr_label.set_sensitive(sensitive)
            self.mask_label.set_sensitive(sensitive)
            self.gate_label.set_sensitive(sensitive)
            self.addr_entry.set_sensitive(sensitive)
            self.mask_entry.set_sensitive(sensitive)
            self.gate_entry.set_sensitive(sensitive)
            if not sensitive:
                self.addr_entry.set_text("")
                self.mask_entry.set_text("")
                self.gate_entry.set_text("")
        elif group_name is "dns":
            self.master_dns.set_sensitive(sensitive)
            self.slave_dns.set_sensitive(sensitive)
            self.master_entry.set_sensitive(sensitive)
            self.slave_entry.set_sensitive(sensitive)
            if not sensitive:
                self.master_entry.set_text("")
                self.slave_entry.set_text("")

    def set_ip_address(self, widget, content, index):
        names = ["ip4", "netmask", "gw"]
        self.ip[index] = content
        if self.check_valid(names[index]):
            print "ip4 valid"
            setattr(self, names[index] + "_flag", True)
            #print "valid"+ names[index]
        else:
            print "ip4 invalid"
            setattr(self, names[index] + "_flag", False)

        if self.check_valid("gw"):
            if self.setting.addresses:
                self.setting.clear_addresses()
            self.setting.add_address(self.ip)

            if self.connection.check_setting_finish():
                self.set_button("save", True)
            else:
                self.set_button("save", False)
        else:
            self.setting.clear_addresses()

    def set_dns_address(self, widget, content, index):
        self.dns[index] = content
        names = ["master", "slaver"]

        dns = self.check_complete_dns()
        if dns:
            self.set_button("save", True)
            self.setting.clear_dns()
            for d in dns:
                self.setting.add_dns(d)
        else:
            self.setting.clear_dns()

        if TypeConvert.is_valid_ip4(content):
            setattr(self, names[index] + "_flag", True)
            print "valid"+ names[index]
        else:
            if content is not "":
                self.set_button("save", False)
            setattr(self, names[index] + "_flag", False)

    def check_complete_dns(self):
        dns = []
        for address in self.dns:
            if TypeConvert.is_valid_ip4(address):
                dns.append(address)
            else:
                return dns
        return dns

    def check_valid(self, name):
        if name == "ip4":
            return TypeConvert.is_valid_ip4(self.ip[0])
        elif name == "netmask":
            return TypeConvert.is_valid_netmask(self.ip[1])
        elif name == "gw":
            return TypeConvert.is_valid_gw(self.ip[0], self.ip[1], self.ip[2])

    def dns_set(self, widget):
        if widget.get_active():
            self.setting.clear_dns()
            self.dns = ["",""]
            self.set_group_sensitive("dns", False)
            if self.connection.check_setting_finish():
                self.set_button("save", True)
            else:
                self.set_button("save", False)
        else:
            self.set_group_sensitive("dns", True)
            self.set_button("save", False)
        self.reset_table()

    def get_ip_addr(self, widget):
        if widget.get_active():
            self.setting.clear_addresses()
            self.ip = ["","",""]
            self.setting.method = 'auto'
            self.set_group_sensitive("ip", False)
            if self.connection.check_setting_finish():
                print "settings complete"
                self.set_button("save", True)
            else:
                print "settings incomplete"
                self.set_button("save", False)
        else:
            self.setting.method = 'manual'
            self.set_group_sensitive("ip", True)
            if self.connection.check_setting_finish():
                self.set_button("save", True)
            else:
                self.set_button("save", False)
        self.reset_table()
        
    
class IPV6Conf(gtk.VBox):
    ENTRY_WIDTH = 300
    def __init__(self, connection=None, set_button_callback=None):
        
        gtk.VBox.__init__(self)
        self.connection = connection 
        self.tab_name = _("IPv6 Settings")
        self.set_button = set_button_callback
        self.table = gtk.Table(9, 2, False)
        # Ip configuration
        self.ip_label = Label(_("Automatic get IP address"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.auto_ip = OffButton()

        self.addr_label = Label(_("IP Address:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.addr_entry = InputEntry()
        self.addr_entry.set_sensitive(False)

        self.mask_label = Label(_("Prefix:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.mask_entry = InputEntry()
        
        self.gate_label = Label(_("Gateway:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.gate_entry = InputEntry()
        
        #DNS configuration
        self.dns_label = Label( _("Automatic get DNS server"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.auto_dns = OffButton()

        self.master_dns = Label(_("Primary DNS server address:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.slave_dns = Label(_("Slave DNS server address:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.master_entry = InputEntry()
        self.slave_entry = InputEntry()
        
        __widget_list = ["ip_label", "addr_label", "addr_entry",
                         "mask_label", "mask_entry", "gate_label", "gate_entry",
                         "dns_label", "master_entry", "slave_entry",
                         "slave_dns", "master_dns"]

        wrap_with_align(self, __widget_list)

        self.auto_ip_align = style.wrap_with_align(self.auto_ip, align="left")
        self.auto_dns_align = style.wrap_with_align(self.auto_dns, align="left")

        # TODO UI change
        style.draw_background_color(self)
        style.set_table(self.table)
        align = style.set_box_with_align(self.table, 'text')
        self.add(align)
        self.addr_entry.set_size(self.ENTRY_WIDTH, WIDGET_HEIGHT)
        self.gate_entry.set_size(self.ENTRY_WIDTH, WIDGET_HEIGHT)
        self.mask_entry.set_size(self.ENTRY_WIDTH, WIDGET_HEIGHT)
        self.master_entry.set_size(self.ENTRY_WIDTH, WIDGET_HEIGHT)
        self.slave_entry.set_size(self.ENTRY_WIDTH, WIDGET_HEIGHT)

        #self.auto_ip_align.set_size_request(self.ENTRY_WIDTH, 30)
        #self.auto_dns_align.set_size_request(self.ENTRY_WIDTH, 30)
        
        self.show_all()
        self.ip = ["", "", ""]
        self.dns = ["", ""]
        self.setting =None
        self.reset(connection)
        self.addr_entry.entry.connect("changed", self.set_ip_address, 0)
        self.mask_entry.entry.connect("changed", self.set_ip_address, 1)
        self.gate_entry.entry.connect("changed", self.set_ip_address, 2)
        self.master_entry.entry.connect("changed", self.set_dns_address, 0)
        self.slave_entry.entry.connect("changed", self.set_dns_address, 1)

        self.auto_ip.connect("toggled", self.get_ip_addr)
        self.auto_dns.connect("toggled", self.dns_set)

        if type(self.connection) is NMRemoteConnection:
            self.set_button("apply", True)
        else:
            self.set_button("save", True)

    def reset_table(self):
        container_remove_all(self.table)
        self.table.attach(self.ip_label_align, 0,1,0,1)
        self.table.attach(self.auto_ip_align, 1, 2, 0, 1)
        if not self.auto_ip.get_active():
            self.table.attach(self.addr_label_align, 0,1,2,3)
            self.table.attach(self.addr_entry_align, 1,2,2,3)
            self.table.attach(self.mask_label_align, 0,1,3,4)
            self.table.attach(self.mask_entry_align, 1,2,3,4)
            self.table.attach(self.gate_label_align, 0,1,4,5)
            self.table.attach(self.gate_entry_align, 1,2,4,5)
        
        hbox = gtk.HBox()
        hbox.set_size_request(-1, 20)
        self.table.attach(hbox, 0, 1, 5, 6) 
        self.table.attach(self.dns_label_align, 0, 1, 6, 7) 
        self.table.attach(self.auto_dns_align, 1, 2, 6, 7)
        if not self.auto_dns.get_active():
            self.table.attach(self.master_dns_align, 0, 1, 7, 8)
            self.table.attach(self.master_entry_align, 1, 2, 7, 8)
            self.table.attach(self.slave_dns_align, 0, 1, 8, 9)
            self.table.attach(self.slave_entry_align, 1, 2, 8, 9)

        #self.table.show_all()
        self.queue_draw()

    def reset(self, connection):
        self.setting = connection.get_setting("ipv6")       

        if self.setting.method == "auto":
            self.auto_ip.set_active(True)
            self.set_group_sensitive("ip", False)
            
        else:
            #self.manual_ip.set_active(True)
            self.set_group_sensitive("ip", True)
            if not self.setting.addresses == []:
                self.addr_entry.set_text(self.setting.addresses[0][0])
                self.mask_entry.set_text(self.setting.addresses[0][1])
                self.gate_entry.set_text(self.setting.addresses[0][2])
                self.ip = self.setting.addresses

        if self.setting.dns == []:
            self.auto_dns.set_active(True)
            self.set_group_sensitive("dns", False)
        else:
            #self.manual_dns.set_active(True)
            self.set_group_sensitive("dns", True)
            self.master_entry.set_text(self.setting.dns[0])
            self.dns = self.setting_dns +[""]
            if len(self.setting.dns) > 1:
                self.slave_entry.set_text(self.setting.dns[1])
                self.dns = self.setting.dns

        self.reset_table()

    def set_group_sensitive(self, group_name, sensitive):
        if group_name is "ip":
            self.addr_label.set_sensitive(sensitive)
            self.mask_label.set_sensitive(sensitive)
            self.gate_label.set_sensitive(sensitive)
            self.addr_entry.set_sensitive(sensitive)
            self.mask_entry.set_sensitive(sensitive)
            self.gate_entry.set_sensitive(sensitive)
            if not sensitive:
                self.addr_entry.set_text("")
                self.mask_entry.set_text("")
                self.gate_entry.set_text("")
        elif group_name is "dns":
            self.master_dns.set_sensitive(sensitive)
            self.slave_dns.set_sensitive(sensitive)
            self.master_entry.set_sensitive(sensitive)
            self.slave_entry.set_sensitive(sensitive)
            if not sensitive:
                self.master_entry.set_text("")
                self.slave_entry.set_text("")

    def set_ip_address(self, widget, content, index):
        names = ["ip6", "netmask", "gw"]
        self.ip[index] = content
        if self.check_valid(names[index]):
            print "is valid "+names[index]
            setattr(self, names[index] + "_flag", True)
            #print "valid"+ names[index]
        else:
            print "is invalid "+names[index]
            setattr(self, names[index] + "_flag", False)

        if self.check_valid("gw"):
            #print "update ip4"
            if self.setting.addresses:
                self.setting.clear_addresses()
            self.setting.add_address(self.ip)
        else:
            self.setting.clear_addresses()

    def set_dns_address(self, widget, content, index):
        self.dns[index] = content
        names = ["master", "slaver"]
        if TypeConvert.is_valid_ip6(content):
            setattr(self, names[index] + "_flag", True)
            print "valid"+ names[index]
        else:
            setattr(self, names[index] + "_flag", False)

        dns = self.check_complete_dns()
        if dns:
            self.setting.clear_dns()
            for d in dns:
                self.setting.add_dns(d)
        else:
            self.setting.clear_dns()
            
    def check_complete_dns(self):
        dns = []
        for address in self.dns:
            if TypeConvert.is_valid_ip6(address):
                dns.append(address)
            else:
                return dns
        return dns

    def check_valid(self, name):
        if name == "ip6":
            return TypeConvert.is_valid_ip6(self.ip[0])
        elif name == "netmask":
            return TypeConvert.is_valid_netmask(self.ip[1])
        elif name == "gw":
            return TypeConvert.is_valid_gw(self.ip[0], self.ip[1], self.ip[2])

    def dns_set(self, widget):
        if widget.get_active():
            self.setting.clear_dns()
            self.dns = ["",""]
            self.set_group_sensitive("dns", False)
            if self.connection.check_setting_finish():
                self.set_button("save", True)
            else:
                self.set_button("save", False)
        else:
            self.set_group_sensitive("dns", True)
            self.set_button("save", False)
        self.reset_table()

    def get_ip_addr(self, widget):
        if widget.get_active():
            self.setting.clear_addresses()
            self.ip = ["","",""]
            self.setting.method = 'auto'
            self.set_group_sensitive("ip", False)
            if self.connection.check_setting_finish():
                print "settings complete"
                self.set_button("save", True)
            else:
                print "settings incomplete"
                self.set_button("save", False)
        else:
            self.setting.method = 'manual'
            self.set_group_sensitive("ip", True)
            if self.connection.check_setting_finish():
                self.set_button("save", True)
            else:
                self.set_button("save", False)
        self.reset_table()
