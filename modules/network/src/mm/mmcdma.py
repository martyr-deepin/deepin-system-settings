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

class MMCdma(MMDevice):
    '''MMCdma'''
    __gsignals__  = {
            "activation-state-changed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT, gobject.TYPE_UINT, gobject.TYPE_PYOBJECT)),
            "signal-quality":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT,)),
            "registration-state-changed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT,gobject.TYPE_UINT))
            }

    def __init__(self, object_path):
        MMDevice.__init__(self, object_path, object_interface = "org.freedesktop.ModemManager.Modem.Cdma")

        self.init_mmobject_with_properties()
        self.bus.add_signal_receiver(self.activation_state_changed_cb, dbus_interface = self.object_interface,
                                     signal_name = "ActivationStateChanged")

        self.bus.add_signal_receiver(self.signal_quality_cb, dbus_interface = self.object_interface,
                                     signal_name = "SignalQuality")

        self.bus.add_signal_receiver(self.registration_state_changed_cb, dbus_interface = self.object_interface,
                                     signal_name = "RegistrationStateChanged")

    def get_meid(self):
        return self.properties["Meid"]

    def activate(self, carrier):
        return TypeConvert.dbus2py(self.dbus_interface.Activate(carrier))
        return TypeConvert.dbus2py(self.dbus_method("Activate", carrier))

    def activate_manual(self, prop_dict):
        self.dbus_interface.ActivateManual(prop_dict)
        self.dbus_method("ActivateManual", prop_dict, reply_handler = self.activate_manual_finish,
                         error_handler = self.activate_manual_error)

    def activate_manual_finish(self, *reply):
        pass

    def activate_manual_error(self, *error):
        pass

    def get_esn(self):
        return TypeConvert.dbus2py(self.dbus_method("GetEsn"))

    def get_registration_state(self):
        return TypeConvert.dbus2py(self.dbus_method("GetRegistrationState"))

    def get_serving_system(self):
        return TypeConvert.dbus2py(self.dbus_method("GetServingSystem"))

    def get_signal_quality(self):
        return TypeConvert.dbus2py(self.dbus_method("GetSignalQuality"))

    def activation_state_changed_cb(self, activation_state, activation_error, state_changes_dict):
        print activation_state
        print activation_error
        print state_changes_dict
        self.emit("ActivationStateChanged", activation_state, activation_error, state_changes_dict)

    def signal_quality_cb(self, quality):
        print quality
        self.emit("SignalQuality", quality)
        
    def registration_state_changed_cb(self, cdma_1x_state, evdo_state):
        self.emit("RegistrationStateChanged", cdma_1x_state, evdo_state)

if __name__ == "__main__":
    pass
