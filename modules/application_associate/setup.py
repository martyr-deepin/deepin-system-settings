#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
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

from setuptools import setup, Extension
import commands

def pkg_config_cflags(pkgs):
    return map(lambda path: path[2::], commands.getoutput('pkg-config --cflags-only-I %s' % (' '.join(pkgs))).split())
    
app_mod = Extension('gdesktopapp',
                                 include_dirs = pkg_config_cflags(['gio-unix-2.0']),
                                 libraries = ['gio-unix-2.0'],
                                 sources = ['appinfo.c']
                                 )


setup(name = 'gdesktopapp',
      version = '0.1',
      ext_modules = [app_mod],
      description = "python bindings for GDesktopAppInfo",
      long_description = '''python bindings for GDesktopAppInfo''',
      author = 'Linux Deepin Team',
      author_email = 'longwei@linuxdeepin.com',
      license = 'GPL-3',
      url = "www.linuxdeepin.com",
      download_url = "www.linuxdeepin.com",
      platforms = ['Linux']

      )
