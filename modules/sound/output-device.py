#!/usr/bin/env python
#-*- coding:utf-8 -*-

import dbus
import os
import gobject
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)
loop = gobject.MainLoop()
def connect():
    if 'PULSE_DBUS_SERVER' in os.environ:
        address = os.environ['PULSE_DBUS_SERVER']
    else:
        bus = dbus.SessionBus()
        server_lookup = bus.get_object("org.PulseAudio1", "/org/pulseaudio/server_lookup1")
        address = server_lookup.Get("org.PulseAudio.ServerLookup1", "Address", dbus_interface="org.freedesktop.DBus.Properties")
        #print "address:", address

    return dbus.connection.Connection(address)

conn = connect()
core = conn.get_object(object_path="/org/pulseaudio/core1")

sink_paths = core.Get("org.PulseAudio.Core1", "Sinks", dbus_interface="org.freedesktop.DBus.Properties")

for path in sink_paths:
    print path
    device = conn.get_object(object_path=path)
    # device index
    print "Index", device.Get("org.PulseAudio.Core1.Device", "Index", dbus_interface="org.freedesktop.DBus.Properties")
    # device name
    print "Name", device.Get("org.PulseAudio.Core1.Device", "Name", dbus_interface="org.freedesktop.DBus.Properties")
    # device driver.通常是源代码的文件名。
    print "Driver", device.Get("org.PulseAudio.Core1.Device", "Driver", dbus_interface="org.freedesktop.DBus.Properties")
    # 拥有该设备的模块。如果没有模块则没有该属性
    print "OwnerModule", device.Get("org.PulseAudio.Core1.Device", "OwnerModule", dbus_interface="org.freedesktop.DBus.Properties")
    # 该设备所属于的card.如果设备不是card的一部分，则没有该属性。
    print "Card", device.Get("org.PulseAudio.Core1.Device", "Card", dbus_interface="org.freedesktop.DBus.Properties")
    # 设备的样本格式。 http://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/Developer/Clients/DBus/Enumerations#Sampleformats
    print "SampleFormat", device.Get("org.PulseAudio.Core1.Device", "SampleFormat", dbus_interface="org.freedesktop.DBus.Properties")
    # 设备的样本率
    print "SampleRate", device.Get("org.PulseAudio.Core1.Device", "SampleRate", dbus_interface="org.freedesktop.DBus.Properties")
    # channels
    # 可能的声道：http://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/Developer/Clients/DBus/Enumerations#Channelpositions
    print "Channels", device.Get("org.PulseAudio.Core1.Device", "Channels", dbus_interface="org.freedesktop.DBus.Properties")
    # volume 每个声道的声音(rw)
    print "Volume", device.Get("org.PulseAudio.Core1.Device", "Volume", dbus_interface="org.freedesktop.DBus.Properties")
    property_manager = dbus.Interface(device, 'org.freedesktop.DBus.Properties')
    #print property_manager.Get('org.PulseAudio.Core1.Device', 'Volume')
    # 分别设置声道音量
    #property_manager.Set('org.PulseAudio.Core1.Device', 'Volume', dbus.Array([dbus.UInt32(1000), dbus.UInt32(0)], signature=dbus.Signature('u')))
    # 统一设置声道音量
    #property_manager.Set('org.PulseAudio.Core1.Device', 'Volume', dbus.Array([dbus.UInt32(1000)], signature=dbus.Signature('u')))
    # device是否配置了"flat volume"
    print "HasFlatVolume", device.Get("org.PulseAudio.Core1.Device", "HasFlatVolume", dbus_interface="org.freedesktop.DBus.Properties")
    # 音量是否可能转化为分贝
    #print "HasConvertibleToDecibelVolume", device.Get("org.PulseAudio.Core1.Device", "HasConvertibleToDecibelVolume", dbus_interface="org.freedesktop.DBus.Properties")
    #print "HasConvertibleToDecibelVolume", property_manager.Get('org.PulseAudio.Core1.Device', 'HasConvertibleToDecibelVolume')
    # 音量等级(100%时的值)
    print "BaseVolume", device.Get("org.PulseAudio.Core1.Device", "BaseVolume", dbus_interface="org.freedesktop.DBus.Properties")
    # 如果设备不支持任意音量值，该属性将返回一个可能的音量值；否则为65537
    print "VolumeSteps", device.Get("org.PulseAudio.Core1.Device", "VolumeSteps", dbus_interface="org.freedesktop.DBus.Properties")
    # 该设置是否静音(rw)
    print "Mute", device.Get("org.PulseAudio.Core1.Device", "Mute", dbus_interface="org.freedesktop.DBus.Properties")
    #property_manager.Set('org.PulseAudio.Core1.Device', 'Mute', dbus.Boolean(0))
    # 是否设备音量控制硬件音量
    print "HasHardwareVolume", device.Get("org.PulseAudio.Core1.Device", "HasHardwareVolume", dbus_interface="org.freedesktop.DBus.Properties")
    # 是否设备静音控制硬件静音
    #print "HasHardwareMute", device.Get("org.PulseAudio.Core1.Device", "HasHardwareMute", dbus_interface="org.freedesktop.DBus.Properties")
    # 配置延时（ms）
    print "ConfiguredLatency", device.Get("org.PulseAudio.Core1.Device", "ConfiguredLatency", dbus_interface="org.freedesktop.DBus.Properties")
    # 设备延时是否能够通过连接流的需求调节
    #print "HasDynamicLatency", device.Get("org.PulseAudio.Core1.Device", "HasDynamicLatency", dbus_interface="org.freedesktop.DBus.Properties")
    # device buffer的音频队列长度。不是所有设备都支持延时查询，在这些设备没有该属性
    #print "Latency", device.Get("org.PulseAudio.Core1.Device", "Latency", dbus_interface="org.freedesktop.DBus.Properties")
    # 该设备是否为硬件设备
    #print "IsHardwareDevice", device.Get("org.PulseAudio.Core1.Device", "IsHardwareDevice", dbus_interface="org.freedesktop.DBus.Properties")
    # 该设备是否为网络设备
    print "IsNetworkDevice", device.Get("org.PulseAudio.Core1.Device", "IsNetworkDevice", dbus_interface="org.freedesktop.DBus.Properties")
    # 当前设备状态 http://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/Developer/Clients/DBus/Enumerations#Devicestates
    print "State", device.Get("org.PulseAudio.Core1.Device", "State", dbus_interface="org.freedesktop.DBus.Properties")
    # 所有可用的设备端口
    print "Ports", device.Get("org.PulseAudio.Core1.Device", "Ports", dbus_interface="org.freedesktop.DBus.Properties")
    Ports = device.Get("org.PulseAudio.Core1.Device", "Ports", dbus_interface="org.freedesktop.DBus.Properties")
    for p in Ports:
        port = conn.get_object(object_path=p)
        prop = dbus.Interface(port, 'org.freedesktop.DBus.Properties')
        #print '\tIndex', port.Get("org.PulseAudio.Core1.DevicePort", "Index", "org.freedesktop.DBus.Properties")
        #print '\tName', port.Get("org.PulseAudio.Core1.DevicePort", "Name", "org.freedesktop.DBus.Properties")
        #print '\tDescription', port.Get("org.PulseAudio.Core1.DevicePort", "Description", "org.freedesktop.DBus.Properties")
        #print '\tPriority', port.Get("org.PulseAudio.Core1.DevicePort", "Priority", "org.freedesktop.DBus.Properties")
        print '\tIndex', prop.Get("org.PulseAudio.Core1.DevicePort", "Index")
        print '\tName', prop.Get("org.PulseAudio.Core1.DevicePort", "Name")
        print '\tDescription', prop.Get("org.PulseAudio.Core1.DevicePort", "Description")
        print '\tPriority', prop.Get("org.PulseAudio.Core1.DevicePort", "Priority")
        print '\t-------------------'

    #print dir(Ports[0]), type(Ports[0]), Ports[0]
    #for p in Ports:
        #print p._bus, p._named_service
    # 当前设备端口，如果设备不存在任何端口则没有该属性
    print "ActivePort", device.Get("org.PulseAudio.Core1.Device", "ActivePort", dbus_interface="org.freedesktop.DBus.Properties")
    # Set ActivePort还有问题
    #property_manager.Set("org.PulseAudio.Core1.Device", "ActivePort", Ports[1])
    #property_manager.Set("org.PulseAudio.Core1.Device", "ActivePort", device.GetPortByName('analog-output-headphones'))
    property_manager.Set("org.PulseAudio.Core1.Device", "ActivePort", property_manager.Get("org.PulseAudio.Core1.Device", "ActivePort"))
    #property_manager.Set("org.PulseAudio.Core1.Device", "ActivePort", dbus.ObjectPath("analog-output-headphones"))
    #property_manager.Set("org.PulseAudio.Core1.Device", "ActivePort", "<analog-output-headphones>")
    #property_manager.Set("org.PulseAudio.Core1.Device", "ActivePort", "耳机")
    #property_manager.Set("org.PulseAudio.Core1.Device", "ActivePort", dbus.ObjectPath(device.GetPortByName('analog-output')))
    ####
    print '-'*20
    #print "PortByName:", device.GetPortByName('1')
    #print "PortByName:", device.GetPortByName('port1')
    print "PortByName:", device.GetPortByName('analog-output')

#loop.run()
