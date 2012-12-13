#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
#             Long Changjin <admin@longchangjin.cn>
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
import os
import socket
import dbus
import traceback

system_bus = dbus.SystemBus()
hostname_object = system_bus.get_object("org.freedesktop.hostname1", "/org/freedesktop/hostname1")
hostname_interface = dbus.Interface(hostname_object, "org.freedesktop.hostname1")

class SysInfo(object):

    def __init__(self):
        self.cpu_info = self._get_cpu_info()
        self.mem_info = self._get_memory_info()
        self.sys_info = self._get_sys_info()
        self.mountlist = self._get_mountlist_info()

    def get_os_type(self):
        return platform.architecture()[0]

    def _get_cpu_info(self):
        return gtop.cpu().dict()

    def _get_memory_info(self):
        return gtop.mem().dict()

    def get_memory_total(self):
        if "total" in self.mem_info.iterkeys():
            return self.mem_info["total"]
        else:
            return filter(lambda x: x.isdigit(), os.popen("grep MemTotal /proc/meminfo").read())

    def _get_sys_info(self):
        return gtop.sysinfo()

    def get_sys_info_ncpu(self):
        if len(self.sys_info):
            return len(self.sys_info)
        else:
            return os.popen('cat /proc/cpuinfo |grep "processor" | wc -l').read().strip()

    def get_cpu_model_name(self):
        if "model name" in self.sys_info[0]:
            return self.sys_info[0]["model name"]
        else:
            return os.popen("grep 'model name' /proc/cpuinfo | head -1").read().split(":")[-1].strip()

    def get_hostname(self):
        return socket.gethostname()

    def set_hostname(self, hostname):
        try:
            hostname_interface.SetStaticHostname(hostname, True)
        except:
            traceback.print_exc()

    def _get_current_display(self):
        pass

    def get_graphics_info(self):
        try:
            graphics_str = os.popen("glxinfo -l |grep 'OpenGL renderer string' ").read().split(":")[-1].strip()
        except:            
            pass

        return graphics_str

    def _get_mountlist_info(self):
        return gtop.mountlist()

    def get_mount_disk_size(self):
        pass

    def get_disk_size(self):
        st = os.statvfs(".")
        return st.f_blocks * st.f_bsize / (1024 * 1024 * 1024)

if __name__ == "__main__":
    sysinfo = SysInfo()

    # print sysinfo.get_os_type()
    # print sysinfo.get_memory_total()
    # print sysinfo.get_sys_info_ncpu()
    # print sysinfo.get_cpu_model_name()
    print sysinfo.get_graphics_info()
    # print sysinfo.get_hostname()
    print sysinfo.get_disk_size()
