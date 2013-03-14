# element widgets to construct complex widgets
from dss import app_theme
from dtk.ui.new_entry import InputEntry
from dtk.ui.button import OffButton
from dtk.ui.label import Label
#from container import TitleBar, Contain
from dtk.ui.utils import cairo_disable_antialias, color_hex_to_cairo, alpha_color_hex_to_cairo, propagate_expose
from dtk.ui.line import HSeparator
from constants import TITLE_FONT_SIZE 
import style

import gtk
class MyInputEntry(InputEntry):

    def __init__(self, content="",):

        InputEntry.__init__(self, content = content)
        self.entry.ancestor = self
        self.normal_color = "#000000"
        self.waring_color = "#ec2828"

        self.border_color = self.normal_color

    def set_warning(self):
        self.border_color = self.waring_color

    def set_normal(self):
        self.border_color = self.normal_color

    def expose_input_entry(self, widget, event):
        '''
        Internal callback for `expose-event` signal.
        '''
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y, w, h = rect.x, rect.y, rect.width, rect.height

        # Draw frame.
        with cairo_disable_antialias(cr):
            cr.set_line_width(1)
            cr.set_source_rgb(*color_hex_to_cairo(self.border_color))
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.stroke()
            
            cr.set_source_rgba(*alpha_color_hex_to_cairo(("#ffffff", 0.9)))
            cr.rectangle(rect.x, rect.y, rect.width - 1, rect.height - 1)
            cr.fill()
        
        propagate_expose(widget, event)
        
        return True

class Title(gtk.HBox):
    def __init__(self,
                 name,
                 text_size = TITLE_FONT_SIZE,
                 always_show = False,
                 toggle_callback=None,
                 label_right=False):
        gtk.HBox.__init__(self)
        self.set_size_request(-1, 30)
        
        label = Label(name,
                      text_size=text_size,
                      text_color=app_theme.get_color("globalTitleForeground"), 
                      enable_select=False,
                      enable_double_click=False)
        if label_right:
            self.label_box = style.wrap_with_align(label, width=210)
        else:
            self.label_box = style.wrap_with_align(label, align="left", width=210)
        self.label_box.set_size_request(210, 30)
        self.pack_start(self.label_box, False, False)

        if not always_show:
            self.switch = OffButton()
            align = style.wrap_with_align(self.switch, align="left")
            self.pack_start(align, False, False)
            self.switch.connect("toggled", toggle_callback)
            align.set_padding(0, 0, 15, 0)

class SettingSection(gtk.VBox):

    def __init__(self,
                section_name,
                text_size = TITLE_FONT_SIZE,
                always_show = True,
                has_seperator=True,
                toggle_callback=None,
                label_right = False,
                revert=False):
        gtk.VBox.__init__(self)
        self.section_name = section_name
        self.always_show = always_show
        self.has_seperator = has_seperator
        self.revert = revert
        self.title = Title(section_name, text_size,  always_show, self.toggle_callback, label_right)
        self.__init_section()

    def __init_section(self):
        
        self.content_box = gtk.VBox()
        self.align = self._set_align()
        self.align.add(self.content_box)
        self.main_align = gtk.Alignment(0, 0, 0, 0)
        self.main_align.set_padding(0, 0, 0, 0)
        self.pack_start(self.main_align, False, False)
        
    def load(self, content):
        self.main_align.add(self.title)
        
        if self.has_seperator:
            self.add_separator(self.content_box, 5)
        for c in content:
            self.content_box.pack_start(c, False, False)
        if self.always_show:
            self.pack_start(self.align, False, False)
        self.show_all()

    def _attach_to(self, table, items, row):
        for index,item in enumerate(items):
            table.attach(item, index, index + 1, row, row+ 1)

    def set_active(self, state):
        self.title.switch.set_active(state)

    def get_active(self):
        self.title.switch.get_active()

    def _set_align(self):
        align = gtk.Alignment(0,0,0,0)
        return align

    def toggle_callback(self, widget):
        is_active = widget.get_active()
        if self.revert:
            is_active = not is_active
        if is_active:
            self.pack_start(self.align, False, False)
            self.show_all()

            self.toggle_on()
            
        else:
            self.toggle_off()
            self.remove(self.align)

    def toggle_on(self):
        pass

    def toggle_off(self):
        pass

    def check_settings(self, connection):
        if connection.check_setting_finish():
            Dispatcher.set_button('save', True)
        else:
            Dispatcher.set_button("save", False)

    def add_separator(self, widget, height=10):
        h_separator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 0)
        h_separator.set_size_request(500, height)
        widget.pack_start(h_separator, False, False)

