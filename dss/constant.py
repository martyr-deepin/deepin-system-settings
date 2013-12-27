#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
#             Zeng Zhi <cursorzz@gmail.com>
#             Long Changjin <admin@longchangjin.cn>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
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
    import deepin_gsettings                                                     
except ImportError:                                                             
    print "----------Please Install Deepin GSettings Python Binding----------"  
    print "git clone git@github.com:linuxdeepin/deepin-gsettings.git"           
    print "------------------------------------------------------------------"
import dbus
from deepin_utils.ipc import is_dbus_name_exists
from deepin_utils.file import get_parent_dir
from dtk.ui.locales import get_locale_code
from nls import _

MAIN_LANG = get_locale_code("deepin-system-settings", get_parent_dir(__file__, 2) + "/locale")
APP_DBUS_NAME = "com.deepin.system_settings"
APP_OBJECT_NAME = "/com/deepin/system_settings"

PAGE_WIDTH = 834
PAGE_HEIGHT = 474

HSEPARATOR_HEIGHT = 10

'''
基准线
'''
STANDARD_LINE = 260

'''
module background color
'''
MODULE_BG_COLOR = "#FFFFFF"

GOTO_FG_COLOR = "#666666"

HSCALEBAR_WIDTH = 200

# 框架类别-上下间距
FRAME_HORIZONTAL_SPACING = 4
# 框架类别-左右间距
FRAME_VERTICAL_SPACING = 4

# 框架类别-窗口左空白
FRAME_LEFT_PADDING = 20
# 框架类别-窗口上空白
FRAME_TOP_PADDING = 15

# 文字控件类别-窗口左空白
TEXT_WINDOW_LEFT_PADDING = 50
TEXT_WINDOW_TOP_PADDING = 35
# 文字控件类别-右对齐间距
TEXT_WINDOW_RIGHT_WIDGET_PADDING = 10
# 文字控件类别-提示信息宽
TIP_BOX_WIDTH = 180

# 默认文字大小 12像素对应9
CONTENT_FONT_SIZE = 9
# 标题文字大小 14像素对应10, 计算方式为 14 × 72/ 96 = 10
TITLE_FONT_SIZE = 10
# 垂直间隔
BETWEEN_SPACING = 15
# 容器高度
CONTAINNER_HEIGHT = 30
# 容器内左右间距
WIDGET_SPACING = 10

# 提示信息
STATUS_HEIGHT = 35

'''
* text widget category
image width beside title
'''
IMG_WIDTH = 16

'''
ComboBox, Label widget height
'''
WIDGET_HEIGHT = 22

WINDOW_HEIGHT = 535
WINDOW_WIDTH = 800

'''
Border color and backgroud color for treeview
'''
TREEVIEW_BORDER_COLOR = "#d2d2d2"
TREEVIEW_BG_COLOR = "#f6f6f6"

MODULES_NAME_FOR_L18N = {
        "display": _("Displays"),
        "desktop": _("Desktop"),
        "individuation": _("Personalization"),
        "sound": _("Sound"),
        "date_time": _("Date &amp; Time"),
        "power": _("Power"),
        "keyboard": _("Keyboard"),
        "mouse": _("Mouse"),
        "touchpad": _("Touchpad"),
        "printer": _("Printers"),
        "network": _("Network"),
        "bluetooth": _("Bluetooth"),
        "driver": _("Additional Drivers"),
        "account": _("User Accounts"),
        "application_associate": _("Default Applications"),
        "system_information": _("System Information"),
    }

def is_laptop():
    xrandr_settings = deepin_gsettings.new("org.gnome.settings-daemon.plugins.xrandr")
    return xrandr_settings.get_boolean("is-laptop")

def handle_dbus_reply(*reply):                                                 
    pass                                                                    
                                                                                
def handle_dbus_error(*error):                                                  
    pass                                                                    

def send_message(message_type, message_content):                                
    if is_dbus_name_exists(APP_DBUS_NAME):                                      
        bus_object = dbus.SessionBus().get_object(APP_DBUS_NAME, APP_OBJECT_NAME)
        method = bus_object.get_dbus_method("message_receiver")                 
        method(message_type,                                                    
               message_content,                                                 
               reply_handler=handle_dbus_reply,                         
               error_handler=handle_dbus_error)
