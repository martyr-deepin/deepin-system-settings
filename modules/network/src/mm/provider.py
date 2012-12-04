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

import commands
import os
from dtk.ui.utils import get_parent_dir
providers = ET.ElementTree(file = get_parent_dir(__file__) + "/serviceproviders.xml")

countryxml = ET.ElementTree(file = get_parent_dir(__file__) + "/iso_3166.xml")

languagexml = ET.ElementTree(file = get_parent_dir(__file__) + "/iso639.xml")

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
        self.language_dict = None
        self.country_languages_dict = None

    def get_country_list(self):
        try:
            return  map(lambda x: x.get("code"), providers.iterfind("country"))    
        except:
            return []

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
        try:
            return map(lambda x:self.get_country_name(x), self.get_country_list())
        except:
            return []

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
            try:
                return map(lambda x:x.find("name").text, self.__providers)
            except:
                return []
        else:
            return []
    
    def get_country_gsm_providers_name(self, code):
        self.__providers = self.__get_country_providers(code)
        if self.__providers:
            has_gsm = filter(lambda x: x.find("gsm") != None, self.__providers)
            if has_gsm:
                try:
                    self.__providers = map(lambda x:x.find("name").text, has_gsm)
                    return self.__providers
                except:
                    return []
            else:
                return []
        else:
            return []

    def get_country_cdma_providers_name(self, code):
        self.__providers = self.__get_country_providers(code)
        if self.__providers:
            has_cdma = filter(lambda x: x.find("cdma") != None, self.__providers)
            if has_cdma:
                try:
                    self.__providers = map(lambda x:x.find("name").text, has_cdma)
                    return self.__providers
                except:
                    return []
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
                try:
                    return map(lambda x:( x.get("mcc"), x.get("mnc") ), self.__networks)
                except:
                    return None
            else:
                return None
        else:
            return None

    def __get_provider_apns(self, code, name):    
        '''only for gsm'''
        self.__provider = self.__get_country_provider(code, name)
        if self.__provider:
            try:
                self.__apns = self.__provider.findall(".//apn")
                return self.__apns
            except:
                return None
        else:
            return None

    def get_provider_apns_name(self, code, name):
        '''only for gsm'''
        self.__apns = self.__get_provider_apns(code, name)
        if self.__apns:
            try:
                return map(lambda x: x.get("value"), self.__apns)
            except:
                return []
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
            try:
                return self._apn.find("plan").get("type")
            except:
                return None
        else:
            return None

    def get_provider_apn_username(self, code, provider_name, apn_name):
        self._apn = self.__get_provider_apn(code, provider_name, apn_name)
        if self._apn:
            try:
                return self._apn.find("username").text
            except:
                return None
        else:
            return None


    def get_provider_apn_password(self, code, provider_name, apn_name):
        self._apn = self.__get_provider_apn(code, provider_name, apn_name)
        if self._apn:
            try:
                return self._apn.find("password").text
            except:
                return None
        else:
            return None

    def get_provider_apn_dns(self, code, provider_name, apn_name):
        self._apn = self.__get_provider_apn(code, provider_name, apn_name)
        if self._apn:
            try:
                return self._apn.find("dns").text
            except:
                return None
        else:
            return None

    def get_provider_username(self, code, provider):
        '''available for both of gsm and cdma, get the default one'''
        self.__provider = self.__get_country_provider(code, provider)
        if self.__provider:
            try:
                return self.__provider.find(".//username").text
            except:
                return None
        else:
            return None

    def get_provider_password(self, code, provider):
        '''available for both of gsm and cdma'''
        self.__provider = self.__get_country_provider(code, provider)
        if self.__provider:
            try:
                return self.__provider.find(".//password").text
            except:
                return None
        else:
            return None

    def get_country_from_timezone(self):
        try:
            import pytz
        except ImportError:
            print "pytz not installed"
            return self.get_country_from_language()

        timezone_country = {}

        for country in self.country_list:
            country_zones = pytz.country_timezones(country)

            for zone in country_zones:
                if zone not in timezone_country.iterkeys():
                    timezone_country[zone] = []

                if country not in timezone_country[zone]:
                    timezone_country[zone].append(country)
        if "TZ" in os.environ.keys():
            timezone = os.environ.get("TZ")
        else:    
            timezone = commands.getoutput("cat /etc/timezone")            

        if timezone in timezone_country.iterkeys():
            if len(timezone_country[timezone]) == 1:
                return timezone_country[timezone][0]
            else:
                return self.get_country_from_language(timezone_country[timezone])
        else:
            return self.get_country_from_language()

    def get_country_languages(self, code):

        if not self.country_languages_dict:
            self.country_languages_dict = {}
            try:
                pfile = open("country_languages.txt", "r").read().strip().splitlines()
                for item in pfile:
                    country = item.split("\t")[0].strip()
                    if "," in item:
                        languages = item.split("\t")[1].strip().split(",")

                    self.country_languages_dict[country] = languages
            except:
                return []

        country_name = self.get_country_name(code)    
        if country_name in self.country_languages_dict.iterkeys():
            return self.country_languages_dict[country_name]
        else:
            return []

    def get_country_from_language(self, country_list = []):
        if not country_list:
            country_list = self.country_list

        if "LANG" in os.environ.keys():
            lang = os.environ.get("LANG").split(".")
        else:
            lang = commands.getoutput("locale |grep 'LANG='").split("=")[-1]

        language_alpha2 = str.lower(lang[0][:2])

        if not self.language_dict:
            self.language_dict = {}
            for language in languagexml.iter():
                if not language.get("iso_639_1_code"):
                    continue
                else:
                    self.language_dict[language.get("iso_639_1_code")] = language.get("name")

        if language_alpha2 not in self.language_dict.iterkeys():
            return country_list[0]
        else:
            current_language = self.language_dict[language_alpha2]
            for country in country_list:
                for l in self.get_country_languages(country):
                    if current_language in l:
                        return country
                else:
                    continue
            return country_list[0]

if __name__ == "__main__":
    sp = ServiceProviders()
    # country_code =  sp.get_country_list()
    # country = sp.get_country_name_list()
    # print country_code[country.index("China")]
    # print sp.get_country_providers_name("cn")
    # print sp.get_country_gsm_providers_name("cn")
    # print sp.get_country_cdma_providers_name("cn")
    # print "networks",sp.get_provider_networks("cn", "China Mobile")
    # print "apns_name",sp.get_provider_apns_name("cn", "China Mobile")
    # print "apn_plan>",sp.get_provider_apn_plan("cn", "China Mobile", "cmwap")
    # print "username>",sp.get_provider_username("cn", "China Mobile")
    # print "password",sp.get_provider_password("cn", "China Mobile")
    # print sp.get_provider_username("cn", "China Telecom")
    # print sp.get_provider_password("cn", "China Telecom")
    # print sp.get_country_from_timezone()
    print sp.get_country_languages("cn")


