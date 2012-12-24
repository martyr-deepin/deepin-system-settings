#!/usr/bin/env python
#-*- coding:utf-8 -*-

from theme import app_theme,ui_theme
import sys
import os
from dtk.ui.utils import get_parent_dir, cairo_disable_antialias, color_hex_to_cairo
from dtk.ui.draw import draw_line
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from constant import *
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

def set_main_window(align):
    align.set_padding(FRAME_TOP_PADDING, STATUS_HEIGHT, FRAME_LEFT_PADDING, FRAME_LEFT_PADDING)

def set_table(table):
    table.set_row_spacings(CONTAINNER_HEIGHT - WIDGET_HEIGHT)
    table.set_col_spacings(BETWEEN_SPACING)


def draw_out_line(cr, rect, exclude=[]):
    with cairo_disable_antialias(cr):
        BORDER_COLOR = color_hex_to_cairo("#d2d2d2")
        cr.set_source_rgb(*BORDER_COLOR)
        cr.set_line_width(1)
        
        # Top
        #draw_line(cr, rect.x, rect.y, rect.x + rect.width, rect.y)
        # bottom
        draw_line(cr, rect.x, rect.y + rect.height, rect.x + rect.width, rect.y + rect.height)
        # left
        draw_line(cr, rect.x , rect.y , rect.x, rect.y + rect.height)
        # right
        draw_line(cr, rect.x + rect.width + 1, rect.y + 29, rect.x + rect.width + 1, rect.y + rect.height)

