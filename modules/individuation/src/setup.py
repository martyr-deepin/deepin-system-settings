#! /usr/bin/env python

from setuptools import setup, Extension
import os
import commands

deepin_io_mod = Extension('deepin_io', sources = ['deepin_io.c'])

setup(name='deepin_io',
      version='0.1',
      ext_modules = [deepin_io_mod],
      description='Deepin IO Python Binding.',
      long_description ="""Deepin IO Python Binding.""",
      author='Linux Deepin Team',
      author_email='zhaixiang@linuxdeepin.com',
      license='GPL-3',
      url="https://github.com/linuxdeepin/deepin-system-settings/tree/master/modules/individuation/src",
      download_url="git@github.com:linuxdeepin/deepin-system-settings.git",
      platforms = ['Linux'],
      )
