#!/usr/bin/env python
#-*- coding:utf-8 -*-
#from theme import app_theme, ui_theme

from dss import app_theme
from dtk.ui.tab_window import TabBox
from dtk.ui.button import Button,CheckButton
from dtk.ui.new_entry import InputEntry, PasswordEntry
from dtk.ui.new_treeview import TreeView
from dtk.ui.label import Label
from dtk.ui.utils import container_remove_all
from dtk.ui.combo import ComboBox
from dtk.ui.scrolled_window import ScrolledWindow
from settings_widget import SettingItem, EntryTreeView, AddSettingItem
from nm_modules import nm_module
from container import MyToggleButton as SwitchButton
from container import TitleBar
from shared_widget import IPV4Conf
from foot_box import FootBox

import gtk

from constants import TITLE_FONT_SIZE, FRAME_VERTICAL_SPACING, CONTENT_FONT_SIZE
import style
from nls import _

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
        main_vbox = gtk.VBox()
        self.foot_box = FootBox()
        hbox = gtk.HBox()
        hbox.connect("expose-event",self.expose_line)

        main_vbox.pack_start(hbox, False, False)
        main_vbox.pack_start(self.foot_box, False, False)

        self.add(main_vbox)

        self.tab_window = TabBox(dockfill = False)
        self.tab_window.draw_title_background = self.draw_tab_title_background
        self.tab_window.set_size_request(674, 415)

        self.setting_group = Settings([Broadband, IPV4Conf, PPPConf], self.set_button)
        self.sidebar = SideBar( None, self.init, self.check_click)

        # Build ui
        hbox.pack_start(self.sidebar, False , False)
        hbox.pack_start(self.tab_window ,True, True)
        self.save_button = Button()
        self.save_button.connect("clicked", self.save_changes)
        self.foot_box.set_buttons([self.save_button])
        #self.foot_box.set_tip("Tip:sfdsfdsfadsf")
        
        self.show_all()
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

            self.sidebar.init(connections, self.setting_group)
            index = self.sidebar.get_active()
            self.set_tab_content(self.connections[index], init_connections)

    def set_tab_content(self, connection, init_connection=False):
        if self.tab_window.tab_items ==  []:
            self.tab_window.add_items(self.setting_group.init_settings(connection))
        else:
            self.tab_window.tab_items = self.setting_group.init_settings(connection)
        if init_connection:
            tab_index = 0
        else:
            tab_index = self.tab_window.tab_index
        self.tab_window.tab_index = -1
        self.tab_window.switch_content(tab_index)
        self.queue_draw()

    def check_click(self, connection):
        self.set_tab_content(connection)
        (label, state) = self.setting_group.get_button_state(connection)
        self.set_button(label, state)
        
    def save_changes(self, widget):
        connection = self.setting_group.connection
        if widget.label == _("save"):
            if connection.check_setting_finish():
                this_index = self.connections.index(connection)
                from nmlib.nm_remote_connection import NMRemoteConnection
                if isinstance(connection, NMRemoteConnection):
                    connection.update()
                else:
                    nm_module.nm_remote_settings.new_connection_finish(connection.settings_dict, 'lan')
                    mobile_type = connection.get_setting("connection").type
                    index = self.sidebar.new_connection_list[mobile_type].index(connection)
                    self.sidebar.new_connection_list[mobile_type].pop(index)
                    self.init(self.sidebar.new_connection_list)

                    # reset index
                    con = self.sidebar.connection_tree.visible_items[this_index]
                    self.sidebar.connection_tree.select_items([con])
            self.set_button("apply", True)
        else:
            self.apply_change()

        ##FIXME need to change device path into variables
    def apply_change(self):
        connection = self.setting_group.connection
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
        else:
            print "no active device"
        self.change_crumb()
        self.slide_back() 
    def set_button(self, name, state):
        if name == "save":
            self.save_button.set_label(_("save"))
            self.save_button.set_sensitive(state)
        else:
            self.save_button.set_label(_("connect"))
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
        style.add_separator(self)
        add_button = AddSettingItem(_("New Connection"),self.add_new_connection)
        self.pack_start(TreeView([add_button]), False, False)
        self.set_size_request(160, -1)
        self.new_connection_list = {'cdma':[], "gsm":[]}
    
    def init(self, connection_list, ip4setting):
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
            self.cons.append(SettingItem(connection, self.check_click_cb, self.delete_item_cb))
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
            mobile_type = self.connection.get_setting("connection").type
            index = self.new_connection_list[mobile_type].index(connection)
            self.new_connection_list[mobile_type].pop(index)

        if self.connection_tree.visible_items == []:
            self.connection_tree.set_size_request(-1,len(self.connection_tree.visible_items) * self.connection_tree.visible_items[0].get_height())
        else:
            container_remove_all(self.buttonbox)

    def get_active(self):
        return self.connection_tree.select_rows[0]

    def set_active(self, connection):
        item = self.cons[self.connections.index(connection)]
        self.connection_tree.select_items([item])
    
    def add_new_connection(self):
        region = slider.get_page_by_name("region")
        region.init()
        slider._slide_to_page("region", "left")

class NoSetting(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)

        label_align = gtk.Alignment(0.5,0.5,0,0)

        label = Label("No active connection")
        label_align.add(label)
        self.add(label_align)

class Settings(object):

    def __init__(self, setting_list, set_button_callback):
        self.set_button_callback = set_button_callback

        self.setting_list = setting_list
        
        self.setting_state = {}
        self.settings = {}

    def get_broadband(self):
        return self.settings[self.connection][0][1]
    
    def init_settings(self, connection):
        self.connection = connection 
        if connection not in self.settings:
            setting_list = []
            for setting in self.setting_list:
                s = setting(connection, self.set_button)
                setting_list.append((s.tab_name, s))

            self.settings[connection] = setting_list
        return self.settings[connection]

    def set_button(self, name, state):
        self.set_button_callback(name, state)
        self.setting_state[self.connection] = (name, state)

    def clear(self):
        print "clear settings"
        self.setting_state = {}
        self.settings = {}

    def get_button_state(self, connection):
        return self.setting_state[self.connection]

class Broadband(gtk.VBox):
    ENTRY_WIDTH = 222
    def __init__(self, connection, set_button_callback):
        gtk.VBox.__init__(self)
        self.tab_name = _("Broadband")
        self.connection = connection        
        self.set_button = set_button_callback
        # Init widgets
        self.table = gtk.Table(12, 4, False)
        
        #self.label_basic = Label(_("Basic"), text_size = TITLE_FONT_SIZE)
        self.label_basic = TitleBar(None, _("Basic"))
        self.label_number = Label(_("Code:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.label_username = Label(_("Username:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.label_password = Label(_("password:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)

        self.number = InputEntry()
        self.username = InputEntry()
        self.password = PasswordEntry()
        self.password_show = CheckButton(_("show password"), padding_x=0)
        self.button_to_region = Button(_("Regions setting"))


        #self.table = gtk.Table(6, 4, False)
        self.label_advanced = TitleBar(None,_("Advanced"))
        self.label_apn = Label(_("APN:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.label_network = Label(_("Network ID:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.label_type = Label(_("Type:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        self.label_pin = Label(_("PIN:"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)

        self.apn = InputEntry()
        self.network_id = InputEntry()
        self.network_type = ComboBox([("Any", None),
                                      ("3G", 0),
                                      ("2G", 1),
                                      ("Prefer 3G", 2),
                                      ("Prefer 2G", 3)],
                                      max_width=self.ENTRY_WIDTH)
        self.roam_check = CheckButton(_("Allow roaming if home network is not available"), padding_x=0)
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

        scrolled_window = ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        align = style.set_box_with_align(self.table, "text")
        scrolled_window.add_with_viewport(align)
        self.add(scrolled_window)
        align.connect("expose-event", self.expose_bg)

        # wrap with alignment
        
        self.refresh()
        # Refesh

    def password_show_toggled(self, widget):
        if widget.get_active():
            self.password.show_password(True)
        else:
            self.password.show_password(False)

    def init_table(self, network_type):
        #container_remove_all(self.table)
        if self.table.get_children() != []:
            pass
        else:
            self.table.attach(self.label_basic, 0,2 ,0, 1)
            self.table.attach(style.wrap_with_align(self.label_number), 0, 1, 1, 2)
            self.table.attach(style.wrap_with_align(self.label_username), 0, 1, 2, 3)
            self.table.attach(style.wrap_with_align(self.label_password), 0, 1, 3, 4)

            self.table.attach(style.wrap_with_align(self.number), 1, 2, 1, 2)
            self.table.attach(style.wrap_with_align(self.username), 1, 2, 2, 3)
            self.table.attach(style.wrap_with_align(self.password), 1, 2, 3, 4)
            self.table.attach(style.wrap_with_align(self.password_show, align="left"), 1, 2, 4, 5)

            def to_region(widget):
                region = slider.get_page_by_name("region")
                region.init(network_type)
                region.need_new_connection =False
                slider._slide_to_page("region", "left")

            if network_type == "gsm":
                self.button_to_region.connect("clicked", to_region)
                self.table.attach(style.wrap_with_align(self.button_to_region), 1,2,5,6)
                self.table.attach(self.label_advanced, 0, 2, 6, 7)
                self.table.attach(style.wrap_with_align(self.label_apn), 0, 1 , 7, 8)
                self.table.attach(style.wrap_with_align(self.label_network), 0, 1, 8, 9)
                self.table.attach(style.wrap_with_align(self.label_type), 0, 1, 9, 10)
                self.table.attach(style.wrap_with_align(self.label_pin), 0, 1, 11, 12)

                self.table.attach(style.wrap_with_align(self.apn), 1, 2, 7, 8)
                self.table.attach(style.wrap_with_align(self.network_id), 1, 2, 8, 9)
                self.table.attach(style.wrap_with_align(self.network_type), 1, 2, 9, 10)
                self.table.attach(style.wrap_with_align(self.roam_check, align="left"), 1, 2, 10, 11)
                self.table.attach(style.wrap_with_align(self.pin), 1, 2, 11, 12)
            #TODO ui change
            #style.set_table_items(self.table, 'entry')
            entry_list = ["number", "username", "password",
                          "apn", "network_id", "pin"]
            for entry in entry_list:
                widget = getattr(self, entry)
                widget.entry.set_size_request(self.ENTRY_WIDTH, 22)

            style.set_table(self.table)
        self.table.show_all()

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

    def expose_bg(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb( 1, 1, 1) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

#class PPPConf(ScrolledWindow):
    #TABLE_WIDTH = 300
    #def __init__(self, connection, set_button_callback):
        #ScrolledWindow.__init__(self)

        #self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        #self.connection = connection
        #self.set_button = set_button_callback
        #self.ppp_setting = self.connection.get_setting("ppp")

        ## invisable settings
        ##method_image = gtk.Image()
        ##method_image.set_from_pixbuf(app_theme.get_pixbuf("network/validation.png").get_pixbuf())
        ##compress_image = gtk.Image()
        ##compress_image.set_from_pixbuf(app_theme.get_pixbuf("network/zip.png").get_pixbuf())
        ##echo_image = gtk.Image()
        ##echo_image.set_from_pixbuf(app_theme.get_pixbuf("network/echo.png").get_pixbuf())

        ##self.method_label = Label("Configure Method", text_size=TITLE_FONT_SIZE)
        #self.method_title = TitleBar(app_theme.get_pixbuf("network/validation.png"),
                                     #_("Configure Method"), width=self.TABLE_WIDTH)
        #self.compression_title = TitleBar(app_theme.get_pixbuf("network/zip.png"),
                                          #_("Compression"), width=self.TABLE_WIDTH)
        #self.echo_title = TitleBar(app_theme.get_pixbuf("network/echo.png"),
                                          #_("Echo"), width=self.TABLE_WIDTH)

        #self.refuse_eap_label = Label(_("EAP"), text_size=CONTENT_FONT_SIZE)
        #self.refuse_pap_label = Label(_("PAP"), text_size=CONTENT_FONT_SIZE)
        #self.refuse_chap_label = Label(_("CHAP"), text_size=CONTENT_FONT_SIZE)
        #self.refuse_mschap_label = Label(_("MSCHAP"), text_size=CONTENT_FONT_SIZE)
        #self.refuse_mschapv2_label = Label(_("MSCHAP v2"), text_size=CONTENT_FONT_SIZE)
        #self.refuse_eap = SwitchButton()
        #self.refuse_pap = SwitchButton()
        #self.refuse_chap = SwitchButton()
        #self.refuse_mschap = SwitchButton()
        #self.refuse_mschapv2 = SwitchButton()
        
        #self.method_table = gtk.Table(16, 3, False)


        #self.method_table.attach(self.method_title, 0, 3, 9, 10)
        ##self.method_table.attach(style.wrap_with_align(self.method_label), 1, 2, 9, 10)
        #self.method_table.attach(style.wrap_with_align(self.refuse_eap_label), 1, 2, 10, 11, xpadding=10)
        #self.method_table.attach(style.wrap_with_align(self.refuse_pap_label), 1, 2, 11, 12, xpadding=10)
        #self.method_table.attach(style.wrap_with_align(self.refuse_chap_label), 1, 2, 12, 13, xpadding=10)
        #self.method_table.attach(style.wrap_with_align(self.refuse_mschap_label), 1, 2, 13, 14, xpadding=10)
        #self.method_table.attach(style.wrap_with_align(self.refuse_mschapv2_label), 1, 2, 14, 15, xpadding=10)

        #self.method_table.attach(style.wrap_with_align(self.refuse_eap), 2, 3, 10, 11)
        #self.method_table.attach(style.wrap_with_align(self.refuse_pap), 2, 3, 11, 12)
        #self.method_table.attach(style.wrap_with_align(self.refuse_chap), 2, 3, 12, 13)
        #self.method_table.attach(style.wrap_with_align(self.refuse_mschap), 2, 3, 13, 14)
        #self.method_table.attach(style.wrap_with_align(self.refuse_mschapv2), 2, 3, 14, 15)

        ##style.set_table(self.method_table, row_spacing=)


        ## visible settings
        ##compression = Label("Compression", text_size=TITLE_FONT_SIZE)
        #self.require_mppe_label = Label(_("Use point-to-point encryption(mppe)"), text_size=CONTENT_FONT_SIZE)
        #self.require_mppe_128_label = Label(_("Require 128-bit encryption"), text_size=CONTENT_FONT_SIZE)
        #self.mppe_stateful_label = Label(_("Use stataful MPPE"), text_size=CONTENT_FONT_SIZE)
        #self.nobsdcomp_label = Label(_("Allow BSD data Compression"), text_size=CONTENT_FONT_SIZE)
        #self.nodeflate_label = Label(_("Allow Deflate date compression"), text_size=CONTENT_FONT_SIZE)
        #self.no_vj_comp_label = Label(_("Use TCP header compression"), text_size=CONTENT_FONT_SIZE)
        ##echo = Label("Echo", text_size=TITLE_FONT_SIZE)
        #self.ppp_echo_label = Label(_("Send PPP echo packets"), text_size=CONTENT_FONT_SIZE)

        #self.require_mppe = SwitchButton()
        #self.require_mppe_128 = SwitchButton()
        #self.mppe_stateful = SwitchButton()
        
        #self.nobsdcomp = SwitchButton()
        #self.nodeflate = SwitchButton()
        #self.no_vj_comp = SwitchButton()
        #self.ppp_echo = SwitchButton()

        #self.method_table.attach(self.compression_title, 0, 3, 0 ,1)
        ##self.method_table.attach(style.wrap_with_align(compression), 1, 2, 0 ,1)
        #self.method_table.attach(style.wrap_with_align(self.require_mppe_label), 1, 2, 1, 2, xpadding=10)
        #self.method_table.attach(style.wrap_with_align(self.require_mppe_128_label), 1, 2, 2, 3, xpadding=10)
        #self.method_table.attach(style.wrap_with_align(self.mppe_stateful_label), 1, 2, 3, 4, xpadding=10)
        #self.method_table.attach(style.wrap_with_align(self.nobsdcomp_label), 1, 2, 4, 5, xpadding=10)
        #self.method_table.attach(style.wrap_with_align(self.nodeflate_label), 1, 2, 5, 6, xpadding=10)
        #self.method_table.attach(style.wrap_with_align(self.no_vj_comp_label), 1, 2, 6, 7, xpadding=10)

        ##self.method_table.attach(style.wrap_with_align(echo_image), 0, 1, 7, 8)
        #self.method_table.attach(self.echo_title, 0, 3, 7, 8)
        #self.method_table.attach(style.wrap_with_align(self.ppp_echo_label), 1, 2, 8, 9, xpadding=10)

        #self.method_table.attach(style.wrap_with_align(self.require_mppe), 2, 3, 1, 2)
        #self.method_table.attach(style.wrap_with_align(self.require_mppe_128), 2, 3, 2, 3, xpadding=15)
        #self.method_table.attach(style.wrap_with_align(self.mppe_stateful), 2, 3, 3, 4, xpadding=15)
        #self.method_table.attach(style.wrap_with_align(self.nobsdcomp), 2, 3, 4, 5)
        #self.method_table.attach(style.wrap_with_align(self.nodeflate), 2, 3, 5, 6)
        #self.method_table.attach(style.wrap_with_align(self.no_vj_comp), 2, 3, 6, 7)
        #self.method_table.attach(style.wrap_with_align(self.ppp_echo), 2, 3, 8, 9)

        #vbox = gtk.VBox()
        ##vbox.pack_start(method, False, False)
        ##vbox.pack_start(table, False, False)
        #vbox.pack_start(self.method_table, False, False)
        #self.method_table.set_col_spacing(0, 10)
        #self.method_table.set_row_spacing(6, 15)
        #self.method_table.set_row_spacing(8, 15)
        #align = style.set_box_with_align(vbox, "text")
        #self.add_with_viewport(align)
        #align.connect("expose-event", self.expose_bg)

        #self.refresh()

        #self.refuse_eap.connect("toggled", self.check_button_cb, "refuse_eap")
        #self.refuse_pap.connect("toggled", self.check_button_cb, "refuse_pap")
        #self.refuse_chap.connect("toggled", self.check_button_cb, "refuse_chap")
        #self.refuse_mschap.connect("toggled", self.check_button_cb, "refuse_mschap")
        #self.refuse_mschapv2.connect("toggled", self.check_button_cb, "refuse_mschapv2")
        #self.require_mppe.connect("toggled", self.check_button_cb, "require_mppe")
        #self.require_mppe_128.connect("toggled", self.check_button_cb, "require_mppe_128")
        #self.mppe_stateful.connect("toggled", self.check_button_cb,"mppe_stateful")
        #self.nobsdcomp.connect("toggled", self.check_button_cb, "nobsdcomp")
        #self.nodeflate.connect("toggled", self.check_button_cb, "nodeflate")
        #self.no_vj_comp.connect("toggled", self.check_button_cb, "no_vj_comp")
        #self.ppp_echo.connect("toggled", self.check_button_cb, "echo")

    #def refresh(self):
        ##=========================
        ## retreieve settings
        #refuse_eap = self.ppp_setting.refuse_eap
        #refuse_pap = self.ppp_setting.refuse_pap
        #refuse_chap = self.ppp_setting.refuse_chap
        #refuse_mschap = self.ppp_setting.refuse_mschap
        #refuse_mschapv2 = self.ppp_setting.refuse_mschapv2

        #require_mppe = self.ppp_setting.require_mppe
        #require_mppe_128 = self.ppp_setting.require_mppe_128
        #mppe_stateful = self.ppp_setting.mppe_stateful

        #nobsdcomp = self.ppp_setting.nobsdcomp
        #nodeflate = self.ppp_setting.nodeflate
        #no_vj_comp = self.ppp_setting.no_vj_comp

        #lcp_echo_failure = self.ppp_setting.lcp_echo_failure
        #lcp_echo_interval = self.ppp_setting.lcp_echo_interval

        #if require_mppe:
            #self.require_mppe_128_label.set_sensitive(True)
            #self.mppe_stateful_label.set_sensitive(True)
            #self.require_mppe_128.set_sensitive(True)
            #self.mppe_stateful.set_sensitive(True)
        #else:
            #self.require_mppe_128_label.set_sensitive(False)
            #self.mppe_stateful_label.set_sensitive(False)
            #self.require_mppe_128.set_active(False)
            #self.mppe_stateful.set_active(False)
            #self.require_mppe_128.set_sensitive(False)
            #self.mppe_stateful.set_sensitive(False)


        #self.refuse_eap.set_active( not refuse_eap)
        #self.refuse_pap.set_active(not refuse_pap)
        #self.refuse_chap.set_active(not refuse_chap)
        #self.refuse_mschap.set_active(not refuse_mschap)
        #self.refuse_mschapv2.set_active(not refuse_mschapv2)

        #self.require_mppe.set_active(require_mppe)
        #self.require_mppe_128.set_active(require_mppe_128)
        ## FIXME umcomment it when backend ready
        #self.mppe_stateful.set_active(mppe_stateful)
        #self.nobsdcomp.set_active(not nobsdcomp)
        #self.nodeflate.set_active(not nodeflate)
        #self.no_vj_comp.set_active(not no_vj_comp)

        #if lcp_echo_failure == None and lcp_echo_interval == None:
            #self.ppp_echo.set_active(False)
        #else:
            #self.ppp_echo.set_active(True)
        ##==================================

    #def check_button_cb(self, widget, key):
        #active = widget.get_active()
        #if key.startswith("refuse"):
            #if active:
                #setattr(self.ppp_setting, key, False)
            #else:
                #setattr(self.ppp_setting, key, True)
        #elif key.startswith("no"):
            #if active:
                #setattr(self.ppp_setting, key, False)
            #else:
                #setattr(self.ppp_setting, key, True)
        #elif key is "echo":
            #if active:
                #setattr(self.ppp_setting, "lcp_echo_failure", 5)
                #setattr(self.ppp_setting, "lcp_echo_interval", 30)
            #else:
                #setattr(self.ppp_setting, "lcp_echo_failure", 0)
                #setattr(self.ppp_setting, "lcp_echo_interval", 0)
        #else:
            #if active:
                #setattr(self.ppp_setting, key, True)
            #else:
                #setattr(self.ppp_setting, key, False)
        #check_settings(self.connection, self.set_button)

        #if key is "require_mppe":
            #if active:
                #self.require_mppe_128_label.set_sensitive(True)
                #self.mppe_stateful_label.set_sensitive(True)
                #self.require_mppe_128.set_sensitive(True)
                #self.mppe_stateful.set_sensitive(True)
            #else:
                #self.require_mppe_128.set_active(False)
                #self.mppe_stateful.set_active(False)
                #self.require_mppe_128_label.set_sensitive(False)
                #self.mppe_stateful_label.set_sensitive(False)
                #self.require_mppe_128.set_sensitive(False)
                #self.mppe_stateful.set_sensitive(False)

    #def toggle_cb(self, widget):
        #if widget.get_active():
            #self.method_table.set_no_show_all(False)
            #self.show_all()
        #else:
            #self.method_table.set_no_show_all(True)
            #self.method_table.hide()

    #def expose_bg(self, widget, event):
        #cr = widget.window.cairo_create()
        #rect = widget.allocation
        #cr.set_source_rgb( 1, 1, 1) 
        #cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        #cr.fill()

class PPPConf(ScrolledWindow):
    TABLE_WIDTH = 300
    def __init__(self, connection, set_button_callback):
        ScrolledWindow.__init__(self)
        self.tab_name = _("PPP")
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        self.connection = connection
        self.set_button = set_button_callback
        self.ppp_setting = self.connection.get_setting("ppp")

        self.method_title = TitleBar(app_theme.get_pixbuf("network/validation.png"),
                                     _("Configure Method"), width=self.TABLE_WIDTH)

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
        
        self.method_table = gtk.Table(16, 3, False)

        # visible settings

        self.compression_title = TitleBar(app_theme.get_pixbuf("network/zip.png"),
                                          _("Compression"), width=self.TABLE_WIDTH)
        self.echo_title = TitleBar(app_theme.get_pixbuf("network/echo.png"),
                                          _("Echo"), width=self.TABLE_WIDTH)


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
        self.ppp_echo_label = Label(_("Send PPP echo packets"), text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)

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
                self.refresh_table(True)
            else:
                self.refresh_table(False)
