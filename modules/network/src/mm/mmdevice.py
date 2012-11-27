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
from mmclient import MMObject
from nmlib.nm_utils import TypeConvert

class MMDevice(MMObject):
    '''MMDevice'''

    __gsignals__  = {
            "state-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_UINT, gobject.TYPE_UINT, gobject.TYPE_UINT)),
            "device-active":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_UINT,)),
            "device-deactive":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_UINT,))
            }

    def __init__(self, object_path, object_interface = "org.freedesktop.ModemManager.Modem"):
        MMObject.__init__(self, object_path, object_interface)

        self.bus.add_signal_receiver(self.state_changed_cb, dbus_interface = self.object_interface, 
                                     path = self.object_path, signal_name = "StateChanged")

        self.prop_list = ["Enabled", "Device", "DeviceIdentifier", "Driver", "EquipmentIdentifier", "MasterDevice",
                          "UnlockRequired", "IpMethod", "State", "Type", "UnlockRetries"]
        self.init_mmobject_with_properties()

    def get_enabled(self):
        return self.properties["Enabled"]

    def get_device(self):
        return self.properties["Device"]

    def get_device_identifier(self):
        return self.properties["DeviceIdentifier"]

    def get_driver(self):
        return self.properties["Driver"]

    def get_equipment_identifier(self):
        return self.properties["EquipmentIdentifier"]

    def get_master_device(self):
        return self.properties["MasterDevice"]
    
    def get_unlock_required(self):
        return self.properties["UnlockRequired"]

    def get_ip_method(self):
        return self.properties["IpMethod"]
    
    def get_state(self):
        return self.properties["State"]

    def get_type(self):
        return self.properties["Type"]

    def get_unlock_retries(self):
        return self.properties["UnlockRetries"]

    def connect(self, number):
        self.dbus_method("Connect", number, reply_handler = self.connect_finish, error_handler = self.connect_error)

    def connect_finish(self, *reply):
        pass
    
    def connect_error(self, *error):
        pass

    def disconnect(self):
        self.dbus_method("Disconnect", reply_handler = self.disconnect_finish, error_handler = self.disconnect_error)

    def disconnect_finish(self, *reply):
        pass

    def disconnect_error(self, *error):
        pass

    def enable(self, enable):
        self.dbus_method("Enabled", enable, reply_handler = self.enable_finish, error_handler = self.enable_error)

    def enable_finish(self, *reply):
        pass

    def enable_error(self, *error):
        pass

    def factory_reset(self, code):
        self.dbus_method("FactoryReset", code, reply_handler = self.factory_reset_finish, error_handler = self.factory_reset_error)

    def factory_reset_finish(self, *reply):
        pass

    def factory_reset_error(self, *error):
        pass

    def get_ip4config(self):
        if self.get_ip_method() == 1:
            return TypeConvert.dbus2py(self.dbus_method("GetIP4Config"))

    def get_info(self):
        return TypeConvert.dbus2py(self.dbus_method("GetInfo"))

    def get_manufacturer(self):
        return self.get_info()[0].split(":")[-1].strip()

    def get_model(self):
        return self.get_info()[1]

    def get_version(self):
        return self.get_info()[2]

    def reset(self):
        self.dbus_method("Reset", reply_handler = self.reset_finish, error_handler = self.reset_error)

    def reset_finish(self, *reply):
        pass

    def reset_error(self, *error):
        pass

    def state_changed_cb(self, old_state, new_state, reason):
        print "state_changed_cb"
        print old_state
        print new_state
        print reason
        self.emit("state-changed", old_state, new_state, reason)


class MMSimple(MMObject):
    '''MMSimple'''

    def __init__(self, object_path, object_interface = "org.freedesktop.ModemManager.Modem.Simple"):
        MMObject.__init__(self, object_path, object_interface)

    def connect(self, prop_dict):
        self.dbus_method("Connect", prop_dict, reply_handler = self.connect_finish, error_handler = self.connect_error)

    def connect_finish(self, *reply):
        pass

    def connect_error(self, *error):
        pass

    def get_status(self):
        return TypeConvert.dbus2py(self.dbus_method("GetStatus"))

class MMLocation(MMObject):
    '''MMLocation'''

    def __init__(self, object_path, object_interface = "org.freedesktop.ModemManager.Modem.Location"):
        MMObject.__init__(self, object_path, object_interface)

        self.prop_list = ["Capabilities", "Enabled", "SignalsLocation", "Location"]
        self.init_mmobject_with_properties()

    def get_capabilities(self):
        return self.properties["Capabilities"]

    def get_enabled(self):
        return self.properties["Enabled"]

    def get_signals_location(self):
        return self.properties["SignalsLocation"]

    def get_location(self):
        return self.properties["Location"]

    def enable(self, enable, signal_location):
        self.dbus_method("Enable", signal_location, reply_handler = self.enable_finish, error_handler = self.enable_error)

    def enable_finish(self, *reply):
        pass

    def enable_error(self, *error):
        pass

    def getlocation(self):
        return TypeConvert.dbus2py(self.dbus_method("GetLocation"))

if __name__ == "__main__":
    device = MMDevice("/org/freedesktop/ModemManager/Modems/1")
    print device.get_info()
    print device.get_manufacturer()
    print device.get_model()
