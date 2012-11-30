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

import accounts
import os
import utils

ACCOUNT = accounts.Accounts()
PERMISSION = utils.PolkitPermission("org.freedesktop.accounts.user-administration")

def check_is_myown(uid):
    '''
    check the user id is the current process's user id
    @param uid: user id, a int type
    @return: true if the user if current process's user, otherwise false
    '''
    return uid == os.getuid()

def get_user_list(account=ACCOUNT):
    '''
    @param account: a accounts.Accounts object
    @return: a list container some accounts.User objects
    '''
    user_list = account.list_cached_users()
    return map(accounts.User, user_list)

def get_user_info(user_path):
    '''
    @param user_path: a object path of dbus, a string type
    @return: a tuple container some info of the user
    '''
    u = accounts.User(user_path)
    return (u, u.get_icon_file(), u.get_real_name(),
            u.get_user_name(), u.get_account_type(),
            check_is_myown(u.get_uid()))
