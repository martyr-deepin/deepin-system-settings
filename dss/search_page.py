#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
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

from dtk.ui.utils import (color_hex_to_cairo, set_clickable_cursor)
from deepin_utils.ipc import is_dbus_name_exists
from deepin_utils.file import get_parent_dir, remove_directory
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.box import ImageBox
from dtk.ui.label import Label
import sys
import os
import gobject
import gtk
import dbus
'''
TODO: production level do not need split word any more
from split_word import init_jieba, split_word
'''
from theme import app_theme
from constant import *
import xappy
import threading as td

sys.path.append(os.path.join(get_parent_dir(__file__, 2), "modules"))

SEARCH_DB_DIR = os.path.join(get_parent_dir(__file__, 2), "search_db")

class BuildIndexThread(td.Thread):
    def __init__(self, ThisPtr):
        td.Thread.__init__(self)
        self.setDaemon(True)
        self.ThisPtr = ThisPtr

    def run(self):
        try:
            self.ThisPtr.build_index()
        except Exception, e:
            print "class BuildIndexThread got error" % e

class KeywordSearch:
    def __init__(self, keywords):
        self.__xappy = None

        self.__keywords = keywords

        '''
        TODO: production level do not need to init jieba any more
        init_jieba()
        '''
    '''
    TODO: production level no need to build index any more
    def build_index(self, remove_old=True):
        if remove_old:
            remove_directory(SEARCH_DB_DIR)

        self.__xappy = xappy.IndexerConnection(SEARCH_DB_DIR)

        self.__xappy.add_field_action("module_uid", 
                                      xappy.FieldActions.STORE_CONTENT)

        self.__xappy.add_field_action("keyword_term", 
                                      xappy.FieldActions.INDEX_FREETEXT, 
                                      nopos=True)

        for module_keyword in self.__keywords:
            for keyword in module_keyword[2]:
                module_doc = xappy.UnprocessedDocument()
                
                module_doc.fields.append(xappy.Field("module_uid", keyword[0]))
                
                terms = list(split_word(keyword[1], True))
                module_doc.fields.append(xappy.Field("keyword_term", ' '.join(terms)))
                
                self.__xappy.add(module_doc)

        self.__xappy.close()
    '''
    def query(self, keyword):
        return self.search_query([x for x in keyword.split(' ') if x.strip()])
        '''
        TODO: production level do not need to split word any more
        return self.search_query(list(split_word(keyword, True)))
        '''
    def search_query(self, keywords):
        sconn = xappy.SearchConnection(SEARCH_DB_DIR)

        search = ' '.join(keywords)
        q = sconn.query_parse(search, default_op=sconn.OP_AND)
        results = sconn.search(q, 0, sconn.get_doccount())
        
        return map(lambda result: result.data["module_uid"][0], results) 

class SearchPage(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self, module_infos):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)

        self.scrolled_window = ScrolledWindow()
        self.scrolled_window.set_size_request(800, 425)
        self.result_align = self.__setup_align(padding_top = TEXT_WINDOW_TOP_PADDING, 
                                               padding_left = TEXT_WINDOW_LEFT_PADDING)
        self.result_box = gtk.VBox()
        self.result_box.connect("expose-event", self.__expose)
        self.result_align.add(self.result_box)

        '''
        struct keywords {
            module_id, 
            module_name, 
            module_keywords {
                uid, 
                keyword
            }
        }
        '''
        self.__keywords = []

        self.__module_infos = module_infos
        '''
        TODO: from EACH MODULE import keywords
        '''
        for module_info_list in self.__module_infos:
            for module_info in module_info_list:
                if module_info.search_keyword != "None":
                    try:
                        module = __import__("%s.%s" % (module_info.id, module_info.search_keyword), fromlist=["keywords"])
                        self.__keywords.append((module_info.id, module_info.name, module.keywords, module_info.menu_icon_pixbuf))
                    except Exception, e:
                        print "Error %s" % e
                        continue

        self.__keyword_search = KeywordSearch(self.__keywords)
        '''
        TODO: build index might be a heavey operation depend on keywords count
              production level do not need to build index any more
        BuildIndexThread(self).start()
        '''
        self.scrolled_window.add_child(self.result_align)
        self.pack_start(self.scrolled_window)

    def __expose(self, widget, event):
        cr = widget.window.cairo_create()                                       
        rect = widget.allocation                                                
        
        cr.set_source_rgb(*color_hex_to_cairo(MODULE_BG_COLOR))                     
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)                       
        cr.fill()
    
    def __setup_align(self, 
                      padding_top=5, 
                      padding_bottom=5, 
                      padding_left=5,
                      padding_right=5):
        align = gtk.Alignment()
        align.set(0, 0, 0, 0)
        align.set_padding(padding_top, 
                          padding_bottom, 
                          padding_left, 
                          padding_right)
        align.connect("expose-event", self.__expose)
        return align

    def __setup_label(self, 
                      text="", 
                      text_size=CONTENT_FONT_SIZE, 
                      label_width=680, 
                      wrap_width=None):
        label = Label(text = text, 
                      text_size = text_size, 
                      label_width = label_width, 
                      wrap_width = wrap_width)
        return label
  
    def __handle_dbus_replay(self, *reply):
        pass

    def __handle_dbus_error(self, *error):
        pass

    def __button_press(self, widget, event, module_id, module_uid=""):
        if is_dbus_name_exists(APP_DBUS_NAME):
            bus_object = dbus.SessionBus().get_object(APP_DBUS_NAME, APP_OBJECT_NAME)
            method = bus_object.get_dbus_method("message_receiver")
            method("goto", 
                   (module_id, module_uid), 
                   reply_handler=self.__handle_dbus_replay, 
                   error_handler=self.__handle_dbus_error)

    def query(self, keyword):
        results = self.__keyword_search.query(keyword)
        is_drawn_module_name = False
 
        '''
        TODO: clear preview widgets
        '''
        for widget in self.result_box.get_children():
            self.result_box.remove(widget)

        if len(results) == 0:                  
            no_result_align = self.__setup_align(padding_top = 45, padding_left = 180)
            no_result_image = ImageBox(app_theme.get_pixbuf("search/noresult.png"))
            no_result_align.add(no_result_image)
            self.result_box.pack_start(no_result_align, False, False)   
            self.show_all()
            return 
        
        for module_keyword in self.__keywords:
            is_drawn_module_name = False
            for keyword in module_keyword[2]:
                if keyword[0] in results:
                    if not is_drawn_module_name:
                        module_name_align = self.__setup_align()
                        module_name_box = gtk.HBox(spacing = WIDGET_SPACING)
                        module_image = gtk.Image()
                        module_image.set_from_pixbuf(module_keyword[3])
                        module_name_label = self.__setup_label("<span foreground=\"blue\" underline=\"single\">%s</span>" % module_keyword[1], TITLE_FONT_SIZE)
                        set_clickable_cursor(module_name_label)
                        module_name_label.connect("button-press-event", 
                                                  self.__button_press, 
                                                  module_keyword[0])
                        module_name_box.pack_start(module_image, False, False)
                        module_name_box.pack_start(module_name_label, False, False)
                        module_name_align.add(module_name_box)
                        self.result_box.pack_start(module_name_align, False, False)
                        is_drawn_module_name = True
                    
                    module_keyword_align = self.__setup_align(padding_left = 30)
                    module_keyword_label = self.__setup_label("<span foreground=\"blue\" underline=\"single\">%s</span>" % keyword[1])
                    set_clickable_cursor(module_keyword_label)
                    module_keyword_label.connect("button-press-event", 
                                                 self.__button_press, 
                                                 module_keyword[0], 
                                                 keyword[0])
                    module_keyword_align.add(module_keyword_label)
                    self.result_box.pack_start(module_keyword_align, False, False)
                    '''
                    TODO: if remove widgets from self, it is better to show_all
                    '''
                    self.show_all()

    def build_index(self):
        self.__keyword_search.build_index()

gobject.type_register(SearchPage)
