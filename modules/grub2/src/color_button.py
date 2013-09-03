#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang YaoHua
#
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
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

import gtk
import gobject
from nls import _
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.iconview import IconView
from dtk.ui.button import Button
from dtk.ui.dialog import DialogBox, DIALOG_MASK_SINGLE_PAGE
from dtk.ui.theme import ui_theme
from dtk.ui.draw import draw_line, draw_vlinear, draw_pixbuf
from dtk.ui.utils import color_hex_to_cairo, alpha_color_hex_to_cairo
from dtk.ui.utils import place_center, cairo_disable_antialias

class ColorItem(gobject.GObject):
    '''
    ColorItem class for use in L{ I{ColorSelectDialog} <ColorSelectDialog>}.
    '''

    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        }

    def __init__(self, color_name, color):
        '''
        Initialize ColorItem class.

        @param color: Hex color string.
        '''
        gobject.GObject.__init__(self)
        self.color_name = color_name
        self.color = color
        self.width = 35
        self.height = 25
        self.padding_x = 4
        self.padding_y = 4
        self.hover_flag = False
        self.highlight_flag = False

    def emit_redraw_request(self):
        '''
        IconView interface function.

        Emit `redraw-request` signal.
        '''
        self.emit("redraw-request")

    def get_width(self):
        '''
        IconView interface function.

        Get item width.
        @return: Return item width, in pixel.
        '''
        return self.width + self.padding_x * 2

    def get_height(self):
        '''
        IconView interface function.

        Get item height.
        @return: Return item height, in pixel.
        '''
        return self.height + self.padding_y * 2

    def render(self, cr, rect):
        '''
        IconView interface function.

        Render item.

        @param cr: Cairo context.
        @param rect: Render rectangle area.
        '''
        # Init.
        draw_x = rect.x + self.padding_x
        draw_y = rect.y + self.padding_y

        # Draw color.
        cr.set_source_rgb(*color_hex_to_cairo(self.color))
        cr.rectangle(draw_x, draw_y, self.width, self.height)
        cr.fill()

        if self.hover_flag:
            cr.set_source_rgb(*color_hex_to_cairo(ui_theme.get_color("color_item_hover").get_color()))
            cr.rectangle(draw_x, draw_y, self.width, self.height)
            cr.stroke()
        elif self.highlight_flag:
            cr.set_source_rgb(*color_hex_to_cairo(ui_theme.get_color("color_item_highlight").get_color()))
            cr.rectangle(draw_x, draw_y, self.width, self.height)
            cr.stroke()

        # Draw frame.
        with cairo_disable_antialias(cr):
            cr.set_line_width(1)
            cr.set_source_rgb(*color_hex_to_cairo(ui_theme.get_color("color_item_frame").get_color()))
            cr.rectangle(draw_x, draw_y, self.width, self.height)
            cr.stroke()

    def icon_item_motion_notify(self, x, y):
        '''
        IconView interface function.

        Handle `motion-notify-event` signal.

        @param x: X coordinate that user motion on item.
        @param y: Y coordinate that user motion on item.
        '''
        self.hover_flag = True

        self.emit_redraw_request()

    def icon_item_lost_focus(self):
        '''
        IconView interface function.

        Handle `lost-focus` signal.
        '''
        self.hover_flag = False

        self.emit_redraw_request()

    def icon_item_highlight(self):
        '''
        IconView interface function.

        Handle `highlight` signal.
        '''
        self.highlight_flag = True

        self.emit_redraw_request()

    def icon_item_normal(self):
        '''
        Normal icon item.
        '''
        self.highlight_flag = False

        self.emit_redraw_request()

    def icon_item_button_press(self, x, y):
        '''
        IconView interface function.

        Handle `button-press` signal.
        '''
        pass

    def icon_item_button_release(self, x, y):
        '''
        IconView interface function.

        Handle `button-release` signal.
        '''
        pass

    def icon_item_single_click(self, x, y):
        '''
        IconView interface function.

        Handle `click` signal.
        '''
        pass

    def icon_item_double_click(self, x, y):
        '''
        IconView interface function.

        Handle `double-click` signal.
        '''
        pass

gobject.type_register(ColorItem)

DEFAULT_COLOR_LIST = {_("white"): "#ffffff", _("blue"): "#0000a8", 
                      _("magenta"): "#a800a8", _("cyan"): "#00a8a8",
                      _("light-gray"): "#a8a8a8", _("yellow"): "#fefe54",
                      _("red"): "#ff0000", _("light-magenta"): "#fe54fe", 
                      _("dark-gray"): "#545454", _("green"): "#00a800",
                      _("light-blue"): "#5454fe", _("light-red"): "#fe5454", 
                      _("black"): "#000000", _("light-cyan"): "#54fefe", 
                      _("light-green"): "#54fe54", _("brown"): "#a85400"}

def color_to_name(hex_color):
    for key, value in DEFAULT_COLOR_LIST.iteritems():
        if value == hex_color:
            return key
    return ""

class ColorSelectionDialog(DialogBox):

    def __init__(self, color, confirm_callback=None, cancel_callback=None):
        super(ColorSelectionDialog, self).__init__(_("Select color"),
                                                   360,
                                                   140,
                                                   DIALOG_MASK_SINGLE_PAGE)
        self.color = color
        self.confirm_callback = confirm_callback
        self.cancel_callback = cancel_callback

        self.color_select_view = IconView()
        self.color_select_view.set_size_request(360, 60)
        self.color_select_view.connect("single-click-item", lambda view, item, x, y: self.update_color(item.color))
        self.color_select_view.connect("double-click-item", lambda view, item, x, y: self.update_color(item.color, False))
        self.color_select_scrolled_window = ScrolledWindow()
        self.color_select_scrolled_window.add_child(self.color_select_view)
        self.color_select_scrolled_window.set_size_request(-1, 60)
        self.color_select_view.draw_mask = self.get_mask_func(self.color_select_view)
        for color_name in DEFAULT_COLOR_LIST:
            self.color_select_view.add_items([ColorItem(color_name, DEFAULT_COLOR_LIST[color_name])])
        # self.color_select_view.draw_mask = self.get_mask_func(self.color_select_view)
        self.body_box.add(self.color_select_scrolled_window)

        self.confirm_button = Button(_("OK"))
        self.cancel_button = Button(_("Cancel"))
        self.confirm_button.connect("clicked", lambda w: self.click_confirm_button())
        self.cancel_button.connect("clicked", lambda w: self.click_cancel_button())
        self.right_button_box.set_buttons([self.cancel_button, self.confirm_button])

    def click_confirm_button(self):
        '''
        Internal function to handle click confirm button.
        '''
        if self.confirm_callback != None:
            self.confirm_callback(self.color)

        self.destroy()

    def click_cancel_button(self):
        '''
        Internal function to handle click cancel button.
        '''
        if self.cancel_callback != None:
            self.cancel_callback()

        self.destroy()

    def update_color(self, color, is_single_click=True):
        self.color = color

        if not is_single_click:
            if self.confirm_callback != None:
                self.confirm_callback(self.color)
            self.destroy()

gobject.type_register(ColorSelectionDialog)

class ColorButton(gtk.VBox):
    '''
    Button to select color.

    @undocumented: popup_color_selection_dialog
    @undocumented: expose_button
    @undocumented: select_color
    '''

    __gsignals__ = {
        "color-select" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
        }

    def __init__(self, color="#FF0000"):
        '''
        Initialize ColorButton class.

        @param color: Hex color string to initialize, default is \"#FF0000\".
        '''
        gtk.VBox.__init__(self)
        self.button = gtk.Button()
        self.color = color
        self.width = 69
        self.height = 22
        self.color_area_width = 39
        self.color_area_height = 14

        self.button.set_size_request(self.width, self.height)
        self.pack_start(self.button, False, False)

        self.button.connect("expose-event", self.expose_button)
        self.button.connect("button-press-event", self.popup_color_selection_dialog)

    def popup_color_selection_dialog(self, widget, event):
        '''
        Internal function to popup color selection dialog when user click on button.

        @param widget: ColorButton widget.
        @param event: Button press event.
        '''
        if not hasattr(self, "dialog") or not self.dialog.get_visible():
            self.dialog = ColorSelectionDialog(self.color, self.select_color)
            self.dialog.show_all()
            place_center(self.get_toplevel(), self.dialog)

    def select_color(self, color):
        '''
        Select color.

        @param color: Hex color string.
        '''
        self.set_color(color)
        self.emit("color-select", color)

    def set_color(self, color):
        '''
        Internal function to set color.

        @param color: Hex color string.
        '''
        self.color = color

        self.queue_draw()

    def get_color(self):
        '''
        Get color.

        @return: Return hex color string.
        '''
        return self.color

    def expose_button(self, widget, event):
        '''
        Internal function to handle `expose-event` signal.

        @param widget: ColorButton instance.
        @param event: Expose event.
        '''
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y, w, h = rect.x, rect.y, rect.width, rect.height

        # Get color info.
        if widget.state == gtk.STATE_NORMAL:
            border_color = ui_theme.get_color("button_border_normal").get_color()
            background_color = ui_theme.get_shadow_color("button_background_normal").get_color_info()
        elif widget.state == gtk.STATE_PRELIGHT:
            border_color = ui_theme.get_color("button_border_prelight").get_color()
            background_color = ui_theme.get_shadow_color("button_background_prelight").get_color_info()
        elif widget.state == gtk.STATE_ACTIVE:
            border_color = ui_theme.get_color("button_border_active").get_color()
            background_color = ui_theme.get_shadow_color("button_background_active").get_color_info()
        elif widget.state == gtk.STATE_INSENSITIVE:
            border_color = ui_theme.get_color("disable_frame").get_color()
            disable_background_color = ui_theme.get_color("disable_background").get_color()
            background_color = [(0, (disable_background_color, 1.0)),
                                (1, (disable_background_color, 1.0))]

        # Draw background.
        draw_vlinear(
            cr,
            x + 1, y + 1, w - 2, h - 2,
            background_color)

        # Draw border.
        cr.set_source_rgb(*color_hex_to_cairo(border_color))
        draw_line(cr, x + 2, y + 1, x + w - 2, y + 1) # top
        draw_line(cr, x + 2, y + h, x + w - 2, y + h) # bottom
        draw_line(cr, x + 1, y + 2, x + 1, y + h - 2) # left
        draw_line(cr, x + w, y + 2, x + w, y + h - 2) # right

        # Draw four point.
        if widget.state == gtk.STATE_INSENSITIVE:
            top_left_point = ui_theme.get_pixbuf("button/disable_corner.png").get_pixbuf()
        else:
            top_left_point = ui_theme.get_pixbuf("button/corner.png").get_pixbuf()
        top_right_point = top_left_point.rotate_simple(270)
        bottom_right_point = top_left_point.rotate_simple(180)
        bottom_left_point = top_left_point.rotate_simple(90)

        draw_pixbuf(cr, top_left_point, x, y)
        draw_pixbuf(cr, top_right_point, x + w - top_left_point.get_width(), y)
        draw_pixbuf(cr, bottom_left_point, x, y + h - top_left_point.get_height())
        draw_pixbuf(cr, bottom_right_point, x + w - top_left_point.get_width(), y + h - top_left_point.get_height())

        # Draw color frame.
        cr.set_source_rgb(*color_hex_to_cairo("#c0c0c0"))
        cr.rectangle(x + (w - self.color_area_width) / 2,
                     y + (h - self.color_area_height) / 2,
                     self.color_area_width,
                     self.color_area_height)
        cr.stroke()

        # Draw color.
        cr.set_source_rgb(*color_hex_to_cairo(self.color))
        cr.rectangle(x + (w - self.color_area_width) / 2,
                     y + (h - self.color_area_height) / 2,
                     self.color_area_width,
                     self.color_area_height)
        cr.fill()

        # Draw mask when widget is insensitive.
        if widget.state == gtk.STATE_INSENSITIVE:
            cr.set_source_rgba(*alpha_color_hex_to_cairo(ui_theme.get_alpha_color("color_button_disable_mask").get_color_info()))
            cr.rectangle(x + (w - self.color_area_width) / 2,
                         y + (h - self.color_area_height) / 2,
                         self.color_area_width,
                         self.color_area_height)
            cr.fill()

        return True

gobject.type_register(ColorButton)

