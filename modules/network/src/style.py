#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os
from dtk.ui.utils import get_parent_dir, cairo_disable_antialias, color_hex_to_cairo
from dtk.ui.draw import draw_line
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from constants import *
import gtk

# Setting UI styles
def set_frame_box_align(box):
    #box.set_spacing(BETWEEN_SPACING)
    align = gtk.Alignment(0, 0, 0, 0)
    align.set_padding(FRAME_TOP_PADDING, STATUS_HEIGHT, FRAME_LEFT_PADDING, 0)
    align.add(box)

    return align

def set_box_with_align(box, types):
    if types is "text":
        align = gtk.Alignment(0, 0, 0, 0)
        align.set_padding(TEXT_WINDOW_TOP_PADDING, 0, TEXT_WINDOW_LEFT_PADDING, 0)
        align.add(box)
        return align
    else:
        align = gtk.Alignment(0, 0, 0, 0)
        align.set_padding(FRAME_TOP_PADDING, STATUS_HEIGHT, FRAME_LEFT_PADDING, FRAME_LEFT_PADDING)
        align.add(box)
        return align

def set_align_text_box(align):
    align.set_padding(TEXT_WINDOW_TOP_PADDING, 0, TEXT_WINDOW_LEFT_PADDING, 0)

def set_main_window(align, has_right=False):
    align.set_padding(FRAME_TOP_PADDING, STATUS_HEIGHT, FRAME_LEFT_PADDING, [0, FRAME_LEFT_PADDING][has_right is True])

def set_table(table):
    #table.set_row_spacings(8)
    table.set_col_spacings(BETWEEN_SPACING)

def wrap_with_align(widget):
    if type(widget.parent) == gtk.Alignment:
        return widget.parent
    else:
        align = gtk.Alignment(0, 0.5, 1, 0)
        align.set_size_request(-1, CONTAINNER_HEIGHT )
        align.add(widget)
        return align


def set_table_items(table, item_name):
    children = table.get_children()
    for child in children:
        if item_name is "entry":
            from dtk.ui.new_entry import InputEntry, PasswordEntry
            if type(child) is gtk.Alignment:
                c = child.get_children()[0]
                if type(c).__name__ == type(InputEntry()).__name__ or \
                    type(c).__name__ == type(PasswordEntry()).__name__:
                    c.set_size(222, WIDGET_HEIGHT)


def draw_out_line(cr, rect, exclude=[]):
    with cairo_disable_antialias(cr):
        BORDER_COLOR = color_hex_to_cairo("#d2d2d2")
        cr.set_source_rgb(*BORDER_COLOR)
        cr.set_line_width(1)
        
        # Top
        if "top" not in exclude:
            draw_line(cr, rect.x, rect.y, rect.x + rect.width, rect.y)
        # bottom
        if "bot" not in exclude:
            draw_line(cr, rect.x, rect.y + rect.height + 1, rect.x + rect.width, rect.y + rect.height +1)
        # left
        if "left" not in exclude:
            draw_line(cr, rect.x , rect.y , rect.x, rect.y + rect.height)
        # right
        if "right" not in exclude:
            draw_line(cr, rect.x + rect.width , rect.y + 29, rect.x + rect.width , rect.y + rect.height)

