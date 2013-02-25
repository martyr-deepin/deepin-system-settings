

from vtk.utils import is_usb_device
import gtk
import gio
import glib
import gobject


ICON_SIZE = 16

class Device(gtk.Button):
    __gsignals__ = {
    "unmounted-event" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    "removed-event" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    def __init__(self, drive, device):
        gtk.Button.__init__(self)
        self.drive  = drive
        self.device = device

        self.was_removed = False
        self.icon_updated = False
        self.d_name = ""
        self.description = ""
        self.volumes = []
        self.mounts  = []
        self.volume_count = 0;
        self.mount_count  = 0;
        self.icon = gtk.image_new_from_gicon(self.drive.get_icon(), ICON_SIZE)
        #
        self.connect("clicked", self.clicked_eject)
        self.drive.connect("disconnected", self.handle_removed_drive)
        #
        self.set_label("")
        self.set_image(self.icon)
        self.show_all()

    def clicked_eject(self, widget):
        print "clicked_eject..."
        op = gtk.MountOperation()
        print op.get_password()
        if self.drive.can_eject():
            try:
                self.emit("unmounted-event")
            except Exception,e:
                print "error:", e
        else:
            for v in self.drive.get_volumes():
                try:
                    m = v.get_mount()
                    if True:
                        self.emit("unmounted-event")
                    else:
                        pass
                except Exception, e:
                    print "error:", e

    def handle_unmounted(self, mount):
        self.mounts.remove(mount)
        self.mount_count = self.mount_count - 1;
        self.update_label()

        if self.mount_count <= 0:
            self.set_mounted(False)
            self.emit("unmounted-event")

    def handle_removed_drive(self, drive):
        self.emit("removed-event")

    def handle_removed_volume(self, volume):
        self.volumes.remove(volume)
        self.volume_count = self.volume_count - 1;
        self.update_label()

        if self.volume_count == 0:
            self.emit("removed-event")

    def handle_removed_drive(self, removed_drive):
        print "handle_removed_drive..."

    def add_volume(self, volume):
        self.volumes.insert(0, volume)
        self.volume_count = self.volume_count + 1
        volume.connect("removed", self.handle_removed_volume)

        if not self.icon_updated:
            self.icon = gtk.image_new_from_gicon(volume.get_icon(), ICON_SIZE)
            self.icon_updated = True

        self.update_label()

    def add_mount(self, mount):
        volume = mount.get_volume()
        # add volume.
        if not (volume in self.volumes):
            self.add_volume(volume)

        try:
            self.mounts.remove(mount)
        except:
            pass
        self.mounts.insert(0, mount)

        self.mount_count = self.mount_count + 1
        self.set_mounted(True)
        mount.connect("unmounted", self.handle_unmounted)
        self.update_label()

    def update_label(self):
        if self.volume_count == 0:
            self.d_name = self.drive.get_name()
            self.description = ""
        elif self.volume_count == 1:
            v = self.volumes[0]
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

    def d_remove(self):
        if self.was_removed:
            return False;
        self.meit("removed")
        self.was_removed = True

    def set_mounted(self, mounted):
        #
        self.set_sensitive(mounted)

gobject.type_register(Device)

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
        self.monitor.connect("volume-added", self.volume_added)
        self.monitor.connect("mount-added", self.mount_added)

    def volume_added(self, monitor, volume):
        print "volume_added..."
        self.monitor_manage_volume(volume)

    def mount_added(self, monitor, mount):
        print "mount_added..."
        self.monitor_manage_mount(mount)


    def load_devices(self):
        for v in self.monitor.get_volumes():
            d = v.get_drive()
            
            self.monitor_manage_drive(d)
            self.monitor_manage_volume(v)

            m = v.get_mount()
            if m != None:
                self.monitor_manage_mount(m)
        #self.check_icon()

    def monitor_manage_drive(self, drive):
        # gio.Drive 
        print "monitor_manage_drive..."
        if drive == None:
            return False
        
        id = drive.get_identifier(self.conf.device_identifier)
        print "id:", id, drive.get_name()
	
        d = Device(drive, 0)
	self.devices[id] = d
	if is_usb_device(id):

	   self.hbox.pack_start(d, False, False) 
	   self.hbox.show_all()

	   d.connect('unmounted-event', self.d_unmounted_event)
	   d.connect('removed-event', self.d_removed_event)

    def d_unmounted_event(self, device):
        print "d_unmounted_event..."

    def d_removed_event(self, device):
        print "d_removed_event..."
        
    def monitor_manage_volume(self, v):
        # gio.Volume
        print "monitor_manage_volume..."
        drive = v.get_drive()
        id = drive.get_identifier(self.conf.device_identifier)
        if id == None: 
            return False

        try: 
            dev = self.devices[id]
            if dev == None:
                return False
        except:
            print "create dev..."
            self.monitor_manage_drive(drive)
            dev = self.devices[id]

        dev.add_volume(v)

    def monitor_manage_mount(self, m):
        # gio.Mount
        print "monitor_manage_mount..."
        drive = m.get_drive()
        print m.get_name(), drive.get_name()
        id = drive.get_identifier(self.conf.device_identifier) 
        if id == None:
            return False

        try:
            dev = self.devices[id]
            if dev == None:
                return False
        except:
            return False
            #dev = self.monitor_manage_drive(drive)

        dev.add_mount(m)


if __name__ == "__main__":
    EjecterApp()
    gtk.main()


