#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
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

from dtk.ui.utils import get_parent_dir, remove_directory
import sys
import os
import gobject
import gtk
import xappy
import jieba

sys.path.append(os.path.join(get_parent_dir(__file__, 2), "modules"))

SEARCH_DB_DIR = os.path.join(get_parent_dir(__file__, 2), "search_db")

class KeywordSearch:
    def __init__(self, keywords):
        self.__xappy = None

        self.__keywords = keywords

    def build_index(self, remove_old=True):
        if remove_old:
            remove_directory(SEARCH_DB_DIR)

        self.__xappy = xappy.IndexerConnection(SEARCH_DB_DIR)

        self.__xappy.add_field_action("module_id", 
                                      xappy.FieldActions.STORE_CONTENT)

        self.__xappy.add_field_action("keyword_term", 
                                      xappy.FieldActions.INDEX_FREETEXT, 
                                      nopos=True)

        for module_keyword in self.__keywords:
            for keyword in module_keyword[1]:
                module_doc = xappy.UnprocessedDocument()
                
                module_doc.fields.append(xappy.Field("module_id", keyword[0]))
                
                terms = list(jieba.cut(keyword[1]))
                module_doc.fields.append(xappy.Field("keyword_term", ' '.join(terms)))
                
                self.__xappy.add(module_doc)

        self.__xappy.close()

    def search_query(self, keywords):
        sconn = xappy.SearchConnection(SEARCH_DB_DIR)

        search = ' '.join(keywords)
        q = sconn.query_parse(search, default_op=sconn.OP_AND)
        results = sconn.search(q, 0, sconn.get_doccount())

        return map(lambda result: result.data["module_id"][0], results) 

class SearchPage(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self, module_infos):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)

        '''
        struct keywords {
            module_id, 
            keywords
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
                    module = __import__("%s.src.search_keyword" % module_info.id, fromlist=["keywords"])
                    self.__keywords.append((module_info.id, module.keywords))

        self.__keyword_search = KeywordSearch(self.__keywords)
        '''
        TODO: it might be a heavey operation depend on keywords count
        '''
        self.__keyword_search.build_index()

        print "DEBUG module_id", self.__keyword_search.search_query(["电源", "配置"])

gobject.type_register(SearchPage)
