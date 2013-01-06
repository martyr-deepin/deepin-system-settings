#!/usr/bin/env python
#-*- coding:utf-8 -*-

#from dtk.ui.draw import draw_pixbuf, draw_text
#from dtk.ui.constant import DEFAULT_FONT_SIZE
import gtk

from dss import app_theme
import sys,os
from dtk.ui.utils import get_parent_dir
from dtk.ui.label import Label
from dtk.ui.box import ImageBox
from dtk.ui.button import RadioButton, OffButton
from dtk.ui.line import HSeparator
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from constant import *
import style

ICON_PADDING = 5
TEXT_PADDING = 5
BUTTON_PADDING = 0
class Contain(gtk.Alignment):

    def __init__(self, icon, text, switch_callback=None):

        gtk.Alignment.__init__(self, 0,0.5,0,0)
        self.set_size_request(-1, CONTAINNER_HEIGHT)

        self.icon = icon
        self.text = text
        self.show()
        self.active_cb = switch_callback
        self.hbox = gtk.HBox()

        self.image = ImageBox(icon) 
        #self.height = app_theme.get_pixbuf("/inactive_normal.png").get_pixbuf().get_height()
        #self.width = app_theme.get_pixbuf("/inactive_normal.png").get_pixbuf().get_width()
        #self.image.set_from_pixbuf(icon.get_pixbuf())
        self.hbox.pack_start(self.image, False, False, ICON_PADDING)
        self.label = Label(text, text_size=TITLE_FONT_SIZE, label_width=100)
        self.hbox.pack_start(self.label, False, False, TEXT_PADDING)

        self.switch = OffButton()
        #from style import wrap_with_align
        #align = wrap_with_align(self.switch)
        self.hbox.pack_start(self.switch, False , False, BUTTON_PADDING)
        self.add(self.hbox)

        self.switch.connect("toggled", self.active_cb)
        self.hbox.connect("expose-event", self.expose_callback)
    
    def expose_callback(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb( 1, 1, 1) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()
    def set_active(self, state):
        self.switch.set_active(state)

    def get_active(self):
        return self.switch.get_active()

    def set_sensitive(self, state):
        #self.switch.set_inconsistent(state)
        self.switch.set_sensitive(state)

class TitleBar(gtk.VBox):
    def __init__(self, 
                 pixbuf, 
                 title,
                 text_size=TITLE_FONT_SIZE,
                 text_color=app_theme.get_color("globalTitleForeground"), 
                 width=222,
                 spacing=10):
        gtk.VBox.__init__(self)
        self.set_size_request(width, -1)
        
        hbox = gtk.HBox(spacing=spacing)
        image_box = ImageBox(pixbuf)
        label = Label(title, text_color, text_size)

        self.__box_pack_start(hbox, [image_box, label])

        align = style.wrap_with_align(hbox, align="left")

        separator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        separator.set_size_request(100, 10)
        self.__box_pack_start(self, [align, separator])

    def __box_pack_start(self, container, items, expand=False, fill=False):
        for item in items:
            container.pack_start(item, expand, fill)
        

class MyToggleButton(OffButton):
    def __init__(self):
        OffButton.__init__(self)

class MyRadioButton(RadioButton):
    '''docstring for MyRadioButton'''
    def __init__(self, main_button, label_text=None, padding_x=0, font_size=CONTENT_FONT_SIZE):
        super(MyRadioButton, self).__init__(label_text, padding_x, font_size)
        self.main_button = main_button
        self.switch_lock = False

        if self.main_button:
            self.main_button.button_list.append(self)
        else:
            self.button_list = [self]
        self.connect("clicked", self.click_radio_button)

    def click_radio_button(self, widget):
        if self.main_button:
            buttons = self.main_button.button_list
        else:
            buttons = self.button_list

        if not self.switch_lock:
            for w in buttons:
                w.switch_lock = True
                w.set_active(w == self)
                w.switch_lock = False
        

if __name__=="__main__":
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_title("Container")
    #win.border_width(2)

    win.connect("destroy", lambda w: gtk.main_quit())
    
    con = Contain(app_theme.get_pixbuf("network/wired.png"), "有线网络", lambda w: "sfdsf")

    vbox = gtk.VBox(False)
    vbox.pack_start(con)
    win.add(vbox)
    win.show_all()

    gtk.main()
