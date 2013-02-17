

import gtk
import gio
import glib


class Device(gtk.Button):
    def __init__(self, drive, device):
        gtk.Button.__init__(self)
        self.drive  = drive
        self.device = device

        self.d_name = ""
        self.description = ""
        self.volumes = []
        self.mounts  = []
        self.volume_count = 0;
        self.mount_count  = 0;

        self.update_label()


    def update_label(self):
        if self.volume_count == 0:
            self.d_name = self.drive.get_name()
            self.description = ""
        elif self.volume_count == 1:
            v = self.volumes
            self.d_name = v.get_name()
            self.description = self.drive.get_name()
        else:
            volumes = ""
            first = true

            for v in self.volumes:
                if first:
                    volumes = volumes + v.get_name()
                    first = False
                else:
                    volumes = volumes + ", " + v.get_name()

                self.d_name = self.drive.get_name()
                self.description = volumes
            
        # set show label.
        self.set_label(self.d_name + " (" + self.description + ")")
        



class Conf(object):
    def __init__(self):
        self.device_identifier = "unix-device"
        self.show_internal = False

class EjecterApp(object):
    def __init__(self):
        self.__init_values()
        self.__init_ejecter_settings()

    def __init_values(self):
        self.hbox = gtk.VBox()
        
        self.conf = Conf()
        self.devices = {}
        self.invalid_devices = []
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
        '''
        print "monitor_manage_drive..."
        if drive == None:
            return False
        
        id = drive.get_identifier(self.conf.device_identifier)
        print "id", id, drive.get_name()

        self.hbox.pack_start(Device(drive, id), False, False) 
        self.hbox.show_all()

        #if
        #self.invalid_devices.append(id)
        '''
        pass

        
    def d_removed(self, volume):
        print "d_removed..."

    def d_unmounted(self, volume):
        print "d_unmounted..."

    def monitor_manage_volume(self, v):
        # gio.Volume
        '''
        print "monitor_manage_volume..."
        print v.get_name(), v.get_icon()
        drive = v.get_drive()
        id = drive.get_identifier(self.conf.device_identifier)

        print "id:", id
        '''
        pass

    def monitor_manage_mount(self, m):
        # gio.Mount
        print "monitor_manage_mount..."
        drive = m.get_drive()
        print m.get_name(), drive.get_name()
        de_test = Device(drive, id)
        de_test.connect("clicked", self.de_test_clicked, m)
        de_test.set_label(m.get_name() + " (" + drive.get_name() + ")")
        self.hbox.pack_start(de_test, False, False) 
        self.hbox.show_all()


    def unmount_end(self, mount, result):
        #mount.unmout_finish(result)
        pass

    def de_test_clicked(self, widget, m):
        m.unmount(self.unmount_end)
    


    def monitor_volume_added(self, volume_monitor, drive):
        print "monitor_volume_added..."

    def monitor_mount_added(self, volume_monitor, mount):
        print "monitor_mount_added..."


if __name__ == "__main__":
    EjecterApp()
    gtk.main()


