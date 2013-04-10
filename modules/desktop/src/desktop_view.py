#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Deepin, Inc.
#               2013 Zhai Xiang
# 
# Author:     Zhai Xiang <zhaixiang@linuxdeepin.com>
# Maintainer: Zhai Xiang <zhaixiang@linuxdeepin.com>
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
from deepin_utils.ipc import is_dbus_name_exists
from dtk.ui.utils import color_hex_to_cairo
from dtk.ui.line import HSeparator
from dtk.ui.box import ImageBox
from dtk.ui.label import Label
from dtk.ui.button import CheckButton, Button
from dtk.ui.combo import ComboBox
from dtk.ui.entry import InputEntry
from dtk.ui.constant import ALIGN_START, ALIGN_END
from constant import *
from nls import _
import gobject
import gtk
import dbus
import deepin_gsettings

class DesktopView(gtk.VBox):
    '''
    class docs
    '''

    LAUNCHER_CMD = "launcher --toggle"

    def __init__(self):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)

        self.desktop_settings = deepin_gsettings.new("com.deepin.dde.desktop")
        self.dock_settings = deepin_gsettings.new("com.deepin.dde.dock")
        self.compiz_integrated_settings = deepin_gsettings.new("org.compiz.integrated")
        self.compiz_core_settings = deepin_gsettings.new_with_path(
            "org.compiz.core", "/org/compiz/profiles/deepin/plugins/core/")
        self.compiz_run_command_edge_settings = deepin_gsettings.new_with_path(
            "org.compiz.commands", "/org/compiz/profiles/deepin/plugins/commands/")
        self.compiz_scale_settings = deepin_gsettings.new_with_path("org.compiz.scale", 
            "/org/compiz/profiles/deepin/plugins/scale/")
        self.compiz_grid_settings = deepin_gsettings.new_with_path("org.compiz.grid", 
            "/org/compiz/profiles/deepin/plugins/grid/")

        self.display_style_items = [(_("Default Style"), 0), 
                                    (_("Auto Hide"), 1), 
                                    (_("Invisible"), 2)]
        self.place_style_items = [(_("Buttom"), 0), 
                                  (_("Top"), 1)]
        self.icon_size_items = [(_("Default Icon"), 0), 
                                (_("Small"), 1)]
        self.hot_zone_items = [(_("Nothing"), 0), 
                               (_("Opening Window"), 1), 
                               (_("Launcher"), 2)]
        self.grid_items = [(_("Maximize"), 0), (_("Nothing"), 1)]
        '''
        icon title
        '''
        self.icon_title_align = self.__setup_title_align(
            app_theme.get_pixbuf("desktop/icon.png"), 
            _("Desktop Icon"), 
            TEXT_WINDOW_TOP_PADDING, 
            TEXT_WINDOW_LEFT_PADDING)
        '''
        icon
        '''
        self.icon_align = self.__setup_align(padding_left = 225)
        self.icon_box = gtk.HBox(spacing = WIDGET_SPACING * 3)
        self.computer_checkbutton = self.__setup_checkbutton(_("Computer"))
        self.computer_checkbutton.set_active(self.desktop_settings.get_boolean("show-computer-icon"))
        self.computer_checkbutton.connect("toggled", self.__toggled, "computer");
        self.home_checkbutton = self.__setup_checkbutton(_("Home"))
        self.home_checkbutton.set_active(self.desktop_settings.get_boolean("show-home-icon"))
        self.home_checkbutton.connect("toggled", self.__toggled, "home")
        self.trash_checkbutton = self.__setup_checkbutton(_("Trash"))
        self.trash_checkbutton.set_active(self.desktop_settings.get_boolean("show-trash-icon"))
        self.trash_checkbutton.connect("toggled", self.__toggled, "trash")
        self.dsc_checkbutton = self.__setup_checkbutton(_("Software Center"))
        self.dsc_checkbutton.set_active(self.desktop_settings.get_boolean("show-dsc-icon"))
        self.dsc_checkbutton.connect("toggled", self.__toggled, "dsc")
        self.__widget_pack_start(self.icon_box, 
                                 [self.computer_checkbutton, 
                                  self.home_checkbutton, 
                                  self.trash_checkbutton, 
                                  self.dsc_checkbutton, 
                                 ])
        self.icon_align.add(self.icon_box)
        '''
        dock title
        '''
        self.dock_title_align = self.__setup_title_align(
            app_theme.get_pixbuf("desktop/dock.png"), 
            _("Dock")) 
        '''
        display style
        '''
        self.display_style_align = self.__setup_align()
        self.display_style_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.display_style_label = self.__setup_label(_("Display Style"))
        self.display_style_combo = self.__setup_combo(self.display_style_items)
        hide_mode = self.dock_settings.get_string("hide-mode")
        hide_mode_index = 0
        if hide_mode == "default":
            hide_mode_index = 0
        elif hide_mode == "autohide":
            hide_mode_index = 1
        else:
            hide_mode_index = 2
        self.display_style_combo.set_select_index(hide_mode_index)
        self.display_style_combo.connect("item-selected", self.__combo_item_selected, "display_style")
        self.__widget_pack_start(self.display_style_box, 
            [self.display_style_label, self.display_style_combo])
        self.display_style_align.add(self.display_style_box)
        '''
        place style
        '''
        self.place_style_align = self.__setup_align()
        self.place_style_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.place_style_label = self.__setup_label(_("Place Style"))
        self.place_style_combo = self.__setup_combo(self.place_style_items)
        self.place_style_combo.set_select_index(0)
        self.place_style_combo.connect("item-selected", self.__combo_item_selected, "place_style")
        self.__widget_pack_start(self.place_style_box, 
            [self.place_style_label, self.place_style_combo])
        self.place_style_align.add(self.place_style_box)
        '''
        icon size
        '''
        self.icon_size_align = self.__setup_align()
        self.icon_size_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.icon_size_label = self.__setup_label(_("Icon Size"))
        self.icon_size_combo = self.__setup_combo(self.icon_size_items)
        self.icon_size_combo.set_select_index(0)
        if self.dock_settings.get_boolean("active-mini-mode"):
            self.icon_size_combo.set_select_index(1)
        self.icon_size_combo.connect("item-selected", self.__combo_item_selected, "icon_size")
        self.__widget_pack_start(self.icon_size_box, 
            [self.icon_size_label, self.icon_size_combo])
        self.icon_size_align.add(self.icon_size_box)
        '''
        preview
        '''
        self.preview_align = self.__setup_align()
        self.preview_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.preview_label = self.__setup_label(_("Preview"))
        self.__widget_pack_start(self.preview_box, [self.preview_label])
        self.preview_align.add(self.preview_box)
        '''
        hot zone
        '''
        self.hot_title_align = self.__setup_title_align(                       
            app_theme.get_pixbuf("desktop/hot.png"),                           
            _("Hot Zone")) 
        self.topleft_align = self.__setup_align()
        self.topleft_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.topleft_label = self.__setup_label(_("Top Left"))
        self.topleft_combo = self.__setup_combo(self.hot_zone_items)
        command1 = self.compiz_integrated_settings.get_string("command-11")
        if command1 == "":
            self.topleft_combo.set_select_index(0)
        elif command1 == self.LAUNCHER_CMD:
            self.topleft_combo.set_select_index(2)
        else:
            pass

        scale_edge_str = self.compiz_scale_settings.get_string("initiate-edge")
        if scale_edge_str == "Top Left":
            self.topleft_combo.set_select_index(1)

        self.topleft_combo.connect("item-selected", self.__combo_item_selected, "topleft")
        self.__widget_pack_start(self.topleft_box, [self.topleft_label, self.topleft_combo])
        self.topleft_align.add(self.topleft_box)
        self.topright_align = self.__setup_align()                               
        self.topright_box = gtk.HBox(spacing = WIDGET_SPACING)                   
        self.topright_label = self.__setup_label(_("Top Right"))                  
        self.topright_combo = self.__setup_combo(self.hot_zone_items)
        command2 = self.compiz_integrated_settings.get_string("command-12")          
        if command2 == "":                                                      
            self.topright_combo.set_select_index(0)                              
        elif command2 == self.LAUNCHER_CMD:                                     
            self.topright_combo.set_select_index(2)                              
        else:                                                                   
            pass
        
        if scale_edge_str == "TopRight":
            self.topright_combo.set_select_index(1)

        self.topright_combo.connect("item-selected", self.__combo_item_selected, "topright")
        self.__widget_pack_start(self.topright_box, [self.topright_label, self.topright_combo])
        self.topright_align.add(self.topright_box)
        '''
        top edge
        '''
        self.topedge_align = self.__setup_align()
        self.topedge_box = gtk.HBox(spacing = WIDGET_SPACING)
        self.topedge_label = self.__setup_label(_("Top Edge"))
        self.topedge_combo = self.__setup_combo(self.grid_items)
        top_edge_action = self.compiz_grid_settings.get_int("top-edge-action")
        if top_edge_action == 10:
            self.topedge_combo.set_select_index(0)
        else:
            self.topedge_combo.set_select_index(1)
        self.topedge_combo.connect("item-selected", self.__combo_item_selected, "topedge")
        self.__widget_pack_start(self.topedge_box, [self.topedge_label, self.topedge_combo])
        self.topedge_align.add(self.topedge_box)
        self.leftedge_align = self.__setup_align()                               
        self.leftedge_box = gtk.HBox(spacing = WIDGET_SPACING)                   
        self.leftedge_label = self.__setup_label(_("Left Edge"))                  
        self.leftedge_combo = self.__setup_combo(self.grid_items)
        left_edge_action = self.compiz_grid_settings.get_int("left-edge-action")
        if left_edge_action == 10:
            self.leftedge_combo.set_select_index(0)
        else:
            self.leftedge_combo.set_select_index(1)
        self.leftedge_combo.connect("item-selected", self.__combo_item_selected, "leftedge")
        self.__widget_pack_start(self.leftedge_box, [self.leftedge_label, self.leftedge_combo])
        self.leftedge_align.add(self.leftedge_box)
        self.rightedge_align = self.__setup_align()                               
        self.rightedge_box = gtk.HBox(spacing = WIDGET_SPACING)                   
        self.rightedge_label = self.__setup_label(_("Right Edge"))                  
        self.rightedge_combo = self.__setup_combo(self.grid_items)                
        right_edge_action = self.compiz_grid_settings.get_int("right-edge-action")
        if right_edge_action == 10:
            self.rightedge_combo.set_select_index(0)
        else:
            self.rightedge_combo.set_select_index(1)
        self.rightedge_combo.connect("item-selected", self.__combo_item_selected, "rightedge")
        self.__widget_pack_start(self.rightedge_box, [self.rightedge_label, self.rightedge_combo])
        self.rightedge_align.add(self.rightedge_box)
        '''
        greeter
        '''
        self.greeter_title_align = self.__setup_title_align(                       
            app_theme.get_pixbuf("desktop/lock.png"),                     
            _("Login &amp;&amp; Lock"),                                                  
            TEXT_WINDOW_TOP_PADDING,                                            
            TEXT_WINDOW_LEFT_PADDING)
        '''
        greeter
        '''
        self.greeter_align = self.__setup_align()
        self.greeter_box = gtk.HBox()
        self.greeter_label = self.__setup_label(_("Login Page"))
        self.greeter_entry_align = self.__setup_align(
            padding_left = WIDGET_SPACING, padding_top = 3)
        self.greeter_entry = self.__setup_entry()
        self.greeter_entry_align.add(self.greeter_entry)
        self.greeter_button = self.__setup_button(_("Select"))
        self.__widget_pack_start(self.greeter_box, 
                                 [self.greeter_label, 
                                  self.greeter_entry_align, 
                                  self.greeter_button])
        self.greeter_align.add(self.greeter_box)
        '''
        lock
        '''
        self.lock_align = self.__setup_align()
        self.lock_box = gtk.HBox()
        self.lock_label = self.__setup_label(_("Lock Page"))
        self.lock_entry_align = self.__setup_align(
            padding_left = WIDGET_SPACING, padding_top = 3)
        self.lock_entry = self.__setup_entry()
        self.lock_entry_align.add(self.lock_entry)
        self.lock_button = self.__setup_button(_("Select"))
        self.__widget_pack_start(self.lock_box, 
                                 [self.lock_label, 
                                  self.lock_entry_align, 
                                  self.lock_button])
        self.lock_align.add(self.lock_box)
        '''
        this->gtk.VBox pack_start
        '''
        self.__widget_pack_start(self, 
                                 [self.icon_title_align, 
                                  self.icon_align, 
                                  self.dock_title_align, 
                                  self.display_style_align, 
                                  #self.place_style_align, 
                                  #self.icon_size_align, 
                                  #self.preview_align, 
                                  self.hot_title_align, 
                                  self.topleft_align, 
                                  self.topright_align, 
                                  self.topedge_align, 
                                  #self.leftedge_align, 
                                  #self.rightedge_align, 
                                  #self.greeter_title_align, 
                                  #self.greeter_align, 
                                  #self.lock_align
                                 ])

        self.connect("expose-event", self.__expose)

        self.__send_message("status", ("desktop", ""))

        self.__check_active_plugins()

    def __check_active_plugins(self):
        active_plugins = self.compiz_core_settings.get_strv("active-plugins")
        
        if "commands" not in active_plugins:
            active_plugins.append("commands")
            self.compiz_core_settings.set_strv("active-plugins", active_plugins)

        if "scale" not in active_plugins:
            active_plugins.append("scale")
            self.compiz_core_settings.set_strv("active-plugins", active_plugins)

    def __toggled(self, widget, obj):
        is_toggled = widget.get_active()

        if obj == "computer":
            if is_toggled:
                self.__send_message("status", ("desktop", _("Show computer icon")))
            else:
                self.__send_message("status", ("desktop", _("Hide computer icon")))
            self.desktop_settings.set_boolean("show-computer-icon", is_toggled)
            return

        if obj == "home":
            if is_toggled:
                self.__send_message("status", ("desktop", _("Show home icon")))
            else:
                self.__send_message("status", ("desktop", _("Hide home icon")))
            self.desktop_settings.set_boolean("show-home-icon", is_toggled)
            return

        if obj == "trash":
            if is_toggled:
                self.__send_message("status", ("desktop", _("Show trash icon")))
            else:
                self.__send_message("status", ("desktop", _("Hide trash icon")))
            self.desktop_settings.set_boolean("show-trash-icon", is_toggled)
            return
        
        if obj == "dsc":                                                      
            if is_toggled:                                                      
                self.__send_message("status", ("desktop", _("Show deepin software center icon")))
            else:                                                               
                self.__send_message("status", ("desktop", _("Hide deepin software conter icon")))
            self.desktop_settings.set_boolean("show-dsc-icon", is_toggled)       
            return

    def __handle_dbus_replay(self, *reply):                                     
        pass                                                                    
                                                                                
    def __handle_dbus_error(self, *error):                                      
        pass                                                                    
                                                                                
    def __send_message(self, message_type, message_content):                    
        if is_dbus_name_exists(APP_DBUS_NAME):                                  
            bus_object = dbus.SessionBus().get_object(APP_DBUS_NAME, APP_OBJECT_NAME)
            method = bus_object.get_dbus_method("message_receiver")             
            method(message_type,                                                
                   message_content,                                             
                   reply_handler=self.__handle_dbus_replay,                     
                   error_handler=self.__handle_dbus_error)       

    def __setup_separator(self):                                                
        hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        hseparator.set_size_request(500, HSEPARATOR_HEIGHT)                                    
        return hseparator                                                       
                                                                                
    def __setup_title_label(self,                                               
                            text="",                                            
                            text_color=app_theme.get_color("globalTitleForeground"),
                            text_size=TITLE_FONT_SIZE,                          
                            text_x_align=ALIGN_START,                           
                            label_width=180):                                   
        return Label(text = text,                                               
                     text_color = text_color,                                   
                     text_size = text_size,                                     
                     text_x_align = text_x_align,                               
                     label_width = label_width, 
                     enable_select = False, 
                     enable_double_click = False)     

    def __setup_title_align(self, 
                            pixbuf, 
                            text, 
                            padding_top=FRAME_TOP_PADDING, 
                            padding_left=TEXT_WINDOW_LEFT_PADDING):
        align = self.__setup_align(padding_top = padding_top, padding_left = padding_left)              
        align_box = gtk.VBox(spacing = WIDGET_SPACING)                             
        title_box = gtk.HBox(spacing = WIDGET_SPACING)                             
        image = ImageBox(pixbuf)                                                   
        label = self.__setup_title_label(text)                                     
        separator = self.__setup_separator()                                       
        self.__widget_pack_start(title_box, [image, label])                        
        self.__widget_pack_start(align_box, [title_box, separator])                
        align.add(align_box)                                                       
        return align        

    def reset(self):
        self.__send_message("status", ("desktop", _("Reset to default value")))
        self.desktop_settings.reset("show-computer-icon")
        self.desktop_settings.reset("show-home-icon")
        self.desktop_settings.reset("show-trash-icon")
        self.desktop_settings.reset("show-dsc-icon")
        self.dock_settings.reset("hide-mode")
        self.computer_checkbutton.set_active(self.desktop_settings.get_boolean("show-computer-icon"))
        self.home_checkbutton.set_active(self.desktop_settings.get_boolean("show-home-icon"))
        self.trash_checkbutton.set_active(self.desktop_settings.get_boolean("show-trash-icon"))
        self.dsc_checkbutton.set_active(self.desktop_settings.get_boolean("show-dsc-icon"))
        hide_mode = self.dock_settings.get_string("hide-mode")                  
        hide_mode_index = 0                                                     
        if hide_mode == "default":                                              
            hide_mode_index = 0                                                 
        elif hide_mode == "autohide":                                           
            hide_mode_index = 1                                                 
        else:                                                                   
            hide_mode_index = 2                                                 
        self.display_style_combo.set_select_index(hide_mode_index)

    def __expose(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation

        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                                               
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)                                                 
        cr.fill()

    def __setup_checkbutton(self, label_text, padding_x=0):
        return CheckButton(label_text, padding_x)

    def __setup_button(self, label):
        return Button(label)

    def __setup_label(self, text="", text_size=CONTENT_FONT_SIZE, align=ALIGN_END):
        return Label(text, None, text_size, align, 200, False, False, False)

    def __setup_combo(self, items=[]):
        combo = ComboBox(items, None, 0, max_width = 285, fixed_width = 285)
        combo.set_size_request(-1, WIDGET_HEIGHT)
        return combo

    def __setup_toggle(self):                                                      
        return ToggleButton(app_theme.get_pixbuf("toggle_button/inactive_normal.png"), 
            app_theme.get_pixbuf("toggle_button/active_normal.png"))               

    def __setup_entry(self, content=""):
        entry = InputEntry(content)
        entry.set_size(215, WIDGET_HEIGHT)
        return entry

    def __setup_align(self, 
                      padding_top=8, 
                      padding_bottom=0, 
                      padding_left=TEXT_WINDOW_LEFT_PADDING + IMG_WIDTH + WIDGET_SPACING, 
                      padding_right=0):
        align = gtk.Alignment()
        align.set(0.0, 0.5, 0, 0)
        align.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        return align

    def __widget_pack_start(self, parent_widget, widgets=[]):
        if parent_widget == None:
            return
        for item in widgets:
            parent_widget.pack_start(item, False, False)

    def __combo_item_selected(self, widget, item_text=None, item_value=None, item_index=None, object=None):
        if object == "display_style":
            if item_value == 0:
                self.dock_settings.set_string("hide-mode", "default")
            elif item_value == 1:
                self.dock_settings.set_string("hide-mode", "autohide")
            elif item_value == 2:
                self.dock_settings.set_string("hide-mode", "keephidden")
            return

        if object == "icon_size":
            if item_value == 0:
                self.dock_settings.set_boolean("active-mini-mode", False)
            else:
                self.dock_settings.set_boolean("active-mini-mode", True)
            return

        if object == "topleft":
            topright_current_value = self.topright_combo.get_current_item()[1]
            if item_value == 0:
                self.compiz_integrated_settings.set_string("command-11", "")
                self.compiz_run_command_edge_settings.set_string("run-command10-edge", "")
                self.compiz_scale_settings.set_string("initiate-edge", "")
            elif item_value == 1:
                if topright_current_value == 1:
                    self.topright_combo.set_select_index(2)
                    self.compiz_integrated_settings.set_string("command-12", self.LAUNCHER_CMD)
                    self.compiz_run_command_edge_settings.set_string("run-command11-edge", "TopRight")
                    #self.compiz_scale_settings.set_string("initiate-edge", "")

                self.compiz_integrated_settings.set_string("command-11", "")
                self.compiz_run_command_edge_settings.set_string("run-command10-edge", "")
                self.compiz_scale_settings.set_string("initiate-edge", "TopLeft")
            elif item_value == 2:
                if topright_current_value == 2:
                    self.topright_combo.set_select_index(1)
                    self.compiz_integrated_settings.set_string("command-12", "")       
                    self.compiz_run_command_edge_settings.set_string("run-command11-edge", "") 
                    self.compiz_scale_settings.set_string("initiate-edge", "TopRight")
                
                self.compiz_integrated_settings.set_string("command-11", self.LAUNCHER_CMD)
                self.compiz_run_command_edge_settings.set_string("run-command10-edge", "TopLeft")
                #self.compiz_scale_settings.set_string("initiate-edge", "")
            else:
                pass
            return

        if object == "topright":                         
            topleft_current_value = self.topleft_combo.get_current_item()[1]
            if item_value == 0:
                self.compiz_integrated_settings.set_string("command-12", "")
                self.compiz_run_command_edge_settings.set_string("run-command11-edge", "")
                self.compiz_scale_settings.set_string("initiate-edge", "")         
            elif item_value == 1:
                if topleft_current_value == 1:
                    self.topleft_combo.set_select_index(2)
                    self.compiz_integrated_settings.set_string("command-11", self.LAUNCHER_CMD)
                    self.compiz_run_command_edge_settings.set_string("run-command10-edge", "TopLeft")
                    #self.compiz_scale_settings.set_string("initiate-edge", "")

                self.compiz_integrated_settings.set_string("command-12", "")
                self.compiz_run_command_edge_settings.set_string("run-command11-edge", "")
                self.compiz_scale_settings.set_string("initiate-edge", "TopRight")
            elif item_value == 2:                        
                if topleft_current_value == 2:
                    self.topleft_combo.set_select_index(1)
                    self.compiz_integrated_settings.set_string("command-11", "")    
                    self.compiz_run_command_edge_settings.set_string("run-command10-edge", "")
                    self.compiz_scale_settings.set_string("initiate-edge", "TopLeft")

                self.compiz_integrated_settings.set_string("command-12", self.LAUNCHER_CMD)
                self.compiz_run_command_edge_settings.set_string("run-command11-edge", "TopRight")
                #self.compiz_scale_settings.set_string("initiate-edge", "")
            else:                                                               
                pass                                                            
            return

        if object == "topedge":
            if item_value == 0:
                self.compiz_grid_settings.set_int("top-edge-action", 10)
            else:
                self.compiz_grid_settings.set_int("top-edge-action", 0)
            return

        if object == "leftedge":                                                 
            if item_value == 0:                                                    
                self.compiz_grid_settings.set_int("left-edge-action", 4)        
            else:                                                               
                self.compiz_grid_settings.set_int("left-edge-action", 0)         
            return

        if object == "rightedge":                                                 
            if item_value == 0:                                                    
                self.compiz_grid_settings.set_int("right-edge-action", 4)        
            else:                                                               
                self.compiz_grid_settings.set_int("right-edge-action", 0)         
            return

gobject.type_register(DesktopView)        
