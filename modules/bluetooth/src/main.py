#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Zhai Xiang
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
from deepin_utils.file import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))

from bluetooth_view import BlueToothView
from module_frame import ModuleFrame

if __name__ == "__main__":
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    bluetooth_view = BlueToothView(module_frame)

    module_frame.add(bluetooth_view)

    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            module_frame.send_module_info()
        elif message_type == "cancel":
            bluetooth_view.cancel()
        elif message_type == "exit":
            module_frame.exit()
        else:
            pass

    module_frame.module_message_handler = message_handler

    module_frame.run()
