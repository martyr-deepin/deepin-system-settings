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

import gobject
from mmdevice import MMDevice
from nmlib.nm_utils import TypeConvert

class MMGsm(MMDevice):
    '''MMGsm'''

    def __init__(self, object_path, object_interface = "org.freedesktop.ModemManager.Modem.Gsm"):
        MMDevice.__init__(self, object_path, object_interface)

class MMGsmCard(MMGsm):
    '''MMGsmCard'''

    def __init__(self, object_path):
        MMGsm.__init__(self, object_path, object_interface = "org.freedesktop.ModemManager.Modem.Gsm.Card")

        self.init_mmobject_with_properties()

    def get_simidentifier(self):
        return self.properties["SimIdentifier"]

    def get_supportedbands(self):
        return self.properties["SupportedBands"]

    def get_supportedModes(self):
        return self.properties["supportedModes"]

    def get_imei(self):
        return TypeConvert.dbus2py(self.dbus_interface.GetImei())

    def get_imsi(self):
        return TypeConvert.dbus2py(self.dbus_interface.GetImsi())

    def get_operator_id(self):
        return TypeConvert.dbus2py(self.dbus_interface.GetOperatorId())

    def get_spn(self):
        return TypeConvert.dbus2py(self.dbus_interface.GetSpn())

    def send_puk(self, puk, pin):
        self.dbus_interface.SendPuk(self, puk, pin)

    def send_pin(self, pin):
        self.dbus_interface.SendPin(self, pin)

    def enable_pin(self, enable, pin):
        self.dbus_interface.EnablePin(self, enable, pin)

    def change_pin(self, old_pin, new_pin):
        self.dbus_interface.ChangePin(self, old_pin, new_pin)


class MMGsmContacts(MMGsm):
    '''MMGsmContacts'''

    def __init__(self, object_path):
        MMGsm.__init__(self, object_path, object_interface = "org.freedesktop.ModemManager.Modem.Gsm.Contacts")

    def add(self, name, number):
        return TypeConvert.dbus2py(self.dbus_interface.Add(name, number))
        
    def delete(self, index):
        self.dbus_interface.Delete(index)

    def get(self, index):
        return TypeConvert.dbus2py(self.dbus_interface.Get(index))

    def list(self):
        return TypeConvert.dbus2py(self.dbus_interface.List())

    def find(self, pattern):
        return TypeConvert.dbus2py(self.dbus_interface.Find(pattern))

    def get_count(self):
        return TypeConvert.dbus2py(self.dbus_interface.GetCount())

class MMGsmNetwork(MMGsm):
    '''MMGsmNetwork'''

    __gsignals__  = {
            "signal-quality":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT, )),
            "registration-info":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT, str, str)),
            "network-mode":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT, ))
            }

    def __init__(self, object_path):
        MMGsm.__init__(self, object_path, object_interface = "org.freedesktop.ModemManager.Modem.Gsm.Network")
        self.bus.add_signal_receiver(self.signal_quality_cb, dbus_interface = self.object_interface, 
                                     signal_name = "SignalQuality")
        self.bus.add_signal_receiver(self.registration_info_cb, dbus_interface = self.object_interface, 
                                     signal_name = "RegistrationInfo")
        self.bus.add_signal_receiver(self.network_mode_cb, dbus_interface = self.object_interface, 
                                     signal_name = "NetworkMode")

        self.init_mmobject_with_properties()

    def get_allowedmode(self):
        return self.properties["AllowedMode"]
        
    def get_accesstechnology(self):
        return self.properties["AccessTechnology"]

    def register(self, network_id):
        self.dbus_interface.Register(network_id)

    def scan(self):
        return TypeConvert.dbus2py(self.dbus_interface.Scan())

    def set_apn(self, apn):
        self.dbus_interface.SetApn(apn)

    def get_signal_quality(self):
        return TypeConvert.dbus2py(self.dbus_interface.GetSignalQuality())

    def set_band(self, band):
        self.dbus_interface.SetBand(band)

    def get_band(self):
        return TypeConvert.dbus2py(self.dbus_interface.GetBand())

    def set_network_mode(self, mode):
        self.dbus_interface.SetNetworkMode(mode)

    def get_network_mode(self):
        return TypeConvert.dbus2py(self.dbus_interface.GetNetworkMode())

    def get_registration_info(self):
        return TypeConvert.dbus2py(self.dbus_interface.GetRegistrationInfo())

    def set_allowed_mode(self, mode):
        self.dbus_interface.SetAllowedMode(mode)

    def signal_quality_cb(self, quality):
        print quality
        self.emit("signal_quality", quality)

    def registration_info_cb(self, status, operator_code, operator_name):
        print status
        print operator_code
        print operator_name
        self.emit("registration_info", status, operator_code, operator_name)
        
    def network_mode_cb(self, mode):
        print mode
        self.emit("network_mode", mode)


class MMGsmSms(MMGsm):
    '''MMGsmSms'''

    __gsignals__  = {
            "sms-received":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT, gobject.TYPE_BOOLEAN)),
            "completed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT, gobject.TYPE_BOOLEAN))
            }

    def __init__(self, object_path):
        MMGsm.__init__(self, object_path, object_interface = "org.freedesktop.ModemManager.Modem.Gsm.Sms")
        self.bus.add_signal_receiver(self.sms_received_cb, dbus_interface = self.object_interface, signal_name = "SmsReceived")
        self.bus.add_signal_receiver(self.completed_cb, dbus_interface = self.object_interface, signal_name = "Completed")

    def delete(self, index):
        self.dbus_interface.Delete(index)

    def get(self, index):
        return TypeConvert.dbus2py(self.dbus_interface.Get(index))

    def get_format(self):
        return TypeConvert.dbus2py(self.dbus_interface.GetFormat())

    def set_format(self, format):
        self.dbus_interface.SetFormat(format)

    def get_smsc(self):
        return TypeConvert.dbus2py(self.dbus_interface.GetSmsc())

    def list(self):
        return TypeConvert.dbus2py(self.dbus_interface.List())

    def save(self, prop_dict):
        return TypeConvert.dbus2py(self.dbus_interface.Save(prop_dict))

    def send(self, prop_dict):
        return TypeConvert.dbus2py(self.dbus_interface.Send(prop_dict))

    def send_from_storage(self, index):
        self.dbus_interface.SendFromStorage(index)

    def set_indication(self, mode, mt, bm, ds, bfr):
        self.dbus_interface.SetIndication(mode, mt, bm, ds, bfr)

    def sms_received_cb(self, index, completed):
        print index
        print completed
        self.emit("sms_received", index, completed)

    def completed_cb(self, index, completed):
        self.emit("completed", index, completed)

class MMGsmHso(MMGsm):
    '''MMGsmHso'''

    def __init__(self, object_path):
        MMGsm.__init__(self, object_path, object_interface = "org.freedesktop.ModemManager.Modem.Gsm.Hso")

    def authenticate(self, username, password):
        self.dbus_interface.Authenticate(username, password)

class MMGsmUssd(MMGsm):
    '''MMGsmUssd'''

    def __init__(self, object_path):
        MMGsm.__init__(self, object_path, object_interface = "org.freedesktop.ModemManager.Modem.Gsm.Ussd")

        self.init_mmobject_with_properties()

    def get_state(self):
        return self.properties["State"]

    def get_network_notification(self):
        return self.properties["NetworkNotification"]

    def get_network_request(self):
        return self.properties["NetworkRequest"]

    def initiate(self, command):
        return TypeConvert.dbus2py(self.dbus_interface.Initiate(command))

    def respond(self, response):
        return TypeConvert.dbus2py(self.dbus_interface.Respond(response))

    def cancel(self):
        self.dbus_interface.Cancel()


if __name__ == "__main__":
    pass
