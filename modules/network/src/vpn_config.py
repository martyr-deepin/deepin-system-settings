#!/usr/bin/env python
#-*- coding:utf-8 -*-

from theme import app_theme

from dtk.ui.tab_window import TabBox
from dtk.ui.button import Button,ToggleButton, RadioButton, CheckButton
from dtk.ui.new_entry import InputEntry, PasswordEntry
from dtk.ui.label import Label
from dtk.ui.spin import SpinBox
from dtk.ui.utils import container_remove_all
#from dtk.ui.droplist import Droplist
from dtk.ui.combo import ComboBox
#from widgets import SettingButton
from settings_widget import SettingItem, EntryTreeView
# NM lib import 
from nmlib.nm_utils import TypeConvert
from nm_modules import nm_module, slider
from nmlib.nmcache import cache
from nmlib.nm_vpn_plugin import NMVpnL2tpPlugin, NMVpnPptpPlugin
#from nmlib.nmclient import nmclient
#from nmlib.nm_remote_settings import nm_remote_settings
from container import Contain

import gtk
#l2tp_plugin = NMVpnL2tpPlugin
#pptp_plugin = NMVpnPptpPlugin
class VPNSetting(gtk.HBox):

    def __init__(self, slide_back_cb = None, change_crumb_cb = None, module_frame = None):

        gtk.HBox.__init__(self)
        self.slide_back = slide_back_cb
        self.change_crumb = change_crumb_cb
        self.module_frame = module_frame
        
        self.pptp = None
        self.ipv4 = None

        self.tab_window = TabBox()
        self.items = [("PPTP", NoSetting()),
                      ("IPv4 Setting", NoSetting())]
        self.tab_window.add_items(self.items)
        self.sidebar = SideBar( None, self.init, self.check_click)

        # Build ui
        self.pack_start(self.sidebar, False , False)
        vbox = gtk.VBox()
        vbox.connect("expose-event", self.expose_event)
        vbox.pack_start(self.tab_window ,True, True)
        self.pack_start(vbox, True, True)
        #hbox = gtk.HBox()
        apply_button = Button("Apply")
        apply_button.connect("clicked", self.save_changes)
        #hbox.pack_start(apply_button, False, False, 0)
        buttons_aligns = gtk.Alignment(0.5 , 1, 0, 0)
        buttons_aligns.add(apply_button)
        vbox.pack_start(buttons_aligns, False , False)
        #hbox.connect("expose-event", self.expose_event)

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb( 1, 1, 1) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

    def init(self):
        # Get all connections  
        connections = nm_module.nm_remote_settings.get_vpn_connections()
        # Check connections
        if connections == []:
            # Create a new connection
            nm_module.nm_remote_settings.new_vpn_pptp_connection()
            connections = nm_module.nm_remote_settings.get_vpn_connections()

        self.ipv4_setting = [IPV4Conf(con) for con in connections]
        self.pptp_setting = [PPTPConf(con, self.module_frame) for con in connections]

        self.sidebar.init(connections, self.ipv4_setting)
        index = self.sidebar.get_active()
        self.ipv4 = self.ipv4_setting[index]
        self.pptp = self.pptp_setting[index]
        #self.dsl = NoSetting()
        #self.ppp = NoSetting()

        self.init_tab_box()

    def init_tab_box(self):
        self.tab_window.tab_items[1] = ("IPV4 setting",self.ipv4)
        self.tab_window.tab_items[0] = ("PPTP", self.pptp)
        tab_index = self.tab_window.tab_index
        self.tab_window.tab_index = -1
        self.tab_window.switch_content(tab_index)
        self.queue_draw()

    def check_click(self, connection):
        index = self.sidebar.get_active()
        self.ipv4 = self.ipv4_setting[index]
        self.pptp = self.pptp_setting[index]

        self.init_tab_box()
        
    def save_changes(self, widget):
        print "saving"

        connection = self.ipv4.connection
        print connection.object_path
        connection.update()
        
        # FIXME Now just support one device

        #active_connections = nm_module.nmclient.get_active_connections()
        #if active_connections:
            #device_path = active_connections[0].get_devices()[0].object_path
            #specific_path = active_connections[0].object_path
            #active_object = nm_module.nmclient.activate_connection(connection.object_path,
                                           #device_path,
                                           #specific_path)
            #print active_object
            #active_object.connect("vpn-state-changed", self.vpn_state_changed)
        #else:
            #print "no active connection available"


        wired_devices = nm_module.nmclient.get_wired_devices()
        wireless_devices = nm_module.nmclient.get_wireless_devices() 
        if wired_devices:
            try:
                self.try_to_connect_wired_device(wired_devices[0], connection)
            except Exception:
                if wireless_devices:
                    self.try_to_connect_wireless_device(wireless_devices[0], connection)

    def vpn_state_changed(self, widget, state, reason):
        print "changed",state

    def vpn_connected(self, widget):
        print "vpn connected"
        self.sidebar.set_active()

    def vpn_connecting(self, widget):
        print "vpn connecting"

    def vpn_disconnected(self, widget):
        print "vpn disconnected"
        cache.del_spec_object(widget.object_path)
        #self.sidebar.clear_active()


    def try_to_connect_wired_device(self, device, connection):
        active = device.get_active_connection()
        if active:
            device_path = device.object_path
            specific_path = active.get_specific_object()
            active_object = nm_module.nmclient.activate_connection(connection.object_path,
                                               device_path,
                                               specific_path)
            if active_object != None:
                active_vpn = cache.get_spec_object(active_object.object_path)
                active_vpn.connect("vpn-connected", self.vpn_connected)
                active_vpn.connect("vpn-connecting", self.vpn_connecting)
                active_vpn.connect("vpn-disconnected", self.vpn_disconnected)
            else:
                raise Exception
        else:
            raise Exception
    def try_to_connect_wireless_device(self, device, connection):
        active = device.get_active_connection()
        if active:
            print active
            device_path = device.object_path
            specific_path = active.object_path
            active_object = nm_module.nmclient.activate_connection(connection.object_path,
                                               device_path,
                                               specific_path)
            if active_object != None:
                active_vpn = cache.get_spec_object(active_object.object_path)
                active_vpn.connect("vpn-connected", self.vpn_connected)
                active_vpn.connect("vpn-connecting", self.vpn_connecting)
                active_vpn.connect("vpn-disconnected", self.vpn_disconnected)


class SideBar(gtk.VBox):
    def __init__(self, connections , main_init_cb, check_click_cb):
        gtk.VBox.__init__(self, False, 5)
        self.connections = connections
        self.main_init_cb = main_init_cb
        self.check_click_cb = check_click_cb

        # Build ui
        self.buttonbox = gtk.VBox(False, 6)
        self.pack_start(self.buttonbox, False, False)
        add_button = Button("Add setting")
        add_button.connect("clicked", self.add_new_connection)
        self.pack_start(add_button, False, False, 6)
        self.set_size_request(160, -1)
    
    def init(self, connection_list, ip4setting):
        # check active
        active_connection = nm_module.nmclient.get_vpn_active_connection()
        #print ">>>>>>", active_connection
        #active_connection = None
        if active_connection:
            active = active_connection[0].get_connection()
        else:
            active = None

        self.connections = connection_list
        self.setting = ip4setting
        
        # Add connection buttons
        container_remove_all(self.buttonbox)
        cons = []
        self.connection_tree = EntryTreeView(cons)
        for index, connection in enumerate(self.connections):
            cons.append(SettingItem(connection, self.setting[index], self.check_click_cb, self.delete_item_cb))
        self.connection_tree.add_items(cons)

        self.connection_tree.show_all()

        self.buttonbox.pack_start(self.connection_tree, False, False, 6)

        try:
            index = self.connections.index(active)
            this_connection = self.connection_tree.visible_items[index]
            this_connection.set_active(True)
            self.connection_tree.select_items([this_connection])
        except ValueError:
            self.connection_tree.select_first_item()

    def delete_item_cb(self):
        self.connection_tree.delete_select_items()
        self.connection_tree.set_size_request(-1,len(self.connection_tree.visible_items) * self.connection_tree.visible_items[0].get_height())

    def get_active(self):
        return self.connection_tree.select_rows[0]

    def set_active(self):
        index = self.get_active()
        this_connection = self.connection_tree.visible_items[index]
        this_connection.set_active(True)

    def clear_active(self):
        items = self.connection_tree.visible_items
        for item in items:
            item.set_active(False)
    
    def add_new_connection(self, widget):
        new_connection = nm_module.nm_remote_settings.new_vpn_pptp_connection()
        self.main_init_cb()

class NoSetting(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)

        label_align = gtk.Alignment(0.5,0.5,0,0)

        label = Label("No connection available")
        label_align.add(label)
        self.add(label_align)


class IPV4Conf(gtk.VBox):

    def __init__(self, connection = None):
        
        gtk.VBox.__init__(self)
        self.connection = connection 
        table = gtk.Table(9, 2 , False)
        # Ip configuration
        self.auto_ip = gtk.RadioButton(None, "自动获得IP地址")
        self.auto_ip.set_sensitive(False)
        table.attach(self.auto_ip, 0,1,0,1,)
        self.manual_ip = gtk.RadioButton(self.auto_ip, "手动添加IP地址")
        self.manual_ip.set_sensitive(False)
        table.attach(self.manual_ip, 0,1,1,2)

        addr_label = Label("IP地址:")
        table.attach(addr_label, 0,1,2,3)
        self.addr_entry = gtk.Entry()
        #self.addr_entry.set_size(30, 25)
        self.addr_entry.connect("activate", self.check_ip_valid)
        self.addr_entry.set_sensitive(False)
        table.attach(self.addr_entry, 1,2,2,3)

        mask_label = Label("子网掩码:")
        table.attach(mask_label, 0,1,3,4)
        self.mask_entry = gtk.Entry()
        #self.mask_entry.set_size(30, 25)
        self.mask_entry.connect("activate", self.check_mask_valid)
        table.attach(self.mask_entry, 1,2,3,4)
        
        gate_label = Label("默认网关")
        table.attach(gate_label, 0,1,4,5)
        self.gate_entry = gtk.Entry()
        #self.gate_entry.set_size(30, 25)
        self.gate_entry.connect("activate", self.check_gate_valid)
        table.attach(self.gate_entry, 1,2,4,5)
        
        #DNS configuration
        self.auto_dns = gtk.RadioButton(None, "自动获得DNS服务器地址")
        self.manual_dns = gtk.RadioButton(self.auto_dns,"使用下面的dns服务器:")
        table.attach(self.auto_dns, 0, 1, 5, 6) 
        table.attach(self.manual_dns, 0, 1, 6, 7)

        master_dns = Label("首选DNS服务器地址:")
        slave_dns = Label("使用下面的DNS服务器地址:")
        self.master_entry = gtk.Entry()
        self.slave_entry = gtk.Entry()
        #self.master_entry.set_size(30, 25)
        #self.slave_entry.set_size(30, 25)
        self.master_entry.connect("activate", self.check_dns_valid)
        self.slave_entry.connect("activate", self.check_dns_valid)
        
        table.attach(master_dns, 0, 1, 7, 8)
        table.attach(self.master_entry, 1, 2, 7, 8)
        table.attach(slave_dns, 0, 1, 8, 9)
        table.attach(self.slave_entry, 1, 2, 8, 9)

        align = gtk.Alignment(0.5,0.5,0.5,0.5)
        align.add(table)
        self.add(align)
        
        self.show_all()
        
        self.cs =None
        self.reset(connection)
        #self.manual_ip.connect("toggled", self.manual_ip_entry, self.cs)
        #self.auto_ip.connect("toggled", self.auto_get_ip_addr, self.cs)
        self.auto_dns.connect("toggled", self.auto_dns_set, self.cs)
        self.manual_dns.connect("toggled", self.manual_dns_set, self.cs)
        #self.apply_button.connect("clicked", self.save_changes, self.cs)
        #self.cancel_button.connect("clicked", self.cancel_changes)

    def check_ip_valid(self, widget ):
        text = widget.get_text()
        if TypeConvert.is_valid_ip4(text):
            print "valid"
        else:
            print "invalid"

    def check_mask_valid(self, widget):
        text = widget.get_text()
        if TypeConvert.is_valid_netmask(text):
            print "valid"
        else:
            print "invalid"


    def check_gate_valid(self, widget):
        text = widget.get_text()
        if TypeConvert.is_valid_gw(self.addr_entry.get_text(),
                                   self.mask_entry.get_text(),
                                   text):
            print "valid"
        else:
            print "invalid"
        

    def check_dns_valid(self, widget):
        text = widget.get_text()
        if TypeConvert.is_valid_ip4(text):
            print "valid"
        else:
            print "invalid"

    def reset(self, connection):
        self.cs = connection.get_setting("ipv4")       
        self.clear_entry()
        #print self.cs.dns
        #print self.cs.method, connection.get_setting("connection").id
        if self.cs.method == "auto":
            self.auto_ip.set_active(True)
            self.addr_entry.set_sensitive(False)
            self.mask_entry.set_sensitive(False)
            self.gate_entry.set_sensitive(False)
            
        else:
            self.manual_ip.set_active(True)
            self.addr_entry.set_sensitive(True)
            self.mask_entry.set_sensitive(True)
            self.gate_entry.set_sensitive(True)
            if not self.cs.addresses == []:
                self.addr_entry.set_text(self.cs.addresses[0][0])
                self.mask_entry.set_text(self.cs.addresses[0][1])
                self.gate_entry.set_text(self.cs.addresses[0][2])

        if self.cs.dns == []:
            self.auto_dns.set_active(True)
            self.master_entry.set_sensitive(False)
            self.slave_entry.set_sensitive(False)
        else:
            self.manual_dns.set_active(True)
            self.master_entry.set_sensitive(True)
            self.slave_entry.set_sensitive(True)
            if len(self.cs.dns) > 1:
                self.slave_entry.set_text(self.cs.dns[1])
            self.master_entry.set_text(self.cs.dns[0])


    def auto_dns_set(self, widget, connection):
        if widget.get_active():
            connection.clear_dns()
            self.master_entry.set_sensitive(False)
            self.slave_entry.set_sensitive(False)

    def manual_dns_set(self, widget, connection):
        if widget.get_active():
            self.master_entry.set_sensitive(True)
            self.slave_entry.set_sensitive(True)
            if len(connection.dns) == 1:
                self.master_entry.set_text(connection.dns[0])
            elif len(connection.dns) > 1:
                self.slave_entry.set_text(connection.dns[1])

    def clear_entry(self):
        self.addr_entry.set_text("")
        self.mask_entry.set_text("")
        self.gate_entry.set_text("")
        self.master_entry.set_text("")
        self.slave_entry.set_text("")

    def auto_get_ip_addr(self, widget, connection):
        if widget.get_active():
            connection.method = 'auto'
            self.addr_entry.set_sensitive(False)
            self.mask_entry.set_sensitive(False)
            self.gate_entry.set_sensitive(False)
    def manual_ip_entry(self,widget, connection):
        if widget.get_active():
            connection.method = 'manual'
            self.addr_entry.set_sensitive(True)
            self.mask_entry.set_sensitive(True)
            self.gate_entry.set_sensitive(True)
            if not connection.addresses == []:
                self.addr_entry.set_text(connection.addresses[0][0])
                self.mask_entry.set_text(connection.addresses[0][1])
                self.gate_entry.set_text(connection.addresses[0][2])
    
    def save_changes(self):
        connection = self.cs
        if connection.method =="manual": 
            connection.clear_addresses()
            connection.add_address([self.addr_entry.get_text(),
                                     self.mask_entry.get_text(),
                                     self.gate_entry.get_text()])
            connection.clear_dns()
            if not self.master_entry.get_text() == "":
                connection.add_dns(self.master_entry.get_text())
            if not self.slave_entry.get_text() == "":
                connection.add_dns(self.slave_entry.get_text())
        
        connection.adapt_ip4config_commit()
        #self.connection.update()


class PPTPConf(gtk.VBox):

    def __init__(self, connection, module_frame):
        gtk.VBox.__init__(self)
        self.connection = connection
        self.module_frame = module_frame
        self.vpn_setting = self.connection.get_setting("vpn")
        self.ppp = PPPConf(self.connection, module_frame)
        slider.append_page(self.ppp)
        self.ppp.show_all()

        # UI
        pptp_table = gtk.Table(7, 4, False)
        gateway_label = Label("Gateway:")
        user_label = Label("User:")
        password_label = Label("Password:")
        nt_domain_label = Label("NT Domain:")
        # Radio Button
        self.pptp_radio = RadioButton("PPTP")
        self.l2tp_radio = RadioButton("L2TP")
        #pack labels
        pptp_table.attach(self.pptp_radio, 0, 2, 0, 1)
        pptp_table.attach(self.l2tp_radio, 2, 4, 0, 1)
        pptp_table.attach(gateway_label, 0, 2 , 1, 2)
        pptp_table.attach(user_label, 0, 2, 2, 3)
        pptp_table.attach(password_label, 0, 2, 3, 4)
        pptp_table.attach(nt_domain_label, 0, 1, 5, 6)

        # entries
        self.gateway_entry = InputEntry()
        self.gateway_entry.set_size(200,25 )
        self.user_entry = InputEntry()
        self.user_entry.set_size(200,25)
        # FIXME should change to new_entry PasswordEntry
        self.password_entry = gtk.Entry()
        self.password_entry.set_visibility(False)
        #self.password_entry.set_size(200, 25)
        self.password_show = CheckButton("Show Password")
        self.password_show.set_active(False)
        self.password_show.connect("toggled", self.show_password)
        self.nt_domain_entry = InputEntry()
        self.nt_domain_entry.set_size(200,25 )

        #pack entries
        pptp_table.attach(self.gateway_entry, 2, 4, 1, 2)
        pptp_table.attach(self.user_entry, 2, 4, 2, 3)
        pptp_table.attach(self.password_entry, 2, 4, 3, 4)
        pptp_table.attach(self.password_show, 2, 4, 4, 5)
        pptp_table.attach(self.nt_domain_entry, 2, 4, 5, 6)
        # Advance setting button
        advanced_button = Button("Advanced Setting")
        advanced_button.connect("clicked", self.advanced_button_click)

        pptp_table.attach(advanced_button, 3, 4, 6, 7)
        self.service_type = self.vpn_setting.service_type.split(".")[-1]
        if self.service_type == "l2tp":
            self.l2tp_radio.set_active(True)
        else:
            self.pptp_radio.set_active(True)
        self.pptp_radio.connect("toggled",self.radio_toggled, "pptp")
        self.l2tp_radio.connect("toggled",self.radio_toggled, "l2tp")
        # set signals

        align = gtk.Alignment(0.5, 0.5, 0, 0)
        align.add(pptp_table)
        self.add(align)
        self.show_all()
        self.refresh()

    def refresh(self):
        #print ">>>",self.vpn_setting.data
        #print self.vpn_setting.data
        gateway = self.vpn_setting.get_data_item("gateway")
        user = self.vpn_setting.get_data_item("user")
        domain = self.vpn_setting.get_data_item("domain")

        self.gateway_entry.entry.connect("focus-out-event", self.entry_changed, "gateway")
        self.user_entry.entry.connect("focus-out-event", self.entry_changed, "user")
        #self.password_entry.entry.connect("focus-out-event", self.entry_changed, "password")
        self.password_entry.connect("focus-out-event", self.entry_changed, "password")
        self.nt_domain_entry.entry.connect("focus-out-event", self.entry_changed, "domain")


        if gateway:
            self.gateway_entry.set_text(gateway)
        if user:
            self.user_entry.set_text(user)
        (setting_name, method) = self.connection.guess_secret_info() 
        try:
            password = nm_module.secret_agent.agent_get_secrets(self.connection.object_path,
                                                    setting_name,
                                                    method)
            if password == None:
                #self.password_entry.entry.set_text("")
                self.password_entry.set_text("")
            else:
                #self.password_entry.entry.set_text(password)
                self.password_entry.set_text(password)
        except:
            print "failed to get password"

        if domain:
            self.nt_domain_entry.set_text(domain)
                
    def save_setting(self):
        pass

    def show_password(self, widget):
        if widget.get_active():
            self.password_entry.set_visibility(True)
        else:
            self.password_entry.set_visibility(False)


    def entry_changed(self, widget, event, item):
        print "focus out"
        text = widget.get_text()
        if text:
            if item == "password":
                self.vpn_setting.set_secret_item(item, text)
            else:
                self.vpn_setting.set_data_item(item, text)
        else:
            self.vpn_setting.delete_data_item(item)
    
    def radio_toggled(self, widget, service_type):
        if widget.get_active():
            self.vpn_setting.service_type = "org.freedesktop.NetworkManager." + service_type
            self.service_type = service_type
            self.refresh()

    def advanced_button_click(self, widget):
        self.ppp.refresh()
        self.module_frame.send_submodule_crumb(3, "高级设置")
        slider.slide_to_page(self.ppp, "right")
        #pass


class PPPConf(gtk.VBox):

    def __init__(self, connection, module_frame):
        gtk.VBox.__init__(self)
        
        self.module_frame = module_frame
        self.connection = connection
        self.vpn_setting = self.connection.get_setting("vpn")
        

        method = Contain(app_theme.get_pixbuf("/Network/misc.png"), "Configure Method", self.toggle_cb)
        # invisable settings
        self.refuse_eap = CheckButton("EAP")
        self.refuse_pap = CheckButton("PAP")
        self.refuse_chap = CheckButton("CHAP")
        self.refuse_mschap = CheckButton("MSCHAP")
        self.refuse_mschapv2 = CheckButton("MSCHAP v2")
        
        self.method_table = gtk.Table(5, 8, False)
        self.method_table.set_no_show_all(True)
        self.method_table.hide()
        self.method_table.attach(self.refuse_eap, 0, 8, 0, 1)
        self.method_table.attach(self.refuse_pap, 0, 8, 1, 2)
        self.method_table.attach(self.refuse_chap, 0, 8, 2, 3)
        self.method_table.attach(self.refuse_mschap, 0, 8, 3, 4)
        self.method_table.attach(self.refuse_mschapv2, 0, 8, 4, 5)

        # visible settings
        self.compression = Label("Security and Compression")

        self.require_mppe = CheckButton("Use point-to-point encryption(mppe)")
        self.require_mppe_128 = CheckButton("Require 128-bit encryption")
        self.mppe_stateful = CheckButton("Use stataful MPPE")
        
        self.nobsdcomp = CheckButton("Allow BSD data Compression")
        self.nodeflate = CheckButton("Allow Deflate date compression")
        self.no_vj_comp = CheckButton("Use TCP header compression")
        self.nopcomp = CheckButton("Use protocal field compression negotiation")
        self.noaccomp = CheckButton("Use Address/Control compression")
        
        ## Settings for IPSec
        self.ip_sec_enable = CheckButton("Enable IPSec tunnel to l2tp host")
        self.group_name_label = Label("Group Name:")
        self.gateway_id_label = Label("Gateway ID:")
        self.pre_shared_key_label = Label("Pre_Shared_key")
        self.group_name = InputEntry()
        self.group_name.set_size(200, 25)
        self.gateway_id = InputEntry()
        self.gateway_id.set_size(200, 25)
        self.pre_shared_key = InputEntry()
        self.pre_shared_key.set_size(200, 25)

        self.echo = Label("Echo")
        self.ppp_echo = CheckButton("Send PPP echo packets")
        
        self.table = gtk.Table(11, 10, False)
        self.ip_sec_table = gtk.Table(4, 3, False)
        self.ip_sec_table.set_size_request(100, 20)
        self.init_ui()
        #self.mppe.set_size_request(100, 10)

        vbox = gtk.VBox()
        vbox.pack_start(method, False, False)
        vbox.pack_start(self.method_table, False, False)
        vbox.pack_start(self.table, False, False)
        hbox = gtk.HBox()
        hbox.pack_start(vbox, False, False)
        ip_sec_vbox = gtk.VBox()
        ip_sec_vbox.pack_start(self.ip_sec_table, False, False)
        hbox.pack_start(ip_sec_vbox, False, False)
        align = gtk.Alignment(0.5, 0.5, 0.5, 0)
        align.add(hbox)
        self.add(align)

        confirm_button = Button("Confirm")
        confirm_button.connect("clicked", self.confirm_button_cb)
        button_aligns = gtk.Alignment(0.5 , 1, 0, 0)

        button_aligns.add(confirm_button)
        self.add(button_aligns)

        self.require_mppe_128.set_sensitive(False)
        self.mppe_stateful.set_sensitive(False)
        #self.refresh()

        self.refuse_eap.connect("toggled", self.check_button_cb, "refuse-eap")
        self.refuse_pap.connect("toggled", self.check_button_cb, "refuse-pap")
        self.refuse_chap.connect("toggled", self.check_button_cb, "refuse-chap")
        self.refuse_mschap.connect("toggled", self.check_button_cb, "refuse-mschap")
        self.refuse_mschapv2.connect("toggled", self.check_button_cb, "refuse-mschapv2")
        self.require_mppe.connect("toggled", self.check_button_cb, "require-mppe")
        self.require_mppe_128.connect("toggled", self.check_button_cb, "require-mppe-128")
        self.mppe_stateful.connect("toggled", self.check_button_cb,"mppe-stateful")
        self.nobsdcomp.connect("toggled", self.check_button_cb, "nobsdcomp")
        self.nodeflate.connect("toggled", self.check_button_cb, "nodeflate")
        self.no_vj_comp.connect("toggled", self.check_button_cb, "novj")
        self.ppp_echo.connect("toggled", self.check_button_cb, "echo")
        self.nopcomp.connect("toggled", self.check_button_cb, "nopcomp")
        self.noaccomp.connect("toggled", self.check_button_cb, "noaccomp")

        self.ip_sec_enable.connect("toggled", self.enable_ipsec_cb)
        self.group_name.entry.connect("focus-out-event", self.entry_focus_out_cb, "ipsec-group-name")
        self.gateway_id.entry.connect("focus-out-event", self.entry_focus_out_cb, "ipsec-gataway-id")
        self.pre_shared_key.entry.connect("focus-out-event", self.entry_focus_out_cb, "ipsec-psk")
        self.group_name.entry.connect("changed", self.entry_changed_cb, "ipsec-group-name")
        self.gateway_id.entry.connect("changed", self.entry_changed_cb, "ipsec-gateway-id")
        self.pre_shared_key.entry.connect("changed", self.entry_changed_cb, "ipsec-psk")

        method.set_active(True)

    def init_ui(self):
        self.service_type = self.vpn_setting.service_type.split(".")[-1]
        print self.service_type
        container_remove_all(self.table)
        container_remove_all(self.ip_sec_table)
        self.table.attach(self.compression, 0, 5, 0 ,1)
        self.table.attach(self.require_mppe, 0, 10, 1, 2)
        self.table.attach(self.require_mppe_128, 1, 10, 2, 3)
        self.table.attach(self.mppe_stateful, 1, 10, 3, 4)
        self.table.attach(self.nobsdcomp, 0, 10, 4, 5)
        self.table.attach(self.nodeflate, 0, 10, 5, 6)
        self.table.attach(self.no_vj_comp, 0, 10, 6, 7)
        self.table.attach(self.echo, 0, 5, 9, 10)
        self.table.attach(self.ppp_echo, 0, 10, 10, 11)

        if self.service_type == "l2tp":
            self.table.attach(self.nopcomp, 0, 10, 7, 8)
            self.table.attach(self.noaccomp, 0, 10 , 8, 9)

            self.ip_sec_table.attach(self.ip_sec_enable, 0, 3, 0, 1)
            self.ip_sec_table.attach(self.group_name_label, 0, 1, 1, 2)
            self.ip_sec_table.attach(self.group_name, 1, 3, 1, 2)
            self.ip_sec_table.attach(self.gateway_id_label, 0, 1, 2, 3)
            self.ip_sec_table.attach(self.gateway_id, 1, 3, 2, 3)
            self.ip_sec_table.attach(self.pre_shared_key_label, 0, 1, 3, 4)
            self.ip_sec_table.attach(self.pre_shared_key, 1, 3, 3, 4)
            self.ip_sec_table.show_all()
        self.table.show_all()

    def refresh(self):
        #=========================
        # retreieve settings
        self.init_ui()
        refuse_eap = self.vpn_setting.get_data_item("refuse-eap")
        print ">>",self.vpn_setting.data
        
        refuse_pap = self.vpn_setting.get_data_item("refuse-pap")
        refuse_chap = self.vpn_setting.get_data_item("refuse-chap")
        refuse_mschap = self.vpn_setting.get_data_item("refuse-mschap")
        refuse_mschapv2 = self.vpn_setting.get_data_item("refuse-mschapv2")

        require_mppe = self.vpn_setting.get_data_item("require-mppe")
        require_mppe_128 = self.vpn_setting.get_data_item("require-mppe-128")
        mppe_stateful = self.vpn_setting.get_data_item("mppe-stateful")

        nobsdcomp = self.vpn_setting.get_data_item("nobsdcomp")
        nodeflate = self.vpn_setting.get_data_item("nodeflate")
        no_vj_comp = self.vpn_setting.get_data_item("novj")


        lcp_echo_failure = self.vpn_setting.get_data_item("lcp-echo-failure")
        lcp_echo_interval = self.vpn_setting.get_data_item("lcp-echo-interval")
        
        self.require_mppe.set_active(require_mppe != None)
        self.refuse_eap.set_active(refuse_eap is None)
        self.refuse_pap.set_active(refuse_pap is None)
        self.refuse_chap.set_active(refuse_chap is None)
        self.refuse_mschap.set_active(refuse_mschap is None)
        self.refuse_mschapv2.set_active(refuse_mschapv2 is None)

        self.require_mppe_128.set_active(require_mppe_128 != None)
        self.mppe_stateful.set_active(mppe_stateful != None)
        self.nobsdcomp.set_active(nobsdcomp is None)
        self.nodeflate.set_active(nodeflate is None)
        self.no_vj_comp.set_active(no_vj_comp is None)

        if self.service_type == "l2tp":
            #no_vj_comp = self.vpn_setting.get_data_item("no_vj_comp")
            nopcomp = self.vpn_setting.get_data_item("nopcomp")
            noaccomp = self.vpn_setting.get_data_item("noaccomp")
            ipsec_enabled = self.vpn_setting.get_data_item("ipsec-enabled")

            self.nopcomp.set_active(nopcomp is None)
            self.noaccomp.set_active(noaccomp is None)
            
            if ipsec_enabled:
                self.ip_sec_enable.set_active(True)

            else:
                self.ip_sec_enable.set_active(False)

        if lcp_echo_failure == None and lcp_echo_interval == None:
            self.ppp_echo.set_active(False)
        else:
            self.ppp_echo.set_active(True)

        #==================================
        # Connect signal
    def enable_ipsec_cb(self, widget):
        active = widget.get_active()
        if active:
            self.vpn_setting.set_data_item("ipsec-enabled", "yes")
            self.group_name.set_sensitive(True)
            self.gateway_id.set_sensitive(True)
            self.pre_shared_key.set_sensitive(True)

            ipsec_group_name = self.vpn_setting.get_data_item("ipsec-group-name")
            ipsec_gateway_id = self.vpn_setting.get_data_item("ipsec-gateway-id")
            ipsec_psk = self.vpn_setting.get_data_item("ipsec-psk")

            self.group_name.set_text(ipsec_group_name)
            self.gateway_id.set_text(ipsec_gateway_id)
            self.pre_shared_key.set_text(ipsec_psk)
        else:
            self.vpn_setting.delete_data_item("ipsec-enabled")
            self.group_name.set_text("")
            self.gateway_id.set_text("")
            self.pre_shared_key.set_text("")

            self.group_name.set_sensitive(False)
            self.gateway_id.set_sensitive(False)
            self.pre_shared_key.set_sensitive(False)

    def entry_focus_out_cb(self, widget, event, key):
        text = widget.get_text()
        if text:
            self.vpn_setting.set_data_item(key, text)
        else:
            self.vpn_setting.delete_data_item(key)
    def entry_changed_cb(self, widget, string, key):
        if string == "":
            print key,"entry is empty"
            self.vpn_setting.delete_data_item(key)

    def check_button_cb(self, widget, key):
        active = widget.get_active()
        if key.startswith("refuse"):
            if active:
                self.vpn_setting.delete_data_item(key)
            else:
                self.vpn_setting.set_data_item(key, "yes")

            if self.auth_lock():
                self.require_mppe.set_sensitive(True)
            else:
                self.require_mppe.set_sensitive(False)
                self.require_mppe.set_active(False)
                # FIXME auth_lock false, still can change others bug
                #self.set_group_sensitive(True)
                #self.set_group_active(True)
                #if self.refuse_eap.get_active():
                    #print key
        elif key.startswith("no"):
            if active:
                self.vpn_setting.delete_data_item(key)
            else:
                self.vpn_setting.set_data_item(key, "yes")

        elif key == "echo":
            if active:
                self.vpn_setting.set_data_item("lcp_echo_failure", "5")
                self.vpn_setting.set_data_item("lcp_echo_interval", "30")
            else:
                self.vpn_setting.delete_data_item("lcp_echo_failure")
                self.vpn_setting.delete_data_item("lcp_echo_interval")
        else:
            if key == "require-mppe":
                if active:
                    self.vpn_setting.set_data_item(key, "yes")
                    self.set_group_active(False)
                    self.set_group_sensitive(False)

                    self.require_mppe_128.set_sensitive(True)
                    self.mppe_stateful.set_sensitive(True)
                else:
                    self.vpn_setting.delete_data_item(key)
                    self.set_group_active(True)
                    self.set_group_sensitive(True)
                    self.require_mppe_128.set_sensitive(False)
                    self.mppe_stateful.set_sensitive(False)
                    self.require_mppe_128.set_active(False)
                    self.mppe_stateful.set_active(False)
            else:
                if active:
                    self.vpn_setting.set_data_item(key, "yes")
                else:
                    self.vpn_setting.delete_data_item(key)

    def confirm_button_cb(self, widget):
        self.module_frame.send_message("change_crumb", 2)
        layout = slider.layout.get_children()
        for widget in layout:
            if isinstance(widget, VPNSetting):
                slider.slide_to_page(widget, "left")
        

    def auth_lock(self):
        if self.refuse_mschap.get_active() or self.refuse_mschapv2.get_active():
            return True
        else:
            return False

    def set_group_active(self, boolean):
        self.refuse_eap.set_active(boolean)
        self.refuse_pap.set_active(boolean)
        self.refuse_chap.set_active(boolean)

    def set_group_sensitive(self, boolean):
        self.refuse_eap.set_sensitive(boolean)
        self.refuse_pap.set_sensitive(boolean)
        self.refuse_chap.set_sensitive(boolean)


    def save_setting(self):
        pass

    def toggle_cb(self, widget):
        if widget.get_active():
            self.method_table.set_no_show_all(False)
            self.show_all()
        else:
            self.method_table.set_no_show_all(True)
            self.method_table.hide()
        # Check Buttons
