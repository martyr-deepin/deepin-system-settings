#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Zhai Xiang
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

try:
    import deepin_xrandr
except ImportError:
    print "----------Please Install Deepin XRandR Python Binding----------"
    print "git clone git@github.com:linuxdeepin/deepin-xrandr.git"
    print "---------------------------------------------------------------"

try:
    import deepin_gsettings
except ImportError:
    print "----------Please Install Deepin GSettings Python Binding----------"
    print "git clone git@github.com:linuxdeepin/deepin-gsettings.git"
    print "------------------------------------------------------------------"

import re
import os
from xml.dom import minidom
from deepin_utils.process import run_command

class DisplayManager:
    BIG_NUM = 0
    
    def __init__(self):
        self.__deepin_xrandr = deepin_xrandr.new()
        self.__xrandr_settings = deepin_gsettings.new("org.gnome.settings-daemon.plugins.xrandr")
        self.__power_settings = deepin_gsettings.new("org.gnome.settings-daemon.plugins.power")
        self.__session_settings = deepin_gsettings.new("org.gnome.desktop.session")
        self.__screensaver_settings = deepin_gsettings.new("org.gnome.desktop.screensaver")

        self.__output_count = 0

        self.__monitors_xml_filename = "%s/.config/monitors.xml" % os.path.expanduser('~')
        if not os.path.exists(self.__monitors_xml_filename):
            self.__create_monitors_xml()

        self.__xmldoc = minidom.parse(self.__monitors_xml_filename) 
        self.__primary_output_name = None
        self.__output_names = []
        self.__output_info_by_xml = []

        self.init_xml()

    def __del__(self):
        self.__deepin_xrandr.delete()
        self.__deepin_xrandr = None
        self.__xrandr_settings.delete()
        self.__xrandr_settings = None
        self.__power_settings.delete()
        self.__power_settings = None
        self.__session_settings.delete()
        self.__session_settings = None

    def reset(self):
        self.__power_settings.reset("sleep-display-battery")
        self.__power_settings.reset("sleep-display-ac")
        self.__session_settings.reset("idle-delay")
        self.__xrandr_settings.reset("copy-multi-monitors")           
        self.__xrandr_settings.reset("only-monitor-shown")
        self.__xrandr_settings.reset("extend-multi-monitors")

    def __create_monitors_xml(self):
        pass
    
    '''
    TODO: Only shown connected outputs
    '''
    def init_xml(self):
        self.__xmldoc = minidom.parse(self.__monitors_xml_filename)
        tmp_list = []

        if self.__xmldoc != None:
            outputs = self.__xmldoc.getElementsByTagName("output")
       
            del self.__output_info_by_xml[:]
            for output in outputs:
                output_name = output.attributes["name"].value
                
                if not self.is_output_connected(output_name):
                    continue
                
                width = output.getElementsByTagName("width")
                height = output.getElementsByTagName("height")
                x = output.getElementsByTagName("x")
                y = output.getElementsByTagName("y")
                rotation = output.getElementsByTagName("rotation")
                primary = output.getElementsByTagName("primary")
                is_primary = False
            
                if len(width) == 0 or len(height) == 0 or len(x) ==0 or len(y) == 0 or len(rotation) == 0 or len(primary) == 0:
                    continue

                if output_name in tmp_list:
                    continue
                else:
                    tmp_list.append(output_name)
            
                '''
                TODO: self.__output_info_by_xml {
                          output_name, 
                          screen_size, 
                          x, 
                          y, 
                          rotation, 
                          is_primary
                      }
                '''
                if self.__getText(primary[0].childNodes) == "yes":
                    is_primary = True
                output_item = (output_name, 
                               "%sx%s" % (self.__getText(width[0].childNodes), self.__getText(height[0].childNodes)), 
                               self.__getText(x[0].childNodes), 
                               self.__getText(y[0].childNodes), 
                               self.__getText(rotation[0].childNodes), 
                               is_primary)
                if is_primary:
                    self.__primary_output_name = output_name
                    self.__output_info_by_xml.insert(0, output_item)
                else:
                    self.__output_info_by_xml.append(output_item)
                '''
                TODO: outputs total count
                '''
                self.__output_count += 1
    
            '''
            TODO: gnome-settings-daemon generated monitors.xml
                  but there is no primary output defined! wired!
            '''
            if self.__primary_output_name == None:
                self.__primary_output_name = self.__output_info_by_xml[0][0]
   
    def get_output_count(self):
        return len(self.__output_names)

    def get_output_info(self):
        return self.__output_info_by_xml
    
    def __update_xml(self, 
                     output_name=None, 
                     width_value=None, 
                     height_value=None, 
                     x_value=None, 
                     y_value=None, 
                     rotation_value=None):
        outputs = self.__xmldoc.getElementsByTagName("output")
        
        for output in outputs:
            if output_name != output.attributes["name"].value:
                continue

            width = output.getElementsByTagName("width")
            height = output.getElementsByTagName("height")
            x = output.getElementsByTagName("x")
            y = output.getElementsByTagName("y")
            rotation = output.getElementsByTagName("rotation")

            if len(width) == 0 or len(height) == 0 or len(x) == 0 or len(y) == 0 or len(rotation) == 0:
                continue

            if width_value != None:
                width[0].firstChild.data = width_value

            if height_value != None:
                height[0].firstChild.data = height_value

            if x_value != None:
                x[0].firstChild.data = x_value

            if y_value != None:
                y[0].firstChild.data = y_value

            if rotation_value != None:
                rotation[0].firstChild.data = rotation_value

        f = open(self.__monitors_xml_filename, 'w')
        self.__xmldoc.writexml(f)
        f.close()
    
    def __getText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def get_xrandr_settings(self):
        return self.__xrandr_settings
    
    def get_primary_output_name(self):
        return self.__primary_output_name
    
    def get_output_name_index(self, output_name, items):
        i = 0

        for item in items:
            if item[1] == output_name:
                return i

            i += 1

        return 0
    
    def get_primary_output_name_index(self, items):
        i = 0
        
        for item in items:
            if item[1] == self.__primary_output_name:
                return i

            i += 1

        return 0
    
    def get_output_name(self, ori_output_name):
        pattern = re.compile(r"(.*?) \((.*?)\)")
        result = pattern.search(ori_output_name)
        if result == None:
            return ("", "")
        else:
            return (result.group(1), result.group(2))
    
    def get_output_display_name(self, output_name_value):
        output_names = self.__xrandr_settings.get_strv("output-names")
        i = 0

        while i < len(output_names):
            (output_display_name, output_name) = self.get_output_name(output_names[i])
            if output_name == output_name_value:
                return output_display_name
            
            i += 1

        return ""
    
    def is_output_connected(self, output_name_value):
        output_names = self.__xrandr_settings.get_strv("output-names")
        i = 0

        while i < len(output_names):
            (output_display_name, output_name) = self.get_output_name(output_names[i])
            if output_name == output_name_value:
                return True
            
            i += 1

        return False
    
    def get_output_names(self):
        output_names = self.__xrandr_settings.get_strv("output-names")
        i = 0

        del self.__output_names[:]
        while i < len(output_names):
            '''
            TODO: NULL means disconnected
            '''
            if output_names[i] != "NULL":
                self.__output_names.append(output_names[i])

            i += 1
 
        return self.__output_names

    def get_screen_sizes(self, output_name):
        ret_sizes = []
        screen_sizes = self.__deepin_xrandr.get_screen_sizes(output_name)
        i = 0
        
        while i < len(screen_sizes):
            if not screen_sizes[i] in ret_sizes:
                ret_sizes.append(screen_sizes[i])

            i += 1
        
        return ret_sizes

    def get_screen_size(self, output_name):
        i = 0

        while i < len(self.__output_info_by_xml):
            if self.__output_info_by_xml[i][0] == output_name:
                return self.__output_info_by_xml[i][1]

            i += 1

        return ""

    def get_same_sizes(self, primary_sizes, other_sizes):
        i = 0
        j = 0
        same_sizes = []

        while i < len(primary_sizes):
            j = 0
            while j < len(other_sizes):
                if (primary_sizes[i] == other_sizes[j]):
                    same_sizes.append(primary_sizes[i])

                j += 1

            i += 1

        return same_sizes

    def get_screen_size_index(self, output_name, items):
        screen_size = self.get_screen_size(output_name)
        i = 0
        
        for item in items:
            if item[0] == screen_size:
                return i
            i += 1

        return 0
    
    def set_screen_size(self, output_name, size):
        m = re.match('(\d+)x(\d+)', size)
        
        self.__update_xml(output_name, m.group(1), m.group(2))

        run_command("xrandr --output %s --mode %s" % (output_name, size))

    def set_screen_pos(self, output_name_value, x_value, y_value):
        self.__update_xml(output_name = output_name_value, x = x_value, y = y_value)

    def get_screen_rotation(self, output_name):
        i = 0

        while i < len(self.__output_info_by_xml):
            if self.__output_info_by_xml[i][0] == output_name:
                return self.__output_info_by_xml[i][4]

            i += 1

        return ""

    def get_screen_rotation_index(self, output_name):
        rotation = self.get_screen_rotation(output_name)

        if rotation == "normal":
            return 0
        if rotation == "right":
            return 1
        if rotation == "left":
            return 2
        if rotation == "inverted":
            return 3
        
        return 0
   
    def is_copy_monitors(self):
        return self.__xrandr_settings.get_boolean("copy-multi-monitors")

    def get_multi_monitor_index(self):
        only_monitor_shown = self.__xrandr_settings.get_int("only-monitor-shown")
        
        if self.__xrandr_settings.get_boolean("copy-multi-monitors"):
            return 0

        if self.__xrandr_settings.get_boolean("extend-multi-monitors"):
            return 1

        if only_monitor_shown:
            return only_monitor_shown + 1
        
        return 0

    def set_multi_monitor(self, value):
        if value == 1:
            self.__xrandr_settings.set_boolean("copy-multi-monitors", True)
            self.__xrandr_settings.set_boolean("extend-multi-monitors", False)
            self.__xrandr_settings.set_int("only-monitor-shown", 0)
            return

        if value == 2:
            self.__xrandr_settings.set_boolean("copy-multi-monitors", False)        
            self.__xrandr_settings.set_boolean("extend-multi-monitors", True)  
            self.__xrandr_settings.set_int("only-monitor-shown", 0)  
            return

        if value == 3:
            self.__xrandr_settings.set_boolean("copy-multi-monitors", False)        
            self.__xrandr_settings.set_boolean("extend-multi-monitors", False)  
            self.__xrandr_settings.set_int("only-monitor-shown", 1)  
            return

        if value == 4:
            self.__xrandr_settings.set_boolean("copy-multi-monitors", False)        
            self.__xrandr_settings.set_boolean("extend-multi-monitors", False)  
            self.__xrandr_settings.set_int("only-monitor-shown", 2)  
            return

    def set_screen_rotation(self, output_name_value, rotation):
        rotation_str = "normal"
        i = 0

        if rotation == 1:
            rotation_str = "normal"
        elif rotation == 2:
            rotation_str = "right"
        elif rotation == 3:
            rotation_str = "left"
        elif rotation == 4:
            rotation_str = "inverted"
        
        
        while i < len(self.__output_names):
            (output_display_name, output_name) = self.get_output_name(self.__output_names[i])
            self.__update_xml(output_name = output_name, 
                              rotation_value = rotation_str)

            i += 1

        run_command("xrandr -o %s" % rotation_str)

    def get_screen_brightness(self):
        return self.__xrandr_settings.get_double("brightness")
    
    def set_screen_brightness(self, output_name, value):
        if value < 0.1 or value > 1.0:
            return

        self.__xrandr_settings.set_double("brightness", value)

    def is_enable_close_monitor(self):
        if self.__power_settings.get_int("sleep-display-battery") < self.BIG_NUM:
            return True

        return False
    
    '''
    TODO: unit is second
    '''
    def get_close_monitor(self):
        '''
        TODO: I use notebook so consider battery at first :)
        '''
        return self.__power_settings.get_int("sleep-display-battery")

    def __get_duration_index(self, value, items):
        i = 0

        for item in items:
            if item[1] == value:
                return i

            i += 1

        return 0
    
    def get_close_monitor_index(self, items):
        return self.__get_duration_index(self.get_close_monitor() / 60, items)

    def set_close_monitor(self, value):
        self.__power_settings.set_int("idle-dim-time", value * 60)
        self.__power_settings.set_int("sleep-display-battery", value * 60)
        self.__power_settings.set_int("sleep-display-ac", value * 60)

    def is_enable_lock_display(self):
        if self.__session_settings.get_uint("idle-delay") == self.BIG_NUM:
            return False

        return True
    
    '''
    TODO: unit is second
    '''
    def get_lock_display(self):
        return self.__session_settings.get_uint("idle-delay")

    def get_lock_display_index(self, items):
        return self.__get_duration_index(self.get_lock_display() / 60, items)

    def set_lock_display(self, value):
        self.__session_settings.set_uint("idle-delay", value * 60)
