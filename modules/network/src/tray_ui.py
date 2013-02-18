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
from dtk.ui.button import OffButton, Button
from dtk.ui.new_treeview import TreeItem, TreeView
from dtk.ui.draw import draw_text, draw_pixbuf
from dtk.ui.utils import get_content_size, cairo_disable_antialias, color_hex_to_cairo, container_remove_all
import gtk
import pango
from nls import _
from constants import CONTENT_FONT_SIZE, IMG_WIDTH
import style
from helper import Dispatcher
WIDGET_HEIGHT = 22
bg_color="#ebf4fd"
line_color="#7da2ce"
BORDER_COLOR = color_hex_to_cairo(line_color)
BG_COLOR = color_hex_to_cairo(bg_color)
#from nm_modules import nm_module

#net_manager = NetManager()
class TrayUI(gtk.VBox):

    def __init__(self, wired_toggle_cb, wireless_toggle_cb, mobile_toggle_cb):
        gtk.VBox.__init__(self)
        self.wired_toggle = wired_toggle_cb
        self.wireless_toggle = wireless_toggle_cb
        self.mobile_toggle = mobile_toggle_cb
        self.init_ui()
        self.active_ap_index = []

    def init_ui(self):
        self.wire = Section(app_theme.get_pixbuf("network/cable.png"), _("wired"), self.wired_toggle)
        self.wireless = Section(app_theme.get_pixbuf("network/wifi.png"), _("wireless"), self.wireless_toggle)
        self.mobile = Section(app_theme.get_pixbuf("network/3g.png"), _("Mobile Network"), self.mobile_toggle)
        self.pack_start(self.wire, False, False)
        self.pack_start(self.wireless, False, False)
        
        self.ssid_list = []
        self.tree_box = gtk.VBox()
        self.pack_start(self.tree_box, False, False)
        self.pack_start(self.mobile, False, False)
        self.ap_tree = TreeView()
        self.more_button = MoreButton("more", self.ap_tree, self.resize_tree)
    
    def get_widget_height(self):
        height = 0
        widgets = self.get_children()
        if self.wire in widgets:
            height += 20
        if self.wireless in widgets:
            height +=20
            if self.ap_tree.visible_items:
                height += len(self.ap_tree.visible_items) * 20
            if self.more_button in self.tree_box.get_children():
                height +=20

        height += 20
        return height

    def remove_net(self, net_type):
        if net_type == "wired":
            self.remove(self.wire)
        elif net_type == "wireless":
            self.remove(self.wireless)

    def set_wired_state(self, widget, new_state, reason):
        if new_state is 20:
            self.wire.set_active(0)
        else:
            print new_state, reason
    
    def set_ap(self, ap_list):
        if not ap_list:
            return 
        self.ap_tree.delete_all_items()
        if len(ap_list) <= 5:
            self.ap_tree.add_items(map(lambda ap: SsidItem(ap), ap_list))
            self.ap_tree.set_size_request(-1, WIDGET_HEIGHT*len(ap_list))
        else:
            self.ap_tree.add_items(map(lambda ap: SsidItem(ap), ap_list[:5]))
            self.more_button.set_ap_list(ap_list[5:])
            self.ap_tree.set_size_request(-1, WIDGET_HEIGHT*5)
            #self.ap_tree.add_items([MoreItem(more_ap, self.resize_tree)])
        container_remove_all(self.tree_box)
        self.tree_box.pack_start(self.ap_tree, True, True)
        self.tree_box.pack_start(self.more_button, False, False)
        self.show_all()


    def set_active_ap(self, index, state):
        print "in set active ap",index
        if state and index:
            self.set_active_ap(self.active_ap_index, False)
            self.active_ap_index = index
        if index:
            for i in index:
                self.ap_tree.visible_items[i].set_active(state)

    def get_active_ap(self):
        return self.active_ap_index

    def resize_tree(self):
        self.tree_box.remove(self.more_button)
        length = len(self.ap_tree.visible_items)
        if length <=10:
            self.ap_tree.set_size_request(-1, WIDGET_HEIGHT*length)
        else:
            self.ap_tree.set_size_request(-1, WIDGET_HEIGHT*10)
            for item in self.ap_tree.visible_items:
                item.set_padding(10)

        Dispatcher.tray_show_more()

         
class Section(gtk.HBox):
    TOGGLE_INSENSITIVE = 0
    TOGGLE_INACTIVE = 1
    TOGGLE_ACTIVE = 2

    def __init__(self, icon, text, toggle_callback):
        gtk.HBox.__init__(self)
        self.icon = icon
        self.text = text
        self.toggle_callback = toggle_callback
        self.height = WIDGET_HEIGHT
        self.set_size_request(-1, self.height)

        self.__init_ui()

    def __init_ui(self):
        icon = ImageBox(self.icon)
        self.label = Label(self.text)
        self.offbutton = OffButton()
        self.offbutton.connect("toggled", self.toggle_callback)
        self.pack_start(style.wrap_with_align(icon), False, False)
        self.pack_start(style.wrap_with_align(self.label, align="left"), False, False, padding=10)
        self.pack_end(style.wrap_with_align(self.offbutton), False, False)
        self.show_all()

    def get_active(self):
        return self.offbutton.get_active()

    def set_active(self, state, emit=False):
        '''
        state format : (dev_state, con_state)
        '''
        (dev_state, con_state) = state
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

        self.lock_pixbuf =  app_theme.get_pixbuf("lock/lock.png")
        self.strength_0 = app_theme.get_pixbuf("network/Wifi_0.png")
        self.strength_1 = app_theme.get_pixbuf("network/Wifi_1.png")
        self.strength_2 = app_theme.get_pixbuf("network/Wifi_2.png")
        self.strength_3 = app_theme.get_pixbuf("network/Wifi_3.png")
        self.jumpto_pixbuf = app_theme.get_pixbuf("network/jump_to.png")
        self.right_padding = 0

    def render_essid(self, cr, rect):
        self.render_background(cr,rect)
        (text_width, text_height) = get_content_size(self.ssid)
        if self.active:
            text_color = "#3da1f7"
        else:
            text_color = "#000000"
        draw_text(cr, self.ssid, rect.x, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT, text_color = text_color)


        if self.is_select:
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

        if self.security:
            lock_icon = self.lock_pixbuf
            draw_pixbuf(cr, lock_icon.get_pixbuf(), rect.x , rect.y + (rect.height - IMG_WIDTH)/2)

        if self.strength > 80:
            signal_icon = self.strength_3
        elif self.strength > 60:
            signal_icon = self.strength_2
        elif self.strength > 30:
            signal_icon = self.strength_1
        else:
            signal_icon = self.strength_0
        
        draw_pixbuf(cr, signal_icon.get_pixbuf(), rect.x + IMG_WIDTH, rect.y + (rect.height - IMG_WIDTH)/2)
        if self.is_select:
            with cairo_disable_antialias(cr):
                cr.set_source_rgb(*BORDER_COLOR)
                cr.set_line_width(1)
                #if self.is_last:
                    #cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
                cr.rectangle(rect.x -1 , rect.y +1, rect.width , rect.height -1 )
                cr.stroke()

    def get_column_widths(self):
        return [-1, IMG_WIDTH * 2 + self.right_padding]

    def get_column_renders(self):
        return [self.render_essid, self.render_signal]

    def get_height(self):
        return WIDGET_HEIGHT
        
    def select(self):
        self.is_select = True
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def unselect(self):
        self.is_select = False
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
    
    def double_click(self, column, offset_x, offset_y):
        self.is_double_click = True

    def single_click(self, column, offset_x, offset_y):
        if self.is_double_click:
            print "double click"
            Dispatcher.connect_by_ssid(self.ssid)
            self.is_double_click = False
            

        self.redraw()
    
    def redraw(self):
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def set_active(self, state):
        self.active = state
        self.redraw()

    def render_background(self, cr, rect):
        if self.is_select:
            cr.set_source_rgb(*BG_COLOR)
        else:
            cr.set_source_rgb(1, 1, 1 )
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

    def set_padding(self, padding):
        self.right_padding = padding
        self.redraw()

class MoreItem(TreeItem):

    def __init__(self, child_list, resize_tree_cb):
        TreeItem.__init__(self)
        self.children = child_list
        self.resize_tree = resize_tree_cb
        #self.arrow_right=ui_theme.get_pixbuf("treeview/arrow_right.png")
        #self.arrow_down=ui_theme.get_pixbuf("treeview/arrow_down.png")

    def render_content(self, cr, rect):
        content = _("more wireless ap")
        self.render_background(cr, rect)
        (text_width, text_height) = get_content_size(content)
        import pango
        draw_text(cr, content, rect.x, rect.y, rect.width, rect.height,
                alignment=pango.ALIGN_LEFT)

    def render_right(self, cr, rect):
        self.render_background(cr, rect)
        

    def get_column_renders(self):
        return [self.render_content,
                self.render_right]

    def get_column_widths(self):
        return [-1, IMG_WIDTH]

    def get_height(self):
        return WIDGET_HEIGHT

    def single_click(self, column, offset_x, offset_y):
        if self.is_expand:
            self.unexpand()
        else:
            self.expand()

    def expand(self):
        self.is_expand = True
        self.add_child_item()
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
        self.resize_tree()

    def unexpand(self):
        '''docstring for unexpand'''
        self.delete_child_item()

        self.is_expand = False
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
        self.resize_tree()

    def add_child_item(self):
        self.delete()
        self.child_items = self.children
        self.add_items_callback(self.child_items, self.row_index + 1)
        
    def delete_child_item(self):
        self.delete_items_callback(self.child_items)

    def render_background(self, cr, rect):
        cr.set_source_rgb(1, 1, 1 )
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

class MoreButton(Button):

    def __init__(self, name, tree,  refresh_cb):
        Button.__init__(self, name)
        self.tree = tree
        self.refresh = refresh_cb
        self.show_all = False
        self.connect("clicked", self.show_more)
        self.connect("expose-event", self.expose_button)

    def set_ap_list(self, ap_list):
        self.ap_list = ap_list

    def show_more(self, widget):
        if self.show_all is False:
            self.tree.add_items(map(lambda ap: SsidItem(ap), self.ap_list))
            self.refresh()
    
    def expose_button(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        if widget.state == gtk.STATE_NORMAL:
            bg_color = "#ffffff"
        else:
            bg_color = "#ebf4fd"

        cr.set_source_rgb(*color_hex_to_cairo(bg_color))

        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()
        # draw text
        label = "more wireless"
        (text_width, text_height) = get_content_size(label)
        offset_y = (rect.height - text_height)/2
        draw_text(cr, label, rect.x, rect.y + offset_y, text_width, text_height,
                alignment = pango.ALIGN_LEFT)
        return True
