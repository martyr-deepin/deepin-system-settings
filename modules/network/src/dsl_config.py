#!/usr/bin/env python
#-*- coding:utf-8 -*-
#from theme import app_theme

from dss import app_theme
from dtk.ui.button import CheckButton, Button
from dtk.ui.entry import InputEntry, PasswordEntry
from dtk.ui.label import Label
from dtk.ui.spin import SpinBox
from nmlib.nm_utils import TypeConvert
from nmlib.nm_remote_connection import NMRemoteConnection
from nm_modules import nm_module

from container import TitleBar
from ipsettings import IPV4Conf
from elements import SettingSection, TableAsm, DefaultToggle

from shared_methods import Settings
from helper import Dispatcher

import gtk

from nls import _
# UI
import style
from constants import CONTENT_FONT_SIZE

def check_settings(connection, fn):
    if connection.check_setting_finish():
        Dispatcher.set_button('save', True)
    else:
        Dispatcher.set_button("save", False)

class DSLSetting(Settings):

    def __init__(self, spec_connection=None):
        Settings.__init__(self, [DSLConf,
                        Sections,
                        IPV4Conf,
                        PPPConf])
        self.crumb_name = _("DSL")
        self.spec_connection= spec_connection

    def get_connections(self):
        # Get all connections  
        connections = nm_module.nm_remote_settings.get_pppoe_connections()
        # Check connections

        if connections == []:
            # Create a new connection
            connections = [nm_module.nm_remote_settings.new_pppoe_connection()]
        
        self.connections = connections

        return self.connections
    
    def delete_request_redraw(self):
        Dispatcher.emit("dsl-redraw")


    def save_changes(self, connection):
        if connection.check_setting_finish():

            from nmlib.nm_remote_connection import NMRemoteConnection
            if isinstance(connection, NMRemoteConnection):
                #print "before update", TypeConvert.dbus2py(connection.settings_dict)
                connection.update()
                #print "after update", TypeConvert.dbus2py(connection.settings_dict)
            else:
                connection = nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')
                Dispatcher.emit("connection-replace", connection)
                Dispatcher.emit("dsl-redraw")

        Dispatcher.to_main_page()

        #Dispatcher.set_button("apply", True)

    def apply_changes(self, connection):
            device_path = nm_module.nmclient.get_wired_devices()[0].object_path
        #FIXME need to change device path into variables
            nm_module.nmclient.activate_connection_async(connection.object_path,
                                           device_path,
                                           "/")
            Dispatcher.to_setting_page()

    def add_new_connection(self):
        connection = nm_module.nm_remote_settings.new_pppoe_connection()
        return (connection, -1)

    def get_broadband(self):
        return self.settings[self.connection][0][1]

class Sections(gtk.Alignment):

    def __init__(self, connection, set_button, settings_obj=None):
        gtk.Alignment.__init__(self, 0, 0 ,1, 0)
        self.set_padding(35, 0, 20, 0)
        self.connection = connection
        self.set_button = set_button
        # 新增settings_obj变量，用于访问shared_methods.Settings对象
        self.settings_obj = settings_obj

        self.main_box = gtk.VBox()
        self.tab_name = "sfds"
        basic = SettingSection(_("Basic"))

        self.button = Button(_("Advanced"))
        #self.button.set_size_request(50, 22)
        self.button.connect("clicked", self.show_more_options)
        align = gtk.Alignment(0, 1.0, 0, 0)
        align.set_padding(0, 0, 376, 0)
        align.set_size_request(-1 ,30)
        align.add(self.button)
        
        basic.load([DSLConf(connection, set_button, settings_obj=self.settings_obj), align])

        self.main_box.pack_start(basic, False, False)

        self.add(self.main_box)

    def show_more_options(self, widget):
        widget.destroy()
        wired = SettingSection(_("Wired"), always_show=True)
        ipv4 = SettingSection(_("Ipv4 setting"), always_show=True)
        ppp = SettingSection(_("PPP"), always_show=True)
        wired.load([Wired(self.connection, self.set_button, settings_obj=self.settings_obj)])
        ipv4.load([IPV4Conf(self.connection, self.set_button, settings_obj=self.settings_obj)])
        ppp.load([PPPConf(self.connection, self.set_button, settings_obj=self.settings_obj)])
        #self.main_box.pack_start(self.space, False, False)
        self.main_box.pack_start(wired, False, False, 15)
        self.main_box.pack_start(ipv4, False, False)
        self.main_box.pack_start(ppp, False, False, 15)

class Wired(gtk.VBox):
    ENTRY_WIDTH = 222
    LEFT_PADDING = 210
    def __init__(self, connection, set_button, settings_obj=None):
        gtk.VBox.__init__(self)
        self.tab_name = _("Wired")
        self.set_button = set_button
        # 新增settings_obj变量，用于访问shared_methods.Settings对象
        self.settings_obj = settings_obj
        
        ethernet_setting = connection.get_setting("802-3-ethernet")

        table = gtk.Table(3, 2, False)
        
        mac_address = Label(_("Device Mac Address:"),
                            text_size=CONTENT_FONT_SIZE,
                            enable_select=False,
                            enable_double_click=False)
        mac_address.set_can_focus(False)

        self.mac_entry = InputEntry()

        clone_addr = Label(_("Cloned Mac Address:"),
                           text_size=CONTENT_FONT_SIZE,
                           enable_select=False,
                           enable_double_click=False)
        clone_addr.set_can_focus(False)
        self.clone_entry = InputEntry()

        mtu = Label("MTU:", 
                    text_size=CONTENT_FONT_SIZE,
                    enable_select=False,
                    enable_double_click=False)
        mtu.set_can_focus(False)
        self.mtu_spin = SpinBox(0,0, 1500, 1, self.ENTRY_WIDTH)
        
        '''
        Park table
        '''
        table.attach(style.wrap_with_align(mac_address, width=self.LEFT_PADDING), 0, 1, 0, 1)
        table.attach(style.wrap_with_align(self.mac_entry), 1, 2, 0, 1)
        table.attach(style.wrap_with_align(clone_addr, width=self.LEFT_PADDING), 0, 1, 1, 2)
        table.attach(style.wrap_with_align(self.clone_entry), 1,2, 1, 2)
        table.attach(style.wrap_with_align(mtu, width=self.LEFT_PADDING), 0,1,2,3)
        table.attach(style.wrap_with_align(self.mtu_spin), 1,2,2,3)

        # TODO UI change
        style.draw_background_color(self)
        #align = style.set_box_with_align(table, "text")
        #self.add(align)
        style.set_table(table)
        table_align = gtk.Alignment(0, 0, 0, 0)
        default_button = DefaultToggle(_("Default Setting"))
        default_button.load([table])
        table_align.add(default_button)
        self.pack_start(table_align, False, False)

        self.mac_entry.set_size(222, 22)
        self.clone_entry.set_size(222, 22)
        ## retrieve wired info
        self.mac_entry.entry.connect("changed", self.save_settings, "mac_address")
        self.clone_entry.entry.connect("changed", self.save_settings, "cloned_mac_address")
        self.mtu_spin.connect("value_changed", self.save_settings, "mtu")

        (mac, clone_mac, mtu) = ethernet_setting.mac_address, ethernet_setting.cloned_mac_address, ethernet_setting.mtu
        #print mac, clone_mac, mtu
        if mac != None:
            self.mac_entry.set_text(mac)
        if clone_mac !=None:
            self.clone_entry.set_text(clone_mac)
        if mtu != None:
            self.mtu_spin.set_value(int(mtu))

    def save_settings(self, widget, value, types):
        if type(value) is str:
            if TypeConvert.is_valid_mac_address(value):
                setattr(self.ethernet, types, value)
                if self.connection.check_setting_finish():
                    Dispatcher.set_button("save", True)
            else:
                Dispatcher.set_button("save", False)
                if value is "":
                    #delattr(self.ethernet, types)
                    Dispatcher.set_button("save", True)
        else:
            setattr(self.ethernet, types, value)
            if self.connection.check_setting_finish():
                Dispatcher.set_button("save", True)

class DSLConf(gtk.VBox):
    LEFT_PADDING = 210

    def __init__(self, connection, set_button_callback=None, settings_obj=None):
        gtk.VBox.__init__(self)
        self.tab_name = _("DSL")
        self.connection = connection
        self.set_button = set_button_callback
        # 新增settings_obj变量，用于访问shared_methods.Settings对象
        self.settings_obj = settings_obj
        self.dsl_setting = self.connection.get_setting("pppoe")

        # UI
        dsl_table = gtk.Table(5, 3, False)
        ssid_label = Label(_("Setting Name:"),
                               text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        ssid_label.set_can_focus(False)

        username_label = Label(_("Username:"),
                               text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        username_label.set_can_focus(False)


        service_label = Label(_("Service:"), 
                              text_size=CONTENT_FONT_SIZE,
                              enable_select=False,
                              enable_double_click=False)
        service_label.set_can_focus(False)
        password_label = Label(_("Password:"),
                               text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        password_label.set_can_focus(False)

        #pack labels
        dsl_table.attach(style.wrap_with_align(ssid_label, width=self.LEFT_PADDING), 0, 1 , 0, 1)
        dsl_table.attach(style.wrap_with_align(username_label, width=self.LEFT_PADDING), 0, 1 , 1, 2)
        dsl_table.attach(style.wrap_with_align(service_label, width=self.LEFT_PADDING), 0, 1, 2, 3)
        dsl_table.attach(style.wrap_with_align(password_label, width=self.LEFT_PADDING), 0, 1, 3, 4)

        # entries
        self.ssid_entry = InputEntry()
        self.ssid_entry.set_size(220 ,22)
        self.username_entry = InputEntry()
        self.username_entry.set_size(220 ,22)
        self.service_entry = InputEntry()
        self.service_entry.set_size(220 ,22)
        self.password_entry = PasswordEntry()
        self.password_entry.set_size(220 ,22)
        self.show_password = CheckButton(_("Show Password"), font_size=CONTENT_FONT_SIZE, padding_x=0)
        def show_password(widget):
            if widget.get_active():
                self.password_entry.show_password(True)
            else:
                self.password_entry.show_password(False)
        self.show_password.connect("toggled", show_password)

        #pack entries
        dsl_table.attach(style.wrap_with_align(self.ssid_entry, align="left"), 1, 3, 0, 1)
        dsl_table.attach(style.wrap_with_align(self.username_entry, align="left"), 1, 3, 1, 2)
        dsl_table.attach(style.wrap_with_align(self.service_entry, align="left"), 1, 3, 2, 3)
        dsl_table.attach(style.wrap_with_align(self.password_entry, align="left"), 1, 3, 3, 4)
        dsl_table.attach(style.wrap_with_align(self.show_password, align="left"), 1, 3, 4, 5)

        # TODO UI change
        style.draw_background_color(self)
        #align = style.set_box_with_align(dsl_table, "text")
        style.set_table(dsl_table)
        # just make table postion looks right
        table_align = gtk.Alignment(0, 0, 0, 0)
        table_align.add(dsl_table)
        self.pack_start(table_align, False, False)
        #self.add(align)
        self.show_all()
        self.refresh()

        self.ssid_entry.entry.connect("changed", self.save_changes, "ssid")
        self.username_entry.entry.connect("changed", self.save_changes, "username")
        self.service_entry.entry.connect("changed", self.save_changes, "service")
        self.password_entry.entry.connect("changed", self.save_changes, "password")

    def refresh(self):
        #print ">>>",self.connection.settings_dict
        # get dsl settings
        ssid = self.connection.get_setting("connection").id
        if type(self.connection) == NMRemoteConnection:
            self.ssid_entry.set_text(ssid)
        username = self.dsl_setting.username
        service = self.dsl_setting.service
        (setting_name, method) = self.connection.guess_secret_info() 
        try:
            password = nm_module.secret_agent.agent_get_secrets(self.connection.object_path,
                                                    setting_name,
                                                    method)
        except:
            password = ""
        # check if empty
        if username == None:
            username = ""
        if service == None:
            service = ""
        if password == None:
            password = ""
        # fill entry
        self.username_entry.entry.set_text(str(username))
        self.service_entry.entry.set_text(str(service))
        self.password_entry.entry.set_text(str(password))
        setattr(self.dsl_setting, "password", str(password))

    def save_changes(self, widget, value, types):
        if types == "ssid":
            self.connection.get_setting("connection").id = value
        else:
            if value:
                setattr(self.dsl_setting, types, value)
            else:
                delattr(self.dsl_setting, types)
        #check_settings(self.connection, self.set_button)
        ############
        is_valid = self.connection.check_setting_finish()
        self.settings_obj.dsl_is_valid = is_valid
        self.settings_obj.set_button("save", is_valid)

class PPPConf(gtk.VBox):
    TABLE_WIDTH = 1
    def __init__(self, connection, set_button_callback, settings_obj=None):
        gtk.VBox.__init__(self)
        self.tab_name = _("PPP")
        self.connection = connection
        self.set_button = set_button_callback
        # 新增settings_obj变量，用于访问shared_methods.Settings对象
        self.settings_obj = settings_obj
        self.ppp_setting = self.connection.get_setting("ppp")

        

        self.method_title = TitleBar(None,
                                     _("Configure Method"),
                                     width=self.TABLE_WIDTH,
                                     has_separator=False)

        self.method_table = TableAsm()
        self.method_table.row_attach(self.method_title)
        self.refuse_eap = self.method_table.row_toggle(_("EAP"))
        self.refuse_pap = self.method_table.row_toggle(_("PAP"))
        self.refuse_chap = self.method_table.row_toggle(_("CHAP"))
        self.refuse_mschap = self.method_table.row_toggle(_("MSCHAP"))
        self.refuse_mschapv2 = self.method_table.row_toggle(_("MSCHAP v2"))
        
        # visible settings

        self.compression_title = TitleBar(None,
                                          _("Compression"),
                                          width=self.TABLE_WIDTH,
                                          has_separator=False)
        self.echo_title = TitleBar(None,
                                   _("Echo"),
                                   width=self.TABLE_WIDTH,
                                   has_separator=False)

        self.comp_table = TableAsm()
        self.sub_item = []

        #compressio))n = Label(_("Compression"), text_size=TITLE_FONT_SIZE)
        self.comp_table.row_attach(self.compression_title)
        self.require_mppe = self.comp_table.row_toggle(_("Use point-to-point encryption(mppe)"))
        self.require_mppe_128 = self.comp_table.row_toggle(_("Require 128-bit encryption"), self.sub_item)
        self.mppe_stateful = self.comp_table.row_toggle(_("Use stataful MPPE"), self.sub_item)
        self.nobsdcomp = self.comp_table.row_toggle(_("Allow BSD data Compression"))
        self.nodeflate = self.comp_table.row_toggle(_("Allow Deflate date compression"))
        self.no_vj_comp = self.comp_table.row_toggle(_("Use TCP header compression"))

        self.echo_table = TableAsm()
        self.echo_table.row_attach(self.echo_title)
        self.ppp_echo = self.echo_table.row_toggle(_("Send PPP echo packets"))

        #compression_list = ["require_mppe_label", "require_mppe",
                            #"require_mppe_128_label", "require_mppe_128",
                            #"mppe_stateful_label", "mppe_stateful",
                            #"nobsdcomp_label", "nobsdcomp",
                            #"nodeflate_label", "nodeflate",
                            #"no_vj_comp_label", "no_vj_comp"]

        #echo_list = ["ppp_echo_label","ppp_echo"]
        #methods_list = ["refuse_eap", "refuse_eap_label",
                        #"refuse_pap", "refuse_pap_label",
                        #"refuse_chap", "refuse_chap_label",
                        #"refuse_mschap", "refuse_mschap_label",
                        #"refuse_mschapv2", "refuse_mschapv2_label"]

        #for name in (compression_list+echo_list+methods_list):
            #widget = getattr(self, name)
            #align = style.wrap_with_align(widget)
            #setattr(self, name + "_align", align)

        self.method_table.table_build()
        self.echo_table.table_build()
        vbox = gtk.VBox()
        table_align = gtk.Alignment(0, 0, 0, 0)
        
        #default_button = DefaultToggle(_("Default Setting"))
        #default_button.load([self.method_table, self.comp_table, self.echo_table])
        #table_align.add(default_button)
        table_align.add(vbox)
        self.pack_start(table_align)
        vbox.pack_start(self.method_table, False, False)
        vbox.pack_start(self.comp_table, False, False)
        vbox.pack_start(self.echo_table, False, False)
        #self.method_table.set_col_spacing(0, 10)
        #self.method_table.set_row_spacing(6, 20)
        #self.method_table.set_row_spacing(8, 20)
        #align = style.set_box_with_align(vbox, "text")
        #self.add_with_viewport(align)
        #style.draw_background_color(align)

        self.refresh()

        self.refuse_eap.connect("toggled", self.check_button_cb, "refuse_eap")
        self.refuse_pap.connect("toggled", self.check_button_cb, "refuse_pap")
        self.refuse_chap.connect("toggled", self.check_button_cb, "refuse_chap")
        self.refuse_mschap.connect("toggled", self.check_button_cb, "refuse_mschap")
        self.refuse_mschapv2.connect("toggled", self.check_button_cb, "refuse_mschapv2")
        self.require_mppe.connect("toggled", self.check_button_cb, "require_mppe")
        self.require_mppe_128.connect("toggled", self.check_button_cb, "require_mppe_128")
        self.mppe_stateful.connect("toggled", self.check_button_cb,"mppe_stateful")
        self.nobsdcomp.connect("toggled", self.check_button_cb, "nobsdcomp")
        self.nodeflate.connect("toggled", self.check_button_cb, "nodeflate")
        self.no_vj_comp.connect("toggled", self.check_button_cb, "no_vj_comp")
        self.ppp_echo.connect("toggled", self.check_button_cb, "echo")


    def refresh_table(self, require_mppe):
        self.comp_table.table_clear()
        if require_mppe:
            self.comp_table.table_build(self.sub_item, 2)
        else:
            self.comp_table.table_build()
            self.require_mppe_128.set_active(False)
            self.mppe_stateful.set_active(False)
        self.show_all()

    #def refresh_table(self, require_mppe):
        #container_remove_all(self.method_table)
        #self.method_table.attach(self.compression_title, 0, 3, 0 ,1)
        #self.method_table.attach(self.require_mppe_label_align, 0, 2, 1, 2, xpadding=10)
        #if require_mppe:
            #self.method_table.attach(self.require_mppe_128_label_align, 0, 2, 2, 3, xpadding=10)
            #self.method_table.attach(self.mppe_stateful_label_align, 0, 2, 3, 4, xpadding=10)
            #self.method_table.attach(self.require_mppe_128_align, 2, 3, 2, 3)
            #self.method_table.attach(self.mppe_stateful_align, 2, 3, 3, 4) 

        #else:
            #self.require_mppe_128.set_active(False)
            #self.mppe_stateful.set_active(False)

        #self.method_table.attach(self.nobsdcomp_label_align, 0, 2, 4, 5, xpadding=10)
        #self.method_table.attach(self.nodeflate_label_align, 0, 2, 5, 6, xpadding=10)
        #self.method_table.attach(self.no_vj_comp_label_align, 0, 2, 6, 7, xpadding=10)

        #self.method_table.attach(self.echo_title, 0, 3, 7, 8)
        ##self.method_table.attach(style.wrap_with_align(echo), 1, 2, 7, 8)
        #self.method_table.attach(self.ppp_echo_label_align, 1, 2, 8, 9, xpadding=10)

        #self.method_table.attach(self.require_mppe_align, 2, 3, 1, 2)
        #self.method_table.attach(self.nobsdcomp_align, 2, 3, 4, 5)
        #self.method_table.attach(self.nodeflate_align, 2, 3, 5, 6)
        #self.method_table.attach(self.no_vj_comp_align, 2, 3, 6, 7)
        #self.method_table.attach(self.ppp_echo_align, 2, 3, 8, 9)
        #self.method_table.attach(self.method_title, 0, 3, 9, 10)
        ##self.method_table.attach(style.wrap_with_align(self.method_label), 1, 2, 9, 10)
        #self.method_table.attach(self.refuse_eap_label_align, 1, 2, 10, 11, xpadding=10)
        #self.method_table.attach(self.refuse_pap_label_align, 1, 2, 11, 12, xpadding=10)
        #self.method_table.attach(self.refuse_chap_label_align, 1, 2, 12, 13, xpadding=10)
        #self.method_table.attach(self.refuse_mschap_label_align, 1, 2, 13, 14, xpadding=10)
        #self.method_table.attach(self.refuse_mschapv2_label_align, 1, 2, 14, 15, xpadding=10)

        #self.method_table.attach(self.refuse_eap_align, 2, 3, 10, 11, )
        #self.method_table.attach(self.refuse_pap_align, 2, 3, 11, 12, )
        #self.method_table.attach(self.refuse_chap_align, 2, 3, 12, 13, )
        #self.method_table.attach(self.refuse_mschap_align, 2, 3, 13, 14, )
        #self.method_table.attach(self.refuse_mschapv2_align, 2, 3, 14, 15, )
        #self.method_table.show_all()


    def refresh(self):
        #=========================
        # retreieve settings
        refuse_eap = self.ppp_setting.refuse_eap
        refuse_pap = self.ppp_setting.refuse_pap
        refuse_chap = self.ppp_setting.refuse_chap
        refuse_mschap = self.ppp_setting.refuse_mschap
        refuse_mschapv2 = self.ppp_setting.refuse_mschapv2

        require_mppe = self.ppp_setting.require_mppe
        require_mppe_128 = self.ppp_setting.require_mppe_128
        mppe_stateful = self.ppp_setting.mppe_stateful

        nobsdcomp = self.ppp_setting.nobsdcomp
        nodeflate = self.ppp_setting.nodeflate
        no_vj_comp = self.ppp_setting.no_vj_comp

        lcp_echo_failure = self.ppp_setting.lcp_echo_failure
        lcp_echo_interval = self.ppp_setting.lcp_echo_interval

        self.refuse_eap.set_active( not refuse_eap)
        self.refuse_pap.set_active(not refuse_pap)
        self.refuse_chap.set_active(not refuse_chap)
        self.refuse_mschap.set_active(not refuse_mschap)
        self.refuse_mschapv2.set_active(not refuse_mschapv2)

        self.require_mppe.set_active(require_mppe)
        self.require_mppe_128.set_active(require_mppe_128)
        # FIXME umcomment it when backend ready
        self.mppe_stateful.set_active(mppe_stateful)
        self.nobsdcomp.set_active(not nobsdcomp)
        self.nodeflate.set_active(not nodeflate)
        self.no_vj_comp.set_active(not no_vj_comp)

        if lcp_echo_failure == None and lcp_echo_interval == None:
            self.ppp_echo.set_active(False)
        else:
            self.ppp_echo.set_active(True)

        self.refresh_table(require_mppe)
        #==================================

    def check_button_cb(self, widget, key):
        active = widget.get_active()
        if key.startswith("refuse"):
            if active:
                setattr(self.ppp_setting, key, False)
            else:
                setattr(self.ppp_setting, key, True)
        elif key.startswith("no"):
            if active:
                setattr(self.ppp_setting, key, False)
            else:
                setattr(self.ppp_setting, key, True)
        elif key is "echo":
            if active:
                setattr(self.ppp_setting, "lcp_echo_failure", 5)
                setattr(self.ppp_setting, "lcp_echo_interval", 30)
            else:
                setattr(self.ppp_setting, "lcp_echo_failure", 0)
                setattr(self.ppp_setting, "lcp_echo_interval", 0)
        else:
            if active:
                setattr(self.ppp_setting, key, True)
            else:
                setattr(self.ppp_setting, key, False)
        #check_settings(self.connection, self.set_button)
        ##################
        is_valid = self.connection.check_setting_finish()
        self.settings_obj.ppp_is_valid = is_valid
        self.settings_obj.set_button("save", is_valid)

        if key is "require_mppe":
            if active:
                self.refresh_table(1)
            else:
                self.refresh_table(None)
