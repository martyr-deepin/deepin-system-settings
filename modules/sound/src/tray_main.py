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

import sys
import os
from dtk.ui.utils import get_parent_dir 
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from theme import app_theme

from dtk.ui.line import HSeparator
from dtk.ui.button import OffButton
from dtk.ui.trayicon import TrayIcon
from dtk.ui.label import Label
from dtk.ui.box import ImageBox
from dtk.ui.mask import draw_mask
from dtk.ui.scrolled_window  import ScrolledWindow
import gtk
import subprocess

class SoundTray(TrayIcon):
    ''' '''
    def __init__(self, witdh=230):
        super(SoundTray, self).__init__()
        self.set_size_request(width, -1)        
        
