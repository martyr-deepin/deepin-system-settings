#! /usr/bin/env python

from setuptools import setup, Extension
import os
import commands

def pkg_config_cflags(pkgs):
    '''List all include paths that output by `pkg-config --cflags pkgs`'''
    return map(lambda path: path[2::], commands.getoutput('pkg-config --cflags-only-I %s' % (' '.join(pkgs))).split())

deepin_tzmap_mod = Extension('deepin_tzmap', 
                include_dirs = pkg_config_cflags(['gtk+-2.0', 'pygtk-2.0']) + ['/usr/include/deepin_tzmap'],
                libraries = ['glib-2.0', 'deepin_tzmap'], 
                sources = ['deepin_tzmap_python.c'])

setup(name='deepin_tzmap',
      version='0.1',
      ext_modules = [deepin_tzmap_mod],
      description='Deepin cc-timezone-map Gtk Widget Python Binding.',
      long_description ="""Deepin cc-timezone-map Gtk Widget Python Binding.""",
      author='Linux Deepin Team',
      author_email='zhaixiang@linuxdeepin.com',
      license='GPL-3',
      url="https://github.com/linuxdeepin/deepin-system-settings",
      download_url="git@github.com:linuxdeepin/deepin-system-settings.git",
      platforms = ['Linux'],
      )
