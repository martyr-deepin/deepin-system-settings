#!/usr/bin/env python
#-*- coding:utf-8 -*-

from theme import app_theme

from dtk.ui.tab_window import TabBox
from dtk.ui.button import Button,  CheckButton, RadioButton
from dtk.ui.new_entry import InputEntry, PasswordEntry
from dtk.ui.label import Label
from dtk.ui.utils import container_remove_all
from dtk.ui.new_treeview import TreeView
#from dtk.ui.droplist import Droplist
#from widgets import SettingButton
from dtk.ui.scrolled_window import ScrolledWindow
from settings_widget import SettingItem, EntryTreeView, AddSettingItem
# NM lib import 
from nm_modules import nm_module
from nmlib.nmcache import cache
from nmlib.nm_remote_connection import NMRemoteConnection
#from nmlib.nmclient import nmclient
#from nmlib.nm_remote_settings import nm_remote_settings
from container import MyToggleButton as SwitchButton
from container import TitleBar
from shared_widget import IPV4Conf

import gtk
from nls import _
import style
from constants import FRAME_VERTICAL_SPACING, CONTENT_FONT_SIZE, TITLE_FONT_SIZE
#from container import MyRadioButton as RadioButton

slider = nm_module.slider
class VPNSetting(gtk.Alignment):

    def __init__(self, slide_back_cb=None, change_crumb_cb=None, module_frame=None):

        gtk.Alignment.__init__(self)
        self.slide_back = slide_back_cb
        self.change_crumb = change_crumb_cb
        self.module_frame = module_frame
        
        # Add UI Align
        style.set_main_window(self)
        hbox = gtk.HBox()
        self.add(hbox)
        self.pptp = None
        self.ipv4 = None

        self.tab_window = TabBox()
        self.tab_window.draw_title_background = self.draw_tab_title_background
        self.tab_window.set_size_request(674, 408)
        self.items = [(_("PPTP"), NoSetting()),
                      (_("IPv4 Setting"), NoSetting())]
        self.tab_window.add_items(self.items)
        self.sidebar = SideBar( None, self.init, self.check_click)

        # Build ui
        hbox.pack_start(self.sidebar, False , False)
        vbox = gtk.VBox()
        vbox.pack_start(self.tab_window ,True, True)
        hbox.pack_start(vbox, True, True)
        self.save_button = Button("Save")
        button_box = gtk.HBox()
        button_box.add(self.save_button)
        self.save_button.connect("clicked", self.save_changes)

        buttons_aligns = gtk.Alignment(0.5 , 1, 0, 0)
        buttons_aligns.add(button_box)
        vbox.pack_start(buttons_aligns, False , False)

        style.draw_background_color(self)
        style.draw_separator(self.sidebar, 3)

    def draw_tab_title_background(self, cr, widget):
        rect = widget.allocation
        cr.set_source_rgb(1, 1, 1)    
        cr.rectangle(0, 0, rect.width, rect.height - 1)
        cr.fill()
        
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

    def init(self, new_connection=None, init_connection=False):
        # Get all connections  
        connections = nm_module.nm_remote_settings.get_vpn_connections()
        
        if init_connection:
            for connection in connections:
                connection.init_settings_prop_dict()
        # Check connections
        if connections == []:
            # Create a new connection
            connect = nm_module.nm_remote_settings.new_vpn_pptp_connection()
            connections.append(connect)

        if new_connection:
            connections += new_connection
        else:
            self.sidebar.new_connection_list = []

        self.ipv4_setting = [IPV4Conf(con, self.set_button, dns_only=True) for con in connections]
        self.pptp_setting = [PPTPConf(con, self.module_frame, self.set_button) for con in connections]

        self.sidebar.init(connections, self.ipv4_setting)
        index = self.sidebar.get_active()
        self.ipv4 = self.ipv4_setting[index]
        self.pptp = self.pptp_setting[index]
        #self.dsl = NoSetting()
        #self.ppp = NoSetting()

        self.init_tab_box()

    def init_tab_box(self):
        self.tab_window.tab_items[1] = (_("IPv4 Setting"),self.ipv4)
        self.tab_window.tab_items[0] = (_("PPTP"), self.pptp)
        tab_index = self.tab_window.tab_index
        self.tab_window.tab_index = -1
        self.tab_window.switch_content(tab_index)
        self.queue_draw()

    def check_click(self, connection):
        index = self.sidebar.get_active()
        self.ipv4 = self.ipv4_setting[index]
        self.pptp = self.pptp_setting[index]

        self.init_tab_box()

    def set_button(self, name, state):
        if name == "save":
            self.save_button.set_label(name)
            self.save_button.set_sensitive(state)
        else:
            self.save_button.set_label("connect")
            self.save_button.set_sensitive(state)
        
    def save_changes(self, widget):
        print "saving"
        if widget.label == "save":
            connection = self.ipv4.connection
            if isinstance(connection, NMRemoteConnection):
                connection.update()
            else:
                nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'vpn')
                index = self.sidebar.new_connection_list.index(connection)
                self.sidebar.new_connection_list.pop(index)
                self.init(self.sidebar.new_connection_list)
            self.set_button("apply", True)
        else:
            self.apply_changes()

    def apply_changes(self):
        connection = self.ipv4.connection
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
        gtk.VBox.__init__(self, False)
        self.connections = connections
        self.main_init_cb = main_init_cb
        self.check_click_cb = check_click_cb

        # Build ui
        self.buttonbox = gtk.VBox(False)
        self.pack_start(self.buttonbox, False, False)
        style.add_separator(self)
        add_button = AddSettingItem(_("New Connection"),self.add_new_connection)
        self.pack_start(TreeView([add_button]), False, False)
        self.set_size_request(180, -1)

        self.new_connection_list = []
    
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
        new_connection = nm_module.nm_remote_settings.new_vpn_pptp_connection()
        self.new_connection_list.append(new_connection)
        self.main_init_cb(self.new_connection_list)

class NoSetting(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)

        label_align = gtk.Alignment(0.5,0.5,0,0)

        label = Label("No connection available")
        label_align.add(label)
        self.add(label_align)

class PPTPConf(gtk.VBox):
    ENTRY_WIDTH = 222
    def __init__(self, connection, module_frame, set_button_callback=None):
        gtk.VBox.__init__(self)
        self.connection = connection
        self.module_frame = module_frame
        self.set_button = set_button_callback
        self.vpn_setting = self.connection.get_setting("vpn")

        # UI
        pptp_table = gtk.Table(7, 4, False)
        gateway_label = Label(_("Gateway:"))
        user_label = Label(_("Username:"))
        password_label = Label(_("Password:"))
        nt_domain_label = Label(_("NT Domain:"))
        # Radio Button
        self.pptp_radio = RadioButton(_("PPTP"))
        self.l2tp_radio = RadioButton(_("L2TP"))
        radio_box = gtk.HBox(spacing=30)
        radio_box.pack_start(self.pptp_radio, False, False)
        radio_box.pack_start(self.l2tp_radio, False, False)
        #pack labels
        pptp_table.attach(style.wrap_with_align(radio_box, align="left"), 2,4, 0, 1)
        pptp_table.attach(style.wrap_with_align(gateway_label), 0, 2 , 1, 2)
        pptp_table.attach(style.wrap_with_align(user_label), 0, 2, 2, 3)
        pptp_table.attach(style.wrap_with_align(password_label), 0, 2, 3, 4)
        pptp_table.attach(style.wrap_with_align(nt_domain_label), 0, 2, 5, 6)

        # entries
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
        pptp_table.attach(style.wrap_with_align(self.gateway_entry), 2, 4, 1, 2)
        pptp_table.attach(style.wrap_with_align(self.user_entry), 2, 4, 2, 3)
        pptp_table.attach(style.wrap_with_align(self.password_entry), 2, 4, 3, 4)
        pptp_table.attach(style.wrap_with_align(self.password_show, align="left"), 2, 4, 4, 5)
        pptp_table.attach(style.wrap_with_align(self.nt_domain_entry), 2, 4, 5, 6)
        # Advance setting button
        advanced_button = Button(_("Advanced Setting"))
        advanced_button.connect("clicked", self.advanced_button_click)

        pptp_table.attach(style.wrap_with_align(advanced_button), 3, 4, 6, 7)
        self.service_type = self.vpn_setting.service_type.split(".")[-1]
        if self.service_type == "l2tp":
            self.l2tp_radio.set_active(True)
        else:
            self.pptp_radio.set_active(True)
        self.pptp_radio.connect("toggled",self.radio_toggled, "pptp")
        self.l2tp_radio.connect("toggled",self.radio_toggled, "l2tp")
        # set signals

        align = style.set_box_with_align(pptp_table, "text")
        #style.set_table_items(pptp_table, "entry")
        style.draw_background_color(self)
        style.set_table(pptp_table)
        self.add(align)
        self.show_all()
        self.refresh()
        self.gateway_entry.entry.connect("changed", self.entry_changed, "gateway")
        self.user_entry.entry.connect("changed", self.entry_changed, "user")
        self.password_entry.entry.connect("changed", self.entry_changed, "password")
        self.nt_domain_entry.entry.connect("changed", self.entry_changed, "domain")

    def refresh(self):
        #print ">>>",self.vpn_setting.data
        #print self.vpn_setting.data
        gateway = self.vpn_setting.get_data_item("gateway")
        user = self.vpn_setting.get_data_item("user")
        domain = self.vpn_setting.get_data_item("domain")

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
        if text:
            if item == "password":
                self.vpn_setting.set_secret_item(item, text)
            else:
                self.vpn_setting.set_data_item(item, text)
            
        else:
            if item == "password":
                self.vpn_setting.delete_secret_item(item)
            else:
                self.vpn_setting.delete_data_item(item)

        if self.connection.check_setting_finish():
            self.set_button("save", True)
        else:
            self.set_button("save", False)
    
    def radio_toggled(self, widget, service_type):
        if widget.get_active():
            self.vpn_setting.service_type = "org.freedesktop.NetworkManager." + service_type
            self.service_type = service_type
            self.refresh()

    def advanced_button_click(self, widget):
        ppp = PPPConf(self.module_frame, self.set_button)
        ppp.refresh(self.connection)
        self.module_frame.send_submodule_crumb(3, _("高级设置"))
        nm_module.slider.slide_to_page(ppp, "right")
        #pass

class PPPConf(ScrolledWindow):
    ENTRY = 0
    OFFBUTTON = 1

    TABLE_WIDTH = 150
    def __init__(self, module_frame, set_button_callback):
        ScrolledWindow.__init__(self)
        
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.set_button = set_button_callback
        self.module_frame = module_frame
        
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
        
        self.method_table = gtk.Table(23, 3, False)

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
        self.nopcomp_label = Label(_("Use protocal field compression negotiation"), text_size=CONTENT_FONT_SIZE)
        self.noaccomp_label = Label(_("Use Address/Control compression"), text_size=CONTENT_FONT_SIZE)

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
        self.ipsec_title = TitleBar(app_theme.get_pixbuf("network/validation.png"),
                                     _("IPSec Setting"), width=self.TABLE_WIDTH)

        self.ip_sec_enable_label = Label(_("Enable IPSec tunnel to l2tp host"), text_size=CONTENT_FONT_SIZE)
        self.group_name_label = Label(_("Group Name:"), text_size=CONTENT_FONT_SIZE)
        self.gateway_id_label = Label(_("Gateway ID:"), text_size=CONTENT_FONT_SIZE)
        self.pre_shared_key_label = Label(_("Pre_Shared_key"), text_size=CONTENT_FONT_SIZE)
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
                align = style.wrap_with_align(widget, width=self.TABLE_WIDTH)
            else:
                align = style.wrap_with_align(widget)

            setattr(self, name + "_align", align)

        vbox = gtk.VBox()
        vbox.pack_start(self.method_table, False, False)
        self.method_table.set_row_spacing(5, 20)
        self.method_table.set_row_spacing(15, 20)
        self.method_table.set_row_spacing(18, 20)
        align = style.set_box_with_align(vbox, "text")
        self.add_with_viewport(align)
        style.draw_background_color(align)


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
        self.group_name.entry.connect("focus-out-event", self.entry_focus_out_cb, "ipsec-group-name")
        self.gateway_id.entry.connect("focus-out-event", self.entry_focus_out_cb, "ipsec-gataway-id")
        self.pre_shared_key.entry.connect("focus-out-event", self.entry_focus_out_cb, "ipsec-psk")
        self.group_name.entry.connect("changed", self.entry_changed_cb, "ipsec-group-name")
        self.gateway_id.entry.connect("changed", self.entry_changed_cb, "ipsec-gateway-id")
        self.pre_shared_key.entry.connect("changed", self.entry_changed_cb, "ipsec-psk")

    def init_ui(self):

        self.service_type = self.vpn_setting.service_type.split(".")[-1]
        def table_attach(widget_name, row, padding=0):
            label = getattr(self, widget_name + "_label_align")
            widget = getattr(self, widget_name + "_align")
            self.method_table.attach(label, 0, 2, row, row + 1, xpadding=10)
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
        print self.connection.object_path
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
        if text:
            self.vpn_setting.set_data_item(key, text)
        else:
            self.vpn_setting.delete_data_item(key)
    def entry_changed_cb(self, widget, string, key):
        if string == "":
            print key,"entry is empty"
            self.vpn_setting.delete_data_item(key)

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
        else:
            if active:
                self.vpn_setting.set_data_item(key, "yes")
            else:
                self.vpn_setting.delete_data_item(key)
    
    def click_mppe_callback(self, widget, key):
        active = widget.get_active()
        if active:
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
        nm_module,slider._slide_to_page("vpn", "left")
        
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
