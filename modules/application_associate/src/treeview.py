#!/usr/bin/env python
#-*- coding:utf-8 -*-
from theme import app_theme
from dtk.ui.new_treeview import TreeView, TreeItem
from dtk.ui.button import Button
from dtk.ui.utils import get_content_size
from dtk.ui.draw import (draw_pixbuf, draw_text, 
                         draw_vlinear)
import gtk
import pango

def render_background( cr, rect):
    background_color = [(0,["#ffffff", 1.0]),
                        (1,["#ffffff", 1.0])]
    draw_vlinear(cr, rect.x ,rect.y, rect.width, rect.height, background_color)

class SessionMain(gtk.VBox):
    def __init__(self):

        gtk.VBox.__init__(self)
        
        self.set_size_request(727, 337)
        self.connect("expose-event", self.expose_outline)

        self.add(Button("sasfsd"))

        
    def expose_outline(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation

        cr.rectangle(rect.x, rect.y, rect.width, rect.width)

        cr.stroke()



class SessionItem(TreeItem):

    def __init__(self, app_name, company_name):

        TreeItem.__init__(self)

        self.app_name = app_name
        self.company_name = company_name
        self.state = "Active"

    def render_app(self, cr, rect):
        render_background(cr, rect)
        CHECK_LEFT_PADDING = 5
        CHECK_RIGHT_PADDING = 5
        
        if self.is_select:
            check_icon = app_theme.get_pixbuf("Network/check_box.png").get_pixbuf()
        else:
            check_icon = app_theme.get_pixbuf("Network/check_box_out.png").get_pixbuf()

        draw_pixbuf(cr, check_icon, rect.x + CHECK_LEFT_PADDING, rect.y + (rect.height - check_icon.get_height())/2)
        
        # Draw Text

        (text_width, text_height) = get_content_size(self.app_name)
        draw_text(cr, self.app_name, rect.x + CHECK_RIGHT_PADDING*2 + check_icon.get_width(), rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)

    def render_company(self, cr, rect):
        render_background(cr, rect)
        (text_width, text_height) = get_content_size(self.company_name)
        draw_text(cr, self.company_name, rect.x, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)
        
    def render_state(self, cr, rect):
        render_background(cr, rect)
        (text_width, text_height) = get_content_size(self.state)
        draw_text(cr, self.state, rect.x, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)

    def get_column_renders(self):
        return [self.render_app, self.render_company, self.render_state]

    def get_column_widths(self):
        '''docstring for get_column_widths'''
        return [-1, -1, -1]

    def get_height(self):
        return 30

    def select(self):
        self.is_select = True
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def unselect(self):
        self.is_select = False
        if self.redraw_request_callback:
            self.redraw_request_callback(self)



class TitleItem(TreeItem):

    def __init__(self):
        TreeItem.__init__(self)
        
    def render_app_name(self, cr, rect):

        '''docstring for _'''
        (text_width, text_height) = get_content_size("程序名称")
        draw_text(cr, "程序名称", rect.x, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)

    def render_company_name(self, cr, rect):
        (text_width, text_height) = get_content_size("制造商")
        draw_text(cr, "制造商", rect.x, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)

    def render_state(self, cr ,rect):
        (text_width, text_height) = get_content_size("状态")
        draw_text(cr, "状态", rect.x, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)

    def get_column_renders(self):
        return [self.render_app_name, self.render_company_name, self.render_state]

    def get_column_widths(self):
        return [335, 300 , 89]

    def get_height(self):
        return 30








