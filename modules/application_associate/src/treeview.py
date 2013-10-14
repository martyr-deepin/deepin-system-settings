#!/usr/bin/env python
#-*- coding:utf-8 -*-
from theme import app_theme
from dtk.ui.treeview import TreeItem
from dtk.ui.button import Button, CheckButtonBuffer
from dtk.ui.utils import get_content_size, color_hex_to_cairo
from dtk.ui.draw import (draw_text, draw_vlinear)
import gtk
import pango
from nls import _
CHECK_WIDTH = 60
def str_mark_down(string):
    if string:
        return string.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") 
    else:
        return ''

def render_background(cr, rect, is_select=False):
    if is_select:
        background_color = [(0,["#91aadd", 1.0]),
                            (1,["#91aadd", 1.0])]
    else:
        background_color = [(0,["#ffffff", 1.0]),
                            (1,["#ffffff", 1.0])]

    draw_vlinear(cr, rect.x ,rect.y, rect.width , rect.height, background_color)

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


class NothingItem(TreeItem):

    def __init__(self):
        TreeItem.__init__(self)

    def render_nothing(self, cr, rect):

        self.render_background(cr, rect)
        #draw_text(cr, _("no autostart"), rect.x , rect.y, rect.width, rect.height,
                #alignment = pango.ALIGN_CENTER)

    def get_column_renders(self):
        return [lambda w,r: self.render_background(w, r),
                lambda w,r: self.render_background(w, r),
                self.render_nothing,
                lambda w,r: self.render_background(w, r)]

    def get_column_widths(self):
        '''docstring for get_column_widths'''
        return [CHECK_WIDTH, 200, 300, 200]
    
    def get_height(self):
        return 30

    def render_background(self,  cr, rect):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

class SessionItem(TreeItem):

    def __init__(self, session_view, item):

        TreeItem.__init__(self)
        self.session_view = session_view
        self.item = item
        self.is_double_click = False
        self.check_buffer = CheckButtonBuffer(self.item.is_autostart(), CHECK_WIDTH/2 - 16, 3)
        
        self.padding_x = 10

    def set_autorun_state(self, run):
        self.item.set_autostart_state(run)
        self.redraw()
    
    
    def render_check(self, cr, rect):
        self.render_background(cr, rect)
        self.check_buffer.render(cr, rect)


    def render_app(self, cr, rect):
        app_name = str_mark_down(self.item.name)
        self.render_background(cr, rect)
        
        # Draw Text

        (text_width, text_height) = get_content_size(app_name)
        rect.x += self.padding_x
        rect.width -= self.padding_x * 2        
        draw_text(cr, app_name, rect.x , rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)
        
        
    def render_exec(self, cr, rect):
        exec_ = self.item.exec_
        self.render_background(cr, rect)
        rect.x += self.padding_x
        rect.width -= self.padding_x * 2        
        if exec_:
            (text_width, text_height) = get_content_size(exec_)
            draw_text(cr, exec_, rect.x, rect.y, rect.width, rect.height,
                    alignment = pango.ALIGN_LEFT)
        else:
            description = _("No exec")
            (text_width, text_height) = get_content_size(description)
            draw_text(cr, description, rect.x, rect.y, rect.width, rect.height,
                    alignment = pango.ALIGN_LEFT)

    def render_description(self, cr, rect):
        self.description = str_mark_down(self.item.comment)
        self.render_background(cr, rect)
        rect.x += self.padding_x
        rect.width -= self.padding_x * 2        
        if self.description:
            (text_width, text_height) = get_content_size(self.description)
            draw_text(cr, self.description, rect.x, rect.y, rect.width, rect.height,
                    alignment = pango.ALIGN_LEFT)
        else:
            description = _("No description")
            (text_width, text_height) = get_content_size(description)
            draw_text(cr, description, rect.x, rect.y, rect.width, rect.height,
                    alignment = pango.ALIGN_LEFT)

    def get_column_renders(self):
        return [self.render_check, self.render_app, self.render_description, self.render_exec]

    def get_column_widths(self):
        '''docstring for get_column_widths'''
        return [CHECK_WIDTH, 200,  300, 200]

    def get_height(self):
        return 30

    def select(self):
        self.is_select = True
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
        if self.item.type == self.item.TYPE_SYS:
            self.session_view.disable_delete_button(True)
        else:
            self.session_view.disable_delete_button(False)

    def unselect(self):
        self.is_select = False
        self.unhighlight()
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def button_press(self, column, x, y):
        if column == 0:
             self.check_buffer.press_button(x, y)
    def button_release(self, column, x, y):
        if column == 0:
            if self.check_buffer.release_button(x,y):
                state = self.check_buffer.get_active()
                self.set_autorun_state(state)

    def single_click(self, column, offset_x, offset_y):
        self.is_select = True
        self.redraw()

    def double_click(self, column, offset_x, offset_y):
        self.is_double_click = True
        self.set_autorun_state(not self.item.is_autostart())


    def redraw(self):
        if self.redraw_request_callback:
            self.redraw_request_callback(self)


    def render_background(self,  cr, rect):
        if self.is_select:
            background_color = app_theme.get_color("globalItemSelect")
        else:
            if  self.is_hover:
                background_color = app_theme.get_color("globalItemHover")
            else:
                background_color = app_theme.get_color("tooltipText")

        cr.set_source_rgb(*color_hex_to_cairo(background_color.get_color()))
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()
