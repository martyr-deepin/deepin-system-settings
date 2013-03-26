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
from nmlib.nmcache import get_cache
import threading
import time
cache = get_cache()

nmclient = cache.getobject("/org/freedesktop/NetworkManager")
nm_remote_settings = cache.getobject("/org/freedesktop/NetworkManager/Settings")

class ThreadWiredAuto(threading.Thread):

    def __init__(self, device_path, connections):
        threading.Thread.__init__(self)
        self.device = cache.get_spec_object(device_path)
        self.conns = connections
        self.run_flag = True

    def run(self):
        for conn in self.conns:
            if self.run_flag:
                try:
                    active_conn = nmclient.activate_connection(conn.object_path, self.device.object_path, "/")
                    while(active_conn.get_state() == 1 and self.run_flag):
                        time.sleep(1)

                    if active_conn.get_state() == 2:
                        self.stop_run()
                        return True
                    else:
                        continue
                except:
                    pass
        self.stop_run()

    def stop_run(self):
        self.run_flag = False

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
    
    def auto_connect(self):
        #if self.get_state() == 100:
            #return True
        #if self.get_state() < 30:
            #return False

        if self.__get_connections():

            wired_prio_connections = sorted(self.__get_connections(),
                                    key = lambda x: int(nm_remote_settings.cf.get("conn_priority", x.settings_dict["connection"]["uuid"])),
                                    reverse = True)

            nm_device = filter(lambda d: d.get_udi() == self.object_path, nmclient.get_modem_devices())[0]
            print nm_device
            object_path = nm_device.object_path

            self.thread_wiredauto = ThreadWiredAuto(object_path, wired_prio_connections)
            self.thread_wiredauto.setDaemon(True)
            self.thread_wiredauto.start()

        else:
            try:
                nmconn = nm_remote_settings.new_wired_connection()
                conn = nm_remote_settings.new_connection_finish(nmconn.settings_dict)
                nmclient.activate_connection(conn.object_path, self.object_path, "/")
            except:
                return False
    
    def connect_error(self, *error):
        pass

    def __get_connections(self):
        if self.get_type() == 2:
            return nm_remote_settings.get_cdma_connections()
        elif self.get_type() == 1:
            return nm_remote_settings.get_gsm_connections()
        else:
            return []

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
