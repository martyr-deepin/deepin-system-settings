# element widgets to construct complex widgets
from dss import app_theme
from dtk.ui.new_entry import InputEntry, PasswordEntry
from dtk.ui.button import OffButton, CheckButton
from dtk.ui.label import Label
from dtk.ui.spin import SpinBox
#from container import TitleBar, Contain
from dtk.ui.utils import cairo_disable_antialias, color_hex_to_cairo, alpha_color_hex_to_cairo, propagate_expose, container_remove_all
from dtk.ui.line import HSeparator
from constants import TITLE_FONT_SIZE, CONTENT_FONT_SIZE, WIDGET_HEIGHT, BETWEEN_SPACING
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
        if self.revert:
            self.set_active(True)

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

class TableAsm(gtk.Table):

    def __init__(self, left_width=210, right_width=220):
        gtk.Table.__init__(self, 1, 2, False)
        self.set_col_spacings(BETWEEN_SPACING)
        self.left_width = left_width
        self.right_width = right_width
        self.shared = list()

    def row_input_entry(self, label_name, table=None):
        label = Label(label_name,
                      text_size=CONTENT_FONT_SIZE,
                      enable_select=False,
                      enable_double_click=False)

        entry = InputEntry()
        entry.set_size(self.right_width, WIDGET_HEIGHT)
        self._wrap_align((label, entry), table)
        return entry
    
    def row_pwd_entry(self, label_name, table=None):
        label = Label(label_name,
                      text_size=CONTENT_FONT_SIZE,
                      enable_select=False,
                      enable_double_click=False)
        entry = PasswordEntry()
        entry.set_size(self.right_width, WIDGET_HEIGHT)
        show_key = CheckButton(_("Show key"), padding_x=0)
        show_key.connect("toggled", lambda w: show_key.show_password(w.get_active()))
        self._wrap_align((label, entry), table)
        self._wrap_align((None, show_key), table)

        return entry

    def row_spin(self, label_name, low, high, table=None):
        label = Label(label_name,
                      text_size=CONTENT_FONT_SIZE,
                      enable_select=False,
                      enable_double_click=False)
        spin = SpinBox(0, low, high, 1, self.right_width)
        self._wrap_align((label, spin), table)

        return spin

    def row_toggle(self, label_name, table=None):
        label = Label(label_name,
                      text_size=CONTENT_FONT_SIZE,
                      enable_select=False,
                      enable_double_click=False)

        toggle = OffButton()
        self._wrap_align((label, toggle), table)

        return toggle
    
    def row_combo(self, label_name, combo_items, table=None):
        label = Label(label_name,
                      text_size=CONTENT_FONT_SIZE,
                      enable_select=False,
                      enable_double_click=False)

        combo = ComboBox([combo_items],
                          max_width=self.right_width)

        self._wrap_align((label, combo), table)
    
        return combo

    def table_build(self, table_spec=[], insert=-1):
        if insert == -1:
            items = self.shared + table_spec
        else:
            items = self.shared[:insert] + table_spec + self.shared[insert:]
        self._table_attach(self, items)
    
    def _wrap_align(self, row_item, table):
        left, right = row_item
        left_align = style.wrap_with_align(left, width = self.left_width)
        right_align = style.wrap_with_align(right, align="left")
        if table == None:
            self.shared.append((left_align, right_align))
        else:
            table.append((left_align, right_align))

    def _table_attach(self, table, items):
        table.resize(len(items), 2)
        for row, item in enumerate(items):
            left, right = item
            if left:
                table.attach(left, 0, 1, row, row + 1)
            if right:
                table.attach(right, 1, 2, row, row + 1)
    
    def table_clear(self):
        container_remove_all(self)
