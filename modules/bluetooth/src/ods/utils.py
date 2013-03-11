# utils.py - utils to parse dbus exceptions and check instance type
#
# Copyright (C) 2008 Vinicius Gomes <vcgomes [at] gmail [dot] com>
# Copyright (C) 2008 Li Dongyang <Jerry87905 [at] gmail [dot] com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import dbus
import sys

BOLD = lambda(x): "\033[1m"+x+"\033[0m"

def dprint(*args):                                                              
    s = ""                                                          
    for a in args:                                                  
        s += (str(a) + " ")                                     
    
    co = sys._getframe(1).f_code                                    
    fname = BOLD(co.co_name)                                        
    
    print "_________"                                               
    print "%s %s" % (fname, "(%s:%d)" % (co.co_filename, co.co_firstlineno))
    print s

def raise_type_error(instance, cls):
    if not isinstance(instance, cls):
        raise TypeError('Expecting an instance of ' + cls.__name__ + ', not ' + type(instance).__name__)
