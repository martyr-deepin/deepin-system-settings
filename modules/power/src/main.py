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
import getopt
from dtk.ui.utils import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))

from power_view import PowerView
from module_frame import ModuleFrame

if __name__ == "__main__":
    ops, args = getopt.getopt(sys.argv[1:], '')
    module_uid = None

    if len(args):
        module_uid = args[0]
        print "DEBUG getopt module_uid", module_uid
    
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    power_view = PowerView()
    
    module_frame.add(power_view)
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            print "DEBUG show_again module_uid", message_content
            module_frame.send_module_info()
        elif message_type == "reset":
            power_view.reset()

    module_frame.module_message_handler = message_handler        
    
    module_frame.run()
