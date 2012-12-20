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

def test_adapter_prop():
    from manager import Manager
    from adapter import Adapter
    manager = Manager()
    adapter = Adapter(manager.get_default_adapter())

    from device import Device
    device_address = Device(adapter.get_devices()[0]).get_address()
    print "find device:\n    %s" % adapter.find_device(device_address)
    print "remove device:\n    %s" % adapter.remove_device(adapter.find_device(device_address))
    # print "create device:\n    %s" % adapter.create_device(device_address)

    print "get devices:\n    %s" % adapter.get_devices()

    adapter.set_name("Long Wei's PC")
    print "get name:\n    %s" % adapter.get_name()

    adapter.set_powered(True)
    print "get powered:\n    %s" % adapter.get_powered()

    adapter.set_discoverable(True)
    print "get discoverable:\n    %s" % adapter.get_discoverable()

    print "get discovering:\n    %s" % adapter.get_discovering()

    adapter.set_discoverable_timeout(120)
    print "get discoverable_timeout:\n    %s" % adapter.get_discoverable_timeout()

    adapter.set_pairable(True)
    print "get pairable:\n    %s" % adapter.get_pairable()

    adapter.set_pairable_timeout(180)
    print "get pairable timeout:\n    %s" % adapter.get_pairable_timeout()

    print "get class:\n    %s" % adapter.get_class()
    print "get address:\n    %s" % adapter.get_address()
    print "get uuids:\n    %s" % adapter.get_uuids()

def test_found_pair():
    '''test_found_pair'''
    def on_device_found(adapter, address, values):
        print "address of found device \n %s " % address
        if address not in adapter.get_address_records():
            print "values of found device \n %s " % values
            print "now create device"
            return adapter.create_device(address)
        else:
            # print "device already exists"
            if adapter.get_discovering():
                print "stop discovery"
                adapter.stop_discovery()
            pass

    def on_device_created(adapter, dev_path):
        print "path of created device \n %s" % dev_path
        device = Device(dev_path)
        pair(device)

    def pair(device):        
        from agent import Agent
        path = "/org/bluez/agent"
        agent = Agent(path)
        agent.set_exit_on_release(False)
        device.set_trusted(True)
        if not device.get_paired():
            print "create paired device"
            adapter.create_paired_device(device.get_address(), path, "DisplayYesNo")

    def create_paired_reply(device):
        print "succeed paired device (%s)" % (device)

    def create_paired_error(error):
        print "paired device failed: %s" % (error)

    from manager import Manager
    from adapter import Adapter
    from device import Device

    manager = Manager()
    adapter = Adapter(manager.get_default_adapter())
    adapter.set_powered(True)
    adapter.set_discoverable(True)
    adapter.set_pairable(True)
    # print "adapter properties:\n %s" % adapter.get_properties()
    adapter.connect("device-found", on_device_found)
    adapter.connect("device-created", on_device_created)

    for dev in  adapter.get_devices():
        adapter.remove_device(dev)
    else:
        pass

    print "begin discovery \n"
    adapter.start_discovery()

    mainloop = gobject.MainLoop()
    mainloop.run()

def test_service():
    '''should had paired first'''
    def device_discover_services(device):
        # discovery services
        services = device.discover_services()
        import re
        for key in services.keys():
            p = re.compile(">.*?<")
            xml = p.sub("><", services[key].replace("\n", ""))
            print "[ 0x%5x ]" % (key)
            print xml
            print

    def device_get_services(device):
        # get services
        from device_service import DeviceService
        from utils import bluetooth_uuid_to_string

        for serv in device.get_services():
            service = DeviceService(serv)
            uuid = service.get_uuid()
            print "uuid:%s" % uuid
            print bluetooth_uuid_to_string(uuid)

    def device_get_uuids(device):
        from utils import bluetooth_uuid_to_string
        for uuid in device.get_uuids():
            print uuid
            print bluetooth_uuid_to_string(uuid)

    from manager import Manager
    from adapter import Adapter
    from device import Device

    manager = Manager()
    adapter = Adapter(manager.get_default_adapter())
    if adapter.get_devices():
        device = Device(adapter.get_devices()[0])
    else:
        print "after paired, should exists devices"

    # device_get_services(device)    
    # device_discover_services(device)    
    device_get_uuids(device)    

    mainloop = gobject.MainLoop()
    mainloop.run()

def test_phone():
    '''must had paired first, use xiaomi for test'''

    def get_device_supported_services(device):
        services = []
        from utils import bluetooth_uuid_to_string
        for uuid in device.get_uuids():
            if bluetooth_uuid_to_string(uuid) != None:
                services.append(bluetooth_uuid_to_string(uuid))
            else:
                continue

        return services    

    def send_file(device, files):
        ###please see the example in obex_agent.py
        pass

    def browse_device(device):
        ###please see the example in utils.py
        pass
    
    def connect_phone_audio(device):
        from device import AudioSource
        from device import Control

        if "AudioSource" not in get_device_supported_services(device):
            print "device not support AudioSource"
            return 

        audiosource = AudioSource(device.object_path)
        ###when connect, voice switch from phone to my'pc
        if audiosource.get_state() == "disconnected":
            audiosource.connect()

        if "A/V_RemoteControlTarget" not in get_device_supported_services(device):
            print "device not support A/V control"
            return
        
        control = Control(device.object_path)
        if not control.get_connected():
            control.connect()
            
        control.volume_up()    

    from manager import Manager
    from adapter import Adapter
    from device import Device

    manager = Manager()
    adapter = Adapter(manager.get_default_adapter())
    if adapter.get_devices():
        device = Device(adapter.get_devices()[0])
    else:
        print "after paired, should exists devices"

    connect_phone_audio(device)    

    mainloop = gobject.MainLoop()
    mainloop.run()

if __name__ == "__main__":
    # test_adapter_prop()
    # test_found_pair()
    # test_service()
    test_phone()
    pass
