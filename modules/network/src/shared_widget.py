#!/usr/bin/env python
#-*- coding:utf-8 -*-

from dtk.ui.label import Label
from dtk.ui.entry import InputEntry
from nmlib.nm_utils import TypeConvert
from nmlib.nm_remote_connection import NMRemoteConnection
import gtk

import style
from constants import CONTENT_FONT_SIZE, TITLE_FONT_SIZE, WIDGET_HEIGHT
from nls import _
from container import MyRadioButton as RadioButton


class IPV4Conf(gtk.VBox):
    def __init__(self, connection=None, set_button_callback=None, dns_only=False):
        
        gtk.VBox.__init__(self)
        self.connection = connection 
        self.set_button = set_button_callback
        self.dns_only = dns_only
        table = gtk.Table(9, 2, False)
        # Ip configuration
        self.auto_ip = RadioButton(None, _("Automatic get IP address"), padding_x=0, font_size=TITLE_FONT_SIZE)
        self.manual_ip = RadioButton(self.auto_ip, _("Manually get IP address"), padding_x=0, font_size=TITLE_FONT_SIZE)
        table.attach(style.wrap_with_align(self.auto_ip), 0,1,0,1)
        table.attach(style.wrap_with_align(self.manual_ip), 0,1,1,2)

        self.addr_label = Label(_("IP Address:"), text_size=CONTENT_FONT_SIZE)
        table.attach(style.wrap_with_align(self.addr_label), 0,1,2,3)
        self.addr_entry = InputEntry()
        self.addr_entry.set_sensitive(False)
        table.attach(style.wrap_with_align(self.addr_entry), 1,2,2,3)

        self.mask_label = Label(_("Mask:"), text_size=CONTENT_FONT_SIZE)
        table.attach(style.wrap_with_align(self.mask_label), 0,1,3,4)
        self.mask_entry = InputEntry()
        table.attach(style.wrap_with_align(self.mask_entry), 1,2,3,4)
        
        self.gate_label = Label(_("Gateway:"), text_size=CONTENT_FONT_SIZE)
        table.attach(style.wrap_with_align(self.gate_label), 0,1,4,5)
        self.gate_entry = InputEntry()
        table.attach(style.wrap_with_align(self.gate_entry), 1,2,4,5)
        
        #DNS configuration
        self.auto_dns = RadioButton(None, _("Automatic get DNS server"), padding_x=0, font_size=TITLE_FONT_SIZE)
        self.manual_dns = RadioButton(self.auto_dns,_("Use following DNS server"), padding_x=0, font_size=TITLE_FONT_SIZE)
        table.attach(style.wrap_with_align(self.auto_dns), 0, 1, 5, 6) 
        table.attach(style.wrap_with_align(self.manual_dns), 0, 1, 6, 7)

        self.master_dns = Label(_("Primary DNS server address:"), text_size=CONTENT_FONT_SIZE)
        self.slave_dns = Label(_("Slave DNS server address:"), text_size=CONTENT_FONT_SIZE)
        self.master_entry = InputEntry()
        self.slave_entry = InputEntry()
        
        table.attach(style.wrap_with_align(self.master_dns), 0, 1, 7, 8)
        table.attach(style.wrap_with_align(self.master_entry), 1, 2, 7, 8)
        table.attach(style.wrap_with_align(self.slave_dns), 0, 1, 8, 9)
        table.attach(style.wrap_with_align(self.slave_entry), 1, 2, 8, 9)

        # TODO UI change
        #table.set_size_request(340, 227)
        style.set_table(table)
        align = style.set_box_with_align(table, 'text')
        self.add(align)
        
        #style.set_table_items(table, "entry")
        self.addr_entry.set_size(222, WIDGET_HEIGHT)
        self.gate_entry.set_size(222, WIDGET_HEIGHT)
        self.mask_entry.set_size(222, WIDGET_HEIGHT)
        self.master_entry.set_size(222, WIDGET_HEIGHT)
        self.slave_entry.set_size(222, WIDGET_HEIGHT)
        
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
        
        self.manual_ip.connect("toggled", self.manual_ip_entry)
        self.auto_ip.connect("toggled", self.auto_get_ip_addr)
        self.auto_dns.connect("toggled", self.auto_dns_set)
        self.manual_dns.connect("toggled", self.manual_dns_set)

        if type(self.connection) is NMRemoteConnection:
            self.set_button("apply", True)
        else:
            self.set_button("save", True)

    def reset(self, connection):
        self.setting = connection.get_setting("ipv4")       

        if self.setting.method == "auto":
            self.auto_ip.set_active(True)
            self.set_group_sensitive("ip", False)
            
        else:
            self.manual_ip.set_active(True)
            self.set_group_sensitive("ip", True)
            if not self.setting.addresses == []:
                self.addr_entry.set_text(self.setting.addresses[0][0])
                self.mask_entry.set_text(self.setting.addresses[0][1])
                self.gate_entry.set_text(self.setting.addresses[0][2])
                self.ip = self.setting.addresses[0]

        if self.setting.dns == []:
            self.auto_dns.set_active(True)
            self.set_group_sensitive("dns", False)
        else:
            self.manual_dns.set_active(True)
            self.set_group_sensitive("dns", True)
            self.master_entry.set_text(self.setting.dns[0])
            self.dns = self.setting.dns + [""]
            if len(self.setting.dns) > 1:
                self.slave_entry.set_text(self.setting.dns[1])
                self.dns = self.setting.dns

        if self.dns_only:
            self.set_group_sensitive("ip", False)
            self.auto_ip.set_sensitive(False)
            self.manual_ip.set_sensitive(False)

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
            setattr(self, names[index] + "_flag", True)
            #print "valid"+ names[index]
        else:
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

    def auto_dns_set(self, widget):
        if widget.get_active():
            self.setting.clear_dns()
            self.dns = ["",""]
            self.set_group_sensitive("dns", False)
            if self.connection.check_setting_finish():
                self.set_button("save", True)
            else:
                self.set_button("save", False)

    def manual_dns_set(self, widget):
        if widget.get_active():
            self.set_group_sensitive("dns", True)
            self.set_button("save", False)

    def auto_get_ip_addr(self, widget):
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

    def manual_ip_entry(self,widget):
        if widget.get_active():
            self.setting.method = 'manual'
            self.set_group_sensitive("ip", True)
            if self.connection.check_setting_finish():
                self.set_button("save", True)
            else:
                self.set_button("save", False)
    
class IPV6Conf(gtk.VBox):

    def __init__(self, connection=None, set_button_callback=None):
        
        gtk.VBox.__init__(self)
        self.connection = connection 
        self.set_button = set_button_callback
        table = gtk.Table(9, 2, False)
        # Ip configuration
        self.auto_ip = RadioButton(None, "自动获得IP地址", padding_x=0, font_size = TITLE_FONT_SIZE)
        self.manual_ip = RadioButton(self.auto_ip, "手动添加IP地址", padding_x=0, font_size=TITLE_FONT_SIZE)
        table.attach(style.wrap_with_align(self.auto_ip), 0,1,0,1)
        table.attach(style.wrap_with_align(self.manual_ip), 0,1,1,2)

        self.addr_label = Label("IP地址:", text_size=CONTENT_FONT_SIZE)
        table.attach(style.wrap_with_align(self.addr_label), 0,1,2,3)
        self.addr_entry = InputEntry()
        self.addr_entry.set_sensitive(False)
        table.attach(style.wrap_with_align(self.addr_entry), 1,2,2,3)

        self.mask_label = Label("前缀:", text_size=CONTENT_FONT_SIZE)
        table.attach(style.wrap_with_align(self.mask_label), 0,1,3,4)
        self.mask_entry = InputEntry()
        table.attach(style.wrap_with_align(self.mask_entry), 1,2,3,4)
        
        self.gate_label = Label("默认网关", text_size=CONTENT_FONT_SIZE)
        table.attach(style.wrap_with_align(self.gate_label), 0,1,4,5)
        self.gate_entry = InputEntry()
        table.attach(style.wrap_with_align(self.gate_entry), 1,2,4,5)
        
        #DNS configuration
        self.auto_dns = RadioButton(None, "  自动获得DNS服务器地址", padding_x=0, font_size=TITLE_FONT_SIZE)
        self.manual_dns = RadioButton(self.auto_dns,"  使用下面的dns服务器", padding_x=0, font_size=TITLE_FONT_SIZE)
        table.attach(style.wrap_with_align(self.auto_dns), 0, 1, 5, 6) 
        table.attach(style.wrap_with_align(self.manual_dns), 0, 1, 6, 7)

        self.master_dns = Label("首选DNS服务器地址:", text_size=CONTENT_FONT_SIZE)
        self.slave_dns = Label("使用下面的DNS服务器地址:", text_size=CONTENT_FONT_SIZE)
        self.master_entry = InputEntry()
        self.slave_entry = InputEntry()
        
        table.attach(style.wrap_with_align(self.master_dns), 0, 1, 7, 8)
        table.attach(style.wrap_with_align(self.master_entry), 1, 2, 7, 8)
        table.attach(style.wrap_with_align(self.slave_dns), 0, 1, 8, 9)
        table.attach(style.wrap_with_align(self.slave_entry), 1, 2, 8, 9)

        # TODO UI change 
        #table.set_size_request(340, 227)

        style.set_table(table)
        align = style.set_box_with_align(table, 'text')
        self.add(align)
        
        self.addr_entry.set_size(222, 22)
        self.gate_entry.set_size(222, 22)
        self.mask_entry.set_size(222, 22)
        self.master_entry.set_size(222, 22)
        self.slave_entry.set_size(222, 22)
        
        self.ip = ["", "", ""]
        self.dns = ["", ""]
        self.setting =None
        self.reset(connection)
        self.addr_entry.entry.connect("changed", self.set_ip_address, 0)
        self.mask_entry.entry.connect("changed", self.set_ip_address, 1)
        self.gate_entry.entry.connect("changed", self.set_ip_address, 2)
        self.master_entry.entry.connect("changed", self.set_dns_address, 0)
        self.slave_entry.entry.connect("changed", self.set_dns_address, 1)

        self.manual_ip.connect("toggled", self.manual_ip_entry)
        self.auto_ip.connect("toggled", self.auto_get_ip_addr)
        self.auto_dns.connect("toggled", self.auto_dns_set)
        self.manual_dns.connect("toggled", self.manual_dns_set)

    def reset(self, connection):
        self.setting = connection.get_setting("ipv6")       

        if self.setting.method == "auto":
            self.auto_ip.set_active(True)
            self.set_group_sensitive("ip", False)
            
        else:
            self.manual_ip.set_active(True)
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
            self.manual_dns.set_active(True)
            self.set_group_sensitive("dns", True)
            self.master_entry.set_text(self.setting.dns[0])
            self.dns = self.setting_dns +[""]
            if len(self.setting.dns) > 1:
                self.slave_entry.set_text(self.setting.dns[1])
                self.dns = self.setting.dns

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
            setattr(self, names[index] + "_flag", True)
            #print "valid"+ names[index]
        else:
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

    def auto_dns_set(self, widget):
        if widget.get_active():
            self.setting.clear_dns()
            self.dns = ["",""]
            self.set_group_sensitive("dns", False)

    def manual_dns_set(self, widget):
        if widget.get_active():
            self.set_group_sensitive("dns", True)

    def auto_get_ip_addr(self, widget):
        if widget.get_active():
            self.setting.clear_addresses()
            self.ip = ["","",""]
            self.setting.method = 'auto'
            self.set_group_sensitive("ip", False)

    def manual_ip_entry(self,widget):
        if widget.get_active():
            self.setting.method = 'manual'
            self.set_group_sensitive("ip", True)
