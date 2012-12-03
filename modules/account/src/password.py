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

import select
import subprocess

class PasswdState:

        PASSWD_STATE_NONE = 0
        PASSWD_STATE_AUTH = 1
        PASSWD_STATE_NEW = 2
        PASSWD_STATE_RETYPE = 3
        PASSWD_STATE_DONE = 4
        PASSWD_STATE_ERR =5

class PasswdHandler(object):

    def __init__(self):

        self.current_password = ""
        self.new_password = ""

        self.backend_pid = None
        self.backend_stdin = None
        self.backend_stdout = None

        self.backend_stdin_queue = None

        self.backend_stdout_watch_id = None
        self.backend_child_watch_id = None

        self.backend_state = 0
        self.changing_password = False

        self.auth_cb = None
        self.auth_cb_data = None
        self.chpasswd_cb = None
        self.chpasswd_cb_data = None


    def child_watch_cb(self):
	pass

    def spawn_password(self):
	pass    

if __name__ == "__main__":
    pass
