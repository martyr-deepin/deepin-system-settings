#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang YaoHua
#
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
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

import os
import sys
import gobject
import dbus.mainloop.glib
from deepin_utils.file import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))

from bt.agent import Agent
from bt.adapter import Adapter
from bt.manager import Manager
from bluetooth_transfer import BluetoothTransfer

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

bus = dbus.SystemBus()
path = "/com/deepin/bluetooth/agent"

agent = Agent(path, bus)

default_adapter = Manager().get_default_adapter()
if default_adapter != "None":
    adptr = Adapter(default_adapter)
    adptr.register_agent(path, "")
    
    BluetoothTransfer()
    
mainloop = gobject.MainLoop()
mainloop.run()
