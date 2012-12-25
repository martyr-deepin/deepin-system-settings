#! /usr/bin/env python

from setuptools import setup, Extension
import os
import commands

deepin_tz_mod = Extension('deepin_tz', 
                sources = ['deepin_tz.c'])

setup(name='deepin_tz',
      version='0.1',
      ext_modules = [deepin_tz_mod],
      description='Deepin TimeZone Python Binding.',
      long_description ="""Deepin TimeZone Python Binding.""",
      author='Linux Deepin Team',
      author_email='zhaixiang@linuxdeepin.com',
      license='GPL-3',
      url="https://github.com/linuxdeepin/deepin-system-settings/tree/master/modules/date_time/src",
      download_url="git@github.com:linuxdeepin/deepin-system-settings.git",
      platforms = ['Linux'],
      )
