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

def bluetooth_verify_address(bdaddr):
    if bdaddr == None:
        return False

    if len(bdaddr) != 17:
        return False

    for i in range(len(bdaddr)):
        if ((i + 1) % 3) == 0:
            if bdaddr[i] != ":":
                return False
            continue
        if bdaddr[i] not in "0123456789abcdefABCDEF":
            return False

    return True    

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
        
def uuid16_custom_to_string (uuid16):
    if uuid16 == 0x2:
	return "SyncMLClient"
    elif uuid16 == 0x5601:
        return "Nokia SyncML Server";
    else:
        return None

def uuid16_to_string(uuid16):

    if uuid16 == 0x1101:
	return "SerialPort"
    elif uuid16 == 0x1103:
	return "DialupNetworking"
    elif uuid16 == 0x1104:
	return "IrMCSync"
    elif uuid16 == 0x1105:
	return "OBEXObjectPush"
    elif uuid16 == 0x1106:
	return "OBEXFileTransfer"
    elif uuid16 == 0x1108:
	return "HSP"
    elif uuid16 == 0x110A:
	return "AudioSource"
    elif uuid16 == 0x110B:
	return "AudioSink"
    elif uuid16 == 0x110c:
	return "A/V_RemoteControlTarget"
    elif uuid16 == 0x110e:
	return "A/V_RemoteControl"
    elif uuid16 == 0x1112:
	return "Headset_-_AG"
    elif uuid16 == 0x1115:
	return "PANU"
    elif uuid16 == 0x1116:
	return "NAP"
    elif uuid16 == 0x1117:
	return "GN"
    elif uuid16 == 0x111e:
	return "Handsfree";
    elif uuid16 == 0x111F:
	return "HandsfreeAudioGateway"
    elif uuid16 == 0x1124:
	return "HumanInterfaceDeviceService"
    elif uuid16 == 0x112d:
	return "SIM_Access"
    elif uuid16 == 0x112F:
	return "Phonebook_Access_-_PSE"
    elif uuid16 == 0x1203:
	return "GenericAudio";
    elif uuid16 in [0x1000, 0x1200]:
        # /* ServiceDiscoveryServerServiceClassID */
        # /* PnPInformation */
	# /* Those are ignored */
        pass
    elif uuid16 == 0x1201:
	return "GenericNetworking";
    elif uuid16 == 0x1303:
	return "VideoSource";
    elif uuid16 in [0x8e771303, 0x8e771301]:
	return "SEMC HLA";
    elif uuid16 == 0x8e771401:
	return "SEMC Watch Phone";
    else:
        return None

def bluetooth_uuid_to_string(uuid):
    try:
        is_custom = uuid.endswith("-0000-1000-8000-0002ee000002")
    except:
        is_custom = False

    parts = uuid.split("-")    

    try:
        uuid16 = int(parts[0], 16)
    except:
        uuid16 = 0

    if uuid16 == 0:
        return None
    
    if is_custom == False:
        return uuid16_to_string(uuid16)
    else:
        return uuid16_custom_to_string(uuid16)

def get_pincode_for_device(bttype, address, name, max_digits):
    pass


if __name__ == "__main__":
    pass
