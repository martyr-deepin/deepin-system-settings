#!/usr/bin/env python
#-*- coding:utf-8 -*-

from dtk.ui.label import Label
from dtk.ui.new_entry import InputEntry
from nmlib.nm_utils import TypeConvert
from dtk.ui.button import OffButton
from nmlib.nm_remote_connection import NMRemoteConnection
from dtk.ui.utils import container_remove_all
import gtk

import style
from constants import CONTENT_FONT_SIZE, TITLE_FONT_SIZE, WIDGET_HEIGHT
from nls import _
from container import MyRadioButton as RadioButton
from helper import Dispatcher
from elements import SettingSection

class IPV4Conf(gtk.VBox):
    ENTRY_WIDTH = 222
    def __init__(self, connection=None, set_button_callback=None, dns_only=False):
        
        gtk.VBox.__init__(self)
        self.tab_name = _("IPv4 Setting")
        self.connection = connection 
        self.set_button = set_button_callback
        self.dns_only = dns_only

        # Ip configuration
        #self.ip_main_section = SettingSection(_("Ipv4 setting"), text_size=TITLE_FONT_SIZE, always_show=True, has_seperator=False )


        self.ip_table = gtk.Table(3, 2, False)
        self.ip_section = SettingSection(_("Automatic get IP address"),text_size=CONTENT_FONT_SIZE, has_seperator=False, always_show=False, revert=True, label_right=True)
        self.ip_section.toggle_on = self.ip_toggle_off
        self.ip_section.toggle_off = self.ip_toggle_on

        self.addr_row = self.__set_row(_("IP Address:"), 0)
        self.mask_row = self.__set_row(_("Mask:"), 1)
        self.gate_row = self.__set_row(_("Gateway:"), 2)

        self.__table_attach(self.ip_table, self.addr_row, 0)
        self.__table_attach(self.ip_table, self.mask_row, 1)
        self.__table_attach(self.ip_table, self.gate_row, 2)
        self.ip_section.load([self.ip_table])
        
        #DNS configuration
        self.dns_table = gtk.Table(2, 2, False)
        self.dns_section = SettingSection( _("Automatic get DNS server"), text_size=CONTENT_FONT_SIZE,has_seperator=False, always_show=False, revert=True, label_right=True)
        self.dns_section.toggle_on = self.dns_toggle_off
        self.dns_section.toggle_off = self.dns_toggle_on

        self.master_row = self.__set_row(_("Primary DNS server address:"), 0)
        self.slave_row = self.__set_row(_("Slave DNS server address:"), 1)

        self.__table_attach(self.dns_table, self.master_row, 0)
        self.__table_attach(self.dns_table, self.slave_row, 1)
        self.dns_section.load([self.dns_table])
        
        # TODO UI change
        style.draw_background_color(self)
        style.set_table(self.ip_table)
        style.set_table(self.dns_table)


        # Init Settings
        self.ip = ["","",""]
        self.dns = ["",""]
        #self.pack_start(self.ip_main_section, False, False)
        #self.ip_main_section.load([self.ip_section, self.dns_section])
        self.pack_start(self.ip_section, False, False)
        self.pack_start(self.dns_section, False, False)
        self.reset(connection)
        #ip_switch.connect("toggled", self.manual_ip_entry)
        self.show_all()

        if type(self.connection) is NMRemoteConnection:
            Dispatcher.set_button("apply", True)
        else:
            if self.connection.check_setting_finish():
                print "in ipv"
                Dispatcher.set_button("save", True)
            else:
                print "in ipv"
                Dispatcher.set_button("save", False)

    def __set_row(self, name, arg):
        label = Label(name, text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        entry = InputEntry()
        entry.entry.connect("changed", self.set_ip_address, arg)
        entry.set_size(self.ENTRY_WIDTH, WIDGET_HEIGHT)

        return (label, entry)

    def __table_attach(self, table, row_item, row):
        for i, item in enumerate(row_item):
            if i >=1:
                align = style.wrap_with_align(item, align="left")
            else:
                align = style.wrap_with_align(item)
                align.set_size_request(210, -1)
            table.attach(align, i, i +1, row, row + 1)

    def reset(self, connection):
        self.setting = connection.get_setting("ipv4")       

        if self.setting.method == "auto":
            self.ip_section.set_active(True)
            #self.set_group_sensitive("ip", False)
            
        else:
            self.ip_section.set_active(False)
            #self.set_group_sensitive("ip", True)
            if not self.setting.addresses == []:
                self.addr_row[1].set_text(self.setting.addresses[0][0])
                self.mask_row[1].set_text(self.setting.addresses[0][1])
                self.gate_row[1].set_text(self.setting.addresses[0][2])
                self.ip = self.setting.addresses[0]

        if self.setting.dns == []:
            self.dns_section.set_active(True)
        else:
            self.dns_section.set_active(False)
            self.master_row[1].set_text(self.setting.dns[0])

            self.dns = self.setting.dns + [""]
            if len(self.setting.dns) > 1:
                self.slave_row[1].set_text(self.setting.dns[1])
                self.dns = self.setting.dns

        self.reset_table()
        #if self.dns_only:
            #self.set_group_sensitive("ip", False)
            #self.auto_ip.set_sensitive(False)
            #self.manual_ip.set_sensitive(False)

    def reset_table(self):
        pass
        #container_remove_all(self.table)
        #if not self.auto_ip.get_active():
            #self.table.attach(self.addr_label_align, 0,1,2,3)
            #self.table.attach(self.addr_entry_align, 1,2,2,3)
            #self.table.attach(self.mask_label_align, 0,1,3,4)
            #self.table.attach(self.mask_entry_align, 1,2,3,4)
            #self.table.attach(self.gate_label_align, 0,1,4,5)
            #self.table.attach(self.gate_entry_align, 1,2,4,5)
        
        #hbox = gtk.HBox()
        #hbox.set_size_request(-1, 20)
        #self.table.attach(hbox, 0, 1, 5, 6) 
        #self.table.attach(self.dns_label_align, 0, 1, 6, 7) 
        #self.table.attach(self.auto_dns_align, 1, 2, 6, 7)
        #if not self.auto_dns.get_active():
            #self.table.attach(self.master_dns_align, 0, 1, 7, 8)
            #self.table.attach(self.master_entry_align, 1, 2, 7, 8)
            #self.table.attach(self.slave_dns_align, 0, 1, 8, 9)
            #self.table.attach(self.slave_entry_align, 1, 2, 8, 9)

        #self.table.show_all()
        self.queue_draw()

    def set_group_sensitive(self, group_name, sensitive):
        pass
                #self.addr_entry.set_text("")
                #self.mask_entry.set_text("")
                ##self.gate_entry.set_text("")
                #self.master_entry.set_text("")
                #self.slave_entry.set_text("")

    def set_ip_address(self, widget, content, index):
        names = ["ip4", "netmask", "gw"]
        self.ip[index] = content
        if self.check_valid(names[index]):
            print "ip4 valid"
            setattr(self, names[index] + "_flag", True)
        else:
            Dispatcher.set_tip("ipv4 invalid")
            setattr(self, names[index] + "_flag", False)

        if self.check_valid("gw"):
            if self.setting.addresses:
                self.setting.clear_addresses()
            self.setting.add_address(self.ip)

            if self.connection.check_setting_finish():
                print "sfsdf"
                Dispatcher.set_button("save", True)
            else:
                print "xxxxxxxxxx"
                Dispatcher.set_button("save", False)
        else:
            self.setting.clear_addresses()

    def set_dns_address(self, widget, content, index):
        self.dns[index] = content
        names = ["master", "slaver"]

        dns = self.check_complete_dns()
        if dns:
            Dispatcher.set_button("save", True)
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
                Dispatcher.set_button("save", False)
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
    
    def dns_toggle_on(self):
        self.setting.clear_dns()
        self.dns = ["",""]
        self.set_group_sensitive("dns", False)
        if self.connection.check_setting_finish():
            Dispatcher.set_button("save", True)
        else:
            Dispatcher.set_button("save", False)

    def dns_toggle_off(self):
        self.set_group_sensitive("dns", True)
        Dispatcher.set_button("save", False)
        
    def ip_toggle_on(self):
        self.setting.clear_addresses()
        self.ip = ["","",""]
        self.setting.method = 'auto'
        self.set_group_sensitive("ip", False)
        if self.connection.check_setting_finish():
            print "settings complete"
            Dispatcher.set_button("save", True)
        else:
            print "settings incomplete"
            Dispatcher.set_button("save", False)

    def ip_toggle_off(self):
        print "manual"
        self.addr_row[1].set_text("")
        self.mask_row[1].set_text("")
        self.gate_row[1].set_text("")
        self.setting.method = 'manual'
        #self.set_group_sensitive("ip", True)
        if self.connection.check_setting_finish():
            Dispatcher.set_button("save", True)
        else:
            Dispatcher.set_button("save", False)

    def get_ip_addr(self, widget):
        if widget.get_active():
            self.setting.clear_addresses()
            self.ip = ["","",""]
            self.setting.method = 'auto'
            self.set_group_sensitive("ip", False)
            if self.connection.check_setting_finish():
                print "settings complete"
                Dispatcher.set_button("save", True)
            else:
                print "settings incomplete"
                Dispatcher.set_button("save", False)
        else:
            self.setting.method = 'manual'
            self.set_group_sensitive("ip", True)
            if self.connection.check_setting_finish():
                Dispatcher.set_button("save", True)
            else:
                Dispatcher.set_button("save", False)
        self.reset_table()

class IPV6Conf(gtk.VBox):
    ENTRY_WIDTH = 300
    def __init__(self, connection=None, set_button_callback=None):
        
        gtk.VBox.__init__(self)
        self.connection = connection 
        self.tab_name = _("IPv6 Settings")
        self.set_button = set_button_callback
        # Ip configuration
        self.ip_table = gtk.Table(3, 2, False)
        self.ip_section = SettingSection(_("Automatic get IP address"),text_size=CONTENT_FONT_SIZE, has_seperator=False, always_show=False, revert=True, label_right=True)
        self.ip_section.toggle_on = self.ip_toggle_off
        self.ip_section.toggle_off = self.ip_toggle_on

        self.addr_row = self.__set_row(_("IP Address:"), 0)
        self.mask_row = self.__set_row(_("Prefix:"), 1)
        self.gate_row = self.__set_row(_("Gateway:"), 2)
        
        self.__table_attach(self.ip_table, self.addr_row, 0)
        self.__table_attach(self.ip_table, self.mask_row, 1)
        self.__table_attach(self.ip_table, self.gate_row, 2)
        self.ip_section.load([self.ip_table])

        #DNS configuration
        self.dns_table = gtk.Table(2, 2, False)
        self.dns_section = SettingSection( _("Automatic get DNS server"), text_size=CONTENT_FONT_SIZE,has_seperator=False, always_show=False, revert=True, label_right=True)
        self.dns_section.toggle_on = self.dns_toggle_off
        self.dns_section.toggle_off = self.dns_toggle_on

        self.master_row = self.__set_row(_("Primary DNS server address:"), 0)
        self.slave_row = self.__set_row(_("Slave DNS server address:"), 1)

        self.__table_attach(self.dns_table, self.master_row, 0)
        self.__table_attach(self.dns_table, self.slave_row, 1)
        self.dns_section.load([self.dns_table])
        
        __widget_list = ["ip_label", "addr_label", "addr_entry",
                         "mask_label", "mask_entry", "gate_label", "gate_entry",
                         "dns_label", "master_entry", "slave_entry",
                         "slave_dns", "master_dns"]



        # TODO UI change
        style.draw_background_color(self)
        style.set_table(self.ip_table)
        style.set_table(self.dns_table)

        self.show_all()

        self.ip = ["", "", ""]
        self.dns = ["", ""]
        self.setting =None
        self.pack_start(self.ip_section, False, False)
        self.pack_start(self.dns_section, False, False)
        self.reset(connection)

        if type(self.connection) is NMRemoteConnection:
            Dispatcher.set_button("apply", True)
        else:
            if self.connection.check_setting_finish():
                Dispatcher.set_button("save", True)
            else:
                Dispatcher.set_button("save", False)

    def __set_row(self, name, arg):
        label = Label(name, text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        entry = InputEntry()
        entry.entry.connect("changed", self.set_ip_address, arg)
        entry.set_size(self.ENTRY_WIDTH, WIDGET_HEIGHT)

        return (label, entry)

    def __table_attach(self, table, row_item, row):
        for i, item in enumerate(row_item):
            if i >=1:
                align = style.wrap_with_align(item, align="left")
            else:
                align = style.wrap_with_align(item)
                align.set_size_request(210, -1)
            table.attach(align, i, i +1, row, row + 1)

    def reset_table(self):
        pass
        #container_remove_all(self.table)
        #self.table.attach(self.ip_label_align, 0,1,0,1)
        #self.table.attach(self.auto_ip_align, 1, 2, 0, 1)
        #if not self.auto_ip.get_active():
            #self.table.attach(self.addr_label_align, 0,1,2,3)
            #self.table.attach(self.addr_entry_align, 1,2,2,3)
            #self.table.attach(self.mask_label_align, 0,1,3,4)
            #self.table.attach(self.mask_entry_align, 1,2,3,4)
            #self.table.attach(self.gate_label_align, 0,1,4,5)
            #self.table.attach(self.gate_entry_align, 1,2,4,5)
        
        #hbox = gtk.HBox()
        #hbox.set_size_request(-1, 20)
        #self.table.attach(hbox, 0, 1, 5, 6) 
        #self.table.attach(self.dns_label_align, 0, 1, 6, 7) 
        #self.table.attach(self.auto_dns_align, 1, 2, 6, 7)
        #if not self.auto_dns.get_active():
            #self.table.attach(self.master_dns_align, 0, 1, 7, 8)
            #self.table.attach(self.master_entry_align, 1, 2, 7, 8)
            #self.table.attach(self.slave_dns_align, 0, 1, 8, 9)
            #self.table.attach(self.slave_entry_align, 1, 2, 8, 9)

        ##self.table.show_all()
        #self.queue_draw()

    def reset(self, connection):
        self.setting = connection.get_setting("ipv6")       
        
        print self.setting.method
        if self.setting.method == "auto":
            self.ip_section.set_active(True)
            self.set_group_sensitive("ip", False)
            
        else:
            self.manual_ip.set_active(False)
            self.set_group_sensitive("ip", True)
            if not self.setting.addresses == []:
                self.addr_row[1].set_text(self.setting.addresses[0][0])
                self.mask_row[1].set_text(self.setting.addresses[0][1])
                self.gate_row[1].set_text(self.setting.addresses[0][2])
                self.ip = self.setting.addresses

        if self.setting.dns == []:
            self.dns_section.set_active(True)
            self.set_group_sensitive("dns", False)
        else:
            #self.manual_dns.set_active(True)
            self.set_group_sensitive("dns", True)
            self.master_row[1].set_text(self.setting.dns[0])
            self.dns = self.setting_dns +[""]
            if len(self.setting.dns) > 1:
                self.slave_row[1].set_text(self.setting.dns[1])
                self.dns = self.setting.dns

        self.reset_table()

    def set_group_sensitive(self, group_name, sensitive):
        pass
        #if group_name is "ip":
            #self.addr_label.set_sensitive(sensitive)
            #self.mask_label.set_sensitive(sensitive)
            #self.gate_label.set_sensitive(sensitive)
            #self.addr_entry.set_sensitive(sensitive)
            #self.mask_entry.set_sensitive(sensitive)
            #self.gate_entry.set_sensitive(sensitive)
            #if not sensitive:
                #self.addr_entry.set_text("")
                #self.mask_entry.set_text("")
                #self.gate_entry.set_text("")
        #elif group_name is "dns":
            #self.master_dns.set_sensitive(sensitive)
            #self.slave_dns.set_sensitive(sensitive)
            #self.master_entry.set_sensitive(sensitive)
            #self.slave_entry.set_sensitive(sensitive)
            #if not sensitive:
                #self.master_entry.set_text("")
                #self.slave_entry.set_text("")

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


    def dns_toggle_on(self):
        self.setting.clear_dns()
        self.dns = ["",""]
        self.set_group_sensitive("dns", False)
        if self.connection.check_setting_finish():
            Dispatcher.set_button("save", True)
        else:
            Dispatcher.set_button("save", False)

    def dns_toggle_off(self):
        self.set_group_sensitive("dns", True)
        Dispatcher.set_button("save", False)

    
    def ip_toggle_on(self):
        self.setting.clear_addresses()
        self.ip = ["","",""]
        self.setting.method = 'auto'
        self.set_group_sensitive("ip", False)
        if self.connection.check_setting_finish():
            print "settings complete"
            Dispatcher.set_button("save", True)
        else:
            print "settings incomplete"
            Dispatcher.set_button("save", False)

    def ip_toggle_off(self):
        self.setting.method = 'manual'
        self.set_group_sensitive("ip", True)
        if self.connection.check_setting_finish():
            Dispatcher.set_button("save", True)
        else:
            Dispatcher.set_button("save", False)

