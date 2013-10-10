#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
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

from nls import _
TYPE_WM = 0
TYPE_MEDIA = 1
TYPE_DP = 2
TYPE_COMPIZ = 3

TYPE_STRING = 4
TYPE_STRV = 5

shortcuts_group_dict = {
    _('System') : [
        {'type': TYPE_DP, 'name': "key1", 'description': _("Launcher"), 'value-type': TYPE_STRING, 'command': "/usr/bin/launcher"},              # 启动器
        {'type': TYPE_WM, 'name': "show-desktop", 'description': _("Show desktop"), 'value-type': TYPE_STRV},        # 显示桌面
        #{'type': TYPE_MEDIA, 'name': "screensaver", 'description': _(""), 'value-type': TYPE_STRING},      # 锁屏
        {'type': TYPE_DP, 'name': "key3", 'description': _("Lock screen"), 'value-type': TYPE_STRING, 'command': "/usr/bin/dlock"},              # 启动器
        {'type': TYPE_DP, 'name': "key11", 'description': _("File manager"), 'value-type': TYPE_STRING, 'command': "/usr/bin/nautilus"},            # 文件管理器
        {'type': TYPE_WM, 'name': "switch-windows", 'description': _("Switch applications"), 'value-type': TYPE_STRV},                   # 应用程序切换
        {'type': TYPE_WM, 'name': "switch-windows-backward", 'description': _("Reverse switch applications"), 'value-type': TYPE_STRV},  # 应用程序反向切换
        {'type': TYPE_COMPIZ, 'plugin': "shift", 'name': "next-key", 'description': _("Switch applications with 3D effect"), 'value-type': TYPE_STRING},             # 应用程序3D切换
        {'type': TYPE_COMPIZ, 'plugin': "shift", 'name': "prev-key", 'description': _("Reverse switch applications with 3D effect"), 'value-type': TYPE_STRING},     # 应用程序3D反向
        {'type': TYPE_DP, 'name': "key4", 'description': _("Show/Hide the dock"), 'value-type': TYPE_STRING, 'command': "dbus-send --type=method_call --dest=com.deepin.dde.dock /com/deepin/dde/dock com.deepin.dde.dock.ToggleShow"},     # 显示/隐藏Dock
        #{'type': TYPE_MEDIA, 'name': "help", 'description': _("Launch user manual"), 'value-type': TYPE_STRING},
        # {'type': TYPE_DP, 'name': "key6", 'description': _("Launch user manual"), 'value-type': TYPE_STRING, 'command': '/usr/bin/deepin-user-manual'},
        #{'type': TYPE_MEDIA, 'name': "screenshot", 'description': _("Take a screenshot"), 'value-type': TYPE_STRING},  # 截图
        {'type': TYPE_DP, 'name': "key7", 'description': _("Take a screenshot"), 'value-type': TYPE_STRING, 'command': '/usr/bin/deepin-screenshot'},  # 截图
        #{'type': TYPE_MEDIA, 'name': "area-screenshot", 'description': _("Take a screenshot of full screen"), 'value-type': TYPE_STRING},
        {'type': TYPE_DP, 'name': "key8", 'description': _("Take a screenshot of full screen"), 'value-type': TYPE_STRING, 'command': '/usr/bin/deepin-screenshot -f'},
        #{'type': TYPE_MEDIA, 'name': "window-screenshot", 'description': _("Take a screenshot of a window"), 'value-type': TYPE_STRING},
        {'type': TYPE_DP, 'name': "key9", 'description': _("Take a screenshot of a window"), 'value-type': TYPE_STRING, 'command': '/usr/bin/deepin-screenshot -w'},
        #{'type': TYPE_MEDIA, 'name': "screenshot-delay", 'description': _("Take a screenshot delayed"), 'value-type': TYPE_STRING},
        {'type': TYPE_DP, 'name': "key10", 'description': _("Take a screenshot delayed"), 'value-type': TYPE_STRING, 'command': '/usr/bin/deepin-screenshot -d 5'},
        #{'type': TYPE_DP, 'name': "key2", 'description': _("Terminal"), 'value-type': TYPE_STRING, 'command': "/usr/bin/gnome-terminal"},
        {'type': TYPE_DP, 'name': "key2", 'description': _("Deepin terminal"), 'value-type': TYPE_STRING, 'command': "deepin-terminal"},
        {'type': TYPE_DP, 'name': "key6", 'description': _("Deepin terminal quake mode"), 'value-type': TYPE_STRING, 'command': 'deepin-terminal --quake-mode'},
        #{'type': TYPE_MEDIA, 'name': "logout", 'description': _("Log out"), 'value-type': TYPE_STRING}],
        {'type': TYPE_DP, 'name': "key5", 'description': _("Log out"), 'value-type': TYPE_STRING, 'command': 'python /usr/share/deepin-system-settings/modules/power/src/tray_shutdown_plugin.py logout'}],
    _('Sound and Media') : [
        {'type': TYPE_MEDIA, 'name': "calculator", 'description': _("Launch calculator"), 'value-type': TYPE_STRING},
        {'type': TYPE_MEDIA, 'name': "email", 'description': _("Launch email client"), 'value-type': TYPE_STRING},
        {'type': TYPE_MEDIA, 'name': "www", 'description': _("Launch web browser"), 'value-type': TYPE_STRING},
        {'type': TYPE_MEDIA, 'name': "media", 'description': _("Launch media player"), 'value-type': TYPE_STRING},
        {'type': TYPE_MEDIA, 'name': "play", 'description': _("Play (or play/pause)"), 'value-type': TYPE_STRING},
        {'type': TYPE_MEDIA, 'name': "pause", 'description': _("Pause playback"), 'value-type': TYPE_STRING},
        {'type': TYPE_MEDIA, 'name': "stop", 'description': _("Stop playback"), 'value-type': TYPE_STRING},
        {'type': TYPE_MEDIA, 'name': "volume-mute", 'description': _("Volume mute"), 'value-type': TYPE_STRING},
        {'type': TYPE_MEDIA, 'name': "volume-down", 'description': _("Volume down"), 'value-type': TYPE_STRING},
        {'type': TYPE_MEDIA, 'name': "volume-up", 'description': _("Volume up"), 'value-type': TYPE_STRING},
        {'type': TYPE_MEDIA, 'name': "previous", 'description': _("Previous track"), 'value-type': TYPE_STRING},
        {'type': TYPE_MEDIA, 'name': "next", 'description': _("Next track"), 'value-type': TYPE_STRING},
        {'type': TYPE_MEDIA, 'name': "eject", 'description': _("Eject"), 'value-type': TYPE_STRING}],
    _("Windows") : [
        {'type': TYPE_WM, 'name': "close", 'description': _("Close window"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "maximize", 'description': _("Maximize window"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "unmaximize", 'description': _("Restore window"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "minimize", 'description': _("Minimize window"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "begin-move", 'description': _("Move window"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "begin-resize", 'description': _("Resize window"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "toggle-shaded", 'description': _("Toggle shaded state"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "activate-window-menu", 'description': _("Activate the window menu"), 'value-type': TYPE_STRV}],
    _("Workspace") : [
        {'type': TYPE_WM, 'name': "switch-to-workspace-1", 'description': _("Switch to workspace 1"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "switch-to-workspace-2", 'description': _("Switch to workspace 2"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "switch-to-workspace-3", 'description': _("Switch to workspace 3"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "switch-to-workspace-4", 'description': _("Switch to workspace 4"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "switch-to-workspace-left", 'description': _("Switch to workspace left"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "switch-to-workspace-right", 'description': _("Switch to workspace right"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "switch-to-workspace-up", 'description': _("Switch to workspace above"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "switch-to-workspace-down", 'description': _("Switch to workspace below"), 'value-type': TYPE_STRV},
        {'type': TYPE_COMPIZ, 'plugin': 'put', 'name': "put-viewport-1-key", 'description': _("Move window to workspace 1"), 'value-type': TYPE_STRING},
        {'type': TYPE_COMPIZ, 'plugin': 'put', 'name': "put-viewport-2-key", 'description': _("Move window to workspace 2"), 'value-type': TYPE_STRING},
        {'type': TYPE_COMPIZ, 'plugin': 'put', 'name': "put-viewport-3-key", 'description': _("Move window to workspace 3"), 'value-type': TYPE_STRING},
        {'type': TYPE_COMPIZ, 'plugin': 'put', 'name': "put-viewport-4-key", 'description': _("Move window to workspace 4"), 'value-type': TYPE_STRING},
        #{'type': TYPE_WM, 'name': "move-to-workspace-1", 'description': _("Move window to workspace 1"), 'value-type': TYPE_STRV},
        #{'type': TYPE_WM, 'name': "move-to-workspace-2", 'description': _("Move window to workspace 2"), 'value-type': TYPE_STRV},
        #{'type': TYPE_WM, 'name': "move-to-workspace-3", 'description': _("Move window to workspace 3"), 'value-type': TYPE_STRV},
        #{'type': TYPE_WM, 'name': "move-to-workspace-4", 'description': _("Move window to workspace 4"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "move-to-workspace-left", 'description': _("Move window one workspace to the left"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "move-to-workspace-right", 'description': _("Move window one workspace to the right"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "move-to-workspace-up", 'description': _("Move window one workspace up"), 'value-type': TYPE_STRV},
        {'type': TYPE_WM, 'name': "move-to-workspace-down", 'description': _("Move window one workspace down"), 'value-type': TYPE_STRV}],
}
