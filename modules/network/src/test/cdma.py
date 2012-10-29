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

import sys
sys.path.append("../")

from pynm.mm.pynm.mm.lient import MMClient
from pynm.mm.pynm.mm.evice import MMDevice
from pynm.mm.pynm.mm.dma import MMCdma
from pynm.mm.pynm.mm.evice import MMSimple
from pynm.mm.pynm.mm.evice import MMLocation

pynm.mm.lient = MMClient()

pynm.mm.evice = MMDevice(pynm.mm.lient.get_cdma_device())
cdma = MMCdma(pynm.mm.evice.object_path)
simple = MMSimple(pynm.mm.evice.object_path)
location = MMLocation(pynm.mm.evice.object_path)

def get_device():
    return pynm.mm.lient.enumerate_devices()[0]

def cdma_device():
    
    print "enabled:", pynm.mm.evice.get_enabled()
    print "device:", pynm.mm.evice.get_device()
    print "device identifier:", pynm.mm.evice.get_device_identifier()
    print "driver:", pynm.mm.evice.get_driver()
    print "equipment_identifier:", pynm.mm.evice.get_equipment_identifier()
    print "master_device:", pynm.mm.evice.get_master_device()
    print "unlock_required:", pynm.mm.evice.get_unlock_required()
    print "ip_method:", pynm.mm.evice.get_ip_method()
    print "state:", pynm.mm.evice.get_state()
    print "type:", pynm.mm.evice.get_type()
    print "unlock_retries:", pynm.mm.evice.get_unlock_retries()

def get_info():
    print pynm.mm.evice.get_info()

def get_ip4config():
    print pynm.mm.evice.get_ip4config()

def print_cdma():
    print "meid:", cdma.get_meid()

    print "esn:", cdma.get_esn()
    print "registration state:", cdma.get_registration_state()
    print "serving system:", cdma.get_serving_system()
    print "signal quality:", cdma.get_signal_quality()

def print_location():
    print "capabilities:", location.get_capabilities()
    print "enables:", location.get_enabled()
    print "signals location:", location.get_signals_location()
    print "getlocation:", location.getlocation()


if __name__ == "__main__":

    # print get_device()
    # cdma_device()
    # get_info()
    # get_ip4config()
    # pynm.mm.evice.enable(False)
    # pynm.mm.evice.enable(True)
    # pynm.mm.evice.disconnect()
    print_cdma()
    # print simple.get_status()
    # print_location()

    pass
