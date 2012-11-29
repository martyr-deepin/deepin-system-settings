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

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

providers = ET.ElementTree(file = "serviceproviders.xml")

countryxml = ET.ElementTree(file = "iso_3166.xml")

class ServiceProviders(object):

    def __init__(self):
        self.provider_dict = {}
        self.country_list = self.get_country_list()
        self.__country = None
        self.__providers = []
        self.__provider = None
        self.__networks = []
        self.__apns = []
        self.__apn = None

    def get_country_list(self):
        return  map(lambda x: x.get("code"), providers.iterfind("country"))    

    def get_country_name(self, code):
        if len(code) != 2:
            return None

        for country in countryxml.iter():
            try:
                if country.get("alpha_2_code") == str.upper(code):
                    return country.get("name")
            except:
                continue
        else:
            return None

    def get_country_name_list(self):
        return map(lambda x:self.get_country_name(x), self.get_country_list())

    def get_country_code(self, name):
        pass

    def __get_country(self, code):
        match = 'country[@code=\"' + code + '\"]'
        if providers.findall(match):
            self.__country = providers.findall(match)[0]
        return self.__country    

    def __get_country_providers(self, code):
        self.__country = self.__get_country(code)
        if self.__country:
            self.__providers = self.__country.findall("provider")
            
        return self.__providers    

    def get_country_providers_name(self, code):
        self.__providers = self.__get_country_providers(code)
        if self.__providers:
            return map(lambda x:x.find("name").text, self.__providers)
        else:
            return []
    
    def get_country_gsm_providers_name(self, code):
        self.__providers = self.__get_country_providers(code)
        if self.__providers:
            has_gsm = filter(lambda x: x.find("gsm") != None, self.__providers)
            if has_gsm:
                self.__providers = map(lambda x:x.find("name").text, has_gsm)
                return self.__providers
            else:
                return []
        else:
            return []

    def get_country_cdma_providers_name(self, code):
        self.__providers = self.__get_country_providers(code)
        if self.__providers:
            has_cdma = filter(lambda x: x.find("cdma") != None, self.__providers)
            if has_cdma:
                self.__providers = map(lambda x:x.find("name").text, has_cdma)
                return self.__providers
            else:
                return []
        else:
            return []

    def __get_country_provider(self, code, name):    
        self.__providers = self.__get_country_providers(code)
        if self.__providers:
            self.__provider = filter(lambda x:x.find("name").text == name, self.__providers)
            if self.__provider:
                return self.__provider[0]
            else:
                return None
        else:
            return None

    def get_provider_networks(self, code, name):
        self.__provider = self.__get_country_provider(code, name)
        if self.__provider:
            self.__networks = self.__provider.findall(".//network-id")
            if self.__networks:
                return map(lambda x:( x.get("mcc"), x.get("mnc") ), self.__networks)
            else:
                return None
        else:
            return None

    def __get_provider_apns(self, code, name):    
        '''only for gsm'''
        self.__provider = self.__get_country_provider(code, name)
        if self.__provider:
            self.__apns = self.__provider.findall(".//apn")
            return self.__apns
        else:
            return None

    def get_provider_apns_name(self, code, name):
        '''only for gsm'''
        self.__apns = self.__get_provider_apns(code, name)
        if self.__apns:
            return map(lambda x: x.get("value"), self.__apns)
        else:
            return []

    def __get_provider_apn(self, code, provider_name, apn_name):
        self.__apns = self.__get_provider_apns(code, provider_name)
        if self.__apns:
            self.__apn = filter(lambda x: x.get("value") == apn_name, self.__apns)
            if self.__apn:
                return self.__apn[0]
            else:
                return None
        else:
            return None


    def get_provider_apn_plan(self, code, provider_name, apn_name):
        self._apn = self.__get_provider_apn(code, provider_name, apn_name)
        if self._apn:
            return self._apn.find("plan").get("type")
        else:
            return None

    def get_provider_apn_username(self, code, provider_name, apn_name):
        self._apn = self.__get_provider_apn(code, provider_name, apn_name)
        if self._apn:
            return self._apn.find("username").text
        else:
            return None


    def get_provider_apn_password(self, code, provider_name, apn_name):
        self._apn = self.__get_provider_apn(code, provider_name, apn_name)
        if self._apn:
            return self._apn.find("password").text
        else:
            return None

    def get_provider_apn_dns(self, code, provider_name, apn_name):
        self._apn = self.__get_provider_apn(code, provider_name, apn_name)
        if self._apn:
            return self._apn.find("dns").text
        else:
            return None

    def get_provider_username(self, code, provider):
        '''available for both of gsm and cdma, get the default one'''
        self.__provider = self.__get_country_provider(code, provider)
        if self.__provider:
            return self.__provider.find(".//username").text
        else:
            return None

    def get_provider_password(self, code, provider):
        '''available for both of gsm and cdma'''
        self.__provider = self.__get_country_provider(code, provider)
        if self.__provider:
            return self.__provider.find(".//password").text
        else:
            return None


if __name__ == "__main__":
    sp = ServiceProviders()
    country_code =  sp.get_country_list()
    country = sp.get_country_name_list()
    print country_code[country.index("China")]
    

    print sp.get_country_providers_name("cn")
    print sp.get_country_gsm_providers_name("cn")
    print sp.get_country_cdma_providers_name("cn")
    print sp.get_provider_networks("cn", "China Mobile")
    print sp.get_provider_apns_name("cn", "China Mobile")
    print sp.get_provider_apn_plan("cn", "China Mobile", "cmwap")
    print sp.get_provider_username("cn", "China Mobile")
    print sp.get_provider_password("cn", "China Mobile")
    print sp.get_provider_username("cn", "China Telecom")
    print sp.get_provider_password("cn", "China Telecom")
