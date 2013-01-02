#! /usr/bin/env python

from setuptools import setup, Extension
import os
import commands

def pkg_config_cflags(pkgs):
    '''List all include paths that output by `pkg-config --cflags pkgs`'''
    return map(lambda path: path[2::], commands.getoutput('pkg-config --cflags-only-I %s' % (' '.join(pkgs))).split())

deepin_lunar_mod = Extension('deepin_lunar', 
                include_dirs = pkg_config_cflags(['gtk+-2.0', 'pygtk-2.0', 'lunar-calendar-3.0']),
                libraries = ['lunar-calendar-3.0'], 
                sources = ['deepin_lunar_python.c'])

setup(name='deepin_lunar',
      version='0.1',
      ext_modules = [deepin_lunar_mod],
      description='Deepin Lunar Calendar Gtk Widget Python Binding.',
      long_description ="""Deepin Lunar Calendar Gtk Widget Python Binding.""",
      author='Linux Deepin Team',
      author_email='zhaixiang@linuxdeepin.com',
      license='GPL-3',
      url="https://github.com/linuxdeepin/deepin-system-settings",
      download_url="git@github.com:linuxdeepin/deepin-system-settings.git",
      platforms = ['Linux'],
      )
