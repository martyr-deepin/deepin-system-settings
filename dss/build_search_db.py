#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang YaoHua
# 
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
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

import os
import sys
supported_locales = ["zh_CN", "zh_TW", "en_US"]
from module_info import get_module_infos
from split_word import init_jieba
from search_page import KeywordSearch

init_jieba()

if sys.argv[1] in supported_locales:
    os.environ["LANGUAGE"] = sys.argv[1]
    keywords = []
    module_infos = get_module_infos()

    for module_info_list in module_infos:
        for module_info in module_info_list:
            if module_info.search_keyword != "None":
                try:
                    print "%s.%s" % (module_info.id, module_info.search_keyword)
                    module = __import__("%s.%s" % (module_info.id, module_info.search_keyword), fromlist=["keywords"])
                    keywords.append((module_info.id, module_info.name, module.keywords, module_info.menu_icon_pixbuf))
                except Exception, e:
                    print "Error %s %s" % (module_info.id, e)
                    continue

    # print "keywords", keywords
    keyword_search = KeywordSearch(keywords)
    keyword_search.build_index()

    # BuildIndexThread(keyword_search).start()
