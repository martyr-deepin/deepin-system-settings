#!/usr/bin/env python
#-*- coding:utf-8 -*-

from dss import app_theme
from dtk.ui.theme import ui_theme
from dtk.ui.new_treeview import TreeItem, TreeView
from dtk.ui.box import ImageBox
from dtk.ui.draw import draw_vlinear, draw_text, draw_pixbuf
from dtk.ui.label import Label
from dtk.ui.button import Button
from dtk.ui.utils import color_hex_to_cairo, cairo_disable_antialias, get_content_size
from nm_modules import nm_module
import gtk
import pango

import style
from constants import FRAME_VERTICAL_SPACING, TITLE_FONT_SIZE, BETWEEN_SPACING, TREEVIEW_BG_COLOR
BORDER_COLOR = color_hex_to_cairo("#d2d2d2")

from nls import _


def render_background( cr, rect):
    background_color = [(0,["#ffffff", 1.0]),
                        (1,["#ffffff", 1.0])]
    draw_vlinear(cr, rect.x, rect.y, rect.width, rect.height, background_color)

class Region(gtk.Alignment):
    def __init__(self, connection=None):
        gtk.Alignment.__init__(self)

        style.set_main_window(self, True)
        #hbox = gtk.HBox(spacing=FRAME_VERTICAL_SPACING)
        #self.add(hbox)
        self.connect('expose-event', self.expose_event)
        self.prop_dict = {}

        main_table = gtk.Table(2, 2, False)
        main_table.set_row_spacings(4)
        main_table.set_col_spacings(8)
        self.add(main_table)
        
        country_label = Label(_("Country or Region:"), text_size=TITLE_FONT_SIZE)
        self.country_tree = TreeView(enable_multiple_select=False,
                                     enable_drag_drop=False,
                                     mask_bound_height=0,
                                     enable_hover=False)

        self.country_tree.set_size_request(370, 345)
        self.country_tree.draw_mask = self.draw_mask
        self.country_tree.connect("button-press-item", self.country_selected)
        left_box_align = gtk.Alignment(0, 0, 0, 0)
        left_box_align.set_padding(1,1,0,0)
        left_box_align.add(self.country_tree)
        left_box_align.connect("expose-event", self.expose_outline, [])
        left_box_align.show_all()

        left_box = gtk.VBox()
        # wrap title
        title_hbox = gtk.HBox(spacing=10)
        country_icon = ImageBox(app_theme.get_pixbuf("network/globe-green.png"))
        title_hbox.pack_start(country_icon, False, False)
        title_hbox.pack_start(country_label, False, False)
        left_box.pack_start(style.wrap_with_align(title_hbox), False, False)
        left_box.pack_start(left_box_align, False, False)

        provider_label = Label(_("Provider:"), text_size=TITLE_FONT_SIZE)
        self.provider_tree = TreeView(enable_multiple_select=False,
                                     enable_drag_drop=False,
                                     enable_hover=False)
        self.provider_tree.set_size_request(370, 345)
        self.provider_tree.draw_mask = self.draw_mask
        self.provider_tree.connect("button-press-item", self.provider_selected)
        right_box_align = gtk.Alignment(0, 0, 0, 0)
        right_box_align.set_padding(1,1,0,0)
        right_box_align.add(self.provider_tree)
        right_box_align.connect("expose-event", self.expose_outline, [])
        right_box = gtk.VBox()
        #right_box.set_size_request(436, 400)
        # wrap title
        title_rbox = gtk.HBox(spacing=10)
        provider_icon = ImageBox(app_theme.get_pixbuf("network/building.png"))
        title_rbox.pack_start(provider_icon, False, False)
        title_rbox.pack_start(provider_label, False, False)
        right_box.pack_start(style.wrap_with_align(title_rbox), False, False)
        right_box.pack_start(right_box_align, False, False)
        
        main_table.attach(left_box, 0, 1, 0, 1)
        main_table.attach(right_box, 1, 2, 0, 1)
        #hbox.pack_start(left_box, False, False)
        #hbox.pack_start(right_box, False, False)

        hint_box = gtk.HBox()
        hint_box.set_size_request(-1, 36)

        hints = "This assistant helps you easily set up a mobile broadband connection to a cellular network."
        label = Label(hints)
        hint_align = style.wrap_with_align(label)
        hint_align.connect("expose-event", self.expose_hint_background)

        #hint_box.pack_start(hint_align, False, False)

        main_table.attach(hint_align, 0,2, 1, 2)

        next_button = Button("Next")
        next_button.connect("clicked", self.next_button_clicked)
        #left_box_align.connect("expose-event", self.expose_outline, [])
        #right_box_align.connect("expose-event", self.expose_outline, [])
        self.show_all()
        #self.init()

    def expose_outline(self, widget, event, exclude):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        style.draw_out_line(cr, rect, exclude)

    def draw_mask(self, cr, x, y, w, h):
        bg_color = color_hex_to_cairo(TREEVIEW_BG_COLOR)

        cr.set_source_rgb(*bg_color)
        cr.rectangle(x, y, w, h)
        cr.fill()
        cr.set_source_rgb(*BORDER_COLOR)
        cr.rectangle(x -1, y, w + 1, h + 1)
        cr.stroke()

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb( 1, 1, 1) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

    def expose_hint_background(self, widget, event):
        bg_color = color_hex_to_cairo(TREEVIEW_BG_COLOR)
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb(*bg_color) 
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            cr.rectangle(rect.x , rect.y, rect.width , rect.height -1)
            cr.stroke()


    def next_button_clicked(self, widget):
        try:
            self.plan_select
        except:
            self.plan_select = None
        
        def add_keys(settings):
            self.prop_dict = settings
            
        username = self.__sp.get_provider_username(self.code, self.provider_select)
        password = self.__sp.get_provider_password(self.code, self.provider_select)
        add_keys({"cdma": {
                 "number": "#777",
                 "username": username,
                 "password": password}})
        provider_type = "cdma"
        if self.plan_select:
            self.prop_dict.pop("cdma")
            apn = self.plan_select
            index = self.__sp.get_provider_apns_name(self.code, self.provider_select).index(apn)
            (network_id, network_type) = self.__sp.get_provider_networks(self.code, self.provider_select)[index]
            add_keys({"gsm":{
                     "number": "*99#",
                     "username": username,
                     "password": password,
                     "apn": apn,
                     #"network_id": network_id,
                     "network_type": network_type}})
            provider_type = "gsm"

        if self.need_new_connection:
            new_connection = getattr(nm_module.nm_remote_settings, "new_%s_connection"%provider_type)()
            setting_page = nm_module.slider.get_page_by_name("mobile")
            setting_page.sidebar.new_connection_list[provider_type].append(new_connection)
            setting_page.init(setting_page.sidebar.new_connection_list)
            setting_page.sidebar.set_active(new_connection)
            setting_page.broadband.set_new_values(self.prop_dict, provider_type)
        else:
            setting_page = nm_module.slider.get_page_by_name("mobile")
            setting_page.broadband.set_new_values(self.prop_dict, provider_type)

        nm_module.slider._slide_to_page("mobile", "right")

    def init(self, connection_type=None):
        self.need_new_connection = True
        self.connection_type = connection_type
        from mm.provider import ServiceProviders
        self.__sp = ServiceProviders()
        self.country_list = self.__sp.get_country_name_list()
        self.country_tree.delete_all_items()
        self.country_tree.add_items([CountryItem(_(country)) for country in self.country_list])
        # add a bottom line for last item
        #self.country_tree.get_items()[-1].is_last = True

        code = self.__sp.get_country_from_timezone()

        self.country_codes = self.__sp.get_country_list()
        try:
            selected_country = self.country_tree.visible_items[self.country_codes.index(code)]
            self.country_tree.select_items([selected_country])
            self.auto_scroll_to()
            self.country_tree.emit("button-press-item", selected_country, 0, 1, 1)
        except:
            pass

    def country_selected(self, widget, w, a, b, c):
        self.provider_tree.delete_all_items()
        self.code = self.country_codes[widget.select_rows[0]]
        if self.connection_type:
            self.provider_names = getattr(self.__sp, "get_country_%s_providers_name"%self.connection_type)(self.code)
        else:
            self.provider_names = self.__sp.get_country_providers_name(self.code)
        
        self.provider_tree.add_items([Item(p, self.__sp, self.code) for p in self.provider_names])
        self.provider_tree.show_all()

    def provider_selected(self, widget, item, column, offset_x, offset_y):
        if type(item) is Item:
            self.provider_select = item.content
            self.plan_select = None
        else:
            self.plan_select = item.content

    def auto_scroll_to(self):
        vadjust = self.country_tree.scrolled_window.get_vadjustment()
        vadjust.set_value(((self.country_tree.select_rows[0]- 4)*30))
        
class Item(TreeItem):

    def __init__(self, content, sp, code):
        TreeItem.__init__(self)
        self.content = content
        self.sp = sp
        self.code = code
        self.gsm_providers = sp.get_country_gsm_providers_name(code)
        self.is_expand = False
        self.show_arrow = False
        self.arrow_right=ui_theme.get_pixbuf("treeview/arrow_right.png")
        self.arrow_down=ui_theme.get_pixbuf("treeview/arrow_down.png")
        self.arrow_height = self.arrow_down.get_pixbuf().get_height()
        self.arrow_width = self.arrow_down.get_pixbuf().get_width()

        self.show_arrow = self.add_apns_name(code, content)
        
    def render_content(self, cr, rect):
        (text_width, text_height) = get_content_size(self.html_escape(self.content))
        if self.is_select:
            draw_vlinear(cr, rect.x, rect.y, rect.width, rect.height,
                         ui_theme.get_shadow_color("listview_select").get_color_info())
        else:
            render_background(cr, rect)

        draw_text(cr, self.html_escape(self.content), rect.x + 5, rect.y, rect.width, rect.height,
                alignment=pango.ALIGN_LEFT)
        if self.show_arrow:
            if self.is_expand:
                draw_pixbuf(cr, self.arrow_down.get_pixbuf(), rect.x + text_width + 10 , rect.y + (rect.height- self.arrow_height)/2)
            else:
                draw_pixbuf(cr, self.arrow_right.get_pixbuf(), rect.x +text_width + 10, rect.y + (rect.height- self.arrow_height)/2)
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            #if self.is_last:            
                #cr.rectangle(rect.x +1, rect.y + rect.height, rect.width, 1)
            #else:
            cr.rectangle(rect.x , rect.y -1, rect.width ,rect.height + 1)
            cr.stroke()

    def get_column_widths(self):
        return [-1]

    def get_column_renders(self):
        return [self.render_content]
    
    def get_height(self):
        #(text_width, text_height) = get_content_size(self.content)
        return 30
        
    def select(self):
        self.is_select = True
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def unselect(self):
        self.is_select = False
        if self.redraw_request_callback:
            self.redraw_request_callback(self)

    def expand(self):
        #if self.content in self.gsm_providers:
            #print "is gsm:", self.content, self.gsm_providers
        if self.show_arrow:
            self.is_expand = True  
            self.add_child_item()
            if self.redraw_request_callback:
                self.redraw_request_callback(self)

    def unexpand(self):
        self.is_expand = False
        if self.show_arrow:
            self.delete_child_item()

        if self.redraw_request_callback:
            self.redraw_request_callback(self)
    
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
        else:
            return False

    def html_escape(self, text):
        html_escape_table = {
             "&": "&amp;",
             '"': "&quot;",
             "'": "&apos;",
             ">": "&gt;",
             "<": "&lt;",
             }
        return "".join(html_escape_table.get(c,c) for c in text)
        
class CountryItem(TreeItem):
    def __init__(self, content):
        TreeItem.__init__(self)
        self.content = content

    def render_flag(self, cr, rect):
        if self.is_select:
            draw_vlinear(cr, rect.x, rect.y, rect.width, rect.height,
                         ui_theme.get_shadow_color("listview_select").get_color_info())
        else:
            render_background(cr, rect)

        flag_icon = self.find_match_flag(self.content)
        if flag_icon:
            draw_pixbuf(cr, flag_icon.get_pixbuf(), rect.x + BETWEEN_SPACING/2 , rect.y) 
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            #if self.is_last:            
                #cr.rectangle(rect.x +1, rect.y + rect.height, rect.width, 1)
            #else:
            cr.rectangle(rect.x , rect.y -1, rect.width + 1,rect.height + 1)
            cr.stroke()

    def find_match_flag(self, country):
        formated_string = country.lower().replace(" ", "_").replace(",",'')
        try:
            return app_theme.get_pixbuf("network/flags/"+"flag_"+formated_string + ".png")
        except:
            return None

    def render_content(self, cr, rect):
        if self.is_select:
            draw_vlinear(cr, rect.x, rect.y, rect.width, rect.height,
                         ui_theme.get_shadow_color("listview_select").get_color_info())
        else:
            render_background(cr, rect)
        draw_text(cr, self.content, rect.x , rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)
        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            cr.rectangle(rect.x , rect.y -1 , rect.width ,rect.height +1)
            cr.stroke()

    def get_column_widths(self):
        return [30 + BETWEEN_SPACING , -1]

    def get_column_renders(self):
        return [self.render_flag, self.render_content]
    
    def get_height(self):
        #(text_width, text_height) = get_content_size(self.content)
        return 30
        
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

class SubItem(TreeItem):
    def __init__(self, content):
        TreeItem.__init__(self)
        self.content = content
        #self.escape_content = self.html_escape(content)
        
    def render_content(self, cr, rect):
        #(text_width, text_height) = get_content_size(self.content)
        if self.is_select:
            draw_vlinear(cr, rect.x, rect.y, rect.width, rect.height,
                         ui_theme.get_shadow_color("listview_select").get_color_info())
        else:
            render_background(cr, rect)
        draw_text(cr, self.content, rect.x + 50, rect.y, rect.width, rect.height,
                alignment = pango.ALIGN_LEFT)

        with cairo_disable_antialias(cr):
            cr.set_source_rgb(*BORDER_COLOR)
            cr.set_line_width(1)
            #if self.is_last:            
                #cr.rectangle(rect.x +1, rect.y + rect.height, rect.width, 1)
            #else:
            cr.rectangle(rect.x , rect.y -1, rect.width ,rect.height + 1)
            cr.stroke()
    def get_column_widths(self):
        return [-1]

    def get_column_renders(self):
        return [self.render_content]
    
    def get_height(self):
        #(text_width, text_height) = get_content_size(self.content)
        return 30
        
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

