

import gtk
import gio
import glib


class Conf(object):
    def __init__(self):
        self.device_identifier = "unix-device"

class EjecterApp(object):
    def __init__(self):
        self.__init_values()
        self.__init_ejecter_settings()

    def __init_values(self):
        self.conf = Conf()
        self.devices = {}
        self.invalid = []
        self.monitor = gio.VolumeMonitor()

    def __init_ejecter_settings(self):
        self.load_devices()
        self.monitor.connect("volume-added", self.monitor_volume_added)
        self.monitor.connect("mount-added", self.monitor_mount_added)

    def load_devices(self):
        for v in self.monitor.get_volumes():
            d = v.get_drive()
            
            self.monitor_manage_drive(d)
            self.monitor_manage_volume(v)

            m = v.get_mount()
            if m != None:
                self.monitor_manage_mount(m)

    def monitor_manage_drive(self, drive):
        # gio.Drive 
        print "monitor_manage_drive..."
        if drive == None:
            return False
        
        id = drive.get_identifier(self.conf.device_identifier)
        print "id", id
        
    def d_removed(self, volume):
        print "d_removed..."

    def d_unmounted(self, volume):
        print "d_unmounted..."

    def monitor_manage_volume(self, v):
        # gio.Volume
        print "monitor_manage_volume..."
        print v.get_name(), v.get_icon()

    def monitor_manage_mount(self, m):
        # gio.Mount
        print "monitor_manage_mount..."
        print m.get_name(), m.get_icon()

    def monitor_volume_added(self, volume_monitor, drive):
        print "monitor_volume_added..."

    def monitor_mount_added(self, volume_monitor, mount):
        print "monitor_mount_added..."


if __name__ == "__main__":
    EjecterApp()
    gtk.main()


