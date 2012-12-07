#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Deepin, Inc.
#               2012 Zhai Xiang
# 
# Author:     Zhai Xiang <zhaixiang@linuxdeepin.com>
# Maintainer: Zhai Xiang <zhaixiang@linuxdeepin.com>
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

from a11y_view import A11yView
from module_frame import ModuleFrame

if __name__ == "__main__":
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    a11y_view = A11yView()
    
    module_frame.add(a11y_view)
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            module_frame.send_module_info()

    module_frame.module_message_handler = message_handler        
    
    module_frame.run()
