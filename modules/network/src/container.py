#!/usr/bin/env python
#-*- coding:utf-8 -*-

from theme import app_theme
from dtk.ui.button import ToggleButton
#from dtk.ui.draw import draw_pixbuf, draw_text
#from dtk.ui.constant import DEFAULT_FONT_SIZE
import gtk

import sys,os
from dtk.ui.utils import get_parent_dir
from dtk.ui.label import Label
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from constant import *

ICON_PADDING = 5
TEXT_PADDING = 30
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
        self.add(self.hbox)

        self.image = gtk.Image()
        self.height = app_theme.get_pixbuf("/inactive_normal.png").get_pixbuf().get_height()
        self.width = app_theme.get_pixbuf("/inactive_normal.png").get_pixbuf().get_width()
        self.image.set_from_pixbuf(icon.get_pixbuf())
        self.hbox.pack_start(self.image, False, True, ICON_PADDING)
        self.label = Label(text, text_size=TITLE_FONT_SIZE)
        self.hbox.pack_start(self.label, False, True, TEXT_PADDING)

        self.switch = ToggleButton(
                app_theme.get_pixbuf("/inactive_normal.png"), 
                app_theme.get_pixbuf("/active_normal.png"),
                inactive_disable_dpixbuf = app_theme.get_pixbuf("/inactive_normal.png"),
                active_disable_dpixbuf = app_theme.get_pixbuf("/inactive_normal.png"))

        self.switch.connect("toggled", self.active_cb)
        self.hbox.pack_start(self.switch, False , True, BUTTON_PADDING)
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

if __name__=="__main__":
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_title("Container")
    #win.border_width(2)

    win.connect("destroy", lambda w: gtk.main_quit())
    
    con = Contain(app_theme.get_pixbuf("/Network/wired.png"), "有线网络", lambda w: "sfdsf")

    vbox = gtk.VBox(False)
    vbox.pack_start(con)
    win.add(vbox)
    win.show_all()

    gtk.main()
