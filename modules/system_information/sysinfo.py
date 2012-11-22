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

from gi.repository import GLib
import gtop
import subprocess

class SysInfo(object):

    def __init__(self):
        self.cpu_info = self.get_cpu_info()
        self.mem_info = self.get_memory_info()
        self.sys_info = self.get_sys_info()

    def get_os_type(self):
        if GLib.SIZEOF_VOID_P == 8:
            return 64
        else:
            return 32

    def get_cpu_info(self):
        return gtop.cpu().dict()

    def get_memory_info(self):
        return gtop.mem().dict()

    def get_memory_total(self):
        if "total" in self.mem_info.iterkeys():
            return self.mem_info["total"]
        else:
            pass

    def get_sys_info(self):
        return gtop.sysinfo()

    def get_sys_info_ncpu(self):
        return len(self.sys_info)

    def get_sys_info_model_name(self):
        if "model name" in self.sys_info[0]:
            return self.sys_info[0]["model name"]
        else:
            pass

    def get_hostname(self):
        pass

    def set_hostname(self, hostname):
        pass

    def get_graphics_info(self):
        try:
            process = subprocess.Popen(("glxinfo", "-l"), stdout = subprocess.PIPE)
            process.wait()
            glxinfo = process.stdout.readlines()

            for item in glxinfo:
                if item.startswith("OpenGL renderer string"):
                    graphics_str = item.split(":")[-1]
                else:
                    continue
            else:
                # need read from /var/log/Xorg.0.log
                # the '0' is read from env
                pass

        except:            
            pass

        return graphics_str


    def get_mount_disk_size(self):
        pass

if __name__ == "__main__":
    sysinfo = SysInfo()

    # print sysinfo.get_os_type()
    # print sysinfo.get_memory_total()
    # print sysinfo.get_sys_info_ncpu()
    # print sysinfo.get_sys_info_model_name()
    print sysinfo.get_graphics_info()
