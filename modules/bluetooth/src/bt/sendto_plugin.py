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

import deepin_gsettings

nst_settings = deepin_gsettings.new("org.gnome.Bluetooth.nst")
contacts_settings = deepin_gsettings.new("org.gnome.Contacts")
sendto_settings = deepin_gsettings.new("org.gnome.Nautilus.Sendto")

def get_last_used_device():
    '''The last Bluetooth device we sent files to'''
    return nst_settings.get_string("last-used")

def set_last_used_device(address):
    nst_settings.set_string("last-used", address)

def get_contacts_first_setup():
    if contacts_settings.get_boolean("did-initial-setup") == None:
        return False
    return contacts_settings.get_boolean("did-initial-setup")

def get_sendto_last_compress():
    return sendto_settings.get_int("last-compress")

def get_sendto_last_meidum():
    return sendto_settings.get_string("last-medium")

if __name__ == "__main__":
    pass
