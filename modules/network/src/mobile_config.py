#!/usr/bin/env python
#-*- coding:utf-8 -*-
from theme import app_theme, ui_theme

from dtk.ui.tab_window import TabBox
from dtk.ui.button import Button,CheckButton
from dtk.ui.new_entry import InputEntry, PasswordEntry
from dtk.ui.new_treeview import TreeView
from dtk.ui.label import Label
from dtk.ui.utils import container_remove_all
from dtk.ui.combo import ComboBox
from settings_widget import SettingItem, EntryTreeView, AddSettingItem
from nm_modules import nm_module
from container import Contain
from shared_widget import IPV4Conf

import gtk

from constants import TITLE_FONT_SIZE, FRAME_VERTICAL_SPACING
import style

slider = nm_module.slider

def check_settings(connection, fn):
    if connection.check_setting_finish():
        fn('save', True)
        print "pass"
    else:
        fn("save", False)
        print "not pass"

class MobileSetting(gtk.Alignment):

    def __init__(self, slide_back_cb = None, change_crumb_cb = None):

        gtk.Alignment.__init__(self, 0, 0, 0, 0)
        self.slide_back = slide_back_cb
        self.change_crumb = change_crumb_cb
        
        # Add UI Align
        style.set_main_window(self)
        hbox = gtk.HBox(spacing=FRAME_VERTICAL_SPACING)
        self.add(hbox)

        self.region = None
        self.ipv4 = None
        self.broadband = None
        self.ppp = None

        self.tab_window = TabBox(dockfill = False)
        self.tab_window.set_size_request(674, 408)
        self.items = [("移动宽带", NoSetting()),
                      ("PPP", NoSetting()),
                      ("IPv4 设置", NoSetting())]
        self.tab_window.add_items(self.items)
        self.sidebar = SideBar( None, self.init, self.check_click)

        # Build ui
        hbox.pack_start(self.sidebar, False , False)
        vbox = gtk.VBox()
        vbox.pack_start(self.tab_window ,True, True)
        hbox.pack_start(vbox, True, True)
        self.save_button = Button("save")
        self.save_button.connect("clicked", self.save_changes)
        buttons_aligns = gtk.Alignment(0.5 , 1, 0, 0)
        buttons_aligns.add(self.save_button)
        vbox.pack_start(buttons_aligns, False , False)
        
        self.show_all()
        self.connect("expose-event", self.expose_event)
        vbox.connect("expose-event", self.expose_outline, ["top"])
        self.sidebar.connect("expose-event", self.expose_outline, [])

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
        if init_connections:
            self.sidebar.new_connection_list ={"cdma":[],"gsm":[]}

        def get_mobile_connections():
            cdma = nm_module.nm_remote_settings.get_cdma_connections()
            gsm = nm_module.nm_remote_settings.get_gsm_connections()
            if new_connection:
                cdma +=new_connection["cdma"]
                gsm += new_connection["gsm"]
            return cdma + gsm
        connections = get_mobile_connections()
        
        if connections == []:
            region = slider.get_page_by_name("region")
            region.init()
            slider._slide_to_page("region", "right")
        else:
            self.connections = connections
            self.ipv4_setting = [IPV4Conf(con, self.set_button) for con in connections]
            self.broadband_setting = [Broadband(con, self.set_button) for con in connections]
            self.ppp_setting = [PPPConf(con) for con in connections]

            self.sidebar.init(connections, self.ipv4_setting)
            index = self.sidebar.get_active()
            #self.region = self.region_setting[index]
            self.ipv4 = self.ipv4_setting[index]
            self.broadband = self.broadband_setting[index]
            self.ppp = self.ppp_setting[index]
            #self.dsl = NoSetting()
            #self.ppp = NoSetting()

            self.init_tab_box()

    def init_tab_box(self):
        #self.tab_window.tab_items[0] = ("Region", self.region)
        self.tab_window.tab_items[0] = ("宽带",self.broadband)
        self.tab_window.tab_items[1] = ("IPV4设置",self.ipv4)
        self.tab_window.tab_items[2] = ("PPP", self.ppp)
        tab_index = self.tab_window.tab_index
        self.tab_window.tab_index = -1
        self.tab_window.switch_content(tab_index)
        self.queue_draw()

    def check_click(self, connection):
        index = self.sidebar.get_active()
        #self.region = self.region_setting[index]
        self.ipv4 = self.ipv4_setting[index]
        self.broadband = self.broadband_setting[index]
        self.ppp = self.ppp_setting[index]

        self.init_tab_box()
        
    def save_changes(self, widget):
        #self.dsl.save_setting()
        ##self.ppp.save_setting()
        connection = self.ipv4.connection
        if widget.label is "save":
            if connection.check_setting_finish():
                this_index = self.connections.index(connection)
                from nmlib.nm_remote_connection import NMRemoteConnection
                if isinstance(connection, NMRemoteConnection):
                    connection.update()
                else:
                    nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')
                    index = self.sidebar.new_connection_list.index(connection)
                    self.sidebar.new_connection_list.pop(index)
                    self.init(self.sidebar.new_connection_list)

                    # reset index
                    con = self.sidebar.connection_tree.visible_items[this_index]
                    self.sidebar.connection_tree.select_items([con])
            self.set_button("apply", True)
        else:
            self.apply_change()

        ##FIXME need to change device path into variables
    def apply_change(self):
        connection = self.ipv4.connection
        cdma_device = nm_module.mmclient.get_cdma_device()
        gsm_device = nm_module.mmclient.get_gsm_device()
        device = cdma_device + gsm_device
        if device:
            print nm_module.nmclient.get_modem_devices()
            device_path = nm_module.nmclient.get_modem_device().object_path
            active_connection = nm_module.nmclient.activate_connection(connection.object_path,
                                               device_path,
                                               device[0])

            if active_connection != None:
                print ">>",active_connection
                #active_vpn = cache.get_spec_object(active_object.object_path)
                #active_vpn.connect("vpn-connected", self.vpn_connected)
                #active_vpn.connect("vpn-connecting", self.vpn_connecting)
                #active_vpn.connect("vpn-disconnected", self.vpn_disconnected)
        else:
            print "no active device"
        self.change_crumb()
        self.slide_back() 
    def set_button(self, name, state):
        if name == "save":
            self.save_button.set_label(name)
            self.save_button.set_sensitive(state)
        else:
            self.save_button.set_label("connect")
            self.save_button.set_sensitive(state)

class SideBar(gtk.VBox):
    def __init__(self, connections , main_init_cb, check_click_cb):
        gtk.VBox.__init__(self, False)
        self.connections = connections
        self.main_init_cb = main_init_cb
        self.check_click_cb = check_click_cb

        # Build ui
        self.buttonbox = gtk.VBox()
        self.pack_start(self.buttonbox, False, False)
        add_button = AddSettingItem("创建新连接",self.add_new_connection)
        self.pack_start(TreeView([add_button]), False, False)
        #add_button.connect("clicked", self.add_new_connection)
        #self.pack_start(add_button, False, False)
        self.set_size_request(160, -1)
        self.new_connection_list = {'cdma':[], "gsm":[]}
    
    def init(self, connection_list, ip4setting):
        # check active
        #wired_device = nm_module.nmclient.get_wired_devices()[0]
        #active_connection = wired_device.get_active_connection()
        # FIXME 
        active_connection = nm_module.nmclient.get_mobile_active_connection()
        if active_connection:
            active = active_connection[0].get_connection()
        else:
            active = None

        self.connections = connection_list
        self.setting = ip4setting
        
        # Add connection buttons
        container_remove_all(self.buttonbox)
        self.cons = []
        self.connection_tree = EntryTreeView(self.cons)
        for index, connection in enumerate(self.connections):
            self.cons.append(SettingItem(connection, self.setting[index], self.check_click_cb, self.delete_item_cb))
        self.connection_tree.add_items(self.cons)

        self.connection_tree.show_all()

        self.buttonbox.pack_start(self.connection_tree, False, False)

        try:
            index = self.connections.index(active)
            this_connection = self.connection_tree.visible_items[index]
            this_connection.set_active(True)
            self.connection_tree.select_items([this_connection])
        except ValueError:
            self.connection_tree.select_first_item()

    def delete_item_cb(self, connection):
        '''docstring for delete_item_cb'''
        from nmlib.nm_remote_connection import NMRemoteConnection
        self.connection_tree.delete_select_items()
        if isinstance(connection, NMRemoteConnection):
            connection.delete()
        else:
            index = self.new_connection_list.index(connection)
            self.new_connection_list.pop(index)
        if self.connection_tree.visible_items:
            self.connection_tree.set_size_request(-1,len(self.connection_tree.visible_items) * self.connection_tree.visible_items[0].get_height())

    def get_active(self):
        return self.connection_tree.select_rows[0]

    def set_active(self, connection):
        item = self.cons[self.connections.index(connection)]
        self.connection_tree.select_items([item])
    
    def add_new_connection(self):
        region = slider.get_page_by_name("region")
        region.init()
        slider._slide_to_page("region", "left")
        #connection = nm_module.nm_remote_settings.new_cdma_connection()
        #self.main_init_cb()
        #self.set_active(connection)
        
        

        #new_connection = nm_module.nm_remote_settings.new_pppoe_connection()
        #self.main_init_cb()

class NoSetting(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)

        label_align = gtk.Alignment(0.5,0.5,0,0)

        label = Label("No active connection")
        label_align.add(label)
        self.add(label_align)



class Broadband(gtk.VBox):
    def __init__(self, connection, set_button_callback):
        gtk.VBox.__init__(self)
        self.connection = connection        
        self.set_button = set_button_callback
        # Init widgets
        self.table = gtk.Table(12, 4, False)
        #self.table.set_size_request(500,500)
        
        self.label_basic = Label("基本设置", text_size = TITLE_FONT_SIZE)
        self.label_number = Label("代号:")
        self.label_username = Label("用户名:")
        self.label_password = Label("密码:")

        self.number = InputEntry()
        self.username = InputEntry()
        self.password = PasswordEntry()
        self.password_show = CheckButton("显示密码", padding_x=0)
        self.button_to_region = Button("地区运营商设置")


        #self.table = gtk.Table(6, 4, False)
        self.label_advanced = Label("Advanced")
        self.label_apn = Label("APN:")
        self.label_network = Label("Network ID:")
        self.label_type = Label("Type:")
        self.label_pin = Label("PIN:")

        self.apn = InputEntry()
        self.network_id = InputEntry()
        self.network_type = ComboBox([("Any", None),
                                      ("3G", 0),
                                      ("2G", 1),
                                      ("Prefer 3G", 2),
                                      ("Prefer 2G", 3)],
                                      max_width=300)
        self.roam_check = CheckButton("Allow roaming if home network is not available")
        self.pin = InputEntry()
        
        
        # Connect signals
        self.number.entry.connect("changed", self.save_settings_by, "number")
        self.username.entry.connect("changed", self.save_settings_by, "username")
        self.password.entry.connect("changed", self.save_settings_by, "password")
        self.apn.entry.connect("changed", self.save_settings_by, "apn")
        self.network_id.entry.connect("changed", self.save_settings_by, "network_id")
        self.network_type.connect("item-selected", self.network_type_selected)

        self.password_show.connect("toggled", self.password_show_toggled)
        self.roam_check.connect("toggled", self.roam_check_toggled)
        self.refresh()
        # Refesh

    def password_show_toggled(self, widget):
        if widget.get_active():
            self.password.show_password(True)
        else:
            self.password.show_password(False)

    def init_table(self, network_type):
        container_remove_all(self.table)
        self.table.attach(self.label_basic, 0 ,1 ,0, 1)
        self.table.attach(self.label_number, 1, 2, 1, 2)
        self.table.attach(self.label_username, 1, 2, 2, 3)
        self.table.attach(self.label_password, 1, 2, 3, 4)

        self.table.attach(self.number, 2, 4, 1, 2)
        self.table.attach(self.username, 2, 4, 2, 3)
        self.table.attach(self.password, 2, 4, 3, 4)
        self.table.attach(self.password_show, 2, 4, 4, 5)

        def to_region(widget):
            region = slider.get_page_by_name("region")
            region.init(network_type)
            region.need_new_connection =False
            slider._slide_to_page("region", "left")

        if network_type == "gsm":
            self.button_to_region.connect("clicked", to_region)
            self.table.attach(self.button_to_region, 2,4,5,6)
            self.table.attach(self.label_advanced, 0, 1, 6, 7)
            self.table.attach(self.label_apn, 1, 2 , 7, 8)
            self.table.attach(self.label_network, 1, 2, 8, 9)
            self.table.attach(self.label_type, 1, 2, 9, 10)
            self.table.attach(self.label_pin, 1, 2, 10, 11)

            self.table.attach(self.apn, 2, 4, 7, 8)
            self.table.attach(self.network_id, 2, 4, 8, 9)
            self.table.attach(self.network_type, 2, 4, 9, 10)
            self.table.attach(self.roam_check, 3, 4, 10, 11)
            self.table.attach(self.pin, 2, 4, 11, 12)
        #TODO ui change
        style.set_table_items(self.table, 'entry')
        style.set_table(self.table)
        align = style.set_box_with_align(self.table, "text")
        self.add(align)

    def refresh(self):
        # get_settings
        mobile_type = self.connection.get_setting("connection").type
        self.broadband_setting = self.connection.get_setting(mobile_type)
        number = self.broadband_setting.number
        username = self.broadband_setting.username
        
        password = self.broadband_setting.password
        if password == None:
            try:
                (setting_name, method) = self.connection.guess_secret_info() 
                password = nm_module.secret_agent.agent_get_secrets(self.connection.object_path,
                                                        setting_name,
                                                        method)
            except:
                password = ""


        # both
        self.number.set_text(number)
        self.username.set_text(username)
        self.password.entry.set_text(password)

        if  mobile_type == "gsm":
            apn = self.broadband_setting.apn
            network_id = self.broadband_setting.network_id
            network_type = self.broadband_setting.network_type
            home_only = self.broadband_setting.home_only
            pin = self.broadband_setting.pin
            
            # gsm
            self.apn.set_text(apn)
            self.network_id.set_text(network_id)
            if network_type:
                self.network_type.set_select_index(network_type + 1)
            else:
                self.network_type.set_select_index(0)

            self.roam_check.set_active(home_only is None)

        self.init_table(mobile_type)
        
        ## retrieve wired info

    def set_new_values(self, new_dict, type):
        params = new_dict[type]

        for key, value in params.iteritems():
            setattr(self.broadband_setting, key, value)

        self.refresh()

    def save_settings_by(self, widget, text, attr):
        if text == "":
            delattr(self.broadband_setting, attr)
        else:
            setattr(self.broadband_setting, attr, text)
        self.set_button("save", True)

    def network_type_selected(self, widget, content, value, index):
        if value == None:
            del self.broadband_setting.network_type
        else:
            self.broadband_setting.network_type = value

    def roam_check_toggled(self, widget):
        if widget.get_active():
            del self.broadband_setting.home_only
        else:
            self.broadband_setting.home_only = 1


class PPPConf(gtk.VBox):

    def __init__(self, connection):
        gtk.VBox.__init__(self)

        self.connection = connection
        self.ppp_setting = self.connection.get_setting("ppp")

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
        table = gtk.Table(9, 8, False)
        compression = Label("Compression")
        table.attach(compression, 0, 5, 0 ,1)

        self.require_mppe = CheckButton("Use point-to-point encryption(mppe)")
        self.require_mppe.connect("toggled", self.mppe_toggled)
        self.require_mppe_128 = CheckButton("Require 128-bit encryption")
        self.mppe_stateful = CheckButton("Use stataful MPPE")
        
        self.nobsdcomp = CheckButton("Allow BSD data Compression")
        self.nodeflate = CheckButton("Allow Deflate date compression")
        self.no_vj_comp = CheckButton("Use TCP header compression")

        echo = Label("Echo")
        self.ppp_echo = CheckButton("Send PPP echo packets")
        #self.mppe.set_size_request(100, 10)
        table.attach(self.require_mppe, 0, 10, 1, 2)
        table.attach(self.require_mppe_128, 1, 10, 2, 3)
        table.attach(self.mppe_stateful, 1, 10, 3, 4)
        table.attach(self.nobsdcomp, 0, 10, 4, 5)
        table.attach(self.nodeflate, 0, 10, 5, 6)
        table.attach(self.no_vj_comp, 0, 10, 6, 7)
        table.attach(echo, 0, 5, 7, 8)
        table.attach(self.ppp_echo, 0, 10, 8, 9)

        vbox = gtk.VBox()
        vbox.pack_start(method, False, False)
        vbox.pack_start(self.method_table, False, False)
        vbox.pack_start(table, False, False)
        
        # TODO ui change
        align = style.set_box_with_align(vbox, "text")
        align.add(vbox)
        self.add(align)

        self.require_mppe_128.set_sensitive(False)
        self.mppe_stateful.set_sensitive(False)
        self.refresh()

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

        # entering ui
        #if widget.get_active():
            #self.require_mppe_128.set_sensitive(True)
            #self.mppe_stateful.set_sensitive(True)
        #else:
            #self.require_mppe_128.set_active(False)
            #self.mppe_stateful.set_active(False)
            #self.require_mppe_128.set_sensitive(False)
            #self.mppe_stateful.set_sensitive(False)

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
        #==================================

    def save_setting(self):
        refuse_eap = not self.refuse_eap.get_active()
        refuse_pap = not self.refuse_pap.get_active()
        refuse_chap = not self.refuse_chap.get_active()
        refuse_mschap = not self.refuse_mschap.get_active()
        refuse_mschapv2 = not self.refuse_mschapv2.get_active()

        require_mppe = self.require_mppe.get_active()
        require_mppe_128 = self.require_mppe_128.get_active()
        mppe_stateful = self.mppe_stateful.get_active()

        nobsdcomp = not self.nobsdcomp.get_active()
        nodeflate = not self.nodeflate.get_active()
        no_vj_comp = not  self.no_vj_comp.get_active()

        echo = self.ppp_echo.get_active()

        self.ppp_setting.refuse_eap = refuse_eap
        self.ppp_setting.refuse_pap = refuse_pap
        self.ppp_setting.refuse_chap = refuse_chap
        self.ppp_setting.refuse_mschap = refuse_mschap 
        self.ppp_setting.refuse_mschapv2 = refuse_mschapv2
        self.ppp_setting.require_mppe = require_mppe
        self.ppp_setting.require_mppe_128 = require_mppe_128
        self.ppp_setting.mppe_stateful = mppe_stateful

        self.ppp_setting.nobsdcomp = nobsdcomp
        self.ppp_setting.nodeflate = nodeflate
        self.ppp_setting.no_vj_comp = no_vj_comp

        if echo:
            lcp_echo_failure = 5
            lcp_echo_interval = 30
        else:
            lcp_echo_failure = 0
            lcp_echo_interval = 0

        #print self.ppp_setting.prop_dict

    def mppe_toggled(self, widget):
        #print "toggled"
        if widget.get_active():
            self.require_mppe_128.set_sensitive(True)
            self.mppe_stateful.set_sensitive(True)
        else:
            self.require_mppe_128.set_active(False)
            self.mppe_stateful.set_active(False)
            self.require_mppe_128.set_sensitive(False)
            self.mppe_stateful.set_sensitive(False)

    def toggle_cb(self, widget):
        if widget.get_active():
            self.method_table.set_no_show_all(False)
            self.show_all()
        else:
            self.method_table.set_no_show_all(True)
            self.method_table.hide()
