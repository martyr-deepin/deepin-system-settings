#!/usr/bin/env python
#-*- coding:utf-8 -*-

from theme import app_theme

from dtk.ui.button import Button,  CheckButton, RadioButton
from dtk.ui.entry import InputEntry, PasswordEntry
from dtk.ui.label import Label
from dtk.ui.utils import container_remove_all

from nm_modules import nm_module
from nmlib.nm_remote_connection import NMRemoteConnection
from container import MyToggleButton as SwitchButton
from container import TitleBar
from ipsettings import IPV4Conf
from elements import SettingSection
from shared_methods import Settings
from helper import Dispatcher, event_manager

import gtk
from nls import _
import style
from constants import CONTENT_FONT_SIZE

class VPNSetting(Settings):

    def __init__(self, spec_connection=None):
        Settings.__init__(self, [PPTPConf,
                                 Sections])
        self.crumb_name = _("VPN")
        self.spec_connection = spec_connection

    def get_connections(self):
        # Get all connections  
        connections = nm_module.nm_remote_settings.get_vpn_connections()
        if connections == []:
            # Create a new connection
            connect = nm_module.nm_remote_settings.new_vpn_pptp_connection()
            connections.append(connect)
        self.connections = connections
        return connections
        
    def save_changes(self, connection):
        print "saving"
        if isinstance(connection, NMRemoteConnection):
            connection.update()
        else:
            connection = nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'vpn')
            Dispatcher.emit("connection-replace", connection)
            Dispatcher.emit("vpn-redraw")

        Dispatcher.to_main_page()
        event_manager.emit("update-vpn-id", connection.get_setting("connection").id)
        #Dispatcher.set_button("apply", True)

    def delete_request_redraw(self):
        Dispatcher.emit("vpn-redraw")

    def apply_changes(self, connection):
        # FIXME Now just support one device

        active_connections = nm_module.nmclient.get_active_connections()
        if active_connections:
            device_path = active_connections[0].get_devices()[0].object_path
            specific_path = active_connections[0].object_path
            active_object = nm_module.nmclient.activate_connection(connection.object_path,
                                           device_path,
                                           specific_path)
            print active_object
            active_object.connect("vpn-state-changed", self.vpn_state_changed)
        else:
            print "no active connection available"

        Dispatcher.to_main_page()


    def try_to_connect_wired_device(self, device, connection):
        active = device.get_active_connection()
        if active:
            device_path = device.object_path
            specific_path = active.get_specific_object()
            active_object = nm_module.nmclient.activate_connection(connection.object_path,
                                               device_path,
                                               specific_path)
            if active_object != None:
                print "in wired device"
                active_vpn = nm_module.cache.get_spec_object(active_object.object_path)
                self.state_change_cb(active_vpn, connection.get_setting("connection").id)
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
                print "in wireless device"
                active_vpn = nm_module.cache.get_spec_object(active_object.object_path)
                self.state_change_cb(active_vpn, connection.get_setting("connection").id)

    def add_new_connection(self):
        new_connection = nm_module.nm_remote_settings.new_vpn_pptp_connection()
        return (new_connection, -1)

class Sections(gtk.Alignment):

    def __init__(self, connection, set_button, settings_obj=None):
        gtk.Alignment.__init__(self, 0, 0 ,0, 0)
        self.connection = connection
        self.set_button = set_button
        # 新增settings_obj变量，用于访问shared_methods.Settings对象
        self.settings_obj = settings_obj

        self.set_padding(35, 0, 20, 0)

        self.main_box = gtk.VBox()
        self.tab_name = "sfds"
        basic = SettingSection(_("Basic"))

        self.button = Button(_("Advanced"))
        self.button.connect("clicked", self.show_more_options)
        self.wired = SettingSection(_("Wired"), always_show=False)
        align = gtk.Alignment(0, 0, 0, 0)
        align.set_padding(0, 0, 376, 0)
        align.set_size_request(-1 , 30)
        align.add(self.button)
        
        basic.load([PPTPConf(connection, set_button), align])

        self.main_box.pack_start(basic, False, False)

        self.add(self.main_box)

    def show_more_options(self, widget):
        widget.destroy()
        self.ipv4 = SettingSection(_("Ipv4 setting"), always_show=True)
        self.ipv4.load([IPV4Conf(self.connection, self.set_button)])
        ppp = SettingSection(_("PPP setting"), always_show=True)
        ppp.load([PPPConf()])
        Dispatcher.emit("vpn-type-change", self.connection)
        self.main_box.pack_start(self.ipv4, False, False, 15 )
        self.main_box.pack_start(ppp, False, False)

class PPTPConf(gtk.VBox):
    ENTRY_WIDTH = 222
    LEFT_PADDING = 210
    def __init__(self, connection, module_frame, set_button_callback=None, settings_obj=None):
        gtk.VBox.__init__(self)
        self.connection = connection
        self.tab_name = _("PPTP")
        self.module_frame = module_frame
        self.set_button = set_button_callback
        # 新增settings_obj变量，用于访问shared_methods.Settings对象
        self.settings_obj = settings_obj

        self.vpn_setting = self.connection.get_setting("vpn")

        # UI

        pptp_table = gtk.Table(7, 4, False)

        name_label = Label(_("Setting Name:"),
                               enable_select=False,
                               enable_double_click=False)
        name_label.set_can_focus(False)
        gateway_label = Label(_("Gateway:"),
                               enable_select=False,
                               enable_double_click=False)
        gateway_label.set_can_focus(False)
        user_label = Label(_("Username:"),
                               enable_select=False,
                               enable_double_click=False)
        user_label.set_can_focus(False)
        password_label = Label(_("Password:"),
                               enable_select=False,
                               enable_double_click=False)
        password_label.set_can_focus(False)
        nt_domain_label = Label(_("NT Domain:"),
                               enable_select=False,
                               enable_double_click=False)
        nt_domain_label.set_can_focus(False)
        # Radio Button
        self.pptp_radio = RadioButton(_("PPTP"))
        self.l2tp_radio = RadioButton(_("L2TP"))
        radio_box = gtk.HBox(spacing=30)
        radio_box.pack_start(self.pptp_radio, False, False)
        radio_box.pack_start(self.l2tp_radio, False, False)
        #pack labels
        pptp_table.attach(style.wrap_with_align(radio_box, align="left"), 2,4, 0, 1)
        pptp_table.attach(style.wrap_with_align(name_label, width=self.LEFT_PADDING), 0, 2, 1, 2)
        pptp_table.attach(style.wrap_with_align(gateway_label, width=self.LEFT_PADDING), 0, 2 , 2, 3)
        pptp_table.attach(style.wrap_with_align(user_label, width=self.LEFT_PADDING), 0, 2, 3, 4)
        pptp_table.attach(style.wrap_with_align(password_label, width=self.LEFT_PADDING), 0, 2, 4, 5)
        #pptp_table.attach(style.wrap_with_align(nt_domain_label), 0, 2, 5, 6)

        # entries
        self.name_entry = InputEntry()
        self.name_entry.set_size(self.ENTRY_WIDTH, 22)

        self.gateway_entry = InputEntry()
        self.gateway_entry.set_size(self.ENTRY_WIDTH,22)
        self.user_entry = InputEntry()
        self.user_entry.set_size(self.ENTRY_WIDTH, 22)
        # FIXME should change to new_entry PasswordEntry
        self.password_entry = PasswordEntry()
        self.password_entry.set_size(self.ENTRY_WIDTH, 22)
        self.password_show = CheckButton(_("Show Password"), padding_x=0)
        self.password_show.set_active(False)
        self.password_show.connect("toggled", self.show_password)
        self.nt_domain_entry = InputEntry()
        self.nt_domain_entry.set_size(self.ENTRY_WIDTH, 22)

        #pack entries
        pptp_table.attach(style.wrap_with_align(self.name_entry, align="left"), 2, 4, 1, 2)
        pptp_table.attach(style.wrap_with_align(self.gateway_entry, align="left"), 2, 4, 2, 3)
        pptp_table.attach(style.wrap_with_align(self.user_entry, align="left"), 2, 4, 3, 4)
        pptp_table.attach(style.wrap_with_align(self.password_entry, align="left"), 2, 4, 4, 5)
        pptp_table.attach(style.wrap_with_align(self.password_show, align="left"), 2, 4, 5, 6)
        #pptp_table.attach(style.wrap_with_align(self.nt_domain_entry), 2, 4, 5, 6)
        # Advance setting button
        #advanced_button = Button(_("Advanced Setting"))
        #advanced_button.connect("clicked", self.advanced_button_click)

        #pptp_table.attach(style.wrap_with_align(advanced_button), 3, 4, 6, 7)
        self.service_type = self.vpn_setting.service_type.split(".")[-1]
        if self.service_type == "l2tp":
            self.l2tp_radio.set_active(True)
        else:
            self.pptp_radio.set_active(True)
        self.pptp_radio.connect("toggled",self.radio_toggled, "pptp")
        self.l2tp_radio.connect("toggled",self.radio_toggled, "l2tp")
        # set signals

        #align = style.set_box_with_align(pptp_table, "text")
        table_align = gtk.Alignment(0, 0, 0, 0)
        table_align.add(pptp_table)
        #style.set_table_items(pptp_table, "entry")
        style.draw_background_color(self)
        style.set_table(pptp_table)
        self.add(table_align)
        self.show_all()
        self.refresh()
        self.name_entry.entry.connect("changed", self.entry_changed, "name")
        self.gateway_entry.entry.connect("changed", self.entry_changed, "gateway")
        self.user_entry.entry.connect("changed", self.entry_changed, "user")
        self.password_entry.entry.connect("changed", self.entry_changed, "password")
        self.nt_domain_entry.entry.connect("changed", self.entry_changed, "domain")

        if self.connection.check_setting_finish():
            print "in vpn"
            Dispatcher.set_button("save", True)
        else:
            print "in vpn"
            Dispatcher.set_button("save", False)

    def refresh(self):
        #print ">>>",self.vpn_setting.data
        #print self.vpn_setting.data
        name = self.connection.get_setting("connection").id
        gateway = self.vpn_setting.get_data_item("gateway")
        user = self.vpn_setting.get_data_item("user")
        domain = self.vpn_setting.get_data_item("domain")

        if type(self.connection) == NMRemoteConnection:
            self.name_entry.set_text(name)

        if gateway:
            self.gateway_entry.set_text(gateway)
        if user:
            self.user_entry.set_text(user)

        (setting_name, method) = self.connection.guess_secret_info() 
        try:
            password = nm_module.secret_agent.agent_get_secrets(self.connection.object_path,
                                                    setting_name,
                                                    method)
            if password is None:
                #self.password_entry.entry.set_text("")
                self.password_entry.entry.set_text("")
            else:
                #self.password_entry.entry.set_text(password)
                self.password_entry.entry.set_text(password)
                self.vpn_setting.set_secret_item("password", password)
        except:
            pass

        if domain:
            self.nt_domain_entry.set_text(domain)
                
    def save_setting(self):
        pass

    def show_password(self, widget):
        if widget.get_active():
            self.password_entry.show_password(True)
        else:
            self.password_entry.show_password(False)


    def entry_changed(self, widget, content, item):
        text = content
        if item == "name":
            self.connection.get_setting("connection").id = content

        if text:
            if item == "password":
                self.vpn_setting.set_secret_item(item, text)
            elif item != "name":
                self.vpn_setting.set_data_item(item, text)
            
        else:
            if item == "password":
                self.vpn_setting.set_secret_item(item, "")
            else:
                self.vpn_setting.delete_data_item(item)

        if self.connection.check_setting_finish():
            Dispatcher.set_button("save", True)
        else:
            Dispatcher.set_button("save", False)
    
    def radio_toggled(self, widget, service_type):
        if widget.get_active():
            self.vpn_setting.service_type = "org.freedesktop.NetworkManager." + service_type
            self.service_type = service_type

        if self.connection.check_setting_finish():
            Dispatcher.set_button("save", True)
        else:
            Dispatcher.set_button("save", False)
            self.refresh()

        Dispatcher.emit("vpn-type-change", self.connection)
            

    def advanced_button_click(self, widget):
        ppp = PPPConf(self.module_frame, Dispatcher.set_button)
        ppp.refresh(self.connection)
        Dispatcher.send_submodule_crumb(3, _("Advanced"))
        nm_module.slider.slide_to_page(ppp, "right")
        #pass

class PPPConf(gtk.VBox):
    ENTRY = 0
    OFFBUTTON = 1

    TABLE_WIDTH = 150
    def __init__(self):
        gtk.VBox.__init__(self)
        
        #self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        #Dispatcher.set_button = set_button_callback
        #self.module_frame = module_frame
        
        self.method_title = TitleBar(None,
                                     _("Configure Method"),
                                     width=self.TABLE_WIDTH,
                                     has_separator=False)

        self.refuse_eap_label = Label(_("EAP"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.refuse_pap_label = Label(_("PAP"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.refuse_chap_label = Label(_("CHAP"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.refuse_mschap_label = Label(_("MSCHAP"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.refuse_mschapv2_label = Label(_("MSCHAP v2"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.refuse_eap = SwitchButton()
        self.refuse_pap = SwitchButton()
        self.refuse_chap = SwitchButton()
        self.refuse_mschap = SwitchButton()
        self.refuse_mschapv2 = SwitchButton()
        
        self.method_table = gtk.Table(23, 3, False)

        # visible settings

        self.compression_title = TitleBar(None,
                                          _("Compression"),
                                          width=self.TABLE_WIDTH,
                                          has_separator=False)

        self.echo_title = TitleBar(None,
                                   _("Echo"),
                                   width=self.TABLE_WIDTH,
                                   has_separator=False)


        #compressio))n = Label(_("Compression"), text_size=TITLE_FONT_SIZE)
        self.require_mppe_label = Label(_("Use point-to-point encryption(mppe)"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.require_mppe_128_label = Label(_("Require 128-bit encryption"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.mppe_stateful_label = Label(_("Use stataful MPPE"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.nobsdcomp_label = Label(_("Allow BSD data Compression"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.nodeflate_label = Label(_("Allow Deflate date compression"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.no_vj_comp_label = Label(_("Use TCP header compression"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        #echo = Label("Echo", text_size=TITLE_FONT_SIZE)
        self.ppp_echo_label = Label(_("Send PPP echo packets"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.nopcomp_label = Label(_("Use protocal field compression negotiation"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.noaccomp_label = Label(_("Use Address/Control compression"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)

        self.require_mppe = SwitchButton()
        self.require_mppe_128 = SwitchButton()
        self.mppe_stateful = SwitchButton()
        
        self.nobsdcomp = SwitchButton()
        self.nodeflate = SwitchButton()
        self.no_vj_comp = SwitchButton()
        self.nopcomp = SwitchButton()
        self.noaccomp = SwitchButton() 
        self.ppp_echo = SwitchButton()
        self.ip_sec_enable = SwitchButton()

        ## Settings for IPSec
        self.ipsec_title = TitleBar(None,
                                    _("IPSec Setting"),
                                    width=self.TABLE_WIDTH,
                                    has_separator=False)

        self.ip_sec_enable_label = Label(_("Enable IPSec tunnel to l2tp host"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.group_name_label = Label(_("Group Name:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.gateway_id_label = Label(_("Gateway ID:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.pre_shared_key_label = Label(_("Pre_Shared_key"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.group_name = InputEntry()
        self.group_name.set_size(self.TABLE_WIDTH, 22)
        self.gateway_id = InputEntry()
        self.gateway_id.set_size(self.TABLE_WIDTH, 22)
        self.pre_shared_key = InputEntry()
        self.pre_shared_key.set_size(self.TABLE_WIDTH, 22)
        
        methods_list = ["refuse_eap", "refuse_eap_label",
                        "refuse_pap", "refuse_pap_label",
                        "refuse_chap", "refuse_chap_label",
                        "refuse_mschap", "refuse_mschap_label",
                        "refuse_mschapv2", "refuse_mschapv2_label"]
        compression_list = ["require_mppe_label", "require_mppe",
                            "require_mppe_128_label", "require_mppe_128",
                            "mppe_stateful_label", "mppe_stateful",
                            "nobsdcomp_label", "nobsdcomp",
                            "nodeflate_label", "nodeflate",
                            "no_vj_comp_label", "no_vj_comp",
                            "nopcomp_label", "nopcomp",
                            "noaccomp_label", "noaccomp"]

        echo_list = ["ppp_echo_label","ppp_echo"]

        ip_sec_list = ["ip_sec_enable_label", "ip_sec_enable",
                       "group_name_label", "group_name",
                       "gateway_id_label", "gateway_id",
                       "pre_shared_key_label", "pre_shared_key"]

        for name in (compression_list+echo_list+methods_list + ip_sec_list):
            widget = getattr(self, name)
            if not name.endswith("label"):
                align = style.wrap_with_align(widget, align="left")
            else:
                align = style.wrap_with_align(widget, width=210)

            setattr(self, name + "_align", align)

        #vbox = gtk.VBox()
        table_align = gtk.Alignment(0, 0, 0, 0)
        table_align.add(self.method_table)
        style.set_table(self.method_table)

        self.pack_start(table_align, False, False)
        self.method_table.set_row_spacing(5, 20)
        self.method_table.set_row_spacing(15, 20)
        self.method_table.set_row_spacing(18, 20)

        Dispatcher.connect("vpn-type-change", lambda w,c:self.refresh(c))
        #align = style.set_box_with_align(vbox, "text")
        #self.add_with_viewport(align)
        #style.draw_background_color(align)


        #confirm_button = Button("Confirm")
        #confirm_button.connect("clicked", self.confirm_button_cb)
        #button_aligns = gtk.Alignment(0.5 , 1, 0, 0)
        #button_aligns.add(confirm_button)
        #self.add(button_aligns)

        #self.require_mppe_128.set_sensitive(False)
        #self.mppe_stateful.set_sensitive(False)
        ##self.refresh()
    
    def init_signal(self):
        self.refuse_eap.connect("toggled", self.check_button_cb, "refuse-eap")
        self.refuse_pap.connect("toggled", self.check_button_cb, "refuse-pap")
        self.refuse_chap.connect("toggled", self.check_button_cb, "refuse-chap")
        self.refuse_mschap.connect("toggled", self.check_button_cb, "refuse-mschap")
        self.refuse_mschapv2.connect("toggled", self.check_button_cb, "refuse-mschapv2")
        self.require_mppe.connect("toggled", self.click_mppe_callback, "require-mppe")
        self.require_mppe_128.connect("toggled", self.check_button_cb, "require-mppe-128")
        self.mppe_stateful.connect("toggled", self.check_button_cb,"mppe-stateful")
        self.nobsdcomp.connect("toggled", self.check_button_cb, "nobsdcomp")
        self.nodeflate.connect("toggled", self.check_button_cb, "nodeflate")
        self.no_vj_comp.connect("toggled", self.check_button_cb, "novj")
        self.ppp_echo.connect("toggled", self.check_button_cb, "echo")
        self.nopcomp.connect("toggled", self.check_button_cb, "nopcomp")
        self.noaccomp.connect("toggled", self.check_button_cb, "noaccomp")

        self.ip_sec_enable.connect("toggled", self.enable_ipsec_cb)
        #self.group_name.entry.connect("focus-out-event", self.entry_focus_out_cb, "ipsec-group-name")
        #self.gateway_id.entry.connect("focus-out-event", self.entry_focus_out_cb, "ipsec-gataway-id")
        #self.pre_shared_key.entry.connect("focus-out-event", self.entry_focus_out_cb, "ipsec-psk")
        self.group_name.entry.connect("changed", self.entry_changed_cb, "ipsec-group-name")
        self.gateway_id.entry.connect("changed", self.entry_changed_cb, "ipsec-gateway-id")
        self.pre_shared_key.entry.connect("changed", self.entry_changed_cb, "ipsec-psk")

    def init_ui(self):

        self.service_type = self.vpn_setting.service_type.split(".")[-1]
        def table_attach(widget_name, row, padding=0):
            label = getattr(self, widget_name + "_label_align")
            widget = getattr(self, widget_name + "_align")
            self.method_table.attach(label, 0, 2, row, row + 1)
            self.method_table.attach(widget, 2, 3, row, row + 1, xpadding=padding)
        #print self.service_type
        container_remove_all(self.method_table)
        self.method_table.attach(self.method_title, 0, 3, 0, 1)
        table_attach( "refuse_eap", 1)
        table_attach( "refuse_pap", 2 )
        table_attach( "refuse_chap", 3)
        table_attach( "refuse_mschap", 4 )
        table_attach( "refuse_mschapv2", 5)
        self.method_table.attach( self.compression_title, 0, 3, 6 ,7)
        table_attach("require_mppe", 8)
        if self.require_mppe.get_active():
            table_attach("require_mppe_128", 9)
            table_attach("mppe_stateful", 10)
        table_attach("nobsdcomp", 11)
        table_attach("nodeflate", 12)
        table_attach("no_vj_comp", 13)
        self.method_table.attach(self.echo_title, 0, 3, 16, 17)
        table_attach("ppp_echo", 18)

        if self.service_type == "l2tp":
            print "this is l2tp"
            table_attach("nopcomp", 14)
            table_attach("noaccomp", 15)
            
            self.method_table.attach(self.ipsec_title, 0, 3, 19, 20)
            table_attach("ip_sec_enable", 20)
            if self.ip_sec_enable.get_active():
                table_attach("group_name", 21)
                table_attach("gateway_id", 22)
                table_attach("pre_shared_key", 23)

        self.method_table.show_all()

    def refresh(self, connection):
        self.connection = connection
        self.vpn_setting = self.connection.get_setting("vpn")
        #=========================
        # retreieve settings
        self.service_type = self.vpn_setting.service_type.split(".")[-1]
        print ">>",self.vpn_setting.data
        refuse_eap = self.vpn_setting.get_data_item("refuse-eap")
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
        
        self.refuse_mschap.set_active(refuse_mschap == None)
        self.refuse_mschapv2.set_active(refuse_mschapv2 == None)
        self.require_mppe.set_active(require_mppe != None)
        
        self.refuse_eap.set_active(refuse_eap == None)
        self.refuse_pap.set_active(refuse_pap == None)
        self.refuse_chap.set_active(refuse_chap == None)

        self.require_mppe_128.set_active(require_mppe_128 != None)
        self.mppe_stateful.set_active(mppe_stateful != None)
        self.nobsdcomp.set_active(nobsdcomp == None)
        self.nodeflate.set_active(nodeflate == None)
        self.no_vj_comp.set_active(no_vj_comp == None)

        if self.service_type == "l2tp":
            nopcomp = self.vpn_setting.get_data_item("nopcomp")
            noaccomp = self.vpn_setting.get_data_item("noaccomp")
            ipsec_enabled = self.vpn_setting.get_data_item("ipsec-enabled")

            self.nopcomp.set_active(nopcomp == None)
            self.noaccomp.set_active(noaccomp == None)
            
            if ipsec_enabled:
                self.ip_sec_enable.set_active(True)

                ipsec_group_name = self.vpn_setting.get_data_item("ipsec-group-name")
                ipsec_gateway_id = self.vpn_setting.get_data_item("ipsec-gateway-id")
                ipsec_psk = self.vpn_setting.get_data_item("ipsec-psk")
                self.group_name.set_text(ipsec_group_name)
                self.gateway_id.set_text(ipsec_gateway_id)
                self.pre_shared_key.set_text(ipsec_psk)

            else:
                self.ip_sec_enable.set_active(False)

        if lcp_echo_failure == None and lcp_echo_interval == None:
            self.ppp_echo.set_active(False)
        else:
            self.ppp_echo.set_active(True)

        self.init_signal()
        self.require_mppe.emit("toggled")
        self.init_ui()
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
            
            print ipsec_group_name
            self.group_name.set_text(ipsec_group_name)
            self.gateway_id.set_text(ipsec_gateway_id)
            self.pre_shared_key.set_text(ipsec_psk)
            self.init_ui()
        else:
            self.vpn_setting.delete_data_item("ipsec-enabled")
            self.group_name.set_text("")
            self.gateway_id.set_text("")
            self.pre_shared_key.set_text("")

            self.group_name.set_sensitive(False)
            self.gateway_id.set_sensitive(False)
            self.pre_shared_key.set_sensitive(False)
            self.init_ui()

    def entry_focus_out_cb(self, widget, event, key):
        text = widget.get_text()
        if text and key != "name":
            self.vpn_setting.set_data_item(key, text)
        else:
            self.vpn_setting.delete_data_item(key)
    def entry_changed_cb(self, widget, string, key):
        if string == "":
            print key,"entry is empty"
            self.vpn_setting.delete_data_item(key)
        elif key != "name":
            self.vpn_setting.set_data_item(key, string)

    def check_button_cb(self, widget, key):
        auth_lock = self.auth_lock()
        active = widget.get_active()
        if key.startswith("refuse"):
            if active:
                self.vpn_setting.delete_data_item(key)
            else:
                self.vpn_setting.set_data_item(key, "yes")

            if auth_lock:
                self.require_mppe_label.set_sensitive(False)
                self.require_mppe.set_sensitive(False)
                self.require_mppe.set_active(False)

                self.set_group_active(True)
                self.set_group_sensitive(False)

            else:
                self.require_mppe_label.set_sensitive(True)
                self.require_mppe.set_sensitive(True)
                self.set_group_sensitive(True)

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
        elif key != "name":
            if active:
                self.vpn_setting.set_data_item(key, "yes")
            else:
                self.vpn_setting.delete_data_item(key)
    
    def click_mppe_callback(self, widget, key):
        active = widget.get_active()
        if active and key != "name":
            self.vpn_setting.set_data_item(key, "yes")
            self.set_group_active(False)
            self.set_group_sensitive(False)

            self.mppe_group_set_sensitive(True)
            self.init_ui()
        else:
            self.set_group_active(True)
            self.set_group_sensitive(True)
            self.vpn_setting.delete_data_item(key)
            self.mppe_group_set_sensitive(False)
            self.mppe_group_set_active(False)
            self.init_ui()

    def mppe_group_set_sensitive(self, boolean):
        self.require_mppe_128_label.set_sensitive(boolean)
        self.mppe_stateful_label.set_sensitive(boolean)
        self.require_mppe_128.set_sensitive(boolean)
        self.mppe_stateful.set_sensitive(boolean)

    def mppe_group_set_active(self, boolean):
        self.require_mppe_128.set_active(boolean)
        self.mppe_stateful.set_active(boolean)

    def confirm_button_cb(self, widget):
        self.module_frame.send_message("change_crumb", 2)
        nm_module.slider._slide_to_page("vpn", "left")
        
    def auth_lock(self):
        if self.refuse_mschap.get_active() or self.refuse_mschapv2.get_active():
            return False
        else:
            return True

    def set_group_active(self, boolean):
        self.refuse_eap.set_active(boolean)
        self.refuse_pap.set_active(boolean)
        self.refuse_chap.set_active(boolean)

    def set_group_sensitive(self, boolean):
        self.refuse_eap.set_sensitive(boolean)
        self.refuse_pap.set_sensitive(boolean)
        self.refuse_chap.set_sensitive(boolean)
        self.refuse_eap_label.set_sensitive(boolean)
        self.refuse_pap_label.set_sensitive(boolean)
        self.refuse_chap_label.set_sensitive(boolean)
