

import gtk
from tray_mount_gui import EjecterApp

class MountMedia(object):
    def __init__(self):
        self.ejecter_app = EjecterApp()
        pass

    def init_values(self, this_list):
        self.this = this_list[0]
        self.tray_icon = this_list[1]
        self.tray_icon.set_icon_theme("usb")

    def id(slef):
        return "deepin-mount-media-hailongqiu"

    def run(self):
        return True

    def insert(self):
        return 4

    def plugin_widget(self):
        return self.ejecter_app.vbox

    def show_menu(self):
        self.this.set_size_request(250, 180)

    def hide_menu(self):
        pass



def return_plugin():
    return MountMedia
