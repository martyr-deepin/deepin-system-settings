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

import platform
import gtop
import gio
import dbus
from socket import gethostname

def get_os_version():
    '''
    get the os's name and version
    @return: a string for the os info
    '''
    dist = platform.linux_distribution()
    return "%s" % (dist[1])

def get_cpu_info():
    '''
    get the cpu info
    @return: a string for cpu info
    '''
    s = gtop.sysinfo()
    model = {}
    for n in s:
        if "model name" in n:
            if not n["model name"] in model:
                model[n["model name"]] = 1
            else:
                model[n["model name"]] += 1
    if model:
        info = ""
        for k in model:
            info += "%s×%d  " % (k, model[k])
        return info
    else:
        return "--"

def get_mem_info():
    '''
    get the memory info
    @return: a float num for the total memory GB value
    '''
    return round(gtop.mem().dict()['total'] / 1000.0 / 1000 / 1024, 1)

def get_os_arch():
    '''
    get the os's architecture
    @return: a string of the architecture
    '''
    arch = platform.architecture()[0]
    i = 0
    for c in arch:
        if not c.isdigit():
            break
        i += 1
    return arch[0:i]

def get_disk_size():
    return get_total_disk_size()

def get_total_disk_size():
    BUS_NAME = "org.freedesktop.UDisks"
    OBJ_NAME = "/org/freedesktop/UDisks"
    try:
        bus = dbus.SystemBus()
        udisks = dbus.Interface(bus.get_object(BUS_NAME, OBJ_NAME), "org.freedesktop.UDisks")

        devices = udisks.EnumerateDevices()
        internal_dev = {}
        for device in devices:
            dev = dbus.Interface(bus.get_object(BUS_NAME, device), "org.freedesktop.DBus.Properties")
            if dev.Get("org.freedesktop.DBus.Properties", 'DeviceIsPartition'):
                slave = dev.Get("org.freedesktop.DBus.Properties", 'PartitionSlave')
                d = dbus.Interface(bus.get_object(BUS_NAME, slave), "org.freedesktop.DBus.Properties") 
                if not d.Get("org.freedesktop.DBus.Properties", 'DeviceIsRemovable'):
                    internal_dev[slave] = d
        total_size = 0
        for d in internal_dev:
            dev = internal_dev[d]
            total_size += dev.Get("org.freedesktop.DBus.Properties", 'DeviceSize')
        return round(total_size / 1000.0 / 1000 / 1000, 1)
    except Exception, e:
        print e
        return None

def get_root_partition_size():
    '''
    get the root partition's size
    @return: a float num
    '''
    f = gio.File('/')
    info = f.query_filesystem_info("*")
    attrs = info.list_attributes()
    if 'filesystem::size' in attrs:
        return round(info.get_attribute_uint64('filesystem::size') / 1024.0 / 1024 / 1024, 3)
    else:
        return 0

def get_hostname():
    '''
    get your own hostname
    @return: a string for hostname
    '''
    return gethostname()
