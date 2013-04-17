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
                self.render_nothing,
                lambda w,r: self.render_background(w, r)]

    def get_column_widths(self):
        '''docstring for get_column_widths'''
        return [200, 100, -1]
    
    def get_height(self):
        return 30

    def render_background(self,  cr, rect):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

class SessionItem(TreeItem):

    def __init__(self, item):

        TreeItem.__init__(self)
        self.item = item
        self.is_double_click = False
        self.autorun = item.has_gnome_auto()
        self.check_buffer = CheckButtonBuffer(self.autorun, 2, 3)



    def set_autorun_state(self, run):
        self.item.set_option("X-GNOME-Autostart-enabled", str(run).lower())
        self.item.save(self.item.get_file())
        self.autorun = run
        self.redraw()

    def render_app(self, cr, rect):
        self.app_name = self.item.name()
        self.render_background(cr, rect)
        CHECK_LEFT_PADDING = 5
        CHECK_RIGHT_PADDING = 5
        
        #if self.autorun:
        self.check_buffer.render(cr, rect)
            #if self.is_select:
                #check_icon = app_theme.get_pixbuf("network/check_box-3.png")
            #else:
                #check_icon = app_theme.get_pixbuf("network/check_box-2.png")
            #draw_pixbuf(cr, check_icon.get_pixbuf(), rect.x + CHECK_LEFT_PADDING, rect.y + (rect.height - 16)/2)

        # Draw Text

        (text_width, text_height) = get_content_size(self.app_name)
        draw_text(cr, self.app_name, rect.x + CHECK_RIGHT_PADDING*2 + 16, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)

    def render_description(self, cr, rect):
        self.description = self.item.get_option("Comment")
        self.render_background(cr, rect)
        if self.description:
            (text_width, text_height) = get_content_size(self.description)
            draw_text(cr, self.description, rect.x, rect.y, rect.width, rect.height,
                    alignment = pango.ALIGN_LEFT)
        else:
            description = _("No description")
            (text_width, text_height) = get_content_size(description)
            draw_text(cr, description, rect.x, rect.y, rect.width, rect.height,
                    alignment = pango.ALIGN_LEFT)

        
    def render_state(self, cr, rect):
        self.state = self.item.is_active()
        self.render_background(cr, rect)
        if self.state:
            state = _("active")
        else:
            state = _("not running")
        (text_width, text_height) = get_content_size(state)
        draw_text(cr, state, rect.x, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT, text_color="#000000")

    def get_column_renders(self):
        return [self.render_app, self.render_state, self.render_description]

    def get_column_widths(self):
        '''docstring for get_column_widths'''
        return [200, 100, -1]

    def get_height(self):
        return 30

    def select(self):
        self.is_select = True
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

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
        self.set_autorun_state(not self.autorun)


    def redraw(self):
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
    

    def render_background(self,  cr, rect):
        #if self.is_highlight:
            #background_color = app_theme.get_color("globalItemHighlight")
        #else:
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
