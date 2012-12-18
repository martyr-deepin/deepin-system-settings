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


def bluetooth_class_to_type(klass):
    p = (klass & 0x1f00) >> 8

    if p == 0x01:
        return "computer"

    elif p == 0x02:
        q = (klass & 0xfc) >> 2
        if q in [0x01, 0x02, 0x03, 0x05]:
            return "phone"
        elif q == 0x04:
            return "modem"
        else:
            pass

    elif p == 0x03:
        return "network"

    elif p == 0x04:
        q = (klass & 0xfc) >> 2
        if q in [0x01, 0x02]:
            return "headset"
        elif q == 0x06:
            return "headphones"
        elif q in [0x0b, 0x0c, 0x0d]:
            return "video"
        else:
            return "other-audio"

    elif p == 0x05:
        q = (klass & 0xc0) >> 6
        if q == 0x00:
            r = (klass & 0x1e) >> 2
            if r in [0x01, 0x02]:
                return "joypad"
            else:
                pass
        elif q == 0x01:
            return "keyboard"
        elif q == 0x02:
            r = (klass & 0x1e) >> 2
            if r == 0x05:
                return "tablet"
            else:
                return "mouse"
        else:
            pass

    elif p == 0x06:
        if (klass & 0x80):
            return "printer"
        if (klass * 0x20):
            return "camera"
        else:
            pass

    return "any"    
        
if __name__ == "__main__":
    pass
