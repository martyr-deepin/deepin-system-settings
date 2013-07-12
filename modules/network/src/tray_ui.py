#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Zeng Zhi
# 
# Author:     Zeng Zhi <zengzhilg@gmail.com>
# Maintainer: Zeng Zhi <zengzhilg@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from dss import app_theme
from dtk.ui.box import ImageBox
from dtk.ui.label import Label
from vtk.button import SelectButton
from dtk.ui.treeview import TreeItem, TreeView
from dtk.ui.draw import draw_text, draw_pixbuf
from dtk.ui.utils import get_content_size, cairo_disable_antialias, color_hex_to_cairo, container_remove_all
import gtk
import pango
from nls import _
from constants import CONTENT_FONT_SIZE, IMG_WIDTH
import style
from helper import Dispatcher
from timer import Timer
from container import MyToggleButton as SwitchButton
from shared_methods import net_manager
from nm_modules import nm_module

from tray_log import tray_log

WIDGET_HEIGHT = 22

ALIGN_SPACING = 28
bg_color="#ebf4fd"
line_color="#7da2ce"
BORDER_COLOR = color_hex_to_cairo(line_color)
BG_COLOR = color_hex_to_cairo(bg_color)
#from nm_modules import nm_module

#net_manager = NetManager()
class TrayUI(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self, spacing=0)
        self.init_ui()
        self.active_ap_index = []
        self.all_showed = False

    def init_ui(self):
        self.wire = Section(app_theme.get_pixbuf("network/cable.png"), _("Wired"))
        self.wireless = Section(app_theme.get_pixbuf("network/wifi.png"), _("Wireless"))
        self.mobile = Section(app_theme.get_pixbuf("network/3g.png"), _("Mobile Network"))
        # vpn
        self.vpn = Section(app_theme.get_pixbuf("network/vpn.png"), _("VPN Network"))
        self.dsl = Section(app_theme.get_pixbuf("network/dsl.png"), _("DSL"))

        self.ssid_list = []
        self.tree_box = gtk.VBox(spacing=0)
        self.button_more = SelectButton(_("Advanced..."), font_size=10, ali_padding=5)
        self.button_more.set_size_request(-1, 25)
        #self.pack_start(self.button_more, False, False)
        self.ap_tree = TreeView(mask_bound_height=0)
        self.ap_tree.set_expand_column(0)

        self.vpn_list = ConList()
        self.dsl_list = DSLConList()

        self.wire_box = self.section_box([self.wire])
        self.wireless_box = self.section_box([self.wireless, self.tree_box])
        self.mobile_box = self.section_box([self.mobile])
        self.vpn_box = self.section_box([self.vpn , self.vpn_list])
        self.dsl_box = self.section_box([self.dsl, self.dsl_list])
        self.wire_state = False
        self.wireless_state = False
        self.mobile_state = False
        self.vpn_state = False
        self.dsl_state = False

        self.device_tree = None

        self.pack_start(self.wire_box, False, False)
        self.pack_start(self.wireless_box, False, False)
        self.pack_start(self.mobile_box, False, False)
        self.pack_start(self.vpn_box, False, False)
        self.pack_start(self.dsl_box, False, False)
        self.pack_start(self.button_more, False, False)

    def get_widget_height(self):
        height = 0
        if self.wire_state:
            height += 35
        if self.wireless_state:
            height += 35
            if self.ap_tree.visible_items and self.wireless.get_active():
                height += self.ap_tree.get_size_request()[1]
            if self.device_tree:
                height += 22

        if self.mobile_state:
            height += 35

        if self.vpn_state:
            height += 35 + len(self.vpn_list.get_children()) * 22

        if self.dsl_state:
            height += 35 + len(self.dsl_list.get_children()) * 22
            height += 5
        height += 25

        return height

    def section_box(self, widgets):
        box = gtk.VBox(spacing=0)
        for w in widgets:
            box.pack_start(w, False, False)
        style.add_separator(box, 10)
        return box

    def remove_net(self, net_type):
        #print net_type
        getattr(self, net_type + "_box").set_no_show_all(True)
        #getattr(self, net_type).set_active((True, False))
        getattr(self, net_type + "_box").hide()
        setattr(self, net_type + "_state", False)

    def show_net(self, net_type):
        getattr(self, net_type + "_box").set_no_show_all(False)
        getattr(self, net_type + "_box").show()
        setattr(self, net_type + "_state", True)

    def set_wired_state(self, widget, new_state, reason):
        if new_state is 20:
            self.wire.set_active(0)
        else:
            tray_log.debug(__name__, new_state, reason)

    def set_visible_aps(self, show_all=False):
        if not self.__ap_list:
            self.visible_aps = []
            return

        tray_log.debug(len(self.__ap_list))

        if show_all:
            if len(self.__ap_list) <= 10:
                self.visible_aps = self.__ap_list[:]
            else:
                self.visible_aps = self.__ap_list[:10]
            self.more_button.set_ap_list([])
            self.show_all = True


        else:
            if len(self.__ap_list) <= 5:
                self.visible_aps = self.__ap_list[:]
                self.show_all = True
            else:
                self.visible_aps = self.__ap_list[:5]
                self.more_button.set_ap_list(self.__ap_list[5:])
                self.show_all = False
    
    def set_ap(self, ap_list, redraw=True):
        if not ap_list:
            return 
        self.__set_ap_list(ap_list)
        #print "DEBUG", len(self.visible_aps), self.show_all
        self.ap_tree.delete_all_items()
        container_remove_all(self.tree_box)

        self.ap_tree.add_items(map(lambda ap: SsidItem(ap), self.__ap_list))
        length = len(self.ap_tree.visible_items)
        if length <=10:
            self.ap_tree.set_size_request(-1, WIDGET_HEIGHT*length)
        else:
            self.ap_tree.set_size_request(-1, WIDGET_HEIGHT*10)
            for item in self.ap_tree.visible_items:
                item.set_padding(10)

        self.tree_box.pack_start(self.ap_tree, False, False)
        self.show_all()

        if redraw:
            Dispatcher.request_resize()

    def __set_ap_list(self, ap_list):
        self.__ap_list = ap_list

    def move_active(self, index):
        if index != [] and self.__ap_list:
            for i in index:
                if i < len(self.ap_tree.visible_items):
                    self.ap_tree.delete_item_by_index(i)
                    self.ap_tree.add_items([SsidItem(self.__ap_list[i])],
                                            insert_pos=0)
                else:
                    self.ap_tree.delete_item_by_index(-1)
                    self.ap_tree.add_items([SsidItem(self.__ap_list[i])],
                                            insert_pos=0)
                self.ap_tree.visible_items[0].set_active(True)


    def set_active_ap(self, index, state):
        self.active_ap_index = index
        self.set_ap(self.__ap_list, redraw=False)

        if index:
            self.move_active(index)
        
    def get_active_ap(self):
        return self.active_ap_index

    def add_switcher(self):
        if not hasattr(self, "device_tree") or not self.device_tree:
            self.device_tree = TreeView([DeviceItem()], mask_bound_height=0)
            self.device_tree.set_expand_column(1)
            self.wireless_box.pack_start(self.device_tree, False, False)
            self.wireless_box.reorder_child(self.wireless_box.get_children()[-2], len(self.wireless_box.get_children()))
            tray_log.debug(self.wireless_box.get_children())
            net_manager.emit_wifi_switch(0)

    def remove_switcher(self):
        if self.device_tree:
            self.wireless_box.remove(self.device_tree)
            self.device_tree = None
    
    def get_active_in_ui(self):
        return filter(lambda i: i.get_active() == True, self.ap_tree.visible_items)

    def reset_tree(self):
        if len(self.ap_tree.visible_items) >= 5 and self.all_showed:
            remove_items = self.ap_tree.visible_items[5:]
            self.ap_tree.delete_items(remove_items)
            self.ap_tree.set_size_request(-1, WIDGET_HEIGHT*5)
            self.tree_box.pack_start(self.more_button, False, False)
            self.all_showed = False
            
class Section(gtk.HBox):
    TOGGLE_INSENSITIVE = 0
    TOGGLE_INACTIVE = 1
    TOGGLE_ACTIVE = 2

    def __init__(self, icon, text, has_separater=True):
        gtk.HBox.__init__(self)
        self.icon = icon
        self.text = text
        self.height = 30
        self.set_size_request(-1, self.height)
        self.has_separater = has_separater

        self.__init_ui()

    def __init_ui(self):
        icon = ImageBox(self.icon)
        self.label = Label(self.text)
        self.offbutton = SwitchButton()
        self.pack_start(self.__wrap_with_align(icon), False, False)
        self.pack_start(self.__wrap_with_align(self.label, align="left"), False, False, padding=10)
        self.pack_end(self.__wrap_with_align(self.offbutton), False, False)
        self.show_all()

    def connect_to_toggle(self, toggle_func):
        self.offbutton.connect("toggled", lambda w: toggle_func())
        self.timer = Timer(200, toggle_func)


    def toggle_callback(self, widget):
        if self.timer.alive():
            self.timer.restart()
        else:
            self.timer.start()

    def __wrap_with_align(self, widget, align="right",h=25):
        if align is "left":
            align = gtk.Alignment(0, 0.5, 1, 0)
        elif align is "right":
            align = gtk.Alignment(1, 0.5, 0, 0)
            align.set_padding(0,0, 1, 0)
        align.set_size_request( -1, h)
        align.add(widget)
        return align

    def get_active(self):
        return self.offbutton.get_active()

    def set_active(self, state, emit=False):
        '''
        state format : (dev_state, con_state)
        '''
        tray_log.debug("someone set button", state)
        #print "---------------------"
        #print "someone set off button"
        #print "state", state
        #print "active", self.get_active()
        #print "------------------------"
        (dev_state, con_state) = state
        print state, emit
        if dev_state is False:
            self.offbutton.set_active(False)
            self.label.set_sensitive(dev_state)
            self.offbutton.set_sensitive(dev_state)
        else:
            self.label.set_sensitive(dev_state)
            self.offbutton.set_sensitive(dev_state)
            self.offbutton.set_active(con_state)
        if emit:
            self.offbutton.emit("toggled")

    def set_sensitive(self, state):
        self.offbutton.set_sensitive(state)

    def set_padding(self, child, padding):
        self.set_child_packing(child, False, False, padding, gtk.PACK_START)

class SsidItem(TreeItem):
    NETWORK_DISCONNECT = 0
    NETWORK_LOADING = 1
    NETWORK_CONNECTED = 2

    SPACING = 5

    def __init__(self,
                 ap,
                 setting_object = None, 
                 font_size = CONTENT_FONT_SIZE):
        TreeItem.__init__(self)
        self.ap = ap
        self.ssid = ap.get_ssid()
        self.security = ap.get_flags()
        self.strength = ap.get_strength()
        self.is_double_click = False

        self.active = False

        '''
        Pixbufs
        '''
        self.loading_pixbuf = app_theme.get_pixbuf("network/loading.png")
        self.check_pixbuf = app_theme.get_pixbuf("network/check_box-2.png")
        self.check_out_pixbuf = app_theme.get_pixbuf("network/check_box_out.png")

        #self.lock_pixbuf =  app_theme.get_pixbuf("lock/lock.png")
        if self.security:
            self.strength_0 = app_theme.get_pixbuf("network/secured-0.png")
            self.strength_1 = app_theme.get_pixbuf("network/secured-1.png")
            self.strength_2 = app_theme.get_pixbuf("network/secured-2.png")
            self.strength_3 = app_theme.get_pixbuf("network/secured-3.png")
        else:
        
            self.strength_0 = app_theme.get_pixbuf("network/Wifi_0.png")
            self.strength_1 = app_theme.get_pixbuf("network/Wifi_1.png")
            self.strength_2 = app_theme.get_pixbuf("network/Wifi_2.png")
            self.strength_3 = app_theme.get_pixbuf("network/Wifi_3.png")
        self.jumpto_pixbuf = app_theme.get_pixbuf("network/jump_to.png")
        self.right_padding = 0

    def render_essid(self, cr, rect):
        self.render_background(cr,rect)
        ssid = self.ssid.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        (text_width, text_height) = get_content_size(ssid)
        if self.active:
            text_color = "#3da1f7"
        else:
            text_color = "#000000"
        draw_text(cr, ssid, rect.x + ALIGN_SPACING , rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT, text_color = text_color)

        if self.is_hover:
            with cairo_disable_antialias(cr):
                cr.set_source_rgb(*BORDER_COLOR)
                cr.set_line_width(1)
                #if self.is_last:
                    #cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
                cr.rectangle(rect.x + 1, rect.y +1, rect.width , rect.height -1)
                cr.stroke()

    def render_signal(self, cr, rect):
        self.render_background(cr,rect)
        if self.is_select:
            pass

        if self.strength > 80:
            signal_icon = self.strength_3
        elif self.strength > 60:
            signal_icon = self.strength_2
        elif self.strength > 30:
            signal_icon = self.strength_1
        else:
            signal_icon = self.strength_0
        
        draw_pixbuf(cr, signal_icon.get_pixbuf(), rect.x, rect.y + (rect.height - IMG_WIDTH)/2)
        if self.is_hover:
            with cairo_disable_antialias(cr):
                cr.set_source_rgb(*BORDER_COLOR)
                cr.set_line_width(1)
                cr.rectangle(rect.x -1 , rect.y +1, rect.width , rect.height -1 )
                cr.stroke()

    def get_column_widths(self):
        return [-1, IMG_WIDTH + self.right_padding+ self.SPACING]

    def get_column_renders(self):
        return [self.render_essid, self.render_signal]

    def get_height(self):
        return WIDGET_HEIGHT
        
    def select(self):
        self.is_select = True
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
    
    def hover(self, column, offset_x, offset_y):
        self.is_hover = True
        self.redraw()

    def unhover(self, column, offset_x, offset_y):
        self.is_hover = False
        self.redraw()

    def unselect(self):
        self.is_select = False
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
    
    def double_click(self, column, offset_x, offset_y):
        self.is_double_click = True

    def single_click(self, column, offset_x, offset_y):
        Dispatcher.connect_by_ssid(self.ssid, self.ap)
    
    def redraw(self):
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def set_active(self, state):
        self.active = state
        self.redraw()
    
    def get_active(self):
        return self.active

    def render_background(self, cr, rect):
        if self.is_hover:
            cr.set_source_rgb(*BG_COLOR)
        else:
            cr.set_source_rgb(1, 1, 1 )
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

    def set_padding(self, padding):
        self.right_padding = padding
        self.redraw()

class DeviceItem(TreeItem):
    SPACING = 5
    
    def __init__(self,
                 font_size = CONTENT_FONT_SIZE):

        TreeItem.__init__(self)
        self.wifi = app_theme.get_pixbuf("network/wifi_device.png")
        self.left = app_theme.get_pixbuf("network/left.png")
        self.right = app_theme.get_pixbuf("network/right.png")

        self.devices =  net_manager.device_manager.wireless_devices

        self.index = 1

    def render_icon(self, cr, rect):
        self.render_background(cr, rect)
        draw_pixbuf(cr, self.wifi.get_pixbuf(), rect.x + 16, rect.y)
    
    def render_text(self, cr, rect):
        self.render_background(cr, rect)
        text = _("card %d")%(self.index)
        (text_width, text_height) = get_content_size(text)
        draw_text(cr, text, rect.x, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_CENTER)

    def render_left(self, cr, rect):
        self.render_background(cr, rect)
        draw_pixbuf(cr, self.left.get_pixbuf(), rect.x + ALIGN_SPACING, rect.y + (rect.height - 16)/2)

    def render_right(self, cr, rect):
        self.render_background(cr, rect)
        draw_pixbuf(cr, self.right.get_pixbuf(), rect.x , rect.y + (rect.height - IMG_WIDTH)/2)

    def get_column_widths(self):
        return [16 + ALIGN_SPACING, -1, IMG_WIDTH + self.SPACING]
    
    def get_height(self):
        return 22

    def get_column_renders(self):
        return [self.render_left, self.render_text,
                self.render_right]

    def hover(self, column, offset_x, offset_y):
        self.is_hover = True

        self.redraw()

    def unhover(self, column, offset_x, offset_y):
        self.is_hover = False
        self.redraw()

    def round_plus(self):
        if self.index == len(self.devices):
            self.index = 1
        else:
            self.index += 1

    def round_minus(self):
        self.index -= 1
        if self.index == 0:
            self.index = len(self.devices)

    def single_click(self, column, offset_x, offset_y):
        if column == 2:
            self.round_plus()
        elif column == 0:
            self.round_minus()

        net_manager.emit_wifi_switch(self.index -1)
        self.redraw()

    def set_index(self, device):
        self.index = self.devices.index(device) + 1
        self.redraw()


    def render_background(self, cr, rect):
        if self.is_hover:
            cr.set_source_rgb(*BG_COLOR)
        else:
            cr.set_source_rgb(1, 1, 1 )
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

    def redraw(self):
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

class ConList(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)

    def connecting_cb(self):
        pass

    def clear(self):
        container_remove_all(self)

    def add_items(self, connections):
        for c in connections:
            self.pack_start(ConButton(c, self.connecting_cb))
        self.show_all()

    def set_active_by(self, index):
        self.get_children()[index].set_active(True)

    def reset_state(self):
        map(lambda i: i.set_active(False), self.get_active_item())

    def get_item_by(self, connection):
        return filter(lambda c: c.connection == connection, self.get_children())
    
    def get_active_item(self):
        return filter(lambda c: c.is_active, self.get_children())

class ConButton(gtk.Button):        
    def __init__(self, 
                 connection,
                 connecting_cb,
                 ali_padding=0,
                 font_size=10,
                 bg_color="#ebf4fd",
                 line_color="#7da2ce",):

        gtk.Button.__init__(self)
        self.connection = connection
        self.connecting_cb = connecting_cb
        self.font_size = font_size
        self.bg_color = bg_color

        self.__init_values()

    def __init_values(self):
        self.con = self.connection.get_setting("connection").id
        self.is_active = False
        self.text_color = "#000000"

        self.set_size_request(-1, WIDGET_HEIGHT)
        self.connect("expose-event", self.__expose_event)
        self.connect("clicked", self.__active_one_vpn)

    def stop_callback(self):
        pass

    def active_callback(self):
        pass


    def __active_one_vpn(self, widget):
        from lists import Monitor
        monitor = Monitor(self.connection,
                          self.stop_callback,
                          self.active_callback,)
        monitor.start()
        self.connecting_cb()

    def set_active(self, state):
        self.is_active = state
        if state:
            self.text_color = "#3da1f7"
        else:
            self.text_color = "#000000"
        self.queue_draw()

    def __expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        
        # Get color info.
        if widget.state == gtk.STATE_NORMAL:
            border = None
            bg = None
            
        elif widget.state == gtk.STATE_PRELIGHT:
            border = BORDER_COLOR
            bg = BG_COLOR
        elif widget.state == gtk.STATE_ACTIVE:
            border = BORDER_COLOR
            bg = None
        elif widget.state == gtk.STATE_INSENSITIVE:
            pass
            
        # Draw background.
        if bg:
            cr.set_source_rgb(*BG_COLOR)
            cr.rectangle(x, y , w, h)
            cr.fill()
        
        # Draw border.
        if border:
            with cairo_disable_antialias(cr):
                cr.set_source_rgb(*border)
                cr.set_line_width(1)
                #if self.is_last:
                    #cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
                cr.rectangle(x + 1, y + 1, w - 1, h -1)
                cr.stroke()
            #draw_line(cr, x + 1, y + 1, x + w - 2, y + 1) # top
            #draw_line(cr, x + 2, y + h, x + w - 2, y + h) # bottom
            #draw_line(cr, x + 1, y + 2, x + 1, y + h - 2) # left
            #draw_line(cr, x + w, y + 2, x + w, y + h - 2) # right
        
        # Draw font.
        draw_text(cr, self.con, x + ALIGN_SPACING, y, w, h, CONTENT_FONT_SIZE, self.text_color,
                    alignment=pango.ALIGN_LEFT)
        
        return True

class DSLConButton(ConButton):

    def __init__(self, connection, connecting_cb=None):
        ConButton.__init__(self, connection, connecting_cb)
        self.connect("clicked", self.__active_dsl)

    def __active_dsl(self, widget):
        device_path = net_manager.wired_device.object_path
        nm_module.nmclient.activate_connection_async(self.connection.object_path,
                                               device_path,
                                               "/")

class DSLConList(ConList):
    def __init__(self):
        ConList.__init__(self)
        self.connections_cb = None

    def add_items(self, connections):
        for c in connections:
            self.pack_start(DSLConButton(c, self.connecting_cb))
        self.show_all()
