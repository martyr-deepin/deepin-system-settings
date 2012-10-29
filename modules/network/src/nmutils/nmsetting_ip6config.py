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

from nmsetting import NMSetting
from nmlib.nm_utils import TypeConvert
import dbus

class NMSettingIP6Config (NMSetting):
    '''NMSettingIP6Config'''
    def __init__(self):
        NMSetting.__init__(self)
        self.name = "ipv6"

    @property    
    def method(self):
        if "method" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["method"])

    @method.setter
    def method(self, new_method):
        if new_method in ["ignore", "auto", "dhcp", "link-local", "manual", "shared"]:
            self.prop_dict["method"] = TypeConvert.py2_dbus_string(new_method)
        else:
            print "invalid value:%s to set ip4config method " % new_method

    @property
    def dns(self):
        if "dns" not in self.prop_dict.iterkeys():
            self.clear_dns()
        return map(lambda x: TypeConvert.ip6_net2native(x), self.prop_dict["dns"])

    @dns.setter
    def dns(self, new_dns):
        self.prop_dict["dns"] = TypeConvert.py2_dbus_array(new_dns)

    @dns.deleter
    def dns(self):
        if "dns" in self.prop_dict.iterkeys():
            del self.prop_dict["dns"]

    def add_dns(self, dns):
        if dns in self.dns:
            print "dns already added"
        else:
            self.prop_dict["dns"].append(TypeConvert.ip6_native2net(dns))

    def remove_dns(self, dns):
        if dns not in self.dns:
            print "doesn't have the dns to remove"
        else:
            self.prop_dict["dns"].remove(TypeConvert.ip6_native2net(dns))

    def clear_dns(self):
        self.prop_dict["dns"] =  dbus.Array([], signature = dbus.Signature('u'))

    @property
    def dns_search(self):
        if "dns-search" not in self.prop_dict.iterkeys():
            self.clear_dns_search()
        return TypeConvert.dbus2py(self.prop_dict["dns-search"])

    @dns_search.setter
    def dns_search(self, new_dns_search):
        self.prop_dict["dns-search"] = TypeConvert.py2_dbus_array(new_dns_search)

    @dns_search.deleter
    def dns_search(self):
        if "dns-search" in self.prop_dict.iterkeys():
            del self.prop_dict["dns-search"]

    def add_dns_search(self, dns):
        if dns in self.dns_search:
            print "already have the dns search"
        else:    
            if "dns-search" not in self.prop_dict.iterkeys():    
                self.clear_dns_search()
            self.prop_dict["dns-search"].append(TypeConvert.py2_dbus_string(dns))
        
    def remove_dns_search(self, dns):
        if dns not in self.dns_search:
            print "doesn't have the dns to remove"
        else:
            self.prop_dict["dns-search"].remove(TypeConvert.py2_dbus_string(dns))

    def clear_dns_search(self):
        self.prop_dict["dns-search"] = dbus.Array([], signature = dbus.Signature('s'))

    @property    
    def addresses(self):
        if "addresses" not in self.prop_dict.iterkeys():
            self.clear_addresses()
        return map(lambda x:TypeConvert.ip6address_net2native(x), TypeConvert.dbus2py(self.prop_dict["addresses"]))

    @addresses.setter
    def addresses(self, new_addresses):
        self.prop_dict["addresses"] = dbus.Array([TypeConvert.ip6address_net2native(x) for x in new_addresses], 
                                                 signature = dbus.Signature('(ayuay)'))

    @addresses.deleter
    def addresses(self):
        if "addresses" in self.prop_dict["addresses"].iterkeys():
            del self.prop_dict["addresses"]

    def add_address(self, address):
        if address in self.addresses:
            print "already have the address"
        else:
            self.prop_dict["addresses"].append(TypeConvert.ip6address_native2net(address))

    def remove_address(self, address):
        if address not in self.addresses:
            print "doesn't have the address to remove"
        else:
            self.prop_dict["addresses"].remove(TypeConvert.ip6address_native2net(address))

    def clear_addresses(self):
        self.prop_dict["addresses"] = dbus.Array([], signature = dbus.Signature('(ayuay)'))
        # for item in self.addresses:
        #     self.remove_address(item)

    @property
    def routes(self):
        if "routes" not in self.prop_dict.iterkeys():
            self.clear_routes()
        return map(lambda x:TypeConvert.ip6route_net2native(x), TypeConvert.dbus2py(self.prop_dict["routes"]))

    @routes.setter
    def routes(self, new_routes):
        self.prop_dict["routes"] = dbus.Array([TypeConvert.ip6route_native2net(x) for x in  new_routes],
                                              signature = dbus.Signature('(ayuay)'))

    @routes.deleter
    def routes(self):
        if "routes" in self.prop_dict.iterkeys():
            del self.prop_dict["routes"]

    def add_route(self, route):
        if route in self.routes:
            print "already have the route, cann't add again"
        else:
            self.prop_dict["routes"].append(TypeConvert.ip6route_native2net(route))
        
    def remove_route(self, route):
        if route not in self.routes:
            print "doesn't have the route to remove"
        else:
            self.prop_dict["routes"].remove(TypeConvert.ip6route_native2net(route))

    def clear_routes(self):
        self.prop_dict["routes"] = dbus.Array([], signature = dbus.Signature('(ayuay)'))

    @property    
    def ignore_auto_routes(self):
        if "ignore-auto-routes" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["ignore-auto-routes"])
        else:
            return False

    @ignore_auto_routes.setter
    def ignore_auto_routes(self, new_ignore_auto_routes):
        self.prop_dict["ignore-auto-routes"] = TypeConvert.py2_dbus_boolean(new_ignore_auto_routes)

    @ignore_auto_routes.deleter
    def ignore_auto_routes(self):
        if "ignore-auto-routes" in self.prop_dict.iterkeys():
            del self.prop_dict["ignore_auto_routes"]
            

    @property
    def ignore_auto_dns(self):
        if "ignore-auto-dns" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["ignore-auto-dns"])
        else:
            return False

    @ignore_auto_dns.setter
    def ignore_auto_dns(self, new_ignore_auto_dns):
        self.prop_dict["ignore-auto-dns"] = TypeConvert.py2_dbus_boolean(new_ignore_auto_dns)

    @property
    def dhcp_client_id(self):
        if "dhcp-client-id" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["dhcp-client-id"])

    @dhcp_client_id.setter
    def dhcp_client_id(self, new_dhcp_client_id):
        self.prop_dict["dhcp-client-id"] = TypeConvert.py2_dbus_string(new_dhcp_client_id)

    @dhcp_client_id.deleter
    def dhcp_client_id(self):
        if "dhcp-client-id" in self.prop_dict.iterkeys():
            del self.prop_dict["dhcp-client-id"]

    @property
    def dhcp_send_hostname(self):
        if "dhcp-send-hostname" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["dhcp-send-hostname"])
        else:
            return True

    @dhcp_send_hostname.setter
    def dhcp_send_hostname(self, new_dhcp_send_hostname):
        self.prop_dict["dhcp_send_hostname"] = TypeConvert.py2_dbus_boolean(new_dhcp_send_hostname)

    @dhcp_send_hostname.deleter
    def dhcp_send_hostname(self):
        if "dhcp-send-hostname" in self.prop_dict.iterkeys():
            del self.porp_dict["dhcp_send_hostname"]

    @property
    def dhcp_hostname(self):
        if "dhcp-hostname" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["dhcp-hostname"])

    @dhcp_hostname.setter
    def dhcp_hostname(self, new_dhcp_host_name):
        self.prop_dict["dhcp-hostname"] = TypeConvert.py2_dbus_string(new_dhcp_host_name)


    @dhcp_hostname.deleter
    def dhcp_hostname(self):
        if "dhcp-hostname" in self.prop_dict.iterkeys():
            del self.prop_dict["dhcp-hostname"]

    @property
    def never_default(self):
        if "never-default" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["never-default"])
        else:
            return False

    @never_default.setter
    def never_default(self, new_never_default):
        self.prop_dict["never-default"] = TypeConvert.py2_dbus_boolean(new_never_default)

    @property
    def may_fail(self):
        if "may-fail" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["may-fail"])
        else:
            return True

    @may_fail.setter
    def may_fail(self, new_may_fail):
        self.prop_dict["may-fail"] = TypeConvert.py2_dbus_boolean(new_may_fail)

    @may_fail.deleter
    def may_fail(self):
        if "may-fail" in self.prop_dict.iterkeys():
            del self.prop_dict["may-fail"]

    @property
    def ip6_privacy(self):
        if "ip6-privacy" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["ip6-privacy"])

    @ip6_privacy.setter
    def ip6_privacy(self, new_ip6_privacy):
        self.prop_dict["ip6-privacy"] = TypeConvert.py2_dbus_int32(new_ip6_privacy)

    def adapt_ip6config_commit(self):
        if self.prop_dict["method"] == "auto":
            self.adapt_auto_commit()
        elif self.prop_dict["method"] == "manual":
            self.adapt_manual_commit()
        elif self.prop_dict["method"] == "link-local":
            self.adapt_link_local_commit()
        elif self.prop_dict["method"] == "shared":
            self.adapt_shared_commit()
        elif self.prop_dict["method"] == "disabled":
            self.adapt_disabled_commit()
        else:
            pass

    def adapt_auto_commit(self):
        self.clear_addresses()

    def adapt_manual_commit(self):            
        del self.dhcp_client_id
        del self.dhcp_hostname
        del self.dhcp_send_hostname
        del self.ignore_auto_routes
        
    def adapt_link_local_commit(self):
        for key in self.prop_dict.iterkeys():
            if key not in ["addresses", "dns", "ignore-auto-routes", "may-fail",
                           "method", "never-default", "routes", "ip6-privacy"]:
                del self.prop_dict[key]

    def adapt_shared_commit(self):
        self.adapt_link_local_commit()

    def adapt_disabled_commit(self):
        pass

if __name__ == "__main__":
    ip6config = NMSettingIP6Config()
    ip6config.clear_addresses()
