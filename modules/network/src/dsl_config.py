#!/usr/bin/env python
#-*- coding:utf-8 -*-
#from theme import app_theme

from dss import app_theme
from dtk.ui.tab_window import TabBox
from dtk.ui.button import Button,CheckButton
from dtk.ui.new_entry import InputEntry, PasswordEntry
from dtk.ui.new_treeview import TreeView
from dtk.ui.label import Label
from dtk.ui.spin import SpinBox
from dtk.ui.utils import container_remove_all
from dtk.ui.scrolled_window import ScrolledWindow
#from dtk.ui.droplist import Droplist
#from widgets import SettingButton
from settings_widget import SettingItem, EntryTreeView, AddSettingItem
# NM lib import 
from nmlib.nm_utils import TypeConvert
from nm_modules import nm_module
#from nmlib.nmclient import nmclient
#from nmlib.nm_remote_settings import nm_remote_settings
from container import MyToggleButton as SwitchButton
from foot_box import FootBox
from container import TitleBar
from shared_widget import IPV4Conf

import gtk

from nls import _
# UI
import style
from constants import CONTENT_FONT_SIZE

def check_settings(connection, fn):
    if connection.check_setting_finish():
        fn('save', True)
    else:
        fn("save", False)

class DSLSetting(gtk.Alignment):

    def __init__(self, slide_back_cb=None, change_crumb_cb=None):
        gtk.Alignment.__init__(self)
        self.slide_back = slide_back_cb
        self.change_crumb = change_crumb_cb
        
        # Add UI Align
        style.set_main_window(self)
        main_vbox = gtk.VBox()
        self.foot_box = FootBox()
        hbox = gtk.HBox()
        hbox.connect("expose-event",self.expose_line)
        main_vbox.pack_start(hbox, False, False)
        main_vbox.pack_start(self.foot_box, False, False)

        self.add(main_vbox)

        self.wired = None
        self.ipv4 = None
        self.dsl = None
        self.ppp = None

        self.tab_window = TabBox()
        self.tab_window.draw_title_background = self.draw_tab_title_background
        self.tab_window.set_size_request(674, 415)
        self.items = [(_("DSL"), NoSetting()),
                      (_("Wired"), NoSetting()),
                      (_("IPv4 Setting"), NoSetting()),
                      (_("PPP"), NoSetting())]
        self.tab_window.add_items(self.items)
        self.sidebar = SideBar( None, self.init, self.check_click)

        # Build ui
        hbox.pack_start(self.sidebar, False , False)
        hbox.pack_start(self.tab_window ,True, True)
        self.save_button = Button()
        self.save_button.connect("clicked", self.save_changes)
        self.foot_box.set_buttons([self.save_button])

        style.draw_background_color(self)
        style.draw_separator(self.sidebar, 3)

    def expose_line(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        style.draw_out_line(cr, rect, exclude=["left", "right", "top"])
        
    def draw_tab_title_background(self, cr, widget):
        rect = widget.allocation
        cr.set_source_rgb(1, 1, 1)    
        cr.rectangle(0, 0, rect.width, rect.height - 1)
        cr.fill()
        
    def set_button(self, name, state):
        if name == "save":
            self.save_button.set_label(_("save"))
            self.save_button.set_sensitive(state)
        else:
            self.save_button.set_label(_("connect"))
            self.save_button.set_sensitive(state)

    def expose_outline(self, widget, event, exclude):
        cr = widget.window.cairo_create()
        rect = widget.allocation

        style.draw_out_line(cr, rect, exclude)

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb( 1, 1, 1) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

    def init(self, new_connection=None, init_connections=False):
        # Get all connections  
        connections = nm_module.nm_remote_settings.get_pppoe_connections()
        if init_connections:
            for con in connections:
                con.init_settings_prop_dict()
        # Check connections
        if new_connection:
            connections += new_connection
        else:
            self.sidebar.new_connection_list = []

        if connections == []:
            # Create a new connection
            connections = [nm_module.nm_remote_settings.new_pppoe_connection()]
            self.sidebar.new_connection_list.extend(connections)
        
        self.connections = connections

        self.wired_setting = [Wired(con) for con in connections]
        self.ipv4_setting = [IPV4Conf(con, self.set_button) for con in connections]
        self.dsl_setting = [DSLConf(con, self.set_button) for con in connections]
        self.ppp_setting = [PPPConf(con, self.set_button) for con in connections]

        self.sidebar.init(connections, self.ipv4_setting)
        index = self.sidebar.get_active()
        self.wired = self.wired_setting[index]
        self.ipv4 = self.ipv4_setting[index]
        self.dsl = self.dsl_setting[index]
        self.ppp = self.ppp_setting[index]
        #self.dsl = NoSetting()
        #self.ppp = NoSetting()

        self.init_tab_box()

    def init_tab_box(self):
        self.tab_window.tab_items[0] = (_("DSL"), self.dsl)
        self.tab_window.tab_items[1] = (_("Wired"),self.wired)
        self.tab_window.tab_items[2] = (_("IPv4 Setting"),self.ipv4)
        self.tab_window.tab_items[3] = (_("PPP"), self.ppp)
        tab_index = self.tab_window.tab_index
        self.tab_window.tab_index = -1
        self.tab_window.switch_content(tab_index)
        self.queue_draw()

    def check_click(self, connection):
        index = self.sidebar.get_active()
        self.wired = self.wired_setting[index]
        self.ipv4 = self.ipv4_setting[index]
        self.dsl = self.dsl_setting[index]
        self.ppp = self.ppp_setting[index]

        self.init_tab_box()
        
    def save_changes(self, widget):
        connection = self.dsl.connection
        if widget.label == _("save"):
            print "saving"
            if connection.check_setting_finish():

                this_index = self.connections.index(connection)
                from nmlib.nm_remote_connection import NMRemoteConnection
                if isinstance(connection, NMRemoteConnection):
                    print "before update", TypeConvert.dbus2py(connection.settings_dict)
                    connection.update()
                    print "after update", TypeConvert.dbus2py(connection.settings_dict)
                else:
                    print self.sidebar.new_connection_list
                    index = self.sidebar.new_connection_list.index(connection)
                    nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')
                    self.sidebar.new_connection_list.pop(index)
                    self.init(self.sidebar.new_connection_list)
                    # reset index
                    con = self.sidebar.connection_tree.visible_items[this_index]
                    self.sidebar.connection_tree.select_items([con])
            self.set_button("apply", True)
        else:
            device_path = nm_module.nmclient.get_wired_devices()[0].object_path
        #FIXME need to change device path into variables
            nm_module.nmclient.activate_connection_async(connection.object_path,
                                           device_path,
                                           "/")
            self.change_crumb()
            self.slide_back() 


class SideBar(gtk.VBox):
    def __init__(self, connections , main_init_cb, check_click_cb):
        gtk.VBox.__init__(self, False)
        self.connections = connections
        self.main_init_cb = main_init_cb
        self.check_click_cb = check_click_cb

        # Build ui
        self.buttonbox = gtk.VBox()
        self.pack_start(self.buttonbox, False, False)
        style.add_separator(self)
        add_button = AddSettingItem(_("New Connection"),self.add_new_connection)
        self.pack_start(TreeView([add_button]), False, False)

        self.set_size_request(160, -1)

        self.new_connection_list = []
    
    def init(self, connection_list, ip4setting):
        # check active
        wired_device = nm_module.nmclient.get_wired_devices()[0]
        active_connection = wired_device.get_active_connection()
        if active_connection:
            active = active_connection.get_connection()
        else:
            active = None

        self.connections = connection_list
        self.setting = ip4setting
        
        container_remove_all(self.buttonbox)
        cons = []
        self.connection_tree = EntryTreeView(cons)
        for index, connection in enumerate(self.connections):
            cons.append(SettingItem(connection, self.setting[index], self.check_click_cb, self.delete_item_cb))
        self.connection_tree.add_items(cons)

        self.connection_tree.show_all()

        self.buttonbox.pack_start(self.connection_tree, False, False)

        try:
            index = self.connections.index(active)
            this_connection = self.connection_tree.visible_items[index]
            this_connection.set_active(True)
            self.connection_tree.select_items([this_connection])
        except ValueError:
            self.connection_tree.select_first_item()
        if self.new_connection_list:
            connect = self.connection_tree.visible_items[-1]
            self.connection_tree.select_items([connect])

    def delete_item_cb(self, connection):
        from nmlib.nm_remote_connection import NMRemoteConnection
        self.connection_tree.delete_select_items()
        if isinstance(connection, NMRemoteConnection):
            connection.delete()
        else:
            index = self.new_connection_list.index(connection)
            self.new_connection_list.pop(index)
        
        if len(self.connection_tree.visible_items) == 0:
            container_remove_all(self.buttonbox)
        else:
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
    
    def add_new_connection(self):
        connection = nm_module.nm_remote_settings.new_pppoe_connection()
        self.new_connection_list.append(connection)
        self.main_init_cb(new_connection=self.new_connection_list)


class NoSetting(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)

        label_align = gtk.Alignment(0.5,0.5,0,0)

        label = Label("No active connection")
        label_align.add(label)
        self.add(label_align)

class Wired(gtk.VBox):
    ENTRY_WIDTH = 222
    def __init__(self, connection):
        gtk.VBox.__init__(self)
        
        ethernet_setting = connection.get_setting("802-3-ethernet")

        table = gtk.Table(3, 2, False)
        
        mac_address = Label(_("Device Mac Address:"), text_size=CONTENT_FONT_SIZE)

        self.mac_entry = InputEntry()

        clone_addr = Label(_("Cloned Mac Address:"), text_size=CONTENT_FONT_SIZE)
        self.clone_entry = InputEntry()

        mtu = Label("MTU:", text_size=CONTENT_FONT_SIZE)
        self.mtu_spin = SpinBox(0,0, 1500, 1, self.ENTRY_WIDTH)
        
        '''
        Park table
        '''
        table.attach(style.wrap_with_align(mac_address), 0, 1, 0, 1)
        table.attach(style.wrap_with_align(self.mac_entry), 1, 2, 0, 1)
        table.attach(style.wrap_with_align(clone_addr), 0, 1, 1, 2)
        table.attach(style.wrap_with_align(self.clone_entry), 1,2, 1, 2)
        table.attach(style.wrap_with_align(mtu), 0,1,2,3)
        table.attach(style.wrap_with_align(self.mtu_spin), 1,2,2,3)

        # TODO UI change
        style.draw_background_color(self)
        align = style.set_box_with_align(table, "text")
        self.add(align)
        style.set_table(table)

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
                    self.set_button("save", True)
            else:
                self.set_button("save", False)
                if value is "":
                    #delattr(self.ethernet, types)
                    self.set_button("save", True)
        else:
            setattr(self.ethernet, types, value)
            if self.connection.check_setting_finish():
                self.set_button("save", True)

class DSLConf(gtk.VBox):

    def __init__(self, connection, set_button_callback=None):
        gtk.VBox.__init__(self)
        self.connection = connection
        self.set_button = set_button_callback
        self.dsl_setting = self.connection.get_setting("pppoe")

        # UI
        dsl_table = gtk.Table(4, 3, False)
        username_label = Label(_("Username:"), text_size=CONTENT_FONT_SIZE)
        service_label = Label(_("Service:"), text_size=CONTENT_FONT_SIZE)
        password_label = Label(_("Password:"), text_size=CONTENT_FONT_SIZE)
        #pack labels
        dsl_table.attach(style.wrap_with_align(username_label), 0, 1 , 0, 1)
        dsl_table.attach(style.wrap_with_align(service_label), 0, 1, 1, 2)
        dsl_table.attach(style.wrap_with_align(password_label), 0, 1, 2, 3)

        # entries
        self.username_entry = InputEntry()
        self.username_entry.set_size(220,22)
        self.service_entry = InputEntry()
        self.service_entry.set_size(220,22 )
        self.password_entry = PasswordEntry()
        self.password_entry.set_size(220, 22)
        self.show_password = CheckButton(_("Show Password"), font_size=CONTENT_FONT_SIZE, padding_x=0)
        def show_password(widget):
            if widget.get_active():
                self.password_entry.show_password(True)
            else:
                self.password_entry.show_password(False)
        self.show_password.connect("toggled", show_password)

        #pack entries
        dsl_table.attach(style.wrap_with_align(self.username_entry), 1, 3, 0, 1)
        dsl_table.attach(style.wrap_with_align(self.service_entry), 1, 3, 1, 2)
        dsl_table.attach(style.wrap_with_align(self.password_entry), 1, 3, 2, 3)
        dsl_table.attach(style.wrap_with_align(self.show_password, align="left"), 1,3,3,4)

        # TODO UI change
        style.draw_background_color(self)
        align = style.set_box_with_align(dsl_table, "text")
        style.set_table(dsl_table)
        self.add(align)
        self.show_all()
        self.refresh()


        self.username_entry.entry.connect("changed", self.save_changes, "username")
        self.service_entry.entry.connect("changed", self.save_changes, "service")
        self.password_entry.entry.connect("changed", self.save_changes, "password")

    def refresh(self):
        #print ">>>",self.connection.settings_dict
        # get dsl settings
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
        print types," dsl changed"
        if value:
            setattr(self.dsl_setting, types, value)
        else:
            delattr(self.dsl_setting, types)
        check_settings(self.connection, self.set_button)

class PPPConf(ScrolledWindow):
    TABLE_WIDTH = 300
    def __init__(self, connection, set_button_callback):
        ScrolledWindow.__init__(self)

        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        self.connection = connection
        self.set_button = set_button_callback
        self.ppp_setting = self.connection.get_setting("ppp")


        self.method_title = TitleBar(app_theme.get_pixbuf("network/validation.png"),
                                     _("Configure Method"), width=self.TABLE_WIDTH)

        self.refuse_eap_label = Label(_("EAP"), text_size=CONTENT_FONT_SIZE)
        self.refuse_pap_label = Label(_("PAP"), text_size=CONTENT_FONT_SIZE)
        self.refuse_chap_label = Label(_("CHAP"), text_size=CONTENT_FONT_SIZE)
        self.refuse_mschap_label = Label(_("MSCHAP"), text_size=CONTENT_FONT_SIZE)
        self.refuse_mschapv2_label = Label(_("MSCHAP v2"), text_size=CONTENT_FONT_SIZE)
        self.refuse_eap = SwitchButton()
        self.refuse_pap = SwitchButton()
        self.refuse_chap = SwitchButton()
        self.refuse_mschap = SwitchButton()
        self.refuse_mschapv2 = SwitchButton()
        
        self.method_table = gtk.Table(16, 3, False)

        # visible settings

        self.compression_title = TitleBar(app_theme.get_pixbuf("network/zip.png"),
                                          _("Compression"), width=self.TABLE_WIDTH)
        self.echo_title = TitleBar(app_theme.get_pixbuf("network/echo.png"),
                                          _("Echo"), width=self.TABLE_WIDTH)


        #compressio))n = Label(_("Compression"), text_size=TITLE_FONT_SIZE)
        self.require_mppe_label = Label(_("Use point-to-point encryption(mppe)"), text_size=CONTENT_FONT_SIZE)
        self.require_mppe_128_label = Label(_("Require 128-bit encryption"), text_size=CONTENT_FONT_SIZE)
        self.mppe_stateful_label = Label(_("Use stataful MPPE"), text_size=CONTENT_FONT_SIZE)
        self.nobsdcomp_label = Label(_("Allow BSD data Compression"), text_size=CONTENT_FONT_SIZE)
        self.nodeflate_label = Label(_("Allow Deflate date compression"), text_size=CONTENT_FONT_SIZE)
        self.no_vj_comp_label = Label(_("Use TCP header compression"), text_size=CONTENT_FONT_SIZE)
        #echo = Label("Echo", text_size=TITLE_FONT_SIZE)
        self.ppp_echo_label = Label(_("Send PPP echo packets"), text_size=CONTENT_FONT_SIZE)

        self.require_mppe = SwitchButton()
        self.require_mppe_128 = SwitchButton()
        self.mppe_stateful = SwitchButton()
        
        self.nobsdcomp = SwitchButton()
        self.nodeflate = SwitchButton()
        self.no_vj_comp = SwitchButton()
        self.ppp_echo = SwitchButton()

        compression_list = ["require_mppe_label", "require_mppe",
                            "require_mppe_128_label", "require_mppe_128",
                            "mppe_stateful_label", "mppe_stateful",
                            "nobsdcomp_label", "nobsdcomp",
                            "nodeflate_label", "nodeflate",
                            "no_vj_comp_label", "no_vj_comp"]

        echo_list = ["ppp_echo_label","ppp_echo"]
        methods_list = ["refuse_eap", "refuse_eap_label",
                        "refuse_pap", "refuse_pap_label",
                        "refuse_chap", "refuse_chap_label",
                        "refuse_mschap", "refuse_mschap_label",
                        "refuse_mschapv2", "refuse_mschapv2_label"]

        for name in (compression_list+echo_list+methods_list):
            widget = getattr(self, name)
            align = style.wrap_with_align(widget)
            setattr(self, name + "_align", align)

        vbox = gtk.VBox()
        vbox.pack_start(self.method_table, False, False)
        self.method_table.set_col_spacing(0, 10)
        self.method_table.set_row_spacing(6, 20)
        self.method_table.set_row_spacing(8, 20)
        align = style.set_box_with_align(vbox, "text")
        self.add_with_viewport(align)
        style.draw_background_color(align)

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
        container_remove_all(self.method_table)
        self.method_table.attach(self.compression_title, 0, 3, 0 ,1)
        self.method_table.attach(self.require_mppe_label_align, 0, 2, 1, 2, xpadding=10)
        if require_mppe:
            self.method_table.attach(self.require_mppe_128_label_align, 0, 2, 2, 3, xpadding=10)
            self.method_table.attach(self.mppe_stateful_label_align, 0, 2, 3, 4, xpadding=10)
            self.method_table.attach(self.require_mppe_128_align, 2, 3, 2, 3)
            self.method_table.attach(self.mppe_stateful_align, 2, 3, 3, 4) 

        else:
            self.require_mppe_128.set_active(False)
            self.mppe_stateful.set_active(False)

        self.method_table.attach(self.nobsdcomp_label_align, 0, 2, 4, 5, xpadding=10)
        self.method_table.attach(self.nodeflate_label_align, 0, 2, 5, 6, xpadding=10)
        self.method_table.attach(self.no_vj_comp_label_align, 0, 2, 6, 7, xpadding=10)

        self.method_table.attach(self.echo_title, 0, 3, 7, 8)
        #self.method_table.attach(style.wrap_with_align(echo), 1, 2, 7, 8)
        self.method_table.attach(self.ppp_echo_label_align, 1, 2, 8, 9, xpadding=10)

        self.method_table.attach(self.require_mppe_align, 2, 3, 1, 2)
        self.method_table.attach(self.nobsdcomp_align, 2, 3, 4, 5)
        self.method_table.attach(self.nodeflate_align, 2, 3, 5, 6)
        self.method_table.attach(self.no_vj_comp_align, 2, 3, 6, 7)
        self.method_table.attach(self.ppp_echo_align, 2, 3, 8, 9)
        self.method_table.attach(self.method_title, 0, 3, 9, 10)
        #self.method_table.attach(style.wrap_with_align(self.method_label), 1, 2, 9, 10)
        self.method_table.attach(self.refuse_eap_label_align, 1, 2, 10, 11, xpadding=10)
        self.method_table.attach(self.refuse_pap_label_align, 1, 2, 11, 12, xpadding=10)
        self.method_table.attach(self.refuse_chap_label_align, 1, 2, 12, 13, xpadding=10)
        self.method_table.attach(self.refuse_mschap_label_align, 1, 2, 13, 14, xpadding=10)
        self.method_table.attach(self.refuse_mschapv2_label_align, 1, 2, 14, 15, xpadding=10)

        self.method_table.attach(self.refuse_eap_align, 2, 3, 10, 11, )
        self.method_table.attach(self.refuse_pap_align, 2, 3, 11, 12, )
        self.method_table.attach(self.refuse_chap_align, 2, 3, 12, 13, )
        self.method_table.attach(self.refuse_mschap_align, 2, 3, 13, 14, )
        self.method_table.attach(self.refuse_mschapv2_align, 2, 3, 14, 15, )
        self.method_table.show_all()


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
        check_settings(self.connection, self.set_button)

        if key is "require_mppe":
            if active:
                self.refresh_table(1)
            else:
                self.refresh_table(None)
