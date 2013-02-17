

import gtk

class MountMedia(object):
    def __init__(self):
        pass

    def init_values(self, this_list):
        self.this = this_list[0]
        self.tray_icon = this_list[1]
        self.tray_icon.set_icon_theme("tray_user_icon")
        

    def id(slef):
        return "deepin-mount-media-hailongqiu"

    def run(self):
        return True

    def insert(self):
        pass

    def plugin_widget(self):
        return gtk.TextView()

    def show_menu(self):
        self.this.set_size_request(160, 180)

    def hide_menu(self):
        pass



def return_plugin():
    return MountMedia
