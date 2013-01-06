#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
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
import gtk
import glib
import locale
import threading
import hashlib
import urllib2


try:
    import simplejson as json
except ImportError:    
    import json

DEFAULT_TIMEOUT = 5    

def download(remote_uri, local_uri, buffer_len=4096, timeout=DEFAULT_TIMEOUT):
    try:
        handle_read = urllib2.urlopen(remote_uri, timeout=timeout)
        handle_write = file(local_uri, "w")
        
        data = handle_read.read(buffer_len)
        handle_write.write(data)
        
        while data:
            data = handle_read.read(buffer_len)
            handle_write.write(data)
            
        handle_read.close()    
        handle_write.close()
    except Exception:
        try:
            os.unlink(local_uri)
        except:    
            pass
        return False
    
    if not os.path.exists(local_uri):
        return False
    return True

def _glib_wait_inner(timeout, glib_timeout_func):
    id = [None] # Have to hold the value in a mutable structure because
                # python's scoping rules prevent us assigning to an
                # outer scope directly.
    def waiter(function):
        def delayer(*args, **kwargs):
            if id[0]: glib.source_remove(id[0])
            id[0] = glib_timeout_func(timeout, function, *args, **kwargs)
        return delayer
    return waiter

def glib_wait(timeout):
    """
        Decorator to make a function run only after 'timeout'
        milliseconds have elapsed since the most recent call to the
        function.

        For example, if a function was given a timeout of 1000 and
        called once, then again half a second later, it would run
        only once, 1.5 seconds after the first call to it.

        Arguments are supported, but which call's set of arguments
        is used is undefined, so this is not useful for much beyond
        passing in unchanging arguments like 'self' or 'cls'.

        If the function returns a value that evaluates to True, it
        will be called again under the same timeout rules.
    """
    # 'undefined' is a bit of a white lie - it's always the most
    # recent call's args. However, I'm reserving the right to change
    # the implementation later for the moment, and really I don't
    # think it makes sense to use functions that have changing args
    # with this decorator.
    return _glib_wait_inner(timeout, glib.timeout_add)

def glib_wait_seconds(timeout):
    """
        Same as glib_wait, but uses glib.timeout_add_seconds instead
        of glib.timeout_add and takes its timeout in seconds. See the
        glib documention for why you might want to use one over the
        other.
    """
    return _glib_wait_inner(timeout, glib.timeout_add_seconds)

class VersionError(Exception):
    """
       Represents version discrepancies
    """
    #: the error message
    message = None

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return repr(self.message)


def get_system_lang():    
    (lang, encode) = locale.getdefaultlocale()
    return lang

def parser_json(raw):
    try:
        data = json.loads(raw)
    except:    
        try:
            data = eval(raw, type("Dummy", (dict,), dict(__getitem__=lambda s,n: n))())
        except:    
            data = {}
    return data    

def get_screen_size():
    root_window = gtk.gdk.get_default_root_window()
    return root_window.get_size()


class ThreadFetch(threading.Thread):            
    
    def __init__(self, fetch_funcs, success_funcs=None, fail_funcs=None):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.fetch_funcs = fetch_funcs
        self.success_funcs = success_funcs
        self.fail_funcs = fail_funcs
        
    def run(self):    
        result = self.fetch_funcs[0](*self.fetch_funcs[1])
        if result:
            if self.success_funcs:
                self.success_funcs[0](result, *self.success_funcs[1])
        else:        
            if self.fail_funcs:
                self.fail_funcs[0](*self.fail_funcs[1])

                
def get_md5(string):                
    return hashlib.md5(string).hexdigest()
