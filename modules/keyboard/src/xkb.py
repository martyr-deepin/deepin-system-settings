#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
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

import xklavier
import gtk


class XKeyBoard(object):
    '''X KeyBoard set class'''
    def __init__(self):
        super(XKeyBoard, self).__init__()
        self.display = gtk.gdk.display_get_default()
        self.engine = xklavier.Engine(self.display)
        # ConfigRegistry
        self.configreg = xklavier.ConfigRegistry(self.engine)
        self.configreg.load(False)
        # current config
        self.configrec = xklavier.ConfigRec()
        self.configrec.get_from_server(self.engine)
        # layout variants dict
        self.layout_variants = {}
        self.configreg.foreach_layout(
            self.__create_xkb_dict, (self.layout_variants,
            'variants', self.configreg.foreach_layout_variant))
        # option groups dict
        self.option_groups = {}
        self.configreg.foreach_option_group(
            self.__create_xkb_dict, (self.option_groups,
            'options', self.configreg.foreach_option))

    def __create_xkb_dict(self, c_reg, item, (mdict, list_key, sub_foreach)):
        '''create layout dict'''
        mdict[item.get_name()] = {}
        mdict[item.get_name()]['descript'] = item.get_description()
        mdict[item.get_name()][list_key] = []
        sub_foreach(item.get_name(), self.__create_sub_dict, mdict[item.get_name()][list_key])
    
    def __create_sub_dict(self, c_reg, item, variants_list):
        '''create layout variants'''
        #print "multip:", item.get_data("allowMultipleSelection")
        var = {}
        var['name'] = item.get_name()
        var['descript'] = item.get_description()
        variants_list.append(var)
    
    def get_layout_variants(self):
        '''
        get system layout variants
        @return: system layout variants, a dict type
        '''
        return self.layout_variants
    
    def get_current_options(self):
        '''
        get current key options
        @return: a list contain current options
        '''
        return self.configrec.get_options()

    def get_current_layouts(self):
        '''
        get current layouts
        @return: a list contain current layouts
        '''
        return self.configrec.get_layouts()
    
    def set_current_layouts(self, layouts):
        '''
        set current layouts
        @param layouts: a list contain layouts
        '''
        return self.configrec.set_layouts(layouts)

    def get_current_variants(self):
        '''
        get current variants
        @return: a list contain current variants
        '''
        return self.configrec.get_variants()
    
    def set_current_variants(self, variants):
        '''
        set current variants
        @param variants: a list contain variants
        '''
        return self.configrec.set_variants(variants)
    
    def get_variants_description(self, name, layout_name=None):
        '''
        get variants description
        @param name: the layout variants name, a string type
        @param layout_name: the layout name, a string type
        @reutn: if the name is in layouts dict return the description, otherwise None
        '''
        if layout_name:
            if layout_name not in self.layout_variants:
                return None
            if not name:
                return self.layout_variants[layout_name]['descript']
            for var in self.layout_variants[layout_name]['variants']:
                if var['name'] == name:
                    return var['descript']
        else:
            for layout in self.layout_variants:
                variants = self.layout_variants[layout]['variants']
                for var in variants:
                    if var['name'] == name:
                        return var['descript']
        return None

    def get_current_model(self):
        '''
        get current model
        @return: a string contain current model
        '''
        return self.configrec.get_model()

    def update_current_config(self):
        ''' update the current config info'''
        self.configrec.get_from_server(self.engine)
    
    def activate_current_config(self):
        ''' apply the current to system '''
        self.configrec.activate(self.engine)

    def get_layout_treeitems(self):
        '''
        get layout items
        @return: a list contain arguments that LayoutItem need.
        '''
        items = []
        for layout in self.layout_variants:
            items.append((self.layout_variants[layout]['descript'], layout))
            variants = self.layout_variants[layout]['variants']
            for var in variants:
                items.append((var['descript'], layout, var['name']))
        return items

    def get_current_variants_description(self):
        '''
        get current variants name
        @return: a list contain current variants as arguments that LayoutItem need
        '''
        variants_name = []
        variants = self.get_current_variants()
        layouts = self.get_current_layouts()
        #print "current variants:", layouts, variants
        length = len(layouts)
        if not variants:
            variants = [''] * length
        i = 0
        while i < length:
            variants_name.append((
                self.get_variants_description(variants[i], layouts[i]), layouts[i], variants[i]))
            i += 1
        return variants_name
    
def search_layout_treeitems(treeitems, key):
    '''
    search layout name contain key from treeitems
    @param treeitems: search from the treeitems, a list contain LayoutItem.
    @param key: the search key, a string type
    @return: a sub list of treeitems
    '''
    key = key.strip()
    if not key:
        return treeitems
    result = []
    for item in treeitems:
        if key in item.name:
            result.append(item)
    return result

def get_treeview_layout_variants(treeview):
    '''
    get layout and layout_variants in the treeview
    @param treeview: get from the treeview, a TreeView type
    @return: a tuple contain layout and layout_variants
    '''
    items = treeview.visible_items
    layouts = []
    variants = []
    for i in items:
        layouts.append(i.layout)
        variants.append(i.variants)
    return (layouts, variants)
