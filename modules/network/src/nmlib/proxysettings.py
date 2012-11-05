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

from gi.repository import Gio

PROXY_SETTINGS = "org.gnome.system.proxy"
FTP_SETTINGS = "org.gnome.system.proxy.ftp"
HTTP_SETTINGS = "org.gnome.system.proxy.http"
HTTPS_SETTINGS = "org.gnome.system.proxy.https"
SOCKS_SETTINGS = "org.gnome.system.proxy.socks"

class ProxySettings(object):
    '''ProxySettings'''

    def __init__(self):
        self.proxy_settings = Gio.Settings.new(PROXY_SETTINGS)
        self.ftp_settings = Gio.Settings.new(FTP_SETTINGS)
        self.http_settings = Gio.Settings.new(HTTP_SETTINGS)
        self.https_settings = Gio.Settings.new(HTTPS_SETTINGS)
        self.socks_settings = Gio.Settings.new(SOCKS_SETTINGS)

    def set_proxy_mode(self, mode):
        if mode in ["none", "auto", "manual"]:
            self.proxy_settings.set_string("mode", mode)

    def get_proxy_mode(self):
        return self.proxy_settings.get_string("mode")

    def set_proxy_autoconfig_url(self, autoconfig_url):
        self.proxy_settings.set_string("autoconfig-url", autoconfig_url)
        
    def get_proxy_authconfig_url(self):
        return self.proxy_settings.get_string("authconfig-url")

    def set_proxy_ignore_hosts(self, ignore_hosts):
        self.proxy_settings.set_strv("ignore-hosts", ignore_hosts)

    def get_proxy_ignore_hosts(self):
        return self.proxy_settings.get_strv("ignore-hosts")

    def set_proxy_use_same_proxy(self, use_same_proxy):
        self.proxy_settings.set_boolean("use-same-proxy", use_same_proxy)
    
    def get_proxy_use_same_proxy(self):
        return self.proxy_settings.get_boolean("use-same-proxy")

    def set_http_authentication_password(self, password):
        self.http_settings.set_string("authentication-password", password)
    
    def get_http_authentication_password(self):
        return self.http_settings.get_string("authentication-password")

    def set_http_authentication_user(self, user):
        self.http_settings.set_string("authentication-user", user)

    def get_http_authentication_user(self):
        return self.http_settings.get_string("authentication-user")

    def set_http_enabled(self, enabled):
        self.http_settings.set_boolean("enabled", enabled)

    def get_http_enabled(self):
        return self.http_settings.get_boolean("enabled")

    def set_http_host(self, host):
        self.http_settings.set_string("host", host)

    def get_http_host(self):
        return self.http_settings.get_string("host")

    def set_http_port(self, port):
        self.http_settings.set_uint("port", port)

    def get_http_port(self):
        return self.http_settings.get_uint("port")

    def set_http_use_authentication(self, use_authentication):
        self.http_settings.set_boolean("use-authentication", use_authentication)

    def get_http_use_authentication(self):
        return self.http_settings.get_boolean("use-authentication")

    def set_ftp_host(self, host):
        self.ftp_settings.set_string("host", host)
    
    def get_ftp_host(self):
        return self.ftp_settings.get_string("host")
    
    def set_ftp_port(self, port):
        self.ftp_settings.set_uint("port", port)

    def get_ftp_port(self):
        return self.ftp_settings.get_uint("port")

    def set_https_host(self, host):
        self.http_settings.set_string("host", host)

    def get_https_host(self):
        return self.http_settings.get_string("host")

    def set_https_port(self, port):
        self.http_settings.set_uint("port", port)

    def get_https_port(self):
        return self.http_settings.get_uint("port")

    def set_socks_host(self, host):
        self.socks_settings.set_string("host", host)
    
    def get_socks_host(self):
        return self.socks_settings.get_string("host")

    def set_socks_port(self, port):
        self.socks_settings.set_uint("port", port)

    def get_socks_port(self):
        return self.socks_settings.get_uint("port")

proxy_settings = ProxySettings()

if __name__ == "__main__":
    pass
