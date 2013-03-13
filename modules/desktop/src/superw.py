#! /usr/bin/env python                                                          
# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE

super_w_sequence = '''keydown Super_L
key W
keyup Super_L
'''

def keypress(sequence):
    p = Popen(['xte'], stdin=PIPE)
    p.communicate(input=sequence)

keypress(super_w_sequence)
