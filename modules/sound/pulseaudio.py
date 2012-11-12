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

import traceback
import os
import syslog
import re

def run_command(command):
    try:
        os.system(command)
    except:
        for line in traceback.format_exc().split("\n"):
            syslog.syslog(syslog.LOG_ERR,line)

def get_command_oneput(command):
    '''run command directly use os.system,return a string item'''
    result=" "
    try:
        f = os.popen(command)
        result = f.readline()
    except:
        for line in traceback.format_exc().split("\n"):
            syslog.syslog(syslog.LOG_ERR,line)
    finally:
        f.close()

    return result    

def get_command_output(command):
    '''run command directly use os.system,return result:[]'''
    data = None
    try:
        f = os.popen(command)
        data = f.readlines()
    except:
        for line in traceback.format_exc().split("\n"):
            syslog.syslog(syslog.LOG_ERR,line)
    finally:
        f.close()

    return data

index_re = re.compile(r" *index")

def parse_output():
    pass

class PulseAudio(object):

    def __init__(self):
        self.modules = []

    def list_modules(self):
        mod_dict = {}
        command = "pacmd list-modules"
        modules = index_re.split(",".join(get_command_output(command)[2:]))

        for i in range(len(modules)):
            mod_dict[i] = modules[i].split(",")
                
        return mod_dict        

    def list_sinks(self):
        command = "pacmd list-sinks"
        run_command(command)

    def list_sources(self):
        command = "pacmd list-sources"
        run_command(command)

    def list_clients(self):
        command = "pacmd list-clients"
        run_command(command)

    def list_sink_inputs(self):
        command = "pacmd list-sink-inputs"
        run_command(command)

    def list_source_outpus(self):
        command = "pacmd list-source-outpus"
        run_command(command)

    def list_cards(self):
        command = "pacmd list-cards"
        run_command(command)

    def stat(self):
        command = "pacmd stat"
        run_command(command)

    def info(self):
        command = "pacmd info"
        run_command(command)

    def load_module(self, name, *args):    
        command = "pacmd load-module %s" % (name, args)
        run_command(command)
        
    def unload_module(self, index):
        command = "pacmd unload-module %d" % index
        run_command(command)

    def describe_module(self, name):
        command = "pacmd descirbe-module %s" % name
        run_command(command)

    def set_sink_volume(self, identifier, volume):
        if isinstance(identifier, int):
            command = "pacmd set-sink-volume %d %d" % (identifier,volume)
        elif isinstance(identifier, str):
            command = "pacmd set-sink-volume %s %d" % (identifier, volume)
        else:
            print "must support index or name to set sink volume"
        run_command(command)    

    def set_sink_input_volume(self, index, volume):    
        command = "pacmd set-sink-input-volume %d %d" % (index, volume) 
        run_command(command)    

    def set_source_volume(self, identifier, volume):    
        if isinstance(identifier, int):
            command = "pacmd set-source-volume %d %d" % (identifier, volume)
        elif isinstance(identifier, str):
            command = "pacmd set-source-volume %s %d" % (identifier, volume)
        else:
            print "must support index or name to set source volume"
        run_command(command)    

    def set_sink_mute(self, identifier, mute):    
        if isinstance(identifier, int):
            command = "pacmd set-source-mute %d %d" % (identifier, mute)
        elif isinstance(identifier, str):
            command = "pacmd set-source-mute %s %d" % (identifier, mute)
        else:
            print "must support index or name to set sink mute"
        run_command(command)    

    def set_sink_input_mute(self, index, mute):    
        command = "pacmd set-sink-input-mute %d %d" % (index, mute)
        run_command(command)    


    def set_source_mute(self, identifier, mute):    
        if isinstance(identifier, int):
            command = "pacmd set-source-mute %d %d" % (identifier, mute)
        elif isinstance(identifier, str):
            command = "pacmd set-source-mute %s %d" % (identifier, mute)
        else:
            print "must support index or name to set source mute"
        run_command(command)    

    def update_sink_proplist(self, identifier, properties):
        if isinstance(identifier, int):
            command = "pacmd update-sink-proplist " + identifier + " " + properties
        elif isinstance(identifier, str):
            command = "pacmd update-sink-proplist " + identifier + " " + properties 
        else:
            print "must support index or name to update sink proplist"
        run_command(command)    

    def update_source_proplist(self, identifier, properties):
        if isinstance(identifier, int):
            command = "pacmd update-source-proplist " + identifier + " " + properties
        elif isinstance(identifier, str):
            command = "pacmd update-source-proplist " + identifier + " " + properties 
        else:
            print "must support index or name to update source proplist"
        run_command(command)    
        
    def update_sink_input_proplist(self, index, properties):
        command = "pacmd update-sink-input-proplist " + index + " " + properties
        run_command(command)

    def update_source_output_proplist(self, index, properties):
        command = "pacmd update-source-output-proplist " + index + " " + properties
        run_command(command)

    def set_default_sink(self, identifier):
        command = "pacmd set-default-sink " + identifier
        run_command(command)

    def set_default_source(self, identifier):
        command = "pacmd set-default-source " + identifier
        run_command(command)

    def kill_client(self, index):
        command = "pacmd kill-client " + index
        run_command(command)

    def kill_sink_input(self, index):
        command = "pacmd kill-sink-input " + index
        run_command(command)

    def kill_source_output(self, index):
        command = "pacmd kill-source-output " + index

    def list_samples(self):
        command = "pacmd list-samples"
        run_command(command)

    def play_samples(self, name, identifier):
        command = "pacmd play-sample " + name + " " + identifier
        run_command(command)

    def remove_sample(self, name):
        command = "pacmd remove-sample " + name
        run_command(command)

    def load_sample(self, name, filename):
        command = "pacmd load-sample " + name + " " + filename
        run_command(command)

    def load_sample_lazy(self, name, filename):
        command = "pacmd load-sample-lazy "+ name + " " + filename
        run_command(command)

    def load_sample_dir_lazy(self, pathname):
        command = "pacmd load-sample-dir-lazy " + pathname
        run_command(command)

    def play_file(self, filename, identifier):
        command = "pacmd play-file " + filename + " " + identifier
        run_command(command)

    def dump(self):
        command = "pacmd dump"
        run_command(command)

    def move_sink_input(self, index, sink):
        command = "pacmd move-sink-input " + index + " " + sink
        run_command(command)

    def move_source_output(self, index, source):
        command = "pacmd move-source-output " + index + " " + source
        run_command(command)

    def suspend_sink(self, identifier, suspend):
        command = "pacmd suspend-sink " + identifier + "" + suspend
        run_command(command)

    def suspend_source(self, identifier, suspend):
        command = "pacmd suspend-source " + identifier + " " + suspend
        run_command(command)

    def suspend(self, suspend):
        command = "pacmd suspend " + suspend
        run_command(command)

    def set_card_profile(self, index, name):
        command = "pacmd set-card-profile " + index + " " + name
        run_command(command)

    def set_sink_port(self, index, name):    
        command = "pacmd set-sink-port " + index + " " + name
        run_command(command)

    def set_source_port(self, index, name):    
        command = "pacmd set-source-port " + index + " " + name
        run_command(command)

    def set_log_level(self, level):
        command = "pacmd set-log-level " + level
        run_command(command)

    def set_log_meta(self, meta):
        command = "pacmd set-log-meta " + meta
        run_command(command)

    def set_log_backtrace(self, frames):
        command = "pacmd set-log-backtrace " + frames
        run_command(command)
        

if __name__ == "__main__":
    pa = PulseAudio()
    print pa.list_modules()
