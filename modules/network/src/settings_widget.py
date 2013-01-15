#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
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
from dss import app_theme
from dtk.ui.new_treeview import TreeView, TreeItem
from dtk.ui.theme import ui_theme
from dtk.ui.draw import draw_text, draw_pixbuf, draw_hlinear,draw_vlinear, draw_line
from dtk.ui.utils import color_hex_to_cairo, cairo_disable_antialias, is_left_button, is_right_button, get_content_size, propagate_expose, alpha_color_hex_to_cairo
from dtk.ui.new_entry import EntryBuffer, Entry, InputEntry
from dtk.ui.box import ImageBox
from dtk.ui.button import Button
from dtk.ui.label import Label
import gobject
import gtk
import pango
from nls import _

from constants import FRAME_LEFT_PADDING, IMG_WIDTH, TREEVIEW_BORDER_COLOR, TREEVIEW_BG_COLOR
BORDER_COLOR = color_hex_to_cairo(TREEVIEW_BORDER_COLOR)
BG_COLOR = color_hex_to_cairo(TREEVIEW_BG_COLOR)

class EntryTreeView(TreeView):
    __gsignals__ = {
        "select"  : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.GObject, int)),
        "unselect": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "double-click" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.GObject, int))}
    
    def __init__(self, 
            items=[],
            drag_data=None,
            enable_hover=True,
            enable_highlight=True,
            enable_multiple_select=False,
            enable_drag_drop=False,
            drag_icon_pixbuf=None,
            start_drag_offset=50,
            mask_bound_height=24,
            right_space=0,
            top_bottom_space=3):
        super(EntryTreeView, self).__init__(
            items, drag_data, enable_hover,
            enable_highlight, enable_multiple_select,
            enable_drag_drop, drag_icon_pixbuf,
            start_drag_offset, mask_bound_height,
            right_space, top_bottom_space)

        self.connect("double-click", self.double_click)
        self.draw_area.connect("button-press-event", self.button_press)
        self.draw_area.connect("button-release-event", self.button_release)
        self.draw_area.connect("motion-notify-event", self.motion_notify)

    def button_press(self, widget, event):
        if self.get_data("entry_widget") is None:
            return
        cell = self.get_cell_with_event(event)
        entry = self.get_data("entry_widget")
        item = entry.get_data("item")
        # if pressed outside entry column area, destroy entry
        if cell is None:
            entry.get_parent().destroy()
            return
        (row, column, offset_x, offset_y) = cell
        if self.visible_items[row] != item or column not in item.ENTRY_COLUMN:
            entry.get_parent().destroy()
            return
        # right button the show menu
        if is_right_button(event):
            entry.right_menu.show((int(event.x_root), int(event.y_root)))
            return
        entry.set_data("button_press", True)
        send_event = event.copy()
        send_event.send_event = True
        send_event.x = float(offset_x)
        send_event.y = 1.0
        send_event.window = entry.window
        entry.event(send_event)
        send_event.free()

    def button_release(self, widget, event):
        if self.get_data("entry_widget") is None:
            return
        entry = self.get_data("entry_widget")
        # has not been pressed
        if not entry.get_data("button_press"):
            return
        cell = self.get_cell_with_event(event)
        if cell is None:
            offset_x = 1
        else:
            (row, column, offset_x, offset_y) = cell
        entry.grab_focus()
        entry.set_data("button_press", False)
        send_event = event.copy()
        send_event.send_event = True
        send_event.x = float(offset_x)
        send_event.y = 1.0
        send_event.window = entry.window
        entry.event(send_event)
        send_event.free()

    def motion_notify(self, widget, event):
        if self.get_data("entry_widget") is None:
            return
        entry = self.get_data("entry_widget")
        # has not been pressed
        if not entry.get_data("button_press"):
            return
        cell = self.get_cell_with_event(event)
        item = entry.get_data("item")
        if cell is None:
            offset_x = 1
        else:
            (row, column, offset_x, offset_y) = cell
            if column != item.ENTRY_COLUMN:
                offset_x = 1
        send_event = event.copy()
        send_event.send_event = True
        send_event.x = float(offset_x)
        send_event.y = 1.0
        send_event.window = entry.window
        entry.event(send_event)
        send_event.free()

    def double_click(self, widget, item, column):
        if not column in item.ENTRY_COLUMN:
            return
        if item.entry:
            item.entry.grab_focus()
            return
        item.get_buffer(column)
        item.entry_buffer.set_property('cursor-visible', True)
        hbox = gtk.HBox(False)
        align = gtk.Alignment(0, 0, 1, 1)
        entry = Entry()
        entry.set_data("item", item)
        entry.set_data("button_press", False)
        entry.set_buffer(item.entry_buffer)
        width = item.get_column_widths()[column]
        if width >= 0:
            entry.set_size_request(item.get_column_widths()[column]-4, 0)

        entry.connect("press-return", lambda w: hbox.destroy())
        entry.connect("destroy", self.edit_done, hbox, item)
        entry.connect_after("focus-in-event", self.entry_focus_changed, item)
        entry.connect_after("focus-out-event", self.entry_focus_changed, item)
        self.pack_start(hbox, False, False)
        self.set_data("entry_widget", entry)
        hbox.pack_start(entry, False, False)
        hbox.pack_start(align)
        hbox.show_all()
        entry.set_can_focus(True)
        entry.grab_focus()
        entry.select_all()
        item.entry = entry

    def edit_done(self, entry, box, item):
        item.set_connection_name(entry.get_text())
        item.entry = None
        item.entry_buffer.set_property('cursor-visible', False)
        item.entry_buffer.move_to_start()
        item.redraw_request_callback(item)
        self.draw_area.grab_focus()
        self.set_data("entry_widget", None)
   
    def entry_focus_changed(self, entry, event, item):
        if event.in_:
            item.entry_buffer.set_property('cursor-visible', True)
        else:
            item.entry_buffer.set_property('cursor-visible', False)

    def release_item(self, event):
        if is_left_button(event):
            cell = self.get_cell_with_event(event)
            if cell is not None:
                (release_row, release_column, offset_x, offset_y) = cell
                
                if release_row is not None:
                    if self.double_click_row == release_row:
                        self.visible_items[release_row].double_click(release_column, offset_x, offset_y)
                        self.emit("double-click", self.visible_items[release_row], release_column)
                    elif self.single_click_row == release_row:
                        self.visible_items[release_row].single_click(release_column, offset_x, offset_y)
                
                if self.start_drag and self.is_in_visible_area(event):
                    self.drag_select_items_at_cursor()
                    
                self.double_click_row = None    
                self.single_click_row = None    
                self.start_drag = False
                
                # Disable select rows when press_in_select_rows valid after button release.
                if self.press_in_select_rows:
                    self.set_select_rows([self.press_in_select_rows])
                    self.start_select_row = self.press_in_select_rows
                    self.press_in_select_rows = None
                
                self.set_drag_row(None)

def render_background( cr, rect):
    background_color = [(0,["#ffffff", 1.0]),
                        (1,["#ffffff", 1.0])]
    draw_vlinear(cr, rect.x ,rect.y, rect.width, rect.height, background_color)

class ShowOthers(TreeItem):
    CHECK_LEFT_PADDING = FRAME_LEFT_PADDING
    CHECK_RIGHT_PADIING = 10

    def __init__(self, child_list, resize_tree_cb):
        TreeItem.__init__(self)
        self.children = child_list
        self.resize_tree = resize_tree_cb

    def render_content(self, cr, rect):
        render_background(cr, rect)
        (text_width, text_height) = get_content_size("show all")
        import pango
        draw_text(cr, "show all", rect.x, rect.y, rect.width, rect.height,
                alignment=pango.ALIGN_CENTER)

    def render_right(self, cr, rect):
        render_background(cr, rect)

        BORDER_COLOR = color_hex_to_cairo("#d2d2d2")
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            cr.rectangle(rect.x , rect.y , rect.width , rect.height + 1)
            cr.stroke()


    def get_column_renders(self):
        return [lambda cr, rect: render_background( cr, rect),
                self.render_content,
                self.render_right]

    def get_column_widths(self):
        return [37,-1,37]

    def get_height(self):
        return 30

    def single_click(self, column, offset_x, offset_y):
        if self.is_expand:
            self.unexpand()
        else:
            self.expand()


    def expand(self):
        self.is_expand = True
        self.add_child_item()

        if self.redraw_request_callback:
            self.redraw_request_callback(self)
        self.resize_tree()

    def unexpand(self):
        '''docstring for unexpand'''
        self.delete_child_item()

        self.is_expand = False
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
        self.resize_tree()

    def add_child_item(self):
        self.child_items = self.children
        self.add_items_callback(self.child_items, self.row_index + 1)
        
    def delete_child_item(self):
        self.delete_items_callback(self.child_items)

class AddSettingItem(TreeItem):
    CHECK_LEFT_PADDING = FRAME_LEFT_PADDING
    CHECK_RIGHT_PADIING = 10

    def __init__(self, name, add_setting_callback):
        TreeItem.__init__(self)
        self.name = name
        self.add_setting = add_setting_callback
        '''
        Pixbuf
        '''
        self.add_pixbuf_out = app_theme.get_pixbuf("network/add-1.png")
        self.add_pixbuf_active = app_theme.get_pixbuf("network/add.png")


    def get_height(self):
        return 30 
    
    def get_column_widths(self):
        return [37, -1, 37]
    
    def get_column_renders(self):
        return [self.render_add, self.render_content, self.render_delete]
    
            
    def render_add(self, cr, rect):
        self.render_background(cr,rect)

        add_icon = self.add_pixbuf_active

        draw_pixbuf(cr, add_icon.get_pixbuf(), rect.x + self.CHECK_LEFT_PADDING, rect.y + (rect.height - IMG_WIDTH)/2)
        #draw outline
        #BORDER_COLOR = color_hex_to_cairo("#d2d2d2")
        #with cairo_disable_antialias(cr):
            #cr.set_source_rgb(*BORDER_COLOR)
            #cr.set_line_width(1)
            #cr.rectangle(rect.x , rect.y , rect.width + 1, rect.height)
            #cr.stroke()

    def render_content(self, cr, rect):
        self.render_background(cr, rect)
        draw_text(cr, self.name, rect.x + self.CHECK_RIGHT_PADIING, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)
        #BORDER_COLOR = color_hex_to_cairo("#d2d2d2")
        #with cairo_disable_antialias(cr):
            #cr.set_source_rgb(*BORDER_COLOR)
            #cr.set_line_width(1)
            #draw_line(cr, rect.x, rect.y, rect.x + rect.width, rect.y )
            #draw_line(cr, rect.x, rect.y + rect.height, rect.x + rect.width, rect.y + rect.height)


    def render_delete(self, cr, rect):
         
        self.render_background(cr, rect)

        BORDER_COLOR = color_hex_to_cairo("#d2d2d2")
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            draw_line(cr, rect.x + rect.width, rect.y, rect.x + rect.width, rect.y + rect.height)
        #with cairo_disable_antialias(cr):
            #cr.set_source_rgb(*BORDER_COLOR)
            #cr.set_line_width(1)
            #cr.rectangle(rect.x , rect.y , rect.width , rect.height)
            #cr.stroke()

    def render_background(self,  cr, rect):
        if self.is_select:
            background_color = app_theme.get_color("globalItemSelect")
            cr.set_source_rgb(*color_hex_to_cairo(background_color.get_color()))
        else:
            if  self.is_hover:
                background_color = app_theme.get_color("globalItemHover")
                cr.set_source_rgb(*color_hex_to_cairo(background_color.get_color()))
            else:
                background_color = "#ffffff"
                cr.set_source_rgb(*color_hex_to_cairo(background_color))
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()
    #def render_background(self,  cr, rect):
        #if self.is_hover:
            #background_color = [(0,["#cce3ef", 1.0]),
                            #(1,["#cce3ef", 1.0])]
        #else:
            #background_color = [(0,["#f6f6f6", 1.0]),
                                #(1,["#f6f6f6", 1.0])]

        #draw_hlinear(cr, rect.x  , rect.y, rect.width , rect.height, background_color)


    def hover(self, column, offset_x, offset_y):
        self.is_hover = True
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def unhover(self,  column, offset_x, offset_y):
        self.is_hover = False
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def select(self):
        self.is_select = True
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def unselect(self):
        self.is_select = False
        if self.redraw_request_callback:
            self.redraw_request_callback(self)


    def single_click(self, column, offset_x, offset_y):
        self.add_setting()
        self.unhover(0,0,0)
        self.unselect()

        
        



class SettingItem(TreeItem):
    CHECK_LEFT_PADDING = FRAME_LEFT_PADDING
    CHECK_RIGHT_PADIING = 10
    def __init__(self, connection, setting, click_cb, delete_cb, set_button_cb=None):
        TreeItem.__init__(self)
        #self.title = title
        self.connection = connection
        self.setting = setting
        self.click = click_cb
        self.delete_connection = delete_cb
        self.set_button = set_button_cb
        self.entry = None
        self.entry_buffer = EntryBuffer(connection.get_setting("connection").id)
        self.entry_buffer.set_property('cursor-visible', False)
        self.entry_buffer.connect("changed", self.entry_buffer_changed)
        self.entry_buffer.connect("insert-pos-changed", self.entry_buffer_changed)
        self.entry_buffer.connect("selection-pos-changed", self.entry_buffer_changed)
        self.child_items = []
        self.height = 30
        self.ENTRY_COLUMN = [1]
        self.is_double_click = False

        self.check_select = False
        self.is_hover = False
        self.delete_hover = False
        self.connection_active = False

        '''
        Pixbuf
        '''
        self.check_pixbuf_active = app_theme.get_pixbuf("network/check_box-1.png")
        #self.check_pixbuf_hover = app_theme.get_pixbuf("network/check_box-1.png")
        #self.check_pixbuf_active = app_theme.get_pixbuf("network/check_box.png")
        #self.check_pixbuf_out = app_theme.get_pixbuf("network/check_box-3.png")
        #self.check_pixbuf_prelight = app_theme.get_pixbuf("network/check_box.png")
        self.delete_pixbuf_out = app_theme.get_pixbuf("network/delete-3.png")
        self.delete_pixbuf_prelight = app_theme.get_pixbuf("network/delete.png")
        self.delete_pixbuf_active = app_theme.get_pixbuf("network/delete-1.png")
        

    
    def entry_buffer_changed(self, bf):
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
    
    def get_height(self):
        return self.height
    
    def get_column_widths(self):
        return [47, -1, 37]

    def get_buffer(self, column):
        buffers = [0, self.entry_buffer, 0]
        self.entry_buffer = buffers[column]
        return self.entry_buffer
    
    def get_column_renders(self):
        return [self.render_check, self.render_content, self.render_delete]
    
    def render_check(self, cr, rect):
        self.render_background(cr,rect)
        if self.is_select:
            check_icon = self.check_pixbuf_active
            draw_pixbuf(cr, check_icon.get_pixbuf(), rect.x + self.CHECK_LEFT_PADDING, rect.y + (rect.height - IMG_WIDTH)/2)

    def render_content(self, cr, rect):
        self.render_background(cr,rect)
        if self.is_select:
            bg_color = "#3399FF"
            text_color = "#ffffff"

            if not self.is_double_click:
                pass
        else:
            text_color = "#000000"
            self.entry_buffer.move_to_start()
        self.entry_buffer.set_text_color(text_color)
        height = self.entry_buffer.get_pixel_size()[1]
        offset = (self.height - height)/2
        if offset < 0 :
            offset = 0
        rect.y += offset  
        if self.entry and self.entry.allocation.width == self.get_column_widths()[1]-4:
            self.entry.calculate()
            rect.x += 2
            rect.width -= 4
            self.entry_buffer.set_text_color("#000000")
            self.entry_buffer.render(cr, rect, self.entry.im, self.entry.offset_x)
        else:
            self.entry_buffer.render(cr, rect)

    def render_delete(self, cr, rect):
         
        self.render_background(cr, rect)
        if self.delete_hover:
            delete_icon = self.delete_pixbuf_out
            draw_pixbuf(cr, delete_icon.get_pixbuf(), rect.x + self.CHECK_LEFT_PADDING/2, rect.y + (rect.height - IMG_WIDTH)/2)
        else:
            delete_icon = self.delete_pixbuf_out

        BORDER_COLOR = color_hex_to_cairo("#d2d2d2")
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            draw_line(cr, rect.x + rect.width, rect.y, rect.x + rect.width, rect.y + rect.height)

    def render_background(self,  cr, rect):
        if self.is_select:
            background_color = app_theme.get_color("globalItemSelect")
            cr.set_source_rgb(*color_hex_to_cairo(background_color.get_color()))
        else:
            if  self.is_hover:
                background_color = app_theme.get_color("globalItemHover")
                cr.set_source_rgb(*color_hex_to_cairo(background_color.get_color()))
            else:
                background_color = "#ffffff"
                cr.set_source_rgb(*color_hex_to_cairo(background_color))
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

        #draw_hlinear(cr, rect.x - 20, rect.y, rect.width +20, rect.height, background_color)

    def set_active(self, active):
        self.connection_active = active
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
    
    def set_connection_name(self, text):
        self.connection.get_setting("connection").id = text
        if self.set_button:
            self.set_button("save", True)

    def unselect(self):
        self.is_select = False
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
    
    def select(self):
        #print self.get_highlight()
        self.is_select = True
        if self.is_hover:
            self.hover(0,0,0)
        self.click(self.connection)
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
    
    def hover(self, column, offset_x, offset_y):
        self.is_hover = True
        if self.is_select:
            self.timer = gobject.timeout_add(300, self.show_delete)

    def show_delete(self):
        self.delete_hover = True
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
        return False

    def unhover(self, column, offset_x, offset_y):
        self.is_hover = False
        # FIXME once delete an item , trigger unhover but hover_row doesnt exist 
        if hasattr(self, "timer"):
            gobject.source_remove(self.timer)
        self.delete_hover = False
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def single_click(self, column, offset_x, offset_y):
        self.is_double_click = False

        #self.click(self.connection)
        if column == 0:
            self.check_select = not self.check_select
            print "check clicked"
        elif column == 2 and self.delete_hover:
            if self.is_hover:
                self.delete_connection(self.connection)
            
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
    
    def double_click(self, column, offset_x, offset_y):
        self.is_double_click = True

    def expand(self):
        pass

    def unexpand(self):
        pass
gobject.type_register(SettingItem)

class HotspotBox(gtk.HBox):
    '''docstring for HotspotBox'''
    def __init__(self):
        super(HotspotBox, self).__init__()
        self.set_size_request(645, 30)
        self.connect("expose-event", self.expose_background)

        self.__init_ui()
    
    def __init_ui(self):
        self.check_bar = ImageBox(app_theme.get_pixbuf("network/check_box-2.png"))
        self.ssid_label = Label(_("ssid:"))
        self.ssid_entry = InputEntry("Deepin.org")
        self.ssid_entry.entry.set_size_request(200 ,22)

        self.password_label = Label(_("password:"))
        self.password_entry = InputEntry("")
        self.password_entry.entry.set_size_request(200 ,22)

        self.active_btn = Button("Active")
        self.jump_bar = ImageBox(app_theme.get_pixbuf("network/jump_to.png"))

        check_bar_align = self.wrap_align(self.check_bar, (0, 0, 10, 10))
        ssid_label_align = self.wrap_align(self.ssid_label, (0, 0, 0, 10))
        ssid_entry_align = self.wrap_align(self.ssid_entry)
        password_label_align = self.wrap_align(self.password_label, (0, 0, 20, 10))
        password_entry_align = self.wrap_align(self.password_entry)
        
        self.active_align = gtk.Alignment(1, 0.5, 0, 0)
        self.active_align.set_padding(0, 0, 0, 10)
        self.active_align.add(self.active_btn)

        self.pack_begin(self, [check_bar_align, ssid_label_align, 
                               ssid_entry_align, password_label_align,
                               password_entry_align,
                               ])

        self.pack_end(self.active_align, False, True)
        self.ssid_entry.expose_input_entry = self.expose_input_entry
        self.show_all()

        self.sensitive = False
        #self.password_entry.expose_input_entry = self.expose_input_entry

    def expose_background(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BG_COLOR)
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.fill()

            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            cr.rectangle(rect.x, rect.y , rect.width, rect.height)
            cr.stroke()

    def set_sensitive(self, state):
        widgets = [self.ssid_label, self.ssid_entry, self.password_label, self.password_entry]
        for w in widgets:
            w.set_sensitive(state)

    def pack_begin(self, parent, widget_list, expand=False, fill=False):
        for w in widget_list:
            parent.pack_start(w, expand, fill)

    def wrap_align(self, widget, padding=(0, 0, 0, 0)):
        align = gtk.Alignment(0, 0.5, 0, 0)
        align.set_padding(*padding)
        align.add(widget)
        return align
    
