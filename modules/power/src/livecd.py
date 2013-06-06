#!/usr/bin/env python

import os
import dbus


def is_deepin_livecd():
    try:
        bus = dbus.SystemBus()
        dde = bus.get_object('com.deepin.dde.lock', '/com/deepin/dde/lock')
        is_livecd = dde.get_dbus_method("IsLiveCD", 'com.deepin.dde.lock')
        return is_livecd(os.getlogin())
    except:
        return False

if __name__ == '__main__':
    print is_deepin_livecd()
