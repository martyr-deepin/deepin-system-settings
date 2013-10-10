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


if __name__ == '__main__':
    import deepin_gsettings
    import subprocess

    dde = deepin_gsettings.new("com.deepin.desktop.default-applications.terminal")
    dde_terminal = dde.get_string('exec')

    gnome = deepin_gsettings.new("org.gnome.desktop.default-applications.terminal")
    gnome_terminal = gnome.get_string('exec')

    if dde_terminal:
        print "open terminal:", dde_terminal
        subprocess.Popen(dde_terminal)
    elif gnome_terminal:
        print "open terminal:", gnome_terminal
        subprocess.Popen(gnome_terminal)
    else:
        print "open terminal: gnome-terminal"
        subprocess.Popen('gnome-terminal')
