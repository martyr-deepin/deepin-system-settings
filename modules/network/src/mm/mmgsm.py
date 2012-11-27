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

        self.prop_list = ["SimIdentifier", "SupportedBands", "SupportedModes"]
        self.init_mmobject_with_properties()

    def get_simidentifier(self):
        return self.properties["SimIdentifier"]

    def get_supportedbands(self):
        return self.properties["SupportedBands"]

    def get_supportedModes(self):
        return self.properties["SupportedModes"]

    def get_imei(self):
        return TypeConvert.dbus2py(self.dbus_method("GetImei"))

    def get_imsi(self):
        return TypeConvert.dbus2py(self.dbus_method("GetImsi"))

    def get_operator_id(self):
        return TypeConvert.dbus2py(self.dbus_method("GetOperatorId)"))

    def get_spn(self):
        return TypeConvert.dbus2py(self.dbus_method("GetSpn"))

    def send_puk(self, puk, pin):
        self.dbus_method("SendPuk", puk, pin, reply_handler = self.send_puk_finish, error_handler = self.send_puk_error)

    def send_puk_finish(self, *reply):    
        pass

    def send_puk_error(self, *error):
        pass

    def send_pin(self, pin):
        self.dbus_method("SendPin", pin, reply_handler = self.send_pin_finish, error_handler = self.send_pin_error)

    def send_pin_finish(self, *reply):
        pass

    def send_pin_error(self, *error):
        pass

    def enable_pin(self, enable, pin):
        self.dbus_method("EnablePin", enable, pin, reply_handler = self.enable_pin_finish, error_handler = self.enable_pin_error)

    def enable_pin_finish(self, *reply):
        pass
        
    def enable_pin_error(self, *error):
        pass

    def change_pin(self, old_pin, new_pin):
        self.dbus_method("ChangePin", old_pin, new_pin, reply_handler = self.change_pin_finish, 
                         error_handler = self.change_pin_error)

    def change_pin_finish(self, *reply):
        pass

    def change_pin_error(self, *error):
        pass

class MMGsmContacts(MMGsm):
    '''MMGsmContacts'''

    def __init__(self, object_path):
        MMGsm.__init__(self, object_path, object_interface = "org.freedesktop.ModemManager.Modem.Gsm.Contacts")

    def add(self, name, number):
        return TypeConvert.dbus2py(self.dbus_method("Add", name, number))
        
    def delete(self, index):
        self.dbus_method("Delete", index, reply_handler = self.delete_finish, error_handler = self.delete_error)

    def delete_finish(self, *reply):
        pass

    def delete_error(self, *error):
        pass

    def get(self, index):
        return TypeConvert.dbus2py(self.dbus_method("Get", index))

    def list(self):
        return TypeConvert.dbus2py(self.dbus_method("List"))

    def find(self, pattern):
        return TypeConvert.dbus2py(self.dbus_method("Find", pattern))

    def get_count(self):
        return TypeConvert.dbus2py(self.dbus_method("GetCount"))

class MMGsmNetwork(MMGsm):
    '''MMGsmNetwork'''

    __gsignals__  = {
            "signal-quality":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_UINT, )),
            "registration-info":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_UINT, str, str)),
            "network-mode":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_UINT, ))
            }

    def __init__(self, object_path):
        MMGsm.__init__(self, object_path, object_interface = "org.freedesktop.ModemManager.Modem.Gsm.Network")

        self.bus.add_signal_receiver(self.signal_quality_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "SignalQuality")

        self.bus.add_signal_receiver(self.registration_info_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "RegistrationInfo")

        self.bus.add_signal_receiver(self.network_mode_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "NetworkMode")

        self.prop_list = ["AllowedMode", "AccessTechnology"]

        self.init_mmobject_with_properties()

    def get_allowedmode(self):
        return self.properties["AllowedMode"]
        
    def get_accesstechnology(self):
        return self.properties["AccessTechnology"]

    def register(self, network_id):
        self.dbus_method("Register", network_id, reply_handler = self.register_finish, error_handler = self.register_error)

    def register_finish(self, *reply):
        pass

    def register_error(self, *error):
        pass

    def scan(self):
        return TypeConvert.dbus2py(self.dbus_method("Scan"))

    def set_apn(self, apn):
        self.dbus_method("SetApn", apn, reply_handler = self.set_apn_finish, error_handler = self.set_apn_error)

    def set_apn_finish(self, *reply):
        pass

    def set_apn_error(self, *error):
        pass

    def get_signal_quality(self):
        return TypeConvert.dbus2py(self.dbus_method("GetSignalQuality"))

    def set_band(self, band):
        self.dbus_method("SetBand", band, reply_handler = self.set_band_finish, error_handler = self.set_band_error)

    def set_band_finish(self, *reply):
        pass

    def set_band_error(self, *error):
        pass

    def get_band(self):
        return TypeConvert.dbus2py(self.dbus_method("GetBand"))

    def set_network_mode(self, mode):
        self.dbus_method("SetNetworkMode", mode, reply_handler = self.set_network_mode_finish,
                         error_handler = self.set_network_mode_error)

    def set_network_mode_finish(self, *reply):
        pass

    def set_network_mode_error(self, *error):
        pass

    def get_network_mode(self):
        return TypeConvert.dbus2py(self.dbus_method("GetNetworkMode"))

    def get_registration_info(self):
        return TypeConvert.dbus2py(self.dbus_method("GetRegistrationInfo"))

    def set_allowed_mode(self, mode):
        self.dbus_method("SetAllowedMode", mode, reply_handler = self.set_allowed_mode_finish,
                         error_handler = self.set_allowed_mode_error)

    def set_allowed_mode_finish(self, *reply):
        pass

    def set_allowed_mode_error(self, *error):
        pass

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
            "sms-received":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_UINT, gobject.TYPE_BOOLEAN)),
            "completed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_UINT, gobject.TYPE_BOOLEAN))
            }

    def __init__(self, object_path):
        MMGsm.__init__(self, object_path, object_interface = "org.freedesktop.ModemManager.Modem.Gsm.Sms")

        self.bus.add_signal_receiver(self.sms_received_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "SmsReceived")

        self.bus.add_signal_receiver(self.completed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "Completed")

    def delete(self, index):
        self.dbus_method("Delete", index, reply_handler = self.delete_finish, error_handler = self.delete_error)

    def delete_finish(self, *reply):
        pass

    def delete_error(self, *error):
        pass

    def get(self, index):
        return TypeConvert.dbus2py(self.dbus_method("Get", index))

    def get_format(self):
        return TypeConvert.dbus2py(self.dbus_method("GetFormat"))

    def set_format(self, new_format):
        self.dbus_method("SetFormat", new_format, reply_handler = self.set_format_finish, error_handler = self.set_format_error )

    def set_format_finish(self, *reply):
        pass

    def set_format_error(self, *error):
        pass

    def get_smsc(self):
        return TypeConvert.dbus2py(self.dbus_method("GetSmsc"))

    def list(self):
        return TypeConvert.dbus2py(self.dbus_method("List"))

    def save(self, prop_dict):
        return TypeConvert.dbus2py(self.dbus_method("Save", prop_dict))

    def send(self, prop_dict):
        return TypeConvert.dbus2py(self.dbus_method("Send", prop_dict))

    def send_from_storage(self, index):
        self.dbus_method("SendFromStorage", index, reply_handler = self.send_from_storage_finish,
                         error_handler = self.send_from_storage_error)

    def send_from_storage_finish(self, *reply):
        pass

    def send_from_storage_error(self, *error):
        pass

    def set_indication(self, mode, mt, bm, ds, bfr):
        self.dbus_method("SetIndication", mode, mt, bm, ds, bfr, reply_handler = self.set_indication_finish, error_handler = self.set_indication_error)

    def set_indication_finish(self, *reply):
        pass

    def set_indication_error(self, *error):
        pass

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

        self.prop_list = ["State", "NetworkNotification", "NetworkRequest"]
        self.init_mmobject_with_properties()

    def get_state(self):
        return self.properties["State"]

    def get_network_notification(self):
        return self.properties["NetworkNotification"]

    def get_network_request(self):
        return self.properties["NetworkRequest"]

    def initiate(self, command):
        return TypeConvert.dbus2py(self.dbus_method("Initiate", command))

    def respond(self, response):
        return TypeConvert.dbus2py(self.dbus_method("Respond", response))

    def cancel(self):
        self.dbus_method("Cancel", reply_handler = self.cancel_finish, error_handler = self.cancel_error)

    def cancel_finish(self, *reply):
        pass

    def cancel_error(self, *error):
        pass

if __name__ == "__main__":
    pass
