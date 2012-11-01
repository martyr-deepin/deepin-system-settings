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
import dbus
import struct
import socket
import copy

class TypeConvert(object):
    
    def __init__(self):
        self.dbus_2py_dict = {"Array": "dbus_array_2py", "Boolean": "dbus_boolean_2py",
                              "Byte": "dbus_byte_2py", "ByteArray": "dbus_bytearray_2py",
                              "Dictionary": "dbus_dictionary_2py", "Double": "dbus_double_2py",
                              "Int16": "dbus_int16_2py", "Int32": "dbus_int32_2py",
                              "Int64": "dbus_int64_2py", "ObjectPath": "dbus_objectpath_2py",
                              "Signature": "dbus_signature_2py", "String": "dbus_string_2py",
                              "Struct": "dbus_struct_2py", "UInt16": "dbus_uint16_2py",
                              "UInt32": "dbus_uint32_2py", "UInt64": "dbus_uint64_2py",
                              "UTF8String": "dbus_utf8string_2py", "UnixFD": "dbus_unixfd_2py",
                              "tuple":"tuple_dbus2py", "unicode": "dbus_string_2py",
                              "str": "str_2str"
                              }

    def dbus2py(self, prop):
        return getattr(self, self.dbus_2py_dict[type(prop).__name__])(prop)
        # return apply(self.dbus_2py_dict[type(prop).__name, prop])

    def py2dbus(self, prop):
        pass

    def str_2str(self, prop):
        return str(prop)

    def tuple_dbus2py(self, prop):
        '''convert a python tuple who contains dbus type items'''
        return tuple([self.dbus2py(x) for x in prop])

    def dbus_array_2py(self, prop):
        if isinstance(prop, dbus.Array):
            return [self.dbus2py(x) for x in prop]

    def dbus_boolean_2py(self, prop):
        if isinstance(prop, dbus.Boolean):
            return bool(prop)

    def dbus_byte_2py(self, prop):
        if isinstance(prop, dbus.Byte):
            return int(prop)

    def dbus_bytearray_2py(self, prop):
        if isinstance(prop, dbus.ByteArray):
            return str(prop)

    def dbus_dictionary_2py(self, prop):
        if isinstance(prop, dbus.Dictionary):
            return {self.dbus2py(key):self.dbus2py(value) for key,value in prop.iteritems()}

    def dbus_double_2py(self, prop):
        if isinstance(prop, dbus.Double):
            return float(prop)

    def dbus_int16_2py(self, prop):
        if isinstance(prop, dbus.Int16):
            return int(prop)

    def dbus_int32_2py(self, prop):
        if isinstance(prop, dbus.Int32):
            return int(prop)

    def dbus_int64_2py(self, prop):
        if isinstance(prop, dbus.Int64):
            return long(prop)

    def dbus_objectpath_2py(self, prop):
        if isinstance(prop, dbus.ObjectPath):
            return str(prop)

    def dbus_signature_2py(self, prop):
        if isinstance(prop, dbus.Signature):
            return str(prop)

    # def dbus_string_2py(self, prop):
    #     if isinstance(prop, dbus.String):
    #         return unicode(prop)
    def dbus_string_2py(self, prop):
        if isinstance(prop, dbus.String):
            return str(prop)

    def dbus_struct_2py(self, prop):
        if isinstance(prop, dbus.Struct):
            return tuple(self.dbus2py(x) for x in prop)

    def dbus_uint16_2py(self, prop):
        if isinstance(prop, dbus.UInt16):
            return int(prop)

    def dbus_uint32_2py(self, prop):
        if isinstance(prop, dbus.UInt32):
            return long(prop)

    def dbus_uint64_2py(self, prop):
        if isinstance(prop, dbus.UInt64):
            return long(prop)

    def dbus_utf8string_2py(self, prop):
        if isinstance(prop, dbus.UTF8String):
            return str(prop)

    def dbus_unixfd_2py(self, prop):
        if isinstance(prop, dbus.UnixFD):
            return int(prop)

    def py2_dbus_array(self, prop):
        return dbus.Array(prop, signature = dbus.Signature('s'))

    def py2_dbus_boolean(self, prop):
        return dbus.Boolean(prop)

    def py2_dbus_byte(self, prop):
        return dbus.Byte(prop)

    def py2_dbus_bytearray(self, prop):
        return dbus.Array([dbus.Byte(x) for x in prop], signature = dbus.Signature('y'))

    def py2_dbus_dictionary(self, setting_dict):
        return dbus.Dictionary(setting_dict, signature = dbus.Signature('sv'))

    def py2_dbus_double(self, prop):
        return dbus.Double(prop)

    def py2_dbus_int16(self, prop):
        return dbus.Int16(prop)

    def py2_dbus_int32(self, prop):
        return dbus.Int32(prop)

    def py2_dbus_int64(self, prop):
        return dbus.Int64(prop)

    def py2_dbus_objectpath(self, prop):
        return dbus.ObjectPath(prop)

    def py2_dbus_signature(self, prop):
        return dbus.Signature(prop)

    def py2_dbus_string(self, prop):
        try:
            return dbus.String(unicode(prop,"utf-8"))
        except:
            return dbus.String(prop)

    def py2_dbus_struct(self, prop):
        return dbus.Struct(prop)

    def py2_dbus_uint16(self, prop):
        return dbus.UInt16(prop)

    def py2_dbus_uint32(self, prop):
        return dbus.UInt32(prop)

    def py2_dbus_uint64(self, prop):
        return dbus.UInt64(prop)

    def py2_dbus_utf8string(self, prop):
        return dbus.UTF8String(prop)

    def mac_address_array2string(self, mac_bytearray):
        return ":".join([hex(item)[2:].zfill(2) for item in mac_bytearray])
    
    def mac_address_string2array(self, mac_string):
        if self.is_valid_mac_address(mac_string):
            return self.py2_dbus_bytearray(map(lambda x:int(x,16), mac_string.split(":")))

    def is_valid_mac_address(self, mac_string):
        if len(mac_string.split(':')) == 6:
            return all(map(lambda x: -1<x<256, map(int, mac_string.split(':'))))
        else:
            return False

    def ssid_ascii2string(self, ssid_ascii_array):
        return "".join(map(lambda x: chr(x), ssid_ascii_array))

    def ssid_string2ascii(self, ssid_string):
        return self.py2_dbus_bytearray([ord(i) for i in ssid_string])

    def prefix_int2str(self, mask_int):
        bin_pre = ['0' for i in range(32)]
        for i in range(mask_int):
            bin_pre[i] = '1'
        tmpmask = [''.join(bin_pre[i*8 : i*8+8]) for i in range(4)]
        tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
        return '.'.join(tmpmask)

    def prefix_str2int(self, mask_str):
        mask_int = 0
        prefix = map(lambda x :bin(int(x)), mask_str.split('.'))
        for item in prefix:
            mask_int = mask_int + item.count('1')

        return mask_int    

    def ip4_net2native(self, ip_int):
        try:
            return socket.inet_ntoa(struct.pack("<I", ip_int))
        except socket.error:
            print "convert ip address failed\n"

    def ip4_native2net(self, ip_dot_string):
        try:
            return dbus.UInt32(struct.unpack("I",socket.inet_aton(ip_dot_string))[0])
        except socket.error:
            print "invalid ip address\n"

    def is_valid_ip4(self, ipstr):
        '''check address is valid addr/prefix/gateway presentation'''
        if len(ipstr.split('.')) == 4:
            return all(map(lambda x: -1<x<256, map(int,ipstr.split('.'))))
        else:
            return False

    def is_valid_netmask(self, mask_str):
        if not self.is_valid_ip4(mask_str):
            return False
        prefix = map(lambda x :bin(int(x)), mask_str.split('.'))
        prefix_str = "".join([str(x) for x in prefix])
        if not prefix_str.index("0"):
            return True
        else:
            if prefix_str[prefix_str.index("0"):].find("1") == -1:
                return True
            else:
                return False

    def is_valid_gw(self, ipstr, mask_str, gw_str):
        if not self.is_valid_ip4(gw_str):
            return False

        return all(map(lambda i: int(bin(int(ipstr.split('.')[i]))[2:]) & int(bin(int(mask_str.split('.')[i]))[2:]) == 
                     int(bin(int(gw_str.split('.')[i]))[2:]) & int(bin(int(mask_str.split('.')[i]))[2:])
                     ,[0,1,2,3]))


    def is_valid_ip6(self, ip_string):
        if len(ip_string.split('::')) > 3:
            return False

        for item in self.complete_ip6_address(ip_string):
            return all(map(lambda x:-1 < x < 16, map(int, list(item))))

        return False

    def ip4address_net2native(self, ip4address):
        if not isinstance(ip4address, list) or len(ip4address) !=3:
            print "ip4address must be a list contains address/prefix/gateway" 
        address = self.ip4_net2native(ip4address[0])
        prefix = self.prefix_int2str(ip4address[1])
        gateway = self.ip4_net2native(ip4address[2])

        return [address,prefix,gateway]

    def ip4address_native2net(self, ip4address_list):
        if not isinstance(ip4address_list, list) or len(ip4address_list) !=3:
            print "ip4address_list must be a list contains address/prefix/gateway" 

        address = self.ip4_native2net(ip4address_list[0])
        prefix = dbus.UInt32(self.prefix_str2int(ip4address_list[1]))
        gateway = self.ip4_native2net(ip4address_list[2])

        return dbus.Array([address,prefix,gateway], signature = dbus.Signature('u'))

    def ip4route_net2native(self, ip4route):
        if not isinstance(ip4route, list) or len(ip4route) != 4:
            print "ip4route must be a list contains dest/prefix/gw/metric"
        dest = self.ip4_net2native(ip4route[0])
        prefix = self.prefix_int2str(ip4route[1])
        next_hop = self.ip4_net2native(ip4route[2])
        metric = ip4route[3]

        return [dest,prefix,next_hop,metric]

    def ip4route_native2net(self, ip4route_list):
        if not isinstance(ip4route_list, list) or len(ip4route_list) != 4:
            print "ip4route must be a list contains dest/prefix/gw/metric"
        dest = self.ip4_native2net(ip4route_list[0])
        prefix = dbus.UInt32(self.prefix_str2int(ip4route_list[1]))
        next_hop = self.ip4_native2net(ip4route_list[2])
        metric = dbus.UInt32(ip4route_list[3])

        return dbus.Array([dest,prefix,next_hop,metric] ,signature = dbus.Signature('u'))    

    def ip6_prefix_int2str(self, prefix_int):
        return str(prefix_int)

    def ip6_prefix_str2int(self, prefix_str):
        return int(prefix_str)
    
    def ip6_net2native(self, ip_bytearray):
        if len(ip_bytearray) != 16:
            print "invalid ip6 address or simplify the address"
        hex_list = map(lambda x: hex(x)[2:], ip_bytearray)
        new_list = []
        for i in range(len(hex_list)):
            if i % 2 == 0:
                new_list.append(str(hex_list[i]).zfill(2) + str(hex_list[i+1]).zfill(2))

        return self.abbreviation_ip6_address(":".join(new_list))        

    def ip6_native2net(self, ip_string):
        return dbus.Array([dbus.Byte(int(x, 16)) for x in self.complete_ip6_address(ip_string)]
                          , signature = dbus.Signature('y'))  

    def abbreviation_ip6_address(self, ip6_string):
        '''abbreviation_ip6_address'''

        # def clear_left_zero(string):
        #     new_string = copy.deepcopy(string)
        #     for i in range(len(string) - 1):
        #         if string[i] == '0':
        #             new_string = copy.deepcopy(string[i+1:])
        #         else:
        #             break
        #     return new_string    
            # return string.lstrip('0')

        def is_zero(item):
            if item in ["0", "00", "000", "0000"]:
                return 1
            else:
                return 0

        def get_zero_continous(ip_list):
            '''a list record the [continous zero length] of ip_list'''
            zero_flag_list = map(lambda x:is_zero(x), ip_list)
            zero_continous_list = copy.deepcopy(zero_flag_list)
            for idx in range(len(zero_continous_list)):
                if zero_continous_list[idx] == 0:
                    continue
                else:
                    for index in range(idx + 1, len(zero_flag_list)):
                        if zero_flag_list[index] == 0:
                            break
                        else:
                            zero_continous_list[idx] = zero_continous_list[idx] + 1

            return zero_continous_list                

        def get_most_zero(continous_list):
            '''return where to abbreviation and the abbreviation length'''
            zero_len = max(continous_list)
            zero_begin = filter(lambda x:continous_list[x] == zero_len, range(len(continous_list)))[0]
            return [zero_begin, zero_len]

        # ip6_list = [clear_left_zero(x) for x in ip6_string.split(":")]
        ip6_list = [x.lstrip('0') for x in ip6_string.split(":")]
        abbr_left_str = ":".join(ip6_list)

        [abbr_start, abbr_lenth] = get_most_zero(get_zero_continous(ip6_list))

        if abbr_start == 0 and abbr_lenth == 0:
            abbr_str = abbr_left_str
        elif abbr_start == 0 and (abbr_start + abbr_lenth) == 8:
            abbr_str = "::"
        elif abbr_start == 0:
            abbr_str = abbr_left_str.replace("0:"*abbr_lenth, "::")
        elif abbr_start + abbr_lenth == 8:
            abbr_str = abbr_left_str.replace(":0"*abbr_lenth, "::")
        else: 
            abbr_str = abbr_left_str.replace("0:"*abbr_lenth, ":")
            
        return abbr_str    
            
    def complete_ip6_address(self, ip_string):
        '''complete_ip6_address, return list of 0x?? of length 16'''
        ###convert ip4 compatiable addr to ipv6 standard
        if ip_string.find('.') != -1 and len(ip_string.split('.')) == 4:
            ip4_string = ip_string.split(':')[-1]
            tmp = map(lambda x:hex(x)[2:], ip4_string.split('.'))    
            ip4_replace = str(tmp[0]) + str(tmp[1]) + ":" + str(tmp[2]) + str(tmp[3])
            ip_string.replace(ip4_string, ip4_replace)    

        ###complete the ip6 address    
        if len(ip_string.split(':')) < 8:
            if ip_string.startswith('::'):
                ip_string.replace("::", "00:"*(10 - len(ip_string.split(':'))))
            elif ip_string.endswith('::'):
                ip_string.replace("::", ":00"*(10 - len(ip_string.split(':'))))
            else:    
                ip_string.replace("::", "00".join(':'*(10 - len(ip_string.split(':')))))

        ip6_list = []        
        for item in map(lambda x: x.zfill(4), ip_string.split(':')):
            ip6_list.append(item[:2])
            ip6_list.append(item[2:])

        return ip6_list

    def ip6address_net2native(self, ip6address):
        address = self.ip6_net2native(ip6address[0])
        prefix = self.ip6_prefix_int2str(ip6address[1])
        gateway = self.ip6_net2native(ip6address[2])

        return [address, prefix, gateway]

    def ip6address_native2net(self, ip6address_list):
        address = self.ip6_native2net(ip6address_list[0])
        prefix = dbus.UInt32(self.ip6_prefix_str2int(ip6address_list[1]))
        gateway = self.ip6_native2net(ip6address_list[2])

        return dbus.Struct((address, prefix, gateway), signature = None)

    def ip6route_net2native(self, ip6route):
        dest = self.ip6_net2native(ip6route[0])
        prefix = self.ip6_prefix_int2str(ip6route[1])
        next_hop = self.ip6_net2native(ip6route[2])
        metric = ip6route[3]

        return [dest,prefix,next_hop,metric]

    def ip6route_native2net(self, ip6route_list):
        dest = self.ip6_native2net(ip6route_list[0])
        prefix = dbus.UInt32(self.ip6_prefix_str2int(ip6route_list[1]))
        next_hop = self.ip6_native2net(ip6route_list[2])
        metric = dbus.UInt32(ip6route_list[3])

        return dbus.Struct((dest, prefix, next_hop, metric), signature = None)

TypeConvert = TypeConvert()

def authWithPolicyKit(sender, connection, priv, interactive=1):
    #print "_authWithPolicyKit()"
    system_bus = dbus.SystemBus()
    obj = system_bus.get_object("org.freedesktop.PolicyKit1", 
                                "/org/freedesktop/PolicyKit1/Authority", 
                                "org.freedesktop.PolicyKit1.Authority")
    policykit = dbus.Interface(obj, "org.freedesktop.PolicyKit1.Authority")
    info = dbus.Interface(connection.get_object('org.freedesktop.DBus',
                                                '/org/freedesktop/DBus/Bus', 
                                                False), 
                          'org.freedesktop.DBus')
    pid = info.GetConnectionUnixProcessID(sender) 
    #print "pid is:",pid
    #print "priv: ", priv
    subject = ('unix-process', 
               { 'pid' : dbus.UInt32(pid, variant_level=1),
                 'start-time' : dbus.UInt64(0),
                 }
               )
    details = { '' : '' }
    flags = dbus.UInt32(interactive) #   AllowUserInteraction = 0x00000001
    cancel_id = ''
    (ok, notused, details) = policykit.CheckAuthorization(subject,
                                                          priv, 
                                                          details,
                                                          flags,
                                                          cancel_id)
    #print "ok: ", ok
    return ok
