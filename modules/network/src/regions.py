#!/usr/bin/env python
#-*- coding:utf-8 -*-

from dtk.ui.theme import ui_theme
from dtk.ui.new_treeview import TreeItem, TreeView
from dtk.ui.draw import draw_vlinear, draw_text
from dtk.ui.label import Label
from dtk.ui.button import Button
import gtk
import pango


def render_background( cr, rect):
    background_color = [(0,["#ffffff", 1.0]),
                        (1,["#ffffff", 1.0])]
    draw_vlinear(cr, rect.x ,rect.y, rect.width, rect.height, background_color)

class Region(gtk.HBox):
    def __init__(self, connection = None):
        gtk.HBox.__init__(self, False, spacing = 10)
        self.set_size_request(680,300)
        
        country_label = Label("Country:")
        self.country_tree = TreeView(enable_multiple_select = False,
                                     enable_drag_drop = False)
        self.country_tree.set_size_request(380, 400)
        self.country_tree.connect("button-press-item", self.country_selected)

        left_box = gtk.VBox()
        left_box.pack_start(country_label, False, False)
        left_box.pack_start(self.country_tree, False, False)
        provider_label = Label("Provider:")
        self.provider_tree = TreeView()
        self.provider_tree.set_size_request(380, 400)
        self.provider_tree.connect("button-press-item", self.provider_selected)
        right_box = gtk.VBox()
        right_box.pack_start(provider_label, False, False)
        right_box.pack_start(self.provider_tree, False, False)
        
        self.pack_start(left_box, False, False)
        self.pack_end(right_box, False, False)

        next_button = Button("Next")
        next_button.connect("clicked", self.next_button_clicked)
        align = gtk.Alignment(0.5, 1, 0, 0)
        align.add(next_button)
        self.pack_start(align)

        self.show_all()
        self.init()


    def next_button_clicked(self, widget):
        
        country_index = self.country_tree.select_rows
        provider_index = self.country_tree.select_rows
        print provider_index
        
        #if country_index and provider_index:
            #country_index = country_index[0]
            #provider_index = provider_index[0]




        #else:
            #print "select!!"

    #def fill_entries(self, country_code, provider)

    def init(self):
        from mm.provider import ServiceProviders
        self.__sp = ServiceProviders()
        self.country_list = self.__sp.get_country_name_list()
        self.country_tree.add_items([SubItem(country) for country in self.country_list])

        code = self.__sp.get_country_from_timezone()

        self.country_codes = self.__sp.get_country_list()
        try:
            selected_country = self.country_tree.visible_items[self.country_codes.index(code)]
            self.country_tree.select_items([selected_country])
            self.country_tree.emit("button-press-item", selected_country, 0, 1, 1)
        except:
            pass
        
    
    def country_selected(self, widget, w, a, b, c ):
        self.provider_tree.delete_all_items()
        self.code = self.country_codes[widget.select_rows[0]]
        self.provider_names = self.__sp.get_country_providers_name(self.code)
        self.provider_tree.add_items([Item(p, self.__sp, self.code) for p in self.provider_names])
        self.provider_tree.show_all()

    def provider_selected(self, widget, w, a, b, c):
        pass


class Item(TreeItem):

    def __init__(self, content, sp, code):
        TreeItem.__init__(self)
        self.content = content
        self.sp = sp
        self.code = code
        self.gsm_providers = sp.get_country_gsm_providers_name(code)
        self.is_expand = False
        
    def render_content(self, cr, rect):
        #(text_width, text_height) = get_content_size(self.content)
        if self.is_select:
            draw_vlinear(cr, rect.x ,rect.y, rect.width, rect.height,
                         ui_theme.get_shadow_color("listview_select").get_color_info())
        else:
            render_background(cr, rect)
        draw_text(cr, self.content, rect.x, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)

    def get_column_widths(self):
        return [-1]

    def get_column_renders(self):
        return [self.render_content]
    
    def get_height(self):
        #(text_width, text_height) = get_content_size(self.content)
        return 40
        
    def select(self):
        self.is_select = True
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def unselect(self):
        self.is_select = False
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def expand(self):
        print self.content
        print self.gsm_providers
        if self.content in self.gsm_providers:
            print "expand!"
            self.is_expand = True  
            self.add_apns_name(self.code, self.content)

            self.add_child_item()
            
            if self.redraw_request_callback:
                self.redraw_request_callback(self)

    def unexpand(self):
        self.delete_child_item()

        if self.redraw_request_callback:
            self.redraw_request_callback(self)
        self.is_expand = False
    
    def single_click(self, column, offset_x, offset_y):
        if self.is_expand:
            self.unexpand()
        else:
            self.expand()

    def add_child_item(self):
        self.add_items_callback(self.child_items, self.row_index + 1)
        
    def delete_child_item(self):
        self.delete_items_callback(self.child_items)

    def add_apns_name(self, country, provider):
        apns = self.sp.get_provider_apns_name(country, provider)
        if apns:
            self.child_items = [SubItem(apn) for apn in apns]
            return True
        

class SubItem(TreeItem):
    def __init__(self, content):
        TreeItem.__init__(self)
        self.content = content
        
    def render_content(self, cr, rect):
        #(text_width, text_height) = get_content_size(self.content)
        if self.is_select:
            draw_vlinear(cr, rect.x ,rect.y, rect.width, rect.height,
                         ui_theme.get_shadow_color("listview_select").get_color_info())
        else:
            render_background(cr, rect)
        draw_text(cr, self.content, rect.x, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_CENTER)

    def get_column_widths(self):
        return [-1]

    def get_column_renders(self):
        return [self.render_content]
    
    def get_height(self):
        #(text_width, text_height) = get_content_size(self.content)
        return 40
        
    def select(self):
        self.is_select = True
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
    
    def unselect(self):
        self.is_select = False
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def expand(self):
        pass

    def unexpand(self):
        pass
