#!/usr/bin/env python
#-*- coding:utf-8 -*-

from dss import app_theme
from mm.provider import ServiceProviders
sp = ServiceProviders()
country_list = sp.get_country_name_list()

def find_match_flag(country):
    formated_string = country.lower().replace(" ", "_").replace(",",'')
    try:
        app_theme.get_pixbuf("network/flags/"+"flag_"+formated_string + ".png")
    except:
        return None

for country in country_list:
    find_match_flag(country)

