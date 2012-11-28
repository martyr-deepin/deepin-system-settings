#!/usr/bin/env python
#-*- coding:utf-8 -*-
# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Zeng Zhi
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
from theme import app_theme
from dtk.ui.theme import ui_theme
from dtk.ui.new_treeview import TreeItem, TreeView
from dtk.ui.draw import draw_vlinear, draw_pixbuf, draw_text, draw_line
from dtk.ui.utils import get_content_size, cairo_disable_antialias, color_hex_to_cairo, get_parent_dir
from dtk.ui.constant import DEFAULT_FONT_SIZE

from lan_config import WiredSetting, NoSetting
from wlan_config import WirelessSetting
#from wired import *
import gtk
import os
import pango
BORDER_COLOR = color_hex_to_cairo("#aeaeae")

class WirelessItem(TreeItem):

    CHECK_LEFT_PADDING = 10
    CHECK_RIGHT_PADIING = 10
    SIGNAL_LEFT_PADDING = 0
    SIGNAL_RIGHT_PADDING = 27
    JUMPTO_RIGHT_PADDING = 10
    VERTICAL_PADDING = 5

    NETWORK_DISCONNECT = 0
    NETWORK_LOADING = 1
    NETWORK_CONNECTED = 2

    def __init__(self,
                 connection,
                 setting_object = None, 
                 slide_to_setting_cb = None, 
                 send_to_crumb = None,
                 font_size = DEFAULT_FONT_SIZE):

        TreeItem.__init__(self)
        self.setting_object = setting_object
        self.connection = connection
        self.slide_to_setting = slide_to_setting_cb
        self.essid = connection.get_ssid()
        self.send_to_crumb = send_to_crumb
        self.strength = connection.get_strength()
        self.font_size = font_size
        self.is_last = False
        self.check_width = self.get_check_width()
        self.essid_width = self.get_essid_width(self.essid)
        self.signal_width = self.get_signal_width()
        self.jumpto_width = self.get_jumpto_width()
        
        self.network_state = self.NETWORK_DISCONNECT

    def render_check(self, cr, rect):
        render_background(cr,rect)
        #print self.is_select, self.check_select_flag
        if self.network_state == self.NETWORK_DISCONNECT:
            check_icon = app_theme.get_pixbuf("/Network/check_box_out.png").get_pixbuf()
        elif self.network_state == self.NETWORK_LOADING:
            check_icon = app_theme.get_pixbuf("/Network/loading.png").get_pixbuf()
        else:
            check_icon = app_theme.get_pixbuf("/Network/check_box.png").get_pixbuf()

        draw_pixbuf(cr, check_icon, rect.x + self.CHECK_LEFT_PADDING, rect.y + (rect.height - check_icon.get_height())/2)

        #draw outline
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            if self.is_last:
                cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
            cr.rectangle(rect.x, rect.y, rect.width, 1)
            cr.rectangle(rect.x, rect.y, 1, rect.height)
            cr.fill()

    def render_essid(self, cr, rect):
        render_background(cr,rect)
        (text_width, text_height) = get_content_size(self.essid)
        if self.is_select:
            text_color = None
        draw_text(cr, self.essid, rect.x, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)

        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            if self.is_last:
                cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
            cr.rectangle(rect.x, rect.y, rect.width, 1)
            cr.fill()

    def render_signal(self, cr, rect):
        render_background(cr,rect)
        if self.is_select:
            pass
        if self.strength > 50:
            signal_icon = app_theme.get_pixbuf("/Network/strength_1.png").get_pixbuf()
        else:
            signal_icon = app_theme.get_pixbuf("/Network/strength0.png").get_pixbuf()
        draw_pixbuf(cr, signal_icon, rect.x , rect.y + self.VERTICAL_PADDING)
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            if self.is_last:
                cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
            cr.rectangle(rect.x, rect.y, rect.width, 1)
            cr.fill()
    
    def render_jumpto(self, cr, rect):
        render_background(cr,rect)
        if self.is_select:
            pass
        jumpto_icon = app_theme.get_pixbuf("/Network/jump_to.png").get_pixbuf()
        draw_pixbuf(cr, jumpto_icon, rect.x , rect.y + self.VERTICAL_PADDING)
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            if self.is_last:
                cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
            cr.rectangle(rect.x, rect.y, rect.width, 1)
            cr.rectangle(rect.x + rect.width -1, rect.y, 1, rect.height)
            cr.fill()

    def get_check_width(self):
        check_icon = app_theme.get_pixbuf("/Network/check_box.png").get_pixbuf()
        return check_icon.get_width()+ self.CHECK_LEFT_PADDING + self.CHECK_RIGHT_PADIING

    def get_essid_width(self, essid):
        return get_content_size(essid)[0]
    
    def get_signal_width(self):
        return app_theme.get_pixbuf("/Network/strength_1.png").get_pixbuf().get_width() + self.SIGNAL_RIGHT_PADDING

    def get_jumpto_width(self):
        return app_theme.get_pixbuf("/Network/jump_to.png").get_pixbuf().get_width() + self.JUMPTO_RIGHT_PADDING

    def get_column_widths(self):
        return [self.check_width, -1, self.signal_width, self.jumpto_width]

    def get_column_renders(self):
        return [self.render_check, self.render_essid, self.render_signal, self.render_jumpto]

    def get_height(self):
        return  app_theme.get_pixbuf("/Network/check_box.png").get_pixbuf().get_height()+ self.VERTICAL_PADDING*2
        
    def select(self):
        #print "select"
        self.is_select = True
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def set_active(self, b):
        if b:
            self.select()
        else:
            self.unselect()

    def get_active(self):
        return self.is_select

    def unselect(self):
        #print "unselect"
        self.is_select = False
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
        
    def hover(self, column, offset_x, offset_y):
        pass

    def unhover(self, column, offset_x, offset_y):
        #print column, offset_x, offset_y
        pass

    def single_click(self, column, x, y):
        if column == 3:
            #if not nm_remote_settings.get_ssid_associate_connections(self.connection.get_ssid()):
                #nm_remote_settings.new_wireless_connection(ssid = self.connection.get_ssid())

            self.setting_object.init(self.connection)
            self.send_to_crumb()
            self.slide_to_setting() 
        #if self.redraw_request_callback:
            #self.redraw_request_callback(self)

def render_background( cr, rect):
    background_color = [(0,["#ffffff", 1.0]),
                        (1,["#ffffff", 1.0])]
    draw_vlinear(cr, rect.x ,rect.y, rect.width, rect.height, background_color)



class WiredItem(TreeItem):
    CHECK_LEFT_PADDING = 10
    CHECK_RIGHT_PADIING = 10
    JUMPTO_RIGHT_PADDING = 10
    VERTICAL_PADDING = 5

    def __init__(self, device, setting, slide_to_setting_cb = None,send_to_crumb= False, font_size = DEFAULT_FONT_SIZE):
        
        TreeItem.__init__(self)
        self.slide_to_setting = slide_to_setting_cb
        self.device = device
        self.essid = self.device.get_device_desc()
        self.items = None
        self.setting = setting
        self.is_last = False
        self.send_to_crumb = send_to_crumb
        self.font_size = font_size
        self.check_width = self.get_check_width()
        self.essid_width = self.get_essid_width(self.essid)
        self.jumpto_width = self.get_jumpto_width()
        self.network_state = 0

    def render_check(self, cr, rect):
        render_background(cr, rect)

        #if self.is_select:
            #check_icon = app_theme.get_pixbuf("/Network/check_box.png").get_pixbuf()
        #else:
            #check_icon = app_theme.get_pixbuf("/Network/check_box_out.png").get_pixbuf()

        if self.network_state == 0:
            check_icon = app_theme.get_pixbuf("/Network/check_box_out.png").get_pixbuf()
        elif self.network_state == 1:
            check_icon = app_theme.get_pixbuf("/Network/loading.png").get_pixbuf()
        else:
            check_icon = app_theme.get_pixbuf("/Network/check_box.png").get_pixbuf()

        draw_pixbuf(cr, check_icon, rect.x + self.CHECK_LEFT_PADDING, rect.y + (rect.height - check_icon.get_height())/2)
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            if self.is_last:
                cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
            cr.rectangle(rect.x, rect.y, rect.width, 1)
            cr.rectangle(rect.x , rect.y, 1, rect.height)
            cr.fill()


    def render_essid(self, cr, rect):
        render_background(cr, rect)
        (text_width, text_height) = get_content_size(self.essid)
        if self.is_select:
            text_color = None
        draw_text(cr, self.essid, rect.x, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            if self.is_last:
                cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
            cr.rectangle(rect.x, rect.y, rect.width, 1)
            cr.fill()

    def render_jumpto(self, cr, rect):

        render_background(cr, rect)
        if self.is_select:
            pass
        jumpto_icon = app_theme.get_pixbuf("/Network/jump_to.png").get_pixbuf()
        draw_pixbuf(cr, jumpto_icon, rect.x , rect.y + self.VERTICAL_PADDING)
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            if self.is_last:
                cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
            cr.rectangle(rect.x, rect.y, rect.width, 1)
            cr.rectangle(rect.x + rect.width -1, rect.y, 1, rect.height)
            cr.fill()

    def get_check_width(self):
        check_icon = app_theme.get_pixbuf("/Network/check_box.png").get_pixbuf()
        return check_icon.get_width() + self.CHECK_LEFT_PADDING + self.CHECK_RIGHT_PADIING
    def get_essid_width(self, essid):
        return get_content_size(essid)[0]
    
    def get_jumpto_width(self):
        return app_theme.get_pixbuf("/Network/jump_to.png").get_pixbuf().get_width() + self.JUMPTO_RIGHT_PADDING

    def get_column_widths(self):
        return [self.check_width, -1,self.jumpto_width]

    def get_column_renders(self):
        return [self.render_check, self.render_essid, self.render_jumpto]

    def get_height(self):
        return  app_theme.get_pixbuf("/Network/check_box.png").get_pixbuf().get_height() + self.VERTICAL_PADDING *2 
        
    def unselect(self):
        self.is_select = False
        
    def hover(self, column, offset_x, offset_y):
        pass

    def unhover(self, column, offset_x, offset_y):
        #print column, offset_x, offset_y
        pass

    def single_click(self, column, x, y):
        #if column == 0 and x in range(self.CHECK_LEFT_PADDING, self.check_width-self.CHECK_RIGHT_PADIING):
            #self.is_select = not self.is_select
        if column == 2:
            self.setting.init(self.device)
            self.slide_to_setting()
            self.send_to_crumb()

        if self.redraw_request_callback:
            self.redraw_request_callback(self)
        

class DSLItem(TreeItem):
    CHECK_LEFT_PADDING = 10
    CHECK_RIGHT_PADIING = 10
    JUMPTO_RIGHT_PADDING = 10
    VERTICAL_PADDING = 5

    def __init__(self, essid, setting, slide_to_setting_cb = None,send_to_crumb= False, font_size = DEFAULT_FONT_SIZE):
        
        TreeItem.__init__(self)
        self.slide_to_setting = slide_to_setting_cb
        self.essid = essid
        self.items = None
        self.setting = setting
        self.is_last = False
        self.send_to_crumb = send_to_crumb
        self.font_size = font_size
        self.check_width = self.get_check_width()
        self.essid_width = self.get_essid_width(essid)
        self.jumpto_width = self.get_jumpto_width()

    def render_check(self, cr, rect):
        render_background(cr, rect)

        if self.is_select:
            check_icon = app_theme.get_pixbuf("/Network/check_box.png").get_pixbuf()
        else:
            check_icon = app_theme.get_pixbuf("/Network/check_box_out.png").get_pixbuf()

        draw_pixbuf(cr, check_icon, rect.x + self.CHECK_LEFT_PADDING, rect.y + self.VERTICAL_PADDING)
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            if self.is_last:
                cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
            cr.rectangle(rect.x, rect.y, rect.width, 1)
            cr.rectangle(rect.x , rect.y, 1, rect.height)
            cr.fill()


    def render_essid(self, cr, rect):
        render_background(cr, rect)
        (text_width, text_height) = get_content_size(self.essid)
        if self.is_select:
            text_color = None
        draw_text(cr, self.essid, rect.x, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            if self.is_last:
                cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
            cr.rectangle(rect.x, rect.y, rect.width, 1)
            cr.fill()

    def render_jumpto(self, cr, rect):

        render_background(cr, rect)
        if self.is_select:
            pass
        jumpto_icon = app_theme.get_pixbuf("/Network/jump_to.png").get_pixbuf()
        draw_pixbuf(cr, jumpto_icon, rect.x , rect.y + self.VERTICAL_PADDING)
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            if self.is_last:
                cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
            cr.rectangle(rect.x, rect.y, rect.width, 1)
            cr.rectangle(rect.x + rect.width -1, rect.y, 1, rect.height)
            cr.fill()

    def get_check_width(self):
        check_icon = app_theme.get_pixbuf("/Network/check_box.png").get_pixbuf()
        return check_icon.get_width() + self.CHECK_LEFT_PADDING + self.CHECK_RIGHT_PADIING
    def get_essid_width(self, essid):
        return get_content_size(essid)[0]
    
    def get_jumpto_width(self):
        return app_theme.get_pixbuf("/Network/jump_to.png").get_pixbuf().get_width() + self.JUMPTO_RIGHT_PADDING

    def get_column_widths(self):
        return [self.check_width, -1,self.jumpto_width]

    def get_column_renders(self):
        return [self.render_check, self.render_essid, self.render_jumpto]

    def get_height(self):
        return  app_theme.get_pixbuf("/Network/check_box.png").get_pixbuf().get_height() + self.VERTICAL_PADDING *2 
        
    def unselect(self):
        self.is_select = False
        
    def hover(self, column, offset_x, offset_y):
        pass

    def unhover(self, column, offset_x, offset_y):
        #print column, offset_x, offset_y
        pass

    def single_click(self, column, x, y):
        #if column == 0 and x in range(self.CHECK_LEFT_PADDING, self.check_width-self.CHECK_RIGHT_PADIING):
            #self.is_select = not self.is_select
        if column == 2:
            if not isinstance(self.setting.ipv4, NoSetting):
                self.setting.ipv4.reset(self.setting.ipv4.connection)
            self.slide_to_setting()
            self.send_to_crumb()

        if self.redraw_request_callback:
            self.redraw_request_callback(self)

class GeneralItem(TreeItem):
    CHECK_LEFT_PADDING = 10
    CHECK_RIGHT_PADIING = 10
    JUMPTO_RIGHT_PADDING = 10
    VERTICAL_PADDING = 5

    def __init__(self,
                 name,
                 setting_page,
                 slide_to_setting_page_cb,
                 send_to_crumb,
                 font_size=DEFAULT_FONT_SIZE):

        TreeItem.__init__(self)

        self.name = name
        self.setting = setting_page
        self.slide_to_setting = slide_to_setting_page_cb
        self.send_to_crumb = send_to_crumb
        self.font_size = font_size
        self.check_width = self.get_check_width()
        self.essid_width = self.get_essid_width(self.name)
        self.jumpto_width = self.get_jumpto_width()
        self.network_state = 2
        self.is_last = True

    def render_check(self, cr, rect):
        render_background(cr, rect)

        if self.network_state == 0:
            check_icon = app_theme.get_pixbuf("/Network/check_box_out.png").get_pixbuf()
        elif self.network_state == 1:
            check_icon = app_theme.get_pixbuf("/Network/loading.png").get_pixbuf()
        else:
            check_icon = app_theme.get_pixbuf("/Network/check_box.png").get_pixbuf()

        draw_pixbuf(cr, check_icon, rect.x + self.CHECK_LEFT_PADDING, rect.y + (rect.height - check_icon.get_height())/2)
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            if self.is_last:
                cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
            cr.rectangle(rect.x, rect.y, rect.width, 1)
            cr.rectangle(rect.x , rect.y, 1, rect.height)
            cr.fill()

    def render_name(self, cr, rect):
        render_background(cr, rect)
        (text_width, text_height) = get_content_size(self.name)
        if self.is_select:
            text_color = None
        draw_text(cr, self.name, rect.x, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            if self.is_last:
                cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
            cr.rectangle(rect.x, rect.y, rect.width, 1)
            cr.fill()

    def render_jumpto(self, cr, rect):

        render_background(cr, rect)
        if self.is_select:
            pass
        jumpto_icon = app_theme.get_pixbuf("/Network/jump_to.png").get_pixbuf()
        draw_pixbuf(cr, jumpto_icon, rect.x , rect.y + self.VERTICAL_PADDING)
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            if self.is_last:
                cr.rectangle(rect.x, rect.y + rect.height -1, rect.width, 1)
            cr.rectangle(rect.x, rect.y, rect.width, 1)
            cr.rectangle(rect.x + rect.width -1, rect.y, 1, rect.height)
            cr.fill()

    def get_check_width(self):
        check_icon = app_theme.get_pixbuf("/Network/check_box.png").get_pixbuf()
        return check_icon.get_width() + self.CHECK_LEFT_PADDING + self.CHECK_RIGHT_PADIING
    def get_essid_width(self, essid):
        return get_content_size(essid)[0]
    
    def get_jumpto_width(self):
        return app_theme.get_pixbuf("/Network/jump_to.png").get_pixbuf().get_width() + self.JUMPTO_RIGHT_PADDING

    def get_column_widths(self):
        return [self.check_width, -1,self.jumpto_width]

    def get_column_renders(self):
        return [self.render_check, self.render_name, self.render_jumpto]

    def get_height(self):
        return  app_theme.get_pixbuf("/Network/check_box.png").get_pixbuf().get_height() + self.VERTICAL_PADDING *2 
        
    def unselect(self):
        self.is_select = False
        
    def hover(self, column, offset_x, offset_y):
        pass

    def unhover(self, column, offset_x, offset_y):
        #print column, offset_x, offset_y
        pass

    def single_click(self, column, x, y):
        #if column == 0 and x in range(self.CHECK_LEFT_PADDING, self.check_width-self.CHECK_RIGHT_PADIING):
            #self.is_select = not self.is_select
        if column == 2:
            self.setting.init(self.device)
            self.slide_to_setting()
            self.send_to_crumb()

        if self.redraw_request_callback:
            self.redraw_request_callback(self)


        
if __name__=="__main__":

    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_title("Container")
    win.set_size_request(700,100)
    #win.border_width(2)

    win.connect("destroy", lambda w: gtk.main_quit())
    tree = [WirelessItem("deepinwork"), WirelessItem("myhost")]
    tv = TreeView(tree)
    tv.set_spacing = 0
    vbox = gtk.VBox(False)
    vbox.pack_start(tv)
    win.add(vbox)
    win.show_all()

    gtk.main()
