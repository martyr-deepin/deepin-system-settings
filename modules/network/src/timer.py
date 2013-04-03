#!/usr/bin/env python
#-*- coding:utf-8 -*-

import glib
class Timer(object):
    
    def __init__(self, interval, stop_callback):
        self.interval = interval
        self.stop_callback = stop_callback
        self.timer = 0

    def start(self):
        self.timer = glib.timeout_add(self.interval, self.__stop_timer_callback)

    def __stop_timer_callback(self):
        self.stop_callback()
        self.timer = 0
        return False
    
    def alive(self):
        return self.timer != 0
    
    def stop(self):
        if self.timer:
            glib.source_remove(self.timer)
            self.timer = 0
    
    def restart(self):
        self.stop()
        self.timer = glib.timeout_add(self.interval, self.__stop_timer_callback)
