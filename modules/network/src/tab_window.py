#!/usr/bin/env python
#-*- coding:utf-8 -*-

from dtk.ui.tab_window import TabBox

class MyTabBox(TabBox):

    def __init__(self):
        TabBox.__init__(self)

    def add_items(self, items, default_index=0):
        '''
        Add items.
        
        @param items: A list of tab item, tab item format: (tab_name, tab_widget)
        @param default_index: Initialize index, default is 0.
        '''
        self.tab_items += items
       
        for item in items:
            self.tab_title_widths.append(get_content_size(item[0], DEFAULT_FONT_SIZE)[0] + self.tab_padding_x * 2)
            
        if self.current_tab_index < 0:
            self.switch_content(default_index)
        else:
            self.switch_content(self.current_tab_index)

