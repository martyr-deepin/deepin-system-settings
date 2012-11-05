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

#copy from ubuntu systemservice backend

import dbus
import dbus.service
import re
import os
import apt_pkg
import dbus.mainloop.glib
import gobject
from nmlib.nm_utils import authWithPolicyKit

class ProxyService(dbus.service.Object):
    '''dbus proxy service'''
    DBUS_INTERFACE_NAME = "com.linuxdeepin.ProxyService"
    SUPPORTED_PROXIES = ("http","ftp", "https", "socks")

    DPKG_LOCK = "/var/lib/dpkg/lock"
    APT_ARCHIVES_LOCK = "/var/cache/apt/archives/lock"
    APT_LISTS_LOCK = "/var/lib/apt/lists/lock"
    UNATTENDED_UPGRADES_LOCK = "/var/run/unattended-upgrades.lock"

    def __init__(self, bus=None):
        if bus is None:
            bus = dbus.SystemBus()
        bus_name = dbus.service.BusName(self.DBUS_INTERFACE_NAME,
                                        bus=bus)
        dbus.service.Object.__init__(self, bus_name, '/')
        apt_pkg.init_config()

    # proxy stuff ---------------------------------------------------
    def _etc_environment_proxy(self, proxy_type):
        " internal that returns the /etc/environment proxy "
        if not os.path.exists("/etc/environment"):
            return ""
        for line in open("/etc/environment"):
            if line.startswith("%s_proxy=" % proxy_type):
                (key, value) = line.strip().split("=")
                value = value.strip('"')
                return value
        return ""

    def _http_proxy(self):
        " internal helper that returns the current http proxy "
        apt_proxy = self._apt_proxy("http")
        env_proxy = self._etc_environment_proxy("http")
        # FIXME: what to do if both proxies are differnet?
        return env_proxy

    def _apt_proxy(self, proxy_type):
        " internal helper that returns the configured apt proxy"
        apt_pkg.init_config()
        proxy = apt_pkg.config.find("Acquire::%s::proxy" % proxy_type)
        return proxy

    def _ftp_proxy(self):
        apt_proxy = self._apt_proxy("ftp")
        env_proxy = self._etc_environment_proxy("ftp")
        # FIXME: what to do if both proxies are differnet?
        return env_proxy

    def _socks_proxy(self):
        env_proxy = self._etc_environment_proxy("socks")
        return env_proxy

    def _ftp_apt_proxy(self):
        " internal helper that returns the configured apt proxy"
        apt_pkg.init_config()
        http_proxy = apt_pkg.config.find("Acquire::ftp::proxy")
        return http_proxy

    def _https_proxy(self):
        " internal helper that returns the current https proxy "
        env_proxy = self._etc_environment_proxy("https")
        return env_proxy

    def _verify_proxy(self, proxy_type, proxy):
        " internal helper, verify that the proxy string is valid "
        return verify_proxy(proxy_type, proxy)

    def _verify_no_proxy(self, proxy):
        " internal helper, verify that the no_proxy string is valid "
        return verify_no_proxy(proxy)

    @dbus.service.method(DBUS_INTERFACE_NAME,
                         in_signature='s', 
                         out_signature='s',
                         sender_keyword='sender',
                         connection_keyword='conn')
    def get_proxy(self, proxy_type, sender=None, conn=None):
        """ 
        Get the current system-wide proxy  for type "proxy_type"

        This function will look in the apt configuration to 
        find the current http proxy.
        """
        if proxy_type == "http":
            return self._http_proxy()
        if proxy_type == "https":
            return self._https_proxy()
        elif proxy_type == "ftp": 
            return self._ftp_proxy()
        elif proxy_type == "socks": 
            return self._socks_proxy()
        raise UnknownProxyTypeError, "proxy_type '%s' is unknown in get_proxy" % proxy_type


    def _write_apt_proxy(self, proxy_type, new_proxy):
        " helper that writes the new apt proxy "
        confdir = apt_pkg.config.find_dir("Dir::Etc") 
        if not self._verify_proxy(proxy_type, new_proxy):
            return False
        # now the difficult case (search the apt configuration files)
        # build the list of apt configuration files first
        apt_conffiles = [os.path.join(confdir,"apt.conf.d",n) for n in 
                         os.listdir(os.path.join(confdir,"apt.conf.d"))]
        apt_conffiles.insert(0, os.path.join(confdir,"apt.conf"))
        # then scan them for the content
        already_saved = False
        for f in apt_conffiles:
            new_content = []
            found = False
            try:
                file = open(f)
                for line in file:
                    # Only replace the Acquire::%s::proxy entry, not other more
                    # complicated forms of the proxy settings
                    if line.lower().startswith("acquire::%s::proxy " % proxy_type):
                        if already_saved:
                            continue
                        found = True
                        line = "Acquire::%s::proxy \"%s\";\n" % (proxy_type, new_proxy)
                        already_saved = True
                    new_content.append(line)
            except Exception:
                pass

            # if we didn't find the proxy, write it out now
            if not found and not already_saved:
                new_content.append("Acquire::%s::proxy \"%s\";\n" % (proxy_type, new_proxy))
                already_saved = True
            open(f,"w").write("".join(new_content))

        return True

    def _write_etc_environment_proxy(self, proxy_type, new_proxy):
        if not self._verify_proxy(proxy_type, new_proxy):
            return False
        found=False
        new_content=[]
        new_proxy_line = '%s_proxy="%s"\n' % (proxy_type, new_proxy)
        for line in open("/etc/environment"):
            if line.startswith("%s_proxy=" % proxy_type):
                line=new_proxy_line
                found = True
            new_content.append(line)
        if found:
            open("/etc/environment","w").write("".join(new_content))
        else:
            open("/etc/environment","a").write(new_proxy_line)
        return True

    def _clear_etc_environment_proxy(self, proxy_type):
        found=False
        new_content=[]
        for line in open("/etc/environment"):
            if line.startswith("%s_proxy=" % proxy_type):
                found = True
            else:
                new_content.append(line)
        if found:
            open("/etc/environment","w").write("".join(new_content))
        return True
    
    def _clear_apt_proxy(self, proxy_type):
        " helper that clears the apt proxy "
        confdir = apt_pkg.config.find_dir("Dir::Etc") 
        apt_conffiles = [os.path.join(confdir,"apt.conf.d",n) for n in 
                         os.listdir(os.path.join(confdir,"apt.conf.d"))]
        apt_conffiles.insert(0, os.path.join(confdir,"apt.conf"))
        for f in apt_conffiles:
            new_content = []
            found = False
            for line in open(f):
                # Only remove the Acquire::%s::proxy entry, not other more
                # complicated forms of the proxy settings
                if line.lower().startswith("acquire::%s::proxy " % proxy_type):
                    found = True
                else:
                    new_content.append(line)
            # if we found/replaced the proxy, write it out now
            if found:
                open(f,"w").write("".join(new_content))
        return True
    
    @dbus.service.method(DBUS_INTERFACE_NAME,
                         in_signature='ss', 
                         out_signature='b',
                         sender_keyword='sender',
                         connection_keyword='conn')
    def set_proxy(self, proxy_type, new_proxy, sender=None, conn=None):
        """
        Set a new system-wide proxy that looks like e.g.:
        http://proxy.host.net:port/

        This function will set a new apt configuration and
        modify /etc/environment
        
        """
        if not authWithPolicyKit(sender, conn, 
                                 "com.linuxdeepin.proxyservice.setproxy"):
            if not authWithPolicyKit(sender, conn,
                                     "org.gnome.gconf.defaults.set-system"):
                raise PermissionDeniedError, "Permission denied by policy"
        
        # check if something supported is set
        if not proxy_type in self.SUPPORTED_PROXIES:
            raise UnknownProxyTypeError, "proxy_type '%s' is unknown in set_proxy" % proxy_type
        
        # set (or reset)
        if new_proxy == "" or new_proxy is None:
            res = self._clear_apt_proxy(proxy_type)
            res &= self._clear_etc_environment_proxy(proxy_type)
        else:
            res = self._write_apt_proxy(proxy_type, new_proxy)
            res &= self._write_etc_environment_proxy(proxy_type, new_proxy)
        return res


    def _clear_etc_environment_no_proxy(self):
        found=False
        new_content=[]
        for line in open("/etc/environment"):
            if line.startswith("no_proxy="):
                found = True
            else:
                new_content.append(line)
        if found:
            open("/etc/environment","w").write("".join(new_content))
        return True

    def _write_etc_environment_no_proxy(self, new_proxy):
        if not self._verify_no_proxy(new_proxy):
            return False
        found=False
        new_content=[]
        new_proxy_line = 'no_proxy="%s"\n' % new_proxy
        for line in open("/etc/environment"):
            if line.startswith("no_proxy="):
                line=new_proxy_line
                found = True
            new_content.append(line)
        if found:
            open("/etc/environment","w").write("".join(new_content))
        else:
            open("/etc/environment","a").write(new_proxy_line)
        return True

    @dbus.service.method(DBUS_INTERFACE_NAME,
                         in_signature='s', 
                         out_signature='b',
                         sender_keyword='sender',
                         connection_keyword='conn')
    def set_no_proxy(self, new_no_proxy, sender=None, conn=None):
        """
        Set a new system-wide no_proxy list that looks like e.g.:
        localhost,foo.com

        This function will modify /etc/environment
        
        """
        if not authWithPolicyKit(sender, conn, 
                                 "com.linuxdeepin.proxyservice.setnoproxy"):
            if not authWithPolicyKit(sender, conn,
                                     "org.gnome.gconf.defaults.set-system"):
                raise PermissionDeniedError, "Permission denied by policy"
        
        # set (or reset)
        if new_no_proxy == "" or new_no_proxy is None:
            res = self._clear_no_proxy()
        else:
            res = self._write_etc_environment_no_proxy(new_no_proxy)
        return res

def verify_proxy(proxy_type, proxy):
    """
    This verifies a proxy string. It works by whitelisting
    certain charackters: 0-9a-zA-Z:/?=-;~+
    """
    # protocol://host:port/stuff
    verify_str = "%s://[a-zA-Z0-9.-]+:[0-9]+/*$" % proxy_type

    if not re.match(verify_str, proxy):
            return False
    return True

def verify_no_proxy(proxy):
    """
    This verifies a proxy string. It works by whitelisting
    certain charackters: 0-9a-zA-Z:/?=-;~+
    """
    # protocol://host:port/stuff
    verify_str = "[a-zA-Z0-9.-:,]+" 

    if not re.match(verify_str, proxy):
            return False
    return True


class UnknownProxyTypeError(dbus.DBusException):
    " an unknown proxy type was passed "
    pass

class PermissionDeniedError(dbus.DBusException):
    " permission denied by policy "
    pass



if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)  
    ProxyService()
    gobject.MainLoop().run()


