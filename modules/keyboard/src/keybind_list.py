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
from treeitem import SelectItem

media_shortcuts_group_dict = {
    _('System') : [
        {'name': "logout", 'description': _("Log out")},
        {'name': "screensaver", 'description': _("Lock screen")}],
    _('Launchers') : [
        {'name': "help", 'description': _("Launch help browser")},
        {'name': "calculator", 'description': _("Launch calculator")},
        {'name': "email", 'description': _("Launch email client")},
        {'name': "www", 'description': _("Launch web browser")},
        {'name': "search", 'description': _("Search")}],
    _('Sound and Media') : [
        {'name': "volume-mute", 'description': _("Volume mute")},
        {'name': "volume-down", 'description': _("Volume down")},
        {'name': "volume-up", 'description': _("Volume up")},
        {'name': "media", 'description': _("Launch media player")},
        {'name': "play", 'description': _("Play (or play/pause)")},
        {'name': "pause", 'description': _("Pause playback")},
        {'name': "stop", 'description': _("Stop playback")},
        {'name': "previous", 'description': _("Previous track")},
        {'name': "next", 'description': _("Next track")},
        {'name': "eject", 'description': _("Eject")}],
    _('Screenshots') : [
        {'name': "screenshot", 'description': _("Take a screenshot")},
        {'name': "window-screenshot", 'description': _("Take a screenshot of a window")},
        #{'name': "area-screenshot", 'description': _("Take a screenshot of an area")},
        #{'name': "screenshot-clip", 'description': _("Copy a screenshot to clipboard")},
        #{'name': "window-screenshot-clip", 'description': _("Copy a screenshot of a window to clipboard")},
        #{'name': "area-screenshot-clip", 'description': _("Copy a screenshot of an area to clipboard")}
        ],
    _('Universal Access') : [
        {'name': "magnifier", 'description': _("Turn zoom on or off")},
        {'name': "magnifier-zoom-in", 'description': _("Zoom in")},
        {'name': "magnifier-zoom-out", 'description': _("Zoom out")},
        {'name': "screenreader", 'description': _("Turn screen reader on or off")},
        {'name': "on-screen-keyboard", 'description': _("Turn on-screen keyboard on or off")},
        {'name': "increase-text-size", 'description': _("Increase text size")},
        {'name': "decrease-text-size", 'description': _("Decrease text size")},
        {'name': "toggle-contrast", 'description': _("High contrast on or off")}]
    }

wm_shortcuts_group_dict = {
    _('Navigation') : [
    {'name': "move-to-workspace-1", 'description': _("Move window to workspace 1")},
    {'name': "move-to-workspace-2", 'description': _("Move window to workspace 2")},
    {'name': "move-to-workspace-3", 'description': _("Move window to workspace 3")},
    {'name': "move-to-workspace-4", 'description': _("Move window to workspace 4")},
    #{'name': "move-to-workspace-5", 'description': _("Move window to workspace 5")},
    #{'name': "move-to-workspace-6", 'description': _("Move window to workspace 6")},
    #{'name': "move-to-workspace-7", 'description': _("Move window to workspace 7")},
    #{'name': "move-to-workspace-8", 'description': _("Move window to workspace 8")},
    #{'name': "move-to-workspace-9", 'description': _("Move window to workspace 9")},
    #{'name': "move-to-workspace-10", 'description': _("Move window to workspace 10")},
    #{'name': "move-to-workspace-11", 'description': _("Move window to workspace 11")},
    #{'name': "move-to-workspace-12", 'description': _("Move window to workspace 12")},
    {'name': "move-to-workspace-left", 'description': _("Move window one workspace to the left")},
    {'name': "move-to-workspace-right", 'description': _("Move window one workspace to the right")},
    {'name': "move-to-workspace-up", 'description': _("Move window one workspace up")},
    {'name': "move-to-workspace-down", 'description': _("Move window one workspace down")},
    #
    #{'name': "switch-group", 'description': _("Switch windows of an application")},
    #{'name': "switch-group-backward", 'description': _("Reverse switch windows of an application")},
    {'name': "switch-windows", 'description': _("Switch applications")},
    {'name': "switch-windows-backward", 'description': _("Reverse switch applications")},
    #{'name': "switch-panels", 'description': _("Switch system controls")},
    #{'name': "switch-panels-backward", 'description': _("Reverse switch system controls")},
    #{'name': "cycle-group", 'description': _("Switch windows of an app directly")},
    #{'name': "cycle-group-backward", 'description': _("Reverse switch windows of an app directly")},
    #{'name': "cycle-windows", 'description': _("Switch windows directly")},
    #{'name': "cycle-windows-backward", 'description': _("Reverse switch windows directly")},
    #{'name': "cycle-panels", 'description': _("Switch system controls directly")},
    #{'name': "cycle-panels-backward", 'description': _("Reverse switch system controls directly")},
    #
    {'name': "switch-to-workspace-1", 'description': _("Switch to workspace 1")},
    {'name': "switch-to-workspace-2", 'description': _("Switch to workspace 2")},
    {'name': "switch-to-workspace-3", 'description': _("Switch to workspace 3")},
    {'name': "switch-to-workspace-4", 'description': _("Switch to workspace 4")},
    #{'name': "switch-to-workspace-5", 'description': _("Switch to workspace 5")},
    #{'name': "switch-to-workspace-6", 'description': _("Switch to workspace 6")},
    #{'name': "switch-to-workspace-7", 'description': _("Switch to workspace 7")},
    #{'name': "switch-to-workspace-8", 'description': _("Switch to workspace 8")},
    #{'name': "switch-to-workspace-9", 'description': _("Switch to workspace 9")},
    #{'name': "switch-to-workspace-10", 'description': _("Switch to workspace 10")},
    #{'name': "switch-to-workspace-11", 'description': _("Switch to workspace 11")},
    #{'name': "switch-to-workspace-12", 'description': _("Switch to workspace 12")},
    {'name': "switch-to-workspace-left", 'description': _("Switch to workspace left")},
    {'name': "switch-to-workspace-right", 'description': _("Switch to workspace right")},
    {'name': "switch-to-workspace-up", 'description': _("Switch to workspace above")},
    {'name': "switch-to-workspace-down", 'description': _("Switch to workspace below")},
    ],
    _('Windows') : [
    {'name': "show-desktop", 'description': _("Show desktop")},
    #{'name': "panel-main-menu", 'description': _("Show the activities overview")},
    #{'name': "panel-run-dialog", 'description': _("Show the run command prompt")},
    {'name': "activate-window-menu", 'description': _("Activate the window menu")},
    {'name': "toggle-fullscreen", 'description': _("Toggle fullscreen mode")},
    {'name': "toggle-maximized", 'description': _("Toggle maximization state")},
    {'name': "toggle-above", 'description': _("Toggle window always appearing on top")},
    {'name': "maximize", 'description': _("Maximize window")},
    {'name': "unmaximize", 'description': _("Restore window")},
    {'name': "toggle-shaded", 'description': _("Toggle shaded state")},
    {'name': "minimize", 'description': _("Minimize window")},
    {'name': "close", 'description': _("Close window")},
    {'name': "begin-move", 'description': _("Move window")},
    {'name': "begin-resize", 'description': _("Resize window")},
    #{'name': "toggle-on-all-workspaces", 'description': _("Toggle window on all workspaces or one")},
    #{'name': "raise-or-lower", 'description': _("Raise window if covered, otherwise lower it")},
    #{'name': "raise", 'description': _("Raise window above other windows")},
    #{'name': "lower", 'description': _("Lower window below other windows")},
    #{'name': "maximize-vertically", 'description': _("Maximize window vertically")},
    #{'name': "maximize-horizontally", 'description': _("Maximize window horizontally")},
    #
    {'name': "move-to-corner-nw", 'description': _("Move window to top left corner")},
    {'name': "move-to-corner-ne", 'description': _("Move window to top right corner")},
    {'name': "move-to-corner-sw", 'description': _("Move window to bottom left corner")},
    {'name': "move-to-corner-se", 'description': _("Move window to bottom right corner")},
    {'name': "move-to-side-n", 'description': _("Move window to top edge of screen")},
    {'name': "move-to-side-s", 'description': _("Move window to bottom edge of screen")},
    {'name': "move-to-side-e", 'description': _("Move window to right side of screen")},
    {'name': "move-to-side-w", 'description': _("Move window to left side of screen")},
    {'name': "move-to-center", 'description': _("Move window to center of screen")},
    ]
    }

def get_wm_shortcuts_select_item():
    '''
    @return: a list SelectItem
    '''
    items = []
    for i in wm_shortcuts_group_dict:
        items.append(SelectItem(i))
    return items

def get_media_shortcuts_select_item():
    '''
    @return: a list SelectItem
    '''
    items = []
    for i in media_shortcuts_group_dict:
        items.append(SelectItem(i))
    return items
